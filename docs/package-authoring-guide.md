# OCPE Package Authoring Guide

How to author a new OCPE domain package: the manifest, documents, identifiers,
units, evidence, provenance and versioning, plus validation. The normative
sources are the JSON Schemas in `specification/schemas/`, the identifier rules
in `specification/core/identifiers.md`, the unit registry in
`specification/core/units.yaml`, the compatibility rules in
`specification/versions/compatibility.yaml`, and the reference packages
(`packages/cardiovascular/`, `packages/conditions/pots/`). Where this guide and
a normative source disagree, the source wins.

A package is an independently versioned unit of physiological knowledge. Its
`id` is also the CURIE namespace of every entity it defines
(`ocpe:<package-id>/<local-id>`), so the package id is a naming commitment, not
just metadata.

## Directory layout

```
packages/<package-id>/
  package.yaml       # manifest — required
  <documents>…       # YAML or JSON files listed in `contents`, in load order
  CHANGELOG.md       # if the manifest declares `changelog`
  *.review.yaml      # optional governance sidecars (ADR 0001) — not package contents
```

Package ids are lowercase kebab-case, dot-separated for sub-namespaces, and the
directory structure follows the dots: `conditions.pots` lives at
`packages/conditions/pots/`. Documents are package-relative paths matching
`^[^/].*\.(ya?ml|json)$` — no leading slash, YAML or JSON only.

## The package.yaml manifest

Required fields: `id`, `name`, `version`, `ocpe_spec`, `description`,
`contents`. The schema rejects unknown fields (`additionalProperties: false`);
the escape hatch is extension keys beginning with `x-`.

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Package id. Must equal the CURIE namespace of its entities: dot-separated kebab-case segments (`cardiovascular`, `conditions.pots`). |
| `name` | string | Human-readable name. |
| `version` | semver | This release, e.g. `"1.0.0"`. Quoted, so YAML does not parse it as numbers. |
| `ocpe_spec` | constraint | Range of OCPE specification versions this package conforms to, e.g. `">=0.1.0 <0.2.0"`. The engine rejects the package if its own spec version does not satisfy this. |
| `description` | string | What the package contains and where it came from. |
| `status` | enum | `draft`, `provisional`, `stable`, `deprecated`, `withdrawn`. |
| `license` | string | SPDX expression, or `UNSPECIFIED`. |
| `maintainers` | array | Objects with required `name` and optional `email`, `url`, `kind` (`human`, `organization`, `ai_agent`). |
| `keywords` | array | Strings. |
| `homepage` | string | URL. |
| `dependencies` | array | See below. |
| `optional_dependencies` | array | Same shape as `dependencies`. |
| `contents` | array | Package-relative document paths, in load order. At least one, no duplicates. |
| `changelog` | string | Package-relative path to the package CHANGELOG; a warning is raised if the file is missing. |
| `provenance` | object | `derived_from` etc. (see Provenance below). |
| `deprecation` | object | `reason` (required) and optional `replaced_by` (a package id). |
| `notes` | string | Free text. |

### Dependencies and version constraints

Each entry of `dependencies` / `optional_dependencies` is
`{package: <id>, version: <constraint>, reason: <string>}`; `package` and
`version` are required. The distinction:

- `dependencies` — packages whose identifiers this package references.
  **References to undeclared packages are validation errors.**
- `optional_dependencies` — packages that enrich this package if present but
  are not required to interpret it.

The engine always permits references in your own namespace and in `core`; every
other referenced namespace must be declared. The reference packages declare
`core` anyway, with a `reason` — follow that habit.

Constraint grammar (see `docs/versioning-policy.md` for the full rules):
whitespace-separated comparators — `>=`, `>`, `<=`, `<`, `=`, `^`, `~` —
combined with AND; alternatives separated by `||`; `*` matches anything. A bare
version means `=`; partial versions are zero-padded. `^1.2.3` means
`>=1.2.3 <2.0.0`, but `^0.2.3` means `>=0.2.3 <0.3.0` (caret pins the minor for
0.y versions), and `~1.2.3` means `>=1.2.3 <1.3.0`. Under the pre-1.0 policy
(see Versioning below), constraints on 0.y artifacts pin the minor:
`">=0.1.0 <0.2.0"`. The engine checks that each declared dependency is loaded
and that its version satisfies the constraint (`ocpe deps` tabulates this).

## Documents: envelope and contents

Every document listed in `contents` has this envelope (unknown fields are
rejected; `x-` extensions allowed):

```yaml
ocpe: "0.1"              # required — spec major.minor this document is written against
package: my-package     # required — must equal the manifest id
title: …                # optional
description: …          # optional
provenance: …           # optional
curation_notes: […]     # optional, verbatim curation history
entities: […]           # at least one of entities / references is required
references: […]         # bibliographic records (doi:, pmid:, …)
```

The `ocpe` marker must be one the engine can read. For the 0.1.0 engine that is
`"0.1"` only (see `releases[].reads_documents` in
`specification/versions/compatibility.yaml`); a document written against any
other marker fails validation. The engine resolves the marker to a schema base
URI (`schema_base_uri`) and validates each entity against the schema for its
`kind`.

The `kind` enum: `concept`, `condition`, `derived_metric`, `functional_form`,
`intervention`, `latent_construct`, `measurement_method`, `model`, `population`,
`predicate`, `relationship`, `variable`. Every entity carries the shared base
fields: required `id`, `kind`, `label`, plus optional `definition`,
`description`, `aliases`, `status`, `since` (the package version that
introduced the identifier), `deprecation`, `evidence`, `provenance`,
`external_mappings`, `see_also`, `notes`, `curation_notes`. Kind-specific
schemas add their own required fields — for a variable, `dimension` and
`canonical_unit`; for a relationship, `subject`, `predicate`, `object`.

## Choosing the entity kind

Kinds are distinct and must never be used interchangeably
(`specification/core/kinds.yaml`). Apply the kind tests in order:

- **concept** — "An entity with no unit or value (organ system, structure,
  process, mechanism)." Example: `ocpe:cardiovascular/baroreflex`.
- **variable** — "A quantity that can, at least in principle, be measured
  directly or indirectly, independent of method and value." If a number could
  in principle be observed for it, it is a variable, not a latent construct.
  Example: `ocpe:cardiovascular/heart-rate`.
- **latent_construct** — "A theoretical quantity that cannot be observed even
  in principle; values are always model- or indicator-conditional estimates."
  If any value is a model- or indicator-conditional estimate, it is a latent
  construct. Example: `ocpe:autonomic/sympathetic-tone`.
- **derived_metric** — "A quantity defined by an algorithm applied to other
  quantities or series (window, artifact handling matter)." If the definition
  is an algorithm whose parameters (window length, artifact handling) change
  the result, it is a derived metric, not a variable. Example:
  `ocpe:autonomic/rmssd`.
- **measurement_method** — "A device, assay, procedure or processing pipeline
  that produces observations; carries context-qualified performance." The
  method is not the quantity. Example: `ocpe:wearables/polar-h10`.

The remaining kinds: `condition` (a disease, syndrome, phenotype, exposure or
state that alters physiology), `intervention` (a test, protocol, therapy, drug,
behaviour or environmental manipulation), `population` (a group description
used to qualify context; not a cohort generator), `model` (a declarative
computational model specification — symbols, equations, assumptions, units,
evidence — never solver code), `relationship` (a typed directed assertion),
`predicate` and `functional_form` (vocabulary kinds, normally added to the core
package rather than a domain package).

Migration pitfall: the legacy `PhysiologicalVariable` class conflated variables,
derived metrics and model compartments, and legacy `LatentState` items that are
measurable in principle (total blood volume, peripheral resistance) were
reclassified as variables. Do not copy legacy class names into `kind` fields;
apply the tests to each item.

## Choosing identifiers

Canonical form: `ocpe:<namespace>/<local-id>`. The namespace is the owning
package id; only that package may define identifiers in it. Local-id rules
(`specification/core/identifiers.md`, section 4):

- Use the established English physiological name in kebab-case
  (`mean-arterial-pressure`).
- Do **not** encode units, models, populations or measurement methods in a
  local-id.
- Do **not** use model symbols as local-ids.

Symbols declared inside a model are referenced with a fragment:
`<model-curie>#<symbol>`, e.g.
`ocpe:models.baroreflex-geddes-2022/baroreflex-geddes-2022#RalpM`. Symbols are
case-sensitive and only meaningful inside the declaring model; they are not
physiological identifiers. Fragments are valid in **references** (`entity_ref`);
an entity's own `id` must never carry a `#fragment`.

Identifiers are permanent: once released, meaning never changes, and withdrawn
identifiers are never reused. Retirement is deprecation, not deletion (see
Versioning below).

## Units

Units are UCUM case-sensitive codes (`mm[Hg]`, `mL/s`, `/min`, `1`), and every
unit you use must be registered in `specification/core/units.yaml`. The
registry lists each unit's dimension and its conversion factor to the
dimension's reference unit; the engine uses it for dimensional-consistency
checks and it is **not** a general-purpose UCUM implementation. The registry's
own instruction: add units there before using them. Register the unit with its
dimension (and `to_reference` factor) first, then reference it in the package.

Registered dimensions include `dimensionless`, `length`, `time`, `volume`,
`pressure`, `volume_flow`, `frequency`, `event_rate`, `angle`, `compliance`,
`elastance`, `hydraulic_resistance`, `inverse_pressure`, `density`,
`acceleration`, `temperature`, `mass_concentration`. Heart beats are a separate
pseudo-dimension (`EVT`), so `/min` (beats per minute) is distinguishable in
intent from `Hz` (generic frequency) while remaining convertible within
`event_rate`. Legacy spellings (`mmHg`, `bpm`, `ml/s`) are mapped to canonical
codes in the registry — use the canonical code in new content.

The validator checks that `canonical_unit`, `accepted_units`, reference-range
units and unit-qualified alias units are registered and consistent with the
entity's `dimension`.

## Attaching evidence

An evidence statement (`specification/schemas/evidence.schema.json`) records
WHAT is supported, BY WHICH references, at WHAT strength. It requires at least
one of `references`, `citation`, or `basis`; everything else qualifies the
claim. Key fields:

- `supports` — which aspect of the assertion the evidence supports, one or more
  of: `existence`, `direction`, `magnitude`, `structure`, `association`,
  `definition`, `mechanism`, `measurement_validity`. This is the central
  discipline: **direction-level support must not be read as magnitude-level
  support.** A study showing that leg reflex NE spillover is blunted supports
  the direction of a perturbation, not its calibrated magnitude.
- `references` — persistent-identifier ids: `doi:…`, `pmid:…`, `pmcid:…`,
  `isbn:…`, `arxiv:…`, `url:…`. Declare the full records in the document's
  `references:` list.
- `citation` — human-readable citation text, preserved verbatim from the
  source where available.
- `basis` — `literature`, `definitional`, `expert_opinion`, `machine_proposed`,
  `machine_calibrated`, `computational_experiment`, `dataset`. `definitional`
  is for mathematical identities (e.g. HR = 60000/RR) that need no empirical
  citation.
- `evidence_level` / `evidence_tier` — legacy values preserved **verbatim**:
  `Level 1`–`Level 4` and `A`–`D`. Only Level 1 (RCT) and Level 4 (in silico)
  have documented anchors; levels 2–3 and the tiers are provisional per
  `specification/core/evidence-scales.yaml`. Do not invent new values.
- `curation_status` — `verified`, `partially_verified`, `unverified`,
  `machine_proposed`, `machine_calibrated`, `disputed`, `retracted`, `unknown`.
  Perturbations whose magnitude is not verified belong in
  `unverified_parameter_perturbations`, which consumers treat as inert unless
  explicitly opted in.
- `claim`, `context`, `limitations`, `notes` — the specific proposition, the
  circumstances under which it holds, and caveats.

Evidence can be attached to an entity, a relationship, a reference range, or a
parameter perturbation, at whatever granularity the sources support. Structural
validity of an evidence statement says nothing about its scientific
correctness; validation never re-grades content.

## Context-qualifying ranges and performance

OCPE treats reference ranges and measurement performance as context-dependent,
never as universal truths. A `reference_range` requires `range_type`, `unit`,
and `context`, plus at least one of `min`/`max`:

- `range_type`: `reference_interval` (population interval), `plausibility_bound`
  (engineering sanity bound), `clinical_threshold` (decision limit),
  `model_validity_domain`, `observed_range`. These must never be conflated —
  the migrated cardiovascular ranges are explicitly plausibility bounds, not
  population reference intervals.
- `context`: `population` (entity reference or free text), `health_status`,
  `age_range` (`min`, `max`, `unit`), `sex` (`female`, `male`, `any`, `mixed`,
  `unspecified`), `posture`, `activity`, `setting`, `measurement_method`,
  `model`, `scope_note`. Further dimensions may be added with string, number
  or boolean values. Use `scope_note` to state what the context is *and is
  not*.

A `measurement_method` carries context-qualified performance the same way:
accuracy claims belong to a stated population, posture, activity and procedure,
not to the device in general. Attach the supporting evidence to the range or
performance entry itself.

## Provenance, migration and aliases

`provenance` (`provenance.schema.json`) records where content came from and how
it was produced; it is descriptive and does not imply review or approval. For
migrated content, `derived_from` entries carry `source` (required; repository
path or URL), `git_ref`, `sha256`, `legacy_id`, `legacy_version`, and
`transformation` — a statement of what changed. Follow the migration principle:
preserve values, citations and curation notes verbatim; restructuring never
re-grades evidence. Verbatim source headers belong in `curation_notes`.

Legacy names map onto canonical identifiers through `aliases`, so old symbols
keep resolving:

```yaml
aliases:
  - {value: Hc, type: symbol, scope: legacy-kb, unit: /s}
```

Aliases are case-sensitive (`HR` ≠ `hr`); a scoped alias is only unique within
its scope (`legacy-kb` for pre-0.1 knowledge-base symbols, or a model CURIE for
model symbols); an alias with a `unit` denotes the same quantity expressed in a
different unit — it does not create a new quantity (`Hc` in `/s` and `HR` in
`/min` both resolve to `ocpe:cardiovascular/heart-rate`). Use `type:
legacy-id` for pre-0.1 identifiers and `type: synonym` / `abbreviation` /
`label` for plain alternative names. Do not re-purpose an alias for a different
entity: a withdrawn identifier remains reserved, and an alias that becomes
ambiguous is reported as an error (`alias-collision`).

## Version bumping

The change classes that drive version bumps
(`specification/versions/compatibility.yaml`, `change_classes.package`):

| Severity | Changes |
|---|---|
| major | `identifier_removed`, `alias_removed`, `identifier_kind_changed`, `dimension_changed`, `canonical_unit_changed`, `dependency_major_bump_required` |
| minor | `identifier_added`, `identifier_deprecated`, `alias_added`, `evidence_added`, `reference_range_added` |
| patch | `label_or_description_changed`, `curation_note_changed` |

Rules of thumb:

- Adding entities, aliases, evidence or reference ranges is a **minor** release.
- Fixing a label, definition or description, or adding curation notes, is a
  **patch** release. Labels and aliases may change in minor releases; canonical
  identifiers may not.
- Removing an identifier or alias, changing an entity's kind, dimension or
  canonical unit, or requiring a new major of a dependency is a **major**
  release.
- Deprecate before you remove: `status: deprecated` plus a `deprecation` block
  (`deprecated_in`, `reason`, optional `replaced_by`) for at least one minor
  release; removal happens only in a major release.
- Record the introducing version in each entity's `since` field; it must not be
  later than the package version.

**Pre-1.0 packages.** While a package is at `0.y.z`, a minor bump may carry
breaking changes (SemVer item 4; `pre_1_0_policy: minor-is-breaking`). A
breaking change in a 0.y package therefore requires a minor bump, not a major —
and consumers must pin the minor in their constraints (`>=0.1.0 <0.2.0`).
Migrated domain packages are already at 1.x and follow the post-1.0 table
directly.

Before releasing, run `ocpe diff <old-dir> <new-dir>`; it classifies the
changes, states the required bump, and reports whether your declared bump is
sufficient (see `docs/versioning-policy.md`).

## Validating and fixing common errors

```bash
pip install -e implementations/python
ocpe validate <dir>          # validate one package directory (default: all of packages/)
ocpe validate <dir> --strict # treat warnings as failures
```

Validation is structural: it establishes that content is well-formed,
internally consistent and resolvable. It does not establish scientific
validity. Common findings and their fixes:

| Finding | Cause | Fix |
|---|---|---|
| `namespace` | Entity id's namespace differs from the manifest `id`. | Define the entity in the package that owns the namespace, or correct the id. |
| `id-fragment` | An entity `id` contains a `#symbol` fragment. | Fragments belong in references only; drop the fragment from the id. |
| `document-package` / `document-version` | Document `package` ≠ manifest id, or its `ocpe` marker is not readable by this engine. | Set `package` to the manifest id; write the document against a readable marker (`"0.1"` for engine 0.1.0). |
| `undeclared-dependency` | A reference targets a package not in `dependencies`/`optional_dependencies`. | Declare the dependency with a version constraint and a `reason`. |
| `dependency-missing` / `dependency-version` | Declared dependency not loaded, or loaded version outside the constraint. | Load the dependency package; widen or adjust the constraint. |
| `unresolved-reference` / `unknown-symbol` | Target entity or model symbol does not exist. | Check the id; model symbols must be declared by the referenced model. |
| `unit` | Unit code not in `specification/core/units.yaml`. | Register the unit (with dimension and `to_reference`) in the registry first. |
| `dimension` / `dimension-mismatch` | Unknown dimension, or a unit whose dimension differs from the entity's. | Use a unit of the declared dimension — e.g. a `volume` variable takes `mL`, not `mm[Hg]`. |
| `unknown-predicate` / `unknown-functional-form` | Token not in the core vocabulary. | Use a registered token (see `specification/core/predicates.yaml`, `functional-forms.yaml`) or its `ocpe:core/…` CURIE. |
| `deprecation` | `status: deprecated` without a `deprecation` block. | Add `deprecated_in`, `reason`, optionally `replaced_by`. |
| `since` | Entity `since` later than the package version. | Bump the package version or correct `since`. |
| `range` | A `min` greater than `max`. | Correct the bounds. |
| `alias-collision` | The same alias (in one scope) maps to several entities. | Scope the aliases or rename; the resolver reports ambiguity rather than guessing. |
| `dependency-cycle` / `self-dependency` | Circular or self dependency. | Restructure — e.g. package model-specific links with the model, as the cardiovascular relationships do for the Geddes 2022 model. |

Warnings (`deprecated-reference`, `changelog-missing`, `predicate-range`) do not
fail validation unless `--strict` is given.

## Worked example 1: a variable with a context-qualified reference range

```yaml
# packages/respiratory/variables.yaml — illustrative excerpt
ocpe: "0.1"
package: respiratory
title: Respiratory variables
entities:
  - id: ocpe:respiratory/respiratory-rate
    kind: variable
    label: Respiratory Rate
    definition: "Number of breaths per unit time, independent of the device or procedure used to count them."
    dimension: event_rate
    canonical_unit: /min
    observability: directly_measurable
    reference_ranges:
      - range_type: reference_interval
        min: 12
        max: 20
        unit: /min
        context:
          population: adults free of acute cardiopulmonary disease   # free text is allowed here
          posture: seated
          activity: resting
          sex: any
          scope_note: "Seated, resting, spontaneously breathing adults; does not apply during sleep, exercise or fever."
        evidence:
          - supports: [magnitude]
            citation: "(illustrative — replace with the verified source citation)"
            basis: literature
    since: "1.0.0"
```

Points to copy: `range_type` says what kind of range this is (a population
`reference_interval`, not a plausibility bound); `unit` is a registered UCUM
code of the entity's dimension; `context` states exactly whom the range covers
and `scope_note` states whom it does not; the evidence is attached to the range
entry itself and claims `magnitude` support only. The `citation` above is a
placeholder — in a real package, reference ids use a persistent-identifier
scheme (`doi:`, `pmid:`, …) declared in the document's `references:` list, and
citations are preserved verbatim from the source.

## Worked example 2: a relationship with evidence and a functional form

```yaml
# packages/respiratory/relationships.yaml — illustrative excerpt
ocpe: "0.1"
package: respiratory
entities:
  - id: ocpe:respiratory/arterial-co2-pressure
    kind: variable
    label: Arterial CO2 Pressure
    dimension: pressure
    canonical_unit: mm[Hg]
    observability: indirectly_measurable
    since: "1.0.0"
  - id: ocpe:respiratory/minute-ventilation
    kind: variable
    label: Minute Ventilation
    dimension: volume_flow
    canonical_unit: L/min
    observability: directly_measurable
    since: "1.0.0"
  - id: ocpe:respiratory/arterial-co2-increases-ventilation
    kind: relationship
    label: Arterial CO2 increases ventilation
    subject: ocpe:respiratory/arterial-co2-pressure
    predicate: INCREASES
    object: ocpe:respiratory/minute-ventilation
    direction_of_effect: positive
    functional_form: sigmoid_hill
    evidence:
      - claim: "Rising arterial CO2 pressure increases minute ventilation; the steady-state response is sigmoidal with a steep mid-range."
        supports: [existence, direction, structure]
        citation: "(illustrative — replace with the verified source citation)"
        basis: literature
    known_limitations: "Steady-state claim; dynamic response to rapid CO2 changes is not asserted."
    applicable_contexts:
      - population: awake healthy adults
        posture: any
        activity: resting
        scope_note: "Chemoreflex-driven ventilation; not a claim about exercise hyperpnoea."
    since: "1.0.0"
```

Points to copy: `predicate` is a registered core token (see
`specification/core/predicates.yaml`); `functional_form: sigmoid_hill` is a
registered token from `specification/core/functional-forms.yaml` — use one of
the registered shapes, not an ad-hoc name; `supports` lists exactly the aspects
the sources back (`structure` covers the sigmoidal shape — do not claim
`magnitude` for uncalibrated parameters); and the claim is restricted to its
`applicable_contexts`. Both subject and object must resolve — they would be
defined in the same package (or a declared dependency's).
