# OCPE Swarm Engineering SPEC — Dataset-Readiness Program (Phase 2)

Single source of truth for all implementation agents. Governing scientific document:
`docs/evidence_package/OCPE_EVIDENCE_AND_SIMULATION_SPECIFICATION_v1.0.md` (user-approved baseline).
Machine-readable evidence layer: `docs/evidence_package/EVIDENCE_REGISTRY.yaml`,
`PHYSIOLOGICAL_RELATIONSHIPS.yaml`, `PARAMETER_SPECIFICATION.yaml`, `EVENT_PROTOCOLS.yaml`.
Gap register: `docs/evidence_package/OCPE_RESEARCH_GAP_ANALYSIS.md` (10 P0 / 17 P1 / 22 P2 / 6 P3).
Integration branch: `swarm/dataset-readiness`. Evidence scale everywhere: E0 hypothesis … E5 meta-analysis/consensus.

## Global rules (binding on every agent)

1. Never invent a scientific value. If evidence is insufficient, write `unresolved` and flag it.
2. Tier-D / machine-calibrated / E0–E1 parameters remain EXPERIMENTAL and engine-inert in canonical mode.
3. No latent physiology (absolute BP, SV, CO, SVR, venous pooling, cerebral perfusion, core temp,
   hydration, insulin, glucose-except-CGM, BRS) may appear as a sensor channel. Latent = ground truth only.
4. No disease-specific signal modification that bypasses mechanism (`if disease: HR += 30` is forbidden).
5. Anti-laundering: between-condition separation must not exceed evidence-honest bands; >0.95 AUC
   disease classification = release failure. Do not engineer data to "win".
6. Every new/changed scientific constant carries: value, units, distribution, evidence tier (E0–E5),
   source (registry claim_id), canonical/experimental status, uncertainty.
7. Tests: every change adds regression tests. `pytest tests/` must pass before commit
   (except formally-scoped xfails, which must carry a written scientific justification).
8. Report per the §25 schema of the master prompt (agent/scope/files/evidence/uncertainties/tests/blockers).
9. Python 3 + numpy/scipy/PyYAML only. No new dependencies without orchestrator approval.
10. Do not modify files outside your ownership list. Interface needs → propose in report, don't hack.

## Worktree protocol (every agent)

```bash
cd /mnt/agents/output/ocpe_repo
git worktree add $HOME/work-<your-branch> -b <your-branch> swarm/dataset-readiness
cd $HOME/work-<your-branch>   # work ONLY here; commit on <your-branch>
```
Never run `git worktree prune`. Never edit /mnt/agents/output/ocpe_repo working tree directly.

---

## Agent W1-A — Core Engine (branch `fix/engine-core`)

Owns: `simulation/engine.py`, `simulation/behavior.py`, `simulation/time_engine.py`,
`simulation/symptoms.py`, `simulation/latent_physiology.py`, `simulation/population.py`,
`tests/test_experimental_mode.py`, `tests/test_steady_state_params.py`, new `tests/test_event_kernels.py`,
`tests/test_pem.py`, `tests/test_circadian.py`. MUST NOT touch: `validation/`, `sensor_models/`,
`tests/test_orthostatic_response.py`, `knowledge_base/**`, `tools/`.

### G-P0-01 — Behavior parameter compounding (verified bug, engine.py ~line 139)
Current: behavior modifiers recomputed from `self.model.params` each beat → multiplicative
perturbations compound per heartbeat (5 beats of meal: RalpM 17.88→4.24; exercise Es ×1.30/beat unbounded).
Fix with explicit event/state semantics:
- Engine keeps an immutable `baseline_params` snapshot per simulation run.
- An `EventKernel` (new class, may live in `simulation/event_kernels.py` under your ownership) defines:
  `event_id, trigger, onset_distribution, duration_distribution, magnitude_distribution,
  affected_parameters, mechanism, interaction_rules, recovery_kernel, evidence_tier, provenance`
  (per master prompt §11). Kernels compose additively-in-effect-space (or multiplicatively against
  BASELINE, never against already-modified params).
- Active events each beat produce a transient parameter overlay: `effective = f(baseline, active_kernels, t)`.
- Regression test: simulate meal event for N beats then recovery; assert parameters return to baseline
  and no exponential drift (assert RalpM within tolerance of one-shot 13.41 during plateau, exact
  baseline after recovery). Same for exercise (Es bounded, defined by kernel plateau).

### G-P0-02 — PEM machinery
Current: `engine.py` never passes `current_exertion`; `is_sleeping` hardcoded False; constants ~2 orders
of magnitude off evidence (2-h "resolution" vs mean 12.7-day recovery).
Implement TWO decoupled kernels (evidence: DISEASE_EVIDENCE_MECFS.md, CONTRADICTION_AUDIT §6):
- `pem_symptom_kernel`: Gamma-shaped onset 12–48 h post-exertion, peak 24–48 h, recovery mean 12.7 d
  (range 1–64 d; Moore 2023 n=144). Symptom-layer only. Probabilistic episode detectability.
- `slowed_recovery_kernel` (physiological): healthy post-exercise recovery 3–6 h vs post-VT1 patient
  9–13 h (long-COVID wearable evidence, E2). Any physiological "second wave" remains E0-labeled and
  OFF by default (honesty flag `extrapolated_E0` when enabled).
- Wire exertion state into engine (fix the dead-code path). Multi-day timescale → coordinate with
  G-P0-06 time semantics below.

### G-P0-06 — Circadian + sleep
- Add 24-h time semantics to the time engine: simulation clock carries wall-time + day index.
- Circadian autonomic modulation: cosinor (24 h + optional 12 h harmonic) on vagal/sympathetic drive
  and resting HR (amplitude ~13.5 bpm, acrophase ~14:40 — HEALTHY dossier; E2/E4). BP dip 14±5% at night.
- Sleep/wake state machine (awake/NREM/REM-lite granularity): autonomic shifts per stage
  (HEALTHY dossier §sleep), sleep fragmentation capability, optional OSA modulation (E3 — leave hook,
  default OFF, experimental).
- Multi-day simulation support with OU baseline drift (τ 3–7 d) and day-to-day RHR CV ≈4.6%,
  lnRMSSD CV ~3–13% (POPULATION dossier).
- Circadian/sleep outputs MUST couple into model parameters (currently fictional). Menstrual modulator
  hook: luteal RHR +2–5 bpm, skin temp +0.2–0.3 °C, RMSSD −~10% (Alzueta 2022; E2/E4) — implement as
  optional population-level toggle, default OFF unless cohort config enables.

### G-P0-04 — Engine/KB consistency
- Single authoritative parameter source: KB YAML (`knowledge_base/`) loaded at init; no silent
  hardcoded duplicates in code. Fix: hyperadrenergic kR/kH/p2H `normal_value` mismatch (KB nominals
  25/25/88.66 vs file's 23/27/88.5 → applied 34.78/31.48/89.96 instead of documented 32/34/89.8);
  stale dead inline `phenotypes:` blocks in `mathematical_models.yaml` (kR=40, kH=40, RalpM=6.5) —
  flag them to orchestrator (KB files are NOT yours; report exact conflicts, do not edit KB).
  Where a code constant duplicates a KB value, make code read KB and leave a provenance comment.
- HRmax equation: replace Fox 220−age with Tanaka 208−0.7·age (E5) where HRmax is used.
- VirtualSubject priors (sex/BMI/fitness) must be cited from POPULATION dossier or marked provisional.
- Add a consistency test: every parameter the engine applies must match its KB/documented value
  (guard against regression of the 34.78-vs-32 class of bug).

---

## Agent W1-B — Evidence Governance (branch `feat/evidence-governance`)

Owns: `tools/` (validate_kb.py, review_tracker.py, new tools), `knowledge_base/**` (schema-level only —
no parameter value changes), new `validation/provenance_gate.py`, `tests/test_governance.py`.
MUST NOT touch: `simulation/`, `sensor_models/`, `validation/evaluator.py`, `validation/validation_suite.py`.

### G-P0-08 — Canonical/experimental separation
- Introduce explicit `canonical_status: canonical|experimental` on every disease/phenotype/parameter
  block in KB YAML (schema extension, backward-compatible default = experimental for tier-D).
- A generation-mode gate: `canonical` mode refuses to apply experimental perturbations (fail-closed
  with clear error); `experimental` mode requires explicit opt-in flag. Currently hEDS, autoimmune,
  sleep_deprivation, beta_blocker are experimental-only engine-inert — formalize, don't change science.
- Fludrocortisone chronic-phase limitation: annotate in KB as schema limitation (P2), do not fix science.

### G-P0-10 — Evidence harmonization
- Extend KB schema so every parameter carries: `evidence_tier` (map repo tiers A–D → E-levels per
  EVIDENCE_AUDIT_NOTES: A≈E4–5, B≈E2–3, C=provenance-label-not-a-grade, D≈E0), `source_claim_ids`
  (into docs/evidence_package/EVIDENCE_REGISTRY.yaml), `uncertainty`, `provenance`, `canonical_status`.
- Build `validation/provenance_gate.py`: dataset-build preflight that refuses KB files which are
  missing review, STALE per review_tracker, missing tier, missing provenance, or experimental (in
  canonical mode). Unit-test the fail-closed behavior incl. hash-tamper test (modify file after review →
  gate must reject).
- Extend `tools/review_tracker.py` minimally if needed for gate integration (keep schema v1.0.0
  compatibility). Record AI-agent reviews for files you legitimately review; human-L3 remains absent —
  gate must surface that as a WARNING (not silent pass) pending human review.
- Remove/resolve the dead inline `phenotypes:` blocks in `knowledge_base/equations/mathematical_models.yaml`
  (kR=40, kH=40, RalpM=6.5 contradict diseases/pots.yaml) — W1-A reports, YOU remove + record review.

---

## Agent W1-C — Orthostatic Reference & Phenotype Scoping (branch `fix/orthostatic-reference`)

Owns: `validation/evaluator.py`, `validation/validation_suite.py`, `tests/test_orthostatic_response.py`,
`knowledge_base/interventions/tilt_test.yaml`, `docs/` (new `docs/orthostatic_reference.md`),
KB annotation comments in `knowledge_base/diseases/pots.yaml` (comments/annotations ONLY — no value changes).
MUST NOT touch: `simulation/`, `sensor_models/`, `tools/`.

### G-P0-09 — Freeze protocol-conditioned healthy reference
- Define ONE metric semantics used identically by model, tests, evaluator, dataset generator:
  `sustained_delta_HR = mean(HR, minutes 5–10 of tilt) − mean(HR, final 5 min supine)`.
  Also record `initial_transient` (first 30 s) separately — never conflate the two timescales.
- Freeze the protocol-conditioned healthy reference table from EVENT_PROTOCOLS.yaml into
  `docs/orthostatic_reference.md` + machine-readable `validation/healthy_reference.yaml`
  (stand casual N(+12,5); stand lab ~+25; 60–70° HUT 10-min sustained distribution; NASA lean +34±8;
  healthy false-positive tail: <5% casual stand, up to 33% aggressive protocols — preserve tails).
- Evaluator compares simulated distributions against this reference with protocol conditioning
  (tilt ≠ stand ≠ lean). Update `tilt_test.yaml` protocol metadata to match (angle, duration, sampling).

### G-P0-03 — Neuropathic POTS formal scoping
- Do NOT fix the science. Formally scope neuropathic POTS as `experimental-xfail`:
  keep the strict-xfail test, add written justification in the test docstring + pots.yaml annotation
  (engine-falsified: 21.2 vs ≥30 bpm; flat dose-response; needs bounded stress-relaxation creep per
  van Heusden 2006 and/or Geddes Eq. 2.16 tilt-onset application semantics — reference GAP register).
- Add a dataset-level exclusion marker so canonical generation rejects neuropathic (coordinate
  interface with W1-B's gate via report; do not edit their files).
- Hyperadrenergic: annotate its ΔSBP pressor criterion failure (simulated −4.0 vs required +10 mmHg)
  as a disclosed limitation in evaluator output; do not silently pass it.

---

## Agent W1-D — Sensor Realism (branch `feat/sensor-realism`)

Owns: `sensor_models/`, `knowledge_base/wearables/`, new `tests/test_sensor_realism.py`.
MUST NOT touch: `simulation/`, `validation/`, `tools/`, other KB dirs.

Evidence: `docs/evidence_package/SENSOR_MODEL_EVIDENCE.md` + WEARABLE_OBSERVABILITY_EVIDENCE.md.
- Replace hardcoded sensor constants (σ=1 ms, 0.5% dropout, PPG coefficients, uniform ±2% HR noise)
  with KB-driven device profiles citing registry claim_ids. Device profiles (research chest strap
  Polar-H10-like: RR bias 0.4–0.7 ms LoA ±1–4 ms, 130 Hz raw; wrist PPG consumer: bias −0.27 bpm
  LoA ±7 bpm; Empatica-E4-like: EDA 4 Hz, PPG 64 Hz; Oura-ring-like temp ±0.05–0.09 °C).
- Implement state-dependent artifact models from the 16-class artifact table: motion-gated PPG/ECG
  artifact (IMU state), contact loss → zero-lines, baseline drift, clipping/saturation, BLE-type
  dropout bursts, day/night usability (PPG good-quality ~30–60% day vs 65–75% night), clock drift
  ~1 s/hour, timing jitter. Ectopy hook (interface for W2 HRV module).
- Enforce the boundary: sensors receive observable physiology (RR series, pulse wave, EDA drive,
  skin temp, respiration, IMU) — never latent BP/SV/CO. Add a static guard test asserting no latent
  variable name reaches the sensor API.
- EDA: tonic SCL 2–20 µS + phasic SCR 0.05–5 µS, latency 1–3 s, rise 1–3 s, half-recovery 2–10 s.
- Tests: artifact rates match configured distributions; derived-metric error vs configured LoA;
  missingness model reproduces day/night usability within tolerance.

---

## Wave-2 preview (contracts wave 1 must honor)

- W2-E Structured HRV (G-P0-05): new `simulation/hrv.py` — IPFM beat generator; inputs: mean-HR
  trajectory + autonomic state (vagal/sympathetic drive, respiration rate); outputs: RR series with
  RSA (~0.15–0.4 Hz), Mayer 0.1 Hz, 1/f fractal structure (DFA-α1 ≈ 1 healthy), ectopy (Bernoulli,
  phase reset). W1-A must expose mean-HR trajectory + autonomic state from engine (document the getter
  in your report). W1-D consumes RR series via sensor boundary.
- W2-F Dataset generation (G-P0-07): cohort sampler + protocol scheduler + batch + seeds + manifest +
  record schema per master prompt §18/§21 (record_id, subject_id, protocol_id, physiological_state,
  events, latent_parameters, observable_parameters, sensor_configuration, derived_metrics, evidence,
  uncertainty, canonical_status, honesty_flags, seed, ocpe_commit, kb_version, registry_version,
  model_version, generation_timestamp). Depends on W1-A (engine API), W1-B (provenance gate), W1-C
  (metric semantics), W1-D (sensor profiles).
