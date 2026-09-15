"""RR-series source adapter (W2-E HRV contract, G-P0-05 interface).

Contract being built in parallel by W2-E::

    simulation/hrv.py::generate_rr_series(hrv_inputs: dict, seed: int,
                                          config=None) -> dict
    -> {"beat_times_s", "rr_intervals_ms", "beat_types", "provenance"}

This module is the SINGLE place the dataset builder obtains beat series:

  * If ``simulation.hrv`` is importable and exposes ``generate_rr_series``,
    it is used directly (the structured IPFM generator: RSA, Mayer 0.1 Hz,
    1/f fractal structure, Bernoulli ectopy with phase reset).
  * Otherwise a clearly-flagged FALLBACK derives beats from the engine's
    mean-HR trajectory by cumulative-phase integration
    (``beats(t) = int HR(u)/60 du`` inverted to beat times).  The fallback
    carries NO RSA/Mayer/1-f/ectopy structure; every record produced with
    it carries the honesty flags ``rr_fallback_no_structured_hrv`` and
    ``hrv_structure_unresolved_E0`` and its ``provenance.source`` is
    ``"fallback_mean_hr_phase_integration"``.

The fallback is honest about its limits (SWARM_SPEC rule 1): the RR
series is a resampling of the engine mean-HR trajectory at beat times,
not a structured HRV model.
"""

from __future__ import annotations

import numpy as np

HRV_MODULE_AVAILABLE = False
_HRV_IMPORT_ERROR = None
try:  # W2-E contract (parallel workstream); consume, never guess.
    from simulation.hrv import generate_rr_series as _w2e_generate_rr_series
    HRV_MODULE_AVAILABLE = True
except ImportError as exc:  # pragma: no cover - depends on merge timing
    _w2e_generate_rr_series = None
    _HRV_IMPORT_ERROR = str(exc)

FALLBACK_HONESTY_FLAGS = ["rr_fallback_no_structured_hrv",
                          "hrv_structure_unresolved_E0"]

#: HRV generator parameters (simulation/hrv.py default_params()) whose
#: realized values scale the beat-to-beat modulation amplitude, and hence
#: RMSSD, ~linearly.  Used by the trait-calibration path below.
HRV_AMPLITUDE_KEYS = ("rsa_amplitude_0p1Hz", "mayer_amplitude",
                      "fractal_amplitude")

#: Bounds of the trait amplitude gain (documented guard): the sampled
#: ln-RMSSD trait is a POPULATION target; gains outside [0.2, 5] would push
#: the IPFM modulator into its rate-clip nonlinearity and are clamped, with
#: the clamp recorded in provenance.
TRAIT_GAIN_MIN, TRAIT_GAIN_MAX = 0.2, 5.0

#: Documented tolerance of the realized-vs-target RMSSD check (generator
#: stochasticity + ectopy + gain clamp): tests assert |realized - target|
#: <= TRAIT_RMSSD_TOLERANCE * target.
TRAIT_RMSSD_TOLERANCE = 0.30

TRAIT_HONESTY_FLAG = "hrv_trait_amplitude_gain_machine_calibrated"


def _rmssd_ms(rr_intervals_ms) -> float:
    rr = np.asarray(rr_intervals_ms, dtype=float)
    if rr.size < 3:
        return float("nan")
    return float(np.sqrt(np.mean(np.diff(rr) ** 2)))


def hrv_module_status() -> dict:
    """Report which RR source is active (for manifests and reports)."""
    return {
        "w2e_hrv_module_available": HRV_MODULE_AVAILABLE,
        "import_error": None if HRV_MODULE_AVAILABLE else _HRV_IMPORT_ERROR,
        "active_source": ("simulation.hrv.generate_rr_series (W2-E IPFM)"
                          if HRV_MODULE_AVAILABLE
                          else "fallback_mean_hr_phase_integration"),
    }


def generate_rr_series(hrv_inputs: dict, seed: int, config: dict | None = None) -> dict:
    """Produce a beat series from engine HRV inputs.

    Parameters
    ----------
    hrv_inputs : dict
        ``SimulationEngine.get_hrv_inputs()`` payload (mean-HR trajectory
        + vagal/sympathetic drives + respiration + sleep stages).
    seed : int
        Per-subject RR-seed (seed hierarchy: dataset -> subject -> channel).
    config : dict, optional
        Passed through to the W2-E generator.  Recognized keys:
        ``subject_params`` (explicit HRVConfig parameter overrides, per the
        documented simulation/hrv.py override keys), ``age_years``,
        ``fitness_rsa_gain``, ``ectopy_enabled``, and ``subject_traits``
        with ``ln_rmssd_ms``: the cohort-sampled HRV trait (dataset-hardening
        W4-2, review F9/F11).  When present, the generator is first run
        once with the unmodified config, and the three modulation-amplitude
        parameters (``rsa_amplitude_0p1Hz``, ``mayer_amplitude``,
        ``fractal_amplitude`` -- the documented HRVConfig subject_params
        override keys) are then scaled by ``exp(ln_rmssd_ms) /
        realized_baseline_rmssd`` so the realized RMSSD tracks the sampled
        trait within TRAIT_RMSSD_TOLERANCE (30%).  This is a machine
        calibration (ratio method, tier C): it is recorded in
        ``provenance["trait_calibration"]`` and honesty-flagged.  Ignored
        by the fallback except for provenance echo.

    Returns
    -------
    dict with ``beat_times_s`` [n], ``rr_intervals_ms`` [n] (interval
    STARTING at each beat), ``beat_types`` [n] ("normal"/"ectopic"
    labels) -- all length-aligned -- plus ``provenance`` dict.
    """
    if HRV_MODULE_AVAILABLE:
        cfg_dict = dict(config or {})
        traits = cfg_dict.pop("subject_traits", None) or {}
        target_ln_rmssd = traits.get("ln_rmssd_ms")
        if target_ln_rmssd is None:
            out = _w2e_generate_rr_series(
                hrv_inputs, seed, config=_to_hrv_config(config))
            out = dict(out)
            out = _align_beats(out)
            out.setdefault("provenance", {})
            out["provenance"].setdefault("source", "simulation.hrv.generate_rr_series")
            return out
        return _generate_with_rmssd_trait(
            hrv_inputs, seed, cfg_dict, float(target_ln_rmssd), traits)
    return _fallback_rr_series(hrv_inputs, seed, config=config)


def _generate_with_rmssd_trait(hrv_inputs, seed, cfg_dict: dict,
                               target_ln_rmssd: float, traits: dict) -> dict:
    """Two-pass amplitude calibration wiring the cohort ln-RMSSD trait into
    the IPFM generator (review F11: the trait previously landed in an
    ignored subject_params key and never reached the RR series).

    Pass 1 realizes the unmodified config; pass 2 overrides the three
    amplitude subject_params with gain = target/baseline.  The age factor
    is NOT additionally applied (``age_years`` intentionally unset): the
    Lifelines trait marginal is already age/sex-specific, so applying the
    generator's age-decline factor would double-count age.
    """
    target_rmssd = float(np.exp(target_ln_rmssd))
    base = _w2e_generate_rr_series(
        hrv_inputs, seed, config=_to_hrv_config(cfg_dict))
    rmssd0 = _rmssd_ms(base["rr_intervals_ms"])
    if not np.isfinite(rmssd0) or rmssd0 <= 0.0:
        raise ValueError(
            f"baseline RR series has no measurable RMSSD ({rmssd0}); "
            "cannot calibrate the ln-RMSSD trait")
    gain = float(np.clip(target_rmssd / rmssd0,
                         TRAIT_GAIN_MIN, TRAIT_GAIN_MAX))
    realized = base.get("provenance", {}).get("parameters", {})
    overrides = dict(cfg_dict.get("subject_params") or {})
    for key in HRV_AMPLITUDE_KEYS:
        param_prov = realized.get(key) or {}
        if "value_used" in param_prov:
            overrides[key] = float(param_prov["value_used"]) * gain
    cal_cfg = dict(cfg_dict)
    cal_cfg["subject_params"] = overrides
    out = _w2e_generate_rr_series(
        hrv_inputs, seed, config=_to_hrv_config(cal_cfg))
    out = dict(out)
    out = _align_beats(out)
    prov = dict(out.get("provenance", {}))
    prov.setdefault("source", "simulation.hrv.generate_rr_series")
    prov["trait_calibration"] = {
        "method": ("two-pass amplitude-gain ratio calibration (tier C "
                   "machine-calibrated): subject_params[amplitude] *= "
                   "target_rmssd / baseline_rmssd"),
        "target_ln_rmssd_ms": round(target_ln_rmssd, 4),
        "target_rmssd_ms": round(target_rmssd, 2),
        "baseline_rmssd_ms": round(rmssd0, 2),
        "amplitude_gain": round(gain, 4),
        "gain_clamped": bool(abs(target_rmssd / rmssd0 - gain) > 1e-12),
        "gain_bounds": [TRAIT_GAIN_MIN, TRAIT_GAIN_MAX],
        "amplitude_keys_scaled": list(HRV_AMPLITUDE_KEYS),
        "age_factor_note": ("HRVConfig.age_years intentionally unset: the "
                            "Lifelines ln-RMSSD trait marginal is already "
                            "age/sex-specific (POP A.2); applying the "
                            "generator age-decline would double-count age"),
        "tolerance": TRAIT_RMSSD_TOLERANCE,
        "trait_echo": dict(traits),
    }
    prov["honesty_flags"] = sorted(set(prov.get("honesty_flags", []))
                                   | {TRAIT_HONESTY_FLAG})
    out["provenance"] = prov
    return out


def _to_hrv_config(config: dict | None):
    """Adapt the dataset-level config dict to W2-E's ``HRVConfig``.

    Integration seam (orchestrator): ``dataset`` passes plain dicts; the
    W2-E generator expects an ``HRVConfig`` dataclass.  Recognized keys:
    ``subject_params`` -> ``subject_params`` (explicit HRV-parameter
    overrides only), ``age_years``, ``fitness_rsa_gain``,
    ``ectopy_enabled``.  ``subject_traits`` is handled by
    ``generate_rr_series`` (trait calibration), NEVER mapped into
    subject_params (unknown keys would be silently ignored by the
    generator -- the review-F11 defect).  Unknown keys are ignored (never
    silently applied).
    """
    if config is None:
        return None
    from simulation.hrv import HRVConfig
    known = {}
    subj = config.get("subject_params")
    if subj is not None:
        known["subject_params"] = dict(subj)
    for key in ("age_years", "fitness_rsa_gain", "ectopy_enabled"):
        if key in config:
            known[key] = config[key]
    return HRVConfig(**known)


def _align_beats(out: dict) -> dict:
    """Length-align the W2-E output to the dataset/sensor convention.

    W2-E returns ``rr_intervals_ms`` with length N-1 (interval between
    beats i and i+1) while ``beat_times_s``/``beat_types`` have length N.
    The sensor device API requires aligned arrays where rr[i] is the
    interval STARTING at beat[i]; drop the final beat (no successor).
    """
    bt = np.asarray(out["beat_times_s"])
    rr = np.asarray(out["rr_intervals_ms"])
    types = np.asarray(out["beat_types"])
    if bt.size == rr.size:
        return out  # already aligned
    if bt.size == rr.size + 1:
        out["beat_times_s"] = bt[:-1]
        out["beat_types"] = types[:-1]
        return out
    raise ValueError(
        f"W2-E RR output shape mismatch: beats={bt.size} rr={rr.size}")


def _fallback_rr_series(hrv_inputs: dict, seed: int, config: dict | None = None) -> dict:
    """Deterministic beat series from the mean-HR trajectory.

    Beat times are the integer crossings of the cumulative beat phase
    ``phi(t) = integral HR(u)/60 du`` -- exact resampling of the mean
    trajectory, no added stochastic structure (documented limitation).
    """
    t = np.asarray(hrv_inputs["time_s"], dtype=float)
    hr = np.asarray(hrv_inputs["mean_hr_bpm"], dtype=float)
    if t.size < 2:
        raise ValueError("hrv_inputs too short for beat derivation")
    hr = np.clip(hr, 20.0, 240.0)
    # cumulative beat phase via trapezoid integration of HR/60 (Hz)
    phase = np.concatenate(([0.0], np.cumsum(0.5 * (hr[1:] + hr[:-1]) / 60.0
                                             * np.diff(t))))
    n_beats = int(np.floor(phase[-1]))
    if n_beats < 2:
        raise ValueError("mean-HR trajectory produced < 2 beats")
    beat_index = np.arange(1, n_beats + 1)
    beat_times = np.interp(beat_index, phase, t)
    rr_ms = np.diff(beat_times) * 1000.0
    # Align lengths: rr_intervals_ms[i] is the interval STARTING at
    # beat_times_s[i]; the final beat has no successor and is dropped so
    # beat_times_s / rr_intervals_ms / beat_types all have length n_beats-1
    # (the sensor device API requires aligned arrays).
    beat_times = beat_times[:-1]
    beat_types = np.full(len(beat_times), "normal")
    return {
        "beat_times_s": beat_times,
        "rr_intervals_ms": rr_ms,
        "beat_types": beat_types,
        "provenance": {
            "source": "fallback_mean_hr_phase_integration",
            "w2e_hrv_module_available": False,
            "w2e_import_error": _HRV_IMPORT_ERROR,
            "honesty_flags": list(FALLBACK_HONESTY_FLAGS),
            "limitations": [
                "no RSA / Mayer 0.1 Hz / 1-f fractal structure",
                "no ectopy (all beats labeled normal)",
                "RR series is a deterministic resampling of the engine "
                "mean-HR trajectory; short-term HRV metrics computed from "
                "it UNDERESTIMATE true variability",
            ],
            "config_echo": config or {},
        },
    }
