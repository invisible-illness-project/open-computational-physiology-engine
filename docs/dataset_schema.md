# OCPE Dataset Record Schema v0.1.0

Owner: `dataset/` (G-P0-07, Agent W2-F). Binding specification:
`docs/evidence_package/OCPE_DATASET_SPECIFICATION.md` and master prompt
sections 7/18/21. Governance: `validation/provenance_gate.py`,
`tools/kb_access.py`; metric semantics: `validation/evaluator.py` (G-P0-09
frozen); latent boundary: `sensor_models/boundary.py`.

## Dataset layout

```
<output_dir>/
  manifest.yaml              # machine-readable dataset manifest
  manifest_summary.txt       # human-readable one-page summary
  cohort.csv                 # one row per subject (demographics/traits/seeds)
  subjects/<subject_id>/<protocol_id>/
    ground_truth.npz         # LATENT physiology (ground truth ONLY, rule 3)
    sensors.npz              # raw observable sensor channels (per device)
    derived.json             # derived metrics (frozen evaluator semantics)
    record.yaml              # the record below
```

Determinism: same `dataset_seed` (+ identical KB/git state) produces
byte-identical outputs. `record_id` is uuid5 over the seed hierarchy;
`generation_timestamp` is a deterministic build clock (config-overridable);
npz zip entries use fixed timestamps; YAML/JSON are key-sorted with
normalized values. Seed hierarchy: `dataset_seed -> subject_seed ->
{engine, rr, sensor, event} seeds` (SHA-256 mixing, `dataset.cohort.stable_seed`).

## Record fields (record.yaml)

| field | content |
|---|---|
| `record_id` | uuid5(dataset_seed, subject_id, protocol_id) |
| `subject_id`, `protocol_id` | cohort/protocol identifiers |
| `physiological_state` | condition, phenotypes, severity, comorbidities (metadata only), demographics, protocol family |
| `events` | typed, timestamped events (tilt onset, meals/exercise/stress kernels) |
| `latent_parameters` | GROUND TRUTH ONLY: variable list + `ground_truth.npz` reference + population trait draws |
| `observable_parameters` | sensor channel declarations + boundary reference |
| `sensor_configuration` | devices: sensor_id, regime, seed, channels, KB profile provenance |
| `derived_metrics` | `derived.json` reference + metrics (orthostatic true/measured + reference comparison; HRV block) |
| `evidence` | rule-6 blocks: population constants consumed, perturbations (canonical/experimental split), RHR calibration, severity resample, pooling axis |
| `uncertainty` | per-constant uncertainty + calibration tolerances |
| `canonical_status` | `canonical` \| `experimental` |
| `honesty` | structured block, five mandatory categories (below) |
| `honesty_flags` | flat list = union of the five categories (validator-enforced) |
| `seed` + `seed_hierarchy` | subject seed + full derived-seed disclosure |
| `ocpe_commit` | git rev of the generating checkout |
| `kb_version` | SHA-256 of the KB bundle (incl. review sidecars) |
| `registry_version` | EVIDENCE_REGISTRY.yaml version + SHA-256 |
| `model_version` | mathematical_models.yaml version |
| `schema_version` | `0.1.0` |
| `generation_timestamp` | deterministic build clock |
| `hrv_source` | W2-E module vs fallback disclosure |
| `generation_mode`, `cohort_frame` | gate mode; population/clinic ascertainment frame |

## Honesty block (five mandatory categories)

Per OCPE_DATASET_SPECIFICATION section 0 and SWARM_SPEC rules 1/2/3, every
record flags, per category:

- `extrapolated_features` — e.g. `extrapolated_E0` engine flags,
  `rr_fallback_no_structured_hrv`, `hrv_structure_unresolved_E0`.
- `latent_only_variables` — declaration of the ground-truth-only variable
  names (never sensor channels).
- `experimental_features` — applied experimental perturbation parameters
  (MUST be empty in canonical records; validator-enforced).
- `weakly_evidenced_features` — tier-C/E0-E1 machinery actually consumed:
  `pooling_capacity_tierC_machine_fitted`,
  `severity_resampled_from_evidence_distribution`,
  `rhr_calibration_machine_fitted_tierC`,
  `subtype_mixture_weight_E0_scenario`, engineering-judgment couplings.
- `validation_limitations` — e.g. `short_protocol_sustained_window_proxy`,
  `prolonged_standing_approximated_as_extended_tilt`,
  `exercise_pem_channel_inactive_in_ode_runs`, hyperadrenergic/neuropathic
  disclosures.

## Validation hooks (importable; consumed by the L1 gate)

```python
from dataset.schema import (validate_record_schema,
                            validate_record_provenance,
                            validate_scientific_contract)
```

Each returns a list of error strings (empty = pass). The builder runs all
three on every record and refuses to write failing records (fail-closed
build CI). `validate_scientific_contract` includes the latent-boundary
guard end-to-end: no observable/derived channel name may match the sensor
boundary's latent blacklist.

## Mechanism-first cohort design (rules 4/5)

Between-condition separation comes from mechanism only:

- RHR trait ~ N(65.5, 7.7^2) (+3 bpm female) -> Hm controller floor via a
  documented machine-fitted calibration (pre-perturbation; tachycardia
  still emerges mechanistically).
- Healthy orthostatic axis: quantile draws from the frozen
  `healthy_reference.yaml` tails, mapped onto the venous-pooling axis
  (VMvl, 500-1000 mL) -- the realized response is ODE output, never a label.
- Hypovolemia severity: per-subject deficit ~ N(689, 270^2) mL (Raj 2005,
  EVD-POTS-004); the KB point -1000 mL extreme is never applied.
- Anti-laundering: the manifest reports realized group separation and
  overlap; >0.95 AUC trivial separability is a release failure.

## KB governance

Builds preflight through `preflight_dataset_build` and fail closed in
canonical mode. Dataset-level exclusions (G-P0-03): `neuropathic_pots` is
refused in canonical mode until the engine-falsification follow-ups land
(`dataset.runner.DATASET_EXCLUDED_PHENOTYPES`). Interim KB closure shim:
`dataset/kb_closure.py` (verbatim copies + fresh AI-agent reviews; the
four ungoverned wearable files are excluded and disclosed, never edited).
