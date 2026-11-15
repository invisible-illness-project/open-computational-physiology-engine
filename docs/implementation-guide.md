# OCPE Implementation Guide

How to build an OCPE-compatible engine in any language. The normative
contracts are the artifacts under `specification/`; this guide explains what
an implementation must do to interoperate, using the Python reference
engine (`implementations/python/src/ocpe/`) as the worked example.

## 1. Resource model

- **Specification root** — the directory holding `core/meta.yaml` and
  `schemas/`. Resolution order used by the reference engine: explicit
  override (`OCPE_SPEC_ROOT` env var), a copy bundled with the
  implementation, then a `specification/` directory found by walking up from
  the engine location. Every implementation must be able to run with a
  bundled copy so installed engines are self-contained.
- **Package** — a directory with `package.yaml` plus the documents its
  `contents` list. Packages are loaded only when given to the engine (plus
  the `core` vocabulary, which the specification itself ships).
- **Registry** — the loaded state: packages, entities indexed by canonical
  id, document-level references, aliases.

## 2. Required capabilities

1. **Identifier parsing.** The CURIE grammar
   (`specification/core/identifiers.md`): `ocpe:<namespace>/<local-id>` with
   kebab-case segments, dot-separated namespace segments, and the optional
   `#symbol` fragment on model references. A syntactically valid identifier
   must never be treated as proof the entity exists.
2. **Schema validation.** Draft-07 JSON Schema against the files in
   `specification/schemas/`, including cross-schema `$ref`s and the
   document envelope's kind discrimination.
3. **Semantic validation.** Namespace = owning package; identifier
   uniqueness; declared-dependency enforcement for every cross-package
   reference; dependency acyclicity; registered-unit and dimensional
   consistency; predicate/functional-form vocabulary; alias-collision
   detection; range sanity (`min ≤ max`); deprecation-block requirements;
   **evidence reference integrity** (claims cite declared records);
   observation semantics (see the observation contract).
4. **Resolution.** Canonical ids, model symbols, scoped aliases, labels,
   predicate/functional-form tokens. Ambiguity is an error, never a guess.
5. **Units.** The `core/units.yaml` registry: normalization of alternative
   spellings, dimension lookup, multiplicative conversion.
6. **Versioning.** SemVer plus the constraint grammar (`^`, `~`, comparators,
   `||`, pre-release rules) and the pre-1.0 minor-is-breaking policy.
7. **Compatibility diffing.** Schema-aware, order-insensitive deep
   comparison of two package releases classifying every semantically
   meaningful change (see `docs/versioning-policy.md`).
8. **Conformance.** Execute `conformance/test-vectors/vectors.json` and the
   `conformance/expected-results/` expectations (see
   `docs/conformance-guide.md`).

## 3. Loading untrusted content safely

- Packages are **data**. Never execute, import or evaluate code found in a
  package; the specification contains no executable semantics.
- Enforce **path containment** for manifest `contents`: reject absolute
  paths, `..` traversal and symlinks resolving outside the package root.
- Parse YAML/JSON with safe parsers only (no arbitrary object construction).
- Be deterministic: no network access, clocks or randomness inside
  validation.

## 4. Reporting

Every validation report must:

- distinguish errors / warnings / info, with stable machine-readable codes
  (the conformance suite pins the codes);
- carry locations (file + entity id + JSON path);
- state the scope disclaimer: structural conformance does not establish
  scientific validity.

## 5. Optional pieces

- **CLI/export**: the reference CLI (`validate`, `resolve`, `search`,
  `show`, `list`, `deps`, `diff`, `units`, `check-observation`, `export`,
  `info`, `conformance`) is a model for interoperable tooling; the `export`
  JSON bundle is the simplest integration surface for non-Python tools.

## 6. Versioning your implementation

Engine versions are independent of the specification version they implement
(e.g. engine 0.3.1 may implement specification 0.1.0). Report both, as the
reference CLI does: `ocpe 0.1.0 (spec 0.1.0)`.
