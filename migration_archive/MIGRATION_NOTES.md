# Migration Notes — Pre-0.1 OCPE → OCPE 0.1

**Status:** preservation verified (2026-11-14). This archive is **temporary**: it
exists so that downstream applications (MOSAIC, Lamina) can extract the
components assigned to them. Once MOSAIC and Lamina confirm extraction, this
directory is deleted; everything in it remains recoverable from git history at
tag `pre-architectural-refactor` (commit `c0d8678`).

OCPE is now a specification and semantic interoperability engine. Numerical
simulation, synthetic data generation and signal synthesis are out of scope
(see `docs/mission.md`). The components below were removed from the active
repository because they fail the architectural test — they do not help
represent, interpret, validate, exchange or version physiological knowledge.

## Destination and status of every preserved component

| Archived component | Destination application | Status |
|---|---|---|
| `simulation/engine.py` — beat-by-beat Radau ODE solver | MOSAIC | preserved here; extract then delete |
| `simulation/perturbations.py` — disease perturbation execution (YAML loading logic is superseded by the OCPE engine) | MOSAIC | preserved here; extract then delete |
| `simulation/behavior.py` — exercise/meal/sleep modulation | MOSAIC | preserved here; extract then delete |
| `simulation/symptoms.py` — probabilistic symptom scoring | MOSAIC | preserved here; extract then delete |
| `simulation/latent_physiology.py` — latent state extraction from ODE output | MOSAIC | preserved here; extract then delete |
| `simulation/time_engine.py` — circadian + homeostatic sleep pressure | MOSAIC | preserved here; extract then delete |
| `simulation/population.py` — virtual subject/cohort generation | MOSAIC | preserved here; extract then delete |
| `models/baroreflex_model.py` — Geddes 2022 Python implementation (+ `baroreflex_model.py.review.yaml` sidecar) | MOSAIC | preserved here; extract then delete. The DECLARATIVE specification of this model stays in OCPE at `packages/models/baroreflex-geddes-2022/`. |
| `validation/evaluator.py`, `validation/validation_suite.py` — simulation output plausibility checks | MOSAIC | preserved here; extract then delete |
| `sensor_models/wearable_sensors.py` — ECG/PPG signal synthesis | Lamina | preserved here; extract then delete |
| `examples/` — simulation runner scripts | MOSAIC | preserved here; extract then delete |
| `results/*.npz` — synthetic telemetry outputs of the pre-0.1 simulator | MOSAIC | preserved here; regenerate in MOSAIC, then delete |
| `tests/test_orthostatic_response.py`, `test_steady_state_params.py`, `test_experimental_mode.py` — simulation behavior tests | MOSAIC | preserved here; extract then delete |
| `docs/latent_physiology.md`, `docs/validation_strategy.md` — simulation design docs | MOSAIC | preserved here; extract then delete |
| MATLAB clone of `github.com/msolufse/BaroreflexPOTSmodel` @ `871f46f` (MIT license; upstream DOI `10.48550/arXiv.2109.14558`) | MOSAIC decides how to incorporate | **deleted** (was an untracked, gitignored local clone). Upstream provenance, license, commit and citation requirement are preserved in the model specification (`source.upstream_implementation`) and in `docs/mosaic-integration.md`. |
| `tools/validate_kb.py`, `tools/ocpe.py` (old CLI) | superseded | **deleted**. Superseded by the OCPE engine validator and the `ocpe` CLI (`implementations/python/`). `tools/review_tracker.py` moved into the engine as `ocpe.governance.tracker`. |
| `knowledge_base/` YAML content | OCPE packages | **migrated** — every file's content now lives in `packages/` (see `docs/migration-guide.md` for the file-by-file mapping). Review sidecars moved alongside their assets with updated paths, hashes and a migration review record. |
| `docs/vision.md` | OCPE docs | **replaced** by `docs/mission.md`. |

## Scientific content preservation

- All 31 DOIs and 13 PMIDs cited anywhere in the legacy knowledge base appear
  in the new `packages/` / `evidence/` / `specification/` tree (verified
  programmatically during the migration).
- Evidence levels/tiers, review-status strings, compliance guards,
  validation criteria and machine-calibrated annotations were transcribed
  verbatim into evidence / curation fields. No scientific content was
  re-graded; structural (schema) validation was never claimed as scientific
  validation.
- Legacy registry gaps were closed, not hidden: `RMSSD` and the RR interval
  are now registered (`packages/autonomic/metrics.yaml`,
  `packages:cardiovascular/rr-interval`); the four unregistered mechanistic
  `type` values are registered functional forms in the core package.

## What was intentionally NOT carried over

- Legacy per-parameter `phenotypes` sub-tables in
  `knowledge_base/equations/mathematical_models.yaml` (v1.0): superseded by
  the newer-curated perturbations in `packages/conditions.*` and
  `packages/interventions/medication` (v1.1–v1.5). Where values conflicted,
  the newer curation cycle wins; the old table remains in git history.
- Numerical solver settings, initialisation routines and run orchestration:
  MOSAIC configuration, not OCPE content.
