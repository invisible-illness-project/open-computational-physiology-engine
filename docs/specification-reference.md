# OCPE Specification Reference

Reference for the OCPE 0.1 schemas and the shared machinery they rely on:
identifiers, units, context, reference ranges and evidence. The JSON Schemas
in `specification/schemas/` are the normative contract (draft-07 of JSON
Schema); this document describes them for authors of packages, tools and AI
agents. Where this document and a schema disagree, the schema wins.

Authoring format is YAML 1.2 (JSON is equally valid). Unless noted, every
schema allows `x-` prefixed extension keys and forbids undeclared properties.

OCPE ships **no domain content**: every example below uses a placeholder
package such as `example-org`. Real entities are defined by external,
independently versioned domain packages.

**Status of validation.** Conformance to these schemas establishes that
content is well-formed, internally consistent and resolvable. It does not
establish scientific validity (`specification/core/meta.yaml`,
`statement_of_scope`).

## The document envelope

Every content file listed in a package manifest's `contents` is a document
(`document.schema.json`) with the envelope:

```yaml
ocpe: "0.1"                # specification major.minor the document is written against
package: example-org      # the owning package id; equals the CURIE namespace
title: Example variables
entities: [ ... ]          # at least one of entities / references is required
references: [ ... ]
```

The `ocpe:` marker is checked against the engine's readable document versions
(`reads_documents` in `specification/versions/compatibility.yaml`); for
specification 0.1.0 the marker is `"0.1"`. A document must not claim a
`package` different from the manifest that lists it.

## Entity discrimination by `kind`

Entities in a document's `entities` array are discriminated by their `kind`
field; the document schema dispatches each entry to the schema for its kind.
The package entity kinds are: `concept`, `variable`, `latent_construct`,
`derived_metric`, `measurement_method`, `model`, `relationship`, plus the
core-vocabulary kinds `predicate` and `functional_form`. The kinds are
distinct and must never be used interchangeably
(`specification/core/kinds.yaml` states the deciding tests; the kind schemas
enforce them).

Specification-level types that are **not** package entity kinds: `observation`
(an exchange record validated by `observation.schema.json`), `unit` (an entry
in `core/units.yaml`), `evidence_claim` and `reference` (attachments and
document-level records), and `package` (the manifest itself).

Every entity kind composes the shared `entity_base` definition (see
[common.schema.json](#commonschemajson)): required `id`, `kind`, `label`;
optional `definition` (normative), `description` (informative), `aliases`,
`status`, `since`, `deprecation`, `evidence`, `provenance`,
`external_mappings`, `see_also`, `notes`, `curation_notes`.

## Identifiers: CURIE grammar and model symbols

Every OCPE entity has exactly one canonical identifier, a compact URI
(`specification/core/identifiers.md` is the normative grammar; the
authoritative regular expression is `definitions.curie` in
`common.schema.json`):

```
ocpe:<namespace>/<local-id>
```

- `namespace` — the owning package id: one or more dot-separated kebab-case
  segments (`example-org`, `consortium.project-a`).
- `local-id` — kebab-case (`flow-rate`).

Examples: `ocpe:example-org/flow-rate`,
`ocpe:consortium.project-a/output-rate`, `ocpe:core/regulates`. Only the
package whose `id` equals the namespace may define identifiers in it. The
`ocpe:` prefix expands to `https://w3id.org/ocpe/id/`; the persistent-URL
registration is pending, so the CURIE is currently the only normative form.

**Model symbol fragments.** A symbol declared inside a model specification is
referenced as `<model-curie>#<symbol>`, e.g.
`ocpe:research.my-model/my-model#Rtot`. Symbols are
case-sensitive and meaningful only inside the declaring model; a symbol is not
a physiological identifier, though it may *represent* one via the model
symbol's `represents:` field. Entity ids must never contain `#` fragments.

**Stability rules.** Identifiers are permanent and never reused; a meaning
change requires a new identifier. Retirement is deprecation, not deletion:
`status: deprecated` plus a `deprecation` block (`deprecated_in`, `reason`,
optional `replaced_by`, `removal_planned_in`) for at least one minor release
before removal in a major release. Labels and aliases may change in minor
releases; canonical identifiers may not.

**Aliases** map other names onto canonical identifiers — synonyms,
abbreviations, an author's previous symbols, unit-qualified spellings
(case-sensitive; `scope` — a package id or model CURIE — restricts where they
are unique; `unit` marks an alias denoting the same quantity in a different
unit). An unscoped lookup matching several entities is an ambiguity error,
never a guess. Alias `type` is one of `symbol`, `synonym`, `abbreviation`,
`legacy-id`, `label`.

```yaml
aliases:
  - {value: FR, type: symbol, unit: mL/s}    # same quantity expressed in mL/s
  - {value: hr, type: synonym}
```

## Units

Units are written as **registered UCUM case-sensitive codes**
(`https://ucum.org`): `mm[Hg]`, `mL/s`, `/min`, `1`. The normative list is
`specification/core/units.yaml`, which maps each code to a named dimension and
a `to_reference` conversion factor. The engine uses this table for
dimensional-consistency checks; it is **not** a general-purpose UCUM
implementation — every unit used in OCPE content must be registered (common
alternative spellings such as `mmHg` or `bpm` normalize to their registered
codes), and new units are added to the registry before use. Dimension vectors
use exponents of L, M, T and the OCPE pseudo-dimension EVT (countable events),
which keeps `counts/min` (event rate) distinguishable in intent from generic
frequency while remaining convertible within the `event_rate` dimension.
Registered dimensions: `dimensionless`, `length`, `time`, `volume`,
`pressure`, `volume_flow`, `frequency`, `event_rate`, `angle`, `compliance`,
`elastance`, `hydraulic_resistance`, `inverse_pressure`, `density`,
`acceleration`, `temperature`, `mass_concentration`.

The validator checks that `canonical_unit`, `accepted_units`,
reference-range units and unit-bearing aliases all match the entity's
declared `dimension`, and that model symbol units match the dimension of the
entity they represent. Unit conversion is multiplicative only; offset
conversions (temperature) are not supported.

## The context object

Ranges, measurement performance, relationships and evidence claims are all
qualified by a `context` object (`common.schema.json#/definitions/context`).
OCPE treats reference ranges and measurement performance as
context-dependent, never as universal truths.

Recognized keys: `population` (population reference or free text),
`health_status`, `age_range` (`min`, `max`, `unit`), `sex`
(`female` | `male` | `any` | `mixed` | `unspecified`), `posture`,
`activity`, `setting`, `measurement_method` (entity reference or
description), `model` (CURIE), and `scope_note` — a plain-language statement
of what the qualifying context is and is not. Additional dimensions may be
added with string, number or boolean values. At least one property is
required.

```yaml
context:
  population: adults 20-40, free-text or an entity reference
  posture: seated
  activity: rest
  scope_note: "Stated population at seated rest; does not apply during exercise."
```

## reference_range and range types

A `reference_range` is a context-qualified range of values. Required:
`range_type`, `unit`, `context`; at least one of `min`/`max`; optional
`evidence`, `notes`.

The `range_type` enum distinguishes five things that must never be conflated:

- `reference_interval` — a population reference interval (e.g. the central
  95% of a stated population).
- `plausibility_bound` — an engineering/physiological plausibility bound on
  a value; explicitly *not* a population reference interval.
- `clinical_threshold` — a cut-off with clinical consequences.
- `model_validity_domain` — the range over which a model is stated to be
  valid.
- `observed_range` — the range actually observed in a stated study sample.

The same five types apply wherever ranges appear (variables, latent
constructs, derived metrics). The validator checks range units against the
entity's dimension and rejects `min > max`; it cannot check that a range was
classified honestly — that is curation responsibility. Domain packages — not
the OCPE core — own all population-specific reference intervals.

## Evidence statements

An `evidence` object (`evidence.schema.json`) is a lightweight, attachable
statement of *what* is supported, *by which references*, at *what strength*.
It can be attached to entities, relationships, reference ranges and model
elements. At least one of `references`, `citation` or `basis` is required:

- `references` — array of persistent-identifier references (`doi:...`,
  `pmid:...`, `pmcid:...`, `isbn:...`, `arxiv:...`, `url:...`). **Integrity
  rule:** every cited id must be a record declared in a `references:` list of
  some loaded package; a syntactically valid DOI string is not proof the
  record exists.
- `citation` — human-readable citation text, preserved verbatim;
- `basis` — nature of the evidential basis: `literature`, `definitional`,
  `expert_opinion`, `machine_proposed`, `machine_calibrated`,
  `computational_experiment`, `dataset`. `definitional` is for mathematical
  identities that need no empirical citation.

Key fields: `claim` (the specific proposition supported); `supports` — which
aspect(s) the evidence supports, from `existence`, `direction`, `magnitude`,
`structure`, `association`, `definition`, `mechanism`,
`measurement_validity` (direction-level evidence must never be read as
magnitude-level support); `study_type`; `context`; `curation_status`
(`verified` | `partially_verified` | `unverified` | `machine_proposed` |
`machine_calibrated` | `disputed` | `retracted` | `unknown`); `limitations`;
`notes`.

OCPE core deliberately defines **no** evidence grading scale: grading
vocabularies are domain-package content. Packages that need levels or tiers
define them via `x-` extensions or their own predicates and vocabulary
entities. Prefer an explicit `basis` over any inherited grading label (a
definitional identity needs no empirical citation).

```yaml
evidence:
  - claim: "Example direction claim supplied by a domain package."
    supports: [direction]
    references: [doi:10.0000/example]
    study_type: observational_human
```

## common.schema.json

Shared, reusable definitions referenced by every other schema. Not used to
validate documents on its own. Beyond the identifier, unit, context, range
and alias definitions described above, it defines:

- `entity_base` — the properties every entity has; kind schemas compose it.
  Required: `id`, `kind`, `label`. Optional: `definition` (normative),
  `description` (informative), `aliases`, `status` (`draft` | `provisional` |
  `stable` | `deprecated` | `withdrawn`), `since` (package version
  introducing the identifier), `deprecation` (`deprecated_in`, `replaced_by`,
  `reason`, `removal_planned_in`), `evidence`, `provenance`,
  `external_mappings`, `see_also`, `notes`, `curation_notes` (verbatim
  curation history preserved from source content).
- `entity_ref` — a CURIE or CURIE `#symbol` fragment.
- `reference_id` — a persistent-identifier scheme prefix: `doi:`, `pmid:`,
  `pmcid:`, `isbn:`, `arxiv:`, `url:`.
- `semver`, `version_constraint` — see below.
- `quantity` — `value` (number), optional `unit`,
  `uncertainty` (≥ 0), `uncertainty_type` (`sd` | `se` |
  `ci95_halfwidth` | `range_halfwidth` | `unspecified`).
- `external_mapping` — a mapping to an external terminology (LOINC,
  SNOMED CT, UBERON, OBA, ...): `system`, `code`, `relation` (`exact` |
  `close` | `broad` | `narrow` | `related`), `verified`, `note`. Mappings
  must not be invented.

**Version constraints.** `version_constraint` is a whitespace-separated set
of comparators (`>=`, `>`, `<=`, `<`, `=`, `^`, `~`) combined with AND;
alternatives separated by `||`. `^1.2.3` means `>=1.2.3 <2.0.0`;
`^0.2.3` means `>=0.2.3 <0.3.0`; `~1.2.3` means `>=1.2.3 <1.3.0`; a bare
version means `=`; partial versions (`1.2`) pad with zeros.

## document.schema.json

A YAML/JSON file listed in a package manifest's `contents`. Contains entities
(discriminated by `kind`, each validated against its kind schema) and/or
bibliographic `references` (each against `reference.schema.json`); at least
one of the two arrays is required. Required envelope keys: `ocpe`, `package`
(see [The document envelope](#the-document-envelope)). Optional: `title`,
`description`, `provenance`, `curation_notes`. No other top-level properties
besides `x-` extensions.

## package.schema.json

The manifest of an independently versioned domain package. The package `id`
is also the CURIE namespace of every entity the package defines.

Required: `id`, `name`, `version` (semver), `ocpe_spec` (version constraint
on the specification versions the package conforms to, e.g.
`">=0.1.0 <0.2.0"`), `description`, `contents` (package-relative document
paths, in load order, at least one). Optional: `status`, `license` (SPDX
expression or `UNSPECIFIED`), `maintainers` (`name`, optional `email`, `url`,
`kind`: `human` | `organization` | `ai_agent`), `keywords`, `homepage`,
`changelog` (path; missing file is a validation warning), `provenance`,
`deprecation` (`reason`, optional `replaced_by`), `notes`.

Dependencies:

- `dependencies` — packages whose identifiers this package references, as
  `{package, version, reason?}`. **References to undeclared packages are
  validation errors.** Version constraints use the
  [version-constraint grammar](#commonschemajson). Self-dependencies are
  errors and the dependency graph must be acyclic.
- `optional_dependencies` — packages that enrich this package if present but
  are not required to interpret it.

The `core` vocabulary package need not be declared. Example:

```yaml
id: example-org
name: Example Org Package
version: "1.0.0"
ocpe_spec: ">=0.1.0 <0.2.0"
description: Synthetic example package for documentation (no scientific content).
dependencies:
  - {package: example-base, version: ">=1.0.0 <2.0.0", reason: shared quantities}
contents:
  - variables.yaml
  - relationships.yaml
```

Content paths are security-relevant: they must be package-relative, must not
traverse outside the package root (`..`), and must not escape it via symlinks.
The loader rejects violating packages.

## concept.schema.json

An unquantified physiological entity: system, structure, process, mechanism
or phenomenon. Concepts are **not** variables — they carry no unit or value;
quantities associated with a concept are separate variable /
latent_construct / derived_metric entities.

Required: `id`, `kind` (`concept`), `label`, `concept_type`. `concept_type`:
`organ_system` | `anatomical_structure` | `physiological_process` |
`mechanism` | `phenomenon` | `cell_type` | `molecular_entity` | `other`.
Optional: `broader`, `part_of` (arrays of concept CURIEs).

```yaml
- id: ocpe:example-org/flow-loop
  kind: concept
  label: Flow loop
  concept_type: mechanism
  definition: "Placeholder concept supplied by the example package."
```

## variable.schema.json

A quantifiable, time-varying property measurable in principle (a rate, a
pressure, a volume). A variable is independent of how it is measured (see
`measurement_method`) and of any recorded value (see `observation`).

Required: `id`, `kind` (`variable`), `label`, `dimension` (a named dimension
from `units.yaml`), `canonical_unit`. Optional: `accepted_units`, `value_type`
(`continuous` | `discrete` | `ordinal` | `categorical` | `boolean`),
`observability` (`directly_measurable` | `indirectly_measurable` |
`invasive_only` | `model_compartment` — the last marks lumped-model
abstractions whose physiological counterpart is approximate; say so in the
local-id or definition), `system` (concept CURIE), `reference_ranges`.

Unit is a representation choice: the same variable may be expressed in any
registered unit of its dimension; `canonical_unit` is the preferred one.

```yaml
- id: ocpe:example-org/flow-rate
  kind: variable
  label: Flow rate
  dimension: volume_flow
  canonical_unit: mL/s
  accepted_units: [mL/s, L/min]
  observability: directly_measurable
  aliases:
    - {value: FR, type: symbol, unit: mL/s}
```

## latent-construct.schema.json

A theoretical quantity not directly observable even in principle (a
capacity index, a composite score). Values are always
estimates conditional on an operationalization and must never be exchanged as
if they were measurements.

Required: `id`, `kind` (`latent_construct`), `label`, `dimension`,
`canonical_unit`. Optional: `scale` (`scale_type`: `normalized` | `index` |
`ordinal` | `ratio` | `interval` | `unspecified`; `min`, `max`,
`interpretation`), `operationalizations` (`description` required; optional
`indicators` (entity refs), `model` (CURIE), `evidence`),
`theoretical_basis`, `system`, `reference_ranges`.

The validator rejects an observation record that reports a latent construct
with `value_kind: measured`; use `estimated`.

```yaml
- id: ocpe:example-org/capacity-index
  kind: latent_construct
  label: Capacity index
  dimension: dimensionless
  canonical_unit: "1"
  scale: {scale_type: normalized, min: 0, max: 1}
```

## derived-metric.schema.json

A quantity computed by a defined algorithm from other quantities or
observation series. The computation — including window length and artifact
handling — is part of the metric's meaning and must be declared.

Required: `id`, `kind` (`derived_metric`), `label`, `derived_from` (array of
entity refs, at least one), `computation`, `dimension`, `canonical_unit`.
`computation` requires `method` and allows `formula` (LaTeX or plain text),
free-form `parameters`, `input_requirements`, and `references`
(persistent-id references, subject to the evidence integrity rule).
Optional: `reference_ranges`.

```yaml
- id: ocpe:example-org/windowed-spread
  kind: derived_metric
  label: Windowed spread index
  derived_from: [ocpe:example-org/flow-rate]
  computation:
    method: root-mean-square of successive differences over a stated window
    formula: "\\sigma_{window} = \\sqrt{\\frac{1}{N-1} \\sum_{i=1}^{N-1} (x_{i+1} - x_i)^2}"
    input_requirements: clean, evenly sampled series; stated window length
  dimension: time
  canonical_unit: ms
```

## measurement-method.schema.json

A device, assay, procedure or signal-processing pipeline by which a quantity
is observed. Performance characteristics are context-qualified: agreement
statistics measured in one population or activity do not transfer
automatically to another. Device catalogs live in external packages; the core
only defines the shape.

Required: `id`, `kind` (`measurement_method`), `label`, `method_type`
(`device` | `assay` | `imaging` | `questionnaire` | `clinical_procedure` |
`signal_processing` | `other`). Optional: `modality`, `manufacturer`,
`device_model`, `measures` (`target` entity ref + `mode`: `direct` |
`estimated` | `derived`), `specifications` (`name`, `value`, `unit`, `note`),
`performance` (context-qualified metric blocks: `metrics` with named
statistics such as `icc`, `pearson_r`, `bias`, `loa_lower`/`loa_upper`,
`mae`, `rmse`, `ccc`, ...; `reference_method`; `evidence`), `failure_modes`,
`artifact_handling`.

The observation validator checks that a record's `method` resolves to a
`measurement_method`, and — when the method declares `measures` — that the
recorded quantity is among its targets with a compatible mode.

## observation.schema.json

The exchange contract for a single value of a quantity (see
`docs/observation-exchange.md`). Required: `quantity` (variable,
latent_construct or derived_metric CURIE), `value` (number, string or
boolean), `unit` (registered UCUM code), `value_kind` (`measured` |
`estimated` | `derived` | `simulated` | `self_reported`). `simulated`
requires `model` (CURIE). Optional: `observation_id`, `time` (ISO 8601
timestamp or interval), `subject` (opaque, non-identifying), `method`
(entity ref), `model`, `context`, `quality` (`flag`: `good` |
`questionable` | `artifact` | `missing`), `provenance`, and the uncertainty
fields `uncertainty` (≥ 0), `uncertainty_type` (`sd` | `se` |
`ci95_halfwidth` | `range_halfwidth` | `unspecified`) and
`uncertainty_unit` (must share the value unit's dimension).

`value_kind` makes synthetic (simulated) data and latent-construct estimates
explicitly distinguishable from measurements. The engine's
`validate_observation` checks, beyond schema conformance: the quantity
resolves and is a quantity kind; latent constructs are not `measured`; the
unit matches the quantity's dimension; the value is compatible with the
quantity's `value_type`; `method` and `model` resolve to the right entity
kinds; the method declares the quantity; timestamps parse; uncertainty units
are dimension-consistent.

## model.schema.json

A declarative specification of a mathematical or computational model: its
identity, version (via the owning package), symbols, equations, assumptions,
units, dependencies, validity domain and evidence. **OCPE stores the
specification only; numerical execution belongs to downstream
implementations.**

Required: `id`, `kind` (`model`), `label`, `formalism` (`ode` | `dae` |
`pde` | `algebraic` | `discrete_time` | `agent_based` | `statistical` |
`machine_learning` | `hybrid` | `other`). Optional:

- `scope` — what the model covers, in words.
- `symbols` — `symbol` + `role` (`state` | `parameter` | `input` | `output`
  | `auxiliary` | `constant` | `time`); optional `label`, `description`,
  `unit`, `represents` (OCPE entity the symbol represents — the symbol unit
  is checked against that entity's dimension), `nominal_value` (a curated
  specification datum with provenance, not a solver setting), `value_range`,
  `evidence`, `curation_status`, `curation_note`.
- `equations` — `id` + `expression_latex`; optional `form`, `inputs`,
  `parameters`, `outputs` (all must name declared symbols), `description`,
  `evidence`.
- `assumptions`, `limitations` — arrays of strings; `validity_domain` — array
  of context objects.
- `source` — `references` (persistent ids) and/or `upstream_implementation`
  (repository, commit, language, license, citation requirement) for the code
  a specification was derived from.
- `implementations` — registered executors (name, repository, language,
  status, conformance note). Referenced, never contained.

## relationship.schema.json

A typed, directed assertion `subject PREDICATE object` between OCPE entities,
optionally with a functional form, a pointer to model equations, applicable
contexts and evidence.

Required: `id`, `kind` (`relationship`), `label`, `subject` (entity ref),
`predicate`, `object` (entity ref). `predicate` is a core token (e.g.
`REGULATES`) or a predicate CURIE (`ocpe:core/regulates`); domain packages
may define additional predicates. Optional: `functional_form` (core token or
CURIE), `direction_of_effect` (`positive` | `negative` | `non_monotonic` |
`none` | `unknown`), `mathematical_specification` (`model` CURIE, `equations`
ids, `expression`), `confidence` (`value` + `scale`), `applicable_contexts`,
`known_limitations`.

The validator checks the predicate against the core (or declared package)
vocabulary and warns when the object kind falls outside a predicate's
declared `object_kinds`.

## predicate.schema.json

A relationship type in the core vocabulary (`specification/core/predicates.yaml`):
`CAUSES`, `INCREASES`, `DECREASES`, `REGULATES`, `DERIVED_FROM`,
`MEASURED_BY`, `ESTIMATED_BY`, `VALIDATED_BY`, `PERTURBED_BY`,
`MODULATED_BY`, `PART_OF`, `ASSOCIATED_WITH`. Required: `id`, `kind`
(`predicate`), `label`, `token` (UPPER_SNAKE). Optional: `subject_kinds`,
`object_kinds`, `inverse`, `causal`, `transitive`, `definition`.

## functional-form.schema.json

A named qualitative/mathematical shape of a dependency used to qualify
relationships without embedding executable code. The core registers only
genuinely generic primitives — `linear`, `first_order_lag`, `qualitative`
(`specification/core/functional-forms.yaml`); domain-specific forms
(sigmoids, hydrostatic relations, kinetics, ...) are `functional_form`
entities defined by external domain packages. Required: `id`, `kind`
(`functional_form`), `label`, `token` (lower_snake). Optional:
`expression_latex`, `parameters`, `monotonicity`.

## evidence.schema.json

See [Evidence statements](#evidence-statements). Required: at least one of
`references`, `citation`, `basis`. Other schemas reference its
`curation_status` definition.

## reference.schema.json

A bibliographic record identified by a persistent id. Required: `id`
(`doi:`/`pmid:`/`pmcid:`/`isbn:`/`arxiv:`/`url:`). Optional: `doi`, `pmid`,
`pmcid`, `arxiv`, `url`, `title`, `authors`, `year` (1600–2100), `venue`,
`citation` (verbatim), `study_type` (RCT, systematic_review, meta_analysis,
narrative_review, observational_human, experimental_human, case_series,
animal, in_vitro, in_silico, device_validation, guideline, textbook, dataset,
other), `sample_size`, `summary_document` (path or URL of a structured
review, stored by the package maintainer), `verification` (`status`:
`verified` | `unverified` | `disputed` | `fabrication_suspected` |
`retracted`; `method`, `date`, `notes`), `notes`.

Fields must be transcribed from the source, never inferred. Records are
declared per document and cited by evidence claims; the validator enforces
that every citation resolves to a declared record.

## provenance.schema.json

Where content came from and how it was produced. Optional: `derived_from`
(`source` path/URL, `git_ref`, `sha256`, `legacy_id`, `legacy_version`,
`transformation`), `contributors` (`name`, `kind`: `human` | `ai_agent` |
`tool` | `organization`, `role`, `identifier`), `created`, `modified`, `notes`.
Provenance is descriptive; it does not imply review or approval.

## The `core` package

`specification/core/package.yaml` defines the `core` package (predicate
vocabulary + functional forms), which the engine always loads. Its manifest
provenance is empty by design: the core is authored natively in OCPE 0.1.
