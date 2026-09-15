"""Sensor boundary contract (Global rule 3).

Defines exactly which physiology may cross from the engine into the sensor
layer, and which latent variables must never appear as sensor inputs or
channels. Latent physiology is ground truth only; sensors receive *observable*
quantities (RR intervals, pulse waveform, EDA drive, skin temperature,
respiration, IMU/activity state) and emit noisy measurement channels.

Enforcement is two-layered:
  1. Runtime: :func:`validate_sensor_inputs` rejects any input mapping whose
     keys are not whitelisted observables or that match a forbidden latent
     variable name.
  2. Static: ``tests/test_sensor_realism.py`` scans every ``sensor_models``
     source file and asserts no forbidden latent identifier appears outside
     this registry module.

Evidence: docs/evidence_package/WEARABLE_OBSERVABILITY_EVIDENCE.md §(d)
("Latent variables that must NEVER emit a direct wearable signal").
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Whitelist: observable physiology that may cross the sensor boundary.
# ---------------------------------------------------------------------------
OBSERVABLE_INPUT_KEYS = frozenset({
    # time base
    "time_s", "clock_time_s",
    # cardiac timing (from engine HRV/RR output or a generic beat series)
    "rr_intervals_ms", "beat_times_s",
    # ectopy hook for the W2 HRV module: per-beat class labels
    # ("normal"/"ectopic"); labels only, never latent hemodynamics
    "beat_types",
    # normalized peripheral pulse waveform (unitless, e.g. 0..1 blood-volume
    # pulse); the engine side must normalize latent pressure/volume into this
    # observable-proxy form BEFORE crossing the boundary
    "pulse_waveform", "pulse_waveform_times_s",
    # electrodermal drive: sudomotor (skin sympathetic cholinergic) drive,
    # unitless 0..1, plus discrete SCR event times/amplitudes
    "eda_drive", "eda_event_times_s", "eda_event_amplitudes_us",
    # temperatures actually measurable at the skin surface / environment
    "skin_temperature_c", "ambient_temperature_c",
    # respiration as an observable waveform/rate (belt/PPG-derived surrogate)
    "respiration_waveform", "respiration_rate_hz",
    # motion: IMU acceleration and activity context
    "acceleration_g", "activity_state", "activity_intensity", "cadence_hz",
    # wear/context state
    "on_body", "is_night", "sleep_state", "fit_state",
    # perfusion/vasomotor drive (unitless 0..1 mechanism coupling that scales
    # optical signal amplitude; an input *drive*, not a latent readout)
    "perfusion_drive",
})

# ---------------------------------------------------------------------------
# Blacklist: latent physiology (ground truth only, never a sensor channel).
# Names are matched exactly and as word-boundary substrings of input keys.
# Source: WEARABLE_OBSERVABILITY_EVIDENCE.md §(d).1 + SWARM_SPEC global rule 3.
# ---------------------------------------------------------------------------
LATENT_FORBIDDEN_NAMES = frozenset({
    "blood_pressure_absolute", "blood_pressure", "arterial_pressure",
    "sbp", "dbp", "systolic", "diastolic",
    "stroke_volume", "cardiac_output",
    "svr", "systemic_vascular_resistance",
    "venous_pooling", "venous_return",
    "core_temperature", "cerebral_perfusion",
    "hydration", "insulin", "glucose",
    "baroreflex_sensitivity", "brs",
    # latent model states of the engine's cardiovascular formulation
    "pau", "pal", "pvu", "vau", "val", "vvu", "vvl",
    "pem_episode", "psychological_stress",
})

# CGM glucose is the single sanctioned exception (minimally invasive enzymatic
# CGM is a direct measurement; WEARABLE_OBSERVABILITY_EVIDENCE.md row M1).
LATENT_ALLOWED_EXCEPTIONS = frozenset({"cgm_glucose"})


class LatentVariableViolation(ValueError):
    """Raised when latent physiology is presented to the sensor layer."""


class UnknownSensorInput(ValueError):
    """Raised when an input key is not a whitelisted observable."""


def _matches_forbidden(key: str) -> str | None:
    """Return the forbidden latent name matched by ``key``, or None."""
    k = key.lower()
    if k in LATENT_ALLOWED_EXCEPTIONS:
        return None
    for name in LATENT_FORBIDDEN_NAMES:
        if k == name:
            return name
        # word-boundary substring match (e.g. "mean_blood_pressure_trace")
        if len(name) >= 4 and (
            k.startswith(name + "_") or k.endswith("_" + name) or ("_" + name + "_") in k
        ):
            return name
    return None


def validate_sensor_inputs(inputs: dict, *, strict: bool = True) -> dict:
    """Validate a mapping of physiology inputs destined for the sensor layer.

    Raises
    ------
    LatentVariableViolation
        If any key matches a forbidden latent variable name.
    UnknownSensorInput
        If ``strict`` and any key is not in :data:`OBSERVABLE_INPUT_KEYS`.
    """
    for key in inputs:
        if not isinstance(key, str):
            raise UnknownSensorInput(f"sensor input keys must be strings, got {type(key)!r}")
        hit = _matches_forbidden(key)
        if hit is not None:
            raise LatentVariableViolation(
                f"latent variable '{hit}' (key '{key}') may not cross the sensor "
                "boundary (SWARM_SPEC global rule 3; WEARABLE_OBSERVABILITY "
                "EVIDENCE §d.1). Latent physiology is ground truth only."
            )
        if strict and key not in OBSERVABLE_INPUT_KEYS:
            raise UnknownSensorInput(
                f"'{key}' is not a whitelisted observable sensor input. Allowed: "
                f"{sorted(OBSERVABLE_INPUT_KEYS)}"
            )
    return inputs
