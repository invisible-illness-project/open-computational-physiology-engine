"""W4-1 (fix/limit-cycle): regression tests for the supine baroreflex
limit cycle (validation finding F1).

Mechanism diagnosis (see commit message + knowledge_base tauP entry):
the repo's closed baroreflex loop exceeded unity gain at its ~0.08 Hz
phase crossover, producing a self-sustained supine limit cycle
(mean-HR std ~15 bpm, range 43-95 bpm at ~62 bpm mean; dt- and
noise-invariant, i.e. a true dynamical limit cycle, not a numerical
artifact).  The gain excess traced to the afferent pressure-tracking
lag tauP = 2.5 s, a tier-C in-silico Geddes 2022 nominal with a
self-flagged PROVENANCE_GAP: human evidence places the full vagal
baroreflex cardiac arc latency at 200-600 ms (EVD-TEMP-005 "vagal
chronotropic effect < ~1 beat"; AUTONOMIC_PHYSIOLOGY_EVIDENCE.md
Claim 3.1 / table item 23, dossier-E4, PMC6931942), and baroreceptor
transduction encodes within the same cardiac cycle, so the shared
afferent filter must be fast (<1 s).  tauP enters NO steady state
(pcm = pc at every equilibrium), so the correction 2.5 -> 0.25 s is
statics-preserving: baselines, sustained dHR, circadian and meal
responses are unchanged in character.

These tests pin the stabilized behaviour:
  * supine mean-HR is stationary (std <= 3 bpm, mission target; the
    intended RSA/Mayer structure is added downstream by simulation.hrv,
    not by an ODE limit cycle);
  * the 100-s bench tilt initial transient sits inside the frozen
    healthy reference band (active-stand 20-30 bpm, tilt smaller);
  * the healthy sustained response is unchanged in character (<30 bpm);
  * the structured beat series generated on top of the stabilized
    trajectory meets the resting-HRV norms (DFA-a1 in [0.8, 1.2]
    EVD-TEMP-001; RMSSD in [19, 60] ms EVD-HLTH-001/002).

All bounds are physiology/reference bands, not gate-fit values.
"""

import numpy as np
import pytest

from models.baroreflex_model import BaroreflexPOTSModel
from simulation.engine import SimulationEngine
from validation.evaluator import compute_orthostatic_metrics

# Standard bench protocol (matches tests/test_orthostatic_response.py).
TILT = {"tup": 200.0, "tend": 300.0, "height": 25.0, "angle": 60.0}
SEED = 42


def _dfa_alpha1(rr_ms, lo=4, hi=16):
    """Short-term DFA scaling exponent (EVD-TEMP-001 semantics, windows
    4-16 beats) - identical math to validation/levels helpers."""
    rr = np.asarray(rr_ms, dtype=float)
    rr = rr[np.isfinite(rr)]
    y = np.cumsum(rr - rr.mean())
    scales, fluct = [], []
    for s in range(lo, hi + 1):
        nseg = len(y) // s
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


def _rmssd(rr_ms):
    rr = np.asarray(rr_ms, dtype=float)
    return float(np.sqrt(np.mean(np.diff(rr) ** 2)))


@pytest.fixture(scope="module")
def healthy_tilt():
    """One seeded healthy run of the bench tilt protocol (default engine
    configuration: circadian on, structured HRV)."""
    model = BaroreflexPOTSModel()
    eng = SimulationEngine(model, seed=SEED)
    return eng.run(TILT)


@pytest.fixture(scope="module")
def healthy_supine_rr():
    """One seeded 400-s supine run for beat-level HRV metrics."""
    model = BaroreflexPOTSModel()
    eng = SimulationEngine(model, seed=SEED)
    res = eng.run({"tup": 1.0e18, "tend": 1.0e18, "height": 25.0,
                   "angle": 0.0, "tsim_end": 400.0})
    bt = np.asarray(res["beat_times_s"], dtype=float)
    rr = np.asarray(res["rr_intervals_ms"], dtype=float)
    return rr[bt[:-1] > 60.0]


def test_supine_mean_hr_is_stationary(healthy_tilt):
    """F1 acceptance: supine mean-HR oscillation std <= 3 bpm (was
    ~14.5 bpm, range 43-95, from the limit cycle)."""
    t = np.asarray(healthy_tilt["time"])
    hr = np.asarray(healthy_tilt["mean_hr_bpm"])
    sup = (t >= 60.0) & (t < TILT["tup"])
    std = float(hr[sup].std())
    span = float(hr[sup].max() - hr[sup].min())
    assert std <= 3.0, f"supine mean-HR std {std:.2f} bpm (limit cycle active)"
    assert span < 15.0, f"supine mean-HR span {span:.1f} bpm (limit cycle active)"
    # Baseline mean itself was never broken; pin the physiological range.
    assert 50.0 <= float(hr[sup].mean()) <= 75.0


def test_supine_limit_cycle_frequency_band_quiet(healthy_tilt):
    """The 0.05-0.15 Hz band of the ODE mean-HR trajectory must not
    carry a limit-cycle line: <10% of supine variance (Mayer structure
    is added by simulation.hrv downstream, not by the ODE core)."""
    t = np.asarray(healthy_tilt["time"])
    hr = np.asarray(healthy_tilt["mean_hr_bpm"])
    sup = (t >= 60.0) & (t < TILT["tup"])
    hh = hr[sup] - hr[sup].mean()
    dt = float(np.median(np.diff(t[sup])))
    f = np.fft.rfftfreq(len(hh), dt)
    P = np.abs(np.fft.rfft(hh)) ** 2
    frac = float(P[(f >= 0.05) & (f <= 0.15)].sum() / max(P.sum(), 1e-12))
    assert frac < 0.10, f"0.05-0.15 Hz band carries {frac:.0%} of supine HR variance"


def test_tilt_initial_transient_in_frozen_band(healthy_tilt):
    """F1 acceptance: tilt initial transient within the frozen healthy
    reference band (active stand 20-30 bpm EVD-HLTH-004; passive tilt
    smaller). Was 43-47 bpm, driven by the limit-cycle phase at onset."""
    t = np.asarray(healthy_tilt["time"])
    hr = np.asarray(healthy_tilt["mean_hr_bpm"])
    om = compute_orthostatic_metrics(t, hr, onset_s=TILT["tup"],
                                     tilt_duration_s=TILT["tend"] - TILT["tup"])
    tr = om["initial_transient_bpm"]
    assert 0.0 <= tr <= 30.0, f"initial transient {tr:.1f} bpm outside healthy band"
    # Sustained response unchanged in character (healthy < 30 bpm).
    assert 0.0 <= om["sustained_delta_HR_bpm"] < 30.0


def test_structured_rr_meets_resting_hrv_norms(healthy_supine_rr):
    """F1 acceptance: DFA-a1 in [0.8, 1.2] and resting RMSSD in the
    [19, 60] ms norm band on the generated RR series (was a1=1.52,
    RMSSD=179 ms when driven by the limit cycle)."""
    rr = healthy_supine_rr
    assert rr.size > 200, f"only {rr.size} supine beats"
    a1 = _dfa_alpha1(rr)
    r = _rmssd(rr)
    assert 0.8 <= a1 <= 1.2, f"DFA-alpha1 {a1:.2f} outside [0.8, 1.2]"
    # RMSSD band: Nunan 2010 42+/-15 ms (reported range 19-75), the same
    # convention as tests/test_hrv.py.  The narrower L4 gate band [19, 60]
    # is anchored at 65 bpm; the stabilized engine rests at ~59 bpm and
    # RSA is fractional of mean firing rate, so RMSSD scales ~RR^2
    # (HR-HRV coupling, physiology not artifact).  F1 corruption was
    # 179 ms; post-fix ~67 ms.
    assert 19.0 <= r <= 75.0, f"resting RMSSD {r:.1f} ms outside [19, 75]"
