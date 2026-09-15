"""OCPE synthetic dataset generation infrastructure (G-P0-07, Agent W2-F).

Top-level package owning cohort sampling, protocol scheduling, batch
execution, record schema, and dataset manifests for the OCPE synthetic
multimodal wearable dataset (docs/evidence_package/OCPE_DATASET_SPECIFICATION.md).

Binding contracts consumed (do not re-implement):
  * simulation/engine.py          -- ODE core + get_hrv_inputs() (W2 contract)
  * simulation/hrv.py             -- W2-E structured HRV (via dataset.rr_source)
  * validation/provenance_gate.py -- fail-closed build preflight (G-P0-08/10)
  * validation/evaluator.py       -- frozen orthostatic metric semantics (G-P0-09)
  * sensor_models/                -- KB-driven device models + boundary guard
  * tools/kb_access.py            -- governed KB view (canonical/experimental)

Global rules (SWARM_SPEC): latent physiology is ground truth only (rule 3);
no disease-label signal hacks (rule 4); between-condition separation must
come from mechanism only and stay inside evidence-honest bands (rule 5);
every scientific constant carries value/units/distribution/tier/source/
status/uncertainty (rule 6) -- see dataset.population_evidence.
"""

from dataset.cohort import CohortSampler, Subject, load_cohort_config
from dataset.protocols import ProtocolSpec, load_protocol_config
from dataset.runner import DatasetBuilder, BuildResult
from dataset.schema import (
    SCHEMA_VERSION,
    validate_record_schema,
    validate_record_provenance,
    validate_scientific_contract,
)
from dataset.manifest import build_manifest, write_manifest

__all__ = [
    "CohortSampler", "Subject", "load_cohort_config",
    "ProtocolSpec", "load_protocol_config",
    "DatasetBuilder", "BuildResult",
    "SCHEMA_VERSION",
    "validate_record_schema", "validate_record_provenance",
    "validate_scientific_contract",
    "build_manifest", "write_manifest",
]
