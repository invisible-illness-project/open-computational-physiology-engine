"""
Event-kernel machinery for transient physiological perturbations (G-P0-01,
G-P0-02).

An :class:`EventKernel` is an explicit, evidence-annotated description of one
transient event (meal, exercise bout, stressor, PEM episode, ...).  Kernels
replace the previous design in which behavior modifiers were recomputed from
``model.params`` every heartbeat, so multiplicative perturbations compounded
per beat (verified bug: 5 beats of ``meal`` drove RalpM 17.88 -> 4.24 instead
of the one-shot 13.41; exercise ``Es x1.30``/beat was unbounded).

Design contract (binding, per SWARM_SPEC W1-A):

* The engine keeps an immutable ``baseline_params`` snapshot per run.
* Kernels NEVER read or modify already-perturbed parameters.  Every beat the
  effective parameter set is recomputed as
  ``effective = f(baseline, active_kernels, t)``.
* Multiplicative kernel magnitudes compose against BASELINE:
  ``eff[p] = base[p] * prod_k (1 + env_k(t) * (m_k - 1))``; additive
  magnitudes compose as ``base[p] + sum_k env_k(t) * delta_k``.  Both are
  idempotent across beats by construction (envelopes depend only on t).
* After a kernel's recovery phase completes, its envelope is exactly 0 and
  parameters return EXACTLY to baseline (no residual drift).

Every kernel carries value/units/evidence-tier/provenance metadata per the
global honesty rules.  Magnitudes that are repo-legacy (uncited) are flagged
``provisional`` in provenance rather than silently presented as evidence.
"""

import os

import numpy as np
import yaml
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Distribution specifications
# ---------------------------------------------------------------------------

@dataclass
class DistributionSpec:
    """A minimal, serializable description of a sampling distribution.

    Supported kinds:
      constant(value)
      uniform(low, high)
      gamma(shape, scale[, truncate_low, truncate_high])  # mode=(shape-1)*scale
      normal(mean, sd)
    """
    kind: str
    params: dict

    def sample(self, rng):
        p = self.params
        if self.kind == "constant":
            return float(p["value"])
        if self.kind == "uniform":
            return float(rng.uniform(p["low"], p["high"]))
        if self.kind == "gamma":
            for _ in range(1000):
                x = float(rng.gamma(p["shape"], p["scale"]))
                lo = p.get("truncate_low", -np.inf)
                hi = p.get("truncate_high", np.inf)
                if lo <= x <= hi:
                    return x
            # Fall back to clamping if rejection sampling fails (pathological)
            return float(min(max(x, p.get("truncate_low", x)),
                             p.get("truncate_high", x)))
        if self.kind == "normal":
            return float(rng.normal(p["mean"], p["sd"]))
        raise ValueError(f"Unknown distribution kind: {self.kind}")

    def mean(self):
        p = self.params
        if self.kind == "constant":
            return float(p["value"])
        if self.kind == "uniform":
            return 0.5 * (p["low"] + p["high"])
        if self.kind == "gamma":
            return float(p["shape"] * p["scale"])
        if self.kind == "normal":
            return float(p["mean"])
        raise ValueError(self.kind)


# ---------------------------------------------------------------------------
# EventKernel
# ---------------------------------------------------------------------------

@dataclass
class EventKernel:
    """One transient physiological event with explicit semantics.

    Fields per master prompt §11 / SWARM_SPEC W1-A:

    event_id              unique identifier string
    trigger               dict describing the trigger; must carry
                          ``time_s`` (absolute simulation seconds at which the
                          event starts) and a human-readable ``type``.
    onset_distribution    DistributionSpec for the RISE time (s) from trigger
                          to full envelope (for delayed events such as PEM this
                          includes the delay: onset_s = delay + rise).
    duration_distribution DistributionSpec for the plateau time (s) at full
                          envelope (may be ~0 for pulse-like kernels).
    magnitude_distribution DistributionSpec for a global amplitude scalar
                          (multiplies every per-parameter magnitude and latent
                          effect; 1.0 = nominal).
    affected_parameters   list of dicts:
                          {"symbol": str,
                           "mode": "multiplicative" | "additive",
                           "magnitude": float}
                          multiplicative: eff = base * (1 + env*(mag-1))
                          additive:       eff = base + env*mag
    mechanism             free-text physiological mechanism (with citations).
    interaction_rules     dict; currently supported:
                          {"compose": "multiplicative_vs_baseline"} (default)
                          Documented composition semantics; kernels never
                          compose against already-modified parameters.
    recovery_kernel       dict describing the return-to-baseline phase:
                          {"shape": "linear"|"exponential"|"gamma",
                           "time_s": <duration or DistributionSpec-as-dict>}
                          Envelope is EXACTLY 0 after recovery completes.
    evidence_tier         "E0".."E5" (E5 = engineering judgment, always
                          flagged in provenance).
    provenance            dict with claim_ids / citations / status
                          ("evidence-anchored" | "provisional" |
                          "extrapolated_E0").
    latent_effects        optional dict {latent_state_name: additive offset at
                          full envelope}.  Latent offsets compose ADDITIVELY
                          in effect space and are applied transiently (never
                          integrated into evolving latent dynamics), so they
                          cannot compound either.
    delay_s               optional constant delay (s) before the rise starts
                          (convenience for PEM-style delayed kernels).
    rise_shape            "linear" (default) or "gamma" (skewed rise peaking
                          at the end of the onset window).
    second_wave           optional dict for an E0 delayed physiological
                          second wave: {"delay_s":..., "onset_s":...,
                          "duration_s":..., "recovery_s":...,
                          "relative_magnitude":...}.  OFF unless explicitly
                          constructed (see make_pem_second_wave_kernel) and
                          always carries honesty flag "extrapolated_E0".
    honesty_flags         list of strings surfaced into simulation results.
    """

    event_id: str
    trigger: dict
    onset_distribution: DistributionSpec
    duration_distribution: DistributionSpec
    magnitude_distribution: DistributionSpec
    affected_parameters: list
    mechanism: str
    interaction_rules: dict
    recovery_kernel: dict
    evidence_tier: str
    provenance: dict
    latent_effects: dict = field(default_factory=dict)
    delay_s: float = 0.0
    rise_shape: str = "linear"
    second_wave: dict = None
    honesty_flags: list = field(default_factory=list)

    # Realized (sampled) timing/amplitude -- set by realize()
    _t0_s: float = None
    _onset_s: float = None
    _duration_s: float = None
    _recovery_s: float = None
    _amplitude: float = None

    # ------------------------------------------------------------------
    def realize(self, rng=None):
        """Sample the kernel's timing/amplitude distributions.  Deterministic
        if a seeded rng is supplied; without one, uses distribution means so
        the kernel is fully deterministic."""
        rng = rng if rng is not None else _MeanRNG()
        self._t0_s = float(self.trigger["time_s"])
        self._onset_s = self.onset_distribution.sample(rng)
        self._duration_s = max(0.0, self.duration_distribution.sample(rng))
        rec = self.recovery_kernel.get("time_s", 0.0)
        if isinstance(rec, DistributionSpec):
            self._recovery_s = max(0.0, rec.sample(rng))
        elif isinstance(rec, dict):
            self._recovery_s = max(0.0, DistributionSpec(rec["kind"], rec["params"]).sample(rng))
        else:
            self._recovery_s = max(0.0, float(rec))
        self._amplitude = self.magnitude_distribution.sample(rng)
        return self

    # ------------------------------------------------------------------
    @property
    def t_end(self):
        """Absolute time at which the kernel's envelope is exactly zero."""
        if self._t0_s is None:
            raise RuntimeError("kernel not realized")
        end = self._t0_s + self.delay_s + self._onset_s + self._duration_s + self._recovery_s
        if self.second_wave is not None:
            sw = self.second_wave
            sw_end = (self._t0_s + sw["delay_s"] + sw["onset_s"]
                      + sw["duration_s"] + sw["recovery_s"])
            end = max(end, sw_end)
        return end

    def is_active(self, t):
        return self._t0_s is not None and self._t0_s <= t < self.t_end

    # ------------------------------------------------------------------
    def envelope(self, t):
        """Envelope in [0, amplitude] at absolute time t (seconds).

        Phases: [t0, t0+delay): 0
                [t0+delay, t0+delay+onset): rise 0 -> amplitude
                [.. + duration): plateau at amplitude
                [.. + recovery): decay amplitude -> 0 (exact 0 at the end)
        """
        if self._t0_s is None:
            raise RuntimeError("kernel not realized")
        tau = t - self._t0_s
        if tau < 0.0:
            return 0.0
        tau -= self.delay_s
        if tau < 0.0:
            env = 0.0
        elif tau < self._onset_s:
            x = tau / self._onset_s if self._onset_s > 0 else 1.0
            if self.rise_shape == "gamma":
                # gamma-style asymmetric rise: (x)*exp(1-x) normalized to 1 at x=1
                env = x * np.exp(1.0 - x)
            else:
                env = x
        elif tau < self._onset_s + self._duration_s:
            env = 1.0
        elif tau < self._onset_s + self._duration_s + self._recovery_s:
            r = self._recovery_s
            x = (tau - self._onset_s - self._duration_s) / r if r > 0 else 1.0
            shape = self.recovery_kernel.get("shape", "linear")
            if shape == "exponential":
                # exponential decay reaching exactly 0 at x=1 via shifted exp
                tau_rec = self.recovery_kernel.get("tau_fraction", 0.25) * r
                env = np.exp(-x * r / max(tau_rec, 1e-12))
                env = max(0.0, (env - np.exp(-r / max(tau_rec, 1e-12)))
                          / (1.0 - np.exp(-r / max(tau_rec, 1e-12))))
            else:  # "linear" (and "gamma" falls back to linear decay)
                env = 1.0 - x
        else:
            env = 0.0

        env = self._amplitude * max(0.0, min(1.0, env))

        # Optional E0 second wave (never present unless explicitly enabled)
        if self.second_wave is not None:
            sw = self.second_wave
            stau = t - self._t0_s - sw["delay_s"]
            sw_env = 0.0
            if 0.0 <= stau < sw["onset_s"]:
                sw_env = stau / sw["onset_s"] if sw["onset_s"] > 0 else 1.0
            elif stau < sw["onset_s"] + sw["duration_s"]:
                sw_env = 1.0
            elif stau < sw["onset_s"] + sw["duration_s"] + sw["recovery_s"]:
                sw_env = 1.0 - (stau - sw["onset_s"] - sw["duration_s"]) / sw["recovery_s"]
            env += self._amplitude * sw.get("relative_magnitude", 0.5) * max(0.0, min(1.0, sw_env))
        return env


class _MeanRNG:
    """Deterministic 'rng' that returns distribution means (used when a
    kernel is realized without a random generator)."""
    def uniform(self, lo, hi):
        return 0.5 * (lo + hi)

    def gamma(self, shape, scale):
        return shape * scale

    def normal(self, mean, sd):
        return mean


# ---------------------------------------------------------------------------
# Kernel manager / overlay composer
# ---------------------------------------------------------------------------

class EventKernelManager:
    """Tracks active kernels and composes their effects against an immutable
    baseline parameter set.  Composition is always against BASELINE, never
    against already-modified parameters (G-P0-01 fix)."""

    def __init__(self):
        self.kernels = []

    def add_kernel(self, kernel, rng=None):
        if kernel._t0_s is None:
            kernel.realize(rng)
        self.kernels.append(kernel)
        return kernel

    def clear(self):
        self.kernels = []

    def active_kernels(self, t):
        return [k for k in self.kernels if k.is_active(t)]

    def prune(self, t):
        """Drop kernels whose envelope has permanently returned to zero."""
        self.kernels = [k for k in self.kernels if k.t_end >= t]

    # ------------------------------------------------------------------
    def compute_parameter_overlay(self, baseline_params, t):
        """effective = f(baseline, active_kernels, t).

        multiplicative: eff[p] = base[p] * prod_k (1 + env_k*(m_k - 1))
        additive:       eff[p] = base[p] + sum_k env_k*delta_k
        """
        effective = dict(baseline_params)
        for kernel in self.active_kernels(t):
            env = kernel.envelope(t)
            if env == 0.0:
                continue
            for aff in kernel.affected_parameters:
                sym = aff["symbol"]
                if sym not in effective:
                    continue
                if aff.get("mode", "multiplicative") == "multiplicative":
                    m = aff["magnitude"]
                    effective[sym] = effective[sym] * (1.0 + env * (m - 1.0))
                else:
                    effective[sym] = effective[sym] + env * aff["magnitude"]
        return effective

    def compute_latent_offsets(self, t):
        """Additive latent-state offsets (effect-space composition)."""
        offsets = {}
        for kernel in self.active_kernels(t):
            env = kernel.envelope(t)
            if env == 0.0:
                continue
            for name, full_offset in kernel.latent_effects.items():
                offsets[name] = offsets.get(name, 0.0) + env * full_offset
        return offsets

    def honesty_flags(self, t=None):
        flags = []
        for kernel in self.kernels:
            if t is None or kernel.is_active(t):
                for f in kernel.honesty_flags:
                    if f not in flags:
                        flags.append(f)
        return flags


# ---------------------------------------------------------------------------
# Predefined behavior kernels (meal / exercise / stress)
# ---------------------------------------------------------------------------

def make_meal_kernel(start_s, rng=None, time_scale=1.0):
    """Postprandial splanchnic pooling kernel.

    Plateau magnitudes are the repo-legacy one-shot factors (RalpM/Ralpm
    x0.75, Cal x1.15) -- UNCITED, flagged provisional.  Timing is
    evidence-anchored: postprandial hemodynamic peak 30-60 min, resolution
    over 2-4 h (EVD-HLTH-006, 25-study systematic review; EVD-METB-005).
    ``time_scale`` (default 1.0 = literature timescale) uniformly compresses
    onset/plateau/recovery for short ODE protocol runs and regression tests;
    it rescales TIMING ONLY, never magnitudes.
    """
    ts = float(time_scale)
    if ts <= 0:
        raise ValueError("time_scale must be positive")
    return EventKernel(
        event_id="meal_postprandial_pooling",
        trigger={"type": "meal_ingestion", "time_s": float(start_s)},
        onset_distribution=DistributionSpec("constant", {"value": 30.0 * 60.0 * ts}),
        duration_distribution=DistributionSpec("constant", {"value": 60.0 * 60.0 * ts}),
        magnitude_distribution=DistributionSpec("constant", {"value": 1.0}),
        affected_parameters=[
            # Repo-legacy plateau factors (provisional, tier C): direction is
            # splanchnic vasodilation + capacitance recruitment, magnitude not
            # directly cited -- see G-P0-01 regression target (RalpM 13.41).
            {"symbol": "RalpM", "mode": "multiplicative", "magnitude": 0.75},
            {"symbol": "Ralpm", "mode": "multiplicative", "magnitude": 0.75},
            {"symbol": "Cal", "mode": "multiplicative", "magnitude": 1.15},
        ],
        mechanism=("Postprandial splanchnic vasodilation and pooling: SMA flow "
                   "~doubles after a mixed meal, HR +6-21%, CO +9-100%, peak "
                   "30-60 min (EVD-HLTH-006)."),
        interaction_rules={"compose": "multiplicative_vs_baseline"},
        recovery_kernel={"shape": "linear", "time_s": 90.0 * 60.0 * ts},
        evidence_tier="E3",
        provenance={
            "claim_ids": ["EVD-HLTH-006", "EVD-METB-005", "EVD-METB-002"],
            "status": "provisional",
            "note": ("Timing evidence-anchored (peak 30-60 min, resolve 2-4 h); "
                     "plateau magnitudes are repo-legacy one-shot factors, "
                     "uncited -- kept for regression continuity, tier C."),
        },
    )


# Supine mean carotid setpoint (mmHg) used to evaluate the resting HR of
# the cardiovagal Hill target.  This is the SAME documented state-
# initialization heuristic used by
# models/baroreflex_model.initialize_steady_state (pcm0); it is read here
# only to invert the Hill target for the exercise resetting factor, never
# to overwrite model parameters.
_PCM0_SUPINE_MMHG = 93.333


def _kb_nominal_params():
    """KB nominal parameter set (single source of truth:
    knowledge_base/equations/mathematical_models.yaml, same file
    models/baroreflex_model.load_parameters reads)."""
    kb_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "knowledge_base", "equations", "mathematical_models.yaml")
    with open(kb_file, "r", encoding="utf-8") as f:
        model_data = yaml.safe_load(f)
    for model in model_data.get("models", []):
        if model.get("model_id") == "pots_baroreflex_response_model":
            return {p["symbol"]: p["nominal_value"]
                    for p in model.get("parameters", [])}
    raise ValueError("pots_baroreflex_response_model not found in KB")


def exercise_p2h_reset_factor(params, intensity):
    """Multiplicative baroreflex operating-point reset factor for p2H.

    Mechanism (EVD-AUTN-008, E4; REL-BAROREFLEX-RESETTING): exercise
    resets the cardiovagal baroreflex sigmoid upward/rightward with
    PRESERVED maximal gain via central command + the exercise pressor
    reflex.  Implemented exactly as prescribed: an intensity-dependent
    shift of the Hill midpoint p2H (kH untouched -> gain preserved).

    Magnitude derivation (no fitted constant): the cited steady-state
    HR-reserve relation (HEALTHY_PHYSIOLOGY_EVIDENCE 4.2 implementation
    recommendation, E1/E4; EVD-HLTH-005) is

        HR_ss = HR_rest + (HR_max - HR_rest) * intensity,

    with HR_max the model's own controller ceiling HM and HR_rest the
    Hill target at the documented supine carotid setpoint.  Inverting
    the Hill target H(p2H) = (HM-Hm)*p2H^kH/(pcm^kH+p2H^kH)+Hm at fixed
    supine pcm gives the p2H multiplier that requests HR_ss open-loop:

        R = [ (HM-Hr)(Ht-Hm) / ((Hr-Hm)(HM-Ht)) ]^(1/kH)

    The closed loop settles BELOW this open-loop request (arterial
    pressure feedback); the measured response is reported, never tuned.
    ``intensity`` is clipped to [0, 0.99] (at 1.0 the request equals the
    controller ceiling and the inversion is singular).
    """
    HM = float(params["HM"])
    Hm = float(params["Hm"])
    kH = float(params["kH"])
    p2H = float(params["p2H"])
    I = min(max(float(intensity), 0.0), 0.99)
    Hr = (HM - Hm) * p2H ** kH / (_PCM0_SUPINE_MMHG ** kH + p2H ** kH) + Hm
    Ht = Hr + I * (HM - Hr)
    return float(((HM - Hr) * (Ht - Hm) / ((Hr - Hm) * (HM - Ht)))
                 ** (1.0 / kH))


def make_exercise_kernel(start_s, duration_s=None, intensity=0.7, rng=None,
                         baseline_params=None):
    """Exercise-bout kernel: contractility + autonomic chronotropic drive.

    Two mechanistic components:

    1. Es x1.30 contractility plateau (repo-legacy one-shot value,
       provisional; bounded by construction, fixing the unbounded
       x1.30/heart-beat compounding of G-P0-01).
    2. Autonomic HR drive (W5): constant-load exercise raises HR via
       vagal withdrawal + sympathetic activation (central command /
       exercise pressor reflex).  Implemented as
         a. an intensity-scaled multiplicative reset of the cardiovagal
            Hill midpoint p2H with preserved gain
            (:func:`exercise_p2h_reset_factor`; EVD-AUTN-008 form,
            magnitude from the cited HR-reserve steady-state relation,
            EVD-HLTH-005), and
         b. latent autonomic offsets (parasympathetic down / sympathetic
            up, scaled by intensity) so the HRV generator sees the bout's
            vagal withdrawal; offset magnitudes are E5 engineering
            (evidence fixes direction and timescale, not a number),
            bounded by the latent [0, 1] clamps.

    Onset ~30 s (sympathetic slow component, EVD-HLTH-005); recovery
    follows the slow HRR component, tau ~2-10 min (EVD-HLTH-005).
    ``baseline_params`` (optional) supplies the run's actual baseline
    controller constants for the reset-factor derivation; when omitted
    the KB nominal set is used (same YAML the model loads).
    """
    duration_s = 300.0 if duration_s is None else float(duration_s)
    intensity = float(intensity)
    params = baseline_params if baseline_params is not None \
        else _kb_nominal_params()
    p2h_reset = exercise_p2h_reset_factor(params, intensity)
    return EventKernel(
        event_id="exercise_bout",
        trigger={"type": "exercise_start", "time_s": float(start_s),
                 "intensity": intensity},
        onset_distribution=DistributionSpec("constant", {"value": 30.0}),
        duration_distribution=DistributionSpec("constant", {"value": duration_s}),
        magnitude_distribution=DistributionSpec("constant", {"value": 1.0}),
        affected_parameters=[
            {"symbol": "Es", "mode": "multiplicative", "magnitude": 1.30},
            # Cardiovagal baroreflex operating-point reset (central
            # command / exercise pressor reflex), gain preserved:
            # p2H x R(intensity), R derived open-loop from the cited
            # HR-reserve steady-state relation - see
            # exercise_p2h_reset_factor (EVD-AUTN-008, EVD-HLTH-005).
            {"symbol": "p2H", "mode": "multiplicative",
             "magnitude": p2h_reset},
        ],
        latent_effects={
            # Vagal withdrawal + sympathetic elevation during the bout
            # (EVD-HLTH-005 mechanism; E5 engineering magnitudes, scaled
            # by intensity, bounded by the latent [0, 1] clamps).
            "parasympathetic_tone": -0.4 * intensity,
            "sympathetic_tone": 0.4 * intensity,
        },
        mechanism=("Constant-load exercise: vagal withdrawal + sympathetic "
                   "activation raise HR (central command resets the "
                   "carotid-cardiac arc; EVD-AUTN-008); contractility rises "
                   "(Es x1.30, repo-legacy); onset tau ~30-45 s (slow "
                   "component), recovery HRR tau ~2-10 min (EVD-HLTH-005)."),
        interaction_rules={"compose": "multiplicative_vs_baseline"},
        recovery_kernel={"shape": "linear", "time_s": 300.0},
        evidence_tier="E5",
        provenance={
            "claim_ids": ["EVD-HLTH-005", "EVD-AUTN-008"],
            "status": "provisional",
            "note": ("Structure E5 (engineering). Es x1.30 plateau is a "
                     "repo-legacy uncited factor kept for continuity, now "
                     "bounded by the kernel envelope. p2H reset factor "
                     f"{p2h_reset:.4f} at intensity {intensity:.2f}: FORM "
                     "evidence-anchored (EVD-AUTN-008 sigmoid midpoint "
                     "shift, gain preserved), magnitude derived open-loop "
                     "from the cited HR-reserve relation HR_ss = HR_rest + "
                     "(HRmax-HR_rest)*intensity (HEALTHY 4.2/EVD-HLTH-005); "
                     "the closed-loop response settles below the request "
                     "and is reported, never tuned. Latent autonomic "
                     "offsets are E5 engineering magnitudes (evidence "
                     "fixes direction/timescale only)."),
        },
    )


def make_stress_kernel(start_s, duration_s=600.0, rng=None):
    """Acute stressor kernel: sympathetic surge + vagal withdrawal on the
    latent autonomic state (minutes-scale rise and decay; EVD-TEMP-002/
    TEMPORAL dossier §3, E2)."""
    return EventKernel(
        event_id="acute_stress",
        trigger={"type": "stress_onset", "time_s": float(start_s)},
        onset_distribution=DistributionSpec("constant", {"value": 120.0}),
        duration_distribution=DistributionSpec("constant", {"value": float(duration_s)}),
        magnitude_distribution=DistributionSpec("constant", {"value": 1.0}),
        affected_parameters=[],
        latent_effects={"stress_load": 0.3},
        mechanism=("Acute stress: SAM-axis sympathetic surge with vagal "
                   "withdrawal, minutes-scale (TEMPORAL dossier §3)."),
        interaction_rules={"compose": "additive_effect_space"},
        recovery_kernel={"shape": "linear", "time_s": 600.0},
        evidence_tier="E2",
        provenance={"claim_ids": ["EVD-TEMP-002"], "status": "evidence-anchored"},
    )


# ---------------------------------------------------------------------------
# PEM kernels (G-P0-02) -- TWO decoupled kernels + an E0 second wave
# ---------------------------------------------------------------------------

# Evidence anchors (DISEASE_EVIDENCE_MECFS.md §4; PARAMETER_SPECIFICATION
# PEM_symptom_kernel_params; EVIDENCE_REGISTRY EVD-MECFS-008/009/010):
#   * symptom kernel: onset delay Gamma(mode 18 h, range 0-48 h) [Chu 2018,
#     Stussman 2020]; peak 24-48 h; recovery right-skewed, mean 12.7 +/- 1.2 d
#     (Moore 2023, n=144 pooled), range 1-64 d, <10% >3 weeks;
#     pharmacokinetic decay ~0.10 +/- 0.02 units/day, peak +1.5 units above
#     baseline ~24 h post second exertion.
#   * physiological slowed-recovery kernel (DECOUPLED): post-exercise HRV
#     recovery 3-6 h in healthy controls vs 9-13 h (up to 24 h) in patients
#     after exercise at/above VT1 (long-COVID wearable proxy, n=127, E2;
#     EVD-MECFS-010).  Direct ME/CFS multi-day wearable PEM data DO NOT EXIST
#     (G-P1-06) -> all PEM channels are labeled evidence_mode "extrapolation".
#   * physiological second wave (24-48 h delayed): E0 hypothesis only, OFF by
#     default, honesty flag "extrapolated_E0" when enabled.

PEM_ONSET_DELAY = DistributionSpec("gamma", {"shape": 4.0, "scale": 6.0,
                                             "truncate_low": 0.0,
                                             "truncate_high": 48.0})  # hours; mode 18 h
PEM_RECOVERY_DAYS = DistributionSpec("gamma", {"shape": 4.0, "scale": 3.175,
                                               "truncate_low": 1.0,
                                               "truncate_high": 64.0})  # days; mean 12.7 d
PEM_DETECTABILITY = 0.575  # mixture: ~50-65% of episodes show a clear
                           # physiological signature (EVD-MECFS-007/010)


def pem_symptom_kernel(exertion_end_s, severity=1.0, rng=None, detectable=None):
    """Delayed PEM SYMPTOM kernel (symptom layer only; ME/CFS-defining).

    Envelope: delay ~ Gamma(mode 18 h, 0-48 h) -> gamma-shaped rise to peak at
    24-48 h post-exertion -> linear decay 0.10 units/day scaled so total
    episode duration matches the sampled right-skewed recovery (mean 12.7 d,
    range 1-64 d, clip).  Acts ONLY on latent symptom substrates
    (metabolic reserve down, inflammatory burden up) -- never on mechanistic
    parameters.  Multiple episodes compose additively in effect space
    (rolling-PEM baseline creep emerges from superposition).
    """
    rng = rng if rng is not None else np.random.default_rng()
    delay_h = PEM_ONSET_DELAY.sample(rng)
    peak_h = float(np.clip(delay_h + rng.uniform(12.0, 24.0), 24.0, 48.0))
    recovery_d = PEM_RECOVERY_DAYS.sample(rng)
    recovery_h = recovery_d * 24.0
    rise_h = max(1.0, peak_h - delay_h)
    # Decay phase length so that (delay+rise+decay) ~= recovery horizon.
    decay_h = max(24.0, recovery_h - delay_h - rise_h)

    if detectable is None:
        detectable = bool(rng.uniform() < PEM_DETECTABILITY)

    kernel = EventKernel(
        event_id="pem_symptom_episode",
        trigger={"type": "post_exertional", "time_s": float(exertion_end_s),
                 "detectable": detectable},
        onset_distribution=DistributionSpec("constant", {"value": rise_h * 3600.0}),
        duration_distribution=DistributionSpec("constant", {"value": 0.0}),
        magnitude_distribution=DistributionSpec("constant", {"value": float(severity)}),
        affected_parameters=[],  # symptom layer ONLY -- never mechanistic params
        latent_effects={
            # Moore 2023: peak ~+1.5 SSS units above baseline (~+35-40% of
            # typical baseline load).  Mapped onto repo latent scales:
            # metabolic_reserve in [0,1], inflammatory_burden in [0,10].
            "metabolic_reserve": -0.4,
            "inflammatory_burden": 1.5,
        },
        mechanism=("Post-exertional malaise: delayed multi-system symptom "
                   "exacerbation 12-48 h after exertion, peak 24-48 h, "
                   "recovery mean 12.7 d (Moore 2023; Chu 2018; Stussman 2020)."),
        interaction_rules={"compose": "additive_effect_space",
                           "stacking": "episodes superpose (rolling-PEM creep)"},
        recovery_kernel={"shape": "linear", "time_s": decay_h * 3600.0},
        evidence_tier="E2",
        delay_s=delay_h * 3600.0,
        rise_shape="gamma",
        provenance={
            "claim_ids": ["EVD-MECFS-008", "EVD-MECFS-009", "EVD-MECFS-001"],
            "status": "evidence-anchored (timing); amplitude single-source (Moore 2023)",
            "evidence_mode": "extrapolation",
            "note": ("No multi-day wearable PEM dataset exists (G-P1-06); "
                     "kernel statistics validated only against literature "
                     "moments. Mean recovery 12.7 d is a MEAN, not median."),
        },
        honesty_flags=["pem_evidence_mode_extrapolation"],
    )
    kernel.realize(rng)
    return kernel


def slowed_recovery_kernel(exertion_end_s, is_patient=False, intensity=0.7,
                           vt1_intensity=0.55, rng=None, detectable=None):
    """Physiological slowed-recovery kernel (DECOUPLED from the symptom
    kernel): suppressed vagal reactivation / HRV after exertion.

    Duration: healthy 3-6 h; post-VT1 patient 9-13 h (up to 24 h) -- long-COVID
    wearable proxy (n=127, E2; EVD-MECFS-010).  Below-VT1 patient exertion
    recovers on the healthy timescale.  Episode detectability is a mixture
    (~50-65% show a clear physiological signature); undetectable episodes have
    zero amplitude.  Latent only: reduces parasympathetic/vagal drive and
    delays nocturnal HRV rebound; does NOT touch mechanistic parameters.
    """
    rng = rng if rng is not None else np.random.default_rng()
    post_vt1 = is_patient and intensity >= vt1_intensity
    if post_vt1:
        duration_h = float(rng.uniform(9.0, 13.0))
    else:
        duration_h = float(rng.uniform(3.0, 6.0))
    if detectable is None:
        detectable = bool(rng.uniform() < PEM_DETECTABILITY) if is_patient else True

    kernel = EventKernel(
        event_id="slowed_autonomic_recovery",
        trigger={"type": "exercise_end", "time_s": float(exertion_end_s),
                 "intensity": float(intensity), "post_vt1": post_vt1,
                 "detectable": detectable},
        onset_distribution=DistributionSpec("constant", {"value": 0.25 * 3600.0}),
        duration_distribution=DistributionSpec("constant", {"value": duration_h * 3600.0}),
        magnitude_distribution=DistributionSpec(
            "constant", {"value": 1.0 if detectable else 0.0}),
        affected_parameters=[],
        latent_effects={
            # RMSSD/HF proxy: -15-30% of persona baseline for the recovery
            # window (EVD-MECFS-010 implementation note) -> vagal drive offset.
            "parasympathetic_tone": -0.2,
            "autonomic_recovery_capacity": -0.3,
        },
        mechanism=("Blunted post-exercise parasympathetic reactivation; HRV "
                   "stays depressed 3-6 h (healthy) vs 9-13 h post-VT1 "
                   "(patient, long-COVID wearable proxy)."),
        interaction_rules={"compose": "additive_effect_space"},
        recovery_kernel={"shape": "exponential", "time_s": 2.0 * 3600.0,
                         "tau_fraction": 0.5},
        evidence_tier="E2",
        provenance={
            "claim_ids": ["EVD-MECFS-010", "EVD-MECFS-011"],
            "status": "evidence-anchored (long-COVID proxy)",
            "evidence_mode": "extrapolation",
            "note": ("Nearest proxy to ME/CFS; direct ME/CFS multi-day "
                     "wearable PEM data do not exist."),
        },
        honesty_flags=["pem_evidence_mode_extrapolation"],
    )
    kernel.realize(rng)
    return kernel


def pem_second_wave_kernel(exertion_end_s, severity=1.0, rng=None):
    """E0 HYPOTHESIS: delayed physiological second wave 24-48 h post-exertion
    (delayed cytokine/gene-expression surge tracks the PEM window;
    DISEASE_EVIDENCE_MECFS Claim 4.4 -- timing only, no wearable-quantified
    magnitude).  OFF by default; constructing this kernel is the explicit
    opt-in.  Always carries honesty flag 'extrapolated_E0' and affects only
    latent autonomic substrates, with a deliberately small amplitude."""
    rng = rng if rng is not None else np.random.default_rng()
    kernel = EventKernel(
        event_id="pem_physiological_second_wave_E0",
        trigger={"type": "post_exertional", "time_s": float(exertion_end_s)},
        onset_distribution=DistributionSpec("constant", {"value": 12.0 * 3600.0}),
        duration_distribution=DistributionSpec("constant", {"value": 12.0 * 3600.0}),
        magnitude_distribution=DistributionSpec("constant", {"value": float(severity)}),
        affected_parameters=[],
        latent_effects={"parasympathetic_tone": -0.1,
                        "inflammatory_burden": 0.5},
        mechanism=("E0 hypothesis: delayed molecular-surrogate second wave "
                   "(gene-expression/cytokine changes 24-72 h post-exertion) "
                   "manifesting as a late autonomic dip. NOT established."),
        interaction_rules={"compose": "additive_effect_space"},
        recovery_kernel={"shape": "linear", "time_s": 24.0 * 3600.0},
        evidence_tier="E0",
        delay_s=24.0 * 3600.0,
        provenance={
            "claim_ids": ["EVD-MECFS-013"],
            "status": "extrapolated_E0",
            "note": ("Hypothesis-only (E0). Engine-inert unless explicitly "
                     "constructed; never enabled in canonical mode."),
        },
        honesty_flags=["extrapolated_E0", "pem_evidence_mode_extrapolation"],
    )
    kernel.realize(rng)
    return kernel
