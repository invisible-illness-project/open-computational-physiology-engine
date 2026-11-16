# OCPE Conformance Guide

The conformance suite (`conformance/`) is the official mechanism for
demonstrating that an implementation interprets OCPE specifications
consistently. It contains **synthetic fixtures only** — no physiological
research content — so any project can run it freely.

## What the suite contains

- **`fixtures/packages/`** — 23 complete packages: 8 valid (concepts,
  quantities, measurement methods, models, relationships, evidence with
  registered references, aliases, deprecation, cross-package dependencies)
  and 15 invalid, each with exactly one targeted defect (bad identifier,
  unregistered unit, dimension mismatch, undeclared dependency, unknown
  predicate, alias collision, missing content file, malformed manifest,
  unsatisfiable spec constraint, unregistered evidence citation, undeclared
  model symbol, namespace violation, dependency-version conflict,
  self-dependency, path traversal).
- **`fixtures/observations/`** — 21 valid/invalid observation records.
- **`fixtures/versions/`** — 12 old/new package pairs exercising the
  compatibility differ: patch/minor/major classifications, nested equation
  and parameter changes, relationship semantics, dependency changes,
  evidence changes, reorder-insensitivity, and an intentionally
  insufficient version bump.
- **`expected-results/`** — the exact expected outcome (validation error-code
  sets, diff change classes, required bumps) for every fixture.
- **`test-vectors/vectors.json`** — 48 language-independent declarative
  vectors (identifier parsing, version constraints, unit conversion and
  dimension, package/observation validation, deep diffing, resolution).

## Running it

With the Python reference engine:

```bash
ocpe conformance conformance/          # CLI report
pytest tests/test_conformance.py       # repository-level gate
```

Both execute the same vectors and fixture expectations.

## What "conformant" means

An engine is conformant when, for every vector and fixture expectation:

- validation produces the **exact expected error-code sets** (not merely
  "invalid" — the codes must match);
- diffs produce the **exact expected change classes and required bumps**;
- resolutions return the **expected canonical identifiers**;
- numeric expectations (unit conversions, version-satisfaction) match.

This tests semantic behavior, not JSON-Schema parsing alone: fixtures
deliberately include syntactically valid identifiers and units that are
semantically wrong.

## Demonstrating conformance from another language

Read `conformance/test-vectors/vectors.json` and the `expected-results/`
files, execute each operation with your implementation, and compare. The
vector `operation` vocabulary is:

| operation | input | expected keys |
|---|---|---|
| `parse_identifier` | `identifier` | `valid` |
| `version_satisfies` | `version`, `constraint` | `satisfied` |
| `unit_convert` | `value`, `from`, `to` | `value` |
| `unit_dimension` | `unit` | `dimension` |
| `validate_package` | `package` (fixture path), `requires` | `ok`, `errors` |
| `validate_observation` | `packages`, `record` | `ok`, `errors` |
| `diff_packages` | `old`, `new` (fixture paths) | `changes` (code→count), `required_bump` |
| `resolve` | `packages`, `term`, `scope` | `id`, `matched_by`, `kind` |

Fixture-relative paths in `input` resolve against the `conformance/`
directory. Publish your runner and results alongside your implementation;
the suite is designed to be vendored.
