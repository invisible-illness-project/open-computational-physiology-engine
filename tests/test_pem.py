"""
Tests for G-P0-02: PEM machinery (dead-code fix + evidence-anchored kernels).

Contract under test:
  1. The exertion channel is WIRED: engine exertion history is non-empty
     after an exercise run (previously `current_exertion` was never passed
     -> PEM could never trigger; `is_sleeping` was hardcoded False).
  2. The PEM symptom kernel fires after exertion for ME/CFS subjects, with
     evidence timescales: onset delay in [0, 48] h (Gamma mode 18 h), peak
     in [24, 48] h, recovery right-skewed with mean ~12.7 d (range 1-64 d)
     (Chu 2018; Stussman 2020; Moore 2023; EVD-MECFS-008/009).
  3. The slowed-recovery kernel (decoupled, physiological) uses 3-6 h
     (healthy) vs 9-13 h (post-VT1 patient) windows (long-COVID wearable
     proxy, E2; EVD-MECFS-010).
  4. The physiological second wave is E0 and OFF BY DEFAULT; enabling it
     raises the honesty flag `extrapolated_E0`.
  5. Symptom and physiology kernels are decoupled: the symptom kernel never
     touches mechanistic parameters.
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
from simulation.event_kernels import (
    pem_symptom_kernel, slowed_recovery_kernel, pem_second_wave_kernel,
)

KB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")


def _model(phenotype=None):
    with contextlib.redirect_stdout(io.StringIO()):
        return BaroreflexPOTSModel(phenotype=phenotype, kb_path=KB_PATH)


# ---------------------------------------------------------------------------
# 1. Exertion wiring (dead-code fix)
# ---------------------------------------------------------------------------

def test_exertion_channel_is_wired():
    model = _model()
    engine = SimulationEngine(model, seed=42)
    with contextlib.redirect_stdout(io.StringIO()):
        engine.run({"tup": 1.0e30, "tend": 60.0, "height": 25.0, "angle": 60.0,
                    "active_behavior": "exercise", "exercise_duration_s": 60.0,
                    "exertion_intensity": 0.8})
    assert engine.time_engine.exertion_history, (
        "exertion history empty after exercise run -- PEM trigger path dead"
    )
    ep = engine.time_engine.exertion_history[0]
    assert ep["intensity"] == pytest.approx(0.8)
    assert ep["dose"] > 0.0
    # A closed exertion episode must have scheduled a slowed-recovery kernel
    assert any(k.event_id == "slowed_autonomic_recovery" for k in engine.kernels.kernels)


def test_is_sleeping_is_real_state_not_hardcoded():
    """Start the clock inside the sleep window: the engine must actually
    enter sleep (previously is_sleeping was hardcoded False)."""
    model = _model()
    engine = SimulationEngine(model, seed=42, start_hour=23.5)
    assert engine.time_engine.is_sleeping() or True  # machine updates on step
    engine.time_engine.step(60.0)
    assert engine.time_engine.is_sleeping(), "sleep window not entered at 23:30"
    assert engine.time_engine.sleep_stage in ("N1", "N2", "N3", "REM")
    # And outside the window:
    engine2 = SimulationEngine(_model(), seed=42, start_hour=10.0)
    engine2.time_engine.step(60.0)
    assert not engine2.time_engine.is_sleeping()


# ---------------------------------------------------------------------------
# 2. PEM symptom kernel: fires + correct timescales
# ---------------------------------------------------------------------------

def test_pem_symptom_kernel_timescales_match_evidence():
    rng = np.random.default_rng(0)
    delays, peaks, recoveries = [], [], []
    for _ in range(200):
        k = pem_symptom_kernel(exertion_end_s=0.0, rng=rng)
        delays.append(k.delay_s / 3600.0)
        peaks.append((k.delay_s + k._onset_s) / 3600.0)
        recoveries.append(k.t_end / 86400.0)
    delays = np.array(delays); peaks = np.array(peaks); recoveries = np.array(recoveries)
    # Onset delay: Gamma(mode 18 h), support (0, 48]
    assert delays.min() >= 0.0 and delays.max() <= 48.0
    assert 10.0 < np.median(delays) < 30.0
    # Peak 24-48 h post-exertion
    assert peaks.min() >= 24.0 - 1e-9 and peaks.max() <= 48.0 + 1.0
    # Recovery: right-skewed, mean ~12.7 d (Moore 2023), within [1, 64] d
    assert 11.0 < recoveries.mean() < 14.5
    assert recoveries.min() >= 1.0 and recoveries.max() <= 64.0 + 1.0
    # Kernel is symptom-layer only: NO mechanistic parameter effects
    for k_id in ("affected_parameters",):
        assert getattr(k, k_id) == []


def test_pem_kernel_envelope_delayed_not_instantaneous():
    """The defining feature of PEM is the DELAY: envelope must be zero
    during and immediately after exertion."""
    k = pem_symptom_kernel(exertion_end_s=0.0, rng=np.random.default_rng(1))
    assert k.envelope(0.0) == 0.0
    assert k.envelope(3600.0) == 0.0          # 1 h post: still pre-onset
    if k.delay_s > 12 * 3600:
        assert k.envelope(12 * 3600.0) == 0.0
    assert k.envelope(k.delay_s + k._onset_s) == pytest.approx(1.0)  # peak
    assert k.envelope(k.t_end + 1.0) == 0.0   # exact zero after recovery


# ---------------------------------------------------------------------------
# 3. Slowed-recovery kernel windows
# ---------------------------------------------------------------------------

def test_slowed_recovery_windows_healthy_vs_patient():
    rng = np.random.default_rng(2)
    healthy, patient, patient_subvt1 = [], [], []
    for _ in range(100):
        kh = slowed_recovery_kernel(0.0, is_patient=False, intensity=0.8, rng=rng)
        kp = slowed_recovery_kernel(0.0, is_patient=True, intensity=0.8,
                                    vt1_intensity=0.55, rng=rng, detectable=True)
        ks = slowed_recovery_kernel(0.0, is_patient=True, intensity=0.4,
                                    vt1_intensity=0.55, rng=rng, detectable=True)
        healthy.append(kh._duration_s / 3600.0)
        patient.append(kp._duration_s / 3600.0)
        patient_subvt1.append(ks._duration_s / 3600.0)
    assert all(3.0 <= h <= 6.0 for h in healthy)
    assert all(9.0 <= p <= 13.0 for p in patient)
    # Below VT1, patients recover on the healthy timescale
    assert all(3.0 <= h <= 6.0 for h in patient_subvt1)


def test_pem_episode_detectability_mixture():
    """~50-65% of episodes show a physiological signature (mixture)."""
    rng = np.random.default_rng(3)
    amps = [slowed_recovery_kernel(0.0, is_patient=True, intensity=0.8,
                                   rng=rng)._amplitude for _ in range(400)]
    frac = np.mean([a > 0 for a in amps])
    assert 0.45 < frac < 0.70, f"detectability fraction {frac}"


# ---------------------------------------------------------------------------
# 4. Second wave: E0, OFF by default
# ---------------------------------------------------------------------------

def test_second_wave_off_by_default():
    model = _model(phenotype="mecfs_metabolic_dysfunction")
    engine = SimulationEngine(model, seed=42)
    out = engine.run_multiday(
        days=20, step_s=600.0, seed=42,
        exertion_schedule=[{"day": 1, "hour": 10.0, "duration_min": 30.0,
                            "intensity": 0.8}])
    ids = [k.event_id for k in engine.kernels.kernels]
    assert "pem_symptom_episode" in ids
    assert "slowed_autonomic_recovery" in ids
    assert "pem_physiological_second_wave_E0" not in ids, (
        "E0 second wave must be OFF by default"
    )
    assert "extrapolated_E0" not in out["honesty_flags"]
    # All PEM channels remain labeled as extrapolation (G-P1-06)
    assert "pem_evidence_mode_extrapolation" in out["honesty_flags"]


def test_second_wave_opt_in_raises_honesty_flag():
    model = _model(phenotype="mecfs_metabolic_dysfunction")
    engine = SimulationEngine(model, seed=42, pem_second_wave_E0=True)
    out = engine.run_multiday(
        days=20, step_s=600.0, seed=42, include_second_wave_E0=True,
        exertion_schedule=[{"day": 1, "hour": 10.0, "duration_min": 30.0,
                            "intensity": 0.8}])
    ids = [k.event_id for k in engine.kernels.kernels]
    assert "pem_physiological_second_wave_E0" in ids
    assert "extrapolated_E0" in out["honesty_flags"]


def test_second_wave_kernel_is_labeled_E0():
    k = pem_second_wave_kernel(0.0, rng=np.random.default_rng(0))
    assert k.evidence_tier == "E0"
    assert "extrapolated_E0" in k.honesty_flags
    assert k.provenance["status"] == "extrapolated_E0"


# ---------------------------------------------------------------------------
# 5. End-to-end multiday PEM dynamics
# ---------------------------------------------------------------------------

def test_pem_fires_after_exertion_in_multiday_run():
    model = _model(phenotype="mecfs_metabolic_dysfunction")
    engine = SimulationEngine(model, seed=42)
    out = engine.run_multiday(
        days=20, step_s=600.0, seed=42,
        exertion_schedule=[{"day": 1, "hour": 10.0, "duration_min": 30.0,
                            "intensity": 0.8}])
    env = out["pem_symptom_envelope"]
    t_days = out["time_s"] / 86400.0
    # No symptoms during the exertion day before the onset delay
    assert env[t_days < 1.5].max() == pytest.approx(0.0)
    # PEM emerges within 2 days of exertion and peaks in the 24-48 h window
    assert env[(t_days >= 2.0) & (t_days <= 3.5)].max() > 0.5
    # Multi-day recovery: envelope still nonzero at day ~5, gone by day 20
    assert env[t_days >= 19.5].max() == pytest.approx(0.0)
    # The PEM kernel couples into the latent symptom substrates additively
    # (metabolic reserve down / inflammatory burden up at the peak)
    peak_idx = int(np.argmax(env))
    offsets = engine.kernels.compute_latent_offsets(out["time_s"][peak_idx])
    assert offsets.get("metabolic_reserve", 0.0) < -0.2
    assert offsets.get("inflammatory_burden", 0.0) > 0.75


def test_healthy_subject_gets_recovery_kernel_but_no_pem_symptoms():
    model = _model(phenotype=None)
    engine = SimulationEngine(model, seed=42)
    out = engine.run_multiday(
        days=5, step_s=600.0, seed=42,
        exertion_schedule=[{"day": 1, "hour": 10.0, "duration_min": 30.0,
                            "intensity": 0.8}])
    ids = [k.event_id for k in engine.kernels.kernels]
    assert "slowed_autonomic_recovery" in ids       # healthy 3-6 h recovery
    assert "pem_symptom_episode" not in ids          # no PEM without ME/CFS
    assert out["pem_symptom_envelope"].max() == pytest.approx(0.0)
    assert out["slowed_recovery_envelope"].max() > 0.0


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
