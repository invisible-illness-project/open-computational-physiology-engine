# OCPE Mission

**OCPE is the common language of computational physiology.** It is a
versioned, machine-readable specification system through which AI agents,
researchers, software applications and datasets communicate physiological
concepts, variables, relationships and evidence without reimplementing
incompatible schemas.

OCPE is semantic infrastructure. It answers questions like: What is this
quantity — a variable, a derived metric, a latent construct? Which unit and
dimension does it have? What is known to cause, regulate or derive it, with
what evidence, in which population and posture and activity context? Which
version of which package defined this identifier, and is it still valid to
use?

## In scope

- A canonical identifier scheme (`ocpe:<package>/<local-id>`, spec:
  `specification/core/identifiers.md`) with aliases for legacy symbols.
- JSON Schema contracts for distinct entity kinds: concepts, variables,
  observations, measurement methods, derived metrics, latent constructs,
  conditions, interventions, populations, models and relationships. These
  kinds are **not interchangeable** and the schemas enforce the distinctions.
- Machine-readable evidence attachments (references, levels/tiers preserved
  verbatim from source curation) and context-qualified reference ranges and
  measurement performance (population ranges are never universal truths).
- Declarative computational model specifications: symbols, equations,
  assumptions, units, nominal values with provenance, validity domains.
  Numerical execution is deliberately excluded.
- A small semantic engine (loader, validator, resolver, units, compatibility)
  and an optional, separable evidence-layered governance extension
  (ADR 0001) whose review workflows and authorization policies are **not**
  required to use the core engine.
- Explicit package dependencies and version compatibility declarations.

## Out of scope (and where it lives)

| Capability | Home |
|---|---|
| Numerical ODE/DAE integration of physiological models | MOSAIC |
| Synthetic patient or cohort generation | MOSAIC |
| Beat-by-beat cardiovascular simulation | MOSAIC |
| Disease-specific physiological trajectory simulation | MOSAIC |
| Clinical cohort management | MOSAIC |
| ECG, PPG, EDA signal synthesis or processing | Lamina |
| Derived HRV metric computation from signals | Lamina |

## Principles

1. **Structural validation is not scientific validation.** Every validator
   output carries this disclaimer; no green checkmark asserts biological truth.
2. **Evidence is attached to specific aspects** (existence, direction,
   magnitude, ...). Direction-level evidence must never be read as
   magnitude-level support.
3. **Context-qualification.** Reference ranges, sensor accuracy and evidence
   apply to stated populations, postures, activities and methods; they do not
   transfer silently.
4. **Identifier permanence.** Identifiers never change meaning and are never
   reused; retirement happens via deprecation, not deletion.
5. **No discarded science.** Migrations preserve content verbatim (values,
   citations, curation notes); restructuring never re-grades evidence.
6. **The architectural test.** Does a component help represent, interpret,
   validate, exchange or version physiological knowledge? If not, it belongs
   in a downstream application, not in OCPE.
