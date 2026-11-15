# OCPE — Python reference engine

Installable reference implementation of the OCPE specification: package
loading, schema + semantic validation, identifier/alias resolution, unit and
dimensional checks, compatibility diffing, conformance execution and a CLI.
The normative specification it implements lives in `../../specification/` and
is bundled into built distributions as `ocpe/_spec`, so an installed engine
is self-contained.

OCPE defines the language of computational physiology; it ships **no domain
content**. Supply the external domain packages you trust:

```bash
pip install -e .
ocpe --help
ocpe validate path/to/domain-package
ocpe resolve ocpe:my-package/my-variable --path path/to/domain-package
ocpe check-observation record.yaml --path path/to/domain-package
ocpe diff old-release/ new-release/
ocpe conformance ../../conformance
```

Python API:

```python
import ocpe

reg = ocpe.load(["path/to/domain-package"])   # + the bundled core vocabulary
report = ocpe.validate(reg)
assert report.ok
res = ocpe.Resolver(reg).resolve("ocpe:my-package/my-variable")
```

Validation is structural and semantic; it never asserts scientific validity.

## Development

```bash
pip install -e . pytest
pytest tests/            # engine unit tests (synthetic fixtures only)
```

Repository-level conformance: `pytest ../../tests` (runs the official suite
in `conformance/` against this engine).

## Layout

- `src/ocpe/loader.py` — package discovery/loading with path-containment enforcement
- `src/ocpe/validator.py` — schema + semantic validation, observation semantics, evidence integrity
- `src/ocpe/resolver.py` — canonical ids, model symbols, scoped aliases, labels, tokens
- `src/ocpe/units.py` — registry-driven unit normalization/conversion
- `src/ocpe/versioning.py` — semver + constraint satisfaction
- `src/ocpe/compatibility.py` — schema-aware deep diffing and bump classification
- `src/ocpe/vectors.py` — conformance vector/fixture execution
- `src/ocpe/governance/` — OPTIONAL review/authorization extension (lazy-imported)
- `src/ocpe/cli.py` — the `ocpe` command-line interface

Runtime dependencies: PyYAML and jsonschema only.
