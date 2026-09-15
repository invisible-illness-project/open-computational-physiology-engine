"""Record schema + importable validation hooks (G-P0-07 build items 4 & 7).

Record fields per master prompt section 18/21 (bound by
docs/evidence_package/OCPE_DATASET_SPECIFICATION.md sections 0, 1, 4):

    record_id, subject_id, protocol_id, physiological_state, events,
    latent_parameters (GROUND TRUTH only), observable_parameters,
    sensor_configuration, derived_metrics, evidence, uncertainty,
    canonical_status, honesty_flags, seed, ocpe_commit, kb_version,
    registry_version, model_version, generation_timestamp,
    schema_version.

Honesty metadata MUST flag (OCPE_DATASET_SPECIFICATION section 0 +
SWARM_SPEC global rules 1/2/3): extrapolated features, latent-only
variables, experimental features, weakly evidenced features, validation
limitations.  The record carries a structured ``honesty`` block with
these five categories; the flat ``honesty_flags`` list is the union.

Three importable validation hooks (the L1 gate consumes these):

    validate_record_schema(record)          -> structural errors
    validate_record_provenance(record)      -> provenance errors
    validate_scientific_contract(record)    -> scientific-contract errors
        (latent-boundary guard end-to-end + honesty categories + metric
        semantics wiring)

Determinism: ``normalize`` maps numpy types, tuples, NaN/inf to
serialization-stable Python values; ``record_id`` is uuid5 over the seed
hierarchy; ``generation_timestamp`` defaults to a deterministic build
clock derived from the dataset seed (never wall time) so identical seeds
produce byte-identical records.
"""

from __future__ import annotations

import datetime
import math
import uuid
from typing import Any, Dict, Iterable, List

import numpy as np

from tools.kb_access import CANONICAL, EXPERIMENTAL

SCHEMA_VERSION = "0.1.0"
RECORD_UUID_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "https://ocpe.org/dataset/record")

#: Required top-level record fields (master prompt section 18/21).
REQUIRED_FIELDS = (
    "record_id", "subject_id", "protocol_id", "physiological_state",
    "events", "latent_parameters", "observable_parameters",
    "sensor_configuration", "derived_metrics", "evidence", "uncertainty",
    "canonical_status", "honesty_flags", "honesty", "seed", "ocpe_commit",
    "kb_version", "registry_version", "model_version", "schema_version",
    "generation_timestamp",
)

#: Mandatory honesty categories (OCPE_DATASET_SPECIFICATION section 0).
HONESTY_CATEGORIES = (
    "extrapolated_features",
    "latent_only_variables",
    "experimental_features",
    "weakly_evidenced_features",
    "validation_limitations",
)

#: Ground-truth-only variable names that must never appear as
#: observable/sensor/derived channels (rule 3; mirrored against
#: sensor_models.boundary at validation time).
LATENT_GROUND_TRUTH_VARIABLES = [
    "time_s", "pau_mmHg", "pal_mmHg", "pvu_mmHg", "pcm_mmHg",
    "Vau_ml", "Vvu_ml", "Val_ml", "Vvl_ml", "Vlv_ml", "Vvm_ml", "Vsr_ml",
    "Hc_bps", "left_ventricular_pressure_mmHg", "aortic_flow", "mitral_flow",
    "sympathetic_tone", "parasympathetic_tone", "baroreflex_gain",
    "blood_volume_ml", "hydration", "stress_load", "inflammatory_burden",
    "metabolic_reserve", "hormonal_state", "autonomic_recovery_capacity",
    "sleep_pressure", "circadian_drive",
    "fatigue", "brain_fog", "pain", "orthostatic_intolerance",
    "palpitations", "sleepiness", "dizziness",
]


def make_record_id(dataset_seed: int, subject_id: str, protocol_id: str) -> str:
    """Deterministic record id (uuid5 over the seed hierarchy)."""
    return str(uuid.uuid5(
        RECORD_UUID_NAMESPACE, f"{dataset_seed}:{subject_id}:{protocol_id}"))


def deterministic_build_timestamp(dataset_seed: int) -> str:
    """Deterministic generation timestamp: fixed epoch + seed seconds.

    Byte-identical reruns require a build clock that depends only on the
    seeds; a config-supplied ``generation_timestamp`` overrides this.
    """
    base = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
    return (base + datetime.timedelta(seconds=int(dataset_seed))).isoformat()


def normalize(obj: Any) -> Any:
    """Recursively map to serialization-stable Python values.

    numpy scalars/arrays -> Python; tuples -> lists; NaN/inf -> None;
    dict keys stringified.  Required for byte-identical YAML/JSON output.
    """
    if isinstance(obj, dict):
        return {str(k): normalize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [normalize(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return normalize(obj.tolist())
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        obj = float(obj)
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


# ---------------------------------------------------------------------------
# Validation hooks (L1 gate)
# ---------------------------------------------------------------------------

def validate_record_schema(record: Dict[str, Any]) -> List[str]:
    """Structural validation of one record. Returns a list of errors."""
    errors: List[str] = []
    for f in REQUIRED_FIELDS:
        if f not in record:
            errors.append(f"missing required field '{f}'")
    if errors:
        return errors

    if not isinstance(record["record_id"], str) or not record["record_id"]:
        errors.append("record_id must be a non-empty string")
    if record["canonical_status"] not in (CANONICAL, EXPERIMENTAL):
        errors.append(f"canonical_status must be one of "
                      f"({CANONICAL}, {EXPERIMENTAL})")
    if not isinstance(record["events"], list):
        errors.append("events must be a list")
    if not isinstance(record["honesty_flags"], list):
        errors.append("honesty_flags must be a list")
    honesty = record.get("honesty", {})
    if not isinstance(honesty, dict):
        errors.append("honesty must be a dict of category -> flag list")
    else:
        for cat in HONESTY_CATEGORIES:
            if cat not in honesty:
                errors.append(f"honesty block missing category '{cat}'")
            elif not isinstance(honesty[cat], list):
                errors.append(f"honesty['{cat}'] must be a list")
    lat = record.get("latent_parameters", {})
    if not isinstance(lat, dict) or "variables" not in lat:
        errors.append("latent_parameters must declare its ground-truth variables")
    obs = record.get("observable_parameters", {})
    if not isinstance(obs, dict) or "channels" not in obs:
        errors.append("observable_parameters must declare its channels")
    sc = record.get("sensor_configuration", {})
    if not isinstance(sc, dict) or "devices" not in sc:
        errors.append("sensor_configuration must declare devices")
    dm = record.get("derived_metrics", {})
    if not isinstance(dm, dict) or "metrics" not in dm:
        errors.append("derived_metrics must carry a metrics mapping")
    for key in ("seed",):
        if not isinstance(record[key], int):
            errors.append(f"{key} must be an integer")
    return errors


def validate_record_provenance(record: Dict[str, Any]) -> List[str]:
    """Provenance validation of one record. Returns a list of errors."""
    errors: List[str] = []
    oc = record.get("ocpe_commit")
    if not isinstance(oc, str) or len(oc) < 7 or oc == "unknown":
        errors.append("ocpe_commit missing or malformed (git rev required)")
    kbv = record.get("kb_version")
    if not isinstance(kbv, str) or len(kbv) != 64:
        errors.append("kb_version must be a 64-hex SHA-256 of the KB bundle")
    rv = record.get("registry_version")
    if not isinstance(rv, dict) or not rv.get("sha256"):
        errors.append("registry_version must carry the EVIDENCE_REGISTRY sha256")
    if not record.get("model_version"):
        errors.append("model_version missing")
    if not record.get("generation_timestamp"):
        errors.append("generation_timestamp missing")
    ev = record.get("evidence", {})
    if not isinstance(ev, dict):
        errors.append("evidence block must be a dict")
    else:
        if "population_constants" not in ev:
            errors.append("evidence.population_constants missing (rule 6)")
        if "perturbations" not in ev:
            errors.append("evidence.perturbations missing (canonical/experimental split)")
    return errors


def _latent_name_hit(name: str) -> str | None:
    """Word-boundary match against the sensor boundary's latent blacklist."""
    from sensor_models.boundary import (
        LATENT_ALLOWED_EXCEPTIONS,
        LATENT_FORBIDDEN_NAMES,
    )
    k = str(name).lower()
    if k in LATENT_ALLOWED_EXCEPTIONS:
        return None
    for forbidden in LATENT_FORBIDDEN_NAMES:
        if k == forbidden:
            return forbidden
        if len(forbidden) >= 4 and (
            k.startswith(forbidden + "_") or k.endswith("_" + forbidden)
            or ("_" + forbidden + "_") in k
        ):
            return forbidden
    return None


def _iter_channel_names(record: Dict[str, Any]) -> Iterable[str]:
    obs = record.get("observable_parameters", {}) or {}
    for ch in obs.get("channels", []) or []:
        if isinstance(ch, dict):
            yield str(ch.get("name", ""))
        else:
            yield str(ch)
    dm = record.get("derived_metrics", {}) or {}
    for name in (dm.get("metrics", {}) or {}).keys():
        yield str(name)


def validate_scientific_contract(record: Dict[str, Any]) -> List[str]:
    """Scientific-contract validation (L1 gate end-to-end guard).

    1. Latent-boundary guard: no sensor/derived channel name may match the
       sensor boundary's latent blacklist (rule 3) -- checked on the RECORD
       (channel declarations), complementing the runtime boundary guard.
    2. Honesty categories all present and the flat flag list equals the
       union of categorized flags.
    3. Canonical records carry no experimental flags/content.
    4. Orthostatic derived metrics declare the frozen evaluator semantics.
    """
    errors: List[str] = []

    for name in _iter_channel_names(record):
        hit = _latent_name_hit(name)
        if hit is not None:
            errors.append(
                f"latent variable '{hit}' leaked into observable/derived "
                f"channel '{name}' (rule 3; latent = ground truth only)")

    honesty = record.get("honesty", {}) or {}
    union = sorted({f for cat in HONESTY_CATEGORIES for f in honesty.get(cat, [])})
    flat = sorted(set(record.get("honesty_flags", []) or []))
    if union != flat:
        errors.append("honesty_flags must equal the union of honesty categories "
                      f"(missing: {sorted(set(union) ^ set(flat))})")

    if record.get("canonical_status") == CANONICAL:
        exp = honesty.get("experimental_features", [])
        if exp:
            errors.append(f"canonical record carries experimental features: {exp}")

    dm = record.get("derived_metrics", {}) or {}
    metrics = dm.get("metrics", {}) or {}
    ortho = metrics.get("orthostatic")
    if ortho is not None:
        sem = ortho.get("semantics", {})
        if sem.get("sustained_delta_HR") is None or sem.get("source") is None:
            errors.append("orthostatic derived metrics must declare the frozen "
                          "evaluator semantics (sustained_delta_HR + source)")
        if ortho.get("sustained_window_kind") not in (
                "minutes_5_10", "short_protocol_proxy", "unresolved", None):
            errors.append("orthostatic.sustained_window_kind must be the "
                          "evaluator's window kind")
    return errors
