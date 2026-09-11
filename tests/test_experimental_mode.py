"""
Tests for EXPERIMENTAL perturbation mode (engine honesty mode).

Canonical mode (default) applies ONLY adversarially reviewed
`parameters_perturbed` blocks. Phenotypes whose entire effect lives in
`unverified_parameters` (tier-D, machine-proposed, UNRESOLVED review status)
are therefore intentionally inert in canonical mode. Experimental mode
(include_experimental=True / enable_experimental_mode) additionally applies
those unverified values and marks the provenance accordingly.

Contract under test:
  1. Provenance metadata distinguishes canonical vs experimental parameters.
  2. Experimental-only phenotypes (autoimmune_neuropathy, beta_blocker,
     heds_venous_pooling, sleep_deprivation) produce healthy-identical results
     by default but measurably distinct tilt responses in experimental mode.
  3. Canonical-active phenotypes keep working in experimental mode.
  4. Experimental mode still never mutates parameters during
     initialize_steady_state().
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
from simulation.perturbations import PerturbationManager, enable_experimental_mode

KB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")

TILT_PARAMS = {"tup": 40.0, "tend": 90.0, "height": 25.0, "angle": 60.0}
HR_NOISE_FLOOR_BPM = 1.0
MAP_NOISE_FLOOR_MMHG = 0.5

_PM = PerturbationManager(kb_path=KB_PATH)
CANONICAL_ACTIVE = sorted(pid for pid, ph in _PM.phenotypes.items() if ph["parameters_perturbed"])
EXPERIMENTAL_ONLY = sorted(
    pid for pid, ph in _PM.phenotypes.items()
    if not ph["parameters_perturbed"] and ph["unverified_parameters"]
)
assert EXPERIMENTAL_ONLY, "expected at least one experimental-only phenotype in the KB"


# ---------------------------------------------------------------------------
# 1. Provenance metadata
# ---------------------------------------------------------------------------

def test_canonical_mode_provenance_has_no_experimental_parameters():
    pm = PerturbationManager(kb_path=KB_PATH)  # default: canonical
    base = {"Hm": 0.3, "kE": 7.0, "Cal": 0.3726, "VMvl": 195.075}
    params, applied = pm.apply_perturbations(base, "heds_venous_pooling")
    assert applied == ["heds_venous_pooling"]
    # Canonical mode: nothing applied for an experimental-only phenotype
    assert params == base
    assert pm.last_application["mode"] == "canonical"
    prov = pm.last_application["phenotypes"]["heds_venous_pooling"]
    assert prov["canonical"] == {}
    assert prov["experimental"] == {}


@pytest.mark.parametrize("phenotype", EXPERIMENTAL_ONLY)
def test_experimental_mode_applies_and_labels_unverified_parameters(phenotype):
    pm = PerturbationManager(kb_path=KB_PATH, include_experimental=True)
    base = dict(_PM_BASE)
    params, applied = pm.apply_perturbations(base, phenotype)

    assert pm.last_application["mode"] == "EXPERIMENTAL"
    prov = pm.last_application["phenotypes"][phenotype]
    assert prov["experimental"], f"[{phenotype}] no experimental parameters recorded"
    # Every unverified symbol was applied and labeled experimental
    expected_symbols = {p["symbol"] for p in _PM.phenotypes[phenotype]["unverified_parameters"]}
    assert set(prov["experimental"].keys()) == expected_symbols
    for sym in expected_symbols:
        assert params[sym] != base[sym], f"[{phenotype}] experimental param {sym} not applied"
        assert np.isclose(prov["experimental"][sym], params[sym])


def test_experimental_flag_defaults_to_instance_default_and_per_call_override():
    pm = PerturbationManager(kb_path=KB_PATH)  # canonical by default
    base = dict(_PM_BASE)
    params_default, _ = pm.apply_perturbations(base, "heds_venous_pooling")
    assert params_default == base
    # Per-call override flips to experimental
    params_exp, _ = pm.apply_perturbations(base, "heds_venous_pooling", include_experimental=True)
    assert params_exp != base
    assert pm.last_application["mode"] == "EXPERIMENTAL"


def test_enable_experimental_mode_attaches_provenance_to_model():
    with contextlib.redirect_stdout(io.StringIO()):
        model = BaroreflexPOTSModel(phenotype="beta_blocker", kb_path=KB_PATH)
        assert not hasattr(model, "perturbation_provenance")  # canonical load: unmarked
        enable_experimental_mode(model)
    prov = model.perturbation_provenance
    assert prov["mode"] == "EXPERIMENTAL"
    assert set(prov["phenotypes"]["beta_blocker"]["experimental"].keys()) == {"HM", "kH"}


def test_experimental_mode_preserves_params_during_steady_state_init():
    """The F1 contract must hold in experimental mode too: enabling it re-runs
    initialize_steady_state(), which must not mutate the (now experimental)
    parameter set."""
    with contextlib.redirect_stdout(io.StringIO()):
        model = BaroreflexPOTSModel(phenotype="sleep_deprivation", kb_path=KB_PATH)
        enable_experimental_mode(model)
    before = copy.deepcopy(model.params)
    model.initialize_steady_state()
    assert set(model.params) == set(before)
    for key, val in before.items():
        assert np.isclose(model.params[key], val, rtol=1e-12, atol=1e-12), key


# ---------------------------------------------------------------------------
# 2. Tilt-response observables in experimental mode
# ---------------------------------------------------------------------------

_RUN_CACHE = {}


def _run_short_tilt(phenotype, experimental):
    key = (phenotype, experimental)
    if key in _RUN_CACHE:
        return _RUN_CACHE[key]

    with contextlib.redirect_stdout(io.StringIO()):
        model = BaroreflexPOTSModel(phenotype=phenotype, kb_path=KB_PATH)
        if experimental:
            enable_experimental_mode(model)
        engine = SimulationEngine(model, seed=42)
        res = engine.run(TILT_PARAMS)

    t = res["time"]
    hr = res["Hc"] * 60.0
    supine = (t >= TILT_PARAMS["tup"] - 10.0) & (t < TILT_PARAMS["tup"])
    upright = t >= TILT_PARAMS["tup"] + 14.0

    obs = {
        "hr_supine": float(hr[supine].mean()),
        "hr_peak": float(hr[upright].max()),
        "delta_hr": float(hr[upright].max() - hr[supine].mean()),
        "map_tilt": float(res["pau"][upright].mean()),
    }
    assert np.all(np.isfinite(hr))
    _RUN_CACHE[key] = obs
    return obs


@pytest.mark.parametrize("phenotype", EXPERIMENTAL_ONLY)
def test_experimental_only_phenotype_differs_in_experimental_mode(phenotype):
    """The phenotype that is inert in canonical mode must produce a measurable
    tilt-response difference once its unverified parameters are applied."""
    healthy = _run_short_tilt(None, experimental=False)
    obs = _run_short_tilt(phenotype, experimental=True)

    d_delta_hr = abs(obs["delta_hr"] - healthy["delta_hr"])
    d_supine_hr = abs(obs["hr_supine"] - healthy["hr_supine"])
    d_map = abs(obs["map_tilt"] - healthy["map_tilt"])

    print(
        f"\n[{phenotype}] EXPERIMENTAL vs healthy: "
        f"supineHR {obs['hr_supine']:.1f} vs {healthy['hr_supine']:.1f} bpm | "
        f"dHR {obs['delta_hr']:.1f} vs {healthy['delta_hr']:.1f} bpm | "
        f"tiltMAP {obs['map_tilt']:.1f} vs {healthy['map_tilt']:.1f} mmHg"
    )

    assert (
        d_delta_hr > HR_NOISE_FLOOR_BPM
        or d_supine_hr > HR_NOISE_FLOOR_BPM
        or d_map > MAP_NOISE_FLOOR_MMHG
    ), (
        f"Phenotype '{phenotype}' remains inert even in EXPERIMENTAL mode: "
        f"|delta(dHR)|={d_delta_hr:.3f}, |delta(supineHR)|={d_supine_hr:.3f}, "
        f"|delta(tiltMAP)|={d_map:.3f}"
    )


@pytest.mark.parametrize("phenotype", CANONICAL_ACTIVE)
def test_canonical_phenotype_still_active_in_experimental_mode(phenotype):
    """Canonical perturbations must remain effective when experimental mode is
    on (experimental mode is additive, not a replacement)."""
    healthy = _run_short_tilt(None, experimental=False)
    obs = _run_short_tilt(phenotype, experimental=True)

    d_delta_hr = abs(obs["delta_hr"] - healthy["delta_hr"])
    d_supine_hr = abs(obs["hr_supine"] - healthy["hr_supine"])
    d_map = abs(obs["map_tilt"] - healthy["map_tilt"])
    assert (
        d_delta_hr > HR_NOISE_FLOOR_BPM
        or d_supine_hr > HR_NOISE_FLOOR_BPM
        or d_map > MAP_NOISE_FLOOR_MMHG
    ), f"Canonical phenotype '{phenotype}' lost its effect in experimental mode"


def test_seeded_runs_are_reproducible():
    """The engine seed must make runs bit-reproducible."""
    a = _run_short_tilt("heds_venous_pooling", experimental=True)
    _RUN_CACHE.pop(("heds_venous_pooling", True), None)
    b = _run_short_tilt("heds_venous_pooling", experimental=True)
    assert a == b


# Shared canonical-baseline parameter values for metadata tests (KB nominals).
_PM_BASE = {
    "HM": 3.3333, "kH": 25.0, "kR": 25.0, "Hm": 0.3, "kE": 7.0,
    "Cal": 0.3726, "VMvl": 195.075,
}
