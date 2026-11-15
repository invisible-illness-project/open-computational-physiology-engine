# Migration Guide — Pre-0.1 Knowledge Base → OCPE 0.1 Packages

This guide maps every pre-0.1 artifact (retrievable verbatim at git tag
`pre-architectural-refactor`, commit `c0d8678`) to its OCPE 0.1 location.
Scientific content was transcribed **verbatim** — values, citations, evidence
levels/tiers, review statuses and correction notes are preserved, not
re-graded. See `migration_archive/MIGRATION_NOTES.md` for components that left
the repository entirely (simulation, sensors, results).

## Knowledge base YAML → packages

| Pre-0.1 file | OCPE 0.1 location | Transformation |
|---|---|---|
| `physiology/variables.yaml` (27 entries) | `packages/cardiovascular/variables.yaml` (25 variables) + `packages/autonomic/metrics.yaml` | `Hc`+`HR` merged into one `heart-rate` variable with unit-qualified aliases (`/s` and `/min`); `DFA_a1` reclassified as a derived metric; `valid_range` → context-qualified `plausibility_bound` ranges; symbols → `legacy-kb` aliases |
| `physiology/latent_states.yaml` (14 entries) | `packages/autonomic/latent.yaml` (6 constructs), `packages/systemic/latent.yaml` (4), `packages/cardiovascular/variables.yaml` (4) | Items measurable in principle (total blood volume, vascular compliance, cardiac contractility, peripheral resistance) reclassified as **variables** per the kind taxonomy; the rest became **latent constructs** with normalized scales |
| `ontology/concepts.yaml` (17 classes) | `specification/core/kinds.yaml` + JSON Schemas | The class taxonomy became the entity-kind system; per-class disposition recorded in `kinds.yaml:legacy_concept_classes` |
| `ontology/relationships.yaml` (v3.2, 8 edges) | relationship entities distributed by subject ownership across `packages/cardiovascular`, `packages/autonomic`, `packages/systemic`, `packages/conditions/pots` | Cycle-3 corrections preserved verbatim; `supporting_publications` → evidence objects; `applicable_populations` → context-qualified `applicable_contexts` |
| `ontology/mechanistic_links.yaml` (7 links) | `packages/models/baroreflex-geddes-2022/relationships.yaml` (6) + `packages/autonomic/relationships.yaml` (1) | `type` → registered functional forms (closing the registry gap); `mathematical_ref` → canonical model+equation pointers |
| `diseases/pots.yaml` (v1.5) | `packages/conditions/pots/` (independently versioned) | disease → condition; phenotypes → phenotype conditions; `parameters_perturbed`/`unverified_parameters` → `parameter_perturbations`/`unverified_parameter_perturbations`; `compliance_guard`/`venomotor_note` → `constraints`; `validation_criteria` preserved |
| `diseases/eds.yaml` (v1.2) | `packages/conditions/eds/` | same pattern |
| `diseases/mecfs.yaml` (v1.1) | `packages/conditions/mecfs/` | same pattern |
| `diseases/autoimmune.yaml` (v1.1) | `packages/conditions/autoimmune/` | same pattern |
| `diseases/heat.yaml` (v1.1) | `packages/conditions/heat/` | exposure condition |
| `diseases/poor_sleep.yaml` (v1.1) | `packages/conditions/poor-sleep/` | `unresolved_gaps` preserved as formatted strings |
| `diseases/medication.yaml` (v1.1) | `packages/interventions/medication/` | legacy `phenotypes` became **pharmacological intervention** entities |
| `interventions/tilt_test.yaml` | `packages/interventions/tilt-test/` | flat protocol fields → `protocol.phases` |
| `wearables/polar_h10.yaml` | `packages/wearables/polar-h10.yaml` | sensor → `measurement_method`; validation rows → context-qualified performance |
| `wearables/photoplethysmography.yaml` | `packages/wearables/photoplethysmography.yaml` | as above; its uncited validation figures are flagged with an explicit provenance gap |
| `populations/cohorts.yaml` | `packages/populations/` | cohorts → **population context descriptors** (not generators) |
| `equations/definitions.yaml` + `equations/mathematical_models.yaml` | `packages/models/baroreflex-geddes-2022/baroreflex-geddes-2022.yaml` | merged into one model specification: 24 equations with structured I/O; parameter table → symbols with nominal values + provenance. Legacy per-parameter `phenotypes` sub-tables (v1.0) were **superseded** by the newer-curated condition packages and are not duplicated (recoverable from git history) |
| `publications/*.md` | `evidence/references/*.md` | moved verbatim |
| `*.review.yaml` sidecars | alongside their migrated asset | paths + SHA-256 updated; a migration review event appended; full review history preserved |

## Identifier changes

- Canonical identifiers are now `ocpe:<package>/<local-id>` CURIEs, e.g.
  `ocpe:cardiovascular/heart-rate`, `ocpe:conditions.pots/neuropathic-pots`.
- Every legacy symbol (`Hc`, `pcm`, `RalpM`, ...) and every legacy phenotype id
  (`neuropathic_pots`, `beta_blocker`, ...) is registered as a `legacy-kb`
  alias, so old content resolves:
  `ocpe resolve Hc --scope legacy-kb` → `ocpe:cardiovascular/heart-rate`.
- Legacy namespace-free ids in `mathematical_models.yaml` (e.g.
  `models/mathematical_models.yaml#heart_rate_control`) became
  model+equation pointers (`mathematical_specification.equations`).

## Behavioral changes to note

- **Unverified perturbations are consumer-inert** (same semantics as the old
  `unverified_parameters` block): applications must not apply
  `unverified_parameter_perturbations` unless explicitly opted in.
- **Registry gaps closed**: `RMSSD` and the RR interval are registered; the
  four mechanistic-link functional forms are registered.
- The old `validate_kb.py` and `tools/ocpe.py` are gone; use
  `ocpe validate packages/` and the `ocpe` CLI.
- Reference ranges in variable entities are **plausibility bounds** from the
  legacy `valid_range` fields — engineering bounds, not population reference
  intervals (stated in each range's `context.scope_note`).
