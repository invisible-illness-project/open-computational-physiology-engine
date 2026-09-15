"""
Regression tests for G-P0-01 (behavior-parameter compounding) and the
EventKernel machinery.

Defect (verified): engine.py used to recompute behavior modifiers from
``model.params`` every heartbeat, so multiplicative perturbations compounded
per beat -- 5 beats of ``meal`` drove RalpM 17.88 -> 4.24 instead of the
one-shot 13.41, and exercise ``Es x1.30``/beat was unbounded.

Contract under test:
  1. Kernels apply against an immutable baseline, never against
     already-modified parameters: NO compounding drift across beats.
  2. Plateau values equal the one-shot perturbation exactly
     (meal: RalpM == 17.88 * 0.75 == 13.41).
  3. After recovery, parameters return EXACTLY to baseline.
  4. Exercise Es is bounded by the kernel plateau (x1.30), forever.
  5. Kernels compose against baseline (multiplicative-in-effect-space).
  6. Engine-level: a full ODE run with an active behavior leaves
     model.params bit-identical to its pre-run values.
"""
import os
import sys
import copy
import io
import contextlib

import numpy as np
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.baroreflex_model import BaroreflexPOTSModel
from simulation.engine import SimulationEngine
from simulation.event_kernels import (
    EventKernelManager, make_meal_kernel, make_exercise_kernel,
)

KB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")

# KB nominals (knowledge_base/equations/mathematical_models.yaml)
RALPM_NOMINAL = 17.88
ES_NOMINAL = 3.0
MEAL_ONE_SHOT_RALPM = 13.41  # 17.88 * 0.75 (documented G-P0-01 regression target)


def _baseline():
    with contextlib.redirect_stdout(io.StringIO()):
        model = BaroreflexPOTSModel(kb_path=KB_PATH)
    return copy.deepcopy(model.params)


# ---------------------------------------------------------------------------
# 1-3. No compounding, exact plateau, exact return to baseline
# ---------------------------------------------------------------------------

def test_meal_kernel_no_compounding_drift():
    """Applying the meal overlay every 'beat' for a full day must produce a
    constant plateau -- the pre-fix bug multiplied x0.75 per beat."""
    base = _baseline()
    mgr = EventKernelManager()
    mgr.add_kernel(make_meal_kernel(start_s=0.0))
    plateau_t = 45.0 * 60.0  # inside the 30-90 min plateau window
    plateau_vals = []
    for beat in range(200):  # 200 consecutive applications at plateau
        eff = mgr.compute_parameter_overlay(base, plateau_t + beat * 0.8)
        plateau_vals.append(eff["RalpM"])
    plateau_vals = np.array(plateau_vals)
    assert np.all(plateau_vals == plateau_vals[0]), "plateau drifts across beats"
    assert plateau_vals[0] == pytest.approx(MEAL_ONE_SHOT_RALPM, rel=1e-12), (
        f"plateau RalpM {plateau_vals[0]} != one-shot {MEAL_ONE_SHOT_RALPM}"
    )
    # The pre-fix failure mode would have given 17.88 * 0.75**200 ~ 0
    assert plateau_vals[-1] > 13.0


def test_meal_kernel_exact_return_to_baseline_after_recovery():
    base = _baseline()
    mgr = EventKernelManager()
    k = mgr.add_kernel(make_meal_kernel(start_s=1000.0))
    # Before trigger: exactly baseline
    eff = mgr.compute_parameter_overlay(base, 999.0)
    assert eff["RalpM"] == base["RalpM"]
    # After full recovery (default: trigger + 30 + 60 + 90 min): EXACT baseline
    eff = mgr.compute_parameter_overlay(base, k.t_end + 1.0)
    for sym in ("RalpM", "Ralpm", "Cal"):
        assert eff[sym] == base[sym], f"{sym} did not return exactly to baseline"


def test_exercise_kernel_es_bounded():
    """Pre-fix, Es grew x1.30 per heartbeat without bound.  The kernel
    plateau must keep it at exactly 1.30 x baseline indefinitely."""
    base = _baseline()
    mgr = EventKernelManager()
    mgr.add_kernel(make_exercise_kernel(start_s=0.0, duration_s=3600.0))
    for beat in range(500):
        eff = mgr.compute_parameter_overlay(base, 60.0 + beat * 1.0)
        assert eff["Es"] == pytest.approx(ES_NOMINAL * 1.30, rel=1e-12)
    # And after recovery: exact baseline
    k = mgr.kernels[0]
    eff = mgr.compute_parameter_overlay(base, k.t_end + 1.0)
    assert eff["Es"] == ES_NOMINAL


def test_kernels_compose_against_baseline_not_modified_params():
    """Two simultaneous kernels touching the same parameter compose
    multiplicatively against BASELINE: eff = base * (1+env1*(m1-1)) *
    (1+env2*(m2-1)) -- never against an already-perturbed intermediate."""
    base = _baseline()
    mgr = EventKernelManager()
    mgr.add_kernel(make_meal_kernel(start_s=0.0))           # RalpM x0.75
    mgr.add_kernel(make_meal_kernel(start_s=0.0))           # RalpM x0.75 again
    t = 45.0 * 60.0  # both at plateau
    eff = mgr.compute_parameter_overlay(base, t)
    assert eff["RalpM"] == pytest.approx(RALPM_NOMINAL * 0.75 * 0.75, rel=1e-12)
    # Sanity: NOT compounding-across-time -- same value 1000 beats later
    eff2 = mgr.compute_parameter_overlay(base, t + 800.0)
    assert eff2["RalpM"] == eff["RalpM"]


def test_envelope_is_causal_and_bounded():
    mgr = EventKernelManager()
    k = mgr.add_kernel(make_exercise_kernel(start_s=100.0, duration_s=50.0))
    assert k.envelope(99.999) == 0.0           # causal: nothing before trigger
    assert 0.0 <= k.envelope(100.0) <= 1.0
    assert k.envelope(140.0) == pytest.approx(1.0)   # plateau (onset 30 s)
    assert k.envelope(k.t_end) == 0.0          # exact zero at end of recovery
    assert k.envelope(k.t_end + 10.0) == 0.0


# ---------------------------------------------------------------------------
# 6. Engine-level regression: behavior runs leave model.params untouched
# ---------------------------------------------------------------------------

def _run_engine_with_behavior(behavior, **tilt_overrides):
    with contextlib.redirect_stdout(io.StringIO()):
        model = BaroreflexPOTSModel(kb_path=KB_PATH)
        pre = copy.deepcopy(model.params)
        engine = SimulationEngine(model, seed=42)
        tilt = {"tup": 1.0e30, "tend": 120.0, "height": 25.0, "angle": 60.0,
                "active_behavior": behavior,
                "kernel_time_scale": 0.01,   # compress meal kernel to seconds
                "exercise_duration_s": 40.0}
        tilt.update(tilt_overrides)
        res = engine.run(tilt)
    return model, pre, res


def test_engine_meal_run_returns_params_to_baseline():
    model, pre, res = _run_engine_with_behavior("meal")
    assert set(model.params) == set(pre)
    for key, val in pre.items():
        assert np.isclose(model.params[key], val, rtol=1e-12, atol=1e-12), (
            f"post-run param '{key}' differs from pre-run: {val} -> {model.params[key]}"
        )


def test_engine_exercise_es_bounded_and_restored():
    """Mid-run, the applied Es must never exceed 1.30 x baseline; post-run,
    model.params must be bit-identical to pre-run (G-P0-01)."""
    with contextlib.redirect_stdout(io.StringIO()):
        model = BaroreflexPOTSModel(kb_path=KB_PATH)
        pre = copy.deepcopy(model.params)
        engine = SimulationEngine(model, seed=42)
        # Instrument: record applied Es each beat by wrapping the behavior
        applied_es = []
        orig = engine.behavior.modulate_parameters
        def spy(base, latent, time_s=None):
            eff = orig(base, latent, time_s=time_s)
            applied_es.append(eff["Es"])
            return eff
        engine.behavior.modulate_parameters = spy
        res = engine.run({"tup": 1.0e30, "tend": 120.0, "height": 25.0,
                          "angle": 60.0, "active_behavior": "exercise",
                          "exercise_duration_s": 60.0})
    applied_es = np.array(applied_es)
    assert applied_es.max() <= pre["Es"] * 1.30 * (1 + 1e-12), (
        f"Es exceeded kernel plateau: {applied_es.max()} vs {pre['Es'] * 1.30}"
    )
    assert applied_es.max() == pytest.approx(pre["Es"] * 1.30, rel=1e-6)
    for key, val in pre.items():
        assert np.isclose(model.params[key], val, rtol=1e-12, atol=1e-12), key


def test_engine_plateau_matches_one_shot_value():
    """During the (compressed) meal plateau, the APPLIED RalpM inside the
    engine must equal the documented one-shot 13.41 within tolerance."""
    with contextlib.redirect_stdout(io.StringIO()):
        model = BaroreflexPOTSModel(kb_path=KB_PATH)
        engine = SimulationEngine(model, seed=42)
        applied = []
        orig = engine.behavior.modulate_parameters
        def spy(base, latent, time_s=None):
            eff = orig(base, latent, time_s=time_s)
            applied.append((time_s, eff["RalpM"]))
            return eff
        engine.behavior.modulate_parameters = spy
        engine.run({"tup": 1.0e30, "tend": 90.0, "height": 25.0, "angle": 60.0,
                    "active_behavior": "meal", "kernel_time_scale": 0.01})
    plateau = [v for (t, v) in applied if t is not None and 25.0 <= t <= 50.0]
    assert plateau, "no samples in compressed plateau window"
    assert np.mean(plateau) == pytest.approx(MEAL_ONE_SHOT_RALPM, rel=1e-3)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
