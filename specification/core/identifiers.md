<!-- Copyright 2026 The Invisible Illness Project. SPDX-License-Identifier: Apache-2.0 -->

# OCPE Canonical Identifiers

**Status:** normative for OCPE specification 0.1.x

## 1. Syntax

Every OCPE entity has exactly one canonical identifier: a compact URI (CURIE) of the form

```
ocpe:<namespace>/<local-id>
```

| Part | Grammar | Example |
|---|---|---|
| prefix | literal `ocpe` | `ocpe` |
| namespace | the owning **package id**: one or more dot-separated segments, each lowercase kebab-case (`[a-z][a-z0-9]*(-[a-z0-9]+)*`) | `example-org`, `consortium.project-a` |
| local-id | lowercase kebab-case (`[a-z0-9]+(-[a-z0-9]+)*`) | `flow-rate` |

Examples: `ocpe:example-org/flow-rate`, `ocpe:consortium.project-a/output-rate`,
`ocpe:core/regulates`.

The authoritative regular expression lives in
[`common.schema.json`](../schemas/common.schema.json) (`definitions.curie`).

### Model-local symbol references

A symbol declared inside a computational model specification is referenced as

```
<model-curie>#<symbol>
```

e.g. `ocpe:example-org.flow-demo/flow-demo#Rtot`. Symbols are
case-sensitive and only meaningful inside the declaring model. A model symbol is
**not** a physiological identifier; it may *represent* one (`represents:` field).

### Prefix expansion

The `ocpe:` prefix expands to `https://w3id.org/ocpe/id/`, so
`ocpe:example-org/flow-rate` ≡ `https://w3id.org/ocpe/id/example-org/flow-rate`.
The persistent-URL registration is pending; until it is registered the CURIE is the only
normative form.

## 2. Stability rules

1. **Identifiers are permanent.** Once a package release contains an identifier, its
   meaning must not change. A meaning change requires a new identifier.
2. **Identifiers are never reused.** A withdrawn identifier remains reserved.
3. **Deprecation, not deletion.** Retiring an identifier requires `status: deprecated`
   plus a `deprecation` block (`deprecated_in`, `reason`, optional `replaced_by`) for at
   least one minor release before removal in a major release.
4. **Namespace = package.** Only the package whose `id` equals the namespace may define
   identifiers in that namespace.
5. **Labels and aliases are not identifiers.** They may change in minor releases;
   canonical identifiers may not.

## 3. Aliases

Aliases map other names onto canonical identifiers — synonyms, abbreviations,
symbols from an author's previous notation, or unit-qualified spellings.

```yaml
aliases:
  - value: FR
    type: symbol
    unit: mL/s           # 'FR' denotes the quantity expressed in mL/s
```

* Aliases are case-sensitive (`FR` ≠ `fr`).
* An alias with a `scope` is only unique within that scope (a package id or a
  model CURIE). The resolver reports an ambiguity rather than guessing when an
  unscoped lookup matches several entities.
* An alias that implies a unit (`unit:`) denotes the same quantity in a different unit.
  It does not create a new quantity.

## 4. Choosing local-ids

* Use the established English name in kebab-case (`mean-flow-rate`).
* Do not encode units, models, populations or measurement methods in a variable's
  local-id. Where a model abstraction has no direct physiological equivalent, say so
  explicitly (e.g. with `observability: model_compartment`).
* Do not use model symbols as local-ids.
