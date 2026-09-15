# OCPE — RESEARCH & IMPLEMENTATION GAP ANALYSIS (Pass 2 Integration)

**Scope:** every gap identified across `CURRENT_IMPLEMENTATION_MAP.md` (engine/KB audit), `CURRENT_PHENOTYPE_SCOPE.md`, the six dossier gap lists, `EVIDENCE_AUDIT_NOTES.md` (§d coverage gaps + tier audit), `CONTRADICTION_AUDIT.md`, and `INDEPENDENT_REVIEW_PASS2.md` (§4 required revisions).
**Severity scale:** **P0** = blocks scientifically defensible dataset generation · **P1** = materially reduces dataset quality/credibility · **P2** = useful, not required for the first dataset · **P3** = future/hygiene.
**Complexity:** S < 1 dev-week · M = 1–4 dev-weeks · L > 4 dev-weeks / research-required.
**Counts:** **10 P0 · 17 P1 · 22 P2 · 6 P3** (55 total). Closed-at-evidence-layer items are marked ⇢; they still need engine/generation enforcement.

---

## P0 — BLOCKS SCIENTIFICALLY DEFENSIBLE DATASET GENERATION

### G-P0-01 — Behavior-parameter compounding bug (`engine.py:139`)
- **gap:** `engine.py` passes `self.model.params` as the base to behavior modulation each beat, so multiplicative behavior mods compound per heartbeat (verified: 5 beats of `meal` drives RalpM 17.88→4.24 instead of one-shot 13.41; Cal 0.373→0.749; TotalVol +650 mL; exercise `Es ×1.30`/beat unbounded absent symptom-abort).
- **severity:** P0 — any non-rest scenario silently corrupts physiology; all meal/exercise/stress outputs are currently wrong by an unbounded factor.
- **scientific_reason:** postprandial/exercise/stress kernels are evidence-anchored (+6±3 bpm etc., consolidated doc D17); compounding destroys every one of them.
- **evidence_needed:** none (pure defect); regression targets from HEALTHY §5/§4.
- **implementation:** compute behavior deltas from the pristine (canonical+perturbation) parameter set each beat; make latent nudges additive with explicit decay rather than overwritten per beat.
- **tests:** meal 5-beat regression (RalpM==13.41 stable); exercise Es bounded; property test: behavior mods idempotent across N beats.
- **validation:** postprandial ΔHR peak/timing vs 25-study review; exercise HR onset τ.
- **dependencies:** none. **complexity:** S.

### G-P0-02 — PEM machinery is dead code, and its constants contradict the evidence by ~2 orders of magnitude
- **gap:** `engine.py:120` calls `time_engine.step(T)` without `current_exertion` → `exertion_history` empty → PEM can never trigger; `is_sleeping` hardcoded `False` → sleep recovery unreachable. Constants: 12-h fixed delay, exertion>0.6 trigger, R_metab−0.5/B_infl+3.0, **2-h resolution "for simulation speed demo"** vs evidence: onset Gamma(mode 12–24 h, 0–48 h), peak 24–48 h, recovery **mean 12.7 d, range 1–64 d** (Moore 2023, D18 mean-not-median); symptom/physiology kernel decoupling (D2).
- **severity:** P0 — ME/CFS is a flagship phenotype; its defining feature currently cannot fire, and when wired with current constants would be scientifically indefensible.
- **scientific_reason:** PEM is a delayed multi-day state transition (symptom kernel E2/E4; physiological slowed-recovery kernel τ 3–6 h → 9–13 h; delayed physiological second wave E0-off); a 2-h scalar bump misrepresents the evidence base.
- **evidence_needed:** none for wiring; exertion→PEM dose-response remains a *labeled modeling hypothesis* (VT1-proxy trigger, EVD-MECFS dossier §D — never present as established law).
- **implementation:** pass exertion through engine hook; implement PEM as latent state with symptom-kernel/physiology-kernel decoupling; right-skewed recovery distribution; detectability mixture (~50–65% of episodes show physiological signatures); rolling-PEM baseline creep.
- **tests:** trigger fires given exertion; kernel shape moments (onset/peak/recovery quantiles) vs Chu 2018/Moore 2023; E0-branch toggle produces no delayed physiology.
- **validation:** EXPLICIT EXCLUSION — no multi-day wearable PEM dataset exists (G-P1-06); validate only kernel statistics vs literature, label all PEM channels as extrapolation.
- **dependencies:** G-P0-06 (multi-day time), G-P0-07 (dataset layer for day-scale outputs). **complexity:** M.

### G-P0-03 — Neuropathic POTS cannot meet its own acceptance criterion
- **gap:** sustained ΔHR 21.2 bpm vs ≥30 bpm target (strict-xfail `tests/test_orthostatic_response.py:212`); flat dose-response 18.5→21.7 over denervation factor 0–0.5 (hydrostatic-gate-limited; stress-relaxation creep re-expands capacity); Geddes Eq. 2.16 tilt-onset application semantics (`application.trigger: head_up_tilt_onset`, 10-s transition) not implemented — perturbations applied as static baseline overrides.
- **severity:** P0 — a flagship POTS subtype fails its clinical criterion; shipping it silently would be a scientific defect.
- **scientific_reason:** human evidence (Jacob 2000 91–99% blunted leg NE spillover, tier A direction) says denervation is real; model structure cannot express it — a model-adequacy failure, not an evidence failure.
- **evidence_needed:** quantitative human venomotor-denervation magnitude (missing; keep tier-D uncertainty); bounded stress-relaxation creep per van Heusden 2006.
- **implementation:** bounded creep state; tilt-onset trigger semantics in engine; re-run dose-response; if still <30, formally scope neuropathic to "experimental-only with published-criterion xfail" rather than shipping a failing canonical phenotype.
- **tests:** existing strict-xfail becomes the acceptance gate; add tilt-onset timing test (10-s transition).
- **validation:** ΔHR time-course vs Orjatsalo minute-resolved curves.
- **dependencies:** none. **complexity:** M.

### G-P0-04 — Engine-vs-KB parameter mismatches (kR/kH/p2H) + dead conflicting data + uncited population priors
- **gap:** PerturbationManager ratio-scaling with `normal_value`≠KB nominal silently changes applied values: hyperadrenergic kR applies 34.78 (stated 32), kH 31.48 (stated 34), p2H 89.96 (stated 89.8). Dead inline `phenotypes:` blocks in `mathematical_models.yaml` contradict `diseases/pots.yaml` (kR→40 vs 32 etc.). `simulation/population.py` HRmax prior `HM=(220−age)/60` (Fox) contradicts the binding Tanaka anchor (208−0.7·age, ε~N(0,11), E5); sex/BMI/fitness priors uncited.
- **severity:** P0 — the dataset's actual generative parameters currently differ from every documented value; silent divergence is exactly the class of bug the provenance system exists to prevent.
- **scientific_reason:** reproducibility requires applied==documented; HRmax anchor is E5 and affects all exercise physiology.
- **evidence_needed:** none for the fixes; cite population priors to HEALTHY dossier anchors (female +4.4 bpm, volume scaling) or flag tier-C.
- **implementation:** assert `normal_value==KB nominal` at load; delete dead blocks; replace Fox with Tanaka+residual; annotate all population.py priors with tier/citation.
- **tests:** applied-value equality test for every phenotype; load-time assertion test; HRmax distribution vs Tanaka.
- **validation:** `validate_kb.py` extended with consistency rule; regenerate POTS acceptance numbers post-fix.
- **dependencies:** none. **complexity:** S.

### G-P0-05 — No HRV structure (no RSA, no LF/HF, no 1/f) 
- **gap:** beat-to-beat variability = uniform ±2% multiplicative noise (`engine.py:231-232`); PPG "respiration" is a cosmetic 0.25-Hz sine; no respiration model exists at all. RMSSD/SDNN/DFA_a1 outputs are physiologically unstructured.
- **severity:** P0 — HRV is the primary observable carrier for nearly every condition axis (tonic vagal gain SHARED latent #1); a dataset without structured HRV cannot support the evidence claims.
- **scientific_reason:** RSA is mechanically generated from respiration (D15); 1/f DFA structure E4 (EVD-TEMP-001); day-to-day CVs quantified (EVD-POP-004); RR-scaling law required to avoid laundered vagal confounds.
- **evidence_needed:** none blocking — anchors exist (HEALTHY §1.2, AUTONOMIC, TEMPORAL, POPULATION). Adult RSA amplitude priors partially provisional.
- **implementation:** respiration state (rate/tidal volume, posture/sleep-stage conditioned) → RSA phase coupling; LF (Mayer-wave) oscillator with loop-gain/phase (needed for POTS 0.1-Hz signature anyway); 1/f background; ectopy/artifact model; within-person day-to-day CV injection.
- **tests:** generated 5-min RMSSD lognormal median ~35–42 ms young; 24-h SDNN ~150±38; day-to-day lnRMSSD CV 10–15%; DFA_a1 structure present; RSA age-graded E/I ratios.
- **validation:** Schaffarczyk LoA table after sensor layer; Nunan pooled table; Aeschbacher 24-h values.
- **dependencies:** none. **complexity:** M–L.

### G-P0-06 — No circadian/sleep coupling; time engine outputs fictional
- **gap:** 24-h clock advances in real seconds during minute-scale sims (circadian range over 300 s ≈ 0.005 → the `circadian_variation>0.1` check passes trivially or fails silently); `D_circ` computed but never fed back to any parameter; sleep never entered (`is_sleeping=False` everywhere); no sleep-stage architecture; no multi-day scheduling.
- **severity:** P0 — circadian HR amplitude (~13.5 bpm), nocturnal dip reference-frames, sleep-stage autonomics, PEM/crash day-scale dynamics, menstrual modulation, flare prodromes (2–7 weeks) all require functioning time/sleep layers; without them the dataset's dominant variance structure is absent.
- **scientific_reason:** disease signatures are largely *modulations of diurnal/sleep structure* (nocturnal RHR semantics, non-dipping axes, sleep fragmentation SHARED latent); simulated outputs without them are unvalidatable.
- **evidence_needed:** none blocking (HEALTHY §2/§6 quantified).
- **implementation:** virtual-time scheduling (compressed time with event calendar); couple D_circ → kR/kH/HM per `validation_strategy.md` §3; sleep-state machine with stage-conditioned autonomics (N3 vagal max, REM bursts); day-scale loop for multi-day runs.
- **tests:** circadian amplitude/acrophase recovery; sleep-stage HR/HF ordering vs Cabiddu/Huang; nocturnal dip reference-frame correctness.
- **validation:** ABPM circadian table; Huang 2018 stage means; Quer within-person SD.
- **dependencies:** G-P0-05 for HRV coupling. **complexity:** L.

### G-P0-07 — No dataset-generation infrastructure
- **gap:** no cohort sampler (`cohorts.yaml` unparsed; `VirtualSubject` single deterministic subject), no batch/parallel runner, no output dataset schema/manifest, no per-record provenance (params, seed, mode, code/KB SHA-256, evidence-tier labels), no train/validation split concept, seeding policy = `seed=42`.
- **severity:** P0 — there is literally no mechanism to produce a defensible dataset; `examples/*.py → results/*.npz` is the only output path.
- **scientific_reason:** evidence-tier labeling and provenance gating (given the fabricated-DOI history, G-P1-05) must be structural, not documentation.
- **evidence_needed:** none.
- **implementation:** cohort sampler from dossier joint distributions (demographics, severity latents, SHARED latents per consolidated §10.1, comorbidity draws with ascertainment down-weighting 0.3–0.5×, background-rate honesty for controls); batch runner with seed policy; manifest schema (params applied, mode canonical/experimental, seeds, code/KB SHA, claim_ids backing each channel).
- **tests:** sampler moments vs dossier distributions; determinism under fixed seed; manifest completeness check.
- **validation:** distribution-level vs dossier anchor tables (per-slice target statistics, G-P1-10).
- **dependencies:** G-P0-04, G-P0-10. **complexity:** M–L.

### G-P0-08 — Experimental-mode policy undecided: 7 of 10 phenotypes are (partly) tier-D
- **gap:** canonical-mode dataset today contains real signal for only ~6 canonical-active phenotype IDs; hEDS, autoimmune, sleep-deprivation, beta-blocker are bit-identical to healthy; neuropathic partially tier-D; all tier-D values are machine-proposed.
- **severity:** P0 — a dataset generated without an explicit policy silently ships healthy-identical "disease" traces or unmarked machine-proposed physiology.
- **scientific_reason:** honesty-by-default engine is architecturally sound (keep); the *policy* of what enters dataset v1 must be decided and labeled per record.
- **evidence_needed:** per-phenotype tier inventory exists (CURRENT_PHENOTYPE_SCOPE summary table).
- **implementation:** dataset-mode flag; per-record `evidence_mode` field; v1 scope = canonical-active phenotypes + explicitly promoted tier-D items with labels; never mix silently.
- **tests:** bit-identity honesty test already exists — extend to dataset layer assertions.
- **validation:** provenance audit on generated manifest.
- **dependencies:** G-P0-07. **complexity:** S (decision) + S (wiring).

### G-P0-09 — Healthy orthostatic reference not frozen/protocol-conditioned; evaluator metric inconsistent
- **gap:** engine healthy sustained ΔHR is a single point (~19.5 bpm); no protocol-conditioned distribution (stand vs tilt vs NASA-lean; initial transient vs sustained; age strata); `PhysiologicalEvaluator` uses **peak** ΔHR in first 60 s (inflated by steep-Hill limit cycle) while tests use sustained — two different metrics gate "POTS vs healthy."
- **severity:** P0 — the healthy false-positive rate at the 30-bpm boundary (33–60% aggressive protocols, <5% casual stands; D14) is the single most consequential calibration choice; every downstream POTS claim depends on it.
- **scientific_reason:** POTS criterion is protocol-dependent; a single-point healthy reference with a peak metric manufactures false positives/negatives.
- **evidence_needed:** ⇢ evidence layer complete (D14; EVD-HLTH-004; Plash/Orjatsalo/NASA-lean distributions).
- **implementation:** protocol-conditioned healthy reference curves in engine + KB; sustained-metric convention in evaluator; muscle-pump absence documented as structural limitation of active-stand simulation (tilt-only v1, or pump module).
- **tests:** healthy >30-bpm fraction per protocol vs Plash/NASA rates; evaluator/test metric unification.
- **validation:** fraction-exceeding-30 calibration (stand ~2–5%, tilt-10min ~40–60%).
- **dependencies:** G-P0-05 (Mayer-wave), G-P1-08 (muscle pump decision). **complexity:** M.

### G-P0-10 — Evidence-scale harmonization not enforced in generation (⇢ evidence layer done)
- **gap:** three incompatible E-scales existed across dossiers; registry normalization (`EVIDENCE_REGISTRY.yaml`) resolves the evidence side, but repo tiers A–D/levels 1–4 are unmapped onto E0–E5, and generated outputs carry no evidence labels.
- **severity:** P0 (per INDEPENDENT_REVIEW §4.1) — without enforced mapping, dataset consumers cannot distinguish established human evidence from machine-proposed fits.
- **scientific_reason:** single binding convention required for provenance-gated generation.
- **evidence_needed:** none; mapping table (tier A→E4/E5 direction, B→E2/E3, C→E1 + machine-fit flag, D→E0/E1).
- **implementation:** tier→E-scale mapping in KB schema; per-parameter evidence labels in manifest (G-P0-07); validator rule.
- **tests:** schema validation of mapping completeness.
- **validation:** provenance audit.
- **dependencies:** none. **complexity:** S.

---

## P1 — MATERIALLY REDUCES QUALITY / CREDIBILITY

| ID | Gap | Scientific reason | Evidence needed | Implementation | Tests / validation | Deps | Cx |
|---|---|---|---|---|---|---|---|
| G-P1-01 | **Hyperadrenergic ΔSBP criterion failure** (−4.0 vs ≥+10 mmHg; 0-D windkessel cannot produce upright pressor; strict-xfail) | Tier-A clinical signature (Okamoto 2024) unmet; MAP surrogate (+5.1) is not ΔSBP | Pulse-pressure-generating structure (distributed arterial or PP surrogate model) | Add pulse-pressure compartment or emit ΔSBP from validated surrogate with limitation flag | Strict-xfail acceptance; ΔSBP ≥+10 in hyperadrenergic, ≤0 in others | — | M |
| G-P1-02 | **Sensor constants decoupled from KB validation data** (code σ=1 ms, 0.5% dropout; KB LoA ±2.3 ms/ICC 0.99 rest vs 0.96 high-intensity; PPG KB has no DOI; motion artifact hardcoded t∈[200,214] s) | Observation layer must reproduce device error structure incl. intensity-dependent degradation and usable-fraction stats | ⇢ SENSOR_MODEL/EVD-SENS anchors exist; PPG validation DOI missing (P2 retrieval) | Drive noise/dropout/artifact from KB metrics; motion windows from behavior layer; day/night and cadence-lock terms | ICC/LoA replay vs Schaffarczyk table; usable-fraction stats | G-P0-05 | M |
| G-P1-03 | **Hypovolemic TotalVol=3500 mL ≈ 1.5× the measured mean deficit** (Raj 689±270 mL; population-mean alternative ~3800 documented in-file) | Machine-calibrated extreme presented as canonical; volume-normal minority erased | ⇢ Triangulated anchor: deficit −12±5% (Raj+Fu+Kulapatana), mixture model (CONTRADICTION §E.3) | Mixture: hypovolemic branch −14±10% / volume-normal; Geddes 3500 demoted to scenario sample | Cohort deficit distribution vs triangulated anchor | G-P0-07 | S |
| G-P1-04 | **Geddes single-source backbone** (29 params Level-4 + 10 tier-C venous) without competing Fu-2010 branch | Single in-silico source, partially engine-falsified; Fu branch (intact baroreflex, small LV+BV) is an evidence-licensed alternative | ⇢ D5 complete in evidence layer | Scenario-sample Geddes set (tier-D discipline on magnitudes); implement Fu branch as alternative generative mechanism (LV-mass/BV deficit, baroreflex intact) | Branch-level tilt ΔHR distributions both reach ≥30 via different routes; parameter-sensitivity report | G-P0-03 | M–L |
| G-P1-05 | **No human L3 review on any sidecar; fabricated-DOI history; no provenance gating** | 4/8 original disease DOIs fabricated/wrong-paper; every disease file "PROPOSED CORRECTION (not yet merged)"; no enforcement hook blocks simulation on STALE/unreviewed | Human review process; registry DOI re-verification pass (Pass-3 item) | Provenance gate: dataset builder refuses KB files without FRESH sidecar + tier labels; ADR-0001 gatekeeping implemented | Gate blocks synthetic run on tampered file (hash-mismatch test) | G-P0-07 | M |
| G-P1-06 | **PEM dynamics are unvalidatable** (no multi-day wearable PEM dataset exists; LC n=127 proxy only) | The flagship ME/CFS channel rests on extrapolation; must be an explicit validation exclusion, not a silent claim | Future: induced-PEM wearable study (external) | Label all PEM channels `evidence_mode: extrapolation`; exclude from validation harness; document LC-proxy provenance | Manifest labeling test; validation-exclusion registry | G-P0-02 | S |
| G-P1-07 | **Missing external validation datasets** (no comparison of synthetic streams to real wearable data; no POTS/ME-CFS/EDS open wearable corpora identified; Level-4 sensor-agreement validation never executed) | External realism is currently asserted, never measured | Dataset search/curation: DETECT/All-of-Us-style RHR corpora, POTS tilt databases, UK citizen-science LC cohort; licensing | `validation/external/` comparators; distribution-distance metrics | Pre-registered tolerances per slice | G-P1-10 | L |
| G-P1-08 | **No skeletal muscle pump; pooling calibration fragile** (historical 76.1 bpm healthy ΔHR failure; Cycle-2 fixed to ~19.5 but pooling 421 mL vs 300–800 mL range; active-stand ≠ tilt) | Active-stand transient is muscle-pump-driven; without it, stand protocols are structurally wrong | Heldt-style pump parameterization (E1/E3 anchors exist) | Implement pump or scope v1 to tilt-only with documentation | Initial-transient kernel vs §3.1 anchors (nadir 8–12 s, recovery 20–30 s) | G-P0-09 | M |
| G-P1-09 | **Missing physiological systems required by dossiers**: respiration (blocks G-P0-05), thermoregulation (blocks fever age-graded slope, heat phenotype which currently perturbs resistances statically, MSA anhidrosis), sleep-stage architecture (blocks RBD/OSA/sleep-fragmentation latent), accelerometry (blocks steps/tremor/seizure/slow-gait undercount), renal/hormonal (blocks fludrocortisone chronic phase), immune dynamics (blocks inflammation core) | Overlap-matrix SHARED latents (#5, #6, fever module, OSA generator) cannot exist without these | ⇢ All anchors in HEALTHY/dossiers | Modular state machines per consolidated §10.1; minimum viable: respiration + sleep stages + activity counts for v1 | Per-module anchor tests (RR distribution KORA; stage HR ordering; step distributions) | G-P0-06 | L |
| G-P1-10 | **No validation harness spec**: per-slice target statistics, distance metrics with pre-registered tolerances, unified negative-control battery (SpO2-null, TNF-null, panic/seizure confusion, artifact-mimic), AUC caps (ME/CFS single-feature ≤0.7–0.8; LC 0.75–0.85), base-rate-coupled PPV | Prevents stereotyped/over-separated synthetic data (the anti-laundering rule, consolidated §10.1) | ⇢ Caps and controls enumerated in consolidated §11.6 | `validation/harness.py` with registered targets/exclusions | Harness self-test on healthy-only data (must fail disease caps) | G-P0-07 | M |
| G-P1-11 | **RHR definition reconciliation + within-person deviation semantics** (clinic vs nocturnal vs real-world ~4–8 bpm offsets; HEALTHY E0 within-person SD superseded by Quer SD≈3.0/CV 4.6%) | Disease RHR claims (POTS +10–20 lab vs +3 real-world; ME/CFS +4.14 below noise floor) are definition-sensitive | ⇢ EVD-POP-004; D13/D20 | Freeze nocturnal-RHR channel semantics; all disease RHR effects as within-person deltas | Definitional-offset unit tests; Welltory-constraint check (rest-only classifier fails) | G-P0-06 | S |
| G-P1-12 | **Adult fever→HR slope is heuristic** (large regression pediatric; adult ~7–10 bpm/°C from ED data) | Fever module is SHARED core; wrong slope propagates to infection/flare/LC-acute layers | Adult-specific regression (targeted search; PMID 31345594 full extraction) | Age-graded slope 7–13 bpm/°C with wide inter-individual spread (D4) | Slope recovery test in febrile synthetic personas | G-P1-09 thermoreg | S |
| G-P1-13 | **Severe ME/CFS physiology is extrapolation** (bedbound excluded from all lab studies) | Severe tier = ~25% of patients; parameters are downward extrapolations anchored only on steps/CBF-seated | External: severe-patient home-monitoring data | Severity latent with extrapolation flag; anchor on step tertiles + van Campen sitting CBF | Step-tertile distribution test; extrapolation labels | G-P0-07 | S |
| G-P1-14 | **Statistic/precision defects need engine-side enforcement** (PEM mean-not-median ⇢ evidence fixed; single-source tags on Moore/van Campen/RA Forecast-derived parameters; RA-flare F1 must never be emitted) | Fabricated-precision history; classifier performances as within-subject associations only | ⇢ D6/D18/D22 | Parameter-level `single_source` flags; ban on emitting F1/AUC as validated (CONTRADICTION §E.12) | Manifest lint for banned fields | G-P0-07 | S |
| G-P1-15 | **Hardcoded uncited constants across simulation layer** (symptoms thresholds; behavior magnitudes; 15 latent defaults; time-engine constants; sensor coefficients; hrv_noise=0.02; 14-s ramp; 20 cm carotid height) | Provenance system exists but code constants bypass it entirely | Map each constant to dossier anchor or tier-D label | Retrofit: constants → KB with citations/tiers; engine reads KB only | `validate_kb.py` constant-coverage rule | G-P0-10 | M |
| G-P1-16 | **No tilt-onset/phase-dependent perturbation semantics beyond neuropathic** (Geddes Eq. 2.16; heat Cal tier-D direction disputed; Ganio whole-body→compartment mapping NEEDS REVIEW) | Several canonical perturbations rest on unresolved compartment mappings | Compartmental heat-vasodilation distribution evidence | `application.trigger` semantics general; mapping caveats as scenario flags | Heat tilt test with both mapping branches | G-P0-03 | M |
| G-P1-17 | **Overlap-matrix enforcement** (⇢ matrix specified in DISEASE_PHYSIOLOGY_EVIDENCE.md §10; not yet in generation) | Without enforcement, nonspecific axes get encoded as disease signatures (the explicit purpose of §16) | ⇢ Complete | SHARED latents as core modules; condition layers as priors only; per-record latent draw provenance | Anti-laundering test: between-condition separation < within-condition variance on shared axes | G-P0-07, G-P1-09 | M |

---

## P2 — USEFUL, NOT REQUIRED FOR FIRST DATASET

| ID | Gap | Key fields (reason / evidence / implementation) | Cx |
|---|---|---|---|
| G-P2-01 | **Schema cannot express chronic-phase medication** (fludrocortisone chronic TPR phase contradicted by own citation; `medication.yaml:81-92` blocked) | Time-varying/phase-dependent perturbation schema extension; chronic-phase parameterization requires human review; magnitude ±50% sampling (§E.11) | M |
| G-P2-02 | **Symptom layer evidence thin + zero provenance** (7 heuristic scores, all thresholds uncited) | Symptom models should sample from dossier symptom statistics (RECOVER clusters, PEM prevalence by wording); currently pure invention; keep latent-ish and labeled | M |
| G-P2-03 | **Latent factor structure is E0** (POPULATION §G theory-driven; loadings ±50%; Gaussian-copula sensitivity at r=0) | No factor-analytic study exists; implement with sampled loadings + sensitivity analysis; document E0 | M |
| G-P2-04 | Orthostatic ΔHR **test-retest reliability unmeasured** (no study; provisional CV 15–25%) | Needed for within-person repeatability realism; provisional parameter with flag | S |
| G-P2-05 | **Population correlation cells unevidenced** (RMSSD↔BP, EDA↔RHR/RMSSD, steps↔RMSSD large-n, core-temp↔RHR) | Copula cells must be flagged E0; sensitivity at independence | S |
| G-P2-06 | **Adult SpO2 population distribution** (pediatric anchor only) | Targeted retrieval; provisional truncated Normal(97.5,1.0) stands | S |
| G-P2-07 | **No large ambulatory panic dataset** (EDA/BP/HR magnitudes genuinely unknown; partially null) | Pass-2 targeted search (Meuret/Wilhelm/Roth); panic layer stays modest-magnitude with wide uncertainty | S |
| G-P2-08 | **Steroid wearable effect sizes all indirect** (RHR/sleep; SLE magnitudes unattributable, 100% steroid confound) | Gain modifiers with flagged uncertainty; no direct numbers | S |
| G-P2-09 | **Disease-specific sleep-staging accuracy unstudied** (healthy-only κ) | Stage-accuracy degradation for disease personas is assumed; flag | S |
| G-P2-10 | Registry referential debt (RMSSD, rr_intervals, 4 predicate types, autonomic_recovery_capacity, Ts/Tr equations, Schaffarczyk cohorts — whitelisted in validator) | Close so `validate_kb.py` runs whitelist-free | S |
| G-P2-11 | No parameter-estimation/calibration path (Kalman plan in validation_strategy.md §3 unimplemented) | Needed for fitting to real data later; not needed for v1 forward generation | L |
| G-P2-12 | TEMPORAL orthostatic band split (initial transient vs sustained as separate parameters) | Evidence-side refinement; engine partially covered by G-P0-09 | S |
| G-P2-13 | Discrete-preset vs continuous-axis policy; pacing/behavioral adaptation not first-class | Phenotype presets must *sample from* dossier joint distributions; pacing as state variable (ME/CFS boom-bust autocorrelation) | M |
| G-P2-14 | Perturbation stacking rule unstated (additive-on-log-scale for HRV recommended; validate per NEURO ST-3) | Must be decided before multi-condition personas | S |
| G-P2-15 | Secondary-verified classics unverified at primary level (Webber & Macdonald 1994; Keys starvation; Westerterp TEF; seizure-detection DOIs Poh 2012/Onorati/Regalia; Fu 2010 exact SV/CO %; Jacob 2000 spillover table; Breier GIP; Stewart CBFv subgroups; Bagai PSG) | Pass-3 targeted extraction before locking numbers; registry carries verbatim-copy risk | M |
| G-P2-16 | Intended-use decision for dataset v1 (screening-algorithm training vs education vs pipeline testing) — AUC-cap guidance differs per use | Governance decision, document before release | S |
| G-P2-17 | Beta-blocker scenario vacuous in canonical mode (`run_advanced_simulation.py` composes experimental-only beta_blocker in canonical mode; efficacy check vacuous) | Fix example mode or promote with tier-D label | S |
| G-P2-18 | hEDS venous compliance/pooling never measured (EVD-EDS-003 E0–E1); mechanism adjudication deconditioning-vs-intrinsic E0 (EVD-EDS-008) | Keep as optional flagged perturbation; components separable; "mechanism unknown" annotation | S |
| G-P2-19 | No validated PEM detector from wearables; PEM remains latent-only (WEARABLE dossier) | Consistent with G-P1-06; detector research is external | S |
| G-P2-20 | Dossier residual retrieval gaps: HEALTHY (exercise-onset τ; young postprandial BP; EDA absolute norms; fitness→HRR1 protocol map; adult SpO2); METABOLIC (healthy dawn magnitude; RER-by-IR distributions; postprandial EDA E0/E1; fasting orthostatic n≤25; TEF DOI unverified; 72-h fast HR secondary); NEURO (migraine trigger-forecasting; PD resting-HR direction — do not perturb); AUTOIMMUNE (Williams exact pooled r; flare skin-temperature; LF/HF inconsistency → excluded from core outputs) | Each is a bounded literature task; interim flags already in place | M |
| G-P2-21 | Long-COVID mechanism layers (microclots, viral persistence, autoantibodies) E0–E1 with independent non-replication — motivate axes, contribute no parameters | Keep parameter-free; revisit on new evidence | S |
| G-P2-22 | Wearable EE/GPS/temperature metrology anchors incomplete (cadence-lock, GPS 3–10 m, skin-T offsets ±0.5–1.5 °C vs core) | SENSOR defaults exist; wire into observation layer with bias sampling (D19) | M |

## P3 — FUTURE / HYGIENE

| ID | Gap | Note | Cx |
|---|---|---|---|
| G-P3-01 | Packaging/CI (no requirements/pyproject, no CI, implicit namespace packages) | Add with pytest + `validate_kb.py` + review-freshness gates | S |
| G-P3-02 | Docs stale (architecture.md missing Cycle-2/3, review tracker, experimental mode; SCHEMA legacy paths) | Sync after P0/P1 code changes | S |
| G-P3-03 | POTS medication prescription-prevalence distributions (E0; only study-arm frequencies) | External epidemiology; sample with wide priors meanwhile | S |
| G-P3-04 | Review-tracker extensions (findings CLI, confidence scores, orcid/commit fields) | Additive per ADR 0001 | S |
| G-P3-05 | Second intervention protocols (exercise/meal/stand as protocol registry entries; tilt_test.yaml currently data-only, unparsed) | Wire protocol registry into engine | M |
| G-P3-06 | Advanced calibration/inference (assimilation of real wearable streams; hierarchical Bayesian cohort fitting) | Post-v1 research direction | L |

---

## REMEDIATION ROADMAP

### Phase 0 — MUST happen before first dataset (blocking; ~6–10 dev-weeks critical path)
1. **Engine correctness:** G-P0-01 (compounding), G-P0-04 (mismatches/dead blocks/Fox→Tanaka), G-P0-03 (neuropathic resolution or formal scope-out). *[S+M, no external deps]*
2. **Core realism:** G-P0-05 (structured HRV + respiration), G-P0-06 (circadian/sleep/virtual time), G-P0-09 (protocol-conditioned orthostatic reference + evaluator metric unification). *[M–L; the long pole]*
3. **Generation layer:** G-P0-07 (cohort sampler/manifest/provenance), G-P0-08 (evidence-mode policy), G-P0-10 (tier→E mapping + labels), G-P0-02 (PEM wiring with evidence-conformant kernels + extrapolation labels). *[M–L]*
4. **Credibility gates:** G-P1-05 (provenance gating + human L3 process initiated), G-P1-10 (validation harness with AUC caps + negative controls + registered exclusions incl. G-P1-06 PEM), G-P1-17 (SHARED-latent architecture per overlap matrix), G-P1-03 (volume mixture), G-P1-11 (RHR semantics), G-P1-14 (banned-field lint). *[S–M, parallelizable]*
5. **Scope freeze:** v1 = canonical-active phenotypes (healthy + 3 POTS + heat + fludrocortisone-acute + ME/CFS-HM) + explicitly labeled experimental slices; tilt-protocol-first; intended-use decision (G-P2-16) documented.

**Definition of done for Phase 0:** `pytest` green incl. former xfails resolved or formally scoped; `validate_kb.py` whitelist-free path planned; a generated pilot cohort whose manifest passes provenance audit; harness caps verified on healthy-only data.

### Phase 1 — first post-v1 quality cycle
G-P1-01 (ΔSBP structure), G-P1-02 (sensor wiring), G-P1-04 (Fu branch), G-P1-07 (external dataset curation + distribution-distance validation), G-P1-08 (muscle pump), G-P1-09 (thermoregulation/sleep-stages/accelerometry modules), G-P1-12, G-P1-13, G-P1-15, G-P1-16.

### Phase 2 — enrichment
P2 items, prioritized: G-P2-01 (medication phases), G-P2-13 (pacing state), G-P2-14 (stacking rule), G-P2-15 (primary-source extraction), G-P2-02 (symptom layer grounding), then the bounded literature tasks (G-P2-20) and factor-structure sensitivity work (G-P2-03/05).

### Phase 3 — continuous governance
P3 hygiene; registry DOI re-verification pass; human L3 completion across all KB files; annual evidence refresh (PEM wearable datasets, severe-ME/CFS monitoring, adult fever regression, panic ambulatory data are the four external evidence items that would most change the model).

*Cross-references: binding downgrades and SHARED-latent architecture in `DISEASE_PHYSIOLOGY_EVIDENCE.md`; claim-level provenance in `EVIDENCE_REGISTRY.yaml`; engine specifics in `CURRENT_IMPLEMENTATION_MAP.md` / `CURRENT_PHENOTYPE_SCOPE.md`.*
