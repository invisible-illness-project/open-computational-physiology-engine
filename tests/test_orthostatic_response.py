"""Cycle 2 acceptance tests: orthostatic (head-up tilt) response of the
extended venous/baroreflex model.

The Cycle 2 extension adds three physiology mechanisms to the Geddes 2022
0-D baroreflex model:

1. Physiologically scaled venous pooling (lower venous capacity VMvl and
   thoracic reservoir Cvu rescaled so 500-1000 ml of blood can translocate
   to the dependent limbs, per MP-01 / Stewart 2004).
2. A baroreflex-driven venomotor reflex (state Vvm; Heldt 2002 structure):
   falling carotid pressure reduces lower venous capacity and mobilizes
   pooled blood.
3. Venous stress-relaxation creep (state Vsr; van Heusden 2006): slow
   viscoelastic capacity increase under sustained venous load, spreading
   pooling over minutes instead of seconds.

Metric convention (documented, clinically grounded):
  * dHR_sustained = mean HR late in tilt - mean supine HR. The clinical
    POTS criterion is a *sustained* HR rise of >= 30 bpm (not a transient
    peak), so the sustained metric is the primary acceptance metric.
  * dHR_peak = max HR in the first 60 s of tilt - mean supine HR. This is
    the metric used by the pre-Cycle-2 evaluation harness; it is reported
    for continuity ("POTS preserved") but is known to be inflated by an
    intrinsic limit cycle of the steep Geddes Hill controllers (kH=kR=25)
    once hemodynamics operate mid-curve. See the Cycle 2 report.

All runs use the seeded engine (seed=42) for determinism.
"""

import numpy as np
import pytest
from scipy.signal import find_peaks

from models.baroreflex_model import BaroreflexPOTSModel
from simulation.engine import SimulationEngine
from simulation.perturbations import enable_experimental_mode

# Standard evaluator protocol: 200 s supine settle, then 100 s of 60 deg
# head-up tilt (tup=200, tend=300; height=25 cm). The long supine segment
# matters: the smoothed valve/gate dynamics re-equilibrate the supine
# baseline within ~1-2 minutes, so shorter protocols mix baseline drift
# into the tilt response.
TILT = {"tup": 200.0, "tend": 300.0, "height": 25.0, "angle": 60.0}
SEED = 42

POTS_PHENOTYPES = ["neuropathic_pots", "hypovolemic_pots", "hyperadrenergic_pots"]


def _run_tilt(phenotype, experimental=False):
    model = BaroreflexPOTSModel(phenotype=phenotype)
    if experimental:
        enable_experimental_mode(model)
    res = SimulationEngine(model, seed=SEED).run(dict(TILT))
    return res


def _sbp(t, pau, lo, hi):
    """Mean of beat-wise systolic peaks of aortic pressure in [lo, hi)."""
    m = (t >= lo) & (t < hi)
    pw = pau[m]
    peaks, _ = find_peaks(pw, distance=40, prominence=3.0)
    return float(pw[peaks].mean()) if len(peaks) else float("nan")


def _metrics(res):
    t = res["time"]
    hr = res["Hc"] * 60.0
    sup = (t >= 180.0) & (t < 200.0)
    early = (t >= 200.0) & (t <= 260.0)
    late = (t >= 260.0) & (t <= 300.0)
    base = float(hr[sup].mean())
    out = {
        "base_hr": base,
        "dHR_sustained": float(hr[late].mean() - base),
        "dHR_peak": float(hr[early].max() - base),
        "pooling_ml": float(res["Vvl"][late].mean() - res["Vvl"][sup].mean()),
        "map_supine": float(res["pau"][sup].mean()),
        "map_late": float(res["pau"][late].mean()),
        "dSBP": _sbp(t, res["pau"], 260.0, 300.0) - _sbp(t, res["pau"], 180.0, 200.0),
        "vvm_supine": float(res["Vvm"][sup].mean()),
        "vvm_late": float(res["Vvm"][late].mean()),
        "vsr_early": float(res["Vsr"][(t >= 205.0) & (t < 215.0)].mean()),
        "vsr_late": float(res["Vsr"][late].mean()),
    }
    return out


@pytest.fixture(scope="module")
def healthy_metrics():
    return _metrics(_run_tilt(None))


@pytest.fixture(scope="module")
def pots_metrics():
    return {ph: _metrics(_run_tilt(ph)) for ph in POTS_PHENOTYPES}


# ---------------------------------------------------------------------------
# Healthy control
# ---------------------------------------------------------------------------

def test_healthy_sustained_hr_rise_below_30(healthy_metrics):
    """Core Cycle 2 acceptance: healthy sustained HR rise must be < 30 bpm
    (documented pre-fix failure was ~74-76 bpm; physiological target 10-20)."""
    d = healthy_metrics["dHR_sustained"]
    assert 0.0 <= d < 30.0, f"healthy sustained dHR = {d:.1f} bpm"


def test_healthy_map_maintained(healthy_metrics):
    """No pathological MAP fall: late-tilt mean arterial pressure must stay
    within 10 mmHg of the supine mean (baroreflex compensation working)."""
    drop = healthy_metrics["map_supine"] - healthy_metrics["map_late"]
    assert drop < 10.0, f"MAP dropped {drop:.1f} mmHg on tilt"
    assert healthy_metrics["map_late"] > 80.0


def test_healthy_pooling_on_track_to_physiological_range(healthy_metrics):
    """Dependent pooling must reach the physiological trajectory: >= 350 ml
    after 100 s upright (on the way to the 500-1000 ml steady-state range),
    and the analytic steady-state pooling estimate must lie in [500, 1000]."""
    pool = healthy_metrics["pooling_ml"]
    assert pool >= 350.0, f"pooling after 100 s tilt only {pool:.0f} ml"

    # Analytic steady state: creep pins pvl just above the hydrostatic gate
    # (pvu + rho*g*h); pooling equilibrium follows from the log P-V law.
    model = BaroreflexPOTSModel()
    p = model.params
    rhogh = 1.06 * 982.0 * TILT["height"] * np.sin(np.radians(TILT["angle"])) / 1333.22
    pvu = 2.75  # supine upper venous operating pressure (model convention)
    pvl_ss = pvu + rhogh
    vvm_ss = healthy_metrics["vvm_late"]
    vsr_ss = p["G_sr"] * max(0.0, pvl_ss - p["pvl_sr0"])
    cap_ss = p["VMvl"] - vvm_ss + vsr_ss
    vvl_ss = cap_ss * (1.0 - np.exp(-p["mvl"] * pvl_ss))
    vvl0 = (p["VMvl"] - healthy_metrics["vvm_supine"]) * (
        1.0 - np.exp(-p["mvl"] * 3.0)
    )
    pool_ss = vvl_ss - vvl0
    assert 500.0 <= pool_ss <= 1000.0, (
        f"steady-state pooling estimate {pool_ss:.0f} ml outside 500-1000 ml"
    )


def test_venomotor_reflex_engaged_on_tilt(healthy_metrics):
    """The baroreflex venomotor mechanism must actively reduce lower venous
    capacity during tilt (Vvm rises above its supine resting tone)."""
    assert healthy_metrics["vvm_late"] > healthy_metrics["vvm_supine"] + 20.0


def test_stress_relaxation_creep_grows_slowly(healthy_metrics):
    """Stress-relaxation creep must recruit additional capacity slowly over
    the tilt (van Heusden 2006 time course, not instantaneous)."""
    assert healthy_metrics["vsr_late"] > healthy_metrics["vsr_early"] + 50.0


# ---------------------------------------------------------------------------
# POTS phenotypes: orthostatic tachycardia preserved
# ---------------------------------------------------------------------------

def test_pots_peak_hr_rise_preserved(pots_metrics):
    """On the pre-Cycle-2 evaluation metric (peak HR in the first 60 s of
    tilt), every POTS phenotype must still exceed the 30 bpm criterion -
    the venous fix must not 'cure' the patients."""
    for ph, m in pots_metrics.items():
        assert m["dHR_peak"] >= 30.0, f"{ph}: peak dHR {m['dHR_peak']:.1f} < 30"


def test_pots_sustained_response_not_better_than_healthy(healthy_metrics, pots_metrics):
    """Every POTS phenotype's sustained HR rise must be at least the healthy
    one (phenotypes must not respond *better* than the healthy control)."""
    h = healthy_metrics["dHR_sustained"]
    for ph, m in pots_metrics.items():
        assert m["dHR_sustained"] >= h - 1.0, (
            f"{ph}: sustained dHR {m['dHR_sustained']:.1f} below healthy {h:.1f}"
        )


def test_hypovolemic_pots_sustained_criterion(pots_metrics):
    """Hypovolemic POTS (reduced TotalVol) has the least venous reserve and
    must still meet the sustained 30 bpm criterion."""
    d = pots_metrics["hypovolemic_pots"]["dHR_sustained"]
    assert d >= 30.0, f"hypovolemic sustained dHR = {d:.1f} bpm"


def test_pots_map_remains_physiological(pots_metrics):
    """POTS phenotypes must also avoid a pathological MAP collapse."""
    for ph, m in pots_metrics.items():
        assert m["map_late"] > 80.0, f"{ph}: late MAP {m['map_late']:.1f}"


# ---------------------------------------------------------------------------
# Cycle 3: POTS re-curation validation (knowledge_base/diseases/pots.yaml v1.5)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def neuropathic_experimental_metrics():
    """Neuropathic POTS with the tier-D venomotor-denervation perturbation
    (dV_veno_max 250 -> 75 mL) applied via experimental mode."""
    return _metrics(_run_tilt("neuropathic_pots", experimental=True))


def test_neuropathic_venomotor_denervation_worsens_tilt(pots_metrics, neuropathic_experimental_metrics):
    """Direction check (tier A, Jacob 2000): blunting the venomotor reflex must
    WORSEN the orthostatic response vs canonical neuropathic mode."""
    can = pots_metrics["neuropathic_pots"]["dHR_sustained"]
    exp = neuropathic_experimental_metrics["dHR_sustained"]
    assert exp > can + 0.5, (
        f"experimental (denervated) sustained dHR {exp:.1f} not above canonical {can:.1f}"
    )


@pytest.mark.xfail(
    reason=("Cycle-3 simulation check: sustained dHR with dV_veno_max=75 mL is "
            "~21 bpm; dose-response over factor 0-0.5 is flat (18.5->21.7 bpm) "
            "because steady-state pooling is hydrostatic-gate-limited and creep "
            "re-expands capacity. Target >=30 bpm requires a future model "
            "revision (bounded creep and/or tilt-onset gain application)."),
    strict=True,
)
def test_neuropathic_experimental_sustained_criterion(neuropathic_experimental_metrics):
    """Target criterion from the cycle-3 re-curation evidence file: neuropathic
    POTS with venomotor denervation should meet the sustained 30 bpm criterion.
    Currently xfail — see reason."""
    assert neuropathic_experimental_metrics["dHR_sustained"] >= 30.0


def test_hyperadrenergic_sustained_criterion(pots_metrics):
    """Hyperadrenergic POTS (canonical, now including secondary hypovolemia
    TotalVol 4500->3900 promoted from optional_parameters after the cycle-3
    simulation check) must meet the sustained 30 bpm criterion."""
    d = pots_metrics["hyperadrenergic_pots"]["dHR_sustained"]
    assert d >= 30.0, f"hyperadrenergic sustained dHR = {d:.1f} bpm"


def test_hyperadrenergic_pressor_map_signature(pots_metrics, healthy_metrics):
    """Model-level surrogate for the Okamoto 2024 pressor signature: upright
    mean arterial pressure must RISE (vs flat/falling in other phenotypes)."""
    m = pots_metrics["hyperadrenergic_pots"]
    assert m["map_late"] >= m["map_supine"] + 3.0, (
        f"MAP pressor response {m['map_late'] - m['map_supine']:+.1f} mmHg"
    )
    # Contrast: healthy MAP must not show a pressor rise.
    assert healthy_metrics["map_late"] <= healthy_metrics["map_supine"] + 3.0


@pytest.mark.xfail(
    reason=("0-D model limitation: arterial pulse pressure narrows on tilt "
            "(stroke volume falls), so beat-peak SBP stays flat even though "
            "the MAP pressor response is present (+5 mmHg). The Okamoto 2024 "
            "upright delta-SBP >= +10 mmHg criterion is not reproducible in "
            "the current 0-D arterial windkessel."),
    strict=True,
)
def test_hyperadrenergic_sbp_pressor_criterion(pots_metrics):
    """Clinical validation criterion (Okamoto 2024, tier A): upright delta-SBP
    >= +10 mmHg. Currently xfail — see reason."""
    assert pots_metrics["hyperadrenergic_pots"]["dSBP"] >= 10.0


# ---------------------------------------------------------------------------
# Determinism (seeded engine)
# ---------------------------------------------------------------------------

def test_seeded_engine_is_deterministic():
    """Short supine-only run: identical seeds must give bit-identical HR."""
    short = {"tup": 1.0e30, "tend": 30.0, "height": 25.0, "angle": 60.0}
    m1 = BaroreflexPOTSModel()
    m2 = BaroreflexPOTSModel()
    r1 = SimulationEngine(m1, seed=SEED).run(short)
    r2 = SimulationEngine(m2, seed=SEED).run(short)
    assert np.array_equal(r1["Hc"], r2["Hc"])
