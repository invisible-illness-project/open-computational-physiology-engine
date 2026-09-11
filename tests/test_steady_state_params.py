"""
Regression tests for the initialize_steady_state() parameter-wipe fix.

Defect (Phase 0 audit §4.1): initialize_steady_state() used to recompute and
overwrite most KB/disease/subject-derived parameters (compliances, venous
capacity, resistances, Hill coefficients, time constants, HR bounds) after
they were applied, rendering several disease phenotypes computationally inert.

Contract under test:
  1. initialize_steady_state() may ONLY compute the 10 integrator initial
     conditions (model.initial_state). It must never modify model.params.
  2. Every disease phenotype registered in knowledge_base/diseases/ must
     produce a measurably different tilt-test response vs healthy baseline.
  3. The healthy-control tilt response must not be worse than the documented
     pre-fix behavior (known failure: ~76 bpm HR rise; missing muscle pump is
     a separate workstream).
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
from simulation.perturbations import PerturbationManager
from simulation.population import VirtualSubject

KB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")

# Short smoke tilt protocol: 40 s supine settle, 14 s transition, 36 s at 60 deg.
TILT_PARAMS = {"tup": 40.0, "tend": 90.0, "height": 25.0, "angle": 60.0}

# Documented pre-fix healthy-control HR rise (full protocol, see
# docs/validation_strategy.md). The fix must not make the healthy
# control response worse than this known-failure benchmark.
HEALTHY_KNOWN_HR_RISE_BPM = 76.1

# Numerical-noise floor for observables (Radau rtol=1e-6; seeded HRV noise).
HR_NOISE_FLOOR_BPM = 1.0
MAP_NOISE_FLOOR_MMHG = 0.5


def _all_phenotype_ids():
    """Dynamically enumerate every phenotype registered in knowledge_base/diseases/."""
    pm = PerturbationManager(kb_path=KB_PATH)
    ids = sorted(pm.phenotypes.keys())
    assert ids, "No disease phenotypes discovered in knowledge_base/diseases/"
    return ids


PHENOTYPES = _all_phenotype_ids()


def _load_params_only(phenotype=None, subject=None):
    """Build a model and run ONLY load_parameters(), bypassing __init__ so the
    pre-initialization parameter dict can be captured."""
    model = BaroreflexPOTSModel.__new__(BaroreflexPOTSModel)
    model.phenotype = phenotype
    model.subject = subject
    model.kb_path = KB_PATH
    model.params = {}
    model.initial_state = []
    with contextlib.redirect_stdout(io.StringIO()):
        model.load_parameters()
    return model


# ---------------------------------------------------------------------------
# 1. Parameter preservation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phenotype", [None] + PHENOTYPES)
def test_initialize_steady_state_never_overwrites_parameters(phenotype):
    """KB/disease-derived parameters must be identical before/after
    initialize_steady_state() (SPEC F1 acceptance: compare dict before/after)."""
    model = _load_params_only(phenotype=phenotype)
    params_before = copy.deepcopy(model.params)
    assert params_before, "load_parameters() produced an empty parameter set"

    model.initialize_steady_state()

    assert set(model.params.keys()) == set(params_before.keys()), (
        f"[{phenotype}] initialize_steady_state() added/removed parameters: "
        f"{set(model.params) ^ set(params_before)}"
    )
    for key, before in params_before.items():
        after = model.params[key]
        assert np.isclose(before, after, rtol=1e-12, atol=1e-12), (
            f"[{phenotype}] parameter '{key}' overwritten by "
            f"initialize_steady_state(): {before} -> {after}"
        )


def test_initialize_steady_state_preserves_virtual_subject_priors():
    """Demographic priors (age/sex/BMI/fitness adjustments) must survive init."""
    subject = VirtualSubject(age=45, sex="female", bmi=27.0, fitness="athletic")
    model = _load_params_only(subject=subject)
    params_before = copy.deepcopy(model.params)

    model.initialize_steady_state()

    for key, before in params_before.items():
        assert np.isclose(model.params[key], before, rtol=1e-12, atol=1e-12), (
            f"VirtualSubject prior '{key}' overwritten: {before} -> {model.params[key]}"
        )
    # Spot-check that priors actually moved away from KB nominals (otherwise
    # this test would be vacuous).
    assert not np.isclose(params_before["HM"], model.kb_nominal_params["HM"])
    assert not np.isclose(params_before["TotalVol"], model.kb_nominal_params["TotalVol"])


@pytest.mark.parametrize("phenotype", [None] + PHENOTYPES)
def test_initial_state_is_consistent_dynamic_state(phenotype):
    """Initial conditions must be finite, physically ordered, and consistent
    with the (sacred) parameter set: controller states start on their Hill
    targets so each control loop begins at dX/dt = 0."""
    model = _load_params_only(phenotype=phenotype)
    model.initialize_steady_state()

    y0 = model.initial_state
    assert len(y0) == 10, "expected 10 integrator initial conditions"
    assert np.all(np.isfinite(y0)), f"[{phenotype}] non-finite initial state: {y0}"

    Vau, Vvu, Val, Vvl, Vlv, pcm, Raup, Ralp, Ed, Hc = y0
    p = model.params

    # Positivity and capacity constraints
    assert min(Vau, Vvu, Val, Vvl, Vlv) > 0.0
    assert Vvl < p["VMvl"], "lower venous volume exceeds venous capacity"
    # Controller states lie strictly inside their Hill operating ranges
    assert p["Raupm"] < Raup < p["RaupM"]
    assert p["Ralpm"] < Ralp < p["RalpM"]
    assert p["Edm"] < Ed < p["EdM"]
    assert p["Hm"] < Hc < p["HM"]

    # Exact steady-state consistency of the heart-rate control loop at the
    # chosen operating point: Hc0 must equal the Hill target H_f(pcm0).
    kH = p["kH"]
    Hf = (p["HM"] - p["Hm"]) * (p["p2H"] ** kH) / (pcm ** kH + p["p2H"] ** kH) + p["Hm"]
    assert np.isclose(Hc, Hf, rtol=1e-9), (
        f"[{phenotype}] Hc0={Hc} is not the steady-state Hill target {Hf} at pcm0={pcm}"
    )


# ---------------------------------------------------------------------------
# 2. Phenotype differentiation in tilt-test observables
# ---------------------------------------------------------------------------

_RUN_CACHE = {}


def _run_short_tilt(phenotype):
    """Run a short seeded tilt simulation and extract key observables."""
    if phenotype in _RUN_CACHE:
        return _RUN_CACHE[phenotype]

    np.random.seed(42)  # deterministic HRV noise for reproducible assertions
    with contextlib.redirect_stdout(io.StringIO()):
        model = BaroreflexPOTSModel(phenotype=phenotype, kb_path=KB_PATH)
        engine = SimulationEngine(model)
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
    assert np.all(np.isfinite(hr)), f"[{phenotype}] non-finite HR series"
    _RUN_CACHE[phenotype] = obs
    return obs


def test_healthy_control_not_worse_than_known_baseline():
    """The fix must not degrade the healthy-control tilt response beyond the
    documented pre-fix known failure (~76.1 bpm rise; missing muscle pump is
    a separate workstream)."""
    healthy = _run_short_tilt(None)
    assert healthy["delta_hr"] > 0.0
    assert healthy["delta_hr"] <= HEALTHY_KNOWN_HR_RISE_BPM + 2.0, (
        f"Healthy-control HR rise {healthy['delta_hr']:.1f} bpm is worse than the "
        f"documented pre-fix failure ({HEALTHY_KNOWN_HR_RISE_BPM} bpm)"
    )


@pytest.mark.parametrize("phenotype", PHENOTYPES)
def test_phenotype_produces_distinct_tilt_response(phenotype):
    """Each disease phenotype must differ from healthy baseline in at least one
    key observable beyond numerical noise (SPEC F1 acceptance)."""
    healthy = _run_short_tilt(None)
    obs = _run_short_tilt(phenotype)

    d_delta_hr = abs(obs["delta_hr"] - healthy["delta_hr"])
    d_supine_hr = abs(obs["hr_supine"] - healthy["hr_supine"])
    d_map = abs(obs["map_tilt"] - healthy["map_tilt"])

    print(
        f"\n[{phenotype}] vs healthy: "
        f"supineHR {obs['hr_supine']:.1f} vs {healthy['hr_supine']:.1f} bpm | "
        f"dHR {obs['delta_hr']:.1f} vs {healthy['delta_hr']:.1f} bpm | "
        f"tiltMAP {obs['map_tilt']:.1f} vs {healthy['map_tilt']:.1f} mmHg"
    )

    assert (
        d_delta_hr > HR_NOISE_FLOOR_BPM
        or d_supine_hr > HR_NOISE_FLOOR_BPM
        or d_map > MAP_NOISE_FLOOR_MMHG
    ), (
        f"Phenotype '{phenotype}' is computationally inert: "
        f"|delta(dHR)|={d_delta_hr:.3f} bpm, |delta(supineHR)|={d_supine_hr:.3f} bpm, "
        f"|delta(tiltMAP)|={d_map:.3f} mmHg vs healthy baseline"
    )


def test_phenotypes_are_pairwise_distinct():
    """Phenotypes should not collapse onto a single shared response: each pair
    must differ in at least one key observable (guards against a 'fix' that
    merely shifts everyone identically)."""
    observables = {ph: _run_short_tilt(ph) for ph in PHENOTYPES}
    for i, ph_a in enumerate(PHENOTYPES):
        for ph_b in PHENOTYPES[i + 1:]:
            a, b = observables[ph_a], observables[ph_b]
            distinct = (
                abs(a["delta_hr"] - b["delta_hr"]) > HR_NOISE_FLOOR_BPM
                or abs(a["hr_supine"] - b["hr_supine"]) > HR_NOISE_FLOOR_BPM
                or abs(a["map_tilt"] - b["map_tilt"]) > MAP_NOISE_FLOOR_MMHG
            )
            assert distinct, (
                f"Phenotypes '{ph_a}' and '{ph_b}' produce indistinguishable "
                f"tilt responses: {a} vs {b}"
            )


if __name__ == "__main__":
    # Convenience: print the quantified phenotype table when run directly.
    healthy = _run_short_tilt(None)
    print(f"{'phenotype':>32} | supineHR | peakHR |  dHR  | tiltMAP")
    print(f"{'healthy_control':>32} | {healthy['hr_supine']:8.1f} | {healthy['hr_peak']:6.1f} | "
          f"{healthy['delta_hr']:5.1f} | {healthy['map_tilt']:7.1f}")
    for ph in PHENOTYPES:
        o = _run_short_tilt(ph)
        print(f"{ph:>32} | {o['hr_supine']:8.1f} | {o['hr_peak']:6.1f} | "
              f"{o['delta_hr']:5.1f} | {o['map_tilt']:7.1f}")
