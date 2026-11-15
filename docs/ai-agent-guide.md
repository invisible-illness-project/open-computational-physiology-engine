# AI Agent Guide to OCPE

OCPE is the common language of computational physiology: versioned schemas,
canonical identifiers, units, relationships, model specifications and
evidence structures. Agents use it to **read** structured physiological
knowledge produced by others and to **write** packages that humans and other
agents can consume without bespoke parsing.

This guide is the contract for agents. The machine-readable contracts are the
JSON Schemas in `specification/schemas/`; when this guide and a schema
disagree, the schema wins.

## The mental model

1. **OCPE is a language, not a database.** The OCPE repository contains the
   specification, the reference engine, conformance tests and documentation —
   and no physiological research content. Domains (diseases, devices,
   populations, literature) live in **external packages** that you load by
   path or receive as documents.
2. **Structural validation ≠ scientific validity.** Every validator output
   says so. Never report OCPE validation as evidence that a claim is true.
3. **Identifiers are permanent.** `ocpe:pkg/local-id`. Never mint a new
   identifier for a meaning that already has one; never reuse a retired one.
4. **Kinds are distinct.** concept ≠ variable ≠ latent_construct ≠
   derived_metric ≠ measurement_method ≠ model ≠ relationship. The schema
   enforces the distinctions.
5. **Evidence attaches to aspects** (existence, direction, magnitude, ...).
   Direction-level support must never be read as magnitude-level support.

## Reading OCPE

### The whole registry as one JSON bundle

```bash
ocpe export --path some-package/ -o bundle.json
```

`bundle.json` contains the spec version, package manifests, all entities and
all references — one document to ingest. It carries the disclaimer:
structural content only.

### Finding and reading entities

```bash
ocpe list entities --path some-package/                 # every entity
ocpe show ocpe:some-package/some-variable --path some-package/
ocpe search "pressure" --path some-package/            # full-text search
```

`ocpe show` resolves the term (canonical id, alias, label or model symbol)
and prints the entity plus any relationships it participates in.

### From Python

```python
import ocpe

reg = ocpe.load(["some-package/"])         # + the bundled core vocabulary
report = ocpe.validate(reg)
if not report.ok:
    for issue in report.errors:
        print(issue)

res = ocpe.Resolver(reg).resolve("ocpe:some-package/some-variable")
print(res.id, res.entity.kind, res.entity.data.get("definition"))
```

### Aliases and unit-qualified spellings

Aliases map alternative names onto canonical ids and may carry a `unit`
meaning "the same quantity expressed in this unit":

```bash
ocpe resolve HR --path some-package/ --json
# -> {"term": "HR", "id": "ocpe:...", "matched_by": "alias", "unit": "/min"}
```

When `unit` is present, interpret raw values in that unit or convert before
mixing with other data (`ocpe units convert 72 /min /s`).

### Model symbol fragments

`ocpe:some-package/some-model#Rtot` references a symbol *inside* a model
specification. Symbols are case-sensitive, scoped to their model, and are not
physiological identifiers — though a symbol may `represent` one. Follow
`represents` to get the canonical quantity.

### Exchanging observations with `ocpe check-observation`

```bash
ocpe check-observation record.yaml --path some-package/
```

A record:

```yaml
quantity: ocpe:some-package/some-variable
value: 72
unit: /min
value_kind: measured          # measured | estimated | derived | simulated | self_reported
time: "2026-11-15T10:00:00Z"  # optional, ISO 8601
method: ocpe:some-package/some-method   # optional, must be a measurement_method
uncertainty: 3                # optional
uncertainty_type: sd
```

Semantic checks you can rely on: the quantity resolves and is a quantity
kind; latent constructs cannot be `measured` (use `estimated`); `simulated`
requires an existing `model`; units match the quantity's dimension; `method`
must exist, be a measurement method, and declare the quantity; timestamps
must parse.

## Authoring packages (your primary output mode)

You produce **standalone packages**, not pull requests to OCPE:

```
my-package/
├── package.yaml
├── variables.yaml
├── relationships.yaml
└── references.yaml (optional)
```

Follow `docs/package-authoring-guide.md`. The non-negotiables:

### Evidence discipline

- Every `references:` entry in an evidence statement must match a record in a
  document-level `references:` list — yours or a dependency's. Citing a DOI
  you did not register is a validation error, and registering a record you
  did not verify is a curation failure. **Never fabricate references.**
- Use `basis: definitional` for mathematical identities; do not dress them as
  literature.
- `curation_status` is honest metadata: `machine_proposed`,
  `machine_calibrated`, `unverified` are legitimate and expected values for
  agent-authored content. Do not mark your own output `verified`.
- State `supports` precisely. Direction evidence is not magnitude evidence.

### Context-qualification duties

Any range, performance statistic or evidence claim you record applies to a
stated context only. Use `context` objects (`population`, `posture`,
`activity`, `setting`, `scope_note`, ...) and never present a context-bound
number as universal.

### Identifier duties

Mint kebab-case identifiers in your own namespace only. If you adapt an
existing vocabulary, map it with aliases (and `provenance.derived_from`),
don't re-mint.

## Validating before you ship

```bash
ocpe validate my-package/ --strict   # errors AND warnings must be clean
ocpe diff my-package-1.0.0/ my-package/   # confirm the bump you declare matches the changes
```

Then run the conformance expectations if you modified language behavior (you
should not need to):

```bash
ocpe conformance conformance/
```

## Worked examples

### Resolve an alias and read its unit-qualified meaning

```python
import ocpe

reg = ocpe.load(["some-package/"])
r = ocpe.Resolver(reg).resolve("HR")            # alias
print(r.id, r.unit)                             # canonical id + "/min"
# Interpret raw values as beats per minute, or convert:
from ocpe import units
print(units.convert(72, "/min", "/s"))          # 1.2
```

### Validate an observation exchange record

```python
import ocpe

reg = ocpe.load(["some-package/"])
rep = ocpe.validate_observation({
    "quantity": "ocpe:some-package/some-variable",
    "value": 0.5, "unit": "1", "value_kind": "measured",
}, reg)
for issue in rep.issues:
    print(issue)      # e.g. latent-measured: use 'estimated'
```

### Read a model specification without executing it

```python
import ocpe

reg = ocpe.load(["some-package/"])
model = reg.get("ocpe:some-package/some-model")
for eq in model.data["equations"]:
    print(eq["id"], eq["expression_latex"])
# Execution is a downstream engine's job (MOSAIC); OCPE checks the
# specification: declared symbols, dimensional consistency, evidence links.
```
