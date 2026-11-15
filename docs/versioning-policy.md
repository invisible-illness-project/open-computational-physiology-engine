# OCPE Versioning Policy

The versioning and compatibility rules of OCPE: what is versioned, what counts
as a breaking change, how identifiers persist across releases, how document
markers gate compatibility, the pre-1.0 policy, and how `ocpe diff` classifies
changes between two releases of a package. The machine-readable form of these
rules lives in `specification/versions/compatibility.yaml`, which the reference
engine consumes (`ocpe.compatibility`); this document is its prose companion.

## The three versioned artifacts

OCPE has three independently versioned artifacts. None of their version
numbers is locked to another's; compatibility between them is declared
through constraints, not implied by matching numbers.

1. **The OCPE specification** — semantic version `spec.X.Y.Z` (currently
   `0.1.0`, status provisional, per `current` in
   `specification/versions/compatibility.yaml`). The specification is the
   normative contract: JSON Schemas, identifier grammar, unit registry,
   predicate and functional-form vocabulary, compatibility rules. Its changes
   are recorded in `specification/versions/CHANGELOG.md`.
2. **Domain packages** — each package carries its own independent semantic
   version in `package.yaml` (`version:`), keeps its own changelog, and is
   released on its own schedule (e.g. `cardiovascular` 1.0.0,
   `conditions.pots` 1.5.0). A package declares which specification versions it
   conforms to via `ocpe_spec`, and which package versions it needs via
   `dependencies`.
3. **The reference engine** — the Python implementation
   (`implementations/python/`) is an independent semantic version (currently
   0.1.0). It implements the specification; it does not share a version line
   with either the specification or the packages.

A package is interpreted under exactly one specification version at a time:
the engine's own spec version must satisfy the package's `ocpe_spec`
constraint, and every document's `ocpe` marker must be one the engine reads
(see Document markers below). A mismatch on either check is a validation
error, not a silent degradation.

## What is a breaking change (packages)

`ocpe diff` classifies changes between two releases of a package against
`change_classes.package` in `specification/versions/compatibility.yaml`:

| Severity | Change class | Meaning |
|---|---|---|
| major | `identifier_removed` | An entity released in the older version no longer exists in the newer one. |
| major | `alias_removed` | A previously released alias no longer resolves. |
| major | `identifier_kind_changed` | An entity's `kind` changed (e.g. variable → latent_construct). Kinds are not interchangeable, so this breaks consumers. |
| major | `dimension_changed` | The physical dimension of a quantity changed. |
| major | `canonical_unit_changed` | The canonical unit of a quantity changed. |
| major | `dependency_major_bump_required` | The package now requires a new major version of a dependency. |
| minor | `identifier_added` | A new entity identifier. |
| minor | `identifier_deprecated` | An entity moved to `status: deprecated` (with a `deprecation` block). |
| minor | `alias_added` | A new alias for an existing identifier. |
| minor | `evidence_added` | Additional evidence attached to an entity. |
| minor | `reference_range_added` | A new context-qualified reference range. |
| patch | `label_or_description_changed` | Editorial changes to labels, definitions or descriptions. |
| patch | `curation_note_changed` | Curation notes added or updated. |

Two rules follow directly. First, additive work — new identifiers, aliases,
evidence, ranges — is always safe for consumers and lands in minor releases.
Second, anything that can invalidate a consumer's reference (removal, kind
change, dimension or canonical-unit change) is major and must not appear in a
minor or patch release of a post-1.0 package.

## Identifier permanence

Identifier rules are normative in `specification/core/identifiers.md`; the
stability rules, in compressed form:

1. **Identifiers are permanent.** Once a package release contains an
   identifier, its meaning must not change. A change of meaning requires a new
   identifier.
2. **Identifiers are never reused.** A withdrawn identifier remains reserved.
3. **Deprecation, not deletion.** Retiring an identifier requires
   `status: deprecated` plus a `deprecation` block (`deprecated_in`, `reason`,
   optional `replaced_by`) for at least one minor release before removal in a
   major release. This matches the change classes: deprecation is minor,
   removal is major.
4. **Namespace = package.** Only the package whose `id` equals the namespace
   may define identifiers in that namespace.
5. **Labels and aliases are not identifiers.** They may change in minor
   releases; canonical identifiers may not.

## Document markers and release compatibility

Each specification release recorded in `compatibility.yaml` carries:

- `version` and `status` — the specification version and its lifecycle status
  (0.1.0 is `provisional`);
- `schema_base_uri` — the base URI under which that release's JSON Schemas are
  published;
- `document_marker` — the value of the `ocpe:` key in documents written
  against that release (`"0.1"`);
- `reads_documents` — the list of document markers an engine at that release
  will read (for 0.1.0: `["0.1"]`);
- `supersedes` and `migration` — what the release replaces and where the
  migration path is documented.

The engine validates every document against this table: a document whose
`ocpe` marker is not in the readable set for the engine's specification
version fails with a `document-version` error, independently of the package's
`ocpe_spec` constraint (which is checked separately, against the engine's
specification version, as `spec-incompatible`). The two checks answer
different questions: `ocpe_spec` asks "is this package written for a
specification this engine implements?", while the marker check asks "can this
engine parse this document?". Both must pass.

## The pre-1.0 policy

`pre_1_0_policy: minor-is-breaking` (SemVer item 4): while a version is
`0.y.z`, a **minor** bump may carry breaking changes. The consequences:

- For a 0.y artifact, consumers must pin the minor in constraints:
  `">=0.1.0 <0.2.0"`, not `"^0.1.0"` — although note that caret already encodes
  this for 0.y versions: `^0.2.3` expands to `>=0.2.3 <0.3.0`, whereas post-1.0
  `^1.2.3` expands to `>=1.2.3 <2.0.0`.
- For a 0.y package, `ocpe diff`'s required bump is shifted down one level: a
  major-class change requires a minor bump, a minor-class change requires a
  patch bump (see `ocpe diff` below).
- The OCPE specification itself is 0.1.0, so every domain package pins the
  specification minor: `ocpe_spec: ">=0.1.0 <0.2.0"`. A specification 0.2.0
  may break packages written for 0.1; packages migrate deliberately by
  widening `ocpe_spec` after adapting their content.
- Migrated domain packages are already at 1.x; for them the pre-1.0 shift does
  not apply and the change-class table holds directly (their dependency
  constraints follow the post-1.0 shape, e.g. `">=1.0.0 <2.0.0"`).

## Version constraints

Constraints follow the grammar in
`common.schema.json#/definitions/version_constraint` (and are evaluated by
`ocpe.versioning.satisfies`): alternatives separated by `||`; within an
alternative, comparators (`>=`, `>`, `<=`, `<`, `=`, `^`, `~`) separated by
whitespace are AND-ed; `*` matches any version. A bare version means `=`, and
partial versions are zero-padded (`1.2` means `1.2.0`). Pre-release versions
only satisfy a constraint that mentions the same core version. The engine
applies these constraints in three places: the package's `ocpe_spec` against
the engine's specification version; each `dependencies` entry against the
loaded dependency's version; and `bump_is_sufficient`'s internal comparisons
during `ocpe diff`.

## How `ocpe diff` classifies changes

`ocpe diff <old-dir> <new-dir>` compares two releases of one package (it warns
if the package ids differ) and reports:

1. **Detected changes.** For each identifier present in only one release:
   `identifier_added` / `identifier_removed`. For identifiers present in both:
   `identifier_kind_changed`, `dimension_changed`, `canonical_unit_changed`, a
   transition to `status: deprecated` (`identifier_deprecated`),
   `alias_added` / `alias_removed`, `evidence_added` when the evidence list
   grows, and `label_or_description_changed` when the label, definition or
   description differs.
2. **Severity mapping.** Each detected change is mapped to a severity through
   `change_classes.package`; change types not listed there default to patch.
3. **Required bump.** The highest severity among the detected changes
   (`required_bump`): major if any major-class change exists, else minor if any
   minor-class change exists, else patch. With no changes at all, no bump is
   required and the new version must simply not be lower than the old.
4. **Sufficiency.** `bump_is_sufficient(old_version, new_version, changes)`
   checks the declared bump against the requirement:
   - Post-1.0: a major requirement needs `new.major > old.major`; a minor
     requirement needs `(new.major, new.minor) > (old.major, old.minor)`; a
     patch requirement needs `new > old`.
   - Pre-1.0 (old major is 0 and `minor-is-breaking` applies): the requirement
     is shifted first — major→minor, minor→patch — and then the same tests
     run. A breaking change in a 0.y package is therefore satisfied by a minor
     bump.

Each change is printed with its severity, class, identifier and detail, and
the command exits 0 if and only if the declared bump is sufficient (1
otherwise). Run it before every release; it is the enforcement point for the
change-class table. Note that it classifies what it detects mechanically —
semantic judgement (whether an edit "really" changed a meaning) stays with the
author, per the permanence rules above.

## Governance of the compatibility rules

`compatibility.yaml` is itself a specification artifact, and changes to it are
governed by `change_classes.specification`:

| Severity | Change class | Meaning |
|---|---|---|
| major | `required_field_added` | A new mandatory field in a schema. |
| major | `field_removed_or_renamed` | A field disappears or changes name. |
| major | `enum_value_removed` | A value removed from an enum (e.g. a kind or status value). |
| major | `identifier_grammar_changed` | The CURIE grammar changes. |
| minor | `optional_field_added` | A new optional field. |
| minor | `enum_value_added` | A new enum value. |
| minor | `new_kind_added` | A new entity kind. |
| patch | `description_clarified` | Editorial clarification of a schema or rule. |

Because the specification is pre-1.0, its own minor bumps may carry breaking
changes under the pre-1.0 policy; specification changes of all severities are
recorded in `specification/versions/CHANGELOG.md`. The compatibility rules
exist to make versioning decisions mechanical and reviewable: a package
release's diff output, its declared bump, and the sufficiency verdict are all
reproducible from `compatibility.yaml` by the engine.
