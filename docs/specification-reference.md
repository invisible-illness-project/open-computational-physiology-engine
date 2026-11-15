# OCPE Specification Reference

Reference for the OCPE 0.1 schemas and the shared machinery they rely on:
identifiers, units, context, reference ranges and evidence. The JSON Schemas
in `specification/schemas/` are the normative contract (draft-07 of JSON
Schema); this document describes them for authors of packages, tools and AI
agents. Where this document and a schema disagree, the schema wins.

Authoring format is YAML 1.2 (JSON is equally valid). Unless noted, every
schema allows `x-` prefixed extension keys and forbids undeclared properties.

**Status of validation.** Conformance to these schemas establishes that
content is well-formed, internally consistent and resolvable. It does not
establish scientific validity (`specification/core/meta.yaml`,
`statement_of_scope`).

## The document envelope

Every content file listed in a package manifest's `contents` is a document
(`document.schema.json`) with the envelope:

```yaml
ocpe: "0.1"            # specification major.minor the document is written against
package: cardiovascular  # the owning package id; equals the CURIE namespace
title: Cardiovascular variables
entities: [ ... ]      # at least one of entities / references is required
references: [ ... ]
```

The `ocpe:` marker is checked against the engine's readable document versions
(`reads_documents` in `specification/versions/compatibility.yaml`); for
specification 0.1.0 the marker is `"0.1"`. A document must not claim a
`package` different from the manifest that lists it.

## Entity discrimination by `kind`

Entities in a document's `entities` array are discriminated by their `kind`
field; the document schema dispatches each entry to the schema for its kind.
The entity kinds are: `concept`, `variable`, `latent_construct`,
`derived_metric`, `measurement_method`, `condition`, `intervention`,
`population`, `model`, `relationship`, plus the core-vocabulary kinds
`predicate` and `functional_form`. The kinds are distinct and must never be
used interchangeably (`specification/core/kinds.yaml` states the deciding
tests; the kind schemas enforce them).

`observation` is not a package entity kind. It is a standalone exchange
record validated by `observation.schema.json` and the engine's
`validate_observation` entry point (see [observation.schema.json](#observationschemajson)).

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
  segments (`cardiovascular`, `conditions.pots`).
- `local-id` — kebab-case (`heart-rate`).

Examples: `ocpe:cardiovascular/heart-rate`,
`ocpe:conditions.pots/neuropathic-pots`, `ocpe:core/regulates`. Only the
package whose `id` equals the namespace may define identifiers in it. The
`ocpe:` prefix expands to `https://w3id.org/ocpe/id/`; the persistent-URL
registration is pending, so the CURIE is currently the only normative form.

**Model symbol fragments.** A symbol declared inside a model specification is
referenced as `<model-curie>#<symbol>`, e.g.
`ocpe:models.baroreflex-geddes-2022/baroreflex-geddes-2022#RalpM`. Symbols
are case-sensitive and meaningful only inside the declaring model; a symbol
is not a physiological identifier, though it may *represent* one via the
model symbol's `represents:` field. Entity ids must never contain `#`
fragments.

**Stability rules.** Identifiers are permanent and never reused; a meaning
change requires a new identifier. Retirement is deprecation, not deletion:
`status: deprecated` plus a `deprecation` block (`deprecated_in`, `reason`,
optional `replaced_by`, `removal_planned_in`) for at least one minor release
before removal in a major release. Labels and aliases may change in minor
releases; canonical identifiers may not.

**Aliases** map other names onto canonical identifiers (case-sensitive;
`scope` restricts where they are unique; `unit` marks an alias that denotes
the same quantity in a different unit — `Hc` and `HR` both resolve to
`ocpe:cardiovascular/heart-rate`, one in beats/s, one in beats/min). An
unscoped lookup matching several entities is an ambiguity error, never a
guess. Alias `type` is one of `symbol`, `synonym`, `abbreviation`,
`legacy-id`, `label`.

## Units

Units are written as **registered UCUM case-sensitive codes**
(`https://ucum.org`): `mm[Hg]`, `mL/s`, `/min`, `1`. The normative list is
`specification/core/units.yaml`, which maps each code to a named dimension
and a `to_reference` conversion factor. The engine uses this table for
dimensional-consistency checks; it is **not** a general-purpose UCUM
implementation — every unit used in OCPE content must be registered (legacy
spellings such as `mmHg` or `bpm` normalize to their registered codes), and
new units are added to the registry before use. Dimension vectors use
exponents of L, M, T and the OCPE pseudo-dimension EVT (countable events),
which keeps `beats/min` (event rate) distinguishable in intent from generic
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

Recognized keys: `population` (population entity reference or free text),
`health_status`, `age_range` (`min`, `max`, `unit`), `sex`
(`female` | `male` | `any` | `mixed` | `unspecified`), `posture`,
`activity`, `setting`, `measurement_method` (entity reference or
description), `model` (CURIE), and `scope_note` — a plain-language statement
of what the qualifying context is and is not. Additional dimensions may be
added with string, number or boolean values. At least one property is
required.

```yaml
context:
  population: ocpe:populations/healthy-control-cohort
  posture: seated
  activity: rest
  scope_note: "Healthy adults at seated rest; does not apply during exercise."
```

## reference_range and range types

A `reference_range` is a context-qualified range of values. Required:
`range_type`, `unit`, `context`; at least one of `min`/`max`; optional
`evidence`, `notes`.

The `range_type` enum distinguishes five things that must never be conflated:

- `reference_interval` — a population reference interval (e.g. the central
  95% of a stated population).
- `plausibility_bound` — an engineering/physiological plausibility bound on
  a value. Many migrated ranges are of this kind: they come from legacy
  `valid_range` fields and are explicitly *not* population reference
  intervals.
- `clinical_threshold` — a cut-off with clinical consequences.
- `model_validity_domain` — the range over which a model is stated to be
  valid.
- `observed_range` — the range actually observed in a stated study sample.

The same five types apply wherever ranges appear (variables, latent
constructs, derived metrics). The validator checks range units against the
entity's dimension and rejects `min > max`; it cannot check that a range was
classified honestly — that is curation responsibility.

```yaml
reference_ranges:
  - range_type: plausibility_bound
    min: 12.0
    max: 240.0
    unit: /min
    context: {scope_note: "Legacy valid_range from the pre-0.1 knowledge base; engineering plausibility bound, not a population reference interval."}
```

## Evidence statements

An `evidence` object (`evidence.schema.json`) is a lightweight, attachable
statement of *what* is supported, *by which references*, at *what strength*.
It can be attached to entities, relationships, reference ranges,
perturbations and other assertions. At least one of `references`, `citation`
or `basis` is required:

- `references` — array of persistent-identifier references (`doi:...`,
  `pmid:...`, `pmcid:...`, `isbn:...`, `arxiv:...`, `url:...`);
- `citation` — human-readable citation text, preserved verbatim;
- `basis` — nature of the evidential basis: `literature`, `definitional`,
  `expert_opinion`, `machine_proposed`, `machine_calibrated`,
  `computational_experiment`, `dataset`. `definitional` is for mathematical
  identities (e.g. HR = 60000/RR) that need no empirical citation.

Key fields: `claim` (the specific proposition supported); `supports` — which
aspect(s) the evidence supports, from `existence`, `direction`, `magnitude`,
`structure`, `association`, `definition`, `mechanism`,
`measurement_validity` (direction-level evidence must never be read as
magnitude-level support); `study_type`; `context`; `curation_status`
(`verified` | `partially_verified` | `unverified` | `machine_proposed` |
`machine_calibrated` | `disputed` | `retracted` | `unknown`); `limitations`;
`notes`.

**Legacy scales, preserved verbatim.** `evidence_level` (`Level 1`–`Level 4`)
and `evidence_tier` (`A`–`D`) are the scales of the pre-0.1 knowledge base,
carried over unchanged — no content was re-graded during migration. Their
definitions are recorded, largely provisional, in
`specification/core/evidence-scales.yaml`: Level 1 is RCT-grade human
evidence, Level 4 is in-silico evidence (both documented); Levels 2–3 are
provisional; tiers A–D are provisional. Prefer `basis` over the level where
both apply (a definitional identity can carry a legacy `Level 1` without any
trial behind it).

```yaml
evidence:
  - claim: "Mean carotid pressure regulates heart rate via the baroreflex."
    supports: [direction, mechanism]
    references: [doi:10.1098/rsif.2022.0220]
    study_type: in_silico
    evidence_level: "Level 4"
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
- `external_mapping` — a verified mapping to an external terminology (LOINC,
  SNOMED CT, UBERON, OBA): `system`, `code`, `relation` (`exact` | `close` |
  `broad` | `narrow` | `related`), `verified`, `note`. Mappings must not be
  invented.
- `model_representation` — how a condition or intervention is represented
  inside a specific model: `model`, `parameter_perturbations`,
  `unverified_parameter_perturbations` (consumers must treat these as inert
  unless explicitly opted in), `constraints`, `validation_criteria`, `notes`.
  A representation is a model-specific hypothesis with its own evidence, not
  a claim about the condition itself.
- `parameter_perturbation`, `representation_constraint`,
  `validation_criterion` — the building blocks of `model_representation`.

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

The `core` vocabulary package need not be declared. Example (abridged from
`packages/cardiovascular/package.yaml`):

```yaml
id: cardiovascular
name: Cardiovascular Physiology
version: "1.0.0"
ocpe_spec: ">=0.1.0 <0.2.0"
dependencies:
  - {package: core, version: ">=0.1.0 <0.2.0", reason: predicate and functional-form vocabulary}
  - {package: populations, version: ">=1.0.0 <2.0.0"}
contents:
  - variables.yaml
  - relationships.yaml
```

## concept.schema.json

An unquantified physiological entity: organ system, anatomical structure,
process, mechanism or phenomenon. Concepts are **not** variables — they carry
no unit or value; quantities associated with a concept are separate
variable / latent_construct / derived_metric entities.

Required: `id`, `kind` (`concept`), `label`, `concept_type`. `concept_type`:
`organ_system` | `anatomical_structure` | `physiological_process` |
`mechanism` | `phenomenon` | `cell_type` | `molecular_entity` | `other`.
Optional: `broader`, `part_of` (arrays of concept CURIEs).

```yaml
- id: ocpe:cardiovascular/baroreflex
  kind: concept
  label: Baroreflex
  concept_type: mechanism
  definition: "Negative-feedback blood pressure regulation via arterial baroreceptors."
```

## variable.schema.json

A quantifiable, time-varying property measurable in principle (heart rate,
arterial blood pressure). A variable is independent of how it is measured
(see `measurement_method`) and of any recorded value (see `observation`).

Required: `id`, `kind` (`variable`), `label`, `dimension` (a named dimension
from `units.yaml`), `canonical_unit`. Optional: `accepted_units`, `value_type`
(`continuous` | `discrete` | `ordinal` | `categorical` | `boolean`),
`observability` (`directly_measurable` | `indirectly_measurable` |
`invasive_only` | `model_compartment` — the last marks lumped-model
abstractions whose physiological counterpart is approximate; scope such
local-ids explicitly), `system` (concept CURIE), `reference_ranges`.

Unit is a representation choice: the same variable may be expressed in any
registered unit of its dimension; `canonical_unit` is the preferred one.
Example (from `packages/cardiovascular/variables.yaml`):

```yaml
- id: ocpe:cardiovascular/heart-rate
  kind: variable
  label: Heart Rate
  dimension: event_rate
  canonical_unit: /min
  accepted_units: [/min, /s]
  observability: directly_measurable
  aliases:
    - {value: Hc, type: symbol, scope: legacy-kb, unit: /s}
    - {value: HR, type: symbol, scope: legacy-kb, unit: /min}
```

## latent-construct.schema.json

A theoretical quantity not directly observable even in principle (sympathetic
tone, hydration state). Values are always estimates conditional on an
operationalization and must never be exchanged as if they were measurements.

Required: `id`, `kind` (`latent_construct`), `label`, `dimension`,
`canonical_unit`. Optional: `scale` (`scale_type`: `normalized` | `index` |
`ordinal` | `ratio` | `interval` | `unspecified`; `min`, `max`,
`interpretation`), `operationalizations` (`description` required; optional
`indicators` (entity refs), `model` (CURIE), `evidence`),
`theoretical_basis`, `system`, `reference_ranges`.

The validator rejects an observation record that reports a latent construct
with `value_kind: measured`; use `estimated`.

```yaml
- id: ocpe:systemic/hydration-state
  kind: latent_construct
  label: Hydration State
  definition: "The relative level of body water, affecting total blood volume and vascular compliance."
  dimension: dimensionless
  canonical_unit: "1"
  scale: {scale_type: normalized, min: 0, max: 1}
  aliases:
    - {value: H_hydr, type: symbol, scope: legacy-kb}
```

## derived-metric.schema.json

A quantity computed by a defined algorithm from other quantities or
observation series (RMSSD, DFA alpha-1). The computation — including window
length and artifact handling — is part of the metric's meaning and must be
declared.

Required: `id`, `kind` (`derived_metric`), `label`, `derived_from` (array of
entity refs, at least one), `computation`, `dimension`, `canonical_unit`.
`computation` requires `method` and allows `formula` (LaTeX or plain text),
free-form `parameters`, `input_requirements`, and `references`
(reference ids). Optional: `reference_ranges`.

Example (from `packages/autonomic/metrics.yaml`):

```yaml
- id: ocpe:autonomic/rmssd
  kind: derived_metric
  label: RMSSD
  derived_from: [ocpe:cardiovascular/rr-interval]
  computation:
    method: "Root mean square of successive differences (time-domain HRV)"
    formula: "RMSSD = sqrt( mean( (RR_{i+1} - RR_i)^2 ) )"
    input_requirements: "RR interval series; sensitive to ectopic beats and motion artifacts."
    references: [doi:10.3390/s22176536]
  dimension: time
  canonical_unit: ms
```

## measurement-method.schema.json

A device, assay, procedure or signal-processing pipeline by which a variable
or derived metric is observed. Performance characteristics are
context-qualified: agreement statistics measured in one population or
activity do not transfer automatically to another.

Required: `id`, `kind` (`measurement_method`), `label`, `method_type`
(`device` | `assay` | `imaging` | `questionnaire` | `clinical_procedure` |
`signal_processing` | `other`). Optional: `modality`, `manufacturer`,
`device_model`, `failure_modes`, `artifact_handling`, plus:

- `measures` — `{target (entity ref), mode, note?}` with `mode`:
  `direct` | `estimated` | `derived`.
- `specifications` — `{name, value?, unit?, note?}` device/procedure
  specifications.
- `performance` — `{context, metrics, target?, reference_method?, evidence?,
  notes?}`; `metrics` entries are `{metric, value, unit?, ci_lower?,
  ci_upper?, note?}` with `metric`: `icc` | `pearson_r` | `spearman_rho` |
  `bias` | `loa_lower` | `loa_upper` | `mae` | `mape` | `rmse` |
  `sensitivity` | `specificity` | `ccc` | `other`. The `context` is
  mandatory — performance without a stated context is not valid OCPE content.

Example (abridged from `packages/wearables/polar-h10.yaml`):

```yaml
- id: ocpe:wearables/polar-h10
  kind: measurement_method
  label: Polar H10 Heart Rate Sensor
  method_type: device
  manufacturer: Polar Electro
  measures:
    - {target: ocpe:cardiovascular/rr-interval, mode: direct}
    - {target: ocpe:cardiovascular/heart-rate, mode: derived}
  performance:
    - target: ocpe:cardiovascular/rr-interval
      reference_method: Standard 12-lead ECG
      metrics:
        - {metric: icc, value: 0.99}
        - {metric: bias, value: 0.05, unit: ms}
      context: {activity: rest, scope_note: "Agreement vs. 12-lead ECG at supine rest; does not transfer to motion."}
```

## observation.schema.json

Exchange format for a single observed, estimated, derived or simulated value
of an OCPE quantity. OCPE defines the record format only; it does not store
observational data. Observations are validated standalone
(`ocpe check-observation`), not as package entities.

Required: `quantity` (CURIE of a variable, derived metric or latent
construct), `value` (number, string or boolean), `unit`, `value_kind`.
`value_kind`: `measured` | `estimated` | `derived` | `simulated` |
`self_reported`. Conditional requirement: `value_kind: simulated` requires
`model` (the CURIE of the model that produced it) — this is what makes
synthetic data explicitly distinguishable from measurements.

Optional: `observation_id`, `time` (ISO 8601 timestamp or interval),
`subject` (opaque, non-identifying identifier), `method` (entity ref),
`model`, `context`, `quality` (`flag`: `good` | `questionable` | `artifact` |
`missing`; `note`), `provenance`.

Semantic checks (`validate_observation`): `quantity` must resolve to a
quantity kind; a latent construct cannot be reported as `measured`; the unit
must match the quantity's dimension.

```yaml
quantity: ocpe:cardiovascular/heart-rate
value: 72
unit: /min
value_kind: measured
time: "2026-11-14T08:30:00Z"
method: ocpe:wearables/polar-h10
context: {posture: supine, activity: rest}
quality: {flag: good}
```

## condition.schema.json

A disease, syndrome, phenotype, exposure or physiological state that alters
physiology. Clinical/physiological claims about the condition are separated
from `model_representations`, which are model-specific hypotheses about how
the condition is encoded in a computational model (see
`model_representation` in [common.schema.json](#commonschemajson)).

Required: `id`, `kind` (`condition`), `label`, `condition_type` (`disease` |
`syndrome` | `phenotype` | `exposure` | `physiological_state`). Optional:
`abbreviation`, `parent` (CURIE), `diagnostic_criteria` (`criterion` plus
optional `evidence`), `association_evidence`, `composability`
(`composable_with` CURIEs, `notes`, `evidence`), `model_representations`,
`unresolved_gaps`.

```yaml
- id: ocpe:conditions.pots/pots
  kind: condition
  label: Postural Orthostatic Tachycardia Syndrome
  abbreviation: POTS
  condition_type: syndrome
  composability:
    composable_with:
      - ocpe:conditions.pots/neuropathic-pots
      - ocpe:conditions.pots/hyperadrenergic-pots
```

## intervention.schema.json

A test, protocol, therapy, drug, behaviour or environmental manipulation
applied to a physiological system. Protocol descriptions are declarative;
executing a protocol in silico is the responsibility of downstream
simulators.

Required: `id`, `kind` (`intervention`), `label`, `intervention_type`
(`diagnostic_protocol` | `therapeutic_protocol` | `pharmacological` |
`behavioral` | `environmental` | `other`). Optional: `purpose`,
`mechanism_of_action`, `targets` (entity refs), `protocol` (`phases` with
`name`, `duration` (quantity), `settings`, `description`; top-level
`parameters`; `notes`), `model_representations`.

```yaml
- id: ocpe:interventions.tilt-test/head-up-tilt-test
  kind: intervention
  label: Head-Up Tilt (HUT) Test
  intervention_type: diagnostic_protocol
  protocol:
    phases:
      - name: supine_rest
        duration: {value: 200.0, unit: s}
      - name: sustained_tilt
        duration: {value: 100.0, unit: s}
        settings:
          - {name: tilt_angle, value: 60.0, unit: deg}
```

## population.schema.json

A description of a group of individuals used to qualify the context of
ranges, evidence and measurement performance. It is a context descriptor,
**not** a generative cohort specification — synthetic cohort generation
belongs to downstream applications.

Required: `id`, `kind` (`population`), `label`. Optional: `health_status`,
`inclusion_criteria`, `exclusion_criteria`, `demographics` (free-form
object), `sample_size` (integer ≥ 0; only for populations denoting a specific
study sample), `source_study` (reference ids).

```yaml
- id: ocpe:populations/pots-clinical-cohort
  kind: population
  label: POTS Clinical Cohort
  health_status: POTS
  sample_size: 25
  inclusion_criteria:
    - "Sustained heart rate increase of >= 30 bpm (or >= 40 bpm for ages 12-19) within 10 minutes of standing/tilt without orthostatic hypotension."
```

## model.schema.json

A declarative specification of a mathematical or computational model:
symbols, equations, assumptions, units, evidence. OCPE stores the
specification only; numerical execution (solvers, step sizes, initialisation,
run orchestration) belongs to implementations, which are referenced but not
contained.

Required: `id`, `kind` (`model`), `label`, `formalism` (`ode` | `dae` |
`pde` | `algebraic` | `discrete_time` | `agent_based` | `statistical` |
`machine_learning` | `hybrid` | `other`). Optional: `scope`, `assumptions`,
`limitations`, `validity_domain` (array of context objects), `source`
(`references`; `upstream_implementation` with `repository`, `commit`,
`language`, `license`, `citation_requirement`), `implementations` (`name` +
`repository`, `language`, `status`, `conformance_note`), plus:

- `symbols` — `{symbol, role, ...}`; `symbol` matches `[A-Za-z_][A-Za-z0-9_]*`
  (case-sensitive, model-local). `role`: `state` | `parameter` | `input` |
  `output` | `auxiliary` | `constant` | `time`. Optional per symbol: `label`,
  `description`, `unit`, `represents` (CURIE of the OCPE entity the symbol
  represents), `nominal_value` (a published/curated specification datum with
  provenance — not a solver setting), `value_range`, `evidence`,
  `curation_status`, `curation_note`.
- `equations` — `{id, expression_latex, ...}`; `id` is `[a-z0-9_]+`.
  Optional: `label`, `form` (`algebraic` | `differential` | `piecewise` |
  `delay_differential` | `stochastic` | `other`), `inputs`, `parameters`,
  `outputs` (lists of symbol names), `description`, `evidence`.

The validator checks that equation inputs/parameters/outputs name declared
symbols, that symbols are not declared twice, and that symbol units match the
dimension of the entity they `represent`. Example (abridged from
`packages/models/baroreflex-geddes-2022`):

```yaml
- id: ocpe:models.baroreflex-geddes-2022/baroreflex-geddes-2022
  kind: model
  label: Closed-Loop Baroreflex Response and Systemic Hemodynamics Model
  formalism: ode
  symbols:
    - symbol: Vau
      role: state
      label: Upper arterial blood volume
      unit: mL
      represents: ocpe:cardiovascular/upper-arterial-volume
  equations:
    - id: upper_arterial_pressure
      form: algebraic
      expression_latex: 'p_{au}(t) = \frac{V_{au}(t)}{C_{au}}'
      inputs: [Vau]
      parameters: [Cau]
      outputs: [pau]
```

## relationship.schema.json

A typed, directed assertion `subject PREDICATE object` between OCPE entities,
optionally qualified by functional form, model equation, context and
evidence. Reading direction is always subject → object.

Required: `id`, `kind` (`relationship`), `label`, `subject` (entity ref),
`predicate`, `object` (entity ref). `predicate` accepts an uppercase token
from the core vocabulary (`REGULATES`) or its CURIE
(`ocpe:core/regulates`). Optional: `functional_form` (token or CURIE from the
functional-form registry), `direction_of_effect` (`positive` | `negative` |
`non_monotonic` | `none` | `unknown`), `mathematical_specification` (`model`
CURIE, `equations`, `expression`), `confidence` (`value` + `scale` —
scales are free-form strings, e.g. a legacy `0-10` scale), `applicable_contexts`
(array of context objects), `known_limitations`.

The validator requires the predicate to be registered in the core vocabulary
and checks declared `object_kinds` restrictions as warnings. Example (from
`packages/cardiovascular/relationships.yaml`):

```yaml
- id: ocpe:cardiovascular/pcm-regulates-heart-rate
  kind: relationship
  label: Mean carotid pressure regulates heart rate
  subject: ocpe:cardiovascular/mean-carotid-pressure
  predicate: REGULATES
  object: ocpe:cardiovascular/heart-rate
  evidence:
    - claim: "Mean carotid pressure regulates heart rate via the baroreflex."
      supports: [direction, mechanism]
      references: [doi:10.1098/rsif.2022.0220]
      study_type: in_silico
      evidence_level: "Level 4"
```

## predicate.schema.json

A relationship type in the core predicate vocabulary
(`specification/core/predicates.yaml`, package `core`). Predicates are
entities so that relationships can reference them by CURIE.

Required: `id`, `kind` (`predicate`), `label`, `token` (uppercase
`[A-Z][A-Z_]*`). Optional: `subject_kinds`, `object_kinds` (kind strings
restricting the relationship endpoints), `inverse`, `causal`, `transitive`.

The registered vocabulary (unchanged from the legacy v3.2 relationships
file): `CAUSES`, `INCREASES`, `DECREASES`, `REGULATES` (causal feedback),
`DERIVED_FROM` (mathematical or direct physical derivation, non-causal),
`MEASURED_BY` (object: measurement methods), `ESTIMATED_BY` (object:
measurement methods or models), `VALIDATED_BY` (links to a validation
dataset), `PERTURBED_BY` (object: conditions or interventions), `MODULATED_BY`
(e.g. circadian or behavioural modulation), `PART_OF` (structural
containment; transitive), `ASSOCIATED_WITH` (correlation without causal
proof).

```yaml
- id: ocpe:core/regulates
  kind: predicate
  token: REGULATES
  label: regulates
  definition: "An active feedback control loop relationship (e.g., baroreflex regulates heart rate)."
  causal: true
```

## functional-form.schema.json

A named qualitative or mathematical shape of a dependency, used to qualify
relationships without embedding executable code. Registered in
`specification/core/functional-forms.yaml`; the first four tokens close a
legacy registry gap (they were used as relationship types but never
registered).

Required: `id`, `kind` (`functional_form`), `label`, `token`
(`[a-z][a-z0-9_]*`). Optional: `expression_latex`, `parameters`,
`monotonicity` (`increasing` | `decreasing` | `non_monotonic` |
`depends_on_parameters`).

Registered forms: `sigmoid_hill`, `gravity_hydrostatic`,
`inverse_proportional`, `inverse_nonlinear`, `first_order_lag`, `linear`,
`qualitative` (direction only; no functional form implied). Expressions are
generic templates; model-specific equations live in model specifications.

```yaml
- id: ocpe:core/first-order-lag
  kind: functional_form
  token: first_order_lag
  label: First-order lag
  expression_latex: '\frac{dx}{dt} = \frac{x_{target} - x}{\tau}'
  parameters: [tau]
  monotonicity: depends_on_parameters
```

## evidence.schema.json

The evidence statement, described in detail in
[Evidence statements](#evidence-statements): at least one of `references`,
`citation`, `basis`; `claim`; `supports` (one or more of `existence`,
`direction`, `magnitude`, `structure`, `association`, `definition`,
`mechanism`, `measurement_validity`); `study_type`; `context`;
`evidence_level` (`Level 1`–`Level 4`, legacy, provisional definitions);
`evidence_tier` (`A`–`D`, legacy, provisional); `curation_status`;
`limitations`; `notes`.

The schema is deliberately independent of review workflows and authorization
policies (those live in the optional governance extension). Structural
validity of an evidence statement says nothing about its scientific
correctness.

## reference.schema.json

Bibliographic record for a source cited by evidence statements. Required:
`id` (a `reference_id`: `doi:`, `pmid:`, `pmcid:`, `isbn:`, `arxiv:` or
`url:` prefixed persistent identifier). Fields must be transcribed from the
source, never inferred. Optional: `doi`, `pmid`, `pmcid`, `arxiv`, `url`,
`title`, `authors`, `year` (1600–2100), `venue`, `citation` (formatted
citation preserved verbatim), `study_type` (see below), `sample_size`,
`summary_document` (repository-relative path to a structured literature
review in `evidence/references/`), `verification` (`status`: `verified` |
`unverified` | `disputed` | `fabrication_suspected` | `retracted`; `method`,
`date`, `notes`).

`study_type`: `randomized_controlled_trial`, `systematic_review`,
`meta_analysis`, `narrative_review`, `observational_human`,
`experimental_human`, `case_series`, `animal`, `in_vitro`, `in_silico`,
`device_validation`, `guideline`, `textbook`, `dataset`, `other`.

```yaml
- id: doi:10.1098/rsif.2022.0220
  doi: 10.1098/rsif.2022.0220
  pmid: "36069002"
  title: "Postural orthostatic tachycardia syndrome explained using a baroreflex response model"
  citation: "Geddes JR, Ottesen JT, Mehlsen J, Olufsen MS. J R Soc Interface 2022;19:20220220."
  study_type: in_silico
  summary_document: evidence/references/geddes_2022_baroreflex_pots.md
```

## provenance.schema.json

Where a piece of specification content came from and how it was produced.
Provenance is descriptive; it does not imply review or approval.

Optional: `derived_from` (entries require `source` — a repository-relative
path or URL — and allow `git_ref`, `sha256` (64 hex chars), `legacy_id`,
`legacy_version`, `transformation`, a free-text note on what was changed);
`contributors` (`name` plus `kind`: `human` | `ai_agent` | `tool` |
`organization`; `role`; `identifier` — ORCID, URL or model identifier);
`created`, `modified` (dates); `review_manifest` (repository-relative path to
a governance sidecar covering this content); `notes`.

```yaml
provenance:
  derived_from:
    - source: knowledge_base/physiology/variables.yaml
      git_ref: pre-architectural-refactor
      legacy_version: "1.0"
      transformation: "variables[] -> variable entities; units converted to UCUM codes."
  review_manifest: packages/cardiovascular/variables.yaml.review.yaml
```

## governance/review-manifest.schema.json

**Optional extension (ADR 0001).** A sidecar file `<asset>.review.yaml`
recording review events, claims, challenges, adjudication, human review and
authorization for one content-addressed asset. None of its layers is
required to load, validate or resolve OCPE packages, and the core engine has
no import dependency on the governance tooling.

Required: `review_manifest_version` (`2.x.x`), `target_file` (`path` plus
`sha256`; the content hash binds every review to the exact content snapshot —
changed content makes prior validation evidence stale; `previous_paths`
records earlier locations for provenance continuity). The manifest has three
separable layers:

1. **Review records** — `reviews` (events with `review_id`, `reviewed_at`,
   `reviewer` (`kind`: `validator` | `ai_agent` | `human`, plus an `identity`
   with name/version/model/provider details and an `independence_group`;
   `verdict`: `PASSED` | `SUPPORTED` | `DISPUTED` | `PASSED_WITH_WARNINGS` |
   `NEEDS_REVISION` | `REJECTED` | `APPROVED` | `ABSTAIN` | `FAILED` |
   `NEUTRAL`; `confidence` 0–1; `findings` with `severity` `INFO` |
   `WARNING` | `CRITICAL`); `claims` (with `status`: `UNREVIEWED` |
   `SUPPORTED` | `DISPUTED` | `UNRESOLVED`, linked to supporting and
   challenging reviews); `challenges` (`status`: `OPEN` |
   `UNDER_INVESTIGATION` | `RESOLVED_SUPPORT` | `RESOLVED_REJECTION` |
   `UNRESOLVED`); `adjudication` (`status`: `NOT_REQUIRED` | `OPEN` |
   `IN_PROGRESS` | `RESOLVED_SUPPORT` | `RESOLVED_REJECTION`; adjudication
   may not erase previous review events); `human_review` (`status`:
   `NOT_REVIEWED` | `REVIEWED` | `APPROVED` | `REJECTED` | `QUALIFIED`).
2. **Derived summary** — `validation`: `state` (`UNREVIEWED` |
   `DETERMINISTICALLY_VALID` | `AGENT_REVIEWED` | `AGENT_SUPPORTED` |
   `AGENT_DISPUTED` | `ADJUDICATION_REQUIRED` | `COMPUTATIONALLY_REPRODUCED` |
   `HUMAN_REVIEWED` | `HUMAN_APPROVED` | `STALE`) plus `deterministic`,
   `agent_evidence`, `computational` detail and an `explanation`. Recomputable
   from layer 1; the underlying evidence is preserved rather than collapsed
   into a single verdict.
3. **Authorization** — per-use decisions `{status, reason}` with `status`:
   `ALLOWED` | `ALLOWED_WITH_DISCLOSURE` | `REQUIRES_HUMAN_APPROVAL` |
   `PROHIBITED`. Produced by an organization-specific policy; human
   authorization is separate from evidence state (per ADR 0001, human review
   is a higher-trust provenance and authorization layer, not a universal
   prerequisite for scientific progress).

One compatibility note: human-review `verdict: PASSED` occurs in legacy
manifests only and is **not** treated as approval.

```yaml
review_manifest_version: "2.0.0"
target_file:
  path: packages/cardiovascular/variables.yaml
  sha256: "..."
reviews: []
human_review:
  status: NOT_REVIEWED
validation:
  state: DETERMINISTICALLY_VALID
authorization:
  exploratory_research: {status: ALLOWED}
  iip_production: {status: REQUIRES_HUMAN_APPROVAL}
```
