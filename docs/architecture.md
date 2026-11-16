# OCPE Architecture

**OCPE is semantic infrastructure, not a simulator.** It is the common,
versioned, machine-readable language through which AI agents, researchers,
applications and datasets communicate physiological knowledge: what things
are, how they relate, what evidence supports the claims, and in which context
a number applies. It does not integrate equations, generate synthetic
patients, or synthesize signals. Those capabilities live in downstream
applications (MOSAIC and Lamina) that consume OCPE content. The scope
statement is in `docs/mission.md`; this document explains how the pieces fit
together and what each piece may depend on.

## System overview

```
   external domain packages (authored by researchers / AI agents /
   device vendors / anyone; versioned and distributed independently)
        │  e.g. a cardiovascular vocabulary, a disease model package,
        │  a wearable specification, a cohort definition
        ▼
┌───────────────────────────────────────────────────────────────┐
│  OCPE specification (normative, language-independent):        │
│  JSON Schemas (draft-07) · identifier grammar · unit registry │
│  · predicate & functional-form vocabularies · compatibility   │
│  rules · core package                                         │
└───────────────────────▲───────────────────────────────────────┘
                        │ reads and enforces
┌───────────────────────┴───────────────────────────────────────┐
│  reference engine (implementations/python):                   │
│  loader · validator · resolver · units · compatibility ·      │
│  versioning · conformance runner · CLI                        │
└───────────────────────▲───────────────────────────────────────┘
                        │ ocpe export / registry API
   downstream applications (consume, never part of OCPE):
     MOSAIC — numerical simulation, synthetic patients/cohorts
     Lamina — ECG/PPG/EDA signal processing, HRV computation
     datasets / analysis tools — observation exchange records
```

## The layers

### 1. Specification contracts (normative)

Everything in `specification/` is the contract every other layer conforms to.
The normative artifacts (`specification/core/meta.yaml`) are the JSON Schemas
in `specification/schemas/`, the identifier grammar
(`specification/core/identifiers.md`), the unit registry
(`specification/core/units.yaml`), the compatibility rules
(`specification/versions/compatibility.yaml`) and the versioning policy
(`docs/versioning-policy.md`). Informative companions describe the entity-kind
taxonomy (`core/kinds.yaml`), the predicate vocabulary and the functional
forms.

The specification is **language-independent**. The Python engine is a
reference implementation, not the definition; another language implementing
the same schemas, identifier rules and vector expectations is an equal
citizen (see `docs/implementation-guide.md`).

### 2. Reference engine (`implementations/python`)

A small, deterministic, dependency-light implementation:

- `loader` — discovers and loads packages (manifest + listed documents) into a
  registry. Enforces **path containment**: content paths must stay inside the
  package root (no absolute paths, no `..` traversal, no symlink escapes).
  Loading is data-only; OCPE **never executes code contained in a package**.
- `validator` — two layers. Schema validation against the JSON Schemas;
  semantic validation of identifier namespaces, cross-package references,
  dependency declarations, units and dimensions, predicate/functional-form
  vocabulary, alias collisions, ranges, deprecation, observation semantics
  and **evidence reference integrity** (claims must cite registered
  bibliographic records).
- `resolver` — canonical CURIEs, model `#symbol` fragments, scoped aliases,
  labels, predicate/functional-form tokens; ambiguity is an error, never a
  guess.
- `units` — registry-driven unit normalization and dimensional checks
  (explicit UCUM-code registry, not a full UCUM parser).
- `compatibility` — schema-aware, order-insensitive deep diffing of two
  releases of a package: nested equations, symbols/parameters, relationship
  semantics, reference ranges, evidence attachments and dependency
  declarations are all compared, and each change is classified
  (major/minor/patch) via `specification/versions/compatibility.yaml`.
- `versioning` — semantic versions and constraint satisfaction.
- `vectors` — executes the language-independent conformance vectors and the
  fixture expectations under `conformance/`.

### 3. External domain packages (not in this repository)

Domain content — variables, relationships, disease definitions, models,
device specifications, populations, evidence — is authored and versioned in
packages whose `id` doubles as their CURIE namespace. Packages declare
dependencies on other packages and an `ocpe_spec` compatibility range. The
engine loads only the packages it is given plus the bundled `core`
vocabulary; there is no default domain content.

### 4. Downstream applications

MOSAIC and Lamina consume OCPE content through the registry/export API and
the observation exchange contract; they never become part of OCPE. Their
integration boundaries are documented in `docs/mosaic-integration.md` and
`docs/lamina-integration.md`.

## Design constraints

- **Deterministic.** Same inputs → same reports; no network access, no
  clocks, no randomness in validation.
- **Lightweight.** Runtime dependencies: PyYAML and jsonschema only. No
  scientific stack.
- **Safe for untrusted content.** Packages are data. The loader refuses path
  escapes; nothing in a package is ever executed or imported.
- **Model-agnostic.** The engine validates model *specifications*; numerical
  execution is explicitly out of scope.
- **Structural ≠ scientific.** Validation output always carries the scope
  disclaimer.

<!-- Copyright 2026 The Invisible Illness Project. SPDX-License-Identifier: Apache-2.0. See LICENSE in the repository root. -->
