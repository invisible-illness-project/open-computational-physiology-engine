# Observation Exchange

The contract through which applications, devices, simulators and datasets
report values of OCPE quantities. OCPE defines the **record format and its
semantic validation**; it stores no observational data.

## The record

```yaml
quantity: ocpe:some-package/heart-rate   # required: variable | latent_construct | derived_metric
value: 72                                # required: number, string or boolean
unit: /min                               # required: registered UCUM code
value_kind: measured                     # required: measured | estimated | derived |
                                         #           simulated | self_reported
time: "2026-11-15T10:00:00Z"             # optional: ISO 8601 timestamp or interval
subject: participant-047                 # optional: opaque, non-identifying
method: ocpe:some-package/some-method    # optional: measurement_method entity
model: ocpe:some-package/some-model      # required when value_kind == simulated
context: {posture: seated, activity: rest}
uncertainty: 3
uncertainty_type: sd                     # sd | se | ci95_halfwidth | range_halfwidth | unspecified
uncertainty_unit: /min                   # optional; must share the value unit's dimension
quality: {flag: good}                    # good | questionable | artifact | missing
provenance: {contributors: [{name: device-42, kind: tool}]}
```

`value_kind` is the honesty field:

- `measured` — produced by a measurement method on a real subject.
- `estimated` — inferred (e.g. a latent construct, or a value from a proxy
  signal). Latent constructs **must** use this (or `derived`), never
  `measured`.
- `derived` — computed from other observations by a defined algorithm (the
  derived metric's `computation` declares the algorithm).
- `simulated` — produced by a model. The record must name the model, and the
  model must exist as an OCPE model entity.
- `self_reported` — reported by the subject (symptoms, questionnaires,
  boolean flags).

## Validating a record

```bash
ocpe check-observation record.yaml --path some-package/
```

or from Python:

```python
import ocpe

reg = ocpe.load(["some-package/"])
rep = ocpe.validate_observation(record, reg)   # schema + semantics
```

Without a registry, only schema validation runs — useful for syntax checks,
but a syntactically valid identifier is never proof the referenced entity
exists.

## Semantic rules

`validate_observation` checks interpretability:

1. **Existence and kind.** `quantity` resolves to a `variable`,
   `latent_construct` or `derived_metric`; `method` resolves to a
   `measurement_method`; `model` resolves to a `model`.
2. **Observability.** A `latent_construct` with `value_kind: measured` is an
   error. A quantity declared `observability: model_compartment` reported as
   `measured` is a warning.
3. **Measurement semantics.** When the method declares `measures`, the
   quantity must be among its targets; a `value_kind` of `measured` /
   `estimated` / `derived` expects the corresponding mode `direct` /
   `estimated` / `derived` (mode mismatches are warnings).
4. **Units.** `unit` must be registered and match the quantity's dimension;
   `uncertainty_unit` must share the value unit's dimension.
5. **Value types.** The value must match the quantity's declared
   `value_type` (boolean constructs take booleans, categorical take strings,
   numeric kinds take numbers).
6. **Timestamps.** `time` must parse as ISO 8601.
7. **Simulated records** must name an existing model entity.

## The interchange contract

- Records are self-contained: every reference is a canonical OCPE identifier
  (or a model symbol fragment for method-internal quantities).
- Units are always explicit; consumers convert with the registry
  (`ocpe units convert`) rather than assuming.
- Records carry their provenance and quality; downstream consumers (MOSAIC
  datasets, Lamina pipelines, analysis tools) must preserve `value_kind`,
  `method` and `provenance` when aggregating.
- OCPE never sees subject identities: `subject` is an opaque token.
