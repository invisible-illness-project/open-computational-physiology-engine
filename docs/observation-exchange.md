# Observation Exchange

A short, practical spec for exchanging measured and estimated physiological
values with OCPE. The normative record format is
`specification/schemas/observation.schema.json` (JSON Schema draft-07); the
semantic rules are enforced by `validator.validate_observation` in the
reference engine; units are checked against the registry in
`specification/core/units.yaml`. OCPE defines the record format only — it
does not store observational data.

## The record

One record is one value of one quantity:

```yaml
quantity: ocpe:cardiovascular/heart-rate   # required: canonical CURIE
value: 78                                  # required: number, string or boolean
unit: /min                                 # required: UCUM code
value_kind: measured                       # required: see below
```

Required fields:

- `quantity` — canonical identifier (`ocpe:<package>/<local-id>`) of the
  quantity being reported. It must resolve to a quantity kind: a `variable`,
  a `derived_metric` or a `latent_construct`.
- `value` — the value itself: number, string or boolean.
- `unit` — a UCUM case-sensitive code as registered in
  `specification/core/units.yaml` (for example `mm[Hg]`, `mL/s`, `/min`, `1`).
- `value_kind` — one of `measured`, `estimated`, `derived`, `simulated`,
  `self_reported`. This is what separates a sensor reading from an algorithm
  output, a model run and a patient report.

Optional fields:

- `observation_id` — a string identifying this record.
- `time` — ISO 8601 timestamp or interval.
- `subject` — opaque, non-identifying subject identifier.
- `method` — reference to the measurement method (CURIE or model CURIE plus
  `#symbol`), e.g. `ocpe:wearables/polar-h10`. Use this to qualify how the
  value was obtained.
- `model` — model CURIE; **required when `value_kind` is `simulated`**.
- `context` — circumstances the value applies under (population, activity,
  posture and further dimensions), per the common schema's context object.
- `quality` — `flag` (`good`, `questionable`, `artifact`, `missing`) and a
  free-text `note`.
- `provenance` — a provenance record.

Keys starting with `x-` are reserved for extensions; any other key is
rejected. Note that the 0.1 record has no uncertainty field: with
`additionalProperties: false`, uncertainty must travel in `provenance` or an
`x-` extension until the schema gains one.

A complete example — a device-measured heart rate with method and context:

```yaml
quantity: ocpe:cardiovascular/heart-rate
value: 78
unit: /min
value_kind: measured
method: ocpe:wearables/polar-h10
time: "2026-11-14T08:30:00Z"
context: {activity: rest, population: ocpe:populations/healthy-control-cohort}
quality: {flag: good}
```

## Validating a record

```bash
pip install -e implementations/python
ocpe check-observation record.yaml            # registry defaults to packages/
ocpe check-observation batch.yaml --path dir # alternate package location
```

The file is YAML or JSON, holding one record or a list of records. For each
record the engine runs the schema check, then, against the loaded registry:

- the `quantity` must resolve, and resolve to a quantity kind — reporting a
  value of a concept, condition or measurement method is an error;
- a `latent_construct` cannot be reported with `value_kind: measured` (the
  engine rejects it and directs you to `estimated`);
- the `unit` must be registered in `specification/core/units.yaml` and its
  dimension must equal the quantity's declared dimension.

Issues are printed per record (`record <i>: <severity> <code>: <message>`);
the exit code is non-zero if any record fails. The same checks are available
in Python as `ocpe.validate_observation(record, registry)`.

## Semantic rules

1. **Latent constructs cannot be measured.** A latent construct (for example
   a sympathetic-tone scale) is not directly observable even in principle;
   its values are estimates conditional on an operationalization. Exchange it
   with `value_kind: estimated` and a `method`/`model` stating the
   operationalization.
2. **The unit must be of the quantity's dimension.** Dimensional consistency
   is checked against the unit registry, not by string matching: heart rate
   has dimension `event_rate` and takes `/min` or `/s`; the RR interval and
   RMSSD have dimension `time` and take `ms` (or any registered time unit);
   a dimensionless metric takes `1`. A registered-but-wrong-dimension unit
   (say `mL` for a pressure) is rejected, as is an unregistered code.
3. **Simulated values name their model.** `value_kind: simulated` requires a
   `model` CURIE, so synthetic data is always attributable to the
   specification it was generated from.
4. **Quantity kinds are not interchangeable.** The record carries a value of
   exactly one variable, derived metric or latent construct — never of a
   concept, relationship or method. If what you have is a proxy measurement
   (PPG-derived pulse-rate variability standing in for the RR interval),
   report the quantity with its `method` qualifier rather than relabeling it.

## The interchange contract

Canonical identifiers plus UCUM units. A consumer that receives an
observation record can resolve `quantity` against the OCPE registry to learn
exactly what was measured, with which unit and dimension, which value kind,
and — via `method`, `model` and `context` — how and under which circumstances.
Legacy symbols (`HR`, `RMSSD`, `Hc`) resolve to the same CURIEs, so producers
may accept them as input aliases, but records are exchanged under the
canonical identifier only. Anything outside the record format (device raw
streams, waveform data, cohort stores) is not covered by this spec.
