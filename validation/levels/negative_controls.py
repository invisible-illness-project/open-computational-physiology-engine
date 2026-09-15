"""Anti-laundering negative controls (master prompt §14; benchmark §3.2).

The release-critical question: synthetic disease vs healthy must NOT be
trivially separable for NON-PHYSIOLOGICAL reasons.  Two families:

  A. Acquisition/statistical-nuisance PARITY across groups: identical
     sampling rates, noise levels, missingness models, record lengths,
     device distribution - checked on the emitted dataset records and on
     the generation configuration.  Any group-conditional nuisance
     channel is an anti-laundering violation (rule 5).
  B. Trivial-separability classifier gate: a simple logistic regression
     on summary features of the pilot-style cohort (LOOCV, numpy-only)
     must NOT exceed the anti-laundering band: healthy-vs-hypovolemic-
     POTS AUC < 0.95 (benchmark NC2 / reviewer Criterion 1).  The value
     is REPORTED; if > 0.95 the gate FAILS and the report says so - the
     data must never be tuned to pass (SWARM_SPEC rule 5).

Demographics note (disclosed, not gated as parity): the POTS cohort IS
demographically different by evidence (85-94% female, adolescent-mode
onset; EVD-POP-006).  Demographic features are therefore reported
separately and are NOT part of the nuisance-parity gate; the classifier
uses signal-derived features only.
"""

from __future__ import annotations

import numpy as np

from validation.levels import (
    STATUS_FAIL, STATUS_PASS, STATUS_UNRESOLVED, CheckResult,
    loocv_auc,
)

#: Pre-registered anti-laundering ceiling (benchmark NC2 / rule 5).
AUC_CEILING = 0.95
#: Evidence-honest classification band (NC2): 0.75-0.85; reported
#: informationally (the gate itself is the 0.95 ceiling).
AUC_HONEST_BAND = (0.75, 0.85)

#: Summary features from the signal (per-subject, licensed-tilt cohort).
SIGNAL_FEATURES = (
    "baseline_hr_bpm", "sustained_dhr_bpm", "initial_transient_bpm",
    "rmssd_ms", "sdnn_ms", "dfa_alpha1", "lf_hf_ratio",
)


def check_parity(parity_items: dict):
    """Family A: every nuisance channel must be identical across groups.

    parity_items: {channel_name: {"healthy": value, "disease": value
    [, "rel_tolerance": float]}}.  Values must compare equal, except
    channels carrying ``rel_tolerance`` (e.g. beat-aligned record lengths
    on an identical protocol), which pass when the relative difference is
    within tolerance."""
    mismatches = {}
    for k, v in parity_items.items():
        h, d = v.get("healthy"), v.get("disease")
        tol = v.get("rel_tolerance")
        if tol is not None and isinstance(h, (int, float)) and isinstance(d, (int, float)):
            scale = max(abs(h), abs(d), 1e-9)
            if abs(h - d) / scale > tol:
                mismatches[k] = v
        elif h != d:
            mismatches[k] = v
    return len(mismatches) == 0, {
        "channels_checked": sorted(parity_items.keys()),
        "mismatches": mismatches,
    }


def check_separability(features_healthy: np.ndarray,
                       features_disease: np.ndarray,
                       ceiling: float = AUC_CEILING):
    """Family B: LOOCV logistic-regression AUC on summary features.

    Returns (auc, detail).  Gate: AUC must be < ceiling."""
    H = np.asarray(features_healthy, dtype=float)
    D = np.asarray(features_disease, dtype=float)
    ok_rows = np.isfinite(H).all(axis=1)
    H = H[ok_rows]
    D = D[np.isfinite(D).all(axis=1)]
    if H.shape[0] < 2 or D.shape[0] < 2:
        return float("nan"), {"reason": "insufficient finite subjects"}
    X = np.vstack([H, D])
    y = np.concatenate([np.zeros(len(H), dtype=int), np.ones(len(D), dtype=int)])
    auc = loocv_auc(X, y)
    return auc, {
        "n_healthy": int(len(H)), "n_disease": int(len(D)),
        "n_features": int(X.shape[1]),
        "ceiling": ceiling, "honest_band_NC2": list(AUC_HONEST_BAND),
    }


def run(ctx: dict) -> list:
    results = []

    # --- A. nuisance parity ---------------------------------------------------
    parity = ctx.get("nc_parity")
    if parity is None:
        results.append(CheckResult(
            "NC", "NC_parity_nuisance_channels",
            "sampling rates / noise / missingness / record lengths / device "
            "distribution identical across groups",
            None, STATUS_UNRESOLVED, evidence="master prompt §14; rule 5",
            note="context artifact 'nc_parity' not provided"))
    else:
        ok, meas = check_parity(parity)
        results.append(CheckResult(
            "NC", "NC_parity_nuisance_channels",
            "group-conditional nuisance channels forbidden (sampling rate, "
            "noise, missingness, record length, device distribution)",
            meas, STATUS_PASS if ok else STATUS_FAIL,
            evidence="master prompt §14; SWARM_SPEC rule 5 (anti-laundering)"))

    # --- B. trivial separability gate ------------------------------------------
    cohort = ctx.get("licensed_cohort")
    if not cohort or not cohort.get("healthy") or not cohort.get("hypovolemic_pots"):
        results.append(CheckResult(
            "NC", "NC2_trivial_separability_auc",
            f"healthy-vs-hypovolemic-POTS LR AUC < {AUC_CEILING} (LOOCV, "
            "signal summary features)",
            None, STATUS_UNRESOLVED, evidence="NC2; reviewer Criterion 1",
            note="context artifact 'licensed_cohort' incomplete"))
    else:
        H = np.array([[s.get(f, float("nan")) for f in SIGNAL_FEATURES]
                      for s in cohort["healthy"]], dtype=float)
        D = np.array([[s.get(f, float("nan")) for f in SIGNAL_FEATURES]
                      for s in cohort["hypovolemic_pots"]], dtype=float)
        auc, det = check_separability(H, D)
        if not np.isfinite(auc):
            status = STATUS_UNRESOLVED
        else:
            status = STATUS_PASS if auc < AUC_CEILING else STATUS_FAIL
        # Secondary, non-diagnostic feature view (informational): excludes
        # the orthostatic diagnostic features to show the resting-signal
        # separation that an artifact-laundering bug would inflate.
        rest_feats = ("baseline_hr_bpm", "rmssd_ms", "sdnn_ms",
                      "dfa_alpha1", "lf_hf_ratio")
        H2 = np.array([[s.get(f, float("nan")) for f in rest_feats]
                       for s in cohort["healthy"]], dtype=float)
        D2 = np.array([[s.get(f, float("nan")) for f in rest_feats]
                       for s in cohort["hypovolemic_pots"]], dtype=float)
        auc_rest, _ = check_separability(H2, D2)
        results.append(CheckResult(
            "NC", "NC2_trivial_separability_auc",
            f"healthy-vs-hypovolemic-POTS LOOCV logistic AUC < {AUC_CEILING}; "
            f"honest band {AUC_HONEST_BAND} reported (NC2)",
            {"auc_full_features": auc,
             "auc_resting_features_only": auc_rest,
             "features": list(SIGNAL_FEATURES),
             **det},
            status,
            evidence="benchmark NC2 (EVD-LCOV-013 overfit counter-example); "
                     "reviewer Criterion 1; rule 5",
            note=("AUC is REPORTED, never tuned to pass; >0.95 = release "
                  "failure regardless of cause. Resting-only view excludes "
                  "the orthostatic diagnostic features.")))

    # --- demographics disclosure (informational) -------------------------------
    if cohort and cohort.get("healthy") and cohort.get("hypovolemic_pots"):
        def _demo(group):
            ages = [s["age"] for s in cohort[group] if s.get("age")]
            sexes = [s["sex"] for s in cohort[group] if s.get("sex")]
            return {"n": len(cohort[group]),
                    "age_mean": float(np.mean(ages)) if ages else None,
                    "female_fraction": (float(np.mean([x == "female" for x in sexes]))
                                        if sexes else None)}
        results.append(CheckResult(
            "NC", "NC_demographics_disclosure",
            "demographic differences are evidence-based (POTS 85-94% female, "
            "young onset; EVD-POP-006) and disclosed; not nuisance parity",
            {"healthy": _demo("healthy"),
             "hypovolemic_pots": _demo("hypovolemic_pots")},
            STATUS_PASS,
            evidence="EVD-POP-006; dataset/cohort.py recipes",
            note="informational: POTS demographics differ BY EVIDENCE; "
                 "classifier uses signal features only"))

    return results
