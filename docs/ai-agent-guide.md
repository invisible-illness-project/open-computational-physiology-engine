# AI Agent Guide to OCPE

How AI agents should consume and contribute to OCPE — the common language of
computational physiology. This guide assumes the reference engine
(`pip install -e implementations/python`) and the repository layout described
in `README.md`.

## The mental model

OCPE is **semantic infrastructure, not a simulator**. It tells you what a
quantity is (variable, derived metric, latent construct), which unit and
dimension it has, what is known to cause, regulate or derive it, with what
evidence, in which population, posture and activity context, and which
version of which package defined the identifier. It does not integrate
equations, generate patients, or synthesize ECG/PPG/EDA signals — those live
in MOSAIC and Lamina (see `docs/mission.md`).

**Structural validation is not scientific validation.** Every `ocpe validate`
run ends with the disclaimer: structural validation only; it does not
establish scientific validity. A record that is well-formed, internally
consistent and resolvable can still be scientifically wrong. Treat every
green checkmark as "parseable and self-consistent", never as "biologically
true". When you report OCPE content to a user, say what is validated
(structure) and what is not (science).

## Reading OCPE

### The whole registry as one JSON bundle

```bash
ocpe export                    # prints the bundle
ocpe export -o ocpe.json       # writes ocpe.json
```

`ocpe export` emits one JSON document with the spec version, every loaded
package (id, version, manifest), every entity record, all references, and an
explicit disclaimer: "Structural content only; inclusion does not imply
scientific validation." This is the intended path for agents and non-Python
tools: load the bundle, index the entities, and work from it.

### Finding and reading entities

```bash
ocpe resolve ocpe:cardiovascular/heart-rate   # canonical identifiers
ocpe resolve Hc --scope legacy-kb             # legacy symbols still resolve
ocpe resolve 'ocpe:models.baroreflex-geddes-2022/baroreflex-geddes-2022#RalpM'
ocpe show ocpe:conditions.pots/neuropathic-pots
ocpe search baroreflex
ocpe list packages
ocpe list entities --kind condition
```

Resolution accepts, in order: canonical CURIEs, `CURIE#symbol` model
fragments, predicate and functional-form tokens, aliases (case-sensitive),
and labels (case-insensitive, only if no alias matched). An ambiguous lookup
raises an ambiguity error listing the candidates rather than guessing — retry
with `--scope`. `ocpe show` adds every relationship whose subject or object
is the entity. Add `--json` to any of these for machine-readable output, and
`resolve --full --json` to include the full entity record.

### From Python

```python
import ocpe

reg = ocpe.load()                    # repository packages/ + core vocabulary
report = ocpe.validate(reg)          # structural + semantic validation
if not report.ok:
    ...                              # inspect report.issues

r = ocpe.Resolver(reg).resolve("Hc", scope="legacy-kb")
print(r.id, r.unit)                  # ocpe:cardiovascular/heart-rate /s
```

`ocpe.load(paths=None, include_core=True)` loads packages (by default the
repository's `packages/` directory plus the core vocabulary) into a
`Registry`. `ocpe.validate(reg)` returns a `Report` whose `ok`, `errors`,
`warnings` and `issues` fields describe structural and semantic problems:
schema conformance, identifier namespaces and uniqueness, dependency
declarations and versions, reference integrity (including model symbols),
units and dimensions, predicate/functional-form vocabulary, alias collisions,
ranges, deprecation. `ocpe.Resolver(reg)` offers the same resolution logic as
the CLI, plus `search()`, `related(curie)` and `aliases_of(curie)`.

### Legacy symbols and unit-qualified aliases

Content migrated from the pre-0.1 knowledge base keeps its old symbols as
scoped aliases, so `Hc`, `pcm`, `Vau`, `neuropathic_pots` and similar tokens
still resolve — but only reliably with the `legacy-kb` scope:

```bash
ocpe resolve Hc --scope legacy-kb
# Hc -> ocpe:cardiovascular/heart-rate (variable: Heart Rate) via alias [unit /s]
```

An alias may carry a `unit`. That unit is part of the meaning: `Hc` (beats
per second) and `HR` (beats per minute) are the same quantity,
`ocpe:cardiovascular/heart-rate`, expressed in different units. Never strip
the unit and never treat the alias as a distinct quantity. Full rules:
`specification/core/identifiers.md`.

### Model symbol fragments

A symbol declared inside a model is referenced as `<model-curie>#<symbol>`,
for example
`ocpe:models.baroreflex-geddes-2022/baroreflex-geddes-2022#RalpM`. Symbols
are case-sensitive and only meaningful inside the declaring model; a symbol
is not a physiological identifier, though it may `represent` one. Resolving a
fragment returns the symbol record including its unit and its `represents`
note when present.

### Exchanging observations with `ocpe check-observation`

When a dataset, sensor pipeline, or simulation hands you a number, OCPE
provides the exchange format for it — nothing more. `observation.schema.json`
defines the record; OCPE does not store observations. Validate an exchange
file (YAML or JSON, one record or a list) before accepting it:

```bash
ocpe check-observation record.yaml
```

Required fields: `quantity` (CURIE of a variable, derived metric or latent
construct), `value`, `unit` (UCUM code), `value_kind`. The semantic checks
beyond the schema are:

- `quantity` must resolve to a quantity kind (variable, `derived_metric` or
  `latent_construct`) — not a condition, method, etc.
- the unit must match the quantity's dimension.
- **a latent construct can never be `measured`.** The engine rejects
  `value_kind: measured` on a latent construct with
  "is a latent construct and cannot be 'measured'; use 'estimated'".
- `value_kind: simulated` requires a `model` field naming the model that
  produced the value, so synthetic data is always traceable to its source.

`value_kind` is `measured`, `estimated`, `derived` or `simulated` (the enum
also admits `self_reported`). Set it honestly: a model output is `simulated`,
an indicator-based score for a latent construct is `estimated`, a computed
metric is `derived`. Mislabeling `simulated` or `estimated` values as
`measured` poisons every downstream consumer.

## Contributing to OCPE

### Authoring packages

New knowledge enters OCPE as a domain package under `packages/`. Follow
`docs/package-authoring-guide.md` for the document format, manifest,
dependencies, versioning and validation workflow (`ocpe validate packages/`,
`ocpe diff`, `ocpe deps`). The entity-kind taxonomy and its decision tests
are in `specification/core/kinds.yaml` and `docs/ontology.md`; pick the kind
by the test, not by resemblance — variables, derived metrics, latent
constructs and measurement methods are distinct kinds and must never be used
interchangeably.

### Evidence discipline

Every scientific claim you add must carry aspect-level evidence
(`evidence.schema.json`). The non-negotiable rules:

- **Never claim magnitude support from direction evidence.** The `supports`
  aspect (`existence`, `direction`, `magnitude`, `structure`, `association`,
  `definition`, `mechanism`, `measurement_validity`) is explicit. Evidence
  attached at `direction` must never be read — by you or by anyone — as
  support for a magnitude. If you only know the sign of an effect, say so.
- **Never invent references.** Cite only real, checked sources using
  persistent-identifier forms (`doi:`, `pmid:`, `pmcid:`, `isbn:`,
  `arxiv:`, `url:` as defined in `common.schema.json`). Do not fabricate a
  DOI because the schema would accept the shape of one.
- **Hypotheses are `basis: machine_proposed`.** Content you generate as a
  hypothesis — not anchored in a checked source — is marked
  `basis: machine_proposed` (other basis values: `literature`,
  `definitional`, `expert_opinion`, `machine_calibrated`,
  `computational_experiment`, `dataset`). `definitional` is reserved for
  mathematical identities that need no empirical citation. Record
  `limitations` honestly.
- Preserve evidence levels and tiers verbatim from source curation; do not
  re-grade during migration or editing ("no discarded science",
  `docs/mission.md`).

### Context-qualification duties

Reference ranges, sensor accuracy and evidence claims apply only to the
stated population, posture, activity and method context — they do not
transfer silently. When you state a range or performance figure, qualify it
with a `context` (population, health status, age range, sex, posture,
activity, setting, measurement method, model, scope note). When you consume
one, check the context before applying it to a new situation; if you extend a
range beyond its stated context, label the extension as yours, with
`basis: machine_proposed` evidence.

### Citing this repository

When you rely on OCPE content in external work, cite the repository, the
package id(s) and their versions (`ocpe list packages`), and the spec
version (`ocpe info`). Identifiers are permanent and versioned precisely so
that a citation can say which meaning of an identifier was used.

### The governance extension is optional

`ocpe governance` (record, aggregate, challenge, authorize, explain, history,
summary, migrate) is an optional, separable review-tracking extension
(ADR 0001). Core commands never touch governance data, and the core engine
does not require it.

Two duties follow for agents:

1. **Absence of human review is not approval.** Content with no review
   entries is simply unreviewed. Never represent structurally valid content
   as human-approved, and never treat your own generated content as reviewed
   because it passed validation.
2. **Surface the curation status of what you rely on.** Evidence statements
   and perturbations carry `curation_status`
   (`verified`, `partially_verified`, `unverified`, `machine_proposed`,
   `machine_calibrated`, `disputed`, `retracted`, `unknown`). When you answer
   from OCPE content, state the curation status of the supporting content —
   especially when it is `machine_proposed` or `unverified`.

## Worked examples

All examples run against this repository's packages; install the engine with
`pip install -e implementations/python` or set
`PYTHONPATH=implementations/python/src`.

### (a) Resolve a legacy symbol and read its unit-qualified meaning

```bash
$ ocpe resolve Hc --scope legacy-kb
Hc -> ocpe:cardiovascular/heart-rate (variable: Heart Rate) via alias [unit /s]
```

The legacy symbol `Hc` resolves through a scoped alias to the canonical
identifier `ocpe:cardiovascular/heart-rate`. The `[unit /s]` qualifier is
meaningful: in the legacy knowledge base and inside the Geddes 2022 model,
`Hc` is heart rate expressed in beats per second, while the canonical unit of
the quantity is `/min`. Converting the value or comparing it against the
plausibility bound (12–240 `/min`) requires the unit-aware form:

```python
import ocpe

reg = ocpe.load()
r = ocpe.Resolver(reg).resolve("Hc", scope="legacy-kb")
assert r.id == "ocpe:cardiovascular/heart-rate"
# r.unit == "/s": interpret any raw value as beats per second, or convert
# with the units module before mixing with /min data.
```

Dropping the scope (`ocpe resolve Hc`) may still work when the alias is
unique, but scoped resolution is deterministic; if an unscoped lookup matches
several entities, the resolver reports the ambiguity and you supply the
scope.

### (b) Validate an observation exchange record

Record file `record.yaml`:

```yaml
quantity: ocpe:cardiovascular/heart-rate
value: 72
unit: /min
value_kind: measured
```

```bash
$ ocpe check-observation record.yaml
1 observation record(s) valid
```

The record passes: the quantity resolves to a variable, the UCUM unit `/min`
matches the entity's `event_rate` dimension, and `measured` is a legal
`value_kind` for a variable. Now mislabel a latent-construct estimate as a
measurement:

```yaml
quantity: ocpe:autonomic/sympathetic-tone
value: 0.8
unit: "1"
value_kind: measured
```

```bash
$ ocpe check-observation bad.yaml
record 0: ERROR   latent-measured: ocpe:autonomic/sympathetic-tone is a latent
construct and cannot be 'measured'; use 'estimated'
```

Sympathetic tone is a `latent_construct` — a theoretical quantity that cannot
be observed even in principle. Any number for it is a model- or
indicator-conditional estimate, so the correct `value_kind` is `estimated`
(and, if a model produced it, `model` names that model). The same check
rejects simulated data that omits its `model` field.

### (c) Extract a phenotype's perturbations with evidence tiers and inert unverified blocks

The POTS phenotype entities declare how each phenotype is represented inside
the Geddes 2022 model. Extract them programmatically:

```python
import ocpe

reg = ocpe.load()
ent = reg.get("ocpe:conditions.pots/neuropathic-pots")
for rep in ent.data.get("model_representations", []):
    print("model:", rep["model"])
    for p in rep.get("parameter_perturbations", []):
        ev = p.get("evidence", [{}])[0]
        print("PERTURB", p["parameter"].split("#")[1],
              p.get("baseline_value"), "->", p.get("perturbed_value"),
              "| tier", ev.get("evidence_tier"),
              "| level", ev.get("evidence_level"),
              "| status", p.get("curation_status"))
    for p in rep.get("unverified_parameter_perturbations", []):
        ev = p.get("evidence", [{}])[0]
        print("INERT-UNLESS-OPTED-IN", p["parameter"].split("#")[1],
              p.get("baseline_value"), "->", p.get("perturbed_value"),
              "| tier", ev.get("evidence_tier"),
              "| basis", ev.get("basis"),
              "| status", p.get("curation_status"))
```

Output (abridged):

```text
model: ocpe:models.baroreflex-geddes-2022/baroreflex-geddes-2022
PERTURB RalpM 17.88 -> 11.5 | tier C | level Level 4 | status partially_verified
PERTURB Ralpm 1.192 -> 0.76 | tier C | level Level 4 | status partially_verified
INERT-UNLESS-OPTED-IN dV_veno_max 250.0 -> 75.0 | tier D | basis machine_calibrated | status machine_calibrated
```

Read this before acting on it. The two verified-block perturbations carry
`magnitude` support at tier C (Level 4, in silico) and `partially_verified`
curation status — human expert review is still pending per the curation
notes. The `dV_veno_max` entry lives in
`unverified_parameter_perturbations`: consumers **must** treat it as inert
unless explicitly opted in (legacy `unverified_parameters` semantics). Its
direction evidence is tier A (blunted leg norepinephrine spillover, Jacob
2000) but its magnitude is `machine_calibrated`, tier D — exactly the
direction/magnitude separation that must never be blurred. The accompanying
`constraints` block (`do_not_perturb: mvl, VMvl`, tier B) is part of the
representation: do not perturb venous compliance for this phenotype. Also
note the package-level curation notes: POTS phenotypes are composable, not
mutually exclusive.
