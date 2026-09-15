"""Level 2 - PHYSIOLOGICAL PLAUSIBILITY (SYNTHETIC_TO_REAL_BENCHMARK.md §L2).

2.1 Event-protocol trajectory battery: supine/tilt/recovery phases, mixed
    meal, exercise - each phase metric must fall inside the evidence-anchored
    band.  Bands are numeric encodings of the EVENT_PROTOCOLS.yaml
    expected-response dossiers (the YAML carries them as curated prose; the
    numbers below quote it and cite the protocol id per check - they are
    fixed here BEFORE the runs, benchmark pre-registration rule).
2.2 Timescale signatures: DFA-alpha1 in [0.8, 1.2] healthy awake
    (EVD-TEMP-001), RSA spectral peak tracks respiration (EVD-TEMP-003),
    circadian HR amplitude ~13.5 bpm via run_multiday (EVD-HLTH-003).

Runtime management (documented, per mandate): the tilt battery uses the
repo bench protocol (150 s supine + 100 s tilt + 60 s recovery, dt=0.02);
the sustained metric is the evaluator's flagged ``short_protocol_proxy``
and is gated against a BENCH band, not the licensed 10-min reference
(L3 owns the licensed protocol).  Meal/exercise kernels run with
compressed timing (kernel ``time_scale``; honesty-flagged upstream).
"""

from __future__ import annotations

import numpy as np

from validation.evaluator import compute_orthostatic_metrics
from validation.levels import (
    STATUS_FAIL, STATUS_PASS, STATUS_UNRESOLVED, CheckResult,
    band_powers, cosinor_amplitude, dfa_alpha1, peak_freq,
)

# Pre-registered bands (EVENT_PROTOCOLS.yaml; see module docstring).
BENCH_TILT_BANDS = {
    # EV-supine-rest: supine ECG lab ~55-70 bpm; allow device margin.
    "supine_baseline_hr_bpm": (55.0, 75.0, "EV-supine-rest (EVD-HLTH-001/002)"),
    # Bench (100 s) healthy tilt sustained proxy: engine-anchored bench
    # continuity band bracketing the documented ~27.6 bpm structured-mode
    # healthy response; directionally between active stand (+12..+25) and
    # the 10-min tilt reference (+34) (EV-active-stand / EV-head-up-tilt).
    "bench_sustained_proxy_dhr_bpm": (15.0, 40.0,
                                      "EV-head-up-tilt (bench proxy, G-P0-09 flagged)"),
    # Initial transient peak rise first 30 s (tilt smaller than stand 20-30).
    "initial_transient_peak_bpm": (3.0, 35.0, "EV-head-up-tilt initial_0_30s"),
    # Recovery: within 10 bpm of supine baseline by 60 s after tilt-down
    # (EV-active-stand recovery: baseline within 30-60 s, ~10 bpm by 2 min).
    "recovery_residual_bpm_45s": (-10.0, 10.0, "EV-active-stand recovery"),
}
MEAL_HR_BAND = (2.0, 15.0)   # mixed meal +6+/-3 bpm (up to +10-20 large), EV-meal
EXERCISE_HR_BAND = (5.0, 70.0)  # submaximal bout elevation, EV-exercise-constant-load
DFA_ALPHA1_BAND = (0.8, 1.2)    # healthy awake, EVD-TEMP-001
CIRCADIAN_AMP_BAND = (11.0, 16.0)  # ~13.5 bpm half-range, EVD-HLTH-003


def _in_band(value, band):
    return bool(band[0] <= value <= band[1])


def check_tilt_trajectory(time, hr_bpm, onset_s, tilt_duration_s,
                          recovery_s=60.0, ramp_s=14.0):
    """2.1 healthy tilt trajectory battery on one engine run.

    Returns dict of phase metrics; gating decisions are made by the caller
    against BENCH_TILT_BANDS."""
    time = np.asarray(time, dtype=float)
    hr = np.asarray(hr_bpm, dtype=float)
    om = compute_orthostatic_metrics(
        time=time, hr_bpm=hr, onset_s=onset_s,
        tilt_duration_s=tilt_duration_s)
    # Recovery residual 35-45 s after the tilt-down ramp completes (the
    # bench protocol keeps ~46 s of post-tilt data; EV-active-stand
    # recovery band: baseline within 30-60 s).
    rec_lo = onset_s + tilt_duration_s + ramp_s
    rec_mask = (time >= rec_lo + 35.0) & (time < rec_lo + 45.0)
    rec_resid = (float(np.mean(hr[rec_mask]) - om["baseline_hr_bpm"])
                 if np.any(rec_mask) else float("nan"))
    return {
        "baseline_hr_bpm": om["baseline_hr_bpm"],
        "sustained_proxy_dhr_bpm": om["sustained_delta_HR_bpm"],
        "sustained_window_kind": om["sustained_window_kind"],
        "initial_transient_peak_bpm": om["initial_transient_bpm"],
        "recovery_residual_bpm_45s": rec_resid,
    }


def check_event_hr_response(time, hr_bpm, event_start_s, plateau_window_s,
                            baseline_window_s=60.0):
    """Meal/exercise battery: plateau HR elevation vs pre-event baseline."""
    time = np.asarray(time, dtype=float)
    hr = np.asarray(hr_bpm, dtype=float)
    bmask = (time >= event_start_s - baseline_window_s) & (time < event_start_s)
    pmask = ((time >= event_start_s + plateau_window_s[0])
             & (time < event_start_s + plateau_window_s[1]))
    if not (np.any(bmask) and np.any(pmask)):
        return float("nan")
    return float(np.mean(hr[pmask]) - np.mean(hr[bmask]))


def run(ctx: dict) -> list:
    results = []

    # --- 2.1 tilt trajectory battery (healthy bench) -----------------------
    tilt = ctx.get("healthy_bench_tilt")
    if tilt is None:
        results.append(CheckResult(
            "L2", "2.1_tilt_trajectory_battery",
            "supine/tilt/recovery phases within EVENT_PROTOCOLS bands",
            None, STATUS_UNRESOLVED, evidence="EV-head-up-tilt",
            note="context artifact 'healthy_bench_tilt' not provided"))
    else:
        m = check_tilt_trajectory(tilt["time"], tilt["hr_bpm"],
                                  tilt["onset_s"], tilt["tilt_duration_s"])
        checks = [
            ("supine_baseline_hr_bpm", m["baseline_hr_bpm"]),
            ("bench_sustained_proxy_dhr_bpm", m["sustained_proxy_dhr_bpm"]),
            ("initial_transient_peak_bpm", m["initial_transient_peak_bpm"]),
            ("recovery_residual_bpm_45s", m["recovery_residual_bpm_45s"]),
        ]
        rows, all_ok = {}, True
        for name, val in checks:
            lo, hi, src = BENCH_TILT_BANDS[name]
            ok = np.isfinite(val) and _in_band(val, (lo, hi))
            rows[name] = {"value": val, "band": [lo, hi], "pass": ok}
            all_ok = all_ok and ok
        # Supine mean-HR stationarity evidence (context for transient/
        # recovery verdicts): excessive baseline oscillation corrupts the
        # phase morphology independently of the mean level.
        t_arr = np.asarray(tilt["time"])
        sup_std = float(np.std(np.asarray(tilt["hr_bpm"])[t_arr < tilt["onset_s"]]))
        results.append(CheckResult(
            "L2", "2.1_tilt_trajectory_battery",
            "healthy bench tilt: baseline 55-75 bpm; sustained proxy +15..+40; "
            "transient 3-35; recovery residual within +/-10 bpm at ~45 s",
            {"phases": rows, "sustained_window_kind": m["sustained_window_kind"],
             "supine_hr_std_bpm": sup_std,
             "band_sources": {k: v[2] for k, v in BENCH_TILT_BANDS.items()}},
            STATUS_PASS if all_ok else STATUS_FAIL,
            evidence="EVENT_PROTOCOLS EV-supine-rest / EV-head-up-tilt / "
                     "EV-active-stand (EVD-HLTH-004)",
            note=("bench protocol = short_protocol_proxy (G-P0-09 flagged); "
                  "licensed 10-min claims live in L3. Supine mean-HR std "
                  f"{sup_std:.1f} bpm documents the engine baseline "
                  "oscillation affecting transient/recovery morphology "
                  "(see 2.2 gates).")))

    # --- 2.1 meal battery ----------------------------------------------------
    meal = ctx.get("meal_run")
    if meal is None:
        results.append(CheckResult(
            "L2", "2.1_meal_response",
            f"postprandial HR elevation within {MEAL_HR_BAND} bpm (EV-meal)",
            None, STATUS_UNRESOLVED, evidence="EV-meal (EVD-HLTH-006)",
            note="context artifact 'meal_run' not provided"))
    else:
        dhr = check_event_hr_response(meal["time"], meal["hr_bpm"],
                                      meal["event_start_s"],
                                      meal["plateau_window_s"])
        ok = np.isfinite(dhr) and _in_band(dhr, MEAL_HR_BAND)
        results.append(CheckResult(
            "L2", "2.1_meal_response",
            f"postprandial HR elevation within {MEAL_HR_BAND} bpm "
            "(mixed meal +6+/-3; EVD-HLTH-006)",
            {"plateau_dhr_bpm": dhr, "time_scale": meal.get("time_scale"),
             "plateau_window_s": meal.get("plateau_window_s")},
            STATUS_PASS if ok else STATUS_FAIL,
            evidence="EV-meal (EVD-HLTH-006, EVD-METB-005)",
            note="kernel timing compressed (time_scale) for ODE feasibility; "
                 "magnitudes untouched"))

    # --- 2.1 exercise battery ----------------------------------------------
    ex = ctx.get("exercise_run")
    if ex is None:
        results.append(CheckResult(
            "L2", "2.1_exercise_response",
            f"exercise HR elevation within {EXERCISE_HR_BAND} bpm; "
            "post-bout recovery direction negative",
            None, STATUS_UNRESOLVED, evidence="EV-exercise-constant-load",
            note="context artifact 'exercise_run' not provided"))
    else:
        dhr = check_event_hr_response(ex["time"], ex["hr_bpm"],
                                      ex["event_start_s"], ex["plateau_window_s"])
        rec = check_event_hr_response(ex["time"], ex["hr_bpm"],
                                      ex["event_start_s"], ex["recovery_window_s"])
        ok = (np.isfinite(dhr) and _in_band(dhr, EXERCISE_HR_BAND)
              and np.isfinite(rec) and rec < dhr)
        results.append(CheckResult(
            "L2", "2.1_exercise_response",
            f"bout HR elevation within {EXERCISE_HR_BAND} bpm; recovery "
            "below bout plateau (EV-exercise-constant-load / EV-recovery)",
            {"bout_dhr_bpm": dhr, "late_recovery_dhr_bpm": rec,
             "es_plateau_bounded": ex.get("es_plateau_bounded")},
            STATUS_PASS if ok else STATUS_FAIL,
            evidence="EV-exercise-constant-load (EVD-TEMP-004/EVD-HLTH-005)",
            note=("the Es x1.30 contractility kernel couples only weakly to "
                  "HR in the ODE (+~6 bpm), and the window comparisons are "
                  "dominated by the engine baseline oscillation (see 2.2 "
                  "gates); reported, not tuned")))

    # --- 2.2 timescale signatures -------------------------------------------
    rr = ctx.get("timescale_rr")
    if rr is None:
        for cid in ("2.2_dfa_alpha1", "2.2_rsa_peak"):
            results.append(CheckResult(
                "L2", cid, "timescale signature from structured RR series",
                None, STATUS_UNRESOLVED, evidence="EVD-TEMP-001/003",
                note="context artifact 'timescale_rr' not provided"))
    else:
        a1 = dfa_alpha1(rr["rr_intervals_ms"])
        ok = np.isfinite(a1) and _in_band(a1, DFA_ALPHA1_BAND)
        results.append(CheckResult(
            "L2", "2.2_dfa_alpha1",
            f"DFA-alpha1 (4-16 beats) in {DFA_ALPHA1_BAND} healthy awake",
            {"dfa_alpha1": a1}, STATUS_PASS if ok else STATUS_FAIL,
            evidence="EVD-TEMP-001 (E4)"))
        freqs, P, lf, hf = band_powers(rr["rr_intervals_ms"])
        resp_hz = float(rr["respiration_rate_brpm"]) / 60.0
        pk = peak_freq(freqs, P, 0.15, 0.40) if freqs.size else float("nan")
        ok = np.isfinite(pk) and abs(pk - resp_hz) <= 0.05
        results.append(CheckResult(
            "L2", "2.2_rsa_peak",
            "RSA/HF spectral peak tracks respiration rate "
            "(|f_peak - f_resp| <= 0.05 Hz)",
            {"hf_peak_hz": pk, "respiration_hz": resp_hz,
             "lf_hf_ratio": (lf / hf if hf > 0 else None)},
            STATUS_PASS if ok else STATUS_FAIL,
            evidence="EVD-TEMP-003; TEMPORAL §1 (RSA confound built-in)"))

    # --- 2.2 circadian amplitude (run_multiday) ------------------------------
    circ = ctx.get("circadian_multiday")
    if circ is None:
        results.append(CheckResult(
            "L2", "2.2_circadian_amplitude",
            f"24-h HR cosinor amplitude within {CIRCADIAN_AMP_BAND} bpm",
            None, STATUS_UNRESOLVED, evidence="EVD-HLTH-003",
            note="context artifact 'circadian_multiday' not provided"))
    else:
        fit = cosinor_amplitude(circ["hour_of_day"], circ["mean_hr_bpm"])
        ok = _in_band(fit["amplitude"], CIRCADIAN_AMP_BAND)
        results.append(CheckResult(
            "L2", "2.2_circadian_amplitude",
            f"circadian HR amplitude within {CIRCADIAN_AMP_BAND} bpm "
            "(~13.5; acrophase ~14:40)",
            {"amplitude_bpm": fit["amplitude"], "mesor_bpm": fit["mesor"],
             "acrophase_h": fit["acrophase_h"], "days": circ.get("days")},
            STATUS_PASS if ok else STATUS_FAIL,
            evidence="EVD-HLTH-003 (E2/E4 cosinor anchor)"))

    return results
