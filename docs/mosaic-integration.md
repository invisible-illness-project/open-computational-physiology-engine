# MOSAIC Integration Contract

MOSAIC is the downstream simulation platform: numerical ODE integration,
beat-by-beat cardiovascular simulation, synthetic patient/cohort generation and
disease-specific trajectory simulation (see `docs/mission.md`, "Out of
scope"). OCPE is upstream of MOSAIC: it supplies the versioned, machine-readable
physiological knowledge MOSAIC executes against. This document is the contract
between the two. It is grounded in `migration_archive/MIGRATION_NOTES.md`,
`packages/models/baroreflex-geddes-2022/baroreflex-geddes-2022.yaml`,
`packages/conditions/pots/pots.yaml`, `packages/interventions/tilt-test/tilt-test.yaml`,
`packages/populations/populations.yaml` and `docs/migration-guide.md`.

## What MOSAIC receives from the pre-0.1 repository

The following components of the pre-0.1 simulator were removed from the active
repository and are preserved — temporarily — under `migration_archive/`. They
are assigned to MOSAIC. Once MOSAIC confirms extraction, the archive directory
is deleted; everything in it remains recoverable from git history at tag
`pre-architectural-refactor` (commit `c0d8678`).

| Component | What it is |
|---|---|
| `simulation/engine.py` | Beat-by-beat Radau ODE solver |
| `simulation/perturbations.py` | Disease perturbation execution. Its YAML loading logic is superseded by the OCPE engine — do not resurrect the loader; consume packages through the engine (below) |
| `simulation/behavior.py` | Exercise/meal/sleep modulation |
| `simulation/symptoms.py` | Probabilistic symptom scoring |
| `simulation/latent_physiology.py` | Latent state extraction from ODE output |
| `simulation/time_engine.py` | Circadian + homeostatic sleep pressure |
| `simulation/population.py` | Virtual subject/cohort generation |
| `models/baroreflex_model.py` | Geddes 2022 Python implementation (with `baroreflex_model.py.review.yaml` sidecar). The declarative specification of this model stays in OCPE at `packages/models/baroreflex-geddes-2022/` |
| `validation/evaluator.py`, `validation/validation_suite.py` | Simulation output plausibility checks |
| `examples/` | Simulation runner scripts |
| `results/*.npz` | Synthetic telemetry outputs of the pre-0.1 simulator. These are not extracted as data: regenerate them in MOSAIC, then delete |
| `tests/test_orthostatic_response.py`, `tests/test_steady_state_params.py`, `tests/test_experimental_mode.py` | Simulation behavior tests |
| `docs/latent_physiology.md`, `docs/validation_strategy.md` | Simulation design documents |

Numerical solver settings, initialisation routines and run orchestration were
intentionally not carried into OCPE content: they are MOSAIC configuration, not
physiological knowledge.

## What MOSAIC consumes from OCPE at runtime

MOSAIC loads OCPE packages with the reference engine
(`pip install -e implementations/python`, then the `ocpe` CLI or the Python
API) and consumes four kinds of content:

**Phenotype model representations** — `packages/conditions.*` (today
`conditions.pots`: neuropathic, hyperadrenergic, hypovolemic phenotypes). Each
phenotype carries a `model_representations` block for the Geddes 2022 model
containing:

- `parameter_perturbations` — curated, evidence-cited parameter changes
  (perturbed value, unit, mechanism, evidence with level/tier, curation
  status). These are the perturbations MOSAIC applies by default.
- `unverified_parameter_perturbations` — machine-calibrated or
  partially-evidenced values (for example the neuropathic `dV_veno_max`
  reduction, calibrated but explicitly marked "Do NOT promote to
  parameters_perturbed"). These are **consumer-inert**: MOSAIC must not apply
  them unless it explicitly opts in.
- `constraints` — including `do_not_perturb` guards with rationale and
  evidence (for example: never perturb `mvl`/`VMvl` in neuropathic POTS —
  venous compliance is normal or reduced, pooling arises from lost tone; never
  reduce `dV_veno_max` in hyperadrenergic POTS — that would mislabel a gain
  disorder as denervation).
- `validation_criteria` — see the last section of this document.

Phenotypes are composable, not mutually exclusive (Angeli 2024: 41.7% of POTS
patients carry two phenotypes, 11.4% all three), so MOSAIC must be able to
apply several phenotypes' perturbation sets to one subject.

**The declarative model specification** —
`packages/models.baroreflex-geddes-2022/baroreflex-geddes-2022.yaml`. This is
the specification MOSAIC's solver implements: 24 equations with structured
input/parameter/output declarations and LaTeX, 12 ODE states plus auxiliary and
control-law symbols, each with unit and, where one exists, the physiological
variable it `represents`; nominal parameter values with provenance; assumptions,
limitations and a validity domain (healthy control and POTS clinical cohorts).
What is deliberately not in the specification: solver choice, step size,
initialisation, and the valve flow laws (`qav`, `qmv`) with the
varying-elastance-driven beat-by-beat mechanics — those live in
implementations, i.e. in MOSAIC.

**Intervention protocols** — `packages/interventions.tilt-test`. The head-up
tilt protocol is declared as phases (`supine_rest` 200 s, `tilt_up` 14 s at
60 deg, `sustained_tilt` 100 s at 60 deg and 25 cm effective height,
`tilt_down` 14 s). Protocol descriptions are declarative; executing a protocol
in silico is MOSAIC's responsibility.

**Population context descriptors** — `packages/populations`. These qualify in
which context physiological statements apply (cohort descriptors with
demographics and inclusion criteria). They are context descriptors, not
generative cohort specifications; virtual cohort generation is MOSAIC's job.

## The contract MOSAIC must honor

1. **Apply only verified perturbations by default.** MOSAIC applies
   `parameter_perturbations` and nothing else unless it has explicitly opted
   into `unverified_parameter_perturbations` (same semantics as the legacy
   `unverified_parameters` block; see `docs/migration-guide.md`). Opting in
   must be a deliberate, visible configuration choice, not a default.
2. **Honor `constraints.do_not_perturb`.** A constrained parameter is not
   perturbable within that representation, whatever the clinical intuition;
   the constraint carries its rationale and evidence tier.
3. **Honor the `application` semantics.** Perturbation entries declare a
   `trigger` (e.g. `head_up_tilt_onset`) and a transition ("10-s delayed
   smooth transition to target, Geddes 2022 Eq. 2.16 — NOT a static baseline
   override"). Where an entry declares no trigger (the neuropathic
   `dV_veno_max` capacity reduction is static), MOSAIC must not invent one.
4. **Declare dependencies in its own manifest.** MOSAIC declares which OCPE
   package versions it supports and its `ocpe_spec` range, mirroring the
   `dependencies` and `ocpe_spec` fields of an OCPE `package.yaml`, and
   re-verifies them with `ocpe deps` / `ocpe validate`.
5. **Load and validate packages with the engine.** Packages are consumed
   through the OCPE engine (`ocpe.load`, `ocpe.validate`, the `ocpe` CLI), not
   by parsing YAML ad hoc. This keeps MOSAIC on the structural-validation
   contract and on canonical identifier resolution.
6. **Never edit OCPE content locally.** Fixes, new perturbations,
   re-curated values and solver-relevant corrections are proposed upstream, in
   OCPE, through its governance process (ADR 0001 sidecars). MOSAIC carries no
   private fork of OCPE knowledge.
7. **Keep structural and scientific validation apart.** A green `ocpe
   validate` establishes that content is well-formed, internally consistent
   and resolvable. It does not establish that a simulation is physiologically
   correct; that is what MOSAIC's own validation suite and the
   `validation_criteria` are for.

## The MATLAB upstream

The model specification records its upstream implementation
(`source.upstream_implementation`):

- Repository: `https://github.com/msolufse/BaroreflexPOTSmodel.git`
- Commit: `871f46f`
- Language: MATLAB; License: MIT
- Citation requirement: Geddes JR, Ottesen JT, Mehlsen J, Olufsen MS. J R Soc
  Interface 2022;19:20220220 (DOI `10.1098/rsif.2022.0220`).

A local clone of this repository existed in the pre-0.1 working tree; it was
untracked and gitignored and has been deleted. The provenance, license, commit
and citation requirement above are the preserved record — this document and
the model specification are where they now live. How MOSAIC incorporates the
MATLAB code (ports it, wraps it, or treats it as a reference to reimplement)
is MOSAIC's decision; the MIT license permits all of these. The citation
requirement applies regardless of the incorporation path.

## Validation criteria are acceptance signatures, not assertions

`validation_criteria` in a model representation are acceptance criteria the
representation is expected to satisfy — for example "tilt delta-HR >= 30 bpm"
for every POTS phenotype, or "upright delta-SBP >= +10 mmHg" for the
hyperadrenergic phenotype. Declaring a criterion does not assert that any
model satisfies it; it tells MOSAIC what to test its implementation against
and what to report.

Read them as signatures with diagnostic value in both directions. The
hyperadrenergic curation notes illustrate this: with `TotalVol = 3900 mL` the
delta-HR criterion is met in silico (34.2 bpm) while the delta-SBP pressor
criterion remains unmet (-4.0 mmHg simulated), and the criterion text itself
flags that a simulated delta-HR far exceeding the other phenotypes would be a
red flag rather than fidelity (Okamoto 2024: the hyperadrenergic biomarker is
the pressor response, not excess tachycardia). MOSAIC reports criterion
results against the declared tier; it does not treat the criteria as
pre-satisfied.
