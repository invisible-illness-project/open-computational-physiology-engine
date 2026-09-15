"""Physiological evaluator with FROZEN canonical orthostatic metric semantics.

Gap G-P0-09 (docs/evidence_package/OCPE_RESEARCH_GAP_ANALYSIS.md): the healthy
orthostatic reference is protocol-conditioned and the evaluator previously used
a PEAK delta-HR in the first 60 s of tilt (inflated by the steep-Hill limit
cycle) while the acceptance tests used a SUSTAINED metric - two different
metrics were gating "POTS vs healthy".

Canonical metric semantics (binding for model, tests, evaluator and the W2-F
dataset generator; frozen in validation/healthy_reference.yaml and
docs/orthostatic_reference.md):

    sustained_delta_HR = mean(HR, minutes 5-10 of tilt)
                         - mean(HR, final 5 min supine)
    initial_transient  = max(HR, first 30 s post-onset)
                         - mean(HR, final 5 min supine)

The initial transient (seconds) and the sustained response (minutes) are
DIFFERENT physiological phases (HEALTHY dossier section 3.1, E3) and must
never be conflated into a single delta-HR number.

Short simulated protocols (the repo bench protocol is 200 s supine + 100 s of
60 deg tilt, so minutes 5-10 of tilt do not exist) fall back to a stabilized
sustained PROXY window (final 40 s of tilt) that is explicitly flagged
``sustained_window_kind = "short_protocol_proxy"``. The clinical >=30 bpm POTS
criterion is evidence-licensed only for standardized 10-min active-stand or
10-min tilt protocols (CONTRADICTION_AUDIT Target 1); on the bench proxy the
comparison is a continuity check, not a validated clinical claim.
"""

import os

import numpy as np
import yaml
from scipy.signal import find_peaks

# ---------------------------------------------------------------------------
# Canonical orthostatic metric semantics (G-P0-09 freeze) - SINGLE definition
# ---------------------------------------------------------------------------

#: Initial transient window: first 30 s after tilt/stand onset.
TRANSIENT_WINDOW_S = (0.0, 30.0)
#: Sustained (diagnostic) window: minutes 5-10 after tilt/stand onset.
SUSTAINED_WINDOW_S = (300.0, 600.0)
#: Baseline window: final 5 min of supine rest before onset.
BASELINE_WINDOW_S = 300.0
#: Short-protocol fallback: stabilized proxy = final 40 s of the tilt phase.
BENCH_SUSTAINED_TAIL_S = 40.0

_REFERENCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "healthy_reference.yaml")

#: POTS diagnostic boundary (adults), licensed only for 10-min protocols.
POTS_SUSTAINED_CRITERION_BPM = 30.0


def compute_orthostatic_metrics(time, hr_bpm, onset_s, tilt_duration_s,
                                baseline_window_s=BASELINE_WINDOW_S):
    """Canonical orthostatic HR metrics (single binding definition, G-P0-09).

    Parameters
    ----------
    time : array-like
        Simulation/sample times in seconds.
    hr_bpm : array-like
        Heart rate in bpm aligned with ``time``.
    onset_s : float
        Tilt/stand onset time in seconds.
    tilt_duration_s : float
        Duration of the upright (tilt/stand) phase in seconds.
    baseline_window_s : float, optional
        Supine baseline window (seconds before onset). Default: final 5 min
        supine. If less supine data is available, all available supine
        samples are used and the actual window is reported.

    Returns
    -------
    dict with keys
        baseline_hr_bpm, baseline_window_s,
        initial_transient_bpm (peak, first 30 s), initial_transient_mean_bpm,
        sustained_delta_HR_bpm, sustained_window_s, sustained_window_kind
        ("minutes_5_10" | "short_protocol_proxy" | "unresolved").
    """
    time = np.asarray(time, dtype=float)
    hr_bpm = np.asarray(hr_bpm, dtype=float)

    # Baseline: final 5 min supine (or all available supine if shorter,
    # explicitly reported via baseline_window_s).
    sup_lo = max(float(time.min()), onset_s - float(baseline_window_s))
    sup_mask = (time >= sup_lo) & (time < onset_s)
    if not np.any(sup_mask):
        raise ValueError("no supine baseline samples before onset_s")
    baseline_hr = float(np.mean(hr_bpm[sup_mask]))
    baseline_window = (float(time[sup_mask].min()), float(onset_s))

    # Initial transient: first 30 s post-onset (peak AND mean, kept separate
    # from the sustained phase - never conflate).
    tr_mask = ((time >= onset_s + TRANSIENT_WINDOW_S[0])
               & (time < onset_s + TRANSIENT_WINDOW_S[1]))
    if np.any(tr_mask):
        transient_peak = float(np.max(hr_bpm[tr_mask]) - baseline_hr)
        transient_mean = float(np.mean(hr_bpm[tr_mask]) - baseline_hr)
    else:
        transient_peak = float("nan")
        transient_mean = float("nan")

    # Sustained phase.
    if tilt_duration_s >= SUSTAINED_WINDOW_S[1]:
        # Full diagnostic window: minutes 5-10 of tilt.
        win = (onset_s + SUSTAINED_WINDOW_S[0], onset_s + SUSTAINED_WINDOW_S[1])
        kind = "minutes_5_10"
    elif tilt_duration_s > TRANSIENT_WINDOW_S[1] + BENCH_SUSTAINED_TAIL_S:
        # Short bench protocol: stabilized proxy = final 40 s of tilt.
        win = (onset_s + tilt_duration_s - BENCH_SUSTAINED_TAIL_S,
               onset_s + tilt_duration_s)
        kind = "short_protocol_proxy"
    else:
        win = None
        kind = "unresolved"

    if win is not None:
        sus_mask = (time >= win[0]) & (time < win[1])
        if not np.any(sus_mask):
            kind = "unresolved"
            sustained = float("nan")
        else:
            sustained = float(np.mean(hr_bpm[sus_mask]) - baseline_hr)
    else:
        sustained = float("nan")

    return {
        "baseline_hr_bpm": baseline_hr,
        "baseline_window_s": baseline_window,
        "initial_transient_bpm": transient_peak,
        "initial_transient_mean_bpm": transient_mean,
        "transient_window_s": (onset_s + TRANSIENT_WINDOW_S[0],
                               onset_s + TRANSIENT_WINDOW_S[1]),
        "sustained_delta_HR_bpm": sustained,
        "sustained_window_s": win,
        "sustained_window_kind": kind,
    }


def load_healthy_reference(path=None):
    """Load the frozen protocol-conditioned healthy orthostatic reference."""
    with open(path or _REFERENCE_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def match_reference_protocol(reference, method, angle_degrees=None,
                             duration_s=None, supine_rest_s=None):
    """Return the reference protocol_id matching a simulated protocol, or None.

    Protocol conditioning is mandatory (tilt != stand != lean;
    CONTRADICTION_AUDIT Target 1): a simulated distribution may only be
    compared against a reference entry whose method, angle, duration class
    and supine-rest class match. Matching duration class requires the
    simulated upright phase to cover the reference entry's sustained window
    (minutes 5-10). Supine-rest bounds disambiguate casual vs lab stands.
    """
    protocols = reference.get("protocols", {})
    for pid, entry in protocols.items():
        if entry.get("method") != method:
            continue
        angles = entry.get("angle_degrees")
        if angles is not None and angle_degrees is not None:
            lo, hi = (angles if isinstance(angles, (list, tuple))
                      else (angles, angles))
            if not (lo <= angle_degrees <= hi):
                continue
        req = entry.get("required_tilt_duration_s")
        if req is not None and duration_s is not None and duration_s < req:
            continue
        min_sup = entry.get("min_supine_rest_s")
        if min_sup is not None and (supine_rest_s is None
                                    or supine_rest_s < min_sup):
            continue
        max_sup = entry.get("max_supine_rest_s")
        if max_sup is not None and (supine_rest_s is None
                                    or supine_rest_s > max_sup):
            continue
        return pid
    return None


def compare_distribution_to_reference(samples, protocol_id, reference=None,
                                      mean_tolerance_bpm=5.0,
                                      allow_noncanonical_window=False):
    """Compare a simulated cohort of sustained delta-HR samples against the
    frozen healthy reference for a SPECIFIC protocol (tilt != stand != lean).

    Both the central tendency AND the upper tail are compared - the healthy
    false-positive fraction at the 30-bpm boundary is a protocol property
    (<5% casual stand up to ~60% on 10-min tilt) and must be preserved, never
    collapsed to a single threshold.

    ``samples`` must be computed with the canonical sustained window
    (minutes 5-10). Reference entries that define a different
    ``sustained_window_s`` (e.g. the 30-min tilt entry) require
    ``allow_noncanonical_window=True`` and samples computed on THAT window -
    window mismatch would silently conflate protocols.
    """
    reference = reference or load_healthy_reference()
    entry = reference["protocols"].get(protocol_id)
    if entry is None:
        raise KeyError(f"unknown reference protocol_id '{protocol_id}'")
    entry_window = entry.get("sustained_window_s")
    if (entry_window is not None
            and list(entry_window) != [SUSTAINED_WINDOW_S[0], SUSTAINED_WINDOW_S[1]]
            and not allow_noncanonical_window):
        raise ValueError(
            f"reference protocol '{protocol_id}' uses sustained window "
            f"{entry_window}, not the canonical minutes 5-10; pass samples "
            f"computed on that window with allow_noncanonical_window=True")

    samples = np.asarray(samples, dtype=float)
    dist = entry["sustained_delta_HR_bpm"]
    tail = entry["fraction_exceeding_30bpm"]

    sample_mean = float(np.mean(samples))
    sample_sd = float(np.std(samples, ddof=1)) if samples.size > 1 else 0.0
    sample_frac30 = float(np.mean(samples >= POTS_SUSTAINED_CRITERION_BPM))

    mean_ok = abs(sample_mean - dist["mean"]) <= max(
        mean_tolerance_bpm, 2.0 * dist.get("sd", 0.0))
    tail_lo = tail.get("min", 0.0)
    tail_hi = tail.get("max", tail.get("point", 1.0))
    tail_ok = tail_lo <= sample_frac30 <= tail_hi

    return {
        "protocol_id": protocol_id,
        "n_samples": int(samples.size),
        "sample_mean_bpm": sample_mean,
        "sample_sd_bpm": sample_sd,
        "sample_fraction_ge_30bpm": sample_frac30,
        "reference_mean_bpm": dist["mean"],
        "reference_sd_bpm": dist.get("sd"),
        "reference_fraction_ge_30bpm": tail,
        "mean_within_reference": bool(mean_ok),
        "tail_within_reference": bool(tail_ok),
        "consistent_with_healthy_reference": bool(mean_ok and tail_ok),
        "evidence_level": entry.get("evidence_level"),
        "sources": entry.get("sources"),
    }


class PhysiologicalEvaluator:
    """
    Evaluates simulation results for physiological plausibility,
    clinical diagnostic criteria compliance, and autonomic response dynamics.

    Orthostatic delta-HR semantics are the FROZEN canonical ones (see module
    docstring): sustained_delta_HR (minutes 5-10 of tilt, or the flagged
    short-protocol proxy) is the clinical/acceptance metric; the initial
    transient (first 30 s) is recorded separately and never used for the
    POTS criterion.
    """

    #: Repo bench protocol (knowledge_base/interventions/tilt_test.yaml):
    #: 200 s supine, 14 s ramp, 100 s of 60 deg passive head-up tilt.
    DEFAULT_PROTOCOL = {
        "method": "head_up_tilt",
        "angle_degrees": 60.0,
        "onset_s": 200.0,
        "tilt_duration_s": 100.0,
        "ramp_s": 14.0,
        "supine_rest_s": 200.0,
    }

    def __init__(self, baseline_t_max=190.0, tilt_stabilized_t_min=240.0,
                 protocol=None, reference_path=None):
        self.baseline_t_max = baseline_t_max
        self.tilt_stabilized_t_min = tilt_stabilized_t_min
        self.protocol = dict(self.DEFAULT_PROTOCOL, **(protocol or {}))
        self._reference_path = reference_path

    def evaluate(self, sim_results, phenotype=None, protocol=None):
        """
        Runs validation checks on the simulation results.
        Returns a validation report with pass/fail outcomes plus a
        ``limitations`` list (disclosed model limitations - never silently
        passed) and a ``reference_comparison`` block when the protocol
        matches a frozen healthy-reference entry.
        """
        time = sim_results["time"]
        pau = sim_results["pau"]
        Hc = sim_results["Hc"]  # in bps
        hr_bpm = Hc * 60.0

        prot = dict(self.protocol, **(protocol or {}))
        onset_s = prot["onset_s"]
        tilt_duration_s = prot["tilt_duration_s"]

        # Canonical orthostatic HR metrics (G-P0-09 semantics).
        om = compute_orthostatic_metrics(hr_bpm=hr_bpm, time=time,
                                         onset_s=onset_s,
                                         tilt_duration_s=tilt_duration_s)
        hr_baseline_mean = om["baseline_hr_bpm"]
        sustained_dhr = om["sustained_delta_HR_bpm"]
        initial_transient = om["initial_transient_bpm"]
        # Transient-phase peak HR (absolute) for continuity reporting.
        tr_mask = (time >= om["transient_window_s"][0]) & (
            time < om["transient_window_s"][1])
        hr_tilt_peak = (float(np.max(hr_bpm[tr_mask])) if np.any(tr_mask)
                        else hr_baseline_mean)

        # BP phase masks (legacy bench windows retained for the BP checks).
        baseline_mask = time <= self.baseline_t_max
        tilt_stabilized_mask = time >= self.tilt_stabilized_t_min

        pau_baseline = pau[baseline_mask]
        sbp_baseline = np.max(pau_baseline)
        dbp_baseline = np.min(pau_baseline)
        map_baseline = np.mean(pau_baseline)

        pau_tilt = pau[tilt_stabilized_mask]
        sbp_tilt = np.max(pau_tilt)
        dbp_tilt = np.min(pau_tilt)
        map_tilt = np.mean(pau_tilt)

        # Beat-wise systolic delta-BP (pressor criterion support).
        sus_win = om["sustained_window_s"]
        if sus_win is not None:
            sbp_sus = self._mean_sbp(time, pau, sus_win[0], sus_win[1])
            sbp_sup = self._mean_sbp(time, pau,
                                     om["baseline_window_s"][0],
                                     om["baseline_window_s"][1])
            d_sbp = sbp_sus - sbp_sup
        else:
            d_sbp = float("nan")

        checks = {}
        limitations = []

        # Check A: Physiological Bounds (extreme limits)
        checks["hr_within_bounds"] = {
            "pass": bool(np.all(hr_bpm >= 30.0) and np.all(hr_bpm <= 220.0)),
            "details": f"HR Range: [{np.min(hr_bpm):.1f}, {np.max(hr_bpm):.1f}] bpm"
        }

        checks["bp_within_bounds"] = {
            "pass": bool(np.all(pau >= 30.0) and np.all(pau <= 230.0)),
            "details": f"BP Range: [{np.min(pau):.1f}, {np.max(pau):.1f}] mmHg"
        }

        # Check B: Clinical criterion on the SUSTAINED metric (never the
        # transient peak). Window kind is disclosed; on the short bench
        # protocol this is a continuity proxy, not a licensed 10-min claim.
        if om["sustained_window_kind"] == "minutes_5_10":
            window_note = "minutes 5-10 diagnostic window"
        elif om["sustained_window_kind"] == "unresolved":
            window_note = ("UNRESOLVED sustained window (tilt phase too "
                           "short after reserving the 30-s transient); no "
                           "sustained metric available")
        else:
            window_note = (f"SHORT-PROTOCOL PROXY ({om['sustained_window_kind']}; "
                           f"the >=30 bpm criterion is evidence-licensed only "
                           f"for 10-min protocols - CONTRADICTION_AUDIT Target 1)")
        if phenotype is None:  # Healthy Control
            checks["clinical_pots_diagnostic"] = {
                "pass": bool(sustained_dhr < POTS_SUSTAINED_CRITERION_BPM),
                "details": (f"Healthy control sustained delta-HR is "
                            f"{sustained_dhr:.1f} bpm (< 30 bpm; {window_note})")
            }
        else:  # POTS Phenotype
            checks["clinical_pots_diagnostic"] = {
                "pass": bool(sustained_dhr >= POTS_SUSTAINED_CRITERION_BPM),
                "details": (f"POTS phenotype sustained delta-HR is "
                            f"{sustained_dhr:.1f} bpm (>= 30 bpm; {window_note})")
            }

        # Check C: Autonomic Compensation (initial drop and recovery)
        post_tilt_initial_mask = (time >= onset_s) & (time <= onset_s + 15.0)
        pau_initial_tilt_min = (np.min(pau[post_tilt_initial_mask])
                                if np.any(post_tilt_initial_mask)
                                else map_baseline)
        bp_drop = map_baseline - pau_initial_tilt_min

        checks["baroreflex_compensation"] = {
            "pass": bool(bp_drop > 5.0 and map_tilt > (pau_initial_tilt_min - 2.0)),
            "details": f"Initial BP drop: {bp_drop:.1f} mmHg. Stabilized Map: {map_tilt:.1f} mmHg."
        }

        # Disclosed limitation (G-P0-03 companion, GAP register G-P1-01):
        # the hyperadrenergic upright delta-SBP >= +10 mmHg pressor criterion
        # (Okamoto 2024, tier A) is NOT met by the 0-D model (simulated
        # ~-4.0 mmHg): arterial pulse pressure narrows on tilt as stroke
        # volume falls. Disclose; never silently pass.
        if phenotype == "hyperadrenergic_pots":
            limitations.append(
                "hyperadrenergic_pots: upright delta-SBP pressor criterion "
                f"(Okamoto 2024, tier A, required >= +10 mmHg) NOT met - "
                f"simulated delta-SBP {d_sbp:+.1f} mmHg (cycle-3 documented "
                f"value -4.0 mmHg). 0-D windkessel limitation: pulse pressure "
                f"narrows on tilt (SV falls); the MAP pressor surrogate "
                f"(~+5 mmHg) is present but is NOT the clinical criterion. "
                f"See tests/test_orthostatic_response.py strict-xfail "
                f"test_hyperadrenergic_sbp_pressor_criterion."
            )

        # Protocol-conditioned healthy reference comparison (only when the
        # simulated protocol matches a frozen reference entry's window).
        reference_comparison = {"status": "not_applicable"}
        try:
            reference = load_healthy_reference(self._reference_path)
            pid = match_reference_protocol(
                reference, prot.get("method"),
                prot.get("angle_degrees"), tilt_duration_s,
                supine_rest_s=prot.get("supine_rest_s"))
            if pid is not None and not np.isnan(sustained_dhr):
                reference_comparison = dict(
                    compare_distribution_to_reference([sustained_dhr], pid,
                                                      reference=reference),
                    status="compared",
                    note=("single-run comparison; cohort-level comparison "
                          "requires sampling the healthy distribution"),
                )
            else:
                reference_comparison = {
                    "status": "not_applicable",
                    "reason": ("no frozen reference entry matches this "
                               "protocol window (method/angle/duration); "
                               "bench 100-s tilt cannot reach the minutes "
                               "5-10 diagnostic window"),
                }
        except (OSError, yaml.YAMLError, KeyError) as exc:
            reference_comparison = {"status": "unavailable",
                                    "reason": str(exc)}

        all_passed = all(check["pass"] for check in checks.values())

        report = {
            "phenotype": phenotype or "Healthy Control",
            "protocol": prot,
            "hr_baseline_mean_bpm": hr_baseline_mean,
            "hr_tilt_mean_bpm": float(np.mean(hr_bpm[tilt_stabilized_mask])),
            # Canonical metrics (frozen semantics, G-P0-09):
            "sustained_delta_HR_bpm": sustained_dhr,
            "sustained_window_s": om["sustained_window_s"],
            "sustained_window_kind": om["sustained_window_kind"],
            "initial_transient_bpm": initial_transient,
            "initial_transient_mean_bpm": om["initial_transient_mean_bpm"],
            # Continuity keys (legacy consumers): hr_increase_bpm is now the
            # SUSTAINED metric; hr_tilt_peak_bpm is the transient-phase peak.
            "hr_tilt_peak_bpm": hr_tilt_peak,
            "hr_increase_bpm": sustained_dhr,
            "delta_SBP_beatwise_mmHg": d_sbp,
            "bp_baseline_sys_dia": (sbp_baseline, dbp_baseline),
            "bp_tilt_sys_dia": (sbp_tilt, dbp_tilt),
            "map_baseline_mmHg": map_baseline,
            "map_tilt_mmHg": map_tilt,
            "initial_bp_drop_mmHg": bp_drop,
            "reference_comparison": reference_comparison,
            "limitations": limitations,
            "validation_passed": all_passed,
            "checks": checks,
        }

        return report

    @staticmethod
    def _mean_sbp(time, pau, lo, hi):
        """Mean of beat-wise systolic peaks of aortic pressure in [lo, hi)."""
        m = (time >= lo) & (time < hi)
        pw = pau[m]
        if pw.size == 0:
            return float("nan")
        peaks, _ = find_peaks(pw, distance=40, prominence=3.0)
        if len(peaks) == 0:
            return float("nan")
        return float(pw[peaks].mean())

    def print_report(self, report):
        print(f"\n==========================================")
        print(f"  PHYSIOLOGICAL VALIDATION REPORT")
        print(f"  Cohort Phenotype: {report['phenotype'].upper()}")
        print(f"==========================================")
        print(f"Baseline HR (mean): {report['hr_baseline_mean_bpm']:.1f} bpm")
        print(f"Baseline BP (sys/dia): {report['bp_baseline_sys_dia'][0]:.1f}/{report['bp_baseline_sys_dia'][1]:.1f} mmHg")
        print(f"Sustained delta-HR (canonical metric): {report['sustained_delta_HR_bpm']:.1f} bpm "
              f"[{report['sustained_window_kind']}]")
        print(f"Initial transient delta-HR (first 30 s, recorded separately): "
              f"{report['initial_transient_bpm']:.1f} bpm")
        print(f"Stabilized Post-Tilt BP: {report['bp_tilt_sys_dia'][0]:.1f}/{report['bp_tilt_sys_dia'][1]:.1f} mmHg")
        print(f"Initial BP Drop on Tilt: {report['initial_bp_drop_mmHg']:.1f} mmHg")
        print(f"Beat-wise delta-SBP (supine->sustained): {report['delta_SBP_beatwise_mmHg']:+.1f} mmHg")
        rc = report.get("reference_comparison", {})
        print(f"Healthy reference comparison: {rc.get('status', 'n/a')}"
              + (f" (protocol_id={rc.get('protocol_id')})"
                 if rc.get("protocol_id") else ""))
        print(f"------------------------------------------")
        print(f"Validation Checks:")
        for name, chk in report["checks"].items():
            status = "\033[92m[PASS]\033[0m" if chk["pass"] else "\033[91m[FAIL]\033[0m"
            print(f"  {status} {name}: {chk['details']}")
        if report.get("limitations"):
            print(f"------------------------------------------")
            print(f"DISCLOSED LIMITATIONS (not pass/fail gated, never silent):")
            for lim in report["limitations"]:
                print(f"  \033[93m[LIMITATION]\033[0m {lim}")
        print(f"------------------------------------------")
        overall_status = "\033[92mPASSED\033[0m" if report["validation_passed"] else "\033[91mFAILED\033[0m"
        print(f"OVERALL PHYSIOLOGICAL VALIDATION: {overall_status}")
        print(f"==========================================\n")
