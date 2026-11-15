# Open Computational Physiology Engine (OCPE)

OCPE defines the **common language of computational physiology** — a versioned,
machine-readable specification system through which AI agents, researchers,
software applications and datasets can communicate physiological concepts,
variables, relationships and evidence without reimplementing incompatible
schemas.

OCPE is **not** a simulation engine, not a dataset generator and not a signal
processor.

- Numerical ODE integration, synthetic patients/cohorts and trajectory
  simulation → **MOSAIC**
- ECG/PPG/EDA signal synthesis and derived-metric computation → **Lamina**
- Physiological knowledge — what things are, how they relate, what evidence
  supports the claims, in which context a number applies → **OCPE** (here)

## Repository layout

```
specification/     The normative contract: JSON Schemas (draft-07), the
                   identifier grammar, unit registry, predicate vocabulary,
                   functional forms, compatibility rules.
packages/          Independently versioned domain packages (cardiovascular,
                   autonomic, systemic, conditions.*, interventions.*,
                   wearables, populations, models.baroreflex-geddes-2022).
evidence/          Structured literature reviews and governance sidecars.
implementations/python/   The reference engine (pip-installable `ocpe`):
                   loader, validator, resolver, units, compatibility, CLI.
migration_archive/ Temporary preservation of pre-0.1 simulation components
                   destined for MOSAIC/Lamina (see MIGRATION_NOTES.md).
docs/              Mission, architecture, guides, integration contracts.
```

## Quick start

```bash
pip install -e implementations/python

ocpe validate packages/                     # validate every domain package
ocpe resolve ocpe:cardiovascular/heart-rate # canonical identifiers
ocpe resolve Hc --scope legacy-kb           # legacy symbols still resolve
ocpe resolve 'ocpe:models.baroreflex-geddes-2022/baroreflex-geddes-2022#RalpM'
ocpe show ocpe:conditions.pots/neuropathic-pots
ocpe deps                                   # declared dependency satisfaction
ocpe governance summary packages/           # OPTIONAL review tracking (ADR 0001)
```

From Python:

```python
import ocpe
reg = ocpe.load()                       # all packages + core vocabulary
report = ocpe.validate(reg)             # structural + semantic validation
r = ocpe.Resolver(reg).resolve("Hc", scope="legacy-kb")
print(r.id, r.unit)                     # ocpe:cardiovascular/heart-rate /s
```

Validation is **structural**: it establishes that content is well-formed,
internally consistent and resolvable. It does **not** establish scientific
validity.

## The defining architectural test

> Does this component help independent researchers, AI agents, or
> applications represent, interpret, validate, exchange, or version
> physiological knowledge?

If not, it probably does not belong in OCPE.

## Status

Specification 0.1.0 (provisional). Engine 0.1.0. Domain packages v1.x
(migrated from the pre-0.1 knowledge base; see `docs/migration-guide.md`).
The pre-refactor repository state is preserved at git tag
`pre-architectural-refactor`.

## Documentation

- `docs/mission.md` — what OCPE is and is not
- `docs/architecture.md` — how the pieces fit together
- `docs/specification-reference.md` — the schemas, field by field
- `docs/package-authoring-guide.md` — how to write a domain package
- `docs/ai-agent-guide.md` — how AI agents consume and contribute to OCPE
- `docs/versioning-policy.md` — versioning and compatibility rules
- `docs/migration-guide.md` — from the pre-0.1 knowledge base
- `docs/mosaic-integration.md` / `docs/lamina-integration.md` — downstream contracts
- `docs/adr/0001-sidecar-yaml-review-validation-tracking.md` — governance ADR (retained)
