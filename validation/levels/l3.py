"""Level 3 - CLINICAL PLAUSIBILITY (SYNTHETIC_TO_REAL_BENCHMARK.md §L3).

Positive targets (§3.1), protocol-conditioned and tail-preserving:

  * Healthy 10-min HUT cohort vs the FROZEN reference
    (validation/healthy_reference.yaml, hut_60_70_10min) via
    validation/evaluator.compare_distribution_to_reference - central
    tendency AND the >=30 bpm false-positive tail (a protocol property,
    never collapsed).
  * Hypovolemic-POTS cohort: sustained delta-HR >= 30 bpm rate and the
    patient-minus-control meta-analytic contrast +19.88 bpm
    (95% CI 15.24-24.52; EVD-POTS-011, E4).
  * Hyperadrenergic delta-SBP pressor criterion: documented engine
    limitation (0-D windkessel; simulated ~-4 mmHg vs required >= +10)
    must surface as a DISCLOSED LIMITATION via the evaluator - never a
    silent pass (G-P0-03 companion, SWARM_SPEC W1-C).

Sample-size discipline (pre-registered here): the licensed-window cohort
is small by design (ODE cost); fraction estimates carry Clopper-Pearson
95% intervals and the small-n precision is disclosed in every note.  A
verdict is pass/fail on the measured value; Monte-Carlo precision is
reported, never tuned.
"""

from __future__ import annotations

import math

import numpy as np

from validation.evaluator import (
    POTS_SUSTAINED_CRITERION_BPM, compare_distribution_to_reference,
    load_healthy_reference,
)
from validation.levels import (
    STATUS_FAIL, STATUS_LIMITATION, STATUS_PASS, STATUS_UNRESOLVED,
    CheckResult,
)

#: EVD-POTS-011 (E4 post-downgrade): HUTT patient-minus-control meta
#: contrast and 95% CI (pre-registered target band).
POTS_HUTT_CONTRAST_BPM = {"mean": 19.88, "ci95": (15.24, 24.52)}
#: Referral-ascertained POTS cohorts ~all meet the >=30 bpm criterion on
#: licensed 10-min protocols (CONTRADICTION Target 1).  The synthetic
#: hypovolemic branch is a severity MIXTURE (Raj 2005 -14+/-10%), so the
#: pre-registered gate is >= 50% with the full distribution reported
#: (never tuned; overlapping mild cases are the honest disease tail).
POTS_SUSTAINED_RATE_MIN = 0.50
#: Minimum cohort size for a tail-fraction verdict; below it the tail
#: check reports measured values but is downgraded to unresolved
#: (Monte-Carlo precision cannot resolve the band).
TAIL_MIN_N = 8


def clopper_pearson(k: int, n: int, alpha: float = 0.05):
    """Exact binomial CI (beta-quantile form; scipy only)."""
    from scipy.stats import beta
    if n == 0:
        return (float("nan"), float("nan"))
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return (lo, hi)


def run(ctx: dict) -> list:
    results = []
    cohort = ctx.get("licensed_cohort")

    # --- 3.1 healthy cohort vs frozen reference (licensed 10-min HUT) ------
    if not cohort or not cohort.get("healthy"):
        results.append(CheckResult(
            "L3", "3.1_healthy_hut_distribution",
            "healthy 10-min HUT sustained dHR vs frozen reference "
            "(mean tolerance + >=30 bpm tail band 0.40-0.60)",
            None, STATUS_UNRESOLVED,
            evidence="healthy_reference.yaml hut_60_70_10min; EVD-HLTH-004",
            note="context artifact 'licensed_cohort.healthy' not provided"))
    else:
        samples = np.array([s["sustained_dhr_bpm"] for s in cohort["healthy"]],
                           dtype=float)
        samples = samples[np.isfinite(samples)]
        ref = load_healthy_reference()
        cmp_ = compare_distribution_to_reference(samples, "hut_60_70_10min",
                                                 reference=ref)
        n = int(samples.size)
        k = int(np.sum(samples >= POTS_SUSTAINED_CRITERION_BPM))
        ci = clopper_pearson(k, n)
        mean_ok = cmp_["mean_within_reference"]
        if n < TAIL_MIN_N:
            status = STATUS_UNRESOLVED
            note = (f"n={n} < {TAIL_MIN_N}: tail band (0.40-0.60) not "
                    f"resolvable at this Monte-Carlo size; measured fraction "
                    f"{cmp_['sample_fraction_ge_30bpm']:.2f} "
                    f"95% CI [{ci[0]:.2f}, {ci[1]:.2f}]; mean check "
                    f"{'PASS' if mean_ok else 'FAIL'}")
            if not mean_ok:
                status = STATUS_FAIL  # central-tendency failures are real
        else:
            status = STATUS_PASS if cmp_["consistent_with_healthy_reference"] \
                else STATUS_FAIL
            note = f"tail fraction 95% CI [{ci[0]:.2f}, {ci[1]:.2f}]"
        results.append(CheckResult(
            "L3", "3.1_healthy_hut_distribution",
            "healthy HUT sustained dHR mean 34+/-tol and >=30 bpm fraction "
            "in [0.40, 0.60] (frozen reference, tails preserved)",
            {"comparison": cmp_, "n": n, "ci95_fraction_ge_30bpm": list(ci)},
            status,
            evidence="healthy_reference.yaml hut_60_70_10min; Plash 2013 "
                     "(EVD-HLTH-004); CONTRADICTION Target 1",
            note=note))

    # --- 3.1 hypovolemic-POTS >=30 rate + meta contrast --------------------
    if not cohort or not cohort.get("hypovolemic_pots") or not cohort.get("healthy"):
        results.append(CheckResult(
            "L3", "3.1_hypovolemic_pots_rate",
            f"POTS sustained dHR >=30 bpm rate >= {POTS_SUSTAINED_RATE_MIN}; "
            f"patient-minus-control mean +{POTS_HUTT_CONTRAST_BPM['mean']} bpm "
            f"within 95% CI {POTS_HUTT_CONTRAST_BPM['ci95']}",
            None, STATUS_UNRESOLVED,
            evidence="EVD-POTS-001; EVD-POTS-011",
            note="context artifact 'licensed_cohort' incomplete"))
    else:
        pots = np.array([s["sustained_dhr_bpm"]
                         for s in cohort["hypovolemic_pots"]], dtype=float)
        ctrl = np.array([s["sustained_dhr_bpm"]
                         for s in cohort["healthy"]], dtype=float)
        pots = pots[np.isfinite(pots)]
        ctrl = ctrl[np.isfinite(ctrl)]
        rate = float(np.mean(pots >= POTS_SUSTAINED_CRITERION_BPM)) if pots.size \
            else float("nan")
        k = int(np.sum(pots >= POTS_SUSTAINED_CRITERION_BPM))
        ci_rate = clopper_pearson(k, int(pots.size))
        contrast = float(np.mean(pots) - np.mean(ctrl)) if pots.size and ctrl.size \
            else float("nan")
        lo, hi = POTS_HUTT_CONTRAST_BPM["ci95"]
        rate_ok = np.isfinite(rate) and rate >= POTS_SUSTAINED_RATE_MIN
        contrast_ok = np.isfinite(contrast) and lo <= contrast <= hi
        results.append(CheckResult(
            "L3", "3.1_hypovolemic_pots_rate",
            f"hypovolemic-POTS >=30 bpm sustained rate >= "
            f"{POTS_SUSTAINED_RATE_MIN} (severity mixture, tails reported) AND "
            f"patient-minus-control +{POTS_HUTT_CONTRAST_BPM['mean']} bpm "
            f"within CI [{lo}, {hi}]",
            {"n_pots": int(pots.size), "rate_ge_30bpm": rate,
             "rate_ci95": list(ci_rate),
             "pots_samples_bpm": sorted(float(x) for x in pots),
             "contrast_bpm": contrast, "contrast_ci95_target": [lo, hi]},
            STATUS_PASS if (rate_ok and contrast_ok) else STATUS_FAIL,
            evidence="EVD-POTS-011 (E4, meta +19.88 [15.24-24.52]); "
                     "EVD-POTS-004 (Raj 2005 severity mixture); "
                     "CONTRADICTION Target 1/3",
            note=("severity-mixture branch: mild deficits overlap the healthy "
                  "high-normal tail BY CONSTRUCTION (pilot design); rate is "
                  "reported, never tuned")))

    # --- hyperadrenergic delta-SBP disclosed limitation ---------------------
    hyp = ctx.get("hyperadrenergic_eval")
    if hyp is None:
        results.append(CheckResult(
            "L3", "3.1_hyperadrenergic_dsbp_limitation",
            "hyperadrenergic upright delta-SBP pressor criterion (>= +10 mmHg) "
            "surfaced as disclosed limitation, NOT a pass",
            None, STATUS_UNRESOLVED,
            evidence="Okamoto 2024 tier A; G-P0-03; strict-xfail",
            note="context artifact 'hyperadrenergic_eval' not provided"))
    else:
        lims = hyp.get("limitations", [])
        surfaced = any("delta-SBP" in l or "pressor" in l for l in lims)
        results.append(CheckResult(
            "L3", "3.1_hyperadrenergic_dsbp_limitation",
            "evaluator surfaces the delta-SBP pressor-criterion failure as a "
            "DISCLOSED LIMITATION (not a pass)",
            {"limitations": lims,
             "delta_SBP_beatwise_mmHg": hyp.get("delta_SBP_beatwise_mmHg"),
             "limitation_surfaced": surfaced},
            STATUS_LIMITATION if surfaced else STATUS_FAIL,
            evidence="G-P0-03 companion; GAP G-P1-01; "
                     "tests/test_orthostatic_response.py strict-xfail",
            note=("0-D windkessel limitation: pulse pressure narrows on tilt "
                  "(SV falls); disclosed per W1-C, never silently passed")))

    return results
