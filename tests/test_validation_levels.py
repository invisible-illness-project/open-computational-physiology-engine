"""Unit tests for the release-gate validation levels (W3-V).

Runtime discipline: every fixture here is tiny/fast - no ODE integration
(the ODE-backed gates live in validation/levels/run_release_gates.py and
degrade to ``unresolved`` when their context artifacts are absent, which
is itself tested).  Kernel-overlay fixtures use the EventKernelManager
directly (no engine); HRV fixtures use the structured RR generator;
WFDB fixtures are crafted byte arrays; network access is never used.
"""

import os
import sys

import numpy as np
import pytest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

from validation.levels import (
    GOVERNING_STATEMENT, STATUS_FAIL, STATUS_LIMITATION, STATUS_PASS,
    STATUS_UNRESOLVED, STATUSES, CheckResult, auc_score, band_powers,
    cosinor_amplitude, dfa_alpha1, loocv_auc, logistic_regression_fit,
    peak_freq, rmssd, sdnn,
)
from validation.levels import l1, l2, l3, l4, negative_controls as nc
from validation.levels.run_release_gates import write_outputs


# ---------------------------------------------------------------------------
# Shared helpers / fixtures
# ---------------------------------------------------------------------------

def _hrv_inputs(n=400, hr=62.0, vagal=0.7, symp=0.3, resp=15.0, stage=0):
    """Minimal structured-HRV generator input (healthy awake supine)."""
    t = np.linspace(0.0, n * 60.0 / hr, n)
    bcast = lambda v: np.full(n, v, dtype=float)
    return {
        "time_s": t, "mean_hr_bpm": bcast(hr), "vagal_drive": bcast(vagal),
        "sympathetic_drive": bcast(symp), "respiration_rate_brpm": bcast(resp),
        "sleep_stage_code": np.full(n, stage, dtype=int),
    }


@pytest.fixture(scope="module")
def rr_series():
    from simulation.hrv import generate_rr_series
    return generate_rr_series(_hrv_inputs(), seed=123)


def _kb_params():
    from models.baroreflex_model import BaroreflexPOTSModel
    return BaroreflexPOTSModel().params


# ---------------------------------------------------------------------------
# Shared infrastructure
# ---------------------------------------------------------------------------

def test_governing_statement_exact_and_binding():
    assert GOVERNING_STATEMENT == (
        "OCPE synthetic data are candidate research artifacts whose utility "
        "for any task is unestablished pending the Level-5 benchmark.")


def test_checkresult_schema_and_statuses():
    r = CheckResult("L1", "x", "target", {"a": np.float64(1.5)},
                    STATUS_PASS, evidence="ev", note="nt")
    d = r.to_dict()
    assert set(d) == {"gate", "check", "target", "measured", "status",
                      "evidence", "note"}
    assert d["status"] in STATUSES
    assert d["measured"]["a"] == 1.5
    # NaN/inf are normalized to None for serialization.
    r2 = CheckResult("L2", "y", "t", float("nan"), STATUS_UNRESOLVED)
    assert r2.to_dict()["measured"] is None


def test_auc_score_extremes_and_ties():
    assert auc_score([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == 1.0
    assert auc_score([0, 0, 1, 1], [0.9, 0.8, 0.2, 0.1]) == 0.0
    assert auc_score([0, 1], [0.5, 0.5]) == 0.5  # ties
    assert np.isnan(auc_score([0, 0], [1.0, 2.0]))  # no positives


def test_logistic_regression_and_loocv():
    rng = np.random.default_rng(0)
    X = np.vstack([rng.normal(0, 1, (20, 3)), rng.normal(2, 1, (20, 3))])
    y = np.concatenate([np.zeros(20, int), np.ones(20, int)])
    w = logistic_regression_fit(X, y)
    p = 1.0 / (1.0 + np.exp(-(np.column_stack([np.ones(40), X]) @ w)))
    assert auc_score(y, p) > 0.9
    auc = loocv_auc(X, y)
    assert 0.8 < auc <= 1.0
    # Fully overlapping classes -> near-chance LOOCV.
    X2 = np.vstack([rng.normal(0, 1, (15, 2)), rng.normal(0.05, 1, (15, 2))])
    y2 = np.concatenate([np.zeros(15, int), np.ones(15, int)])
    auc2 = loocv_auc(X2, y2)
    assert 0.3 <= auc2 <= 0.8


def test_dfa_alpha1_white_noise_vs_structured(rr_series):
    rng = np.random.default_rng(1)
    white = rng.normal(900, 40, 500)
    a_white = dfa_alpha1(white)
    assert a_white < 0.7  # uncorrelated -> ~0.5
    a1 = dfa_alpha1(rr_series["rr_intervals_ms"])
    assert 0.8 <= a1 <= 1.2  # structured healthy-awake target (EVD-TEMP-001)


def test_band_powers_rsa_peak_tracks_respiration():
    # Synthetic RR series modulated at exactly 0.25 Hz.
    tt = np.arange(0, 300.0, 1.0)
    rr = 900.0 + 30.0 * np.sin(2 * np.pi * 0.25 * tt)
    freqs, P, lf, hf = band_powers(rr)
    pk = peak_freq(freqs, P, 0.15, 0.40)
    assert abs(pk - 0.25) <= 0.05


def test_cosinor_fit_recovers_parameters():
    h = np.linspace(0, 48, 200)
    v = 63.0 + 13.5 * np.cos(2 * np.pi * (h - 14.67) / 24.0)
    fit = cosinor_amplitude(h, v)
    assert abs(fit["amplitude"] - 13.5) < 0.2
    assert abs(fit["mesor"] - 63.0) < 0.2


# ---------------------------------------------------------------------------
# Level 1
# ---------------------------------------------------------------------------

def test_l1_volume_conservation_pass_and_fail():
    n = 50
    tot = np.full(n, 4500.0)
    # Stressed compartments sum to a constant below TotalVol (implicit
    # unstressed offset) -> PASS; drift or offset change -> FAIL.
    vols = np.column_stack([tot * 0.05, tot * 0.1, tot * 0.05,
                            tot * 0.12, tot * 0.02])
    ok, meas = l1.check_volume_conservation(vols, tot)
    assert ok and meas["drift_rel_totalvol"] < 1e-6
    assert meas["unstressed_offset_ml"] == pytest.approx(4500 * 0.66)
    vols_bad = vols.copy()
    vols_bad[10, 0] += 1.0  # 1 mL leak / redistribution event
    ok, meas = l1.check_volume_conservation(vols_bad, tot)
    assert not ok
    tot_bad = tot.copy()
    tot_bad[25:] += 5.0  # defended-volume series changes mid-run
    ok, _ = l1.check_volume_conservation(vols, tot_bad)
    assert not ok


def test_l1_determinism_check():
    a = {"x": np.arange(5), "y": np.array([1.5, 2.5])}
    ok, _ = l1.check_determinism(a, {k: v.copy() for k, v in a.items()})
    assert ok
    ok, meas = l1.check_determinism(a, {"x": np.arange(5), "y": np.array([1.5, 9.9])})
    assert not ok and "y" in meas["mismatches"]


def test_l1_kernel_overlay_restoration_meal_and_exercise():
    """G-P0-01 semantics at the manager level (no engine): plateau is
    multiplicative vs BASELINE; the envelope is exactly zero after t_end."""
    import copy
    from simulation.event_kernels import (
        EventKernelManager, make_exercise_kernel, make_meal_kernel,
    )
    baseline = copy.deepcopy(_kb_params())
    for factory, sym, factor in (
            (lambda: make_meal_kernel(50.0, time_scale=0.03), "RalpM", 0.75),
            (lambda: make_exercise_kernel(50.0, duration_s=60.0), "Es", 1.30)):
        mgr = EventKernelManager()
        k = factory()
        mgr.add_kernel(k, np.random.default_rng(0))
        t_plateau = 50.0 + k.delay_s + k._onset_s + 0.5 * k._duration_s
        plateau = mgr.compute_parameter_overlay(baseline, t_plateau)
        final = mgr.compute_parameter_overlay(baseline, k.t_end + 5.0)
        ok, meas = l1.check_kernel_baseline_restoration(
            baseline, plateau, final, sym, factor)
        assert ok, meas
        assert meas["restored_exactly"]


def test_l1_kernel_no_compounding_two_meals_same_baseline():
    """Two kernels of the same kind compose against baseline, never against
    each other's already-modified parameters (G-P0-01)."""
    import copy
    from simulation.event_kernels import EventKernelManager, make_meal_kernel
    baseline = copy.deepcopy(_kb_params())
    mgr = EventKernelManager()
    k1 = make_meal_kernel(50.0, time_scale=0.03)
    mgr.add_kernel(k1, np.random.default_rng(0))
    t_plateau = 50.0 + k1.delay_s + k1._onset_s + 0.5 * k1._duration_s
    over1 = mgr.compute_parameter_overlay(baseline, t_plateau)
    over2 = mgr.compute_parameter_overlay(over1, t_plateau)  # wrong usage demo
    # Overlay is f(baseline): applying it to an already-modified dict must
    # still be driven by the multiplicative-vs-baseline semantics of the
    # manager (documented contract: callers pass the immutable baseline).
    assert over1["RalpM"] == pytest.approx(0.75 * baseline["RalpM"], rel=0.02)
    assert over2["RalpM"] != over1["RalpM"]  # hence callers MUST pass baseline


def test_l1_identifiability_enforcement_and_demo():
    meta = {f"p{i}": {"evidence_e_level": "E4", "canonical_status": "canonical"}
            for i in range(3)}
    ok, _ = l1.check_identifiability_enforcement(meta)
    assert ok
    meta["pX"] = {"evidence_e_level": None, "canonical_status": "experimental"}
    ok, meas = l1.check_identifiability_enforcement(meta)
    assert not ok and meas["missing_e_level"] == ["pX"]
    non_id, det = l1.practical_identifiability_demo(2.0)
    assert non_id and det["label"] == "non_identifiable"
    non_id, det = l1.practical_identifiability_demo(12.0)
    assert not non_id and det["label"] == "recoverable"


def test_l1_run_degrades_to_unresolved_without_context():
    for r in l1.run({}):
        assert r.status == STATUS_UNRESOLVED, r.check


def test_l1_run_with_synthetic_artifacts():
    n = 20
    arr = {"time": np.arange(n), "Hc": np.full(n, 1.05)}
    ctx = {
        "det_runs": {"run_a": arr, "run_b": {k: v.copy() for k, v in arr.items()}},
        "conservation": {
            "volumes_ml": np.column_stack([np.full(n, 900.0)] * 5),
            "total_vol_ml": np.full(n, 4500.0)},
        "identifiability": {
            "kb_param_meta": {"kH": {"evidence_e_level": "E4",
                                     "canonical_status": "canonical"}},
            "delta_hr_from_param_perturbation_bpm": 1.5},
        "meal_kernel_check": {"baseline": {"RalpM": 13.41},
                              "plateau": {"RalpM": 13.41 * 0.75},
                              "final": {"RalpM": 13.41}},
        "exercise_kernel_check": {"baseline": {"Es": 2.0},
                                  "plateau": {"Es": 2.6},
                                  "final": {"Es": 2.0}},
        "honesty_gating": {"experimental_inert": True,
                           "perturbations_tagged": True,
                           "tamper_refused": True},
        "scale_harmonization": {"all_tiers_standard": True,
                                "unknown_scale_fails_closed": True},
        "record_validation": {"n_records": 2, "errors": []},
        "record_determinism": {"identical": True},
    }
    statuses = {r.check: r.status for r in l1.run(ctx)}
    assert all(s == STATUS_PASS for s in statuses.values()), statuses


# ---------------------------------------------------------------------------
# Level 2
# ---------------------------------------------------------------------------

def _synthetic_tilt_trace(baseline=64.0, dhr=25.0, transient=12.0, seed=0):
    """Piecewise HR trace: 150 s supine, 14 s ramp, 86 s tilt hold,
    60 s recovery (bench geometry)."""
    rng = np.random.default_rng(seed)
    t = np.arange(0.0, 310.0, 0.5)
    hr = np.full_like(t, baseline)
    tilt = t >= 150.0
    hr[tilt] = baseline + dhr * (1.0 - np.exp(-(t[tilt] - 150.0) / 20.0))
    tr = (t >= 150.0) & (t < 180.0)
    hr[tr] += transient * np.exp(-(t[tr] - 150.0) / 8.0)
    rec = t >= 264.0
    hr[rec] = baseline + (hr[rec] - baseline) * np.exp(-(t[rec] - 264.0) / 10.0)
    hr += rng.normal(0, 0.3, t.size)
    return t, hr


def test_l2_tilt_trajectory_metrics_and_bands():
    t, hr = _synthetic_tilt_trace()
    m = l2.check_tilt_trajectory(t, hr, onset_s=150.0, tilt_duration_s=100.0)
    assert abs(m["baseline_hr_bpm"] - 64.0) < 1.0
    assert 15.0 < m["sustained_proxy_dhr_bpm"] < 30.0
    assert m["initial_transient_peak_bpm"] > 15.0  # rise + transient hump
    assert abs(m["recovery_residual_bpm_45s"]) < 10.0


def test_l2_event_hr_response_windows():
    t = np.arange(0.0, 300.0, 0.5)
    hr = np.full_like(t, 62.0)
    hr[(t >= 90.0) & (t < 200.0)] = 70.0
    d = l2.check_event_hr_response(t, hr, 80.0, (20.0, 110.0), baseline_window_s=60.0)
    assert d == pytest.approx(8.0, abs=0.5)


def test_l2_run_full_synthetic_context(rr_series):
    t, hr = _synthetic_tilt_trace()
    # Meal trace: +7 bpm plateau in [80, 190] s (inside the band).
    tm = np.arange(0.0, 320.0, 0.5)
    hrm = np.full_like(tm, 62.0)
    hrm[(tm >= 84.0) & (tm < 172.0)] = 69.0
    # Exercise trace: +30 bpm bout, decaying recovery.
    te = np.arange(0.0, 320.0, 0.5)
    hre = np.full_like(te, 62.0)
    bout = (te >= 100.0) & (te < 180.0)
    hre[bout] = 92.0
    recm = te >= 180.0
    hre[recm] = 62.0 + 30.0 * np.exp(-(te[recm] - 180.0) / 60.0)
    hours = np.linspace(0, 48, 290)
    ctx = {
        "healthy_bench_tilt": {"time": t, "hr_bpm": hr, "onset_s": 150.0,
                               "tilt_duration_s": 100.0},
        "meal_run": {"time": tm, "hr_bpm": hrm, "event_start_s": 20.0,
                     "plateau_window_s": (64.0, 152.0), "time_scale": 0.03},
        "exercise_run": {"time": te, "hr_bpm": hre, "event_start_s": 60.0,
                         "plateau_window_s": (40.0, 120.0),
                         "recovery_window_s": (200.0, 250.0),
                         "es_plateau_bounded": True},
        "timescale_rr": {"rr_intervals_ms": rr_series["rr_intervals_ms"],
                         "respiration_rate_brpm": 15.0},
        "circadian_multiday": {"hour_of_day": hours % 24.0,
                               "mean_hr_bpm": 63.0 + 13.5 * np.cos(
                                   2 * np.pi * (hours - 14.67) / 24.0),
                               "days": 2},
    }
    statuses = {r.check: r.status for r in l2.run(ctx)}
    assert statuses["2.1_tilt_trajectory_battery"] == STATUS_PASS
    assert statuses["2.1_meal_response"] == STATUS_PASS
    assert statuses["2.1_exercise_response"] == STATUS_PASS
    assert statuses["2.2_dfa_alpha1"] == STATUS_PASS
    assert statuses["2.2_rsa_peak"] == STATUS_PASS
    assert statuses["2.2_circadian_amplitude"] == STATUS_PASS


def test_l2_band_violations_fail():
    t, hr = _synthetic_tilt_trace(dhr=3.0)  # no meaningful tilt response
    ctx = {"healthy_bench_tilt": {"time": t, "hr_bpm": hr, "onset_s": 150.0,
                                  "tilt_duration_s": 100.0}}
    statuses = {r.check: r.status for r in l2.run(ctx)}
    assert statuses["2.1_tilt_trajectory_battery"] == STATUS_FAIL


# ---------------------------------------------------------------------------
# Level 3
# ---------------------------------------------------------------------------

def _cohort_row(dhr, rm=35.0):
    return {"sustained_dhr_bpm": dhr, "baseline_hr_bpm": 64.0,
            "initial_transient_bpm": 15.0, "rmssd_ms": rm, "sdnn_ms": 50.0,
            "dfa_alpha1": 1.0, "lf_hf_ratio": 1.2, "age": 28.0, "sex": "female"}


def test_l3_healthy_distribution_small_n_unresolved_tail_but_mean_checked():
    ctx = {"licensed_cohort": {
        "healthy": [_cohort_row(x) for x in (30.0, 33.0, 35.0, 38.0)],
        "hypovolemic_pots": [_cohort_row(x) for x in (50.0, 55.0, 52.0, 58.0)],
    }}
    res = {r.check: r for r in l3.run(ctx)}
    row = res["3.1_healthy_hut_distribution"]
    # n=4 < TAIL_MIN_N: tail unresolved, mean (34) within reference.
    assert row.status == STATUS_UNRESOLVED
    assert "tail" in row.note.lower() or "n=4" in row.note


def test_l3_healthy_distribution_mean_failure_is_fail_even_small_n():
    ctx = {"licensed_cohort": {
        "healthy": [_cohort_row(x) for x in (10.0, 12.0, 14.0, 16.0)],
        "hypovolemic_pots": [_cohort_row(x) for x in (50.0, 55.0, 52.0, 58.0)],
    }}
    res = {r.check: r for r in l3.run(ctx)}
    assert res["3.1_healthy_hut_distribution"].status == STATUS_FAIL


def test_l3_healthy_distribution_large_n_tail_verdict():
    rng = np.random.default_rng(5)
    samples = rng.normal(34.0, 12.0, 24)  # ~50% above 30 -> in [0.40, 0.60]
    ctx = {"licensed_cohort": {
        "healthy": [_cohort_row(float(x)) for x in samples],
        "hypovolemic_pots": [_cohort_row(x) for x in (52.0, 55.0, 53.0, 58.0)],
    }}
    res = {r.check: r for r in l3.run(ctx)}
    assert res["3.1_healthy_hut_distribution"].status == STATUS_PASS


def test_l3_pots_rate_and_meta_contrast():
    ctx = {"licensed_cohort": {
        "healthy": [_cohort_row(x) for x in (30.0, 33.0, 35.0, 38.0)],
        "hypovolemic_pots": [_cohort_row(x) for x in (50.0, 55.0, 52.0, 58.0)],
    }}
    res = {r.check: r for r in l3.run(ctx)}
    row = res["3.1_hypovolemic_pots_rate"]
    assert row.status == STATUS_PASS  # rate 1.0, contrast ~+19.75 in CI
    # Contrast outside CI -> fail.
    ctx2 = {"licensed_cohort": {
        "healthy": [_cohort_row(x) for x in (30.0, 33.0, 35.0, 38.0)],
        "hypovolemic_pots": [_cohort_row(x) for x in (80.0, 85.0, 82.0, 88.0)],
    }}
    res2 = {r.check: r for r in l3.run(ctx2)}
    assert res2["3.1_hypovolemic_pots_rate"].status == STATUS_FAIL


def test_l3_hyperadrenergic_limitation_is_disclosed_not_passed():
    ctx = {"hyperadrenergic_eval": {
        "limitations": ["hyperadrenergic_pots: upright delta-SBP pressor "
                        "criterion ... NOT met - simulated delta-SBP -4.0 mmHg"],
        "delta_SBP_beatwise_mmHg": -4.0}}
    res = {r.check: r for r in l3.run(ctx)}
    assert res["3.1_hyperadrenergic_dsbp_limitation"].status == STATUS_LIMITATION
    ctx_bad = {"hyperadrenergic_eval": {"limitations": [],
                                        "delta_SBP_beatwise_mmHg": -4.0}}
    res2 = {r.check: r for r in l3.run(ctx_bad)}
    assert res2["3.1_hyperadrenergic_dsbp_limitation"].status == STATUS_FAIL


def test_l3_clopper_pearson():
    lo, hi = l3.clopper_pearson(2, 4)
    assert lo < 0.5 < hi
    assert l3.clopper_pearson(0, 4)[0] == 0.0
    assert l3.clopper_pearson(4, 4)[1] == 1.0


# ---------------------------------------------------------------------------
# Level 4 (hermetic: crafted WFDB bytes, no network)
# ---------------------------------------------------------------------------

def _wfdb_word(delta, code):
    return bytes([delta & 0xFF, ((code << 2) | ((delta >> 8) & 0x3)) & 0xFF])


def _wfdb_skip(dt):
    w = bytes([0x00, 59 << 2])
    w += bytes([(dt >> 16) & 0xFF, (dt >> 24) & 0xFF,
                dt & 0xFF, (dt >> 8) & 0xFF])
    return w


def _wfdb_aux(s):
    b = s.encode("latin1")
    w = _wfdb_word(len(b), 63) + b
    if len(b) % 2:
        w += b"\x00"
    return w


def test_l4_wfdb_annotation_reader(tmp_path):
    fs = 250
    beats = b""
    t = 0
    for i in range(1, 40):
        beats += _wfdb_word(240, 1)  # normal beat every 240 samples
    note = (_wfdb_skip(87240) + _wfdb_word(0, 22)
            + _wfdb_aux("Initiate slow tilt up"))
    note2 = (_wfdb_skip(50000) + _wfdb_word(0, 22)
             + _wfdb_aux("Initiate slow tilt down"))
    p = tmp_path / "x.anI"
    p.write_bytes(note + note2 + b"\x00\x00")
    anns = l4.read_wfdb_annotations(str(p))
    assert len(anns) == 2
    assert anns[0]["sample"] == 87240 and anns[0]["aux"] == "Initiate slow tilt up"
    assert anns[1]["sample"] == 87240 + 50000


def test_l4_prcp_delta_hr_episodes(tmp_path):
    """Craft a miniature PRCP-like record: supine ~60 bpm, tilt hold
    ~75 bpm; expect delta-HR ~+15 bpm."""
    fs = 250.0
    anI = (_wfdb_skip(250 * 300) + _wfdb_word(0, 22)
           + _wfdb_aux("Initiate slow tilt up")
           + _wfdb_skip(250 * 180) + _wfdb_word(0, 22)
           + _wfdb_aux("Initiate slow tilt down") + b"\x00\x00")
    (tmp_path / "r1.anI").write_bytes(anI)
    wqrs = _wfdb_skip(250 * 300 - 250 * 130)
    t = 250 * 300 - 250 * 130
    while t < 250 * 480:
        dt = 250 if t < 250 * 300 else 200  # 60 bpm -> 75 bpm on tilt
        wqrs += _wfdb_word(dt, 1)
        t += dt
    wqrs += b"\x00\x00"
    (tmp_path / "r1.wqrs").write_bytes(wqrs)
    eps = l4.prcp_delta_hr_episodes(str(tmp_path), "r1")
    assert len(eps) == 1
    assert eps[0]["delta_hr_bpm"] == pytest.approx(15.0, abs=0.5)


def test_l4_wasserstein_comparison():
    a = [12.0, 15.0, 18.0, 21.0]
    assert l4.compare_orthostatic_distributions(a, a) == 0.0
    w = l4.compare_orthostatic_distributions(a, [x + 2.0 for x in a])
    assert w == pytest.approx(2.0, abs=1e-6)
    assert np.isnan(l4.compare_orthostatic_distributions([], a))


def test_l4_run_unresolved_paths():
    res = {r.check: r for r in l4.run({})}
    assert all(r.status == STATUS_UNRESOLVED for r in res.values())
    ctx = {"prcp": {"error": "URLError: <urlopen error timed out>"},
           "eurobavar": {"error": "OSError: network unreachable"},
           "resting_hrv": {"rmssd_median_ms": 38.0, "n": 4}}
    res = {r.check: r for r in l4.run(ctx)}
    assert res["4_prcp_orthostatic_wasserstein"].status == STATUS_UNRESOLVED
    assert "timed out" in str(res["4_prcp_orthostatic_wasserstein"].measured)
    assert res["4_resting_hrv_norms"].status == STATUS_PASS
    ctx2 = {"prcp": {"real_delta_hr_bpm": [12.0, 15.0, 18.0, 21.0, 14.0],
                     "sim_delta_hr_bpm": [13.0, 16.0, 19.0, 20.0],
                     "window_semantics": "matched"},
            "resting_hrv": {"rmssd_median_ms": 38.0, "n": 4}}
    res2 = {r.check: r for r in l4.run(ctx2)}
    assert res2["4_prcp_orthostatic_wasserstein"].status == STATUS_PASS


# ---------------------------------------------------------------------------
# Negative controls
# ---------------------------------------------------------------------------

def test_nc_parity_pass_and_fail():
    ok, meas = nc.check_parity({
        "engine_dt": {"healthy": 0.02, "disease": 0.02},
        "device": {"healthy": "polar_h10", "disease": "polar_h10"}})
    assert ok
    ok, meas = nc.check_parity({
        "engine_dt": {"healthy": 0.02, "disease": 0.01},
        "device": {"healthy": "polar_h10", "disease": "polar_h10"}})
    assert not ok and "engine_dt" in meas["mismatches"]


def test_nc_separability_gate_logic():
    rng = np.random.default_rng(7)
    H = rng.normal(0, 1, (6, 4))
    D = rng.normal(3, 1, (6, 4))
    auc, _ = nc.check_separability(H, D)
    assert auc >= 0.95  # perfectly separable toy -> would be a gate FAILURE
    H2 = rng.normal(0, 1, (6, 4))
    D2 = rng.normal(0.4, 1, (6, 4))
    auc2, _ = nc.check_separability(H2, D2)
    assert auc2 < 0.95


def test_nc_run_reports_auc_and_gate_failure():
    rng = np.random.default_rng(3)
    healthy = [dict(_cohort_row(30.0 + rng.normal(0, 3)),
                    **{"rmssd_ms": 35 + rng.normal(0, 3)}) for _ in range(5)]
    pots = [dict(_cohort_row(55.0 + rng.normal(0, 3)),
                 **{"rmssd_ms": 25 + rng.normal(0, 3)}) for _ in range(5)]
    ctx = {"licensed_cohort": {"healthy": healthy, "hypovolemic_pots": pots},
           "nc_parity": {"device": {"healthy": "polar_h10",
                                    "disease": "polar_h10"}}}
    res = {r.check: r for r in nc.run(ctx)}
    row = res["NC2_trivial_separability_auc"]
    assert row.measured["auc_full_features"] is not None
    assert row.measured["auc_resting_features_only"] is not None
    assert res["NC_parity_nuisance_channels"].status == STATUS_PASS
    assert res["NC_demographics_disclosure"].status == STATUS_PASS


def test_nc_run_degrades_without_context():
    res = {r.check: r for r in nc.run({})}
    assert res["NC_parity_nuisance_channels"].status == STATUS_UNRESOLVED
    assert res["NC2_trivial_separability_auc"].status == STATUS_UNRESOLVED


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

def test_write_outputs_emits_governing_statement_and_table(tmp_path):
    results = [
        CheckResult("L1", "c1", "target text", {"v": 1}, STATUS_PASS,
                    evidence="ev", note="a note"),
        CheckResult("NC", "c2", "target 2", {"v": 2}, STATUS_FAIL,
                    evidence="ev2"),
        CheckResult("L4", "c3", "target 3", None, STATUS_UNRESOLVED,
                    evidence="ev3"),
    ]
    md = tmp_path / "report.md"
    yml = tmp_path / "gates.yaml"
    payload = write_outputs(results, str(md), str(yml),
                            {"meta": {"gate_seed": 1, "ocpe_commit": "abc",
                                      "started": "now", "n_healthy": 4,
                                      "n_pots": 4}})
    text = md.read_text()
    assert GOVERNING_STATEMENT in text
    assert "Level-5" in text and "does not exist" in text
    assert "| gate | check | target | measured | status | evidence |" in text
    assert "a note" in text
    data = yaml.safe_load(yml.read_text())
    assert data["governing_statement"] == GOVERNING_STATEMENT
    assert data["summary"]["pass"] == 1
    assert data["summary"]["fail"] == 1
    assert data["summary"]["unresolved"] == 1
    assert len(data["results"]) == 3
    assert "level5_status" in data
