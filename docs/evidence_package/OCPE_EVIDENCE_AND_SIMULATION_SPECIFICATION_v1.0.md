# OCPE — EVIDENCE AND SIMULATION SPECIFICATION v1.0

**Document role:** Final synthesis (capstone) of the OCPE research swarm. This is the single document an independent engineer or scientist should use to determine **what OCPE should simulate, why, with what evidence, with what uncertainty, through which interactions, into which wearable outputs, and against which validation**.

**Author role:** Final Synthesis Scientist (OCPE research swarm). **Status:** DECISION DOCUMENT — it binds scope, evidence discipline, and validation gates for the first dataset release.

**Source of record:** every statement below traces to the Pass-1/Pass-2/Pass-3 artifacts in `/mnt/agents/output/ocpe/` (full inventory in §8.2). The four machine-readable translation artifacts — `EVIDENCE_REGISTRY.yaml` (143 claims), `PHYSIOLOGICAL_RELATIONSHIPS.yaml` (26 relationships), `PARAMETER_SPECIFICATION.yaml` (58 parameters), `EVENT_PROTOCOLS.yaml` (16 protocols) — are the executable layer; this document is the decision layer on top of them.

**Binding evidence scale (single convention, enforced everywhere in this document):** E0 hypothesis · E1 mechanistic · E2 observational human · E3 controlled human experimental · E4 replicated quantitative · E5 meta-analysis/consensus. Dossier-native grades on other scales (TEMPORAL inverted; WEARABLE_OBSERVABILITY metrology; repo tiers A–D) are preserved verbatim in `EVIDENCE_REGISTRY.yaml.dossier_evidence_strength` but are **not** authoritative (EVIDENCE_AUDIT_NOTES §0; the three-scale defect is itself a closed evidence-layer item whose engine-side enforcement is G-P0-10).

**Binding auditor decisions:** the 22 downgrades/refutations D1–D22 in `DISEASE_PHYSIOLOGY_EVIDENCE.md` §1 (sourced from EVIDENCE_AUDIT_NOTES.md, CONTRADICTION_AUDIT.md, INDEPENDENT_REVIEW_PASS2.md) override every dossier statement. The 23-item must-not-be-hard-coded list (EVIDENCE_AUDIT_NOTES §c) and the 12-item model-uncertainty list (CONTRADICTION_AUDIT §E) are mandatory distribution/mixture representations, never point constants.

---

## 1. EXECUTIVE SUMMARY

**What OCPE is.** OCPE (Open Computational Physiology Engine) is intended to be an evidence-based generator of synthetic multimodal wearable data (ECG, PPG, EDA, respiration, skin temperature, IMU) for healthy physiology and systemic disorders (POTS/dysautonomia, ME/CFS, long COVID, hEDS, autoimmune/inflammatory, metabolic, neurological). The repository today contains a beat-by-beat 12-state 0-D cardiovascular ODE with baroreflex Hill control (Geddes 2022 backbone), a composable YAML perturbation framework with canonical/experimental evidence modes, chest-strap ECG and wrist PPG sensor models, a review-sidecar governance system, and a 67-test suite — but **no dataset-generation layer, no structured HRV, no circadian/sleep coupling, and a parameter-corruption bug in the behavior path** (CURRENT_IMPLEMENTATION_MAP.md).

**What the evidence base is.** Thirteen Pass-1 dossiers plus three Pass-2 audits, consolidated into a 143-claim normalized registry (E0–E5), 26 quantitative physiological relationships, 58 parameter specifications (25 implementable-now, 22 provisional-with-uncertainty, 11 requires-further-research), and 16 event protocols. The evidence layer passed independent review on confirmation bias, mechanism-vs-observable discipline, and timescale discipline; it carries binding downgrades wherever the literature is contradicted, single-sourced, or over-precise (INDEPENDENT_REVIEW_PASS2.md; CONTRADICTION_AUDIT.md — 23 citations independently re-verified, none fabricated at dossier level, in stark contrast to the repo's own history of 4/8 fabricated disease-file DOIs).

**The decision (§2).** **NOT READY.** OCPE cannot today generate a scientifically defensible evidence-based wearable systemic-disorder dataset. Ten P0 gaps exist in `OCPE_RESEARCH_GAP_ANALYSIS.md`, and P0 gaps by definition block defensible generation. They include a silent behavior-parameter compounding bug (`engine.py:139`) that corrupts every non-rest scenario by an unbounded factor; dead PEM code whose constants contradict the evidence by ~2 orders of magnitude; absence of structured HRV (the primary observable carrier of nearly every disease axis); absence of circadian/sleep coupling (where most disease signatures live); no dataset infrastructure whatsoever; a neuropathic-POTS phenotype that fails its own clinical acceptance criterion; and silent divergence between documented and actually-applied generative parameters. None of these requires new literature at scale; all are integration and engineering work estimated at ~6–10 dev-weeks of critical path (Phase 0, GAP §Roadmap).

**First dataset (§3).** The recommended first vertical slice is **healthy vs graded orthostatic-intolerance/POTS-like physiology under a tilt-first protocol family (supine → 60–70° head-up tilt 10 min → optional prolonged standing → supine recovery), with the full modality stack (ECG strap, wrist PPG, EDA, skin temperature, respiration, IMU)** — restricted at release to the evidence-licensed generative branches: the protocol-conditioned healthy reference and the hypovolemic/volume axis (the only POTS branch that currently meets its ≥30 bpm criterion and the only one anchored in triangulated human data). Neuropathic POTS is scoped out or labeled experimental-xfail; hyperadrenergic POTS ships only with its ΔSBP criterion failure disclosed. This recommendation is a hypothesis tested in §3, not an assumption: it wins on evidence depth, engine readiness, and — decisively — on the availability of open validation data (PRCP, EUROBAVAR, Autonomic Aging), with the explicit caveat that no open POTS patient cohort exists and validation is proxy-plus-published-statistics until the restricted Zenodo POTS request clears.

**Architecture (§5).** The cross-condition overlap matrix shows 13 of 15 candidate mechanism axes are shared across conditions. The binding architecture is therefore **shared latent axes** (single tonic vagal gain knob; one systemic-inflammation core; graded orthostatic axis; deconditioning axis; sleep-fragmentation/OSA generator; post-exertional recovery kernel; post-infection layer; medication-mask layer; stress/pain/hyperventilation cores; menstrual/circadian modulation) with condition layers as sampling priors — never per-condition machinery — under anti-laundering rules that forbid emitting any feature whose between-condition separation is smaller than within-condition/within-person variance as discriminating, and cap classifier performance at evidence-honest bands (ME/CFS single-feature AUC ≤0.7–0.8; LC 0.75–0.85; >0.95 anywhere = release failure).

**Governance (§6).** Given the repo's fabricated-DOI history, provenance must be structural: dataset build refuses KB files without FRESH SHA-256 sidecars and tier/E-level labels; human L3 review is mandatory (currently zero files carry it); registry DOIs were copied verbatim and require a Pass-3 re-verification before any number is locked.

**Traceability (§7).** Every claim is navigable end-to-end: `claim_id → registry (normalized E-grade, source, distributions) → parameter spec (sampling rule, equation) → relationship (functional form) → event protocol (expected phases) → engine/sensor layer (observable channels + artifact model) → validation level 1–5`. A complete worked example (POTS hypovolemic blood volume → orthostatic ΔHR) is provided.

---

## 2. FINAL SCIENTIFIC DECISION

### 2.1 Verdict

> **Is OCPE currently capable of generating a scientifically defensible evidence-based wearable systemic-disorder dataset?**
> >
> # **NOT READY**

**Criterion applied.** The project's own severity scale (OCPE_RESEARCH_GAP_ANALYSIS.md header) defines **P0 = blocks scientifically defensible dataset generation**. Ten P0 gaps are open. The verdict is therefore forced; the only substantive content of this section is what must happen to change it. For completeness: the *evidence layer alone* is sufficient as an evidence base (INDEPENDENT_REVIEW Criterion 9: "sufficient as an evidence base; not yet sufficient to build a defensible dataset without the revisions in §4"), and the verdict is NOT READY *for generation*, not for the research program, whose Phase-0 path is fully specified and requires no large-scale new literature discovery.

### 2.2 Critical blockers (the 10 P0 gaps — each independently blocks release)

| Gap | Defect (verified location) | Why it blocks defensible generation |
| --- | --- | --- |
| **G-P0-01** | Behavior-parameter compounding bug, `engine.py:139`: behavior mods computed from `self.model.params` each beat, so multiplicative perturbations compound per heartbeat (verified: 5 beats of `meal` drives RalpM 17.88→4.24 instead of one-shot 13.41; TotalVol +650 mL; exercise Es ×1.30/beat unbounded) | Every meal/exercise/stress scenario silently corrupts physiology; destroys every evidence-anchored behavior kernel (postprandial +6±3 bpm etc.). Any dataset containing non-rest records is wrong by an unbounded factor |
| **G-P0-02** | PEM machinery is dead code (`engine.py:120` never passes `current_exertion`; `is_sleeping=False` hardcoded) with constants contradicting evidence by ~2 orders of magnitude (2-h "resolution" vs mean 12.7-day recovery, range 1–64 d, Moore 2023) | ME/CFS is a flagship phenotype whose defining feature cannot fire; wiring it with current constants would be scientifically indefensible |
| **G-P0-03** | Neuropathic POTS fails its own acceptance criterion: sustained ΔHR 21.2 bpm vs ≥30 target (strict-xfail, `tests/test_orthostatic_response.py:212`); flat dose-response 18.5→21.7; tilt-onset application semantics (Geddes Eq. 2.16) unimplemented | Shipping a flagship POTS subtype that fails its published clinical criterion is a scientific defect; xfail is documentation, not resolution |
| **G-P0-04** | Engine-vs-KB parameter mismatches (hyperadrenergic kR applies 34.78 not 32; kH 31.48 not 34; p2H 89.96 not 89.8); dead conflicting inline `phenotypes:` blocks (kR→40 vs 32); `population.py` uses the superseded Fox HRmax equation against the E5 Tanaka anchor (208−0.7·age, ε~N(0,11)); sex/BMI/fitness priors uncited | The dataset's actual generative parameters currently differ from every documented value — precisely the silent-divergence failure class the provenance system exists to prevent |
| **G-P0-05** | No HRV structure: beat-to-beat variability is uniform ±2% multiplicative noise (`engine.py:231-232`); PPG "respiration" is a cosmetic 0.25-Hz sine; no respiration model exists | HRV (RMSSD/SDNN/DFA-α1) is the primary observable carrier for nearly every condition axis (shared tonic vagal gain latent #1); without RSA, Mayer-wave LF, and 1/f structure the dataset cannot support its own evidence claims |
| **G-P0-06** | No circadian/sleep coupling: 24-h clock advances in real seconds during minute-scale sims; `D_circ` computed but never fed to any parameter; sleep never entered; no multi-day scheduling | Circadian HR amplitude (~13.5 bpm), nocturnal-dip reference frames, sleep-stage autonomics, PEM day-scale dynamics, menstrual modulation, and flare prodromes — the dominant variance structure of the dataset and most disease signatures — are absent or fictional |
| **G-P0-07** | No dataset-generation infrastructure: no cohort sampler (`cohorts.yaml` unparsed; `VirtualSubject` is a single deterministic subject), no batch runner, no output schema/manifest, no per-record provenance, no seeding policy beyond `seed=42` | There is literally no mechanism to produce a defensible dataset; `examples/*.py → results/*.npz` is the only output path |
| **G-P0-08** | Experimental-mode policy undecided: 7 of 10 phenotypes are (partly) tier-D; hEDS, autoimmune, sleep-deprivation, beta-blocker are bit-identical to healthy in canonical mode; all tier-D values are machine-proposed | A dataset generated today silently ships healthy-identical "disease" traces or unmarked machine-proposed physiology |
| **G-P0-09** | Healthy orthostatic reference not frozen or protocol-conditioned; evaluator uses peak ΔHR (inflated by steep-Hill limit cycle) while tests use sustained — two different metrics gate "POTS vs healthy" | The healthy false-positive rate at the 30-bpm boundary (33–60% on aggressive protocols, <5% casual stands; D14/CONTRADICTION Target 1) is the single most consequential calibration choice; every downstream POTS claim depends on it |
| **G-P0-10** | Evidence-scale harmonization not enforced in generation: repo tiers A–D/levels 1–4 unmapped to E0–E5; generated outputs carry no evidence labels (evidence layer itself resolved in the registry) | Without enforced mapping, dataset consumers cannot distinguish established human evidence from machine-proposed fits |

### 2.3 Required scientific remediation (before or during Phase 0; gap IDs referenced)

1. **Freeze the protocol-conditioned healthy orthostatic reference** (G-P0-09; D14; CONTRADICTION Target 1): stand vs tilt vs NASA-lean, initial transient vs sustained, age strata, with the healthy >30-bpm exceedance rates stated numerically per protocol (casual stand <5%; lab stand ~10–33%; tilt-10 min ~60%; tilt-30 min ~80%; adolescents 95th pct 41–48 bpm → pediatric criterion ≥40). Unify evaluator and tests on the **sustained** metric. Decide muscle-pump policy (G-P1-08): tilt-only v1 with documented structural limitation, or implement a Heldt-style pump.
2. **Adopt the binding parameter resolutions already specified** (PARAMETER_SPECIFICATION.yaml `binding_resolutions_applied`): hypovolemic TotalVol=3500 demoted to extreme-tail scenario sample, replaced by the mixture distribution (hypovolemic branch ~40–50% weight, deficit −14±10%; volume-normal branch) per CONTRADICTION Target 3 (G-P1-03); Geddes gain perturbations demoted to tier-D scenario samples with the competing Fu-2010 branch (small LV mass + hypovolemia, *intact* baroreflex) as an explicit alternative generative mechanism (G-P1-04); Fox→Tanaka HRmax replacement; age-graded fever slope 7–13 bpm/°C (D4, G-P1-12).
3. **Wire PEM as evidence-conformant kernels** (G-P0-02): symptom kernel (onset Gamma mode 12–24 h, peak 24–48 h, right-skewed recovery mean 12.7 d, range 1–64 d — D2/D18, mean not median) decoupled from the physiological slowed-recovery kernel (τ 3–6 h healthy → 9–13 h patient post->VT1; delayed physiological second wave E0, default OFF); exertion-dose trigger (VT1-proxy ≈ RHR+15 bpm) carried as a labeled modeling hypothesis, never established law; PEM detectability mixture (~50–65% of episodes); all PEM channels labeled `evidence_mode: extrapolation` and registered as a **validation exclusion** (G-P1-06) because no multi-day wearable PEM dataset exists.
4. **Resolve or formally scope out neuropathic POTS** (G-P0-03): implement bounded stress-relaxation creep (van Heusden 2006) and tilt-onset trigger semantics (G-P1-16); re-run dose-response; if sustained ΔHR still <30 bpm, scope neuropathic to "experimental-only with published-criterion xfail" rather than shipping a failing canonical phenotype.
5. **Enforce the overlap matrix and anti-laundering rules in generation** (G-P1-17; §5 below): SHARED latents as core modules, condition layers as priors only, per-record latent-draw provenance; the anti-laundering CI test (between-condition separation < within-condition variance on shared axes).
6. **RHR semantics** (G-P1-11; D20): freeze nocturnal-RHR channel semantics; all disease RHR effects as within-person deltas; Quer within-person SD ≈3.0 bpm/CV 4.6% supersedes the E0 healthy estimate; Welltory constraint (rest-only classifier must fail) wired as a negative control.
7. **Evidence-scale mapping into the KB schema** (G-P0-10; EVIDENCE_AUDIT_NOTES §e): tier A→E4/E5, B→E2/E3, C→provenance "machine-fitted" + strength E0–E1 + mandatory human-range citation, D→E0 + engine-inert; CI rule "no canonical parameter without E-level + provenance tag; no E0/E1 in canonical mode."
8. **Statistic/precision enforcement** (G-P1-14): `single_source` flags on Moore-PEM, van-Campen-CBF, RA-Forecast-derived parameters; manifest lint banning F1/AUC emission as validated (D6, D22, CONTRADICTION §E.12).
9. **Retrofit hardcoded uncited constants into the KB** (G-P1-15): symptoms thresholds, behavior magnitudes, 15 latent defaults, time-engine constants, sensor coefficients, `hrv_noise=0.02`, 14-s ramp, 20 cm carotid height — each mapped to a dossier anchor or labeled tier-D.
10. **Sensor layer re-anchoring** (G-P1-02; D19): drive noise/dropout/artifact from KB validation metrics (Polar H10 LoA −2.3/+2.4 ms, ICC 0.99 rest / 0.96 high-intensity; PPG HR LoA −7.19/+6.64 bpm; day/night usable fractions; cadence-lock), remove the hardcoded t∈[200,214] s motion window, and sample skin-tone terms (mass at ~0 for PPG-HR; positive-bias distribution for SpO2) rather than baking constants.

### 2.4 Required engineering remediation (Phase 0, critical path ~6–10 dev-weeks; GAP §Roadmap)

1. **Engine correctness:** fix G-P0-01 (behavior deltas from pristine canonical+perturbation parameter set each beat; additive latent nudges with explicit decay) with regression tests (meal 5-beat RalpM==13.41 stable; idempotence property test). Fix G-P0-04 (load-time assertion `normal_value==KB nominal`; delete dead inline phenotype blocks; applied-value equality test per phenotype). Complexity S each.
2. **Core realism (the long pole, M–L):** G-P0-05 structured HRV — respiration state (rate/tidal volume, posture/sleep-stage conditioned, KORA-FF4 distribution) → RSA phase coupling; LF Mayer-wave oscillator with loop gain/phase (required anyway for the POTS 0.1-Hz signature); 1/f background targeting DFA-α1 ≈1.0 at rest; ectopy model; day-to-day within-person CV injection (lnRMSSD 10–15%). G-P0-06 virtual-time scheduling with event calendar; D_circ → kR/kH/HM coupling; sleep-state machine with stage-conditioned autonomics (N3 vagal max, REM bursts); day-scale loop. G-P0-09 protocol-conditioned orthostatic reference in engine + KB.
3. **Generation layer (M–L):** G-P0-07 cohort sampler from dossier joint distributions (demographics, severity latents, SHARED latents per §5, comorbidity draws with 0.3–0.5× ascertainment down-weighting, background-rate honesty for controls); batch runner with seed policy; manifest schema (applied params, canonical/experimental mode, seeds, code/KB SHA-256, per-channel claim_ids). G-P0-08 dataset-mode flag and per-record `evidence_mode` field. G-P0-10 labels in manifest.
4. **Credibility gates (S–M, parallelizable):** G-P1-05 provenance gating (dataset builder refuses non-FRESH sidecars); G-P1-10 validation harness (`validation/harness.py` with registered targets, AUC caps, unified negative controls NC1–NC12, pre-registered tolerances, validation-exclusion registry); G-P1-03 volume mixture; G-P1-11 RHR semantics; G-P1-14 banned-field lint.
5. **Scope freeze:** v1 = canonical-active phenotypes (healthy + hypovolemic/hyperadrenergic/neuropathic POTS per §3 disposition + heat + fludrocortisone-acute + ME/CFS-HM) + explicitly labeled experimental slices; tilt-protocol-first; intended-use decision (G-P2-16) documented before release.

**Definition of done for Phase 0 (verbatim from the gap analysis):** `pytest` green including former xfails resolved or formally scoped; `validate_kb.py` whitelist-free path planned; a generated pilot cohort whose manifest passes provenance audit; harness caps verified on healthy-only data (healthy-only data must *fail* the disease caps — the harness self-test).

### 2.5 Required validation (before any utility claim)

Per `SYNTHETIC_TO_REAL_BENCHMARK.md` (acceptance gate; tolerances pre-registered, post-hoc widening forbidden):

1. **Level 1 — mathematical validity:** equation fixtures, mass conservation, integration tolerance, determinism/seed sweep, identifiability guards (unrecoverable parameters labeled `non_identifiable` and fixed to literature distributions — CI-enforced), honesty gating, scale-harmonization machine check.
2. **Level 2 — physiological plausibility:** the 11-protocol trajectory battery (stand/tilt/recovery/exercise/meal/TSST/sleep/2-day-CPET/PEM/infection/RA-flare) plus whole-record timescale signatures (DFA-α1, inverse-Gaussian RR, spectral peaks with RSA respiration-scaling, Mayer-wave emergence, multiscale-entropy CinC-2002 realism bar, circadian cosinor, weekly lnRMSSD CV, menstrual biphasic pattern, training block).
3. **Level 3 — clinical plausibility:** 18 positive distribution targets (§3.1 of the benchmark) with pre-registered tolerances, and the 12-item negative-control battery (NC1–NC12: LF/HF never a sympathetic index; AUC band 0.75–0.85; TNF-null; SpO2-null; classifier ceilings; panic-vs-seizure confusability; no PEM detector; menstrual-not-flare; CPET decrement not patient-specific; no optical glucose; cuffless BP cannot certify no-OH; disease sleep staging capped at healthy κ). Any NC failure invalidates the release regardless of other scores.
4. **Level 4 — signal-level comparison to real open datasets** per the priority ladder (§6 of this document's §4.Q11): PRCP first (free, immediate), then PPG-DaLiA, WESAD, EUROBAVAR (labeled reflex-gain validation only), Autonomic Aging (n=1,121 healthy envelope — the synthetic healthy cohort must sit inside it *before* any disease perturbation is judged), plus artifact/usability validation against published free-living usable-fraction statistics.
5. **Level 5 — synthetic-to-real transfer matrix** (tasks T1–T7, cells R→R/S→S/S→R/R→S/S+R→R, participant-level splits): S→R within 10% relative of R→R = PASS; report all cells including failures; the binding sentence — *"OCPE synthetic data are candidate research artifacts whose utility for any task is unestablished pending the Level-5 benchmark"* — must appear in all documentation until then.
6. **Registered validation exclusions** (SYNTHETIC_TO_REAL_BENCHMARK §6): PEM individual-level dynamics; severe-ME/CFS physiology; hEDS venous pooling; direct POTS cohort validation (proxy + published-statistics until restricted access clears); long-COVID waveforms, EDS/autoimmune wearable data, consumer-watch PPG at scale, cold-pressor beat-to-beat (literature-constraint tier only); disease-specific sleep staging; multi-day full-stack synchrony (piecewise only); metabolomic/ML-classifier targets permanently barred.

---

## 3. FIRST DATASET RECOMMENDATION

### 3.1 The hypothesis under evaluation

**Candidate first validated dataset:** *Healthy vs orthostatic-intolerance/POTS-like physiology under supine → standing/tilt → prolonged standing → recovery, with ECG, PPG, EDA, respiration, skin temperature, and IMU.*

This is evaluated below as a hypothesis against three axes — evidence strength, validation-data availability, engine readiness — and against the plausible alternatives (ME/CFS-first, long-COVID-first, healthy-only-first). It is not assumed.

### 3.2 Evidence strength: POTS has the deepest quantitative base — with two load-bearing caveats

**For the hypothesis:**

- The defining criterion is consensus-grade: sustained orthostatic ΔHR ≥30 bpm/10 min (≥40 ages 12–19) without OH (EVD-POTS-001, E5).
- The hypovolemia finding is the best-replicated objective abnormality in the entire disease scope: blood-volume deficit −12 to −15% triangulated across three independent methods/cohorts (Raj 2005 131I-albumin 689±270 mL, n=15; Fu 2010 dye-dilution 60 vs 71 mL/kg; Kulapatana 2025 CO-rebreathing −13.92±10.38%, deficit correlates with upright HR r=−0.608 in POTS only) — EVD-POTS-004, E4, CONTRADICTION Target 3 verdict (A) CONFIRMED in direction/magnitude class.
- Subtype mixture structure is empirically grounded: Angeli 2024 (n=378, verified) joint distribution — hyperadrenergic 75.0%, hypovolemic 44.9%, neuropathic 37.8%; 41.7% dual, 11.4% triple, 6.8% none — which licenses *composable continuous axes* rather than discrete classes (EVD-POTS-003, E2, referral-bias caveat).
- Orthostatic time courses are quantified at minute resolution: HUT 49±4/55±5/62±4 bpm at 5/10/30 min; stand 44±4/50±4; group separation develops over minutes 2–10 (EVD-POTS-005, E4); fast supine recovery 50–70% of ΔHR recovered in 20–60 s (EVD-POTS-012, E4); AM>PM diurnal modulation with 100% vs 28–44% criteria-positive rates (EVD-POTS-002, E4).
- The healthy contrast side is equally quantified — the full protocol-conditioned table exists (SPEC §5.4; CONTRADICTION Target 1), and the SV→HR compensatory coupling that carries the signal is an E3 relationship (REL-HR-SV-COMPENSATION).

**Caveat 1 — the 30-bpm boundary is protocol-fragile (D14).** Healthy exceedance at 10 min ranges from <5% (casual stand) through 33% (NASA lean; lab-protocol stand specificity 67%) to ~60% (10-min tilt) and ~80% (30-min tilt); healthy tails are unmeasured at scale in free living. Consequence: the dataset must treat *protocol* as a first-class covariate on every orthostatic record (EVENT_PROTOCOLS `protocol_dependence_policy` is MANDATORY), and the healthy tail behavior is itself a pre-registered validation target — not a nuisance.

**Caveat 2 — the parameter backbone is single-source in-silico and partially engine-falsified (D5).** All 29 Geddes-base parameters and the POTS gain perturbations trace to one modeling paper; the engine itself falsifies two of four phenotype stories (neuropathic 21.2 vs ≥30 bpm; hyperadrenergic ΔSBP −4.0 vs +10 mmHg). The binding resolution (scenario sampling at tier-D discipline + the Fu-2010 competing branch with intact baroreflex) converts this weakness into honest model-structure uncertainty — but it means the first slice must be built on the *human-anchored* volume axis, not on Geddes gain magnitudes.

### 3.3 Validation-data availability: decisive asymmetry

- **Open and immediate:** PRCP (10 healthy, ECG + continuous BP, slow/rapid tilt + stand-up — the orthostatic ground truth; Level-4 W1≤3 bpm on ΔHR distributions), EUROBAVAR (21 subjects supine/standing incl. 2 baroreflex-impaired — the only open dysautonomia analogue, labeled reflex-gain validation only), Autonomic Aging Jena (n=1,121 rigorously screened healthy — the population envelope), plus the cardiorespiratory-orthostatic PhysioNet set for the stand-up transient.
- **Not available:** no openly downloadable diagnosed-POTS tilt/stand dataset exists anywhere (VALIDATION_DATASETS §1 honest statement; §12 item 1). The only raw POTS resource is Zenodo 20327114 (13 POTS/13 controls, posture×exercise) — **restricted, access on request; request pending**. The PSB-2026 Faros-ECG POTS cohort (66/20) is not released.
- Consequence: the POTS arm of this slice is validated as *impaired-autonomic proxies + published-statistics constraints* (pre-registered Level-3 targets), not direct cohort validation, until the restricted request clears. This is a disclosed limitation, not a blocker — and it is *less* severe than for any alternative first slice (see 3.5).

### 3.4 Engine readiness: tilt model exists; exactly one POTS branch meets its criterion

| Component | State (verified) | Readiness for the slice |
| --- | --- | --- |
| 12-state ODE + baroreflex Hill loops + Cycle-2 venous extension (venomotor reflex, stress-relaxation creep) | Implemented; structure evidence-cited (Heldt 2002, van Heusden 2006); healthy sustained tilt ΔHR 19.49 bpm, pooling 421 mL simulation-verified | **Ready** after G-P0-01/04/09 fixes; healthy tail calibration pending G-P0-09 |
| Tilt protocol | `tilt_test.yaml` exists but is data-only/unparsed; examples hardcode 200 s supine / 60° / 100 s tilt | Minor wiring (G-P3-05) |
| Hypovolemic branch | Meets sustained ≥30 bpm (34.6 bpm, test-verified) | **Ready** after G-P1-03 mixture replacement |
| Hyperadrenergic branch | ΔHR ≥30 met (34.2); ΔSBP +10 criterion fails (−4.0; 0-D windkessel structural limit, strict-xfail); applied-value mismatch (G-P0-04) | Ships only with disclosed limitation; ΔSBP channel cannot certify the pressor signature |
| Neuropathic branch | Fails criterion even in experimental mode (21.2 bpm; flat dose-response; hydrostatic-gate-limited) | **Not ready** — scope out of v1 canonical dataset or ship as experimental-xfail slice (G-P0-03) |
| Muscle pump (active stand) | Absent; historical 76.1 bpm healthy failure; pooling calibration fragile | Tilt-first v1; stand protocols documented as structurally limited, or pump implemented (G-P1-08) |
| Structured HRV / circadian / sleep | Absent (G-P0-05/06) | **Required before release** — the slice's disease signatures (reduced upright rMSSD, Mayer-wave amplification, AM>PM asymmetry, nocturnal HR) live exactly in this structure |
| Sensor/artifact layer | Implemented but decoupled from KB validation metrics | G-P1-02 wiring; artifact realism is a HARD RULE (SPEC §0.3) |

### 3.5 Alternatives considered and rejected for slice #1

- **ME/CFS-first:** rejected. The defining feature (PEM) is dead code, its physiological channels are a validation exclusion (no multi-day wearable PEM dataset exists at any access level; nearest proxy n=127 long-COVID), baseline effects sit below the within-person noise floor (+4.14 bpm RHR vs ~5 bpm noise), and the marquee lab signature (2-day CPET) has a direct null replication (Natelson 2026: decline *less* frequent in patients, 22% vs 33%). There is no defensible validation target for a first dataset. ME/CFS enters in the second cycle, anchored on step-severity tertiles and the slowed-recovery kernel, with PEM as assumption-labeled extrapolation.
- **Long-COVID-first:** rejected. RECOVER routine labs are null (the boundary condition); all signature effects are small, penetrance-weighted, and definition-dependent; no open continuous-waveform data exist. Its best-validated module (post-infection RHR trajectory, E4) is a *shared base layer* (SHARED latent #7) that will be built anyway and composed under the orthostatic slice's post-infectious personas.
- **Healthy-only-first:** necessary but not sufficient. The healthy reference must be built and validated first *internally* (it is the binding calibration layer; every disease perturbation acts on it), but releasing healthy-only data does not demonstrate the systemic-disorder capability that is OCPE's purpose, and the orthostatic contrast is exactly where healthy-tail honesty (the hardest part of the healthy model) is testable.
- **Stress/sleep-first (WESAD/MESA-anchored):** viable second slice (open data, CORE modules evidenced) but weaker as a *systemic-disorder* demonstration; stress physiology is shared-core machinery, not a disease claim.

### 3.6 Recommendation

**Adopt the candidate slice, narrowed as follows — "vertical slice v1":**

1. **Population:** healthy reference cohort + graded orthostatic-axis cohort (the SHARED orthostatic latent #4: a continuous ΔHR-liability continuum 0→>30 bpm with protocol-conditioned healthy reference), on top of which the POTS label is a threshold crossing — never a binary disease switch. POTS personas express the hypovolemic/volume branch as the primary evidence-licensed mechanism (mixture per §2.3.2), with hyperadrenergic gain as a secondary flagged branch and neuropathic excluded from canonical v1.
2. **Protocols:** tilt-first (supine ≥10 min baseline → 60–70° HUT 10 min → supine recovery), with active-stand and NASA-lean as protocol variants *labeled with their structural limitation* (no muscle pump in v1) or held until G-P1-08; every record carries protocol covariates (supine-rest duration, fasting, time of day, age).
3. **Modalities:** full stack (ECG strap RR/HR/HRV; wrist PPG HR/PRV with PRV≠HRV modeling; EDA tonic/phasic; skin temperature; respiration belt + PPG-derived; IMU posture/activity), with the artifact scheduler and missingness model active — the artifact layer is part of the validated product, not an afterthought.
4. **Embedded honest tails and confounds:** healthy >30-bpm exceedance at protocol rates; within-person day-to-day orthostatic CV 15–25% (provisional flag); menstrual/medication/anxiety confound layers active so that orthostatic tachycardia is not trivially classifiable (anti-laundering, §5).
5. **Validation:** Level 1–2 gates; Level-3 targets (POTS-vs-control ΔHR +19.88 bpm [15.24–24.52]; subtype joint distribution; volume-deficit mixture moments; demographics; resting-HR cohort-frame duality); Level 4 against PRCP → EUROBAVAR → Autonomic Aging ladder; Level 5 tasks T1 (orthostatic event detection/ΔHR regression, including the healthy-tail fidelity check that can FAIL the release regardless of AUC) and T6 (stratification in the 0.75–0.85 AUC band, reported as proxy-validated).

**What would make a different slice superior:**

- **Zenodo 20327114 access granted + a second open POTS cohort appearing** → upgrade the same slice from proxy-validated to direct-cohort-validated; this strengthens the *same* slice rather than replacing it.
- **Muscle-pump module validated against the PhysioNet stand-up transient set** → the active-stand protocol (the clinically dominant one) becomes first-class; slice extends rather than changes.
- **A multi-day wearable PEM dataset emerging** (the single external evidence item that would most change the model, GAP Phase 3) → ME/CFS slice becomes defensible and would rival the orthostatic slice on novelty; re-evaluate then.
- **Human L3 review completing faster for the metabolic/neurological KB files than for POTS** → improbable given the POTS evidence lead, but provenance gating (§6), not evidence depth, is the formal gate; whichever slice achieves full FRESH-sidecar + L3 + harness-pass first is releasable first.

---

## 4. ANSWERS TO THE 17 FINAL-SYNTHESIS QUESTIONS

### Q1. What does OCPE already do correctly?

(From CURRENT_IMPLEMENTATION_MAP §5 and §7 — "architecturally sound" and "can remain unchanged".)

1. **KB/code separation with sacred parameters:** canonical parameters live in YAML; the steady-state initializer never mutates params (test-enforced); 12-state Radau integration (dt=0.01 s, rtol=1e-6) with softplus-smoothed valves/gates and mass-conservation clamps is numerically defensible.
2. **Composable perturbation framework** with multiplicative compounding semantics, expression syntax (`"neuropathic_pots * environmental_heat"`), and per-application provenance (`last_application` canonical vs experimental).
3. **Honesty-by-default engine:** tier-D values are engine-inert unless `include_experimental=True`; tests assert experimental-only phenotypes are bit-identical to healthy in canonical mode — exactly the evidence-gating behavior the mission requires; keep.
4. **Sidecar governance that works:** 21/21 sidecars SHA-256-FRESH at audit; validator auto-records; ADR-0001 documents the L1/L2/L3 review model.
5. **Test-harness culture:** dynamic phenotype enumeration, seeded bit-reproducibility, strict-xfail with precise quantitative reasons for unmet clinical criteria (21.2 bpm; ΔSBP −4.0) instead of silent failure.
6. **Adversarial-review culture encoded in data:** compliance guards (`do_not_perturb: [mvl, VMvl]` with Stewart/Freeman citations), `unresolved_gaps` blocks, fabricated DOIs replaced after adversarial review.
7. **Evidence-layer assets that are already best-in-class** (INDEPENDENT_REVIEW §5): null/contradictory registers in every dossier with quantitative anti-overfitting guards; latent/observable "do-not-fabricate" discipline applied across five dossiers; an honest validation-dataset inventory that states what does NOT exist; the population dossier's unevidenced-correlation-cell markings.

### Q2. Unsupported scientific assumptions currently in the system

(CURRENT_IMPLEMENTATION_MAP §4; EVIDENCE_AUDIT_NOTES §e; CONTRADICTION_AUDIT Targets 1–8, 11.)

1. **Silent parameter corruption:** behavior compounding (G-P0-01) makes every non-rest scenario's applied parameters wrong by an unbounded factor — the single most dangerous current assumption is that outputs mean what the KB says.
2. **Applied≠documented values:** hyperadrenergic kR/kH/p2H apply 34.78/31.48/89.96, not the documented 32/34/89.8 (ratio-scaling over mismatched `normal_value`); dead inline phenotype blocks contradict the live disease files (kR→40 vs 32).
3. **Superseded population priors:** Fox 220−age HRmax against the E5 Tanaka anchor; female ×0.90 volume, Hm ×1.10, BMI and fitness factors — all uncited.
4. **Machine-calibrated extremes presented as canonical:** hypovolemic TotalVol=3500 mL ≈1.5× the triangulated measured deficit; healthy sustained ΔHR 19.5 bpm is mean-consistent but tail-unvalidated.
5. **PEM constants contradicting evidence by ~2 orders of magnitude** (2-h resolution vs 12.7-day mean recovery) — and unreachable anyway.
6. **Untiered shadow parameters** escaping governance entirely: all symptom thresholds/weights, behavior magnitudes, 15 latent defaults, time-engine constants, sensor constants (σ=1 ms, 0.5% dropout vs KB LoA ±2.3 ms/ICC 0.99), hrv_noise=0.02, 14-s ramp, 20 cm carotid height.
7. **Uniform ±2% noise as "HRV"** — physiologically unstructured RMSSD/SDNN/DFA-α1.
8. **Tier-C single-source in-silico backbone** (29 Geddes parameters, evidentially ~E1) functioning as canonical tier-A-equivalent; the 10 Cycle-2 venous magnitudes are machine fits with human-range constraints only.
9. **Vacuous validation:** `beta_blocker_efficacy` checks a scenario in which the beta-blocker is inert (canonical mode); circadian check passes trivially on a 300-s simulation.
10. **Historical (corrected, governance-relevant):** 4 of 8 original disease-file DOIs were fabricated or wrong-paper.

### Q3. What evidence is missing?

(EVIDENCE_AUDIT_NOTES §d coverage gaps — 17 items — plus dossier residual lists, G-P2-20.)

Coverage gaps that bound what v1 can claim: (1) no multi-day wearable PEM dataset (PEM channels = assumption-labeled extrapolation); (2) no validated PEM detector (PEM latent-only); (3) hEDS venous compliance/pooling never measured (E0–E1); (4) hEDS dysautonomia mechanism adjudication (deconditioning vs intrinsic) unstudied; (5) orthostatic ΔHR event-to-event reliability unmeasured (provisional CV 15–25%); (6) population correlation cells unevidenced (RMSSD↔BP, EDA↔RHR/RMSSD, steps↔RMSSD, core-temp↔RHR); (7) factor-analytic structure of autonomic/wearable batteries (E0, theory-driven); (8) adult SpO2 population distribution (pediatric anchor only); (9) adult fever→HR slope regression (PMID 31345594 full extraction pending, G-P1-12); (10) large ambulatory panic dataset (panic magnitudes genuinely unknown); (11) fludrocortisone in POTS — no adequate RCT (E0); (12) POTS medication prescription-prevalence distributions (E0); (13) severe-ME/CFS physiology (systematically excluded from lab studies; extrapolation); (14) steroid wearable effect sizes (all indirect); (15) low-grade-inflammation temperature-setpoint shifts and PPG-stiffness observability (latent-only); (16) within-person RHR SD reconciliation (resolved to Quer 2020, D20); (17) disease-specific wearable sleep staging (healthy-κ only).

Bounded retrieval tasks (P2, each a targeted literature job): exercise-onset τ; young postprandial BP; EDA absolute norms; fitness→HRR1 protocol map; healthy dawn magnitude; RER-by-IR distributions; postprandial EDA; fasting orthostatic (n≤25); TEF DOI; 72-h-fast HR primary; migraine trigger forecasting; PD resting-HR direction (do not perturb); Williams pooled r; flare skin temperature; secondary-verified classics list (G-P2-15).

### Q4. Healthy physiology to add (before any disease perturbation)

(HEALTHY dossier §1–§10; DISEASE consolidated §2; INDEPENDENT_REVIEW Criterion 5 — the healthy reference must be upgraded first because disease signatures live in the missing structure.)

1. **Structured HRV generation** (G-P0-05): respiration state (KORA-FF4 RR distribution, median 15.8 brpm, 5th–95th 12.1–20.4) driving RSA; Mayer-wave LF oscillator; 1/f background (DFA-α1 ≈1.0 rest, E4); ectopy (40–75% of adults ≥1 PVC/24 h); within-person day-to-day CVs (lnRMSSD 10–15%).
2. **Circadian coupling** (G-P0-06): HR amplitude ~13.5 bpm, acrophase ~14:40; SBP ~10/DBP ~7 mmHg; core T ~0.5 °C (nadir 04:00–06:00); distal skin T amplitude 1.2–2.2 °C; CAR +50% phase-gated.
3. **Sleep architecture:** stage-conditioned autonomics (N3 vagal max, REM sympathetic bursts); the 20–30% nocturnal "dip" is relative to *ambulatory day* — reference-frame discipline mandatory (stage-HR spread vs recumbent wake only ~2 bpm).
4. **Protocol-conditioned orthostatic curve** (§2.3.1) — the binding calibration layer.
5. **Event kernels:** postprandial +6±3 bpm (meal-size scaled to +10–20; D17); exercise on/off kinetics (τ 10–45 s; HRR1 44±11 bpm young, abnormal <12); TSST SAM arm (HR d≈0.9, SBP d≈1.2, no habituation) + habituating HPA arm (latent cortisol); cold-pressor pressor +8–12 mmHg with bimodal HR responders; hyperventilation +4.4 bpm/MAP −3.5.
6. **Menstrual modulation** (mandatory core so female disease personas are not misread): luteal RHR +2–7 bpm, RMSSD −4–5 ms, distal skin T +0.2–0.3 °C (E2–E3, high per-person heterogeneity).
7. **Population marginals with honest variance:** RHR definition-conditional (nocturnal 65.5±7.7; within-person SD 3.0/CV 4.6%/ICC 0.87); inverted-U age shape; female +3–4 bpm; fitness −5 to −12; seasonality ±1 bpm; most between-person variance unexplained — do not over-determine.

### Q5. Disease physiology to add

(DISEASE consolidated §3–§9 with binding downgrades; scope per v1 freeze.)

**v1 canonical scope:** POTS volume axis (mixture, §2.3.2); hyperadrenergic gain axis (flagged, ΔSBP limitation disclosed); heat vasodilation (Ganio ×0.58, NEEDS-REVIEW compartment mapping); fludrocortisone acute volume (+500 mL sampled ±50%, acute phase only); ME/CFS chronotropic blunting (HM ×0.92, metric-mismatch caveat). **v1 experimental-labeled scope:** neuropathic denervation (xfail-disclosed), hEDS pooling (mechanism-untested flag), autoimmune gain reduction, sleep-deprivation BRS reduction, beta-blockade ceiling. **Post-v1 condition machinery** (§5 condition-specific list): ME/CFS PEM trigger-dose state + boom-bust autocorrelation + severity latents; long-COVID trajectory classes + incidence modifiers; hEDS as composition-only; neurological injectors (cardiac-denervation gain, nOH baroreflex-failure gain, GTCS events, RBD REM movement, tremor IMU, levodopa post-dose OH windows, anxiety tonic trait, panic events); metabolic (insulin-sensitivity/GV personas, CAN severity, dawn amplitude, CGM channel); autoimmune flare wrappers with prodrome lengths and symptomatic/inflammatory discordance.

All disease resting-HR/HRV effects enter as **within-person deltas with mandatory overlap** (POTS clinic +10–20 vs real-world +~3; ME/CFS +4.14 below noise floor; LC +1–3; hEDS ~+10; T2DM +5–10; RA flare +5 — INDEPENDENT_REVIEW §2 row 9), and all condition signals are **excess-over-background** (synthetic controls carry PEM 7%, fatigue 17%, brain fog 4%, OI ~6%; EVD-LCOV-012).

### Q6. Physiological relationships to model

(PHYSIOLOGICAL_RELATIONSHIPS.yaml — 26 relationships, all with normalized E-levels and source claim_ids.)

Core coupling constraints (must hold in every generated record): **REL-HR-SV-COMPENSATION** (HR driven by SV/preload deficit, never independently — upright SV −23±5%, CO −14–20%, SVR +25%; the core POTS equation); **REL-ORTHOSTATIC-TIMECOURSE** (multi-phase kernel: transient + sustained creep + drift, parameterized per protocol; the >95%-below-30 constraint is forbidden); **REL-BAROREFLEX-SIGMOID / RESETTING**; **REL-RSA-RESPIRATORY-GATING** and **REL-HRV-GENERATION-STRUCTURE** (RMSSD = f(vagal state, respiration rate, tidal volume, HR level, device bias) — confounds mechanistic, not noise; LF/HF never emitted as a sympathetic label, NC1); **REL-ACCENTUATED-ANTAGONISM** (k~1–3, E1/E2, tunable); **REL-INTRINSIC-HR** (118.1−0.57·age); **REL-AUTONOMIC-FILTERING** (vagal 0.2–0.6 s vs sympathetic 5–20 s latencies, soft priors); **REL-VENOUS-POOLING-REFILL**; **REL-EXERCISE-KINETICS**; **REL-MEAL-RESPONSE**; **REL-TEMPERATURE-HR** (age-graded fever slope) and **REL-HEAT-RESPONSE**; **REL-SLEEP-AUTONOMIC**; **REL-CIRCADIAN-MODULATION**; **REL-PEM-SYMPTOM-KERNEL** decoupled from **REL-PEM-PHYSIOLOGY-KERNEL** (slowed recovery; delayed second wave E0-off); **REL-CPET-DAY2-CONTESTED** (small mean + effort coupling + responder subgroup; null arm generatable); **REL-MENSTRUAL-MODULATION**; **REL-MEDICATION-MASKS** (cross-disease gain layer); **REL-INFLAMMATION-IMPULSE** (LPS reference: HR +40–55% peak 3–6 h, recovery 8–24 h; no vitals change ≤0.5 ng/kg); **REL-STRESS-SAM-HPA** (habituation asymmetry); **REL-DAY-TO-DAY-DRIFT** (OU baseline); **REL-TRAINING-ADAPTATION** (RMSSD SMD 0.6–0.9 over 8–12 wk); **REL-HR-RMSSD-SCALING** (RR-scaling law, not fixed r=−0.58).

### Q7. Population distributions needed

(POPULATION dossier §A–H; SPEC §5; all correlation cells honestly marked.)

Marginals: RHR (definition-conditional, above); HRmax N(208−0.7·age, 10.5²; women 206−0.88·age, E5); HRV (24-h SDNN ~150±38 ms; 5-min RMSSD lognormal median 35–42 ms young, age-graded); RR (KORA distribution); BP (NHANES II 127/79, SBP–DBP r=0.717 — latent); SV/CO allometric scaling; skin-T (mesor ~33 °C, amplitude 1.2–2.2 °C); steps, sleep duration/efficiency, and activity marginals with day-to-day within-person SDs. Variance decomposition: between/within-person splits with ICCs (5-day RHR ICC 0.87); within-day structure. Correlation structure: documented cells retained (SBP↔DBP 0.717; RHR↔VO2max −0.34); **unevidenced cells flagged E0 with independence-sensitivity** (RMSSD↔BP, EDA↔RHR/RMSSD, steps↔RMSSD, core-T↔RHR); latent factor structure E0 — loadings sampled ±50%, Gaussian-copula sensitivity at r=0 (D21). Disease recipes: POTS (female 0.85–0.94; onset mode 14/median 17 y; ~25% disabled tail; subtype joint distribution sampled with referral-bias flag); ME/CFS (bimodal onset; severity step anchors 8235/5195/2031); LC (~75% female; penetrance-weighted axes); comorbidity joint sampling with 0.3–0.5× ascertainment down-weighting or explicit `cohort_frame: clinic`.

### Q8. Temporal dynamics needed

(TEMPORAL dossier §9 six-layer stack, adopted in SPEC §6.)

L1 slow latent modulators (OU drift τ 3–7 d; adaptation τ 2–6 wk; menstrual 28.6±3.8 d; illness/flare kernels; PEM kernel on exertion history). L2 circadian (24 h + 12 h harmonic; two-process S+C gating; masking terms). L3 event layer (gamma kernels, rise 10–30 min/decay 1–3 h). L4 fast ODE core active only during transients (Geddes-scale ~20–30 params; Mayer 0.1 Hz emerges from feedback delay — never an injected oscillator). L5 beat generator (IPFM + 1/f + Bernoulli ectopy; inverse-Gaussian as validation reference). L6 measurement model. Data flow slow→fast only; fast→slow only via aggregated exertion load. Granularity rule: closed-form sampling for slow layers; ODE only in transients; waveforms derived, not simulated. Required temporal features that do not yet exist in the engine: virtual-time scheduling, sleep-state machine, multi-day loop, boom-bust activity autocorrelation (day-to-day variation 47%), rolling-PEM baseline creep, training-block trajectories.

### Q9. Sensor models needed

(SENSOR dossier §1–§9; SPEC §2.1–2.5 device profiles and defaults; G-P1-02 wiring.)

Device profiles: research patch, Polar-H10-like strap (130 Hz, 0.7–40 Hz band — ST/morphology distortion disclosed), Empatica-E4-like wristband, Apple-Watch-like (duty-cycled green/IR, derived HR ~1 Hz), Oura-ring-like (1-min temp epochs) — duty-cycling and silent quality-gating are part of the profile. Required behaviors: KB-metric-driven noise (LoA/ICC per intensity regime), the 16-class gated artifact scheduler (motion bursts, cadence-lock — generate the *raw corrupted signal*, day/night usability, streaming vs on-device loss, non-wear, clock drift, BLE jitter, electrode motion, baseline wander, EMG, dry/contact loss, cold vasoconstriction, sampled skin-tone terms, contact pressure/light leak, IMU clipping/step false-positives, EDA thermal bias), state-dependent gating on IMU activity class/posture/perfusion/sleep/disease (slow-gait undercount 5–30% scaling with ME/CFS severity), and non-MCAR state-correlated missingness (PPG day usable 30–50%, night 65–75%).

### Q10. Wearable artifacts to model

(SPEC §2.3 table — the binding 16-class list with evidence per class; §0.3 hard rule that every inferred feature ships with its documented mimics.)

The full 16-class scheduler of Q9, plus derived-metric degradation rows: DFA-α1 LoA +58.1%/−40.9% at high intensity despite RR LoA ±~1 ms; HRV MAPE ~28.9% (Apple Watch vs H10); arrhythmia-state degradation (AF sens 0.79/spec 0.91 context); PRV≠HRV distortions (RMSSD inflation +3–6% rest; LF/HF distortion 10–40% sympathetic; posture-transition ICC ~0.5–0.7); EE heteroscedastic error ±20–30% (never a precise value); sleep staging per-device confusion matrices (κ 0.37–0.65, disease cohorts capped at healthy κ, NC12). Mandatory mimic couplings: motion-as-HRV, immobility-as-sleep, cold-vasoconstriction-as-BP-change, cadence-lock, slow-gait undercount, alcohol/jet-lag-as-infection-anomaly.

### Q11. Validation datasets that exist

(VALIDATION_DATASETS.md — verified hosts and access tiers; priority ladder §13.)

**Open now:** PRCP (orthostatic ground truth, n=10); cardiorespiratory-orthostatic PhysioNet (stand-up transient); EUROBAVAR (incl. 2 baroreflex-impaired); Autonomic Aging Jena (n=1,121); MIT-BIH arrhythmia + NSRDB + Fantasia + Icentia11k (CC BY-NC-SA) ECG; PPG-DaLiA (CC BY 4.0 — the best all-round wearable validator); BIDMC, MIMIC-III-Ext-PPG (open derivative), BUT PPG; WESAD + Wearable-Device stress/exercise + UnivPM + UT-Dallas (EDA/stress); CapnoBase + Vortal (respiration reference); CAPTURE-24 + ScientISST MOVE (IMU); Sleep-EDF + CAP (sleep); TMET-Málaga 992 tests + Wrist-PPG-exercise + TROIKA + frail post-surgery exercise; CinC-2015 false-alarm set (artifact corruption). **Registered/DUA:** MESA + SHHS (NSRR); MIMIC waveform matched subset (credentialed). **Restricted/controlled — start requests now:** Zenodo 20327114 POTS 13/13 (request pending); RECOVER BioData Catalyst (dbGaP DAR, weeks–months); All of Us Fitbit (institutional DURA, workbench-only). **Literature-constraint only:** DETECT/COVID-Collab/TemPredict published statistics; ME/CFS wearable summaries (request-only); RA Forecast marginal means. **Honest gaps (nothing at any access level):** open POTS tilt cohorts, ME/CFS raw wearables, LC continuous waveforms, EDS/autoimmune wearables, cold-pressor beat-to-beat, consumer-watch PPG at scale, multi-day synchronized full-stack (max ~2.5 h DaLiA) → joint multi-day × multimodal validation is piecewise by construction.

### Q12. What cannot currently be modeled reliably?

1. **Neuropathic POTS hemodynamics** — engine structure cannot reach the ≥30 bpm criterion (21.2 bpm, flat dose-response); model-adequacy failure, not evidence failure (G-P0-03).
2. **Upright pulse-pressure/ΔSBP pressor response** — 0-D arterial windkessel structurally cannot produce it (−4.0 vs +10 mmHg); needs a pulse-pressure compartment or validated surrogate (G-P1-01).
3. **PEM as a physiological trajectory** — no validating data exist; symptom kernel stands (E2), physiological delayed kernel is E0/E1 (D2, G-P1-06).
4. **Active-stand initial transient** — no muscle pump; the stand protocol is structurally wrong without it (G-P1-08).
5. **Severe ME/CFS** — all parameters are downward extrapolations (G-P1-13).
6. **hEDS mechanism** — etiology unresolved at E0; composition-only with "mechanism unknown" annotation (EVD-EDS-008).
7. **Panic-event magnitudes** — partially null evidence, no ambulatory dataset; keep modest with wide uncertainty (EVD-NEUR-010).
8. **Anything resting on the 23-item must-not-hard-code list as point constants** (POTS BRS gain, subtype weights, comorbidity rates, skin-tone terms, latent factor loadings, autonomic latencies, menstrual effect sizes, 24-h-fast shift…).
9. **Fludrocortisone chronic phase** — schema cannot express phase-dependent perturbations; own citation contradicts the static +500 mL chronically (G-P2-01).
10. **Disease-specific sleep staging accuracy** (healthy-κ only) and **free-living healthy stand-ΔHR tails** (unmeasured at scale).

### Q13. What must remain latent (ground truth only, never a sensor channel)?

(SPEC §0.1 hard-rule table; WEARABLE §d; enforced in the generator.)

Absolute BP (cuffless error ±16 mmHg LoA/drift exceeds OH thresholds; only calibration-anchored *trend* pseudo-channel with error growth, and it can never certify absence of OH — NC11); SV/CO at wrist; SVR; venous pooling volume; cerebral perfusion/CBFv; core temperature at rest/fever; hydration; glucose via any optical channel (CGM only); insulin, ketones, RER, BAT, endothelial stiffness, cytokine levels; absolute BRS (index only); PEM episode labels (ground-truth only, `evidence: E0–E2, no validated detector`); psychological stress as ground truth (valence-/cause-blind arousal only). The **coupling-not-readout rule** is binding: latents modulate observables through documented mechanisms; the engine implements the coupling, never the readout.

### Q14. Minimum viable scientifically defensible model

The smallest system whose outputs could survive the Level 1–4 harness on the §3.6 slice:

1. Corrected 12-state ODE + Hill baroreflex core (exists) **+ G-P0-01/04 fixes** (correct applied parameters).
2. Protocol-conditioned orthostatic event layer (transient/sustained split; tilt-first; healthy tails at protocol rates) — G-P0-09.
3. Structured beat generation: RSA from a real respiration state + Mayer-wave LF + 1/f + ectopy — G-P0-05 minimum subset (respiration + RSA + LF; 1/f and ectopy follow in the same work item).
4. Minimal time layer: virtual-time scheduling + circadian coupling of gains + one sleep/wake state with stage-conditioned vagal/sympathetic modulation (full multi-day PEM scheduling is required only when ME/CFS enters) — G-P0-06 slice-scoped.
5. The hypovolemic mixture branch + graded orthostatic latent + protocol covariates; hyperadrenergic flagged branch optional; neuropathic excluded.
6. KB-driven sensor/artifact layer for the six modalities with state-correlated missingness — G-P1-02 subset.
7. Cohort sampler + manifest with per-record provenance and evidence labels — G-P0-07/08/10 minimal viable (single cohort pair, fixed schema).
8. Validation harness with registered targets, NC battery, and the honest-release sentence — G-P1-10.

Everything else (full comorbidity copula, medication-mask library beyond beta-blocker/steroid, menstrual layer for the healthy-female subset, pacing state) is strongly desired but formally Phase-0-parallel or Phase-1.

### Q15. What must be implemented before dataset generation?

Exactly the Phase-0 list of §2.4 plus the scientific items of §2.3 that feed it — in dependency order: (i) G-P0-01, G-P0-04 (correctness, S); (ii) G-P0-09 + G-P1-08 decision (reference freeze); (iii) G-P0-05, G-P0-06 (realism, the long pole); (iv) G-P0-07, G-P0-08, G-P0-10 (generation + provenance); (v) G-P0-02 (PEM wiring, only because ME/CFS-HM is in the v1 freeze; its channels ship extrapolation-labeled), G-P0-03 (neuropathic resolution or scope-out); (vi) credibility gates G-P1-05, G-P1-10, G-P1-17, G-P1-03, G-P1-11, G-P1-14; (vii) intended-use decision G-P2-16 documented. **Plus one item the gap list treats as a process, stated here as a gate: human L3 review of every KB file whose parameters enter the generated cohort (§6).**

### Q16. What can wait until after the first dataset?

Phase 1 (GAP §Roadmap): ΔSBP pulse-pressure structure (G-P1-01); full sensor wiring beyond the v1 subset (G-P1-02 remainder); Fu-2010 competing branch as a second generative mechanism (G-P1-04); external disease-cohort curation (G-P1-07, schedule-gated anyway); muscle pump (G-P1-08) if v1 ships tilt-only; thermoregulation/sleep-stage/accelerometry full modules (G-P1-09 remainder); adult fever regression retrieval (G-P1-12); severe-tier refinement (G-P1-13); constants retrofit completion (G-P1-15); general trigger semantics (G-P1-16). Phase 2: medication phase schema (G-P2-01), symptom-layer grounding (G-P2-02), factor-structure sensitivity (G-P2-03/05), reliability retrieval (G-P2-04), stacking-rule formalization (G-P2-14), primary-source extraction of secondary-verified classics (G-P2-15), pacing first-class state (G-P2-13), bounded literature tasks (G-P2-20). Phase 3: packaging/CI polish, docs sync, calibration/inference research (G-P2-11, G-P3-06), annual evidence refresh.

### Q17. How will synthetic-to-real utility be demonstrated?

Only through the pre-registered Level-5 transfer matrix (SYNTHETIC_TO_REAL_BENCHMARK §5): for each task T1–T7, the five cells R→R (ceiling), S→S (sanity floor), S→R (the utility claim), R→S (asymmetry diagnostic — markedly worse R→S means synthetic is *easier* than real, triggering trivial-separation investigation), S+R→R (augmentation benefit, ≥2 pp AUC with paired bootstrap CI excluding 0). PASS = S→R within 10% relative of R→R; 10–20% = MARGINAL with domain-adaptation caveats; <80% = FAIL, reported, not spun. All splits participant-level. Negative-control battery NC1–NC12 runs on the same generated data and any NC failure invalidates the release regardless of Level-5 scores. Until the matrix is executed and reported in full, the binding sentence — *"OCPE synthetic data are candidate research artifacts whose utility for any task is unestablished pending the Level-5 benchmark"* — appears in all release materials. For the v1 slice specifically, the load-bearing cells are T1 (orthostatic event detection and ΔHR regression, including the healthy-tail fidelity check that can fail the release independent of AUC) and T6 (phenotype stratification constrained to the 0.75–0.85 band, proxy-validated until restricted cohorts clear).

---

## 5. SHARED-LATENT-AXES ARCHITECTURE (binding) AND ANTI-LAUNDERING RULES

### 5.1 Why this architecture is forced by the evidence

The cross-condition overlap matrix (DISEASE consolidated §10, built from the 14-item candidate nonspecific-mechanism list of INDEPENDENT_REVIEW §3, endorsed as binding) scores 15 mechanism/observable axes across 8 condition columns. **13 of 15 are SHARED (or healthy-core) across ≥2 conditions**; only the POTS Mayer-wave loop-gain/phase alteration and the ME/CFS PEM trigger-dose state approach condition-specificity, and even they sit on shared machinery. The evidence is unambiguous that the dominant disease axes — tonic vagal withdrawal, resting-HR elevation, orthostatic tachycardia, activity suppression, sleep fragmentation, EDA surges, delayed post-exertional flares, skin-temperature shifts, SpO2 sawtooth, medication masks — are *nonspecific systemic physiology*. An engine that encodes them as per-disease signatures would be laundering nonspecificity into biomarkers. The anti-laundering architecture is therefore not a design preference; it is the only evidence-consistent structure.

### 5.2 The ten composable SHARED latents (implemented once in core; condition layers set sampling priors only)

(DISEASE consolidated §10.1, verbatim scope.)

1. **Tonic vagal gain** (vmHRV axis) — one knob; RR-scaling law + respiration/HR/device confounds built in (D15); condition priors: ME/CFS −0.37 SD, LC −10–20% at ~50% penetrance, hEDS −30%, anxiety g≈−0.3–−0.45, inflammation CRP-dose-dependent, T2DM SDNN −6–15 ms.
2. **Systemic inflammation state** — one core (acute impulse + chronic low-grade + flare dynamics, log-severity like LPS dose); disease wrappers (RA/IBD/SLE/Sjögren's/gout/infection/LC tier); low-grade sits *below* the acute-vitals threshold (no vital change ≤0.5 ng/kg LPS).
3. **Deconditioning/fitness axis** — sampled independently of disease severity; no baked causal coupling (cause-vs-consequence unresolved in POTS, ME/CFS, hEDS).
4. **Orthostatic dysregulation axis** — graded ΔHR-liability continuum with protocol-conditioned healthy reference; POTS label = threshold crossing on top; healthy tails per D14.
5. **Sleep-fragmentation axis + AHI-parameterized OSA generator** — one generator, comorbidity branches everywhere (EDS OSA 32% vs 6%, OR 5.3).
6. **Post-exertional recovery kernel** — slowed-recovery (hours; 3–6 h → 9–13 h) as the physiological default for all conditions; delayed symptom kernel (12–48 h) only for PEM-capable personas; speculative delayed physiological second wave E0-off.
7. **Post-acute-infection response layer** — standalone (triphasic RHR, mean 79 d to baseline; 7–14% prolonged-elevation tail); all post-infectious phenotypes compose on it.
8. **Medication gain-mask layer** — beta-blockers, steroids, levodopa, SSRIs, biologics as cross-disease modifiers (beta-blockade caps HR impulse gain ~×0.5; steroids decorrelate CRP-proxy from RHR).
9. **Stress / pain-pressor / hyperventilation CORE modules** — TSST (SAM non-habituating + HPA habituating), cold-pressor bimodal, hypocapnia (+4.4 bpm, MAP −3.5).
10. **Menstrual + circadian modulation** — mandatory healthy core so female disease personas are not misread as flare/infection (NC8).

**Condition-specific machinery (justified as distinct, not shared):** POTS 3-axis subtype mixture with Angeli joint distribution + Fu-2010 competing branch + Mayer-wave gain/phase + fast supine recovery; ME/CFS PEM trigger-dose state + symptom/physiology kernel decoupling + boom-bust autocorrelation + severity latent; LC trajectory classes + incidence modifiers; hEDS as composition only ("mechanism unknown" annotation); neurological injectors (denervation gain, baroreflex-failure gain, GTCS/RBD/tremor/levodopa/anxiety/panic); metabolic personas (GV, CAN, dawn, CGM channel); autoimmune flare wrappers.

### 5.3 Anti-laundering rules (binding on generation and validation)

1. **Separation rule:** any dataset feature whose between-condition effect-size separation is smaller than the within-condition/within-person variance (per the WHOOP group-null, Welltory null, 24-h-HR null, Nelson small-SMD evidence) must be documented as non-discriminating and must not be emitted as a disease signature.
2. **Classifier-cap rule:** ME/CFS single-feature AUROC ≤0.7–0.8; LC discrimination band 0.75–0.85; any phenotype classification AUC >0.95 fails CI as stereotyped. RA-flare/IBD/metabolomic classifier performances (F1 ~0.95, AUROC 94–96% in-sample) are permanently barred as validation targets (NC5).
3. **Background-rate honesty:** synthetic controls carry non-zero background symptom/flare/orthostatic rates (PEM 7%, fatigue 17%, brain fog 4%, OI ~6%; healthy 30-bpm exceedance at protocol rates); disease signals are excess-over-background only.
4. **Within-person semantics:** all disease RHR/HRV effects are deltas from personal baseline; between-person absolute thresholds are device/definition-dependent and never the disease channel.
5. **Negative-control battery** (NC1–NC12, §2.5.3) is part of the release gate, not a reporting nicety; the harness must fail on healthy-only data pushed through disease caps (self-test).
6. **Base-rate coupling:** screening-style metrics are reported with prevalence-adjusted PPV (iRBD lesson: AUC 0.84–0.87 → PPV 3–6% at 1.5% prevalence).
7. **Latent discipline:** the Q13 latent-only list is enforced structurally; no fabricated observable (optical glucose = automatic FAIL, NC10).
8. **Confound presence:** medication masks, menstrual modulation, anxiety tonic layer, and artifact mimics are *present in the data* so that downstream models confront the real confound structure (broken-sensor regimes are mandatory content: POTS tachycardia decouples HR–intensity; pacing invalidates activity–EE links; orthostatic transients violate PRV≈HRV).

---

## 6. EVIDENCE-PROVENANCE GOVERNANCE

### 6.1 Why governance is structural, not documentary

The repo's own history is the justification: 4 of 8 original disease-file DOIs were fabricated or wrong-paper (mecfs.yaml, eds.yaml, autoimmune.yaml, poor_sleep.yaml, heat.yaml, medication.yaml all carry corrected citations; CURRENT_IMPLEMENTATION_MAP §4). Dossier-level citation discipline in Pass 1 was far better (CONTRADICTION_AUDIT Section D: 23 spot-checks, none failed outright), but `EVIDENCE_REGISTRY.yaml` identifiers were copied verbatim — including dossier-flagged unverified ones — so verbatim copying preserves traceability without constituting verification. Every disease KB file still carries "PROPOSED CORRECTION (not yet merged)" and no file anywhere carries a human L3 APPROVED verdict.

### 6.2 The review-tracker mechanics and how decisions map to sidecars

Per ADR-0001 and `tools/review_tracker.py` (CURRENT_IMPLEMENTATION_MAP §1.10): every KB/data file `X.yaml`/`X.md` has a co-located sidecar `X.<ext>.review.yaml` binding `sha256` of the current content to a `review_history` of entries `{review_id, reviewed_at, reviewer{kind: human|ai_agent|validator, identity}, scope, verdict, findings, comments}`. Usage:

- `python3 tools/review_tracker.py record <target> --kind ... --scope ... --verdict ...` — recomputes the hash and appends a review entry; **every decision in this document and the gap analysis that changes a KB file must be followed by a `record` entry whose `comments` cite the governing artifact and gap ID** (e.g., a pots.yaml edit resolving G-P0-04 records `--comments "G-P0-04 normal_value fix per OCPE_RESEARCH_GAP_ANALYSIS / SPEC v1.0 §2.4"`).
- `python3 tools/review_tracker.py history <target>` — chronological reviews + freshness verdict (FRESH if current SHA-256 == recorded, else STALE). Any edit without re-review renders the file STALE.
- `python3 tools/review_tracker.py summary [directory]` — fleet-level FRESH/STALE/UNREVIEWED table.
- `tools/validate_kb.py --record` auto-appends `validator`-kind PASSED entries after a clean run.

Known tool gaps (G-P3-04, additive): findings not settable via CLI, no confidence/commit/orcid fields, and — critically — **no gatekeeping hook** (ADR-0001's enforcement paragraph is unimplemented).

### 6.3 Provenance gating for dataset generation (required, G-P1-05)

1. **The dataset builder refuses any KB file whose sidecar is missing, STALE, or lacks tier/E-level labels** — provenance gating must be code, given the fabricated-DOI history (hash-mismatch tamper test required).
2. **Human L3 review is a release gate:** every KB file whose parameters enter a generated cohort must carry a human `APPROVED` entry at L3 (the ADR's 3-tier model: L1 schema/validator, L2 adversarial/AI-agent, L3 human domain review). Current state: zero files qualify. The review-freshness gate joins pytest and validate_kb.py in CI (G-P3-01).
3. **Per-record provenance in the manifest** (SPEC §4): applied params with `{tier, registry_refs, canonical|experimental}`, code/KB SHA-256, registry version + SHA-256, seed, mode, and `honesty_flags` (e.g., `neuropathic_pots_unvalidated_xfail`, `pem_physiology_speculative`). Tier-D inert by default; experimental draws labeled `mode: EXPERIMENTAL`; no E0/E1 value in canonical mode (audit CI rule, G-P0-10).
4. **Single-source and banned-field lint** (G-P1-14): parameters derived from Moore 2023, van Campen series, RA Forecast, Sports Med 2026 carry `single_source: true`; F1/AUC emission as validated truth is lint-banned.

### 6.4 Registry DOI re-verification — Pass 3 (standing obligation)

The registry's 143 claims carry DOIs/PMIDs copied verbatim from dossiers, including identifiers dossiers flagged as unverified (e.g., METABOLIC TEF DOI; seizure-detection primaries Poh 2012/Onorati/Regalia "not yet pulled"; Breier GIP; Fu 2010 exact SV/CO percentages; Jacob 2000 spillover table; Webber & Macdonald 1994; Keys; Westerterp). **Pass 3 = systematic identifier re-verification of the full registry** (existence + numeric claim match), prioritized by: (a) any identifier backing an implementable-now parameter (25 items), (b) the secondary-verified classics list (G-P2-15), (c) the remainder. No number whose identifier fails re-verification may remain in the `implementable_now` tier; it drops to provisional-with-uncertainty pending primary extraction. The 23 already-verified pivotal citations (CONTRADICTION_AUDIT Section D + INDEPENDENT_REVIEW spot-checks) are exempt from re-verification but their verification entries should be recorded as sidecar/audit references.

---

## 7. TRACEABILITY APPENDIX

### 7.1 The navigation chain

An engineer traces any element of the dataset through one canonical path:

```javascript
claim_id (EVD-XXX-NNN)
  → EVIDENCE_REGISTRY.yaml        : full claim text, normalized E-grade, verbatim dossier grade,
                                    source/DOI, distribution, sample size, ratings, contradictions
  → audit disposition             : EVIDENCE_AUDIT_NOTES (downgrades, must-not-hard-code) ·
                                    CONTRADICTION_AUDIT (A/B/C/E verdicts) ·
                                    DISEASE consolidated §1 (D1–D22 binding resolutions)
  → PARAMETER_SPECIFICATION.yaml  : sampling rule (point|distribution|mixture|flagged-speculative),
                                    bounds, population/condition dependence, equation, tier, validation
  → PHYSIOLOGICAL_RELATIONSHIPS.yaml : functional form / kernel / coupling the parameter enters
  → EVENT_PROTOCOLS.yaml          : the protocol context with expected phase responses and covariates
  → engine / sensor layer         : repo symbol or NEW symbol; observable channels + artifact model
                                    (SPEC §2–§3); latent-only discipline (SPEC §0.1)
  → OCPE_DATASET_SPECIFICATION.md : schema field, sampling policy, metadata/provenance fields
  → SYNTHETIC_TO_REAL_BENCHMARK.md: which Level 1–5 checks gate this element, with tolerances
  → manifest of a generated record: evidence_version, kb_sha256, claim_ids per channel, honesty_flags
```

Reverse navigation (audit direction): a suspicious value in a generated record → manifest `parameter_draw_id` + `perturbations_applied[].registry_refs` → registry claim → `source`/`doi` → dossier section → audit verdict. Any link that terminates in an uncited constant is a G-P1-15 defect by definition.

### 7.2 Worked end-to-end example: POTS hypovolemic blood volume → orthostatic ΔHR

1. **Claim.** `EVD-POTS-004` (registry): "Many POTS patients have true hypovolemia… total blood volume deficit 689±270 mL vs 228±353 mL" — Raj 2005 (Circulation 111:1574-82), n=15/14; supporting: Fu 2010 (60 vs 71 mL/kg), Kulapatana 2025 CO-rebreathing (−13.92±10.38%, r=−0.608 with upright HR in POTS only). Normalized **E4**; ratings: measurement_quality high, replication moderate, quantitative_strength high; `wearable_modality: none (latent)`.
2. **Audit disposition.** CONTRADICTION Target 3: **(A) CONFIRMED** direction/magnitude class (triangulated, 3 methods) + **(E)** heterogeneity real — Kulapatana's ±10.38% SD and Angeli's 44.9% hypovolemic fraction imply a volume-normal minority; Raj's absolute mL stays out of the generative prior (weight/sex-dependent; use mL/kg or % deficit). Must-not-hard-code list item: mixture, not point value.
3. **Parameter.** `PARAMETER_SPECIFICATION.yaml → POTS_blood_volume_deficit`: type **mixture** — hypovolemic branch weight 0.40–0.50, deficit ~ N(−0.14, 0.10); volume-normal branch weight 0.50–0.60, deficit ~ N(0, 0.05); bounds [−0.35, 0.1]; equation `TotalVol_persona = TotalVol_healthy × (1 + deficit)`; evidence_level E4; implementation note: "REPO MISMATCH RESOLUTION: replace canonical TotalVol=3500 (Geddes in-silico, ~1.5× measured) with this mixture; keep 3500 only as an extreme-tail scenario sample" (binding resolution; closes G-P1-03 at spec level, engine enforcement pending).
4. **Relationship.** The parameter enters **REL-HR-SV-COMPENSATION** (E3): blood volume → preload/SV (upright SV −23±5% healthy; POTS resting SV 69±3 vs 85±7 mL, Fu 2010; upright CO decreased in every POTS patient, n=58 Stewart 2018) → compensatory HR rise defending CO/MAP — "HR must NOT be driven independently of SV/preload in orthostatic scenarios." It also conditions **REL-VENOUS-POOLING-REFILL** and the sustained phase of **REL-ORTHOSTATIC-TIMECOURSE**.
5. **Event.** `EVENT_PROTOCOLS.yaml → EV-head-up-tilt` / `EV-active-stand`: expected_response phases — initial BP dip nadir ~10 s, recovery 20–30 s; sustained healthy ΔHR protocol-conditioned (casual stand N(+12,5), <5% >30 bpm; lab stand +23–26, ~10–33% exceed; tilt-10 min +34±8, ~60%); condition delta `pots`: ΔHR rises over 2–5 min, stand 44±4/50±4 (5/10 min), HUT 49±4/55±5/62±4, ≥30 sustained (≥40 ages 12–19), AM +8–10 bpm bias. Protocol covariates (supine-rest duration, fasting, time of day) are mandatory record fields.
6. **Engine + signals.** Engine symbol: `TotalVol` perturbation on the 12-state ODE (today: `diseases/pots.yaml hypovolemic_pots` 4500→3500 — to be replaced by the mixture draw); the engine's venous compartments absorb the volume change at steady-state init; baroreflex loops produce the compensatory tachycardia (simulation-verified today at 34.6 bpm sustained for the extreme branch). Observables: ECG-strap RR/HR and wrist-PPG HR with the artifact model active (motion at transition; PRV≠HRV during the transient, ICC ~0.5–0.7); IMU posture transition detection. **Latent-only:** absolute BP, SV/CO, the pooling volume itself (SPEC §0.1) — the record carries them in `ground_truth` only; no sensor channel may read them out. Manifest: `perturbations_applied: [{id: pots_hypovolemic_volume_deficit, tier: C→(post-fix human-anchored mixture), registry_refs: [EVD-POTS-004], mode: canonical}]`.
7. **Validation gates.** Level 2.1 tilt battery (ΔHR time course in band; recovery −23%/−28%/−29% at 20 s/1 min/2 min per EVD-POTS-012); Level 3.1 targets (HUTT patient-minus-control +19.88 bpm [15.24–24.52], EVD-POTS-011 E4; subtype joint distribution vs Angeli; hypovolemic-branch deficit moments −12..−15%; ΔHR–BV negative correlation reproduced per the claim's own `validation_strategy`); Level 4 PRCP W1 ≤ 3 bpm on healthy ΔHR + EUROBAVAR proxy; Level 5 T1 (ΔHR regression S→R MAE within 15% of R→R; healthy-tail fidelity check) and T6 (band-capped stratification). Negative controls engaged: NC2 (band), NC11 (no BP channel clean enough to exclude OH).

The same chain applies identically to any other element — e.g., orthostatic ΔHR itself: `EVD-POTS-001/005 + EVD-HLTH-004 → D14 + CONTRADICTION Target 1 → orthostatic_protocol_deltas parameter → REL-ORTHOSTATIC-TIMECOURSE → EV-active-stand/EV-head-up-tilt/EV-nasa-lean/EV-prolonged-standing → PPG/ECG HR + IMU → SPEC §5.4 table → Level 2.1/3.1 + T1 healthy-tail gate`.

---

## 8. VERSION FOOTER

### 8.1 Evidence version

- **Evidence base:** OCPE research swarm Pass 1 (discovery) + Pass 2 (adversarial audit, contradiction audit, independent review) + Pass 3 model-translation artifacts; normalized on the standard E0–E5 scale per `EVIDENCE_REGISTRY.yaml` (Pass 2). **Registry identifier re-verification (Pass 3 proper) is pending** — see §6.4; until it completes, no registry number is locked.
- **This document:** OCPE_EVIDENCE_AND_SIMULATION_SPECIFICATION v1.0. It supersedes no artifact; it binds their joint interpretation. Conflicts resolve in favor of: binding downgrades (D1–D22) > audit notes/contradiction audit > normalized registry > dossier text > repo KB (the repo is the least-trusted layer pending L3 review).

### 8.2 Artifact inventory

| File | Contents | Scale |
| --- | --- | --- |
| CURRENT_IMPLEMENTATION_MAP.md | Repo source audit (file-by-file): what exists/partial/missing/unsupported/sound; verified test and validator state | 69 files audited; 67 tests + 2 strict-xfail verified |
| CURRENT_PHENOTYPE_SCOPE.md | All 10 phenotype IDs + healthy reference; canonical vs experimental semantics; per-phenotype evidence and gaps; scope summary table | 10 phenotypes, 7 KB disease files |
| HEALTHY_PHYSIOLOGY_EVIDENCE.md | Healthy reference: resting distributions, circadian, orthostatic, exercise, meal, sleep, environmental stressors, coupling constraints | registry EVD-HLTH-001..010 |
| AUTONOMIC_PHYSIOLOGY_EVIDENCE.md | Baroreflex/autonomic parameterization: tones, gains, latencies, orthostatic reflex arc, HRV proxy discipline, model-ready master table | EVD-AUTN-001..010 |
| DISEASE_EVIDENCE_POTS.md / _MECFS.md / _LONGCOVID.md / _EDS.md / _AUTOIMMUNE.md | Per-condition Pass-1 dossiers with null/contradiction registers (source of record for full claim text) | EVD-POTS-001..020; EVD-MECFS-001..014; EVD-LCOV-001..015; EVD-EDS-001..008; EVD-AUTO-001..011 |
| METABOLIC_PHYSIOLOGY_EVIDENCE.md | Glucose/insulin, postprandial, EE, substrate, fasting, sleep–metabolism, thermoregulation, IR→T2DM/CAN; observability master table | EVD-METB-001..014 |
| NEUROLOGICAL_PHYSIOLOGY_EVIDENCE.md | PD/MSA/PAF, epilepsy, migraine, anxiety/panic, OSA, stress CORE, hyperventilation; CORE-vs-perturbation allocation | EVD-NEUR-001..013 |
| WEARABLE_OBSERVABILITY_EVIDENCE.md | Mechanism→observable chains; demonstrated-vs-claimed; latent-only list; design rules | metrology scale (normalized in registry) |
| SENSOR_MODEL_EVIDENCE.md | Per-modality sensor physics and validation metrics; 16-class artifact table; state-dependent degradation; simulator defaults | EVD-SENS-001..009 |
| POPULATION_MODEL_EVIDENCE.md | Marginals, correlation structure (with unevidenced cells marked), variance decomposition, severity/comorbidity distributions, latent architecture, sampling guidance | EVD-POP-001..008 |
| TEMPORAL_MODEL_EVIDENCE.md | Multi-timescale evidence (beat to weekly), noise models, identifiability, six-layer architecture | EVD-TEMP-001..011 (inverted scale, normalized) |
| VALIDATION_DATASETS.md | Verified external dataset inventory with access tiers; honest coverage gaps; priority ladder | 30+ datasets; 8 documented gaps |
| EVIDENCE_AUDIT_NOTES.md | E-scale structural finding; 20-item downgrade list; fabricated-precision flags; 23-item must-not-hard-code list; 17 coverage gaps; repo tier audit | binding on interpretation |
| CONTRADICTION_AUDIT.md | 12 adversarial targets; 23 citation verifications; confirmed/weakened/refuted sections; 12-item uncertainty list | binding (D-series source) |
| INDEPENDENT_REVIEW_PASS2.md | 9-criterion independent verdicts; 11-row inconsistency table; 14-item nonspecific-mechanism list; prioritized P0–P2 revisions | binding (reviewer authority) |
| DISEASE_PHYSIOLOGY_EVIDENCE.md | Consolidated conditions; D1–D22 binding downgrades; healthy anchor; overlap matrix (15 mechanisms); shared-latent architecture §10.1 | 143-claim integration layer |
| EVIDENCE_REGISTRY.yaml | Normalized claim registry | **143 claims** |
| PHYSIOLOGICAL_RELATIONSHIPS.yaml | Quantitative relationships with functional forms | **26 relationships** |
| PARAMETER_SPECIFICATION.yaml | Generation-ready parameters with sampling rules | **58 parameters (25 implementable / 22 provisional / 11 research)** |
| EVENT_PROTOCOLS.yaml | Protocol-conditioned event models | **16 protocols** |
| OCPE_DATASET_SPECIFICATION.md | Hard rules, ground-truth schema, sensor layer, metadata, population design, temporal design, provenance hooks | spec v0.1 |
| SYNTHETIC_TO_REAL_BENCHMARK.md | 5-level acceptance gate; 12 negative controls; T1–T7 transfer matrix; exclusion declarations | benchmark v0.1 |
| OCPE_RESEARCH_GAP_ANALYSIS.md | Integrated gap register and phased roadmap | **55 gaps (10 P0 / 17 P1 / 22 P2 / 6 P3)** |

### 8.3 Known limitations of this synthesis

1. **Registry identifiers are verbatim-copied, not re-verified** (Pass 3 pending, §6.4); four dossier-flagged unverified DOIs and the secondary-verified classics list remain open.
2. **Engine-side state is as of the Pass-1/2 repo audit** (67 passed / 2 strict-xfail / 21 FRESH sidecars at clone); any concurrent repo change invalidates §2.2's file:line citations, not its conclusions.
3. **The first-slice recommendation is proxy-limited by data availability**, not by preference: no open POTS cohort exists; the Zenodo 20327114 request is pending and is a schedule risk, as are RECOVER/All-of-Us/MESA access paths.
4. **Several v1-load-bearing numbers are single-source** (Moore PEM recovery; van Campen CBF; RA Forecast offsets; Sports Med 2026 recovery kernel) and carry `single_source` flags; their failure under replication would force parameter, not architecture, changes.
5. **The latent factor structure is theory-driven (E0)**; the ±50% loading sampling and copula sensitivity analysis are the containment strategy, not a cure.
6. **This document makes no utility claim** for any synthetic data; the binding sentence of §4.Q17 applies to this document's own downstream use.
7. **Human L3 review is incomplete (zero files)**; this document's scientific decisions are swarm-internal until that gate clears.

*End of OCPE Evidence and Simulation Specification v1.0.*