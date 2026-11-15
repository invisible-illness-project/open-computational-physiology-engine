# OCPE Ontology

This document describes the OCPE 0.1 ontology: the taxonomy of entity kinds,
the relationship predicate vocabulary, the functional forms, and the
identifier system. It replaces the pre-0.1 ontology documentation, which
described a single undifferentiated concept graph with ad hoc relationship
types; OCPE 0.1 replaces that with typed, schema-enforced entity kinds and a
closed, registered vocabulary of predicates and functional forms.

## Entity kinds

OCPE distinguishes eleven content kinds. They are **not interchangeable**:
the JSON Schemas enforce the distinctions, and the decision test — not
surface resemblance — decides which kind an item belongs to. Two further
kinds, `predicate` and `functional_form`, exist only in the core vocabulary
(`specification/core/predicates.yaml`, `specification/core/functional-forms.yaml`)
and name the vocabulary used by `relationship` entities.

The decision tests, from `specification/core/kinds.yaml`:

| Kind | Test | Example |
|---|---|---|
| `concept` | An entity with no unit or value (organ system, structure, process, mechanism). | `ocpe:cardiovascular/baroreflex` |
| `variable` | A quantity that can, at least in principle, be measured directly or indirectly, independent of method and value. | `ocpe:cardiovascular/heart-rate` |
| `latent_construct` | A theoretical quantity that cannot be observed even in principle; values are always model- or indicator-conditional estimates. | `ocpe:autonomic/sympathetic-tone` |
| `derived_metric` | A quantity defined by an algorithm applied to other quantities or series (window, artifact handling matter). | `ocpe:autonomic/rmssd` |
| `measurement_method` | A device, assay, procedure or processing pipeline that produces observations; carries context-qualified performance. | `ocpe:wearables/polar-h10` |
| `observation` | A single reported value of a quantity at a time, with `value_kind` (measured/estimated/derived/simulated). OCPE defines the format only and stores no observations. | `{quantity: ocpe:cardiovascular/heart-rate, value: 72, unit: /min, value_kind: measured}` |
| `condition` | A disease, syndrome, phenotype, exposure or state that alters physiology. | `ocpe:conditions.pots/neuropathic-pots` |
| `intervention` | A test, protocol, therapy, drug, behaviour or environmental manipulation. | `ocpe:interventions.tilt-test/head-up-tilt-test` |
| `population` | A group description used to qualify context; not a cohort generator. | population descriptors in `packages/populations/` |
| `model` | A declarative computational model specification (symbols, equations, assumptions, units, evidence) — never solver code. | `ocpe:models.baroreflex-geddes-2022/baroreflex-geddes-2022` |
| `relationship` | A typed directed assertion between entities. | relationships in `packages/*/relationships.yaml` |
| `predicate` | (Core vocabulary) a named relationship type from the predicate vocabulary below. | `ocpe:core/causes` |
| `functional_form` | (Core vocabulary) a named shape of dependency used to qualify relationships. | `ocpe:core/sigmoid-hill` |

The two decision boundaries that matter most:

- **Measurable in principle, independent of method** → `variable`. This
  includes quantities that are only indirectly measurable (e.g. total
  systemic blood volume by indicator dilution).
- **Defined by an algorithm** → `derived_metric`. RMSSD is a function of a
  windowed RR series and artifact handling; it is not the series itself.
- **Not observable even in principle** → `latent_construct`. Any number
  attached to it is an estimate conditional on a model or indicator set,
  never a measurement.
- **Devices and pipelines** → `measurement_method`. A sensor does not become
  part of the quantity it measures; it produces observations, and its
  accuracy is context-qualified.
- **Single reported values** → `observation`, of which OCPE defines only the
  exchange format (`observation.schema.json`). OCPE stores no observational
  data.

## Legacy concept classes

The pre-0.1 knowledge base used 17 concept classes. Their disposition is
recorded in the `legacy_concept_classes` mapping in
`specification/core/kinds.yaml`:

| Legacy class | Maps to | Note |
|---|---|---|
| `PhysiologicalVariable` | `variable` | Legacy class conflated variables, derived metrics and model compartments; split per item during migration. |
| `LatentState` | `latent_construct` | Legacy items that are measurable in principle (e.g. total blood volume, peripheral resistance) were reclassified as variables; see `docs/migration-guide.md`. |
| `OrganSystem` | `concept` (`concept_type: organ_system`) | |
| `Organ` | `concept` (`concept_type: anatomical_structure`) | |
| `Mechanism` | `concept` (`concept_type: mechanism`) | |
| `Process` | `concept` (`concept_type: physiological_process`) | |
| `Measurement` | `observation` | |
| `Sensor` | `measurement_method` | |
| `MathematicalEquation` | `model` | Equations are parts of model specifications. |
| `Disease` | `condition` | |
| `Intervention` | `intervention` | |
| `Medication` | `intervention` (`intervention_type: pharmacological`) | |
| `Behavior` | `intervention` (`intervention_type: behavioral`) | |
| `Population` | `population` | |
| `ValidationDataset` | `reference` | Represented as a reference with `study_type` 'dataset'. |
| `Publication` | `reference` | |
| `Evidence` | `evidence` | Evidence is an attached statement (`evidence.schema.json`), not an entity. |

Note that two legacy classes map to things that are not entity kinds at all:
`Publication` and `ValidationDataset` map to `reference` records, and
`Evidence` maps to the evidence statement structure that can be attached to
any assertion.

## Relationship predicates

Relationships are typed directed assertions, read as **subject PREDICATE
object** — e.g. "sympathetic tone MODULATED_BY circadian drive" means
sympathetic tone is modulated by circadian drive. The predicate vocabulary
carries the twelve predicates of the legacy `relationships.yaml` (v3.2)
verbatim into registered core entities. Each predicate records whether it is
causal, and some constrain the kind of entity allowed as object; the
validator enforces the core vocabulary and warns on object-kind mismatches.

| Predicate | Token | Causal | Object kinds (if constrained) |
|---|---|---|---|
| `ocpe:core/causes` | `CAUSES` | yes | |
| `ocpe:core/increases` | `INCREASES` | yes | |
| `ocpe:core/decreases` | `DECREASES` | yes | |
| `ocpe:core/regulates` | `REGULATES` | yes | |
| `ocpe:core/derived-from` | `DERIVED_FROM` | no | |
| `ocpe:core/measured-by` | `MEASURED_BY` | no | `measurement_method` |
| `ocpe:core/estimated-by` | `ESTIMATED_BY` | no | `measurement_method`, `model` |
| `ocpe:core/validated-by` | `VALIDATED_BY` | no | |
| `ocpe:core/perturbed-by` | `PERTURBED_BY` | yes | `condition`, `intervention` |
| `ocpe:core/modulated-by` | `MODULATED_BY` | yes | |
| `ocpe:core/part-of` | `PART_OF` | no (transitive) | |
| `ocpe:core/associated-with` | `ASSOCIATED_WITH` | no | |

Definitions (verbatim from the registry): `CAUSES` — a directly causal
biological link where changes in subject lead to changes in object.
`INCREASES` — positive directional modulation. `DECREASES` — negative
directional modulation. `REGULATES` — an active feedback control loop
relationship. `DERIVED_FROM` — a mathematical or direct physical derivation.
`MEASURED_BY` — a sensor directly measures a physical variable.
`ESTIMATED_BY` — a variable estimated via proxy sensor measurements.
`VALIDATED_BY` — links a model, relationship, or variable to a validation
dataset. `PERTURBED_BY` — a disease, medication, or external stressor alters
this variable. `MODULATED_BY` — a behavior or circadian state alters a
physiological state. `PART_OF` — structural or organizational containment
(e.g. heart is part of cardiovascular system). `ASSOCIATED_WITH` — a
statistical correlation or physiological association without direct causal
proof.

The causal/non-causal distinction is load-bearing: `ASSOCIATED_WITH` and
`DERIVED_FROM` assertions must never be read as causal claims.

## Functional forms

A relationship may additionally name a `functional_form`: the shape of the
dependency between subject and object. Seven forms are registered in
`specification/core/functional-forms.yaml`. The first four tokens
(`sigmoid_hill`, `gravity_hydrostatic`, `inverse_proportional`,
`inverse_nonlinear`) were used as relationship `type` values in the legacy
`mechanistic_links.yaml` but were never registered; OCPE 0.1 registers them,
closing that legacy registry gap. The expressions are generic templates;
model-specific equations live in model specifications, not here.

| Form | Token | Shape |
|---|---|---|
| `ocpe:core/sigmoid-hill` | `sigmoid_hill` | Hill sigmoid between asymptotes, parameterised by half-saturation and steepness. |
| `ocpe:core/gravity-hydrostatic` | `gravity_hydrostatic` | Hydrostatic pressure offset under gravity, scaled by sin of body tilt. |
| `ocpe:core/inverse-proportional` | `inverse_proportional` | y = c / x (e.g. heart rate = 60000 / RR interval in ms). |
| `ocpe:core/inverse-nonlinear` | `inverse_nonlinear` | Qualitatively decreasing, non-linear, form unspecified. |
| `ocpe:core/first-order-lag` | `first_order_lag` | dx/dt = (x_target − x)/τ. |
| `ocpe:core/linear` | `linear` | y = a·x + b. |
| `ocpe:core/qualitative` | `qualitative` | Existence and/or direction only; no functional form implied. |

A relationship carrying `qualitative` asserts less than one carrying
`sigmoid_hill`; the form is part of the claim and its evidence.

## Identifiers, aliases and model symbols

Every entity has exactly one canonical identifier, a compact URI:

```
ocpe:<namespace>/<local-id>
```

The namespace is the owning package id (dot-separated kebab-case segments);
the local-id is kebab-case. Examples: `ocpe:cardiovascular/heart-rate`,
`ocpe:conditions.pots/neuropathic-pots`, `ocpe:core/regulates`. The
authoritative grammar lives in `common.schema.json` (`definitions.curie`);
`specification/core/identifiers.md` is normative.

Stability rules:

1. **Identifiers are permanent.** Once a package release contains an
   identifier, its meaning must not change; a meaning change requires a new
   identifier.
2. **Identifiers are never reused.** A withdrawn identifier remains reserved.
3. **Deprecation, not deletion.** Retirement requires `status: deprecated`
   plus a `deprecation` block (`deprecated_in`, `reason`, optional
   `replaced_by`) for at least one minor release before removal in a major
   release.
4. **Namespace = package.** Only the package whose `id` equals the namespace
   may define identifiers in it.
5. **Labels and aliases are not identifiers.** They may change in minor
   releases; canonical identifiers may not.

**Aliases** map other names onto canonical identifiers and carry backward
compatibility for legacy symbols (`Hc`, `pcm`, `Vau`, ...). Aliases are
case-sensitive (`HR` ≠ `hr`); an alias with a `scope` (e.g. `legacy-kb`, or a
model CURIE) is only unique within that scope, and the resolver reports an
ambiguity rather than guessing on an unscoped lookup that matches several
entities. An alias that implies a `unit` denotes the same quantity in a
different unit — it does not create a new quantity. `Hc` (beats/s) and `HR`
(beats/min) both resolve to `ocpe:cardiovascular/heart-rate`.

**Model-local symbol fragments** reference a symbol declared inside a model
specification:

```
<model-curie>#<symbol>
```

e.g. `ocpe:models.baroreflex-geddes-2022/baroreflex-geddes-2022#RalpM`.
Symbols are case-sensitive and only meaningful inside the declaring model. A
model symbol is not a physiological identifier; it may *represent* one (via
the symbol's `represents` field). Entity ids themselves must never contain
`#symbol` fragments — the validator rejects them.

The `ocpe:` prefix is intended to expand to `https://w3id.org/ocpe/id/`, but
that persistent-URL registration is pending; until it is registered the CURIE
is the only normative form.

## Where the semantics live

- **The JSON Schemas are normative.** `specification/schemas/` (draft-07)
  defines the entity contracts field by field; `common.schema.json` holds the
  shared definitions (identifier grammar, units as UCUM codes, context,
  reference ranges with their `range_type` distinctions, evidence
  attachments, deprecation, entity base). An entity is what its schema says
  it is.
- **`specification/core/kinds.yaml` is informative.** It records the kind
  taxonomy and the decision tests, and the legacy class mapping — a guide for
  authors, not the contract.
- **Identifier grammar is normative in
  `specification/core/identifiers.md`**; the unit registry
  (`specification/core/units.yaml`) grounds unit semantics, and the engine —
  not the schemas — checks that units are known and dimensionally consistent.
  Evidence scales (`specification/core/evidence-scales.yaml`) define the
  legacy levels and tiers.
- **Structural conformance says nothing about scientific truth.** A valid
  relationship with predicate `CAUSES` is a well-formed causal claim; whether
  the physiology agrees is a question for its evidence, its context, and its
  curation status — never for the schema alone.
