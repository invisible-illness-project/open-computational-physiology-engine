# MOSAIC Integration Contract

MOSAIC is the downstream home of physiological **simulation**: numerical
model execution, disease-specific models, patient and cohort generation,
synthetic datasets, sensor simulation and simulation validation. This
document fixes the boundary: what MOSAIC owns, what it consumes from OCPE,
and the contract it must honor.

## Ownership

| MOSAIC owns | OCPE owns |
|---|---|
| Physiological simulation (ODE/DAE integration, event handling) | The language models are specified in |
| Disease-specific models and their parameterizations | Model *specifications*: identity, symbols, equations, assumptions, units, evidence |
| Patient and cohort generation | Population *descriptors* as package content |
| Synthetic datasets | The observation/dataset description formats |
| Sensor simulation | Measurement-method semantics (via packages) |
| Simulation validation (numerical correctness, phenotypic fidelity) | Structural validation of the specifications validation consumes |
| Numerical results, trajectories, telemetry | Provenance/evidence structures for citing them |

## What MOSAIC consumes from OCPE

1. **Model specifications** (`model.schema.json` entities, typically in a
   domain package): symbols with roles/units/`represents`, equations with
   input/parameter/output sets, assumptions, validity domains, and
   `implementations` links. MOSAIC registers itself as an implementation of
   the models it executes.
2. **Canonical quantities**: variables, latent constructs and derived metrics
   that model inputs/outputs represent, so simulated output is labelled with
   the same identifiers real measurements use.
3. **Units**: the UCUM registry for dimensional consistency between model
   symbols, simulated outputs and observed data.
4. **Observation exchange**: synthetic data is exported as observation
   records with `value_kind: simulated` and the producing `model` named —
   indistinguishable in format from (and explicitly distinguished in
   `value_kind` from) real measurements.
5. **Evidence structures**: model validation claims reference the same
   evidence/reference machinery as every other OCPE assertion.

## The contract MOSAIC must honor

1. **Execution fidelity.** MOSAIC executes the equations a model entity
   declares. If MOSAIC deviates (solver behavior, defaults, extensions), the
   deviation is documented in its `implementations[].conformance_note`; it
   never silently rewrites the specification.
2. **Identifier discipline.** Simulated outputs use the canonical identifiers
   of the quantities model symbols `represent`. Model-local symbols stay
   model-local (`model#symbol` references); they are not minted as new
   physiological identifiers.
3. **Unit discipline.** Values cross boundaries in declared units; conversion
   uses the OCPE registry. Mixed-unit datasets declare units per record.
4. **Honest provenance.** Synthetic data is `value_kind: simulated` with the
   model (name + version via its package) recorded. Datasets describe their
   generation provenance through the standard provenance schema.
5. **Structural ≠ scientific.** MOSAIC may advertise "conforms to OCPE
   package X" only as structural conformance; numerical and scientific
   validation remain MOSAIC's claims, backed by its own evidence.
6. **No upstream divergence.** Disease models, parameter sets and population
   definitions evolve in domain packages (MOSAIC's own packages where it is
   the author). OCPE repository changes are never required to ship a model.

## Data flow

```
OCPE domain packages (model specs, quantities, units)
        │  ocpe load / ocpe export
        ▼
MOSAIC simulation engine ── executes declared equations ──► trajectories
        │
        ▼
OCPE observation records (value_kind: simulated, model named)
        │
        ▼
datasets / analysis tools (validated with ocpe check-observation)
```
