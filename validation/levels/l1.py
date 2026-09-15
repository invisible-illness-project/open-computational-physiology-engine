"""Level 1 - MATHEMATICAL VALIDITY (SYNTHETIC_TO_REAL_BENCHMARK.md §L1).

Checks (anchors in the benchmark table):
  1.2  Blood-volume mass conservation in the ODE core.
  1.4  Identifiability guards: ODE parameters are population priors with
       documented uncertainty, never per-subject estimates (structural
       guard + practical non-identifiability demonstration).
  1.5  Determinism / reproducibility: same seed -> bit-identical output.
  1.6  Honesty gating: tier-D / experimental parameters inert in canonical
       mode; applied perturbations carry E-level + provenance tags; the
       provenance gate aborts a build on missing/tampered governance.
  1.7  Scale harmonization: every consumed evidence tier maps to the
       standard E0-E5 scale; unknown scales fail closed to experimental.
  G-P0-01 regression: event-kernel baseline restoration (parameters return
       EXACTLY to baseline after event recovery; bounded plateau).
  dataset/schema.py hooks: validate_record_schema / validate_record_provenance
       / validate_scientific_contract must pass on every emitted record.

Checks that need engine/dataset artifacts read them from the shared gate
context (built once by run_release_gates.py); when an artifact is absent
the check degrades to ``unresolved`` with the exact reason (rule 1) -
the pure check functions below are unit-testable without the engine.
"""

from __future__ import annotations

import numpy as np

from validation.levels import (
    STATUS_FAIL, STATUS_PASS, STATUS_UNRESOLVED, CheckResult,
)

# ---------------------------------------------------------------------------
# Pure check functions (unit-testable, engine-free)
# ---------------------------------------------------------------------------

def check_volume_conservation(volumes_ml: np.ndarray,
                              total_vol_ml: np.ndarray,
                              rtol: float = 1e-6):
    """L1 1.2 mass conservation in the ODE core.

    The Geddes-scale baroreflex state convention stores STRESSED volumes
    per compartment (p = V_stressed/C); the unstressed remainder of
    TotalVol is implicit in the pressure-volume relations.  The machine
    invariant is therefore:
      (a) numerical conservation: sum_i V_i(t) constant to rtol*TotalVol
          across the whole run (ODE flows redistribute, never create or
          destroy volume; non-negativity clamps inactive nominally), AND
      (b) the implicit unstressed offset (TotalVol - sum_i V_i) constant
          to the same tolerance.
    volumes_ml: [N, 5] columns (Vau, Vvu, Val, Vvl, Vlv).
    total_vol_ml: [N] defended total volume series (engine blood_volume
    channel = params['TotalVol']).
    """
    vols = np.asarray(volumes_ml, dtype=float)
    tot = np.asarray(total_vol_ml, dtype=float)
    s = vols.sum(axis=1)
    denom = max(abs(float(tot[0])), 1e-9)
    drift_rel = float(np.abs(s - s[0]).max() / denom)
    offset = tot - s
    offset_rel = float(np.abs(offset - offset[0]).max() / denom)
    passed = bool(drift_rel < rtol and offset_rel < rtol)
    return passed, {
        "max_sumV_drift_ml": float(np.abs(s - s[0]).max()),
        "drift_rel_totalvol": drift_rel,
        "unstressed_offset_ml": float(offset[0]),
        "offset_drift_rel": offset_rel,
        "n_steps": int(vols.shape[0]), "rtol": rtol,
        "convention": ("state compartments are STRESSED volumes (p=V/C); "
                       "unstressed remainder implicit and constant "
                       "(Geddes-scale ODE)"),
    }


def check_kernel_baseline_restoration(baseline: dict, plateau: dict,
                                      final: dict, symbol: str,
                                      plateau_factor: float,
                                      rtol_plateau: float = 0.02):
    """G-P0-01 regression: a parameter perturbed by an event kernel equals
    baseline*plateau_factor during the plateau (multiplicative vs BASELINE)
    and returns EXACTLY to baseline after recovery."""
    b = float(baseline[symbol])
    p = float(plateau[symbol])
    f = float(final[symbol])
    plateau_ok = abs(p - b * plateau_factor) <= rtol_plateau * abs(
        b * plateau_factor)
    restored_ok = bool(f == b)
    return plateau_ok and restored_ok, {
        "symbol": symbol, "baseline": b, "plateau": p,
        "expected_plateau": b * plateau_factor, "final": f,
        "plateau_ok": bool(plateau_ok), "restored_exactly": restored_ok,
    }


def check_determinism(arrays_a: dict, arrays_b: dict):
    """L1 1.5: same seed -> bit-identical output arrays."""
    diffs = {}
    for k in arrays_a:
        if k not in arrays_b:
            diffs[k] = "missing_in_rerun"
            continue
        a, b = np.asarray(arrays_a[k]), np.asarray(arrays_b[k])
        if a.shape != b.shape or not np.array_equal(a, b):
            diffs[k] = "differs"
    extra = [k for k in arrays_b if k not in arrays_a]
    for k in extra:
        diffs[k] = "missing_in_first"
    return len(diffs) == 0, {"keys_compared": sorted(arrays_a.keys()),
                             "mismatches": diffs}


def check_identifiability_enforcement(kb_param_meta: dict):
    """L1 1.4 structural guard: every engine-consumed ODE parameter is a
    population prior carrying governance metadata (evidence E-level and
    canonical status), i.e. fixed to literature distributions and never a
    per-subject estimate.

    kb_param_meta: {symbol: {"evidence_e_level": str|None,
                             "canonical_status": str|None}}.
    """
    missing = sorted(sym for sym, m in kb_param_meta.items()
                     if not m.get("evidence_e_level"))
    return len(missing) == 0, {
        "n_parameters": len(kb_param_meta),
        "missing_e_level": missing,
        "semantics": ("population priors with documented uncertainty; "
                      "never per-subject estimates (EVD-TEMP-010)"),
    }


def practical_identifiability_demo(delta_hr_bpm: float,
                                   noise_loa_bpm: float = 7.0):
    """L1 1.4 practical guard: a +/-20% perturbation of an internal ODE
    parameter whose observable (PPG-grade, LoA +/-7 bpm) signature is
    smaller than the measurement noise is structurally non-identifiable
    at the wearable channel and must remain labeled as such."""
    non_identifiable = abs(delta_hr_bpm) < noise_loa_bpm
    return non_identifiable, {
        "delta_hr_bpm_from_param_perturbation": float(delta_hr_bpm),
        "observation_noise_loa_bpm": noise_loa_bpm,
        "label": "non_identifiable" if non_identifiable else "recoverable",
    }


# ---------------------------------------------------------------------------
# Gate assembly from the shared context
# ---------------------------------------------------------------------------

def run(ctx: dict) -> list:
    """Assemble all Level-1 checks from the gate context."""
    results = []

    # --- 1.5 determinism (engine-level) -----------------------------------
    det = ctx.get("det_runs")
    if det is None:
        results.append(CheckResult(
            "L1", "1.5_determinism",
            "same seed -> bit-identical engine output (1.5)",
            None, STATUS_UNRESOLVED,
            evidence="SYNTHETIC_TO_REAL_BENCHMARK L1.5",
            note="context artifact 'det_runs' not provided"))
    else:
        keys = ("time", "Hc", "pau", "Vau", "rr_intervals_ms")
        a = {k: det["run_a"][k] for k in keys if k in det["run_a"]}
        b = {k: det["run_b"][k] for k in keys if k in det["run_b"]}
        ok, meas = check_determinism(a, b)
        results.append(CheckResult(
            "L1", "1.5_determinism",
            "same seed -> bit-identical engine output (time/state/RR)",
            meas, STATUS_PASS if ok else STATUS_FAIL,
            evidence="SYNTHETIC_TO_REAL_BENCHMARK L1.5; engine seeded-determinism precedent"))

    # --- 1.2 blood-volume conservation -------------------------------------
    cons = ctx.get("conservation")
    if cons is None:
        results.append(CheckResult(
            "L1", "1.2_volume_conservation",
            "sum V_i constant < 1e-6*TotalVol drift; implicit unstressed "
            "offset constant (1.2)",
            None, STATUS_UNRESOLVED,
            evidence="L1.2; Geddes-scale ODE",
            note="context artifact 'conservation' not provided"))
    else:
        ok, meas = check_volume_conservation(cons["volumes_ml"],
                                             cons["total_vol_ml"])
        results.append(CheckResult(
            "L1", "1.2_volume_conservation",
            "ODE mass conservation: sum(stressed V_i) drift < 1e-6*TotalVol "
            "over a full tilt run; unstressed offset constant",
            meas, STATUS_PASS if ok else STATUS_FAIL,
            evidence="L1.2; Geddes-scale ODE (EVD-TEMP-003 context)",
            note="state convention: compartments hold STRESSED volumes; "
                 "benchmark 1.2 invariant applied to the conserved quantity"))

    # --- G-P0-01 kernel baseline restoration (meal + exercise) -------------
    for art, sym, factor in (("meal_kernel_check", "RalpM", 0.75),
                             ("exercise_kernel_check", "Es", 1.30)):
        kc = ctx.get(art)
        cid = "meal_postprandial_pooling" if sym == "RalpM" else "exercise_bout"
        if kc is None:
            results.append(CheckResult(
                "L1", f"kernel_restoration_{sym.lower()}",
                f"{cid}: plateau {sym} = baseline x{factor}; EXACT baseline after recovery",
                None, STATUS_UNRESOLVED,
                evidence="G-P0-01; SWARM_SPEC W1-A",
                note=f"context artifact '{art}' not provided"))
        else:
            ok, meas = check_kernel_baseline_restoration(
                kc["baseline"], kc["plateau"], kc["final"], sym, factor)
            results.append(CheckResult(
                "L1", f"kernel_restoration_{sym.lower()}",
                f"{cid}: plateau {sym} = baseline x{factor}; EXACT baseline after recovery",
                meas, STATUS_PASS if ok else STATUS_FAIL,
                evidence="G-P0-01 compounding fix; EVD-HLTH-006 timing"))

    # --- 1.4 identifiability guards ----------------------------------------
    ident = ctx.get("identifiability")
    if ident is None:
        results.append(CheckResult(
            "L1", "1.4_identifiability",
            "ODE params = population priors w/ documented uncertainty; "
            "non-recoverable params labeled non_identifiable (1.4)",
            None, STATUS_UNRESOLVED, evidence="L1.4; EVD-TEMP-010",
            note="context artifact 'identifiability' not provided"))
    else:
        ok_s, meas_s = check_identifiability_enforcement(ident["kb_param_meta"])
        non_id, meas_p = practical_identifiability_demo(
            ident["delta_hr_from_param_perturbation_bpm"])
        meas = {"structural": meas_s, "practical_demo": meas_p,
                "parameter_semantics": "population priors, never per-subject estimates"}
        results.append(CheckResult(
            "L1", "1.4_identifiability",
            "all ODE params carry E-level governance metadata; +/-20% kH "
            "perturbation below PPG LoA +/-7 bpm -> non_identifiable",
            meas, STATUS_PASS if (ok_s and non_id) else STATUS_FAIL,
            evidence="L1.4; EVD-TEMP-010 (structural unidentifiability, E4)",
            note=("ODE parameters are population priors with documented "
                  "uncertainty, never per-subject estimates")))

    # --- 1.6 honesty gating -------------------------------------------------
    hon = ctx.get("honesty_gating")
    if hon is None:
        results.append(CheckResult(
            "L1", "1.6_honesty_gating",
            "tier-D inert in canonical mode; applied params carry E-level + "
            "provenance; build aborts on tampered governance (1.6)",
            None, STATUS_UNRESOLVED,
            evidence="L1.6; EVIDENCE_AUDIT_NOTES §e CI rule",
            note="context artifact 'honesty_gating' not provided"))
    else:
        ok = bool(hon["experimental_inert"] and hon["perturbations_tagged"]
                  and hon["tamper_refused"])
        results.append(CheckResult(
            "L1", "1.6_honesty_gating",
            "tier-D inert in canonical mode; perturbations carry E-level + "
            "claim ids; provenance gate refuses hash-tampered KB",
            hon, STATUS_PASS if ok else STATUS_FAIL,
            evidence="L1.6; EVIDENCE_AUDIT_NOTES §e; ADR 0001"))

    # --- 1.7 scale harmonization -------------------------------------------
    sc = ctx.get("scale_harmonization")
    if sc is None:
        results.append(CheckResult(
            "L1", "1.7_scale_harmonization",
            "all consumed evidence tiers map to standard E0-E5; unknown "
            "scale fails closed (1.7)",
            None, STATUS_UNRESOLVED,
            evidence="L1.7; EVIDENCE_AUDIT_NOTES §0",
            note="context artifact 'scale_harmonization' not provided"))
    else:
        ok = bool(sc["all_tiers_standard"] and sc["unknown_scale_fails_closed"])
        results.append(CheckResult(
            "L1", "1.7_scale_harmonization",
            "consumed KB tiers map to E0-E5; unrecognized tier -> EXPERIMENTAL "
            "(fail-closed)",
            sc, STATUS_PASS if ok else STATUS_FAIL,
            evidence="L1.7; EVIDENCE_AUDIT_NOTES §0 action item"))

    # --- dataset/schema.py hooks on built records ---------------------------
    rec = ctx.get("record_validation")
    if rec is None:
        results.append(CheckResult(
            "L1", "schema_provenance_contract_hooks",
            "validate_record_schema/provenance/scientific_contract pass on "
            "every emitted record",
            None, STATUS_UNRESOLVED,
            evidence="dataset/schema.py hooks; OCPE_DATASET_SPECIFICATION §0",
            note="context artifact 'record_validation' not provided"))
    else:
        ok = rec["n_records"] > 0 and not rec["errors"]
        results.append(CheckResult(
            "L1", "schema_provenance_contract_hooks",
            "dataset/schema.py hooks (schema + provenance + scientific "
            "contract incl. latent-boundary guard) pass on all records",
            rec, STATUS_PASS if ok else STATUS_FAIL,
            evidence="dataset/schema.py; master prompt §18/§21; rule 3"))

    # --- record-level determinism -------------------------------------------
    rdet = ctx.get("record_determinism")
    if rdet is None:
        results.append(CheckResult(
            "L1", "1.5_record_determinism",
            "same seeds -> byte-identical dataset records (1.5)",
            None, STATUS_UNRESOLVED,
            evidence="L1.5; dataset deterministic build clock",
            note="context artifact 'record_determinism' not provided"))
    else:
        results.append(CheckResult(
            "L1", "1.5_record_determinism",
            "same dataset_seed -> byte-identical record.yaml/derived.json",
            rdet, STATUS_PASS if rdet["identical"] else STATUS_FAIL,
            evidence="L1.5; dataset/schema.py deterministic_build_timestamp"))

    return results
