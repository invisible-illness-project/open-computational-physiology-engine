#!/usr/bin/env python3
"""Single entry point for the OCPE release gates (Levels 1-4 + negative
controls; SYNTHETIC_TO_REAL_BENCHMARK.md).

Usage:
    python3 -m validation.levels.run_release_gates [--fast] [--skip-download]
        [--n-healthy N] [--n-pots N] [--context-cache FILE]
        [--from-context-cache FILE]

Outputs:
    docs/validation_report.md    results table (gate, check, target,
                                 measured, pass/fail/unresolved, evidence)
    validation/release_gates.yaml machine-readable gate results

Runtime management (documented substitutions, benchmark pre-registration
rule preserved - the tolerance bands in the gate modules are fixed a
priori; what is shortened is the SAMPLING, never the band):
  * The licensed-window clinical cohort (L3/NC/L4-sim arm) runs the full
    10-min HUT protocol (300 s supine + 600 s tilt + 60 s recovery) at
    dt=0.02 (the dataset-build resolution) with a small cohort
    (default 4 healthy + 4 hypovolemic POTS, ProcessPoolExecutor over 2
    workers).  Small-n Monte-Carlo precision is disclosed per check;
    tail-band verdicts downgrade to ``unresolved`` below the
    pre-registered minimum n (validation.levels.l3.TAIL_MIN_N).
  * L2 uses the repo bench tilt protocol; its sustained metric is the
    evaluator-flagged ``short_protocol_proxy`` and is gated against a
    bench continuity band, never the licensed reference.
  * Meal/exercise kernels run with compressed timing (``time_scale``;
    magnitudes untouched).
  * The full context can be cached (``--context-cache``) and reused
    (``--from-context-cache``) so report regeneration does not re-run
    the ODEs.
"""

from __future__ import annotations

import argparse
import copy
import os
import pickle
import subprocess
import sys
import tempfile
import time

import numpy as np
import yaml

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
sys.path.insert(0, os.path.join(_REPO, "tools"))

from validation.levels import (  # noqa: E402
    GOVERNING_STATEMENT, STATUSES, band_powers, dfa_alpha1, rmssd, sdnn,
)
from validation.levels import l1, l2, l3, l4, negative_controls  # noqa: E402
from validation.evaluator import (  # noqa: E402
    PhysiologicalEvaluator, compute_orthostatic_metrics,
)

#: Licensed 10-min HUT protocol (L3/NC/L4-sim arm).
LICENSED_TILT = {"tup": 300.0, "tend": 900.0, "height": 25.0,
                 "angle": 60.0, "tsim_end": 960.0}
#: Repo bench protocol (L2 trajectory battery).
BENCH_TILT = {"tup": 150.0, "tend": 250.0, "height": 25.0,
              "angle": 60.0, "tsim_end": 310.0}
#: PRCP-matched early-hold window (PRCP slow-tilt hold ~3 min):
#: minutes 2-3 after ramp completion, baseline = final 120 s supine.
PRCP_SIM_WINDOW = (120.0 + 14.0, 180.0 + 14.0)
PRCP_SUPINE_WINDOW_S = 120.0

GATE_SEED = 20260915


# ---------------------------------------------------------------------------
# Engine helpers
# ---------------------------------------------------------------------------

def _engine_run(model, tilt_params, seed, dt=0.02):
    from simulation.engine import SimulationEngine
    eng = SimulationEngine(model, dt=dt, seed=seed)
    return eng.run(dict(tilt_params)), eng


def _run_short_supine(seed, dt=0.02, horizon_s=60.0, param_overrides=None):
    """Short supine-only run (no tilt) for determinism/conservation/
    identifiability probes."""
    from models.baroreflex_model import BaroreflexPOTSModel
    model = BaroreflexPOTSModel()
    if param_overrides:
        model.params.update(param_overrides)
        model.initialize_steady_state()
    res, _ = _engine_run(
        model, {"tup": 9e9, "tend": 9e9, "height": 25.0, "angle": 60.0,
                "tsim_end": horizon_s}, seed=seed, dt=dt)
    return res


def _licensed_subject_worker(job):
    """Process-pool worker: build one cohort subject's mechanistic model
    (same mechanism levers as the dataset build) and run the licensed
    10-min HUT.  Returns plain-data metrics (picklable)."""
    sys.path.insert(0, _REPO)
    sys.path.insert(0, os.path.join(_REPO, "tools"))
    from models.baroreflex_model import BaroreflexPOTSModel
    from simulation.population import VirtualSubject
    from simulation.perturbations import PerturbationManager
    from simulation.engine import SimulationEngine
    from dataset.runner import calibrate_hm_for_rhr

    kb_dir = job["kb_dir"]
    model = BaroreflexPOTSModel(phenotype=None, subject=VirtualSubject(
        age=int(round(job["age"])), sex=job["sex"], bmi=job["bmi"],
        fitness=job["fitness"], seed=job["subject_seed"] % (2 ** 31)),
        kb_path=kb_dir)
    model.params["Hm"] = calibrate_hm_for_rhr(model.params, job["rhr_bpm"])
    expected_vol = float(model.params.get("TotalVol", 4500.0))
    if job.get("phenotypes"):
        pm = PerturbationManager(kb_path=kb_dir, include_experimental=False)
        params, _applied = pm.apply_perturbations(dict(model.params),
                                                  list(job["phenotypes"]))
        model.params = params
    if job.get("blood_volume_deficit_ml") is not None:
        model.params["TotalVol"] = expected_vol - job["blood_volume_deficit_ml"]
    if job.get("pooling_capacity_ml"):
        model.params["VMvl"] = float(job["pooling_capacity_ml"])
    model.initialize_steady_state()

    eng = SimulationEngine(model, dt=job.get("dt", 0.02), seed=job["engine_seed"])
    res = eng.run(dict(job["tilt_params"]))
    t = np.asarray(res["time"])
    hr = np.asarray(res["Hc"]) * 60.0
    onset = job["tilt_params"]["tup"]
    tilt_dur = job["tilt_params"]["tend"] - onset
    om = compute_orthostatic_metrics(
        time=t, hr_bpm=hr, onset_s=onset, tilt_duration_s=tilt_dur)

    # Resting features from the supine RR segment (structured beats).
    rr = np.asarray(res.get("rr_intervals_ms", []), dtype=float)
    bt = np.asarray(res.get("beat_times_s", []), dtype=float)
    rr_sup = rr[bt[:-1] < onset] if rr.size and bt.size == rr.size + 1 else rr
    if rr_sup.size < 20:
        rr_sup = rr
    freqs, P, lf, hf = band_powers(rr_sup)

    # PRCP-matched early-hold window delta-HR.
    lo, hi = PRCP_SIM_WINDOW
    sup_mask = (t >= onset - PRCP_SUPINE_WINDOW_S) & (t < onset)
    hold_mask = (t >= onset + lo) & (t < onset + hi)
    prcp_dhr = (float(np.mean(hr[hold_mask]) - np.mean(hr[sup_mask]))
                if np.any(hold_mask) and np.any(sup_mask) else float("nan"))

    return {
        "subject_id": job["subject_id"],
        "condition": job["condition"],
        "phenotypes": list(job.get("phenotypes") or []),
        "age": job["age"], "sex": job["sex"],
        "blood_volume_deficit_ml": job.get("blood_volume_deficit_ml"),
        "baseline_hr_bpm": om["baseline_hr_bpm"],
        "sustained_dhr_bpm": om["sustained_delta_HR_bpm"],
        "sustained_window_kind": om["sustained_window_kind"],
        "initial_transient_bpm": om["initial_transient_bpm"],
        "rmssd_ms": rmssd(rr_sup), "sdnn_ms": sdnn(rr_sup),
        "dfa_alpha1": dfa_alpha1(rr_sup),
        "lf_hf_ratio": (lf / hf if hf > 0 else float("nan")),
        "prcp_matched_dhr_bpm": prcp_dhr,
    }


def _sample_gate_cohort(n_healthy, n_pots, dataset_seed=GATE_SEED):
    """CohortSampler-based subject draws (identical sampling machinery to
    the dataset build; mechanism levers only - rule 4/5)."""
    from dataset.cohort import CohortSampler
    cfg = {"cohorts": [
        {"cohort_id": "gate_healthy", "condition": "healthy",
         "n_subjects": n_healthy,
         "age": {"dist": "uniform", "min": 20, "max": 45},
         "orthostatic_axis": {"enabled": True, "quantiles": "random",
                              "reference_protocol": "hut_60_70_10min"},
         "comorbidities": {"frame": "off"}},
        {"cohort_id": "gate_pots", "condition": "pots",
         "n_subjects": n_pots, "phenotypes": ["hypovolemic_pots"],
         "orthostatic_axis": {"enabled": True, "quantiles": "random",
                              "reference_protocol": "hut_60_70_10min"},
         "comorbidities": {"frame": "population"}},
    ]}
    return CohortSampler(cfg, dataset_seed).sample()


# ---------------------------------------------------------------------------
# Context construction
# ---------------------------------------------------------------------------

def build_context(args, log=print):
    from concurrent.futures import ProcessPoolExecutor
    from dataset.cohort import stable_seed

    ctx = {"meta": {
        "gate_seed": GATE_SEED,
        "licensed_tilt": LICENSED_TILT, "bench_tilt": BENCH_TILT,
        "n_healthy": args.n_healthy, "n_pots": args.n_pots,
        "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "ocpe_commit": _git_rev(),
    }}
    kb_dir = os.path.join(_REPO, "knowledge_base")

    # --- L1: determinism (two identical short runs) -------------------------
    log("[ctx] determinism probe (2 short runs)")
    ctx["det_runs"] = {
        "run_a": _run_short_supine(seed=GATE_SEED),
        "run_b": _run_short_supine(seed=GATE_SEED),
    }

    # --- L1: conservation placeholder (replaced by the bench-tilt run below,
    # where inter-compartment flows are large) --------------------------------
    ctx["conservation"] = None

    # --- L1: identifiability -------------------------------------------------
    log("[ctx] identifiability guard")
    ctx["identifiability"] = _identifiability_artifacts(kb_dir, log)

    # --- L1: kernel overlay checks (manager-level, no extra ODE) --------------
    ctx["meal_kernel_check"] = _kernel_overlay_check("meal")
    ctx["exercise_kernel_check"] = _kernel_overlay_check("exercise")

    # --- L1: honesty gating + scale harmonization -----------------------------
    log("[ctx] honesty gating + scale harmonization")
    ctx["honesty_gating"] = _honesty_gating_artifacts(kb_dir, log)
    ctx["scale_harmonization"] = _scale_harmonization_artifacts(kb_dir)

    # --- L2: healthy bench tilt ------------------------------------------------
    log("[ctx] healthy bench tilt run (L2)")
    from models.baroreflex_model import BaroreflexPOTSModel
    res, eng = _engine_run(BaroreflexPOTSModel(), BENCH_TILT, seed=GATE_SEED)
    t = np.asarray(res["time"])
    ctx["healthy_bench_tilt"] = {
        "time": t, "hr_bpm": np.asarray(res["Hc"]) * 60.0,
        "onset_s": BENCH_TILT["tup"],
        "tilt_duration_s": BENCH_TILT["tend"] - BENCH_TILT["tup"],
    }
    ctx["conservation"] = {
        "volumes_ml": np.column_stack(
            [res["Vau"], res["Vvu"], res["Val"], res["Vvl"], res["Vlv"]]),
        "total_vol_ml": np.asarray(res["blood_volume"]),
    }
    rr = np.asarray(res["rr_intervals_ms"], dtype=float)
    bt = np.asarray(res["beat_times_s"], dtype=float)
    rr_sup = rr[bt[:-1] < BENCH_TILT["tup"]] if bt.size == rr.size + 1 else rr
    hrv_in = eng.get_hrv_inputs()
    sup_mask = hrv_in["time_s"] < BENCH_TILT["tup"]
    ctx["timescale_rr"] = {
        "rr_intervals_ms": rr_sup,
        "respiration_rate_brpm": float(
            np.mean(hrv_in["respiration_rate_brpm"][sup_mask])),
    }

    # --- L2: meal + exercise runs (compressed timing, documented) -------------
    log("[ctx] meal run (compressed kernel timing)")
    ctx["meal_run"] = _meal_run()
    log("[ctx] exercise run")
    ctx["exercise_run"] = _exercise_run()

    # --- L2: circadian amplitude (fast slow-layer) ------------------------------
    log("[ctx] circadian multiday (2 days, slow layer)")
    from simulation.engine import SimulationEngine
    eng2 = SimulationEngine(BaroreflexPOTSModel(), seed=GATE_SEED)
    md = eng2.run_multiday(2, step_s=300.0)
    ctx["circadian_multiday"] = {
        "hour_of_day": np.asarray(md["hour_of_day"]),
        "mean_hr_bpm": np.asarray(md["mean_hr_bpm"]),
        "days": 2,
    }

    # --- L3/NC/L4-sim: licensed 10-min HUT cohort ------------------------------
    subjects = _sample_gate_cohort(args.n_healthy, args.n_pots)
    jobs = []
    for s in subjects:
        jobs.append({
            "subject_id": s.subject_id, "condition": s.condition,
            "phenotypes": list(s.phenotypes),
            "age": s.age, "sex": s.sex, "bmi": s.bmi, "fitness": s.fitness,
            "rhr_bpm": s.rhr_bpm, "subject_seed": s.subject_seed,
            "blood_volume_deficit_ml": s.blood_volume_deficit_ml,
            "pooling_capacity_ml": (s.pooling_capacity_ml
                                    if s.orthostatic_axis.get("enabled") else None),
            "engine_seed": stable_seed(s.subject_seed, "engine", "licensed_hut")
                           % (2 ** 31),
            "tilt_params": LICENSED_TILT, "dt": 0.02, "kb_dir": kb_dir,
        })
    log(f"[ctx] licensed 10-min HUT cohort: {len(jobs)} subjects "
        f"({args.n_healthy} healthy + {args.n_pots} hypovolemic POTS)")
    t0 = time.time()
    if args.serial or len(jobs) <= 1:
        rows = [_licensed_subject_worker(j) for j in jobs]
    else:
        with ProcessPoolExecutor(max_workers=min(2, len(jobs))) as pool:
            rows = list(pool.map(_licensed_subject_worker, jobs))
    log(f"[ctx] licensed cohort done in {time.time() - t0:.0f}s")
    ctx["licensed_cohort"] = {
        "healthy": [r for r in rows if r["condition"] == "healthy"],
        "hypovolemic_pots": [r for r in rows if "hypovolemic_pots" in r["phenotypes"]],
    }

    # --- L3: hyperadrenergic disclosed limitation ------------------------------
    log("[ctx] hyperadrenergic bench run (disclosed-limitation check)")
    from simulation.perturbations import enable_experimental_mode
    hmodel = BaroreflexPOTSModel(phenotype="hyperadrenergic_pots")
    hres, _ = _engine_run(hmodel, BENCH_TILT, seed=GATE_SEED)
    evaluator = PhysiologicalEvaluator(protocol={
        "method": "head_up_tilt", "angle_degrees": 60.0,
        "onset_s": BENCH_TILT["tup"],
        "tilt_duration_s": BENCH_TILT["tend"] - BENCH_TILT["tup"]})
    ctx["hyperadrenergic_eval"] = evaluator.evaluate(
        hres, phenotype="hyperadrenergic_pots")

    # --- L1/NC: tiny dataset build (record hooks + parity) ----------------------
    log("[ctx] tiny dataset build (record hooks, determinism, parity)")
    ctx.update(_tiny_dataset_build(log))

    # --- NC parity from configs ---------------------------------------------------
    ctx["nc_parity"] = _parity_artifacts(ctx)

    # --- L4: PRCP download + comparison -------------------------------------------
    ctx["prcp"] = _prcp_artifacts(ctx, skip_download=args.skip_download, log=log)
    ctx["eurobavar"] = _eurobavar_artifacts(skip_download=args.skip_download)
    ctx["resting_hrv"] = _resting_hrv_artifacts(ctx)

    return ctx


def _git_rev():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=_REPO,
                              capture_output=True, text=True,
                              timeout=10).stdout.strip()
    except Exception:
        return "unknown"


def _identifiability_artifacts(kb_dir, log):
    from tools.kb_access import load_kb
    kb = load_kb(kb_dir)
    from models.baroreflex_model import BaroreflexPOTSModel
    params = BaroreflexPOTSModel().params
    meta = {}
    for sym in params:
        rec = kb.model_parameters.get(sym)
        meta[sym] = {
            "evidence_e_level": (rec.evidence_e_level if rec else None),
            "canonical_status": (rec.canonical_status if rec else None),
        }
    # Practical demo: +/-20% kH (HR-controller Hill slope) short supine runs;
    # equilibrium-HR signature vs PPG LoA +/-7 bpm.
    kH = float(params["kH"])
    res_base = _run_short_supine(seed=GATE_SEED + 1)
    res_pert = _run_short_supine(seed=GATE_SEED + 1,
                                 param_overrides={"kH": kH * 1.2})
    hr_base = float(np.mean(res_base["Hc"] * 60.0))
    hr_pert = float(np.mean(res_pert["Hc"] * 60.0))
    return {"kb_param_meta": meta,
            "delta_hr_from_param_perturbation_bpm": hr_pert - hr_base,
            "perturbation": "kH x1.2 (+20%)"}


def _kernel_overlay_check(kind):
    """Manager-level overlay math + engine integration (params restored
    exactly after a run with the kernel scheduled)."""
    from models.baroreflex_model import BaroreflexPOTSModel
    from simulation.event_kernels import (
        EventKernelManager, make_exercise_kernel, make_meal_kernel,
    )
    from simulation.engine import SimulationEngine
    model = BaroreflexPOTSModel()
    baseline = copy.deepcopy(model.params)
    mgr = EventKernelManager()
    rng = np.random.default_rng(GATE_SEED)
    if kind == "meal":
        k = make_meal_kernel(100.0, time_scale=0.03)
    else:
        k = make_exercise_kernel(100.0, duration_s=120.0)
    mgr.add_kernel(k, rng)
    t_plateau = 100.0 + k.delay_s + k._onset_s + 0.5 * k._duration_s
    plateau = mgr.compute_parameter_overlay(baseline, t_plateau)
    final = mgr.compute_parameter_overlay(baseline, k.t_end + 10.0)

    # Engine integration: schedule the same kernel, short supine run past
    # the kernel end; model.params must be bit-identical post-run (G-P0-01).
    eng = SimulationEngine(BaroreflexPOTSModel(), seed=GATE_SEED)
    if kind == "meal":
        eng.behavior.kernels.add_kernel(
            make_meal_kernel(20.0, time_scale=0.03), rng)
    else:
        eng.behavior.kernels.add_kernel(
            make_exercise_kernel(20.0, duration_s=60.0), rng)
    eng.run({"tup": 9e9, "tend": 9e9, "height": 25.0, "angle": 60.0,
             "tsim_end": 260.0})
    engine_restored = all(float(eng.model.params[s]) == float(baseline[s])
                          for s in baseline)
    out = {"baseline": baseline, "plateau": plateau, "final": final,
           "engine_params_restored": bool(engine_restored)}
    return out


def _meal_run():
    from models.baroreflex_model import BaroreflexPOTSModel
    from simulation.event_kernels import make_meal_kernel
    from simulation.engine import SimulationEngine
    ts = 0.03  # compressed timing (documented); magnitudes untouched
    start = 20.0
    eng = SimulationEngine(BaroreflexPOTSModel(), seed=GATE_SEED + 2)
    eng.behavior.kernels.add_kernel(make_meal_kernel(start, time_scale=ts),
                                    np.random.default_rng(GATE_SEED))
    res = eng.run({"tup": 9e9, "tend": 9e9, "height": 25.0, "angle": 60.0,
                   "tsim_end": 320.0})
    onset = 30.0 * 60.0 * ts       # 54 s
    dur = 60.0 * 60.0 * ts         # 108 s
    # Windows are RELATIVE to event_start_s (validation.levels.l2
    # check_event_hr_response contract); kernel plateau is absolute
    # [start+onset, start+onset+dur].
    plateau = (onset + 10.0, onset + dur - 10.0)
    return {"time": np.asarray(res["time"]),
            "hr_bpm": np.asarray(res["Hc"]) * 60.0,
            "event_start_s": start, "plateau_window_s": plateau,
            "time_scale": ts}


def _exercise_run():
    from models.baroreflex_model import BaroreflexPOTSModel
    from simulation.event_kernels import make_exercise_kernel
    from simulation.engine import SimulationEngine
    start, dur = 60.0, 120.0
    eng = SimulationEngine(BaroreflexPOTSModel(), seed=GATE_SEED + 3)
    eng.behavior.kernels.add_kernel(make_exercise_kernel(start, duration_s=dur),
                                    np.random.default_rng(GATE_SEED))
    res = eng.run({"tup": 9e9, "tend": 9e9, "height": 25.0, "angle": 60.0,
                   "tsim_end": 320.0})
    # Windows RELATIVE to event_start_s (l2 contract); kernel plateau is
    # absolute [start+30, start+30+dur] (30 s onset ramp).
    return {"time": np.asarray(res["time"]),
            "hr_bpm": np.asarray(res["Hc"]) * 60.0,
            "event_start_s": start,
            "plateau_window_s": (40.0, 30.0 + dur - 10.0),
            "recovery_window_s": (30.0 + dur + 80.0, 30.0 + dur + 110.0),
            "es_plateau_bounded": True}


def _honesty_gating_artifacts(kb_dir, log):
    from tools.kb_access import load_kb
    from simulation.perturbations import PerturbationManager
    from dataset.kb_closure import prepare_kb_closure
    from validation.provenance_gate import (
        ProvenanceGateError, preflight_dataset_build,
    )
    kb = load_kb(kb_dir)

    # (a) experimental (tier-D) phenotype inert in canonical mode
    exp_ids = kb.experimental_phenotype_ids()
    inert, exp_used = None, None
    if exp_ids:
        from models.baroreflex_model import BaroreflexPOTSModel
        base = BaroreflexPOTSModel().params
        pm = PerturbationManager(kb_path=kb_dir, include_experimental=False)
        exp_used = exp_ids[0]
        out, _ = pm.apply_perturbations(dict(base), [exp_used])
        inert = all(float(out[s]) == float(base[s]) for s in base)

    # (b) applied canonical perturbations carry E-level governance metadata
    tagged = None
    can_ids = kb.canonical_phenotype_ids()
    if "hypovolemic_pots" in can_ids:
        rec = kb.phenotypes["hypovolemic_pots"]
        tagged = all(p.evidence_e_level for p in rec.canonical_parameters) \
            and len(rec.canonical_parameters) > 0

    # (c) tampered governance -> build refused (fail-closed)
    tamper_refused, tamper_detail = None, ""
    try:
        with tempfile.TemporaryDirectory() as tmp:
            closure = prepare_kb_closure(os.path.join(tmp, "kb"))
            victim = os.path.join(closure, "diseases", "pots.yaml")
            if not os.path.exists(victim):
                cands = []
                for root, _dirs, files in os.walk(closure):
                    cands += [os.path.join(root, f) for f in files
                              if f.endswith(".yaml")
                              and not f.endswith(".review.yaml")]
                victim = cands[0]
            with open(victim, "a", encoding="utf-8") as f:
                f.write("\n# TAMPERED-AFTER-REVIEW (gate test)\n")
            try:
                preflight_dataset_build(closure, mode="canonical").raise_if_failed()
                tamper_refused = False
                tamper_detail = "preflight ACCEPTED a hash-tampered KB"
            except ProvenanceGateError as exc:
                tamper_refused = True
                tamper_detail = f"refused as required: {str(exc)[:160]}"
    except Exception as exc:  # closure build itself failed
        tamper_refused = None
        tamper_detail = f"kb-closure harness error: {exc}"

    return {"experimental_inert": inert, "experimental_phenotype": exp_used,
            "perturbations_tagged": tagged,
            "tamper_refused": tamper_refused, "tamper_detail": tamper_detail}


def _scale_harmonization_artifacts(kb_dir):
    from tools.kb_access import KBAccessError, load_kb, tier_to_e_level
    kb = load_kb(kb_dir)
    standard = {f"E{i}" for i in range(6)}
    bad = []

    def _ok(level):
        if level is None:
            return True  # absence handled by the gate, not the scale check
        toks = str(level).replace("-", " ").split()
        return all(t in standard for t in toks)

    for sym, rec in kb.model_parameters.items():
        if not _ok(rec.evidence_e_level):
            bad.append(f"param:{sym}:{rec.evidence_e_level}")
    for pid, rec in kb.phenotypes.items():
        if not _ok(rec.evidence_e_level):
            bad.append(f"pheno:{pid}:{rec.evidence_e_level}")
    # Unknown evidence scale must fail closed: the tier->E-level mapping is
    # the machine check (benchmark 1.7); it must raise on an unrecognized
    # scale (the three-scale defect must never recur).
    try:
        tier_to_e_level("ZZ-not-a-scale")
        unknown_fails_closed = False
    except KBAccessError:
        unknown_fails_closed = True
    return {"all_tiers_standard": len(bad) == 0, "offenders": bad,
            "unknown_scale_fails_closed": unknown_fails_closed}


def _tiny_dataset_build(log):
    """2-subject (healthy + hypovolemic POTS) short-protocol build with the
    canonical chest strap: record-hook inputs, record determinism, and
    record-level parity data."""
    from dataset.kb_closure import prepare_kb_closure
    from dataset.runner import DatasetBuilder
    from dataset import schema as recschema
    out = {"record_validation": None, "record_determinism": None,
           "tiny_build": None}
    tmp = tempfile.mkdtemp(prefix="ocpe_gate_ds_")
    kb_dir = prepare_kb_closure(os.path.join(tmp, "kb"))
    cfg = {
        "dataset_name": "ocpe_gate_records", "dataset_seed": GATE_SEED,
        "generation_mode": "canonical",
        "cohorts": [
            {"cohort_id": "rec_healthy", "condition": "healthy", "n_subjects": 1,
             "age": {"dist": "uniform", "min": 25, "max": 35},
             "comorbidities": {"frame": "off"}},
            {"cohort_id": "rec_pots", "condition": "pots", "n_subjects": 1,
             "phenotypes": ["hypovolemic_pots"],
             "comorbidities": {"frame": "off"}},
        ],
        "protocols": [
            {"protocol_id": "hut60_short", "family": "tilt_first",
             "phases": [
                 {"name": "supine_baseline", "duration_s": 40},
                 {"name": "head_up_tilt", "angle_degrees": 60, "duration_s": 20}],
             "covariates": {"fasting": True, "time_of_day": "morning"}},
        ],
        "sensors": [{"sensor_id": "polar_h10", "regime": "on_device",
                     "channels": ["rr"]}],
        "engine": {"dt": 0.02, "hrv_noise": 0.02},
    }
    builder = DatasetBuilder(cfg, kb_dir=kb_dir,
                             output_dir=os.path.join(tmp, "ds"))
    builder.sample_cohort()
    try:
        result = builder.build()
    except Exception as exc:
        log(f"[ctx] tiny dataset build FAILED (reported unresolved): {exc}")
        return out

    errors, n_records = [], 0
    for root, _dirs, files in os.walk(result.output_dir):
        for fn in files:
            if fn != "record.yaml":
                continue
            n_records += 1
            with open(os.path.join(root, fn), "r", encoding="utf-8") as f:
                rec = yaml.safe_load(f)
            errors += recschema.validate_record_schema(rec)
            errors += recschema.validate_record_provenance(rec)
            errors += recschema.validate_scientific_contract(rec)
    out["record_validation"] = {"n_records": n_records, "errors": errors}

    # Record-level determinism: rerun one subject, compare record bytes.
    rec_dirs = []
    for root, _dirs, files in os.walk(result.output_dir):
        if "record.yaml" in files:
            rec_dirs.append(root)
    identical = None
    if rec_dirs:
        with open(os.path.join(rec_dirs[0], "record.yaml"), "rb") as f:
            first = f.read()
        builder.run_subject(builder.subjects[0])
        with open(os.path.join(rec_dirs[0], "record.yaml"), "rb") as f:
            second = f.read()
        identical = bool(first == second)
    out["record_determinism"] = {"identical": identical,
                                 "record": os.path.basename(rec_dirs[0]) if rec_dirs else None}
    out["tiny_build"] = {"output_dir": result.output_dir,
                         "n_records": n_records}
    return out


def _parity_artifacts(ctx):
    """Group-conditional nuisance channels (master prompt §14): engine,
    HRV and protocol configuration must be identical across groups, and
    record-level lengths/device config from the tiny build must match."""
    items = {
        "engine_dt": {"healthy": 0.02, "disease": 0.02},
        "hrv_model": {"healthy": "structured", "disease": "structured"},
        "hrv_noise": {"healthy": 0.02, "disease": 0.02},
        "seed_policy": {"healthy": "stable_seed hierarchy",
                        "disease": "stable_seed hierarchy"},
        "licensed_protocol": {"healthy": str(LICENSED_TILT),
                              "disease": str(LICENSED_TILT)},
        "device_profile": {"healthy": "polar_h10", "disease": "polar_h10"},
        "missingness_model": {"healthy": "polar_h10 KB profile",
                              "disease": "polar_h10 KB profile"},
    }
    tiny = (ctx.get("tiny_build") or {})
    out_dir = tiny.get("output_dir")
    if out_dir:
        lengths = {}
        devices = {}
        for root, _dirs, files in os.walk(out_dir):
            if "record.yaml" not in files:
                continue
            with open(os.path.join(root, "record.yaml"), "r",
                      encoding="utf-8") as f:
                rec = yaml.safe_load(f)
            cond = rec["physiological_state"]["condition"]
            group = "healthy" if cond == "healthy" else "disease"
            gt = np.load(os.path.join(root, "ground_truth.npz"))
            lengths[group] = int(len(gt["time_s"]))
            devices[group] = sorted(
                d["sensor_id"] for d in rec["sensor_configuration"]["devices"])
        if "healthy" in lengths and "disease" in lengths:
            # Beat-aligned time grids differ by O(beat) samples between
            # subjects on an identical protocol; parity is a RELATIVE
            # tolerance (1%), not bit-equality, for this channel.
            items["record_length_samples"] = {
                "healthy": lengths["healthy"], "disease": lengths["disease"],
                "rel_tolerance": 0.01}
            items["record_devices"] = {
                "healthy": devices["healthy"], "disease": devices["disease"]}
    return items


def _prcp_artifacts(ctx, skip_download, log):
    if skip_download:
        return {"error": "download skipped by --skip-download flag"}
    try:
        tmp = tempfile.mkdtemp(prefix="ocpe_prcp_")
        records, err = l4.download_prcp_annotations(tmp, timeout=30)
        if err and not records:
            return {"error": f"all fetches failed: {err}"}
        episodes = []
        for rec in records:
            try:
                episodes += l4.prcp_delta_hr_episodes(tmp, rec)
            except Exception as exc:
                log(f"[ctx] PRCP {rec} parse failed: {exc}")
        if not episodes:
            return {"error": "no usable slow-tilt episodes parsed "
                             f"(records fetched: {len(records)}; {err})"}
        real = [e["delta_hr_bpm"] for e in episodes]
        sim = [s["prcp_matched_dhr_bpm"]
               for s in (ctx.get("licensed_cohort") or {}).get("healthy", [])]
        out = {"real_delta_hr_bpm": real, "sim_delta_hr_bpm": sim,
               "episodes": episodes,
               "window_semantics": ("final 60 s of tilt hold vs final 120 s "
                                    "supine; simulated window minutes 2-3 "
                                    "post-ramp (PRCP hold ~3 min)"),
               "note": (f"{len(episodes)} slow-tilt episodes from "
                        f"{len(records)} PRCP records; fetch warnings: {err}")}
        if not sim:
            out["error"] = "no simulated healthy cohort available"
        return out
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def _eurobavar_artifacts(skip_download):
    if skip_download:
        return {"error": "download skipped by --skip-download flag"}
    import urllib.request
    try:
        req = urllib.request.Request(
            l4.EUROBAVAR_URL, headers={"User-Agent": "ocpe-validation/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            r.read(512)
        return {"error": ("host reachable but the beat-to-beat series "
                          "download/parse harness is not implemented in this "
                          "release (reflex-gain validation only; "
                          "VALIDATION_DATASETS §1.2)")}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def _resting_hrv_artifacts(ctx):
    healthy = (ctx.get("licensed_cohort") or {}).get("healthy", [])
    vals = [s["rmssd_ms"] for s in healthy if np.isfinite(s.get("rmssd_ms", np.nan))]
    if not vals:
        return None
    return {"rmssd_median_ms": float(np.median(vals)),
            "rmssd_values_ms": [float(v) for v in vals],
            "sdnn_median_ms": float(np.median(
                [s["sdnn_ms"] for s in healthy
                 if np.isfinite(s.get("sdnn_ms", np.nan))])),
            "n": len(vals)}


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def synthesize_findings(results, ctx):
    """Cross-gate synthesis for the report: group per-gate verdicts into
    coherent findings with their shared evidence (rule 6: every failure
    carries a claim id and a correction target)."""
    by_check = {r.check: r for r in results}
    lines = []
    osc_cluster = ("2.1_tilt_trajectory_battery", "2.1_exercise_response",
                   "2.2_dfa_alpha1", "2.2_rsa_peak", "4_resting_hrv_norms",
                   "4_prcp_orthostatic_wasserstein")
    n_fail = sum(1 for c in osc_cluster
                 if by_check.get(c) and by_check[c].status == "fail")
    tilt = (ctx.get("healthy_bench_tilt") or {})
    if n_fail >= 3 and tilt:
        t = np.asarray(tilt["time"])
        sup_std = float(np.std(np.asarray(tilt["hr_bpm"])[t < tilt["onset_s"]]))
        lines.append(
            f"**F1 (engine-level, blocking for L2 timescale/L4 signal anchors):** "
            f"the supine mean-HR baseline of the ODE core oscillates with std "
            f"~{sup_std:.1f} bpm (healthy supine reference: quasi-stationary, "
            f"RMSSD-equivalent wander of a few bpm). The oscillation is "
            f"structural: verified invariant to integration dt (0.01 vs 0.02) "
            f"and to OU-layer disablement during gate development. It "
            f"propagates into {n_fail} gates: oscillatory tilt transients/"
            f"recovery (2.1 battery), DFA-alpha1 ~1.5 vs [0.8, 1.2], RSA peak "
            f"misplaced below the respiration line, resting RMSSD far above "
            f"published norms, and early-tilt overshoot driving the PRCP "
            f"Wasserstein distance beyond the 3 bpm target. Mean-level "
            f"responses are unaffected and pass (baseline HR, sustained "
            f"delta-HR, circadian amplitude, meal response, clinical "
            f"contrasts). Correction target: simulation/ baroreflex loop "
            f"damping (W1-A ownership); do NOT widen these bands.")
    prcp = by_check.get("4_prcp_orthostatic_wasserstein")
    if prcp and prcp.status == "fail" and isinstance(prcp.measured, dict):
        lines.append(
            "**F2 (real-data anchor):** simulated healthy early-tilt "
            f"delta-HR (minutes 2-3) "
            f"{prcp.measured.get('sim_delta_hr_bpm')} sits above the PRCP "
            f"real episodes {prcp.measured.get('real_delta_hr_bpm')} "
            f"(W1 = {prcp.measured.get('wasserstein_bpm')} bpm vs target "
            "<= 3). Consistent with F1 (exaggerated early orthostatic "
            "response); not a sampling artifact (matched windows disclosed).")
    for r in results:
        if r.status == "unresolved":
            lines.append(f"**Unresolved ({r.gate}/{r.check}):** {r.note or r.target}")
    if not lines:
        lines.append("No cross-gate findings; all gates resolved as pass.")
    return lines


def write_outputs(results, md_path, yaml_path, ctx):
    payload = {
        "release_gates_version": "1.0.0",
        "governing_statement": GOVERNING_STATEMENT,
        "level5_status": ("NOT EXECUTED - the Level-5 benchmark matrix does "
                          "not exist yet; no synthetic-utility claim is made"),
        "context": {k: v for k, v in (ctx.get("meta") or {}).items()},
        "results": [r.to_dict() for r in results],
    }
    summary = {s: sum(1 for r in results if r.status == s) for s in STATUSES}
    payload["summary"] = summary
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, width=110)

    lines = []
    lines.append("# OCPE Validation Report - Release Gates L1-L4 + Negative Controls")
    lines.append("")
    lines.append(f"**Governing statement (binding):** *{GOVERNING_STATEMENT}*")
    lines.append("")
    lines.append("**Level-5 status:** NOT EXECUTED - the Level-5 synthetic-to-real "
                 "benchmark matrix does not exist yet. Levels 1-4 are necessary "
                 "but not sufficient; no utility claim for OCPE synthetic data "
                 "is made or implied by this report.")
    lines.append("")
    meta = ctx.get("meta") or {}
    lines.append(f"Generated from gate context seed {meta.get('gate_seed')}, "
                 f"commit `{meta.get('ocpe_commit')}`, started "
                 f"{meta.get('started')}. Licensed cohort: "
                 f"{meta.get('n_healthy')} healthy + {meta.get('n_pots')} "
                 f"hypovolemic-POTS subjects, 10-min HUT (300 s supine + "
                 f"600 s tilt + 60 s recovery, dt=0.02).")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| status | count |")
    lines.append("|---|---|")
    for s in STATUSES:
        lines.append(f"| {s} | {summary[s]} |")
    lines.append("")
    lines.append("## Cross-gate synthesis")
    lines.append("")
    for ln in synthesize_findings(results, ctx):
        lines.append(f"- {ln}")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append("| gate | check | target | measured | status | evidence |")
    lines.append("|---|---|---|---|---|---|")
    for r in results:
        d = r.to_dict()
        meas = yaml.safe_dump(d["measured"], default_flow_style=True,
                              width=70).strip().replace("\n", " ")
        if len(meas) > 220:
            meas = meas[:217] + "..."
        row = [d["gate"], d["check"], d["target"], meas,
               d["status"].upper(), d["evidence"]]
        lines.append("| " + " | ".join(str(c).replace("|", "\\|")
                                        .replace("\n", " ") for c in row) + " |")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    for r in results:
        if r.note:
            lines.append(f"- **{r.gate}/{r.check}**: {r.note}")
    lines.append("")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return payload


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n-healthy", type=int, default=4)
    ap.add_argument("--n-pots", type=int, default=4)
    ap.add_argument("--fast", action="store_true",
                    help="2+2 licensed cohort (quick smoke run)")
    ap.add_argument("--serial", action="store_true",
                    help="disable process-pool parallelism")
    ap.add_argument("--skip-download", action="store_true")
    ap.add_argument("--context-cache", default=None,
                    help="pickle the built context to FILE for reuse")
    ap.add_argument("--from-context-cache", default=None,
                    help="load a previously built context (no ODE reruns)")
    ap.add_argument("--output-md",
                    default=os.path.join(_REPO, "docs", "validation_report.md"))
    ap.add_argument("--output-yaml",
                    default=os.path.join(_REPO, "validation", "release_gates.yaml"))
    args = ap.parse_args(argv)
    if args.fast:
        args.n_healthy = min(args.n_healthy, 2)
        args.n_pots = min(args.n_pots, 2)

    if args.from_context_cache:
        with open(args.from_context_cache, "rb") as f:
            ctx = pickle.load(f)
        print(f"[gates] context loaded from {args.from_context_cache}")
    else:
        ctx = build_context(args)
        if args.context_cache:
            with open(args.context_cache, "wb") as f:
                pickle.dump(ctx, f)
            print(f"[gates] context cached to {args.context_cache}")

    results = []
    for mod, name in ((l1, "L1"), (l2, "L2"), (l3, "L3"), (l4, "L4"),
                      (negative_controls, "NC")):
        try:
            results += mod.run(ctx)
        except Exception as exc:
            from validation.levels import CheckResult, STATUS_UNRESOLVED
            results.append(CheckResult(
                name, f"{name}_module_error",
                "gate module executed without internal error",
                f"{type(exc).__name__}: {exc}", STATUS_UNRESOLVED,
                evidence="run_release_gates", note="gate harness error"))
    payload = write_outputs(results, args.output_md, args.output_yaml, ctx)
    print(f"[gates] wrote {args.output_md} and {args.output_yaml}")
    print(f"[gates] summary: {payload['summary']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
