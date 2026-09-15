# OCPE — Current Implementation Map
**Source:** actual source code of `github.com/invisible-illness-project/open-computational-physiology-engine` (branch `main`, cloned and read file-by-file; 69 non-git files). Not based on the README.
**Empirical checks performed:** `tools/validate_kb.py` → **0 errors, 9 warnings** (all whitelisted known issues); `pytest tests/` → **67 passed, 2 xfailed (strict)** in 683 s; all 21 `.review.yaml` sidecars SHA-256-**FRESH** at clone time; smoke simulation of the engine executed (healthy short tilt: supine HR 57.3 bpm, peak 111.0 bpm).

---

## 1. WHAT EXISTS

### 1.1 Architecture (as actually wired)
```
knowledge_base/*.yaml  ──load──▶ models/baroreflex_model.py (12-state ODE, params)
        │ diseases/*.yaml ──▶ simulation/perturbations.py (composable overrides)
        │ populations (NOT consumed by code; priors live in simulation/population.py)
        ▼
simulation/engine.py (beat-by-beat Radau ODE, dt=0.01 s, rtol=1e-6, atol=1e-8)
   ├─ simulation/latent_physiology.py  (latent state container + derived autonomic tones)
   ├─ simulation/behavior.py           (activity triggers → latent/param modulation)
   ├─ simulation/symptoms.py           (7 heuristic symptom scores)
   └─ simulation/time_engine.py        (24-h clock, circadian, sleep pressure, PEM)
        ▼
sensor_models/wearable_sensors.py (Polar H10 RR telemetry; PPG waveform)
        ▼
validation/evaluator.py + validation/validation_suite.py
        ▼
examples/*.py → results/*.npz   (only "dataset" output mechanism)
tools/validate_kb.py (schema/referential validator) + tools/review_tracker.py (sidecar governance)
```

### 1.2 Implemented physiological systems
**Cardiovascular (0-D lumped, Geddes et al. 2022, DOI 10.1098/rsif.2022.0220, Level 4 in-silico source)** — `models/baroreflex_model.py`, 12 integrator states:
`y = [Vau, Vvu, Val, Vvl, Vlv, pcm, Raup, Ralp, Ed, Hc, Vvm, Vsr]`
- Compartment pressure laws: `pau=Vau/Cau`, `pal=Val/Cal`, `pvu=Vvu/Cvu`, logarithmic lower-venous law `pvl=(1/mvl)·ln(VMvl_eff/(VMvl_eff−Vvl))` with `VMvl_eff = VMvl − Vvm + Vsr`; `plv=Elv·Vlv`; double-cosine varying elastance `Elv(t)` with `Ts/Tr` time scales (duplicated verbatim in `engine.py:183-184` and `baroreflex_model.py:278-279`).
- Ideal valves smoothed via `_softplus(·, 0.05 mmHg)` (`Rav=Rmv=0.0001` hardcoded); hydrostatic venous-return gate `_softplus(pvl−pvu−ρgh, 0.1)`; Ohmic flows `qal, qaup, qalp, qvl`; mass-conservation derivatives with non-negativity clamps.
- **Baroreflex control loops** (all first-order ODEs tracking Hill-sigmoid targets in `pcm`): `dpcm=(pc−pcm)/tauP` (tauP=2.5 s); `Raup`, `Ralp` targets with Hill coeff `kR`, bounds `RaupM/Raupm=4.5292/0.3019`, `RalpM/Ralpm=17.88/1.192`, half-saturations `p2Ru=p2Ra=89.97`, time constant `taur=12.5 s`; `Ed` target (parasympathetic limb) with `kE=7`, `EdM/Edm=0.03125/0.00025`, `p2E=76.62`, `tauE=12.5 s`; HR target with `kH=25`, `HM=3.3333 bps (200 bpm)`, `Hm=0.3 bps (18 bpm)`, `p2H=88.66`, `tauH=6.25 s`.
- **Cycle-2 venous/orthostatic extension** (registered in `knowledge_base/equations/definitions.yaml` and `mathematical_models.yaml`): venomotor reflex state `Vvm` (Heldt 2002 structure, DOI 10.1152/japplphysiol.00241.2001; Hill target `dV_veno_max·p2V^kV/(pcm^kV+p2V^kV)`, `tau_veno=12 s`) and venous stress-relaxation creep `Vsr` (van Heusden 2006, DOI 10.1152/ajpheart.01268.2004; `Vsrf=G_sr·max(0,pvl−pvl_sr0)`, `tau_sr=100 s`).
- **Orthostatic stressor**: head-up tilt, angle ramp hardcoded at 14 s (`engine.py:155-163`, `baroreflex_model.py:257-268`), hydrostatic terms `ρ=1.06`, `g=982`, `conv=1333.22`, heights 25 cm (compartment) and 20 cm (carotid, hardcoded). Protocol registry `knowledge_base/interventions/tilt_test.yaml` (200 s supine, 60°, 100 s tilt; DOI-cited to Geddes 2022) is **data-only — not parsed by any code**; the examples hardcode the same numbers.
- **Steady-state initializer** (`initialize_steady_state()`): computes only the 12 initial conditions; controller states placed exactly on Hill targets at supine `pcm0=93.333`; TotalVol perturbations absorbed into venous compartments. Contract "parameters are sacred, init never mutates params" is enforced by `tests/test_steady_state_params.py`.

**Autonomic/latent layer** — `simulation/latent_physiology.py`: 15 latent states with defaults (T_sym=0.3, T_para=0.7, G_baro=25, V_total=4500, E_syst=3.0, R_periph=1.0, C_vasc=1.0, D_circ=0, P_sleep=0.1, H_hydr=0.9, L_stress=0.1, B_infl=0.1, R_metab=1.0, S_horm=0.0, C_rec=1.0). Only **two are dynamically derived** per beat: `sympathetic_tone = p2Ru^kR/(pcm^kR+p2Ru^kR)` and `parasympathetic_tone = pcm^kE/(pcm^kE+p2E^kE)` (`update_derived_states`). Registry: `knowledge_base/physiology/latent_states.yaml` (14 symbols; engine's `autonomic_recovery_capacity` is **not registered** there).

**Symptom layer** — `simulation/symptoms.py`: 7 probabilistic scores ∈[0,1] (fatigue, brain_fog, pain, orthostatic_intolerance, palpitations, sleepiness, dizziness) from hardcoded linear blends, e.g. dizziness `(85−pcm)/35` if pcm<85; palpitations `(HR−80)/100 + 0.2·T_sym` if HR>80 bpm.

**Behavior layer** — `simulation/behavior.py`: 5 activities (rest/exercise/meal/sleep/stress); latent nudges (e.g. exercise: T_sym+0.3, T_para−0.4 per call) and parameter mods (meal: `RalpM,Ralpm ×0.75`, `Cal ×1.15`; hydration→`TotalVol += −500+700·H_hydr`; exercise: `Es ×1.30`); symptom-driven abort feedback (fatigue>0.8 or dizziness>0.7 stops exercise).

**Time layer** — `simulation/time_engine.py`: 24-h clock; circadian cosine peaking 14:00; sleep pressure linear accumulation 0.05/h awake, exponential decay 0.3/h asleep; metabolic/inflammatory recovery in sleep; ME/CFS delayed-PEM trigger (exertion >0.6 recorded 12 h earlier → R_metab−0.5, B_infl+3.0; resolves after 2 h "for simulation speed demo").

### 1.3 Equations & parameters (knowledge_base/equations/)
- `definitions.yaml` v1.0: 23 equation entries (20 Geddes base + 3 Cycle-2: `lower_venous_effective_capacity`, `venomotor_reflex`, `venous_stress_relaxation`), LaTeX + inputs/parameters/outputs. **Gap flagged in its own sidecar: engine `Ts`/`Tr` systole/diastole time-scale equations are absent from the registry.**
- `mathematical_models.yaml` v1.0: single model `pots_baroreflex_response_model`, 39 parameters with nominal values; model-level source = Geddes 2022. Only the 10 Cycle-2 parameters carry per-parameter `doi`/`evidence_tier: C`/`review_status: machine_proposed*` fields (`Cvu 436.36`, `VMvl 700`, `mvl 0.035`, `dV_veno_max 250`, `p2V 87.5`, `kV 8`, `tau_veno 12`, `G_sr 50`, `tau_sr 100`, `pvl_sr0 3`). The 29 Geddes-base parameters have **no per-parameter provenance fields**.
- **Dead conflicting data**: `mathematical_models.yaml` still contains inline `phenotypes:` blocks (`kR→40 hyperadrenergic`, `kH→40 hyperadrenergic`, `RalpM→6.5 neuropathic`, `TotalVol→3500 hypovolemic`) that `load_parameters()` never reads — they contradict `diseases/pots.yaml` v1.5 values (32, 34, 11.5) and are stale Cycle-1 leftovers.

### 1.4 Sensor models (sensor_models/wearable_sensors.py)
- `PolarH10SensorModel(noise_std_ms=1.0, dropout_rate=0.005)`: beat detection by phase integration of Hc; Gaussian RR noise σ=1 ms; 0.5% random dropout with forward-fill; computes RMSSD/SDNN.
- `PPGWearableSensorModel(fs=50 Hz, motion_noise_level=0.15)`: AC = min-max-normalized `pau` ×0.2; DC = `2.0 − 0.8·T_sym`; respiration 0.05·sin(2π·0.25 Hz); measurement noise σ=0.005; motion artifact hardcoded to t∈[200,214] s with sinusoidal fade.
- KB counterparts: `knowledge_base/wearables/polar_h10.yaml` (130 Hz, 1 ms resolution; ICC 0.99 rest / 0.96 high-intensity; LoA −2.3/+2.4 ms rest; DOI 10.3390/s22176536) and `photoplethysmography.yaml` (50 Hz, green/red/IR; HR ICC 0.92, PRV ICC 0.85; **no DOI provenance**). **The sensor model constants are NOT drawn from these KB validation metrics.**

### 1.5 Dataset generation infrastructure
Minimal: `examples/run_simulation.py` (4 cohorts: healthy + 3 POTS; saves `results/<phenotype>_telemetry.npz`) and `examples/run_advanced_simulation.py` (4 composed scenarios with `VirtualSubject` + behaviors; saves `results/<label>_advanced.npz`). No batch cohort sampler, no dataset schema/manifest, no output provenance metadata, no seeding policy beyond `seed=42`.

### 1.6 Validation infrastructure
- `tools/validate_kb.py`: loads all registries; referential integrity (variables, latent states, predicates, mechanistic-link causes/effects, disease-perturbed symbols vs model params); publication frontmatter DOI presence; cohort sample-size warnings; `KNOWN_REFERENTIAL_ISSUES` whitelist (`RMSSD`, `rr_intervals`, `sigmoid_hill`, `gravity_hydrostatic`, `inverse_proportional`, `inverse_nonlinear`) downgrades 6 pre-existing defects to warnings. `--record` appends a `validator` review entry to every validated file's sidecar.
- `validation/evaluator.py` (`PhysiologicalEvaluator`): HR bounds [30,220] bpm, BP bounds [30,230] mmHg, POTS diagnostic check on **peak** HR rise in first 60 s of tilt (≥30 bpm for POTS, <30 for healthy), baroreflex compensation check (initial BP drop >5 mmHg and MAP recovery).
- `validation/validation_suite.py` (`AdvancedValidationSuite`): hemodynamic bounds, circadian variation range >0.1, symptom–carotid-pressure coupling, beta-blocker efficacy (peak HR <145), hydration–volume regulation.
- `docs/validation_strategy.md`: 4-tier strategy (schema → plausibility → clinical cohort → sensor agreement ICC/LoA); documents the historical healthy-control 76.1 bpm failure and the missing muscle pump.

### 1.7 Schemas & knowledge structures
- `SCHEMA.md`: publication-review frontmatter schema (publication/population/variables/mathematical_models/relationships/sensor_validation/conflicts) + 3 central registry schemas. Note: SCHEMA paths still reference legacy locations (`knowledge_base/variables/`, `knowledge_base/models/`) that were migrated per `docs/architecture.md`.
- `TEMPLATE.md`: filled exemplar of the publication review schema.
- Ontology: `concepts.yaml` v3.0 (17 concept classes), `relationships.yaml` v3.2 (12 predicates + 8 semantic edges, adversarially corrected: inverted edges fixed, mis-citations replaced, evidence levels downgraded), `mechanistic_links.yaml` v1.0 (7 links, 4 Geddes Hill links + hydrostatic + RR→HR + HR→DFA_a1).
- Publications: 2 full reviews — `geddes_2022_baroreflex_pots.md` (Level 4 in-silico, confidence 9; full parameter table incl. legacy `Cvu=70.936`, `VMvl=195.075`, `mvl=0.0959` values) and `schaffarczyk_2022_polar_h10_validation.md` (Level 2 validation study, confidence 9; detailed ICC/LoA table incl. DFA_a1 high-intensity LoA −40.9/+58.1%).
- Populations: `cohorts.yaml` v1.0 — only `pots_clinical_cohort` (n=25, 85% female, 12–19 y) and `healthy_control_cohort` (n=25, 18–45 y). The Schaffarczyk cohorts referenced by mechanistic links (`recreational_men_cohort`, `recreational_women_cohort`) are **not registered**.

### 1.8 Tests (tests/, verified: 67 passed + 2 strict-xfail)
- `test_steady_state_params.py`: params never overwritten by init (all phenotypes + VirtualSubject priors); 12-state consistency; canonical-active phenotypes produce distinct tilt responses; **experimental-only phenotypes bit-identical to healthy in canonical mode** (honesty check); pairwise distinctness; healthy not worse than documented 76.1 bpm pre-fix benchmark.
- `test_orthostatic_response.py`: healthy sustained ΔHR <30 (achieved ~19.5 per sidecar), MAP maintained, pooling ≥350 ml at 100 s with analytic steady state ∈[500,1000] ml, venomotor engagement, creep growth; POTS peak criterion preserved; hypovolemic & hyperadrenergic sustained ≥30 bpm; hyperadrenergic MAP pressor surrogate; **2 strict xfails**: neuropathic-with-denervation sustained ≥30 bpm (actual ~21.2 — flat dose-response 18.5→21.7, hydrostatic-gate-limited), hyperadrenergic ΔSBP ≥+10 mmHg (0-D pulse-pressure limitation; actual −4.0).
- `test_experimental_mode.py`: provenance labeling canonical vs EXPERIMENTAL; per-call override; seeded bit-reproducibility.
- `test_steady_state_params.py` is run against **all KB phenotypes dynamically** via `PerturbationManager` enumeration.

### 1.9 Documentation
`docs/architecture.md` (layout + migration + rationale), `docs/ontology.md` (schemas), `docs/latent_physiology.md` (latent→parameter mappings), `docs/validation_strategy.md`, `docs/vision.md`, `docs/adr/0001-sidecar-yaml-review-validation-tracking.md` (governance ADR). Docs partially stale (architecture.md doesn't mention Cycle-2/3 files, `tools/review_tracker.py`, or the experimental mode).

### 1.10 Review-tracker tooling (`tools/review_tracker.py` + sidecars) — exact mechanics
**Pattern (ADR 0001, accepted 2026-09-10):** every data file `X.yaml`/`X.md` gets a co-located sidecar `X.<ext>.review.yaml`. Sidecar schema (`review_manifest_version: 1.0.0`):
```yaml
target_file: {path: <repo-relative>, sha256: <hex of CURRENT content at record time>}
review_history:
  - review_id: rev-<uuid4>
    reviewed_at: <ISO-8601 UTC>
    reviewer: {kind: human|ai_agent|validator,
               identity: {name, [provider, model_name, system_prompt_sha256]}}
    scope: [<comma-split strings>]        # default ["general_validation"]
    verdict: <free string, default REVIEWED>   # observed: PASSED, PASSED_WITH_WARNINGS, REVIEWED; ADR also lists NEEDS_REVISION/REJECTED/APPROVED
    findings: [{path, severity: INFO|WARNING|CRITICAL, message}]   # API only, NOT exposed in CLI
    comments: <string>
```
**CLI commands:**
- `python3 tools/review_tracker.py record <target> --kind {human|ai_agent|validator} --name <id> [--model-provider X] [--system-prompt-hash H] --scope a,b --comments "..." --verdict PASSED` → recomputes SHA-256 of target, appends entry to sidecar (creates it if absent).
- `python3 tools/review_tracker.py history <target>` → prints chronological review list + **freshness verdict** (FRESH if current SHA-256 == recorded, else STALE).
- `python3 tools/review_tracker.py summary [directory]` (default `knowledge_base`) → table of all YAML/MD files: review count, latest reviewer, FRESH/STALE/UNREVIEWED.
- `tools/validate_kb.py --record` auto-records `validator`-kind PASSED entries after a clean validation run.
**Current repo state:** 21 sidecars, all FRESH (verified by recomputing every SHA-256). Reviewer mix: `validate_kb.py` (validator), `adversarial-doi-verifier`, `independent-changeset-reviewer`, `independent-cycle2-reviewer`, `simulation-verification-coder` (all ai_agent, "Moonshot Kimi K3 (subagent)"), one `human` entry ("Dr. Jane Doe", `REVIEWED`, variables.yaml — demonstrative), one Anthropic Claude and one Google Gemini ai_agent entry. **Gaps vs ADR:** no `confidence_score`, `version`, `commit_sha`, `orcid` fields in the tool; findings not settable via CLI; no gatekeeping/enforcement hook that blocks simulation on STALE/unreviewed files; no L3 human APPROVED verdict exists anywhere — every disease file explicitly says "Human L3 review still required."

---

## 2. WHAT IS PARTIALLY IMPLEMENTED

| Component | State |
|---|---|
| **Neuropathic POTS** | Canonical arterial perturbations (RalpM 17.88→11.5, Ralpm 1.192→0.76, tier C) are static baseline overrides; the annotated `application.trigger: head_up_tilt_onset` 10-s transition (Geddes Eq. 2.16) is **not implemented in the engine**. Venomotor denervation (dV_veno_max 250→75, tier D) is experimental-only and even then reaches only 21.2 bpm sustained ΔHR vs the ≥30 target (strict-xfail; flat dose-response documented). |
| **Hyperadrenergic POTS** | Meets ΔHR≥30 (34.2) and MAP pressor surrogate, but the tier-A clinical signature ΔSBP ≥+10 mmHg (Okamoto 2024) is unmet (−4.0 mmHg; 0-D windkessel limitation, strict-xfail). Also see kR/kH/p2H applied-value mismatch in §4. |
| **ME/CFS** | Only HM 3.3333→3.07 (tier B, NEEDS REVIEW) canonical; tauH/taur tier-D; the PEM machinery in `time_engine.py` is **dead code** — `engine.py:120` calls `time_engine.step(T)` without ever passing `current_exertion`, so `exertion_history` stays empty and PEM can never trigger; `is_sleeping` is hardcoded `False` everywhere in the engine. |
| **Behavior layer** | Functional but buggy: `engine.py:139` passes `self.model.params` as the base each beat, so multiplicative behavior mods **compound per heartbeat** (verified: 5 beats of `meal` drives RalpM 17.88→4.24 instead of one-shot 13.41; Cal 0.373→0.749; TotalVol +650 ml). Exercise `Es ×1.30/beat` is unbounded absent the symptom-abort loop. Latent-state nudges are overwritten each beat by `update_derived_states`. |
| **Latent physiology** | 9 of 15 latent states (blood_volume, cardiac_contractility, peripheral_resistance, vascular_compliance, hydration, stress_load, inflammatory_burden, metabolic_reserve, hormonal_state, autonomic_recovery_capacity) are static defaults or behavior-nudged; only T_sym/T_para are dynamically derived; circadian_drive is computed but **never fed back into any model parameter** (despite `docs/validation_strategy.md` §3 plan to modulate kR/kH). |
| **Time engine** | 24-h clock advances in real seconds during minute-scale sims (circadian range over 300 s ≈ 0.005 — the AdvancedValidationSuite `circadian_variation > 0.1` check can only pass trivially via the `len>1` guard or fail silently); sleep is never entered; PEM dead (above). |
| **HRV realism** | Beat-to-beat variability is uniform ±2% multiplicative noise on cycle length (`engine.py:231-232`); no respiratory sinus arrhythmia, no LF/HF structure, no 1/f — RMSSD/SDNN from this are not physiologically structured. |
| **Sensor models** | Implemented but **decoupled from KB validation data** (KB: LoA ±2.3 ms rest, ICC 0.99; code: σ=1 ms Gaussian, 0.5% dropout — hardcoded, unreferenced). PPG motion artifact hardcoded to t∈[200,214] s regardless of actual tilt timing. |
| **Validation evaluators** | `PhysiologicalEvaluator` uses the **peak** ΔHR metric, which `tests/test_orthostatic_response.py` documents as inflated by the steep-Hill limit cycle; the sustained metric convention exists only in tests. `AdvancedValidationSuite.beta_blocker_efficacy` is vacuous in canonical mode (beta_blocker is experimental-only; `run_advanced_simulation.py` composes `"hyperadrenergic_pots * beta_blocker"` in canonical mode, so the beta-blocker silently contributes nothing). |
| **Review tracker** | MVP per its own docstring: record/history/summary work; findings CLI, confidence scores, CI gatekeeping, and enforcement (ADR 0001 "Gatekeeping" paragraph) are unimplemented. |

---

## 3. WHAT IS MISSING

1. **Dataset generation pipeline**: no cohort sampler (cohorts.yaml is not parsed by any simulation code), no batch/parallel runner, no output dataset schema/manifest, no per-record provenance (params, seed, phenotype expression, code hash), no train/validation split concept.
2. **Physiological systems**: no skeletal muscle pump (documented known failure, historically 76.1 bpm healthy ΔHR; Cycle-2 venous changes brought sustained healthy ΔHR to ~19.5 per sidecar/tests), no respiration model (PPG respiration is a cosmetic 0.25 Hz sine), no renal-fluid/hormonal dynamics (S_horm placeholder), no thermoregulation (heat phenotype perturbs resistances statically, no temperature state), no immune dynamics (B_infl is a scalar placeholder), no metabolism model (R_metab is a scalar), no sleep-stage architecture, no activity/accelerometry, no multi-day scheduling.
3. **Model structure**: no tilt-onset application semantics for perturbations (Geddes Eq. 2.16); perturbation schema cannot express time-varying/phase-dependent effects (fludrocortisone chronic phase explicitly blocked, `medication.yaml:81-92`); 0-D arterial windkessel cannot reproduce the ΔSBP pressor criterion.
4. **Calibration/inference**: no parameter estimation (Kalman-filter plan in validation_strategy.md §3 unimplemented); no fitting of sensor outputs to real data.
5. **External validation**: no comparison of synthetic streams against real wearable datasets; Level-4 sensor-agreement validation (ICC/LoA on generated data) not executed anywhere.
6. **Engineering**: no `requirements.txt`/`pyproject.toml`, no CI config, no `__init__.py` files (implicit namespace packages), no package metadata; `results/` gitignored presumably (only `.gitignore` present — not inspected for results).
7. **Registries**: `RMSSD`/`rr_intervals` not in variables.yaml; 4 mechanistic-link `type` values not in the predicate registry; `autonomic_recovery_capacity` latent not registered; `Ts`/`Tr` equations not registered; Schaffarczyk cohorts not in cohorts.yaml.
8. **Second intervention**: only the tilt test exists; no exercise/meal/stand protocols as interventions (behaviors partially cover this but without protocol semantics).

---

## 4. WHAT IS SCIENTIFICALLY UNSUPPORTED

Evidence conventions in-repo: `evidence_tier` A–D (A=established human direction/magnitude, B=human direction/semi-quantitative, C=machine-proposed fit within documented ranges or scaled from an in-silico source, D=machine-proposed hypothesis, UNRESOLVED) and `evidence_level` 1–4 (4=in-silico).

**Machine-calibrated (tier C, `machine_proposed*`)** — all Cycle-2 venous parameters: `Cvu=436.36`, `VMvl=700`, `mvl=0.035`, `dV_veno_max=250`, `p2V=87.5`, `kV=8`, `tau_veno=12`, `G_sr=50`, `tau_sr=100`, `pvl_sr0=3` (structure cited to Heldt 2002/van Heusden 2006/Stewart 2004; magnitudes machine-fitted; DOIs present but tier C). Also hypovolemic `TotalVol=3500` (Geddes value, ~1.5× the Raj 2005 measured mean deficit 689±270 ml — flagged MACHINE-CALIBRATED in-file).

**Machine-proposed hypotheses (tier D, engine-inert `unverified_parameters`)**: autoimmune kR/kH 25→15; hEDS Cal 0.3726→0.65, VMvl 700→987; beta_blocker HM→2.2, kH→12; sleep_deprivation kH 25→20; ME/CFS tauH 6.25→12, taur 12.5→25; neuropathic dV_veno_max 250→75; heat Cal→0.5. **None have parameter-level DOIs (deliberately, per governance fix).**

**Evidence-cited but Level-4 provenance**: the entire Geddes-2022 base parameter set (29 params) and POTS canonical perturbations trace to an in-silico modeling paper; only 5 canonical perturbations cite human data — heat `Raupm`/`Ralpm` ×0.58 (Ganio 2012, tier B, NEEDS REVIEW compartment mapping), ME/CFS `HM` ×0.92 (Davenport 2019, tier B, metric-mismatch caveat), fludrocortisone `TotalVol` +500 ml (Chobanian 1979, tier B direction/time-course; magnitude an assumption), hyperadrenergic `TotalVol=3900` (Raj 2005, Level 2).

**No provenance at all (hardcoded in code, uncited):**
- `simulation/symptoms.py`: every threshold/weight (80 bpm, 85/90 mmHg, 0.5/0.3/0.2 blends, inflammation /10 scaling).
- `simulation/behavior.py`: all modulation magnitudes (T_sym+0.3, meal ×0.75/×1.15, hydration→volume map −500+700·H, Es ×1.30).
- `simulation/population.py`: `HM=(220−age)/60`; female `TotalVol ×0.90`, `Hm ×1.10`; BMI volume scale `1+0.015·(BMI−22)` clipped [0.8,1.3]; fitness factors (athletic Hm ×0.8, Es ×1.25, kR/kH ×1.15; sedentary inverse). `disease_severity` attribute is stored but never used.
- `simulation/latent_physiology.py`: all 15 default latent values.
- `simulation/time_engine.py`: circadian peak 14:00, sleep accumulation 0.05/h, PEM 12-h delay/0.6 threshold/2-h resolution.
- `simulation/engine.py`: `hrv_noise=0.02` uniform; 14-s tilt ramp; 20 cm carotid height.
- `sensor_models/wearable_sensors.py`: σ=1 ms, dropout 0.5%, PPG coefficients (0.2/2.0/0.8/0.05/0.005/0.15).
- **Historical provenance failure (corrected, still governance-relevant):** sidecars record that 4 of 8 original disease-file DOIs were fabricated/wrong-paper and were replaced after adversarial review; all disease files carry "PROPOSED CORRECTION (not yet merged)" headers and "Human L3 review still required".
- **Applied-value mismatches (found in this audit):** hyperadrenergic `kR` (file says normal 23, KB nominal is 25 → multiplicative scaling applies 32/23×25 = **34.78**, not 32), `kH` (27 vs 25 → applies **31.48**, not 34), `p2H` (88.5 vs 88.66 → applies **89.96**, not 89.8). The PerturbationManager's ratio-scaling semantics make `normal_value` divergence from the KB nominal silently change applied values.

---

## 5. WHAT IS ARCHITECTURALLY SOUND

1. **KB/code separation**: canonical parameters in YAML, executable model reads them; steady-state init treats params as sacred (test-enforced).
2. **Composable perturbation framework** with multiplicative compounding (`perturbed/normal × current`), expression syntax (`"neuropathic_pots * environmental_heat"`), and per-parameter provenance (`last_application` canonical vs experimental).
3. **Honesty-by-default engine**: tier-D values are engine-inert unless `include_experimental=True`; tests assert experimental-only phenotypes are bit-identical to healthy in canonical mode. This is exactly the evidence-gating behavior the mission requires.
4. **Sidecar governance**: SHA-256 freshness binding works (all 21 sidecars verified FRESH); validator auto-records; ADR documents the 3-tier L1/L2/L3 review model.
5. **Test harness**: dynamic phenotype enumeration, seeded determinism, strict-xfail for known unmet clinical criteria with precise quantitative reasons (21.2 bpm, flat dose-response; ΔSBP −4.0).
6. **Adversarial-review culture encoded in files**: compliance guards (`do_not_perturb: [mvl, VMvl]` with Stewart/Freeman citations), `unresolved_gaps` blocks, review_status strings with quantitative simulation-check results.
7. **Beat-by-beat Radau integration with smoothed discontinuities** (softplus valves/gates) is numerically defensible; mass conservation clamps present.

---

## 6. WHAT MUST CHANGE BEFORE DATASET GENERATION

Priority-ordered:
1. **Fix behavior compounding** (`engine.py:139`): compute behavior mods from the pristine parameter set each beat, not from `self.model.params`. Currently any non-rest scenario silently corrupts parameters.
2. **Resolve neuropathic POTS model structure** (bounded stress-relaxation creep per van Heusden 2006 and/or tilt-onset gain application per Geddes Eq. 2.16) or formally scope it out — it cannot meet its own acceptance criterion today (strict-xfail, 21.2 bpm).
3. **Decide the experimental-mode policy for dataset output**: 7 of 10 phenotypes are partially or wholly tier-D; a dataset generated canonically today contains physiological signal for only 4 perturbations (3 POTS + heat + fludrocortisone + ME/CFS-HM — i.e. 6 canonical-active phenotype IDs) and healthy-identical traces for the rest.
4. **Build the dataset layer**: cohort sampling from priors (currently `VirtualSubject` is a single deterministic subject; `cohorts.yaml` unconsumed), batch runner, output schema with provenance (params applied, mode, seed, code/KB SHA-256), and per-record evidence-tier labeling.
5. **Wire KB sensor-validation metrics into the sensor models** (LoA/bias/ICC-driven noise and dropout models; Polar H10 rest vs high-intensity regimes) and remove the hardcoded PPG motion window.
6. **Fix applied-value mismatches** in `diseases/pots.yaml` (kR/kH/p2H `normal_value` vs KB nominals) and delete the dead inline `phenotypes:` blocks in `mathematical_models.yaml`.
7. **Make HRV physiologically structured** (RSA + LF/HF + ectopy/artifact model) before claiming RMSSD/DFA_a1 outputs; validate generated HRV against the Schaffarczyk LoA table.
8. **Activate or remove the time-engine paths**: pass exertion into `TimeEngine.step`, implement sleep scheduling, and couple `D_circ` to baroreflex gains per validation_strategy.md §3 — otherwise circadian/sleep/PEM outputs in a dataset are fictional.
9. **Close registry gaps** (RMSSD, rr_intervals, predicate types, autonomic_recovery_capacity, Ts/Tr equations, Schaffarczyk cohorts) so `validate_kb.py` runs whitelist-free.
10. **Add packaging + CI** (requirements, pytest run, `validate_kb.py` gate, review-freshness gate per ADR 0001).
11. **Human L3 review**: no knowledge-base file carries it; every disease file is explicitly "PROPOSED CORRECTION (not yet merged)" pending human sign-off.

---

## 7. WHAT CAN REMAIN UNCHANGED

- The 12-state ODE core and Hill-controller structure (`models/baroreflex_model.py`) including the Cycle-2 venous extension structure (structure is evidence-cited; only magnitudes are tier C).
- `simulation/perturbations.py` composition semantics and provenance plumbing (modulo the `normal_value`-vs-nominal consistency issue in data, not code).
- `tools/review_tracker.py` CLI and sidecar schema (works as specified; extensions — findings CLI, confidence, gating — are additive).
- `tools/validate_kb.py` architecture (whitelist is data-debt, not design-debt).
- Test files' structure and metric conventions.
- KB schemas (`SCHEMA.md`, `TEMPLATE.md`, ontology schemas) — modulo the time-varying-perturbation extension flagged in `medication.yaml` and the `application.trigger` semantics that need engine support.
- Publication review files (both are high quality, schema-conformant).
- `examples/` as smoke demos.
