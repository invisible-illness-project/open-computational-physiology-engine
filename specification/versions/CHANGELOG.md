# OCPE Specification Changelog

All notable changes to the OCPE specification (schemas, identifier rules, core
vocabulary, compatibility rules). Engines and domain packages keep their own
version numbers.

## [0.1.0] — 2026-11-15 (provisional)

First release of OCPE as a standalone, language-independent computational
physiology interoperability engine: specification, reference implementation,
CLI and official conformance suite.

### Added
- Canonical identifier scheme `ocpe:<package>/<local-id>` with stability,
  deprecation and alias rules (`core/identifiers.md`).
- JSON Schema (draft-07) contracts for the entity kinds: concept, variable,
  latent_construct, derived_metric, measurement_method, model, relationship,
  predicate, functional_form; plus document, package manifest, evidence,
  reference, provenance and observation schemas.
- Observation exchange records with `value_kind` (measured/estimated/
  derived/simulated/self_reported), uncertainty fields, timestamps, method
  and model references.
- Evidence statements with reference-integrity enforcement (claims must cite
  registered bibliographic records) and provisional grading scales
  (`core/evidence-scales.yaml`).
- Context-qualified `reference_range` with an explicit `range_type`
  (reference_interval, plausibility_bound, clinical_threshold,
  model_validity_domain, observed_range).
- UCUM-based unit registry with dimensions and alternative-spelling
  normalization (`core/units.yaml`).
- `core` vocabulary package: 12 relationship predicates and 7 named
  functional forms.
- Package manifests with explicit dependencies, `ocpe_spec` compatibility
  ranges, maintainers and provenance.
- Machine-readable compatibility rules with a comprehensive, schema-aware
  change classification for `ocpe diff` (`versions/compatibility.yaml`),
  covering nested equations, symbols/parameters, relationship semantics,
  measurement semantics, evidence attachments and dependency constraints.
- Official conformance suite (`conformance/`): synthetic fixtures, expected
  results and language-independent test vectors.
- Optional governance extension: review-manifest schema (ADR 0001,
  manifest v2.0.0) with separable review, derived-summary and authorization
  layers.

### Scope
- OCPE owns the language, schemas, identifiers, semantic rules, reference
  implementation, conformance tests and interoperability interfaces.
- Physiological domain content (variables, relationships, disease
  definitions, models, devices, populations, literature, evidence records)
  is authored and versioned in external packages; the OCPE repository ships
  no such content.
