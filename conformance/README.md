# OCPE Conformance Suite

The official, language-independent conformance suite for OCPE semantic engines.
It contains **synthetic fixtures only** — no physiological research content.

Any implementation (Python, Rust, JavaScript, ...) that interprets OCPE
specifications can demonstrate consistent behavior by executing these vectors
and fixture expectations:

```bash
# with the Python reference engine installed:
ocpe conformance conformance/          # or: pytest tests/test_conformance.py
```

## Layout

```
fixtures/
  packages/
    valid/      complete, valid packages (concepts, quantities, methods,
                models, relationships, evidence+references, aliases,
                deprecation, cross-package dependencies)
    invalid/    one targeted defect each (bad identifier, bad unit, dimension
                mismatch, undeclared dependency, unknown predicate, alias
                collision, missing content, bad manifest, unsatisfiable spec
                constraint, unregistered evidence citation, undeclared model
                symbol, namespace violation, dependency-version conflict,
                self-dependency, path traversal)
    base/       dependency target for the cross-package fixtures
  observations/ 22 valid and invalid observation exchange records
  versions/     old/new package pairs exercising the compatibility differ
                (patch/minor/major classifications, nested equation and
                parameter changes, relationship semantics, dependencies,
                evidence changes, reorder insensitivity)
expected-results/
  packages.json      fixture -> expected validation outcome (ok + error codes)
  observations.json  record  -> expected validation outcome
  versions.json      pair    -> expected change classes + required bump
test-vectors/
  vectors.json       48 language-independent declarative vectors; every engine
                     must produce results matching `expect` (subset match)
```

## Vector operations

| operation | input | expected-result keys |
|---|---|---|
| `parse_identifier` | `identifier` | `valid` |
| `version_satisfies` | `version`, `constraint` | `satisfied` |
| `unit_convert` | `value`, `from`, `to` | `value` |
| `unit_dimension` | `unit` | `dimension` |
| `validate_package` | `package` (fixture path), `requires` | `ok`, `errors` |
| `validate_observation` | `packages`, `record` | `ok`, `errors` |
| `diff_packages` | `old`, `new` (fixture paths) | `changes` (code->count), `required_bump` |
| `resolve` | `packages`, `term`, `scope` | `id`, `matched_by`, `kind` |

Fixture-relative paths in `input` resolve against the `conformance/` directory
that contains `test-vectors/`.

The suite tests **semantic behavior**, not merely JSON Schema parsing: error
codes are exact sets, diff classifications are exact, and fixtures deliberately
include cases where a syntactically valid identifier or unit is semantically
wrong.
