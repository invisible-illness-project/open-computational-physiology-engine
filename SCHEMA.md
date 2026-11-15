# OCPE Schema

This file used to document the pre-0.1 knowledge-base YAML schema. That schema
is **retired**: it described the old `knowledge_base/` tree and was superseded
when OCPE became a versioned, machine-readable specification system. This
file is now a pointer to the normative contract.

## Where the machine-readable contract lives

- **JSON Schemas (draft-07, normative for specification 0.1.x):**
  `specification/schemas/*.schema.json` — one schema per entity kind, plus
  shared definitions in `common.schema.json`.
- **Identifier grammar:** `specification/core/identifiers.md` — the
  `ocpe:<package>/<local-id>` CURIE grammar, model-local `#symbol` references,
  stability rules and aliases.
- **Units:** `specification/core/units.yaml` — the canonical unit registry:
  UCUM case-sensitive codes, physical dimensions and reference-unit
  conversion factors used by the engine for dimensional checks.
- **Supporting core vocabulary:** `specification/core/` also holds the entity
  kind taxonomy (`kinds.yaml`), predicate vocabulary (`predicates.yaml`),
  functional forms (`functional-forms.yaml`), evidence scales
  (`evidence-scales.yaml`) and the specification meta-file (`meta.yaml`).
- **Human reference:** `docs/specification-reference.md` — the schemas
  described field by field.

The schemas are enforced by the reference engine
(`implementations/python/`, the `ocpe` CLI and Python API). Validation is
structural: it establishes that content is well-formed, internally consistent
and resolvable. It does not establish scientific validity.

## Schema inventory

The 19 schemas in `specification/schemas/`:

| Schema | Purpose |
|---|---|
| `common.schema.json` | Shared definitions referenced by every schema: CURIE and package-id grammar, unit codes, references, context, evidence helpers, deprecation. |
| `concept.schema.json` | Unquantified physiological entity (organ system, structure, process, mechanism) — has no unit or value; distinct from any quantity. |
| `condition.schema.json` | Disease, syndrome, phenotype, exposure or state; separates clinical claims from model-specific `model_representations`. |
| `derived-metric.schema.json` | Quantity computed by a declared algorithm from variables or series (e.g. RMSSD); the computation, including window and artifact handling, is part of the definition. |
| `document.schema.json` | A YAML/JSON file listed in a package manifest's `contents`; entities in it are discriminated by `kind` and validated against the per-kind schema. |
| `evidence.schema.json` | Attachable evidence statement: what is supported, by which references, at what strength; independent of review workflows. |
| `functional-form.schema.json` | Named qualitative/mathematical shape of a dependency (Hill sigmoid, first-order lag) used to qualify relationships without executable code. |
| `intervention.schema.json` | Test, protocol, therapy, drug or manipulation; protocols are declarative — in-silico execution belongs to downstream simulators. |
| `latent-construct.schema.json` | Theoretical quantity not directly observable even in principle; its values are estimates conditional on an operationalization, never measurements. |
| `measurement-method.schema.json` | Device, assay, procedure or pipeline that observes a quantity; performance is context-qualified and does not transfer silently. |
| `model.schema.json` | Declarative computational model specification: symbols with units and meanings, equations, assumptions, validity domain, evidence; no numerical execution. |
| `observation.schema.json` | Exchange record for a single observed, estimated, derived or simulated value of a quantity; `value_kind` separates measurements from estimates and synthetic data. |
| `package.schema.json` | Package manifest: id, version, `ocpe_spec` range, dependencies, contents. The package id is the CURIE namespace of its entities. |
| `population.schema.json` | Group description qualifying the context of ranges, evidence and performance; a context descriptor, not a generative cohort specification. |
| `predicate.schema.json` | A relationship type in the core predicate vocabulary. |
| `provenance.schema.json` | Where content came from and how it was produced; descriptive only, implying no review or approval. |
| `reference.schema.json` | Bibliographic record keyed by a persistent identifier (DOI, PMID, ...); transcribed from the source, never inferred. |
| `relationship.schema.json` | Typed, directed `subject PREDICATE object` assertion with optional functional form, model-equation pointer, context and evidence. |
| `variable.schema.json` | Quantifiable, time-varying property measurable in principle; independent of measurement method and of any recorded value. |

Separately, `specification/schemas/governance/review-manifest.schema.json` is
the OPTIONAL governance extension (ADR 0001): the `*.review.yaml` sidecar
recording review events, claims, challenges and adjudication for one content
addressed asset. It is not required to use the core engine or the 19 schemas
above.

## The retired knowledge-base schema

The old YAML knowledge-base schema (publication-review frontmatter, central
variable/relationship/model registries) described content that either
migrated into OCPE packages or left the repository. It applies only to the
pre-0.1 tree, recoverable verbatim at git tag `pre-architectural-refactor`.
The file-by-file mapping from the old knowledge base to OCPE 0.1 locations is
in `docs/migration-guide.md`; components that left the repository entirely
(simulation, sensor models, results) are inventoried in
`migration_archive/MIGRATION_NOTES.md`.
