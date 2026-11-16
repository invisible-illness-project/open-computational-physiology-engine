# OCPE Versioning Policy

This document is the human-readable companion to
`specification/versions/compatibility.yaml` (machine-readable, normative).
It covers the three versioned artifacts — the specification, packages, and
document markers — the change classification used by `ocpe diff`, and the
pre-1.0 policy.

## The three versioned artifacts

1. **The OCPE specification** (`specification/core/meta.yaml`,
   `ocpe_spec_version`, currently `0.1.0`) versions the schemas, the
   identifier grammar, the unit registry, the predicate/functional-form
   vocabularies and the compatibility rules themselves. Releases are recorded
   in `specification/versions/compatibility.yaml` with a `schema_base_uri`,
   the `document_marker` they write, and the document versions they read.
2. **Packages** version content. Each package has its own semver, changelog
   and release cadence, independent of every other package and of the
   specification. A package declares the specification range it conforms to
   via `ocpe_spec` in its manifest.
3. **Documents** carry an `ocpe:` major.minor marker. An engine accepts a
   document only if its marker is in the release's `reads_documents` list, so
   specification upgrades can introduce new document shapes without silently
   misreading old ones.

## What is a breaking change (packages)

`ocpe diff old-release/ new-release/` performs a **schema-aware,
order-insensitive deep comparison** of two releases of the same package:
every entity (including nested model symbols, equations, evidence
attachments and reference ranges) and the manifest's dependency and
specification constraints are compared field by field. Each detected change
is classified using the `change_classes.package` table in
`specification/versions/compatibility.yaml`:

- **major (breaking)**: removing an identifier, alias, symbol or equation;
  changing an identifier's kind, dimension, canonical unit, value type or
  observability; changing equation expressions or their input/parameter/
  output sets; changing relationship semantics (subject, predicate, object,
  functional form, direction of effect); changing model semantics
  (formalism, assumptions, validity domain); changing measurement semantics
  (what a method measures, how, or its declared performance); removing
  evidence; removing dependencies or tightening dependency/specification
  constraints.
- **minor (compatible addition)**: adding identifiers, symbols, equations,
  aliases, dependencies, reference ranges or evidence; deprecating an
  identifier (with a `deprecation` block); changing non-normative content.
- **patch (editorial)**: label/definition/description rewording, notes and
  curation notes, provenance metadata.

Two properties of the differ matter for trust:

- **Comprehensiveness.** Any change to a semantically meaningful field is
  detected — not just top-level identifiers and metadata. In particular,
  edits to *nested* mathematical content (an equation's `expression_latex`,
  a parameter's `nominal_value`, an equation's input/output sets) are
  breaking changes, as are relationship predicate changes, measurement-mode
  changes, evidence attachment changes and dependency constraint changes.
  The conformance suite (`conformance/fixtures/versions/`) pins all of these.
- **Order insensitivity.** Reordering lists (equations, symbols, aliases,
  assumptions) is not a change; content is compared as keyed sets.

The required bump is the maximum severity across all changes, and
`bump_is_sufficient` checks the declared version bump against it.

## Identifier permanence

Identifiers are permanent and never reused. A meaning change requires a new
identifier; retirement is `status: deprecated` plus a `deprecation` block
(`deprecated_in`, `reason`, optional `replaced_by`,
`removal_planned_in`) for at least one minor release before removal in a
major release. Labels and aliases may change in minor releases; canonical
identifiers may not.

## Document markers and release compatibility

For specification 0.1.0 the document marker is `"0.1"` and engines read only
documents marked `"0.1"`. When a future specification release changes the
schemas incompatibly, it will bump the document marker, list the markers it
reads in `reads_documents`, and provide a migration path. Documents are then
migrated explicitly — no silent reinterpretation.

## The pre-1.0 policy

While a version is `0.y.z` (SemVer item 4), a minor bump may carry breaking
changes. `bump_is_sufficient` encodes this: for 0.y.z packages a required
*major* classification is satisfied by a minor bump. Consequently
**consumers should always pin the minor** in constraints:

```yaml
dependencies:
  - {package: some-domain, version: ">=0.3.0 <0.4.0"}   # not ">=0.3.0"
```

The same applies to `ocpe_spec` ranges (`>=0.1.0 <0.2.0`).

## Version constraints

Constraint grammar: comparators `>=`, `>`, `<=`, `<`, `=`, `^`, `~`
combined with AND; alternatives separated by `||`.

- `^1.2.3` := `>=1.2.3 <2.0.0`; `^0.2.3` := `>=0.2.3 <0.3.0` (pre-1.0 caret
  pins the minor); `^0.0.3` := `>=0.0.3 <0.0.4`.
- `~1.2.3` := `>=1.2.3 <1.3.0`.
- A bare version means `=`; partial versions (`1.2`) pad with zeros.
- Pre-releases only satisfy constraints that mention the same core version
  (`1.0.0-alpha` does not satisfy `^1.0.0`).

## Governance of the compatibility rules

`change_classes.specification` (in `compatibility.yaml`) classifies
specification-level changes: adding a required field, removing/renaming a
field, removing an enum value or changing the identifier grammar are
specification-major; adding optional fields or enum values, or adding a kind,
are specification-minor; clarifications are specification-patch.
Specification-minor releases must not invalidate documents written against
earlier 0.1.x markers.

<!-- Copyright 2026 The Invisible Illness Project. SPDX-License-Identifier: Apache-2.0. See LICENSE in the repository root. -->
