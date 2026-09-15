"""
Tests for G-P0-06: circadian + sleep coupling.

Contract under test:
  1. The 24-h circadian modulation is PRESENT in the mean-HR trajectory with
     the evidence amplitude ballpark (cosinor half-amplitude ~13.5 bpm,
     acrophase ~14:40; EVD-HLTH-003) -- previously the circadian drive was
     computed but never coupled to anything ("fictional").
  2. Circadian/sleep state ACTUALLY couples into model parameters (Hm/HM
     chronotropic set point; p2Ru/p2Ra defended-pressure set point).
  3. A sleep/wake state machine produces stage architecture (N3/REM appear
     in the sleep window; is_sleeping is a real state).
  4. Multi-day runs work and reproduce day-to-day resting-HR variability
     (within-person CV ~= 4.6%, EVD-POP-004) via the OU baseline drift.
"""
import os
import sys
import io
import contextlib

import numpy as np
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.baroreflex_model import BaroreflexPOTSModel
from simulation.engine import SimulationEngine
from simulation.time_engine import SLEEP_STAGE_CODES

KB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")


def _engine(start_hour=8.0, phenotype=None, seed=42, **kw):
    with contextlib.redirect_stdout(io.StringIO()):
        model = BaroreflexPOTSModel(phenotype=phenotype, kb_path=KB_PATH)
    return SimulationEngine(model, seed=seed, start_hour=start_hour, **kw)


def _fit_cosinor(hours, values, period_h=24.0):
    """Least-squares single-component cosinor: returns (amplitude, acrophase_h)."""
    w = 2.0 * np.pi / period_h
    X = np.column_stack([np.ones_like(hours), np.cos(w * hours), np.sin(w * hours)])
    beta, *_ = np.linalg.lstsq(X, values, rcond=None)
    amp = float(np.hypot(beta[1], beta[2]))
    acro = float(np.mod(np.arctan2(beta[2], beta[1]) / w, period_h))
    return amp, acro


# ---------------------------------------------------------------------------
# 1. 24-h modulation present with evidence amplitude ballpark
# ---------------------------------------------------------------------------

def test_circadian_24h_modulation_amplitude_and_phase():
    eng = _engine()
    out = eng.run_multiday(days=4, step_s=300.0, seed=42)
    hours = out["hour_of_day"] + out["day_index"] * 24.0
    # Use absolute time for the fit; HR includes sleep-stage offsets (~2 bpm)
    # and OU drift, so tolerance is the PARAMETER_SPEC ballpark [8, 20] bpm.
    amp, acro = _fit_cosinor(hours, out["mean_hr_bpm"])
    assert 8.0 <= amp <= 20.0, f"circadian HR amplitude {amp:.1f} bpm outside [8, 20]"
    # Acrophase ~14:40 lab (allow free-living spread 13:00-17:30)
    assert 13.0 <= acro <= 17.5, f"acrophase {acro:.2f} h not in afternoon"
    # Vagal drive must peak at night (anti-phase to the HR rhythm)
    v = out["vagal_drive"]
    night = out["hour_of_day"][(out["hour_of_day"] >= 1.0) & (out["hour_of_day"] <= 5.0)]
    day = out["hour_of_day"][(out["hour_of_day"] >= 12.0) & (out["hour_of_day"] <= 16.0)]
    assert v[(out["hour_of_day"] >= 1.0) & (out["hour_of_day"] <= 5.0)].mean() > \
           v[(out["hour_of_day"] >= 12.0) & (out["hour_of_day"] <= 16.0)].mean()


def test_circadian_amplitude_matches_anchor_when_isolated():
    """With sleep stages neutralized (awake all day) and OU off, the
    recovered cosinor amplitude must match the 13.5 bpm anchor (E2)."""
    eng = _engine(start_hour=8.0, ou_enabled=False)
    # Force the sleep machine out of the picture: schedule sleep window that
    # never triggers is not possible (window always wraps); instead evaluate
    # the pure circadian offset function directly.
    offsets = []
    hours = []
    for i in range(288):  # 24 h at 5-min steps
        eng.time_engine.wall_seconds = i * 300.0
        offsets.append(eng.time_engine.circadian_hr_offset_bpm())
        hours.append(i * 300.0 / 3600.0)
    amp, acro = _fit_cosinor(np.array(hours), np.array(offsets))
    assert amp == pytest.approx(13.5, abs=0.5)
    # Simulation starts at 08:00, so the 14:40 acrophase appears 6.67 h in.
    assert acro == pytest.approx((14.0 + 40.0 / 60.0) - 8.0, abs=0.25)


# ---------------------------------------------------------------------------
# 2. Coupling into model parameters (must not be fictional)
# ---------------------------------------------------------------------------

def test_circadian_overlay_modifies_model_parameters():
    eng = _engine()
    base = dict(eng.model.params)
    eng.time_engine.wall_seconds = 0.0          # 08:00
    p_am = eng._circadian_param_overlay(base)
    eng.time_engine.wall_seconds = 18 * 3600.0  # 02:00 next day
    p_night = eng._circadian_param_overlay(base)
    # Chronotropic set point (p2H re-targeting) moves with time of day
    assert p_night["p2H"] != p_am["p2H"]
    # Night p2H is LOWER (lower HR set point at night)
    assert p_night["p2H"] < p_am["p2H"]
    # Gain modulation is OFF by default (magnitude unresolved, E5)
    assert p_am["kR"] == base["kR"] and p_night["kR"] == base["kR"]
    # The defended-pressure (p2R) coupling is OFF by default in the ODE
    # core (structural HR-inversion limitation, see engine docstring);
    # enabling it must produce the night-dip direction.
    assert p_am["p2Ru"] == base["p2Ru"] and p_night["p2Ru"] == base["p2Ru"]
    eng.circadian_bp_coupling = 1.0
    eng.time_engine.wall_seconds = 0.0
    p_am_bp = eng._circadian_param_overlay(base)
    eng.time_engine.wall_seconds = 18 * 3600.0
    p_night_bp = eng._circadian_param_overlay(base)
    assert p_night_bp["p2Ru"] < p_am_bp["p2Ru"]
    # The baseline snapshot itself is never mutated
    assert eng.model.params["p2H"] == base["p2H"]


def test_bp_dip_factor_peak_to_trough_matches_abpm_anchor():
    """The slow-layer defended-pressure factor must reproduce the ABPM
    nocturnal dip 14.1% peak-to-trough (EVD-HLTH-003)."""
    eng = _engine()
    factors = []
    for i in range(288):
        eng.time_engine.wall_seconds = i * 300.0
        factors.append(eng.time_engine.circadian_bp_factor())
    p2t = max(factors) - min(factors)
    assert p2t == pytest.approx(0.141, abs=0.01)
    # And it is exposed on multiday outputs for the dataset layer
    out = eng.run_multiday(days=1, step_s=600.0, seed=42)
    assert "bp_setpoint_factor" in out
    assert out["bp_setpoint_factor"].max() - out["bp_setpoint_factor"].min() > 0.10


def test_circadian_coupling_changes_ode_resting_hr():
    """Two identical short ODE runs at different start hours must produce
    measurably different resting HR (coupling is real, not cosmetic).

    The mean is taken over the early settling window (8-20 s): after the
    tauH ~6.25 s transient but before the model's documented intrinsic
    limit cycle (steep kH=kR=25 Hill controllers) develops -- that
    oscillation is pre-existing, present with circadian coupling disabled,
    and would make late-window means phase-dependent."""
    res_day = _engine(start_hour=14.0).run(
        {"tup": 1.0e30, "tend": 40.0, "height": 25.0, "angle": 60.0})
    res_night = _engine(start_hour=2.0).run(
        {"tup": 1.0e30, "tend": 40.0, "height": 25.0, "angle": 60.0})
    def early_mean(res):
        m = (res["time"] >= 8.0) & (res["time"] < 20.0)
        return float(res["Hc"][m].mean() * 60.0)
    hr_day = early_mean(res_day)
    hr_night = early_mean(res_night)
    assert hr_day > hr_night + 5.0, (
        f"circadian coupling absent: day {hr_day:.1f} vs night {hr_night:.1f} bpm"
    )


# ---------------------------------------------------------------------------
# 3. Sleep/wake state machine
# ---------------------------------------------------------------------------

def test_sleep_state_machine_produces_stage_architecture():
    eng = _engine()
    out = eng.run_multiday(days=2, step_s=300.0, seed=42)
    codes = out["sleep_stage_code"]
    hour = out["hour_of_day"]
    night = (hour >= 23.0) | (hour < 7.0)
    day = ~night
    # Awake during the day, sleep stages at night
    assert (codes[day] == SLEEP_STAGE_CODES["awake"]).all()
    night_codes = set(np.unique(codes[night]).tolist())
    assert SLEEP_STAGE_CODES["N3"] in night_codes
    assert SLEEP_STAGE_CODES["REM"] in night_codes
    # Deep NREM predominates early night, REM late night (hypnogram structure)
    early = night & ((hour >= 23.0) | (hour < 2.0))
    late = night & (hour >= 5.0) & (hour < 7.0)
    frac_n3_early = (codes[early] == SLEEP_STAGE_CODES["N3"]).mean()
    frac_rem_late = (codes[late] == SLEEP_STAGE_CODES["REM"]).mean()
    assert frac_n3_early > 0.25
    assert frac_rem_late > 0.15
    # N3 has the highest vagal drive of all stages (EVD-HLTH-007)
    vagal = out["vagal_drive"]
    mean_by_stage = {c: vagal[codes == c].mean() for c in np.unique(codes)}
    assert mean_by_stage[SLEEP_STAGE_CODES["N3"]] == max(mean_by_stage.values())


def test_respiration_is_state_conditioned():
    eng = _engine()
    out = eng.run_multiday(days=2, step_s=300.0, seed=42)
    codes = out["sleep_stage_code"]
    rr = out["respiration_rate_brpm"]
    rr_n3 = rr[codes == SLEEP_STAGE_CODES["N3"]]
    rr_rem = rr[codes == SLEEP_STAGE_CODES["REM"]]
    rr_awake = rr[codes == SLEEP_STAGE_CODES["awake"]]
    # N3 ~13 low CV; REM ~16 high CV; awake ~15.5 (EVD-HLTH-010)
    assert 11.5 < rr_n3.mean() < 14.5
    assert 14.5 < rr_rem.mean() < 17.5
    assert 14.0 < rr_awake.mean() < 17.0
    assert rr_rem.std() > rr_n3.std()


# ---------------------------------------------------------------------------
# 4. Multi-day runs + day-to-day RHR variability (OU drift)
# ---------------------------------------------------------------------------

def test_multiday_run_structure():
    eng = _engine()
    out = eng.run_multiday(days=3, step_s=600.0, seed=42)
    # Timestamps are post-step, so the final sample lands at day 3 exactly.
    assert out["day_index"].min() == 0 and out["day_index"].max() <= 3
    assert len(out["time_s"]) == 3 * 144
    assert np.all(np.isfinite(out["mean_hr_bpm"]))
    # HRV contract getter is populated
    assert eng.get_hrv_inputs() is out
    for key in ("time_s", "mean_hr_bpm", "vagal_drive", "sympathetic_drive",
                "respiration_rate_brpm", "sleep_stage_code"):
        assert key in out


def test_day_to_day_rhr_cv_matches_population_anchor():
    """Within-person day-to-day RHR CV ~= 4.6% (n=92,457; EVD-POP-004).
    Tolerance [2%, 9%]: the OU SD anchor is 3.03 bpm absolute, so the CV
    depends on the model's resting-HR mesor."""
    eng = _engine()
    out = eng.run_multiday(days=14, step_s=600.0, seed=42)
    hr = out["mean_hr_bpm"]
    hour = out["hour_of_day"]
    days = out["day_index"]
    # Nocturnal RHR proxy: fixed 04:00-05:00 window every day (removes most
    # within-day circadian variance, leaving day-to-day drift)
    mask = (hour >= 4.0) & (hour < 5.0)
    daily = np.array([hr[mask & (days == d)].mean() for d in range(14)])
    cv = daily.std(ddof=1) / daily.mean()
    assert 0.02 <= cv <= 0.09, f"day-to-day RHR CV {cv:.3f} outside [0.02, 0.09]"
    # Sanity guard: disabling the OU drift must collapse day-to-day variance
    eng2 = _engine(ou_enabled=False)
    out2 = eng2.run_multiday(days=14, step_s=600.0, seed=42)
    hr2 = out2["mean_hr_bpm"]
    daily2 = np.array([hr2[mask & (out2["day_index"] == d)].mean() for d in range(14)])
    assert daily2.std(ddof=1) < daily.std(ddof=1)


def test_menstrual_hook_off_by_default():
    eng = _engine()
    assert eng.time_engine.menstrual_enabled is False
    assert eng.time_engine.menstrual_vagal_factor() == 1.0
    # Explicit opt-in produces the luteal RHR offset (+2-5 bpm, E2)
    eng_on = _engine(menstrual_enabled=True)
    eng_on.time_engine.menstrual_cycle_day = 20.0  # luteal
    assert 2.0 <= eng_on.time_engine._menstrual_rhr_offset_bpm() <= 5.0
    assert eng_on.time_engine.menstrual_vagal_factor() == pytest.approx(0.9)
    eng_on.time_engine.menstrual_cycle_day = 5.0   # follicular
    assert eng_on.time_engine._menstrual_rhr_offset_bpm() == 0.0


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
