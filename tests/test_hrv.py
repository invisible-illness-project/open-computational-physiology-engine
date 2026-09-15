"""Statistical validation of the structured HRV generator (G-P0-05, W2-E).

Normative anchors (5-min supine healthy adults, Nunan 2010 meta-review,
n=21,438, PMID 20663071; EVD-HLTH-002 / AUTONOMIC Claim 1.5):
  RMSSD 42+/-15 ms (range 19-75), SDNN 50+/-16 ms (range 32-93),
  LF 519+/-291 ms^2, HF 657+/-777 ms^2.
DFA-alpha1 healthy-awake target ~1.0, range 0.7-1.2 (EVD-TEMP-001).
"""

import numpy as np
import pytest

from simulation.hrv import (
    HRVConfig, generate_rr_series, rmssd_age_factor, HRV_CONFIG_VERSION,
)

SEED = 42
DURATION_S = 600.0          # 10-min reference record
N_SAMPLES = 6001


def _inputs(hr=65.0, vagal=0.5, symp=0.5, resp=15.5, duration=DURATION_S,
            n=N_SAMPLES, stage=0):
    t = np.linspace(0.0, duration, n)
    bcast = lambda v: np.full(n, float(v)) if np.isscalar(v) else np.asarray(v, float)
    return {
        "time_s": t,
        "mean_hr_bpm": bcast(hr),
        "vagal_drive": bcast(vagal),
        "sympathetic_drive": bcast(symp),
        "respiration_rate_brpm": bcast(resp),
        "sleep_stage_code": np.full(n, stage, dtype=int),
    }


# ---------------------------------------------------------------------------
# HRV metric helpers (self-contained; the generator must stand up to
# standard, independently implemented metrics).
# ---------------------------------------------------------------------------
def rmssd(rr_ms):
    return float(np.sqrt(np.mean(np.diff(rr_ms) ** 2)))


def sdnn(rr_ms):
    return float(np.std(rr_ms, ddof=1))


def dfa_alpha1(rr_ms, lo=4, hi=16):
    """Detrended fluctuation analysis, short-term scaling exponent
    (windows lo..hi beats, linear detrend) — EVD-TEMP-001 semantics."""
    rr = np.asarray(rr_ms, dtype=float)
    y = np.cumsum(rr - rr.mean())
    scales, fluct = [], []
    for s in range(lo, hi + 1):
        nseg = len(y) // s
        if nseg < 1:
            continue
        rms = []
        for j in range(nseg):
            seg = y[j * s:(j + 1) * s]
            x = np.arange(s)
            p = np.polyfit(x, seg, 1)
            rms.append(np.sqrt(np.mean((seg - np.polyval(p, x)) ** 2)))
        scales.append(s)
        fluct.append(np.mean(rms))
    a, _ = np.polyfit(np.log(scales), np.log(fluct), 1)
    return float(a)


def band_powers(rr_ms, fs=4.0):
    """Periodogram of the evenly resampled RR tachogram.

    Returns (freqs, power, LF, HF) with LF = 0.04-0.15 Hz,
    HF = 0.15-0.40 Hz (Task Force 1996 bands)."""
    tt = np.cumsum(rr_ms / 1000.0)
    tg = np.arange(0.0, tt[-1], 1.0 / fs)
    sig = np.interp(tg, tt, rr_ms)
    sig = sig - sig.mean()
    P = np.abs(np.fft.rfft(sig * np.hanning(len(sig)))) ** 2
    freqs = np.fft.rfftfreq(len(sig), 1.0 / fs)
    lf = float(P[(freqs >= 0.04) & (freqs < 0.15)].sum())
    hf = float(P[(freqs >= 0.15) & (freqs <= 0.40)].sum())
    return freqs, P, lf, hf


def peak_freq(freqs, P, lo, hi):
    mask = (freqs >= lo) & (freqs <= hi)
    return float(freqs[mask][np.argmax(P[mask])])


# ---------------------------------------------------------------------------
# Output contract (binding for W2-F)
# ---------------------------------------------------------------------------
def test_output_contract_keys_and_dtypes():
    out = generate_rr_series(_inputs(), seed=SEED)
    assert set(out.keys()) == {"beat_times_s", "rr_intervals_ms",
                               "beat_types", "provenance"}
    assert out["beat_times_s"].dtype == np.float64
    assert out["rr_intervals_ms"].dtype == np.float64
    assert out["beat_types"].dtype.kind == "U"
    assert len(out["beat_times_s"]) == len(out["beat_types"])
    assert len(out["rr_intervals_ms"]) == len(out["beat_times_s"]) - 1
    assert np.all(np.diff(out["beat_times_s"]) > 0)
    assert np.all(out["rr_intervals_ms"] > 0)
    assert set(np.unique(out["beat_types"])) <= {"normal", "ectopic"}
    prov = out["provenance"]
    assert prov["seed"] == SEED
    assert prov["config_version"] == HRV_CONFIG_VERSION
    assert "parameters" in prov and "claim_ids" in prov
    for p in prov["parameters"].values():
        for key in ("value_used", "mean", "units", "distribution",
                    "evidence_tier", "claim_ids", "source"):
            assert key in p


def test_determinism_under_seed():
    a = generate_rr_series(_inputs(), seed=SEED)
    b = generate_rr_series(_inputs(), seed=SEED)
    np.testing.assert_array_equal(a["beat_times_s"], b["beat_times_s"])
    np.testing.assert_array_equal(a["rr_intervals_ms"], b["rr_intervals_ms"])
    np.testing.assert_array_equal(a["beat_types"], b["beat_types"])
    c = generate_rr_series(_inputs(), seed=SEED + 1)
    assert not np.array_equal(a["rr_intervals_ms"], c["rr_intervals_ms"])


def test_chunk_size_invariance():
    """Chunking is a memory bound only — it must not change the series."""
    ref = generate_rr_series(_inputs(), seed=SEED)
    chunked = generate_rr_series(_inputs(), seed=SEED,
                                 config=HRVConfig(chunk_s=47.0))
    np.testing.assert_allclose(ref["rr_intervals_ms"],
                               chunked["rr_intervals_ms"], atol=1e-6)


# ---------------------------------------------------------------------------
# Normative statistics
# ---------------------------------------------------------------------------
def test_rmssd_sdnn_normative_ballpark():
    out = generate_rr_series(_inputs(), seed=SEED)
    rr = out["rr_intervals_ms"]
    r, s = rmssd(rr), sdnn(rr)
    # Nunan 2010: RMSSD 42+/-15 (19-75); SDNN 50+/-16 (32-93).
    assert 25.0 <= r <= 65.0, f"RMSSD {r:.1f} outside healthy ballpark"
    assert 32.0 <= s <= 93.0, f"SDNN {s:.1f} outside healthy ballpark"


def test_dfa_alpha1_healthy_awake():
    out = generate_rr_series(_inputs(), seed=SEED)
    a1 = dfa_alpha1(out["rr_intervals_ms"])
    assert 0.8 <= a1 <= 1.2, f"DFA-alpha1 {a1:.3f} outside [0.8, 1.2]"


def test_alpha1_population_spread_healthy_range():
    """Across subject draws (seeds), alpha1 stays in the healthy 0.7-1.2
    range (EVD-TEMP-001) — the legacy uniform noise gave alpha1 = 0.5
    (white noise), which is falsified physiology."""
    for s in range(8):
        out = generate_rr_series(_inputs(), seed=100 + s)
        a1 = dfa_alpha1(out["rr_intervals_ms"])
        assert 0.7 <= a1 <= 1.2, f"seed {100 + s}: alpha1 {a1:.3f}"


# ---------------------------------------------------------------------------
# Spectral structure
# ---------------------------------------------------------------------------
def test_rsa_peak_tracks_respiration_frequency():
    for brpm in (12.0, 15.5, 20.0):
        out = generate_rr_series(_inputs(resp=brpm), seed=SEED)
        freqs, P, _, hf = band_powers(out["rr_intervals_ms"])
        peak = peak_freq(freqs, P, 0.15, 0.40)
        assert abs(peak - brpm / 60.0) < 0.03, (
            f"resp {brpm} brpm: HF peak at {peak:.3f} Hz")
        assert hf > 0.0


def test_lf_power_near_0p1_hz():
    out = generate_rr_series(_inputs(), seed=SEED)
    freqs, P, lf, hf = band_powers(out["rr_intervals_ms"])
    peak = peak_freq(freqs, P, 0.04, 0.15)
    assert abs(peak - 0.1) < 0.03, f"LF peak at {peak:.3f} Hz"
    assert lf > 0.0


def test_lf_hf_responds_to_respiration_without_sympathetic_change():
    """Required failure-mode reproduction (AUTONOMIC dossier Claim 6.2 /
    Claim 6.3): paced 0.1 Hz (6 brpm) breathing moves RSA power into the LF
    band, inflating LF and LF/HF with ZERO sympathetic-drive change.
    LF/HF is therefore NOT a sympathovagal index and must never be
    labeled one — this test pins the mechanism, not an interpretation."""
    symp = 0.5
    out_fast = generate_rr_series(_inputs(resp=15.5, symp=symp), seed=SEED)
    out_slow = generate_rr_series(_inputs(resp=6.0, symp=symp), seed=SEED)
    _, _, lf_f, hf_f = band_powers(out_fast["rr_intervals_ms"])
    _, _, lf_s, hf_s = band_powers(out_slow["rr_intervals_ms"])
    ratio_fast = lf_f / hf_f
    ratio_slow = lf_s / hf_s
    assert ratio_slow > 2.0 * ratio_fast, (
        f"0.1 Hz breathing should inflate LF/HF (got {ratio_fast:.2f} -> "
        f"{ratio_slow:.2f}) with unchanged sympathetic drive")


def test_vagal_drive_reduction_lowers_rmssd_monotonically():
    rms = []
    for v in (0.9, 0.7, 0.5, 0.3, 0.1):
        out = generate_rr_series(_inputs(vagal=v), seed=SEED)
        rms.append(rmssd(out["rr_intervals_ms"]))
    assert all(rms[i] > rms[i + 1] for i in range(len(rms) - 1)), (
        f"RMSSD not monotonic in vagal drive: {rms}")


def test_age_hook_suppresses_rmssd():
    young = generate_rr_series(_inputs(), seed=SEED,
                               config=HRVConfig(age_years=25.0))
    old = generate_rr_series(_inputs(), seed=SEED,
                             config=HRVConfig(age_years=65.0))
    assert rmssd(old["rr_intervals_ms"]) < rmssd(young["rr_intervals_ms"])
    # Factor shape: plateau 0.25, reference 1.0 at 25 y (POPULATION A.2).
    assert rmssd_age_factor(25.0) == pytest.approx(1.0)
    assert rmssd_age_factor(80.0) == pytest.approx(0.25)


# ---------------------------------------------------------------------------
# Ectopy
# ---------------------------------------------------------------------------
def test_ectopy_phase_reset_and_compensatory_pause():
    cfg = HRVConfig(subject_params={"ectopy_prob_per_beat": 0.02})
    out = generate_rr_series(_inputs(), seed=SEED, config=cfg)
    types = out["beat_types"]
    rr = out["rr_intervals_ms"]
    idx = np.where(types == "ectopic")[0]
    assert len(idx) >= 3, "expected several ectopic beats at p=0.02/beat"
    # Convention: rr[j] = beats[j+1] - beats[j].  An ectopic beat at index i
    # ENDS the short coupling interval rr[i-1] and STARTS the pause rr[i].
    t_loc = 60000.0 / 65.0  # local sinus cycle from the input mean HR (ms)
    for i in idx[:8]:
        assert 1 <= i < len(rr) - 1
        coup, pause = rr[i - 1], rr[i]
        # Prematurity: coupling interval clearly shorter than the sinus RR
        assert coup < 0.85 * t_loc
        # Fully compensatory pause: coupling + pause ~= 2 x local sinus RR
        assert abs((coup + pause) - 2.0 * t_loc) < 0.10 * t_loc
        # The post-pause beat is normal (no stacked ectopy)
        assert types[i + 1] == "normal"


def test_ectopy_disabled_by_config():
    out = generate_rr_series(_inputs(), seed=SEED,
                             config=HRVConfig(ectopy_enabled=False))
    assert set(np.unique(out["beat_types"])) == {"normal"}


# ---------------------------------------------------------------------------
# Mean-HR tracking
# ---------------------------------------------------------------------------
def test_beat_rate_tracks_mean_hr_trajectory():
    """Statistical tracking: 60-s window mean rates follow the input
    trajectory.  Tolerance is HRV-consistent: with SDNN ~65 ms the 1/f
    component gives 1-min mean-HR wander of ~3-4 bpm SD (this is the
    physiology the generator is REQUIRED to produce, EVD-TEMP-001), so a
    12 bpm (~3 sigma) window tolerance plus a trend-correlation floor is
    the honest assertion."""
    n = N_SAMPLES
    t = np.linspace(0.0, DURATION_S, n)
    hr = np.linspace(55.0, 95.0, n)  # ramp
    out = generate_rr_series(_inputs(hr=hr, n=n), seed=SEED)
    beats = out["beat_times_s"]
    win = 60.0
    achieved, target = [], []
    for t0 in np.arange(0.0, DURATION_S - win, win):
        sel = (beats >= t0) & (beats < t0 + win)
        assert sel.sum() > 10
        achieved.append(60.0 / np.mean(np.diff(beats[sel])))
        target.append(np.interp(t0 + win / 2.0, t, hr))
    achieved, target = np.array(achieved), np.array(target)
    err = achieved - target
    assert np.abs(err).mean() < 5.0, f"mean |err| {np.abs(err).mean():.2f} bpm"
    assert np.abs(err).max() < 12.0, f"max |err| {np.abs(err).max():.2f} bpm"
    assert np.corrcoef(achieved, target)[0, 1] > 0.9


def test_beat_rate_tracks_tightly_with_low_modulation():
    """Mechanistic tracking: with modulation amplitudes ~0 the IPFM core
    must reproduce the input trajectory to within interpolation error."""
    quiet = {"rsa_amplitude_0p1Hz": 1e-4, "mayer_amplitude": 1e-4,
             "fractal_amplitude": 1e-4, "ectopy_prob_per_beat": 0.0}
    n = N_SAMPLES
    t = np.linspace(0.0, DURATION_S, n)
    hr = np.linspace(55.0, 95.0, n)
    out = generate_rr_series(_inputs(hr=hr, n=n), seed=SEED,
                             config=HRVConfig(subject_params=quiet))
    beats = out["beat_times_s"]
    win = 30.0
    for t0 in np.arange(15.0, DURATION_S - win, 60.0):
        sel = (beats >= t0) & (beats < t0 + win)
        achieved = 60.0 / np.mean(np.diff(beats[sel]))
        tgt = np.interp(t0 + win / 2.0, t, hr)
        assert abs(achieved - tgt) < 1.5, (
            f"window {t0:.0f}s: achieved {achieved:.2f} vs {tgt:.2f} bpm")


def test_beat_count_matches_mean_hr():
    out = generate_rr_series(_inputs(hr=60.0), seed=SEED)
    expected = 60.0 / 60.0 * DURATION_S  # 60 bpm * 600 s
    assert abs(len(out["beat_times_s"]) - expected) / expected < 0.02


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------
def test_missing_key_raises():
    bad = _inputs()
    del bad["vagal_drive"]
    with pytest.raises(KeyError):
        generate_rr_series(bad, seed=SEED)


def test_nonpositive_hr_raises():
    with pytest.raises(ValueError):
        generate_rr_series(_inputs(hr=0.0), seed=SEED)



# ---------------------------------------------------------------------------
# Engine wiring (hrv_model flag; G-P0-05). Short ODE runs only — the full
# statistical battery above runs directly on generate_rr_series.
# ---------------------------------------------------------------------------
import contextlib
import io
import os

from models.baroreflex_model import BaroreflexPOTSModel
from simulation.engine import SimulationEngine

KB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "knowledge_base")
TILT_SHORT = {"tup": 20.0, "tend": 45.0, "height": 30.0, "angle": 60.0}


def _make_engine(**kw):
    with contextlib.redirect_stdout(io.StringIO()):
        model = BaroreflexPOTSModel(phenotype=None, kb_path=KB_PATH)
    return SimulationEngine(model, **kw)


def test_engine_structured_mode_attaches_rr_outputs():
    eng = _make_engine(seed=SEED)
    res = eng.run(dict(TILT_SHORT))
    for key in ("beat_times_s", "rr_intervals_ms", "beat_types", "hrv_provenance"):
        assert key in res, f"missing {key} in structured mode"
    assert res["beat_times_s"].dtype == np.float64
    assert res["rr_intervals_ms"].dtype == np.float64
    assert res["beat_types"].dtype.kind == "U"
    assert set(np.unique(res["beat_types"])) <= {"normal", "ectopic"}
    assert res["hrv_provenance"]["seed"] == SEED
    # Beat times stay inside the simulated horizon
    assert res["beat_times_s"][0] >= res["time"][0]
    assert res["beat_times_s"][-1] <= res["time"][-1] + 1.0


def test_engine_structured_deterministic_and_noise_free_mean_hr():
    r1 = _make_engine(seed=SEED).run(dict(TILT_SHORT))
    r2 = _make_engine(seed=SEED).run(dict(TILT_SHORT))
    np.testing.assert_array_equal(r1["rr_intervals_ms"], r2["rr_intervals_ms"])
    np.testing.assert_array_equal(r1["mean_hr_bpm"], r2["mean_hr_bpm"])
    # Structured mode removes the uniform beat noise from the ODE loop:
    # its trajectory must equal the legacy path with hrv_noise forced to 0.
    r3 = _make_engine(seed=SEED, hrv_model="legacy",
                      hrv_noise=0.0).run(dict(TILT_SHORT))
    np.testing.assert_array_equal(r1["mean_hr_bpm"], r3["mean_hr_bpm"])
    # ... while the legacy default (hrv_noise=0.02) perturbs it.
    r4 = _make_engine(seed=SEED, hrv_model="legacy").run(dict(TILT_SHORT))
    assert not np.array_equal(r1["mean_hr_bpm"], r4["mean_hr_bpm"])


def test_engine_legacy_mode_keeps_uniform_noise_path():
    res = _make_engine(seed=SEED, hrv_model="legacy").run(dict(TILT_SHORT))
    assert "beat_times_s" not in res
    assert "rr_intervals_ms" not in res
    assert "mean_hr_bpm" in res  # legacy channels unchanged
    # Legacy path remains seed-deterministic
    res2 = _make_engine(seed=SEED, hrv_model="legacy").run(dict(TILT_SHORT))
    np.testing.assert_array_equal(res["mean_hr_bpm"], res2["mean_hr_bpm"])


def test_engine_rejects_unknown_hrv_model():
    with pytest.raises(ValueError):
        _make_engine(seed=SEED, hrv_model="pink")
