# OCPE Package Authoring Guide

How to author an **external, independently versioned OCPE domain package**.
OCPE owns the language; you own the content. Your package is a directory (or
repository) with a manifest and some documents — no OCPE code, no changes to
the OCPE repository, no review gate.

Everything here is validated by `ocpe validate <your-package>` (schema +
semantic layers). Validation is structural: a clean report means
well-formed, consistent, resolvable content — never scientific truth.

## Directory layout

```
my-package/
├── package.yaml          # required manifest
├── variables.yaml        # documents listed in manifest contents, any names
├── relationships.yaml
├── references.yaml       # optional: bibliographic records
└── CHANGELOG.md          # optional; recommended
```

The package id (`my-package`, kebab-case, dot-separated segments allowed) is
also the CURIE namespace of every entity you define:
`ocpe:my-package/<local-id>`.

## The package.yaml manifest

```yaml
id: my-package
name: My Physiology Package
version: "1.0.0"
ocpe_spec: ">=0.1.0 <0.2.0"
description: What this package contains and who it is for.
license: MIT                      # SPDX expression, or UNSPECIFIED
maintainers:
  - name: Jane Researcher
    kind: human
  - name: agent-42
    kind: ai_agent
contents:
  - variables.yaml
  - relationships.yaml
```

- `version` is semver and this package's releases are versioned
  **independently** of OCPE and of every other package.
- `ocpe_spec` constrains the specification versions your package conforms to.
  While OCPE is 0.1.x, pin the minor: `>=0.1.0 <0.2.0`.
- `contents` lists package-relative document paths. Paths are
  security-checked: absolute paths, `..` traversal and symlink escapes are
  rejected at load time.

### Dependencies and version constraints

Declare every package whose identifiers you reference:

```yaml
dependencies:
  - {package: other-package, version: ">=1.0.0 <2.0.0", reason: shared quantities}
optional_dependencies:
  - {package: nice-to-have, version: "^1.2.0"}
```

References to undeclared packages are validation errors. Constraints use the
OCPE grammar: `>=`, `>`, `<=`, `<`, `=`, `^`, `~`, combined with AND;
alternatives separated by `||`. `^1.2.3` := `>=1.2.3 <2.0.0`; `^0.2.3` :=
`>=0.2.3 <0.3.0` (pre-1.0 caret pins the minor); `~1.2.3` := `>=1.2.3
<1.3.0`. The `core` vocabulary package never needs to be declared.

Self-dependencies are errors; the dependency graph must be acyclic.

## Documents: envelope and contents

```yaml
ocpe: "0.1"
package: my-package
title: Variables
entities:
  - { ... }
references:
  - { ... }
```

`ocpe` is the document marker for specification 0.1.x; `package` must equal
your manifest id. A document holds `entities` (discriminated by `kind`) and/or
bibliographic `references`. Every entity needs `id`, `kind`, `label`.

## Choosing the entity kind

The kinds are **not interchangeable** (`specification/core/kinds.yaml` has
the deciding tests):

| Use | When |
|---|---|
| `concept` | No unit, no value: a system, structure, process, mechanism, phenomenon. |
| `variable` | A quantity measurable in principle, independent of method and value. |
| `latent_construct` | Not observable even in principle; values are always model/indicator-conditional estimates. |
| `derived_metric` | An algorithm on other quantities/series; window and artifact handling are part of the meaning. |
| `measurement_method` | A device, assay, procedure or pipeline that produces observations. |
| `model` | A declarative computational model specification — never solver code. |
| `relationship` | A typed, directed assertion using a core or package-defined predicate. |
| `predicate`, `functional_form` | Additional vocabulary (core already provides a stock set). |

If you are unsure between `variable` and `latent_construct`, ask: *can this,
even in principle, be observed directly?* If no, it is a latent construct.

## Choosing identifiers

`ocpe:my-package/heart-rate` style: kebab-case English name; no units,
models, populations or methods encoded in the local-id. Identifiers are
permanent — a meaning change requires a new identifier, and retirement is
`status: deprecated` plus a `deprecation` block, never deletion:

```yaml
- id: ocpe:my-package/old-term
  kind: concept
  label: Old term
  concept_type: phenomenon
  status: deprecated
  deprecation:
    deprecated_in: "1.1.0"
    reason: Superseded by the replacement term.
    replaced_by: ocpe:my-package/new-term
```

Aliases keep older names working (synonyms, abbreviations, your previous
symbols, unit-qualified spellings). Aliases are case-sensitive; use `scope`
(a package id or model CURIE) to keep the same alias valid in different
contexts.

## Units

Use registered UCUM codes (`specification/core/units.yaml`): `mm[Hg]`,
`mL/s`, `/min`, `1`. Common alternative spellings (`mmHg`, `bpm`) normalize to
registered codes, but the registered form is preferred. Every unit you use
must be registered; request or add units to the registry before publishing
with them. The validator checks dimensional consistency of
`canonical_unit`, `accepted_units`, range units, alias units and model-symbol
units.

## Attaching evidence

Evidence statements attach to entities, relationships, ranges and model
elements:

```yaml
evidence:
  - claim: "The specific proposition being supported."
    supports: [direction]               # never read direction-level as magnitude-level
    references: [doi:10.0000/example]   # must be declared in a document-level references: list
    basis: literature
    study_type: observational_human
```

**Integrity rule:** every `references:` entry must match a record declared in
a `references:` list of a loaded document — yours or a dependency's. A
well-formed DOI string that no package declares is an error. Declare your
records where you cite them:

```yaml
references:
  - id: doi:10.0000/example
    title: Example Reference
    year: 2026
    study_type: observational_human
```

Optional grading scales (`evidence_level` 1–4, `evidence_tier` A–D) are
defined in `specification/core/evidence-scales.yaml`; several values are
provisional. `basis: definitional` covers mathematical identities with no
empirical citation needed.

## Context-qualifying ranges and performance

Reference ranges and measurement performance apply to a **stated context
only** — never as universal truths:

```yaml
reference_ranges:
  - range_type: plausibility_bound      # reference_interval | plausibility_bound |
    min: 0.5                            # clinical_threshold | model_validity_domain |
    max: 20.0                           # observed_range
    unit: L/min
    context:
      population: stated cohort description or entity reference
      posture: supine
      activity: rest
      scope_note: What this range is — and is not.
```

The five `range_type` values must never be conflated: a plausibility bound is
not a population reference interval. OCPE does not ship population reference
ranges; you own yours.

## Provenance

Record where content came from:

```yaml
provenance:
  contributors:
    - {name: Jane Researcher, kind: human, role: curator}
    - {name: agent-42, kind: ai_agent, role: drafted definitions}
  created: "2026-11-15"
```

`derived_from` (source path/URL, git ref, sha256, transformation) is how you
document migrations from your earlier notations.

## Version bumping

Use `ocpe diff old-release/ new-release/` to classify every change between
two releases — identifiers, nested equations, symbols/parameters, relationship
semantics, reference ranges, evidence attachments and dependency constraints
are all compared, and the required bump is derived from
`specification/versions/compatibility.yaml`:

- **major**: identifier/symbol/equation removal or semantic change,
  dimension/unit/kind changes, dependency removals or constraint tightening.
- **minor**: identifier/symbol/equation/predicate additions, deprecations,
  alias additions, evidence/range additions.
- **patch**: label/description/notes/provenance edits.

While your package is 0.y.z, a minor bump may carry breaking changes (SemVer
item 4), so consumers should pin the minor.

## Validating and fixing common errors

```bash
ocpe validate my-package/            # full report
ocpe validate my-package/ --strict   # warnings fail too
ocpe deps my-package/                # dependency resolution table
ocpe resolve SOME-ALIAS --path my-package/   # check resolution
```

Frequent findings:

| Error code | Meaning |
|---|---|
| `namespace` | Entity id namespace ≠ owning package id. |
| `undeclared-dependency` | You reference a package not in `dependencies`. |
| `unresolved-reference` | Referenced identifier not defined (or its package not loaded). |
| `unit` / `dimension-mismatch` | Unknown unit code or unit of the wrong dimension. |
| `unknown-predicate` | Predicate token not in the core (or declared package) vocabulary. |
| `alias-collision` | Same alias+scope maps to several entities. |
| `unresolved-evidence-reference` | Evidence cites a record no package declares. |
| `path-escape` | A content path leaves the package root. |
| `dependency-version` | Loaded dependency does not satisfy your constraint. |

## Worked example: a small package (synthetic)

`package.yaml`:

```yaml
id: example-flow
name: Example Flow Package
version: "1.0.0"
ocpe_spec: ">=0.1.0 <0.2.0"
description: Synthetic worked example for the authoring guide (no scientific content).
contents: [quantities.yaml]
```

`quantities.yaml`:

```yaml
ocpe: "0.1"
package: example-flow
references:
  - id: doi:10.12345/synthetic-example
    title: Synthetic Example Reference
    year: 2026
    study_type: in_silico
entities:
  - id: ocpe:example-flow/flow-rate
    kind: variable
    label: Flow rate
    definition: Synthetic volume-flow quantity used as a documentation example.
    dimension: volume_flow
    canonical_unit: mL/s
    value_type: continuous
    observability: directly_measurable
    evidence:
      - claim: This example quantity exists for documentation purposes.
        supports: [existence]
        references: [doi:10.12345/synthetic-example]
  - id: ocpe:example-flow/flow-meter
    kind: measurement_method
    label: Example flow meter
    method_type: device
    measures:
      - {target: ocpe:example-flow/flow-rate, mode: direct}
  - id: ocpe:example-flow/flow-rate-measured-by
    kind: relationship
    label: Flow rate is measured by the example flow meter
    subject: ocpe:example-flow/flow-rate
    predicate: MEASURED_BY
    object: ocpe:example-flow/flow-meter
```

`ocpe validate example-flow/` passes on this package. Your own packages will
be far richer — that is the point: the language is small, the domains are
yours.
