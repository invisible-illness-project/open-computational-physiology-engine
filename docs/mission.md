# OCPE Mission

**OCPE is an open, versioned computational physiology interoperability
engine.** It defines the common language, schemas, identifiers, semantic
contracts and validation mechanisms through which:

- AI agents represent physiological knowledge.
- Researchers exchange structured physiological information.
- Computational models declare their interfaces and assumptions.
- Applications exchange physiological observations.
- Datasets describe physiological measurements.
- Independent software implementations interpret physiological specifications
  consistently.

OCPE defines **how physiological information is represented and interpreted**.
It does not own or curate the specific research content represented using that
language.

## The fundamental architectural principle

> Separate the infrastructure for representing knowledge from the knowledge itself.

**OCPE owns:** the language, the specification, the schemas, the identifiers,
the semantic rules, the reference implementation, the conformance tests and
the interoperability interfaces.

**External projects own:** physiological research, disease definitions,
disease-specific relationships, physiological equations and models, clinical
protocols, wearable-device specifications, population and cohort definitions,
literature reviews, evidence claims and dataset-specific definitions.

A researcher can create a new physiological domain package **without
modifying OCPE**. An AI agent can produce an OCPE-compatible package
**without merging it into the OCPE repository**.

## What OCPE provides

1. **A canonical physiological language.** Stable identifiers
   (`ocpe:<package>/<local-id>`, spec: `specification/core/identifiers.md`),
   aliases, deprecation rules and provenance metadata.
2. **Common data and specification schemas** (JSON Schema, draft-07):
   concepts, physiological variables, latent constructs, derived metrics,
   measurement methods, relationships, computational model specifications,
   units and dimensions, evidence claims, bibliographic references, package
   manifests and observation exchange records. Schemas define the *structure
   and meaning* of information; they never implement physiological
   computation.
3. **A semantic engine** (the Python reference implementation): package
   discovery and loading, schema validation, semantic validation, identifier
   and alias resolution, unit/dimensional checks, cross-package reference
   validation, observation validation, model-spec validation, evidence
   reference integrity, version compatibility, dependency resolution,
   migrations and conformance reporting.
4. **An official conformance suite** (`conformance/`) with synthetic fixtures
   and language-independent test vectors so implementations in any language
   can demonstrate consistent behavior.
5. **An optional, separable governance extension** (ADR 0001) whose review
   workflows and authorization policies are not required to load, validate or
   resolve OCPE content.

## Explicit non-goals

OCPE is a **small core**. It is not a comprehensive biomedical ontology, and
it does not prepopulate cardiovascular, autonomic, respiratory or neurological
physiology; no disease definitions (POTS, EDS, ME/CFS, Long COVID, MCAS); no
wearable-device catalogs; no population registries; no literature database.
All of that is external domain content. The core defines generic entity types
and relationship predicates only.

OCPE does not execute models, simulate physiology, generate synthetic data or
process signals.

## Principles

1. **Structural validation is not scientific validation.** Every validator
   output carries this disclaimer; no green checkmark asserts biological truth.
2. **Evidence is attached to specific aspects** (existence, direction,
   magnitude, ...). Direction-level evidence must never be read as
   magnitude-level support.
3. **Context-qualification.** Reference ranges, sensor accuracy and evidence
   apply to stated populations, postures, activities and methods; they do not
   transfer silently.
4. **Identifier permanence.** Identifiers never change meaning and are never
   reused; retirement happens via deprecation, not deletion.
5. **Small, stable core; independently versioned domain packages.** Domains
   evolve at their own pace without destabilizing the language.
6. **Safe to consume untrusted content.** Package loading is data-only:
   path-containment enforced, no code execution, deterministic behavior.
7. **The architectural test.** Does a component help represent, interpret,
   validate, exchange or version physiological knowledge? If not, it belongs
   in a downstream application, not in OCPE.

## Downstream integration

| Capability | Home |
|---|---|
| Physiological simulation, disease-specific models, patient/cohort generation, synthetic datasets, sensor simulation | MOSAIC (consumes OCPE identifiers, schemas, packages) |
| ECG/PPG/EDA/respiration processing, HRV computation, signal quality assessment | Lamina (produces OCPE observation records) |

See `docs/mosaic-integration.md` and `docs/lamina-integration.md`.
