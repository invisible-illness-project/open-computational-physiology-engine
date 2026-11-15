# OCPE Architecture

**OCPE is semantic infrastructure, not a simulator.** It is the common,
versioned, machine-readable language through which AI agents, researchers,
applications and datasets communicate physiological knowledge: what things are,
how they relate, what evidence supports the claims, and in which context a
number applies. It does not integrate equations, generate synthetic patients,
or synthesize signals. Those capabilities live in downstream applications
(MOSAIC and Lamina) that consume OCPE content. The full scope statement is in
`docs/mission.md`; this document explains how the pieces fit together and what
each piece may depend on.

## System overview

```
                 ┌───────────────────────────────────────────────┐
                 │  downstream applications (consume, never      │
                 │  part of OCPE):                               │
                 │    MOSAIC — numerical simulation, synthetic   │
                 │             patients/cohorts, trajectories    │
                 │    Lamina — ECG/PPG/EDA signal synthesis and  │
                 │             derived-metric computation        │
                 └───────────────────────▲───────────────────────┘
                                         │ ocpe export / registry API
                 ┌───────────────────────┴───────────────────────┐
   OPTIONAL ───► │  governance extension (ADR 0001):             │
   (not required │  *.review.yaml sidecars + ocpe.governance     │
    to load,     │  review / aggregate / challenge / authorize   │
    validate or  └───────────────────────▲───────────────────────┘
    resolve)                             │ lazy import only
                 ┌───────────────────────┴───────────────────────┐
                 │  reference engine (implementations/python):    │
                 │  loader · validator · resolver · units ·      │
                 │  compatibility · versioning · CLI             │
                 └───────────────────────▲───────────────────────┘
                                         │ reads and enforces
                 ┌───────────────────────┴───────────────────────┐
                 │  domain packages (packages/): independently   │
                 │  versioned content packages (cardiovascular,  │
                 │  autonomic, systemic, conditions.*, ... )     │
                 └───────────────────────▲───────────────────────┘
                                         │ must conform to
                 ┌───────────────────────┴───────────────────────┐
                 │  specification contracts (normative):         │
                 │  JSON Schemas (draft-07) · identifier        │
                 │  grammar · unit registry · predicate and     │
                 │  functional-form vocabularies ·              │
                 │  compatibility rules                         │
                 └───────────────────────────────────────────────┘
```

## The layers

### 1. Specification contracts (normative)

Everything in `specification/` is the contract that everything else conforms
to. The normative artifacts (`specification/core/meta.yaml`) are the JSON
Schemas in `specification/schemas/`, the identifier grammar
(`specification/core/identifiers.md`), the unit registry
(`specification/core/units.yaml`), the predicate vocabulary
(`specification/core/predicates.yaml`), the functional-form registry
(`specification/core/functional-forms.yaml`), and the versioning policy.
`kinds.yaml` and `evidence-scales.yaml` are informative. The specification has
its own version (currently `0.1.0`, provisional) and its own changelog
(`specification/versions/CHANGELOG.md`). The specification depends on nothing
in this repository; everything else depends on it.

### 2. Domain packages

`packages/` holds independently versioned domain packages: `cardiovascular`,
`autonomic`, `systemic`, `conditions.*`, `interventions.*`, `wearables`,
`populations`, and `models.baroreflex-geddes-2022`. Each package is a
directory with a `package.yaml` manifest and a set of content documents listed
in the manifest's `contents`, in load order.

A package may only define identifiers in its own namespace: the package `id`
is exactly the CURIE namespace of its entities
(`ocpe:<package-id>/<local-id>`), and the validator rejects an entity whose
namespace differs from the defining package's id. Packages that reference
identifiers from other packages must declare those packages in
`dependencies` (with version constraints) or `optional_dependencies`. The
validator enforces this: an `ocpe:` reference to an undeclared package is an
error, not a courtesy warning. It also enforces that the declared dependency
graph is acyclic and that loaded dependency versions satisfy the declared
constraints. Self-dependencies are errors. Every package may use the `core`
vocabulary (predicates and functional forms) without declaring it.

Package content is plain data. A package has no code and no imports; its only
external couplings are the declared dependencies.

### 3. Reference engine

`implementations/python/` is the Python reference implementation of the
specification: a library (`ocpe`) plus a CLI. It is deliberately small:

- `loader.py` — discovery and parsing of packages into an in-memory `Registry`
  (packages, entities, references, aliases). Loading is purely structural:
  files are parsed and indexed, never checked for conformance.
- `validator.py` — the two-layer validation pipeline (see below).
- `resolver.py` — resolution of CURIEs, model symbols, aliases, labels and
  vocabulary tokens.
- `units.py` — unit normalization and dimensional consistency against the
  registered unit table. This is a registry lookup, not a UCUM parser.
- `versioning.py` / `compatibility.py` — semantic versions, version
  constraints, dependency satisfaction, and change classification
  (`ocpe diff`) between package releases.
- `spec.py` — locates the specification (environment variable, bundled copy,
  or source checkout) and loads its artifacts.
- `cli.py` — the `ocpe` command line (`validate`, `resolve`, `search`,
  `show`, `list`, `deps`, `diff`, `units`, `check-observation`, `export`,
  `info`).

The engine never imports `ocpe.governance`. Governance is an optional
extension loaded lazily, only when the `ocpe governance` sub-command runs.
Core commands never touch governance data. This separation is a hard
dependency rule, not a preference: loading, validating and resolving OCPE
content must work identically with zero governance files present.

### 4. Governance extension (optional, ADR 0001)

The governance extension adds evidence-layered review tracking on top of the
engine: sidecar manifests (`<asset>.review.yaml`, schema
`specification/schemas/governance/review-manifest.schema.json`), an
`ocpe.governance` subpackage, and the `ocpe governance` CLI. It records review
events, claims, challenges, adjudication, a derived validation summary and
downstream authorization decisions for content-addressed assets. See
[Governance](#governance-optional-extension) below.

### 5. Downstream applications

MOSAIC and Lamina consume OCPE content but are not part of it. MOSAIC performs
numerical ODE/DAE integration, synthetic patient and cohort generation, and
disease-specific trajectory simulation; Lamina synthesizes and processes ECG,
PPG and EDA signals and computes derived HRV metrics. OCPE hands them a
validated, resolved knowledge base (via the registry API or `ocpe export`);
what they compute with it is their responsibility. The boundary test from
`docs/mission.md` applies: a component belongs in OCPE only if it helps
represent, interpret, validate, exchange or version physiological knowledge.

## The entity-kind system

OCPE distinguishes a fixed set of entity kinds, and the kinds are **not
interchangeable** (`specification/core/kinds.yaml` states this as a
requirement; the JSON Schemas enforce it). The distinction matters because
each kind answers a different question and carries different obligations:

- **concept** — an entity with no unit or value (organ system, structure,
  process, mechanism). Not a variable: quantities attached to a concept are
  separate entities.
- **variable** — a quantity measurable in principle, independent of method
  and of any recorded value. Carries a dimension, a canonical unit and
  optionally reference ranges.
- **latent_construct** — a theoretical quantity not observable even in
  principle (e.g. sympathetic tone). Values are always model- or
  indicator-conditional estimates and must never be exchanged as
  measurements.
- **derived_metric** — a quantity defined by an algorithm applied to other
  quantities or series. Window length and artifact handling are part of its
  meaning and must be declared.
- **measurement_method** — a device, assay, procedure or processing pipeline
  that produces observations. Its performance characteristics are
  context-qualified.
- **observation** — a single reported value of a quantity at a time, with an
  explicit `value_kind` (measured / estimated / derived / simulated /
  self_reported). OCPE defines the record format only; it stores no
  observations. An observation is an exchange record, not a package entity —
  it does not appear in a document's `entities` list.
- **condition** — a disease, syndrome, phenotype, exposure or state that
  alters physiology.
- **intervention** — a test, protocol, therapy, drug, behaviour or
  environmental manipulation. Declarative only; execution is a downstream
  concern.
- **population** — a group description used to qualify context; explicitly
  not a cohort generator.
- **model** — a declarative computational model specification (symbols,
  equations, assumptions, units, evidence). Never solver code.
- **relationship** — a typed, directed assertion between entities, qualified
  by a predicate from the core vocabulary and optionally a functional form.
- **predicate** / **functional_form** — the core vocabulary kinds that
  register relationship types and named dependency shapes.

The document schema discriminates entities by their `kind` field and validates
each against its kind schema; kind-changing an identifier is classified as a
major (package-level) change by `ocpe diff`.

## Loading and validation pipeline

Validation has two layers, run in sequence by `ocpe.validator`:

**Layer 1 — schema.** Manifests are validated against
`package.schema.json`; each content document against `document.schema.json`,
whose `if`/`then` dispatch validates every entity against the schema for its
`kind`. This layer is a pure JSON Schema (draft-07) check.

**Layer 2 — semantic.** Checks that schemas cannot express, across the whole
loaded registry:

- identifier namespace ownership (entities defined in their own package's
  namespace; no `#symbol` fragments in entity ids; no duplicate identifiers);
- reference integrity: every `ocpe:` reference resolves, refers only to
  declared dependencies, and any `#symbol` fragment names a symbol declared by
  a model entity (unresolved references to *loaded* packages are errors;
  references to packages that are not loaded at all are warnings, since the
  target may simply be absent from this load);
- dependency declarations: targets loaded, version constraints satisfied, no
  self-dependencies, and a dependency graph without cycles;
- units and dimensions: registered UCUM codes, `canonical_unit` /
  `accepted_units` / reference-range units / alias units matching the declared
  dimension, model symbol units matching the dimension of the entity they
  represent;
- vocabulary: relationship predicates and functional forms must be registered
  in the core vocabulary; predicate `object_kinds` restrictions are checked;
- housekeeping: `min` ≤ `max` everywhere, alias collisions across entities,
  `status: deprecated` requires a deprecation block, `since` may not be later
  than the package version.

Observation exchange records go through a separate entry point
(`validate_observation`): schema validation plus semantics — the `quantity`
must resolve to a variable, derived metric or latent construct, a latent
construct can never be reported as `value_kind: measured`, and the unit must
match the quantity's dimension.

Every report carries the disclaimer, in machine-readable and CLI output alike:

> **Structural validation only; it does not establish scientific validity.**

This is the first principle in `docs/mission.md` and the
`statement_of_scope` of `specification/core/meta.yaml`. A green validation
means well-formed, internally consistent and resolvable — never biological
truth.

## Identifier and alias resolution

Every entity has exactly one canonical identifier,
`ocpe:<package-id>/<local-id>` (full grammar: `specification/core/identifiers.md`).
Identifiers are permanent, never reused, and retired by deprecation rather
than deletion. Aliases map other names — legacy knowledge-base symbols such as
`Hc` and `HR`, synonyms, abbreviations — onto canonical identifiers. An alias
may carry a `unit`, meaning it denotes the same quantity expressed in a
different unit; it does not create a new quantity. Aliases are case-sensitive
and may be scoped; a scoped alias is only unique within its scope.

The resolver (`ocpe.resolver.Resolver`) resolves a term in a fixed order of
precedence:

1. canonical CURIE;
2. CURIE with a `#symbol` fragment (model-local symbol; the resolution
   reports the symbol's unit and what it represents);
3. predicate token (e.g. `REGULATES`);
4. functional-form token (e.g. `sigmoid_hill`);
5. alias — case-sensitive, filtered by scope if one is given;
6. label — case-insensitive, and only if no alias matched.

Ambiguity is an error that lists the candidates; the resolver never guesses.
This is what makes legacy symbols safe to keep using: `Hc` and `HR` both
resolve to `ocpe:cardiovascular/heart-rate`, distinguished by unit, and an
unscoped lookup that matches several entities raises an ambiguity instead of
silently picking one.

## Versioning and compatibility

Three things are versioned independently, and keeping them apart is the whole
point:

- **Specification version** (`0.1.0`, provisional; from `meta.yaml`). Drives
  the schema base URI, the document marker (`ocpe: "0.1"` in every document)
  and which document versions an engine release can read
  (`specification/versions/compatibility.yaml`). A package declares the spec
  range it conforms to in its manifest's `ocpe_spec` field, and the validator
  checks the loaded engine's spec version against it.
- **Package versions** (semver, e.g. `cardiovascular 1.0.0`). Each package
  keeps its own changelog. Identifier stability rules tie content to versions:
  `since` records the introducing version, and a deprecation must carry a
  deprecation block for at least one minor release before removal in a major
  release.
- **Engine version** (`ocpe 0.1.0`). The reference implementation's own
  release number; independent of the spec version it implements.

Compatibility is machine-readable in
`specification/versions/compatibility.yaml`, which records
releases (with `document_marker` and `reads_documents`), classifies changes as
major/minor/patch for both packages and the specification, and states the
pre-1.0 policy.

**Pre-1.0 policy.** While a version is `0.y.z`, a MINOR bump may carry
breaking changes (SemVer item 4). Constraints must therefore pin the minor:
`>=0.1.0 <0.2.0`, which is what the shipped manifests do. `ocpe diff`
classifies the differences between two releases of a package against the
change classes and checks that the declared version bump is sufficient, with
severities shifted accordingly while the major version is 0
(major→minor, minor→patch).

## Governance (optional extension)

Review and authorization live outside the core, per ADR 0001
(`docs/adr/0001-sidecar-yaml-review-validation-tracking.md`). The decision
recorded there: scientific content and governance metadata are separate, so
review activity is stored in sidecar manifests (`<asset>.review.yaml`) next to
the assets they cover, bound to the exact content by SHA-256. The review
manifest has three separable layers — review records (reviews, claims,
challenges, adjudication, human review), a derived validation summary
recomputable from the first layer, and authorization decisions produced by an
organization-specific policy. None of them is required to load, validate or
resolve OCPE packages, and the core engine has no import dependency on the
governance code.

The ADR's core principle: human review is not a universal prerequisite for
scientific progress; it is a higher-trust provenance and authorization layer
applied according to downstream risk. AI-generated consensus is evidence, not
truth. Content links to its sidecar through the optional
`provenance.review_manifest` field; `ocpe governance summary` gives an
optional overview of review state across packages.

## What OCPE deliberately does not do

- No numerical execution. Model entities are specifications (symbols,
  equations, assumptions, units, evidence); solvers, step sizes and run
  orchestration belong to implementations — MOSAIC or others — which are
  referenced but not contained.
- No data storage. Observation is an exchange format; OCPE stores knowledge,
  not measurements.
- No cohort generation. Population entities qualify context; generating
  synthetic patients is MOSAIC's job.
- No signal processing. Derived-metric *definitions* (with declared
  computation and input requirements) are OCPE content; computing RMSSD from a
  PPG stream is Lamina's job.

Anything that computes belongs downstream; anything that says what things
mean belongs here.
