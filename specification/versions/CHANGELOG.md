# OCPE Specification Changelog

All notable changes to the OCPE specification (schemas, identifier rules, core
vocabulary). Domain packages and the Python reference implementation keep their
own changelogs and version numbers.

## [0.1.0] — 2026-11-14 (provisional)

First versioned release of OCPE as a specification and semantic interoperability
engine. It replaces the pre-0.1 monolithic simulation repository, which is
preserved at git tag `pre-architectural-refactor`.

### Added
- Canonical identifier scheme `ocpe:<package>/<local-id>` with stability,
  deprecation and alias rules (`core/identifiers.md`).
- JSON Schema (draft-07) contracts for all entity kinds: concept, variable,
  latent_construct, derived_metric, measurement_method, condition, intervention,
  population, model, relationship, predicate, functional_form; plus document,
  package manifest, evidence, reference, provenance and observation schemas.
- Context-qualified `reference_range` with an explicit `range_type`
  (reference_interval, plausibility_bound, clinical_threshold,
  model_validity_domain, observed_range).
- UCUM-based unit registry with dimensions and legacy-spelling mapping
  (`core/units.yaml`).
- Core package `core` with the predicate vocabulary (12 predicates, unchanged from
  legacy v3.2) and registered functional forms. This closes the legacy gap where
  `sigmoid_hill`, `gravity_hydrostatic`, `inverse_proportional` and
  `inverse_nonlinear` were used but never registered.
- Package manifests with explicit `dependencies` and an `ocpe_spec` compatibility
  range.
- Optional governance extension: review-manifest schema (ADR 0001 manifest v2.0.0),
  with separable review, derived-summary and authorization layers.

### Changed (relative to the pre-0.1 knowledge base)
- Evidence is an attached statement (`evidence.schema.json`), separate from the
  review workflow.
- Legacy `evidence_level` / `evidence_tier` values are preserved verbatim. Their
  definitions are recorded as provisional in `core/evidence-scales.yaml`.

### Removed from scope
- Numerical simulation, synthetic data generation and signal synthesis. See
  `migration_archive/MIGRATION_NOTES.md`.
