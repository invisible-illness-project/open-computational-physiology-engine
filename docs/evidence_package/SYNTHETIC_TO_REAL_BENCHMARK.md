# OCPE — Synthetic-to-Real Benchmark & Validation Harness

**Version:** 0.1. **Companion:** OCPE_DATASET_SPECIFICATION.md (all `EVD-*` IDs reference EVIDENCE_REGISTRY.yaml normalized grades).
**Status discipline:** this document defines the *acceptance gate*. **No utility claim for OCPE synthetic data is made until the Level-5 matrix in §5 has been executed and reported**, including failures. Prior levels are necessary but not sufficient.
**Pre-registration rule:** tolerance bands below are fixed *before* generation runs; post-hoc widening is forbidden and logged as a harness failure.

---

## LEVEL 1 — MATHEMATICAL VALIDITY (unit tests of the generator itself)

| # | Test | Acceptance criterion | Anchor |
|---|---|---|---|
| 1.1 | Equation unit tests | Each ODE/algebraic RHS evaluated against hand-computed fixtures to rtol ≤1e-8; Hill targets, softplus valves, hydrostatic gate, IPFM integrate-to-threshold | CURRENT_IMPLEMENTATION_MAP test conventions |
| 1.2 | Conservation checks | Blood-volume mass conservation \|ΣV_i − TotalVol\| < 1e-6·mL per integration step (non-negativity clamps inactive in nominal regimes); energy bookkeeping for thermal layer (skin = core-coupled setpoint + circadian + vasomotor + ambient leak) | Geddes-scale ODE (EVD-TEMP-003 context) |
| 1.3 | Numerical integration | Radau dt=0.01 s, rtol=1e-6/atol=1e-8 reference vs halved-step rerun: HR trajectory max deviation <0.01 bpm | engine precedent |
| 1.4 | **Identifiability guards** | ODE parameters are **population priors with documented uncertainty, never per-subject estimates**. Harness test: attempt to recover each internal parameter from the simulator's own *observable* output under realistic noise (PPG-HR LoA ±7 bpm, day/night dropout). Any parameter not recoverable (structural or practical) must be labeled `non_identifiable` and fixed to literature distributions — enforced by CI. Structural unidentifiability under pressure-only or volume-only observation is documented (EVD-TEMP-010, E4); baroreflex τ_h has infinitely many solutions in a priori analysis; ~20+ → ~5–6 estimable parameters in Olufsen-group workflows | EVD-TEMP-010 |
| 1.5 | Determinism / reproducibility | Same seed → bit-identical output; seed sweep produces correct inter-record variance decomposition (between/within-person split matches §5.2 targets within Monte-Carlo tolerance) | engine seeded-determinism precedent |
| 1.6 | Honesty gating | Tier-D parameters inert in canonical mode (experimental-only phenotypes bit-identical to healthy in canonical mode); every emitted parameter carries E-level + provenance tag; generation aborts on missing tag | EVIDENCE_AUDIT_NOTES §e CI rule |
| 1.7 | Scale-harmonization machine check | Generator rejects any parameter file whose evidence scale definition ≠ standard E0–E5 (the three-scale defect must never recur) | EVIDENCE_AUDIT_NOTES §0 action item |

## LEVEL 2 — PHYSIOLOGICAL PLAUSIBILITY (trajectory battery per protocol + timescale signatures)

### 2.1 Event-protocol trajectory battery (expected ranges from dossiers)
| Protocol | Trajectory checks (must all fall in band) | Evidence |
|---|---|---|
| Active stand (lab, long pre-rest) | Initial dip nadir ~10 s, recovery 20–30 s; sustained ΔHR +10–25 bpm healthy (protocol-conditioned table, SPEC §5.4); POTS ≥30 bpm sustained without SBP drop ≥20 mmHg | EVD-HLTH-004, EVD-POTS-001 |
| Head-up tilt 60–70°, 10 min | Healthy +34±8 bpm; POTS meta +19.88 bpm (95% CI 15.24–24.52) after HUTT vs controls; tilt > stand ΔHR at every time point; ΔHR keeps rising past 10 min in POTS | EVD-POTS-011 (E4 post-downgrade), EVD-POTS-005 |
| Tilt/stand recovery (lie down) | From max HR 109±16.9 bpm: −23% at 20 s, −28% at 1 min, −29% at 2 min (POTS recovery profile) | EVD-POTS-012 |
| Graded exercise | HR on-kinetics mono-exponential τ 10–45 s; linear HR–VO2 slope; off-kinetics bi-exponential (τ_fast 15–30 s, τ_slow 2–4 min); HRR 1-min 44±11 bpm young, −3.6 bpm/20 y aging; abnormal <12 bpm | EVD-TEMP-004, EVD-HLTH-005, CARDIA |
| Mixed meal | HR +6±3 bpm (up to +10–20 large/high-carb), peak 30–60 min, decay 2–4 h; HF-HRV dip 1–2 h; LF/HF 1.78→2.50–2.68 | EVD-METB-005, TEMPORAL §3 |
| TSST-class stressor | HR/SBP/cortisol elevation with published effect sizes; responder/non-responder mixture; EDA surge per §3 EDA error model | EVD-NEUR-011, WESAD |
| Sleep night | Nocturnal HR dip 10–20%; HRV increase; NREM vagal predominance, REM sympathetic surge; distal skin temp rise at sleep onset | EVD-HLTH-007, EVD-TEMP-006 |
| 2-day CPET (ME/CFS/LC) | Small mean day-2 capacity decrement 0–7% (wide CI, threshold/workload-weighted) + explicit effort-coupling term + responder subgroup 20–40%; **universal decrement is a FAILED check** (Natelson null: decline less frequent in patients 22% than controls 33%) | CONTRADICTION Target 4, EVD-MECFS-007 |
| PEM episode | Symptom kernel: onset 12–48 h, peak 24–48 h, recovery right-skewed (mean 12.7 d, range 1–64 d; controls 2.1±0.2 d); physiological channels show slowed same-day recovery (healthy 3–6 h → patient 9–13 h post-VT1); delayed physiological second wave only under EXPERIMENTAL flag | EVD-MECFS-008/009, CONTRADICTION Target 5 |
| Infection episode | Multiphasic RHR elevation, mean 79 d to baseline post-COVID; fever-HR age-graded slope 7–13 bpm/°C | EVD-LCOV-010, EVD-AUTO-003 |
| RA flare | Within-person RHR +5.0 bpm, mean HR +6.0, HRV mesor reduction (21.5 vs 28.7 ms); detectable-window claims NOT validated (see §3 negative controls) | EVD-AUTO-005 |

### 2.2 Timescale-specific statistical signatures (whole-record level)
| Signature | Target | Evidence |
|---|---|---|
| DFA-α1 (4–16 beats) | ≈1.0 at rest (0.7–1.2); declines with exercise intensity; α1=0.5 (white noise) is FAIL | EVD-TEMP-001 (E4) |
| RR-interval distribution | Inverse-Gaussian, not Gaussian (KS test; time-rescaling theorem for point-process check) | EVD-TEMP-002 |
| Spectral peaks | 0.1 Hz Mayer (LF) + respiratory 0.15–0.4 Hz (HF/RSA); LF/HF ~1–2 seated rest, state-dependent; **RSA amplitude must scale with respiration rate/depth at constant vagal state** (confound built-in, Target 6) | EVD-TEMP-003, TEMPORAL §1 |
| Post-tilt 0.1 Hz oscillation power | Small healthy; amplified in POTS (feedback-delay emergence, not injected oscillator) | EVD-TEMP-003 (Geddes) |
| Multiscale entropy | Synthetic must be distinguishable from *shuffled* but NOT from real (CinC 2002 criterion — the realism bar is fractal/complexity statistics, not waveform cosmetics) | TEMPORAL §1 (Costa) |
| Poincaré | Comet-shaped cluster, SD1 ≪ SD2 | TEMPORAL §1 |
| Circadian cosinor fits | Significant 24-h component; HR acrophase afternoon, nadir ~03:00–05:00; skin-temp nadir ~2 h before wake after de-masking; second harmonic improves fit | EVD-TEMP-006 |
| Weekly lnRMSSD CV | 3–10% (2.8% stable baseline; ~8% perturbed); RHR day-to-day SD ~3 bpm (CV ~4.6%) | EVD-TEMP-007, EVD-POP-004 |
| Menstrual biphasic pattern | Detectable by standard cycle-detection in ~82% of simulated tracked cycles (real-data falsification target); luteal T_skin +0.2–0.3 °C ∧ RHR +2–5 bpm ∧ RMSSD −~10% anti-correlated | EVD-TEMP-008 |
| Training block | RMSSD weekly-mean rise SMD ~0.6–0.9 over 8–12 wk; RHR −2 to −6 bpm | EVD-TEMP-009 |

## LEVEL 3 — CLINICAL PLAUSIBILITY (phenotype distribution agreement with independent literature)

### 3.1 Positive targets (synthetic distributions must match these published values within pre-registered tolerance)
| Check | Published target | Source / registry |
|---|---|---|
| POTS ΔHR≥30 rate, 10-min stand, clinic protocol | POTS cohorts ~all meet criterion by definition (referral ascertainment); healthy exceedance 10–33% by protocol (stand-10 min specificity 67%, NASA lean 33%, tilt-10 min 60%) | Plash 2013 / Lee 2020 (CONTRADICTION Target 1, VERIFIED) |
| POTS HUTT ΔHR vs controls | +19.88 bpm (95% CI 15.24–24.52) meta-analytic patient-minus-control | EVD-POTS-011 (E4) |
| POTS subtype joint distribution | hyperadrenergic 75.0%, hypovolemic 44.9%, neuropathic 37.8%; 41.7% dual, 11.4% triple, 6.8% none (sampled with E0-weights caveat, referral-bias flag) | EVD-POTS-003 (Angeli 2024, VERIFIED) |
| POTS blood-volume deficit | hypovolemic branch −14±10% (mixture; volume-normal branch exists) | EVD-POTS-004, CONTRADICTION Target 3 |
| POTS demographics | female 85–94%; onset mode 14 y, median 17 (IQR 13–28); ~25% disabled | EVD-POP-006 |
| POTS resting HR | clinic +10–20 bpm BUT real-world wearable +~3 bpm with near-complete overlap — **cohort-frame-dependent, both generatable** | EVD-POTS-014 (E3 post-downgrade) |
| ME/CFS steps/day by severity | mild 8,235±1,004; moderate 5,195±1,231; severe 2,031±824; %predicted VO2 90/64/48 | EVD-MECFS-002 (single-clinic tag) |
| ME/CFS resting HR | +4.14 bpm (95% CI ±1.30) — **below the within-person day-to-day RHR noise floor (~5 bpm); group-level only** | EVD-MECFS-003 (E4 post-downgrade) |
| ME/CFS resting HRV | HF SMD −0.34, RMSSD SMD −0.37, LF/HF +0.20 NS — small effects, high heterogeneity | EVD-MECFS-004 (E4 post-downgrade) |
| ME/CFS activity pattern | mean 5,701±2,670 steps/d with boom-bust day-to-day variability | EVD-MECFS-011 |
| ME/CFS PEM prevalence/recovery | PEM ≥24 h in 84%; >5 d recovery in 60%; judged-recovery mean 12.7±1.2 d (range 1–64) vs controls 2.1±0.2 d | EVD-MECFS-008/009 (mean, not median) |
| ME/CFS sleep | TIB +26.6 min, latency +7.2 min (meta, 20 studies); TST null — do NOT generate large TST differences | EVD-MECFS-012 (E4 post-downgrade) |
| Long COVID PEM contrast | 28% vs 7% uninfected, aOR 5.2 (3.9–6.8) | EVD-LCOV-001 (RECOVER n=9,764) |
| Long COVID HRV/HR | SDNN −15–25%; resting HR +5–7 bpm; RMSSD/LF-HF inconsistent — do not force | EVD-LCOV-005 |
| Long COVID chronotropic incompetence | CI in 30% vs 5% (OR 17.6); CI subgroup peak HR −49 bpm | EVD-LCOV-007 (LIINC n=60) |
| hEDS resting autonomics | HR 87.3±11.6 vs 75.2±9.8; RMSSD 20.7±6.9 vs 28.7 — direction replicated, small-n, pre-2017 contamination flag | EVD-EDS-002 (E4 borderline) |
| RA flare wearable offsets | RHR +5.0 bpm, mean HR +6.0, night-HR elevation, steps lower; HRV mesor 21.5 vs 28.7 ms | EVD-AUTO-005 (marginal means only) |
| T2DM resting autonomics | resting tachycardia + globally reduced HRV scaling with duration (cross-sectional only, E2) | EVD-METB-014 |
| OSA cyclical pattern | 4-phase HR/SpO2 sawtooth parameterized by AHI | EVD-NEUR-012 |
| iRBD actigraphy | sleep-only movement model AUC 0.838–0.865 (multicenter, 3 devices) — NOT 0.92–0.95 single-center figures | EVD-NEUR-004, CONTRADICTION Target 9 |
| Anxiety | tonic vmHRV reduction g≈−0.3–−0.45, NOT reactivity shift | EVD-NEUR-009 |

### 3.2 Negative controls (the data must NOT show these — unified battery per INDEPENDENT_REVIEW P1-8)
| # | Negative control | Rationale / source |
|---|---|---|
| NC1 | **LF/HF must not behave as a sympathetic index**: LF/HF changes must be uncorrelated-or-miscorrelated with true sympathetic latent in tilt/stress maneuvers (Billman critique is consensus) | EVD-AUTN-006 |
| NC2 | **No trivial classifiability**: phenotype classification AUC must land in ~0.75–0.85 band; >0.95 = FAIL (over-stereotyped); long-COVID ML AUC 0.951 literature figure is an overfit negative example | EVD-LCOV-013; reviewer Criterion 1 |
| NC3 | **No cytokine-specific HRV signatures**: TNF-α vs IL-6 vs CRP must be indistinguishable at the HRV channel (TNF null within Williams meta); inflammation → HRV link is small (|r|≈0.1) and non-specific | EVD-AUTO-002; reviewer Criterion 1 |
| NC4 | **SpO2 null for IBD/inflammatory flares**: no flare-correlated SpO2 signal may emerge | AUTOIMMUNE dossier null; reviewer P1-8 |
| NC5 | **RA-flare/long-COVID/metabolomic classifier ceilings**: never emit F1≈0.95 / AUC≈0.95–1.00 performance (within-subject imbalanced-data artifacts); flare *predictability* is unproven | EVD-AUTO-005 caveat; EVD-MECFS-013 |
| NC6 | **Panic vs seizure confusion**: EDA/HR panic surges (modest, partially null — only 3/8 ambulatory attacks beyond activity) must be confusable with ictal autonomic surges at the wearable channel | EVD-NEUR-010/008; reviewer P1-8 |
| NC7 | **No PEM detector channel**: no derived metric may track ground-truth PEM labels with usable accuracy (AUC target ≈ chance–0.6); activity-matching must abolish apparent PEM group differences | EVD-MECFS-010; WEARABLE S2 |
| NC8 | **Menstrual cycle not misread as flare/infection**: luteal RHR +2–5 bpm / temp +0.2–0.3 °C present in healthy females so illness detectors see the confound | EVD-TEMP-008; reviewer §3.12 |
| NC9 | **2-day CPET decrement not patient-specific**: healthy controls must show ≥1-unit day-2 declines at ≥ patient rate (33% vs 22%) | CONTRADICTION Target 4 (Natelson) |
| NC10 | **Optical glucose channel absent**: any glucose-reading trace from PPG/EDA = automatic FAIL | EVD-METB-004 |
| NC11 | **Cuffless BP cannot certify no-OH**: POTS records must never carry a BP channel clean enough to exclude orthostatic hypotension | WEARABLE C3 rule |
| NC12 | **Sleep staging in disease cohorts capped at healthy κ**: no disease-specific staging accuracy above healthy κ 0.37–0.65 may appear | AUDIT gap 17 |

## LEVEL 4 — SIGNAL-LEVEL COMPARISON vs REAL DATASETS

Datasets, access tiers, and scope per VALIDATION_DATASETS.md (priority ladder §13). Metrics: per-channel distributional distances + artifact rates + feature-level agreement, all with pre-registered tolerances.

| Real dataset (access) | What it validates | Concrete metrics & tolerances |
|---|---|---|
| **PRCP / PhysioNet (OPEN)** — 10 healthy, ECG+Finapres 250 Hz, slow/rapid tilt + stand-up | Orthostatic ground truth, healthy arm | ΔHR/ΔBP magnitude & time course: Wasserstein distance on ΔHR distributions W1 ≤ 3 bpm; transient-vs-steady-state split; RR–SBP coupling (cross-correlation lag 0±1 beat); tilt-speed dependence present |
| **PPG-DaLiA (CC BY 4.0)** — 15 subjects, E4 wrist + RespiBAN chest, 8 labeled activities, ~2.5 h | Full wearable stack vs chest-ECG truth | PPG-HR error vs activity class: match per-activity MAE/LoA bands (rest σ≈3.5 bpm; walking worst; cycling best); motion-artifact severity distribution per activity; EDA/temp wrist dynamics (correlation of event-locked responses ≥0.8); cross-device synchrony lag distribution |
| **WESAD (CC BY 4.0)** — 15 subjects, TSST, chest+wrist EDA/ECG/PPG/resp/temp | Autonomic stress physiology | Baseline-vs-stress effect sizes within ±25% of WESAD's per modality; EDA SCR rate/latency/amplitude distributions (KS p>0.01 after multiple-comparison control); wrist-vs-chest EDA attenuation ratio |
| **EUROBAVAR (OPEN)** — 21 subjects supine/standing ECG+beat-to-beat BP, incl. 2 baroreflex-impaired | Baroreflex working-point shift; **labeled as reflex-gain validation ONLY — not a POTS cohort** (reviewer Criterion 8) | Supine→standing Δ(HR, LF/HF, BRS-index) direction+magnitude; impaired-subject attenuation reproduced qualitatively; no claim beyond reflex gain |
| **Autonomic Aging, Jena (OPEN)** — 1,121 healthy, ECG 1000 Hz + CNAP, supine | Population priors, healthy envelope | Age/sex-conditioned HR, RMSSD/SDNN, BP-variability percentile overlap: synthetic percentiles within ±10% of empirical per decade×sex bin; healthy cohort must sit inside envelope BEFORE disease perturbation judged |
| **BUT PPG (OPEN)** | Quality-flag / missingness sub-model | Fraction of 10-s segments unusable at rest vs motion within ±5 pp of empirical; artifact morphology class balance |
| **CapnoBase / BIDMC (OPEN)** | Respiratory modulation depth on PPG/ECG | RIIV/RIAV/RIFV modulation depths; PPG-RR MAE in 0.1–2.0 brpm clean band |
| **TMET-Málaga (OPEN)** — 992 maximal tests | Exercise dose-response | HR–VO2 slope, on-kinetics τ distribution (10–45 s), HRR distribution vs CARDIA norms |
| **CAPTURE-24 (CC BY 4.0)** | Free-living IMU realism | Activity-type distribution, intensity (mg) marginals, non-wear patterns, day/night structure |
| **Icentia11k (CC BY-NC-SA)** | Multi-day ECG nonstationarity, ectopy burdens | Day/night HR patterns; ectopy burden distribution (40–75% ≥1 PVC/24 h); **license restricts derivative release — flag in manifest** |
| **MESA / SHHS (REGISTERED, DUA)** | Multi-day actigraphy + nocturnal physiology | Sleep-wake distributions, night-to-night variability (within-person SD median 0:30), nocturnal HR/SpO2 marginals |
| **Artifact-label sets (CSL oximetry labels; ScientISST MOVE; TROIKA)** | Artifact realism floor | Artifact-class conditional distributions match labeled rates; worst-case running PPG usability reproduced (TROIKA lower bound) |
| **Free-living usability statistics (Väliaho/Böttcher, published)** | Artifact/observation layer (reviewer Criterion 8.5 — cheap, high value) | Daytime PPG usable 30–60%, night 65–75%; streaming loss ≤49%; on-body 80–99.7% — synthetic rates within ±5 pp |

**Piecewise-validation disclosure (VALIDATION_DATASETS §12.7):** no multi-day synchronized full-stack real dataset exists (max ~2.5 h DaLiA). Multi-day statistics are validated from MESA/All-of-Us-tier aggregates; multimodal coupling from DaLiA/WESAD. The joint claim is validated piecewise and labeled as such.

## LEVEL 5 — SYNTHETIC-TO-REAL BENCHMARK MATRIX

### 5.1 Transfer cells
For every task: **R→R** (train real / test real, cross-validated) is the ceiling; **S→S** sanity floor; **S→R** the utility claim; **R→S** diagnostic asymmetry check; **S+R→R** augmentation benefit. All splits at **participant level** (no day-level leakage). Baselines per task: (i) majority/null; (ii) logistic regression on hand-crafted features; (iii) gradient-boosted trees; (iv) 1-D CNN/TSFresh-class model where sample size allows.

**Success criteria (pre-registered):**
- S→R within **10% relative** of R→R performance (AUC or macro-F1) = PASS (utility demonstrated).
- S→R within 10–20% = MARGINAL (dataset usable with domain-adaptation caveats, documented).
- S→R <80% of R→R = FAIL for that task (dataset not usable for that task; report, do not spin).
- S+R→R ≥ R→R by a non-trivial margin (≥2 pp AUC with paired bootstrap CI excluding 0) = augmentation value demonstrated.
- S→S ≈ R→R within Monte-Carlo noise = internal consistency (necessary, not sufficient).
- R→S markedly worse than S→R ⇒ synthetic data *easier* than real (trivial-separation defect — investigate NC2).

### 5.2 Task matrix

| Task | Labels / target | Real training/test data | Synthetic arm | Baselines | Success criteria |
|---|---|---|---|---|---|
| **T1 Orthostatic stress detection** (event-level: stand/tilt epoch vs supine; ΔHR trajectory regression) | event flags; ΔHR at 1/3/5/10 min | PRCP (OPEN), cardioresp-orthostatic PhysioNet (OPEN), EUROBAVAR standing epochs; free-living stand-events from DaLiA/CAPTURE-24 transitions | synthetic lab-day tilt/stand protocols + free-living stands (SPEC §6 scheduling) | null; ΔHR-threshold rule; LR on posture+HR features; CNN on HR+IMU window | Event detection F1: S→R within 10% of R→R. ΔHR regression: S→R MAE within 15% of R→R MAE. Healthy-tail fidelity: synthetic healthy >30 bpm exceedance within protocol band (10–33%) else FAIL regardless of AUC |
| **T2 Autonomic-state classification** (rest/stress/exercise/sleep epoch classification) | protocol phase | WESAD (TSST), DriveDB (condition-proxy), PPG-DaLiA activities, Wearable-Device-Dataset stress/exercise (OPEN) | synthetic stress/exercise/sleep events | LR on HR/HRV/EDA features; GBM; within-dataset vs cross-dataset generalization gap must be reproduced (reviews show >90% claims are within-dataset artifacts) | macro-F1 S→R within 10% of R→R; **cross-dataset degradation of the real-trained model must also appear in the synthetic-trained model** (generalization-gap transfer) |
| **T3 Recovery estimation** (post-exercise HR recovery; slowed-recovery patient phenotype) | HRR 1-min value; recovery-τ class (healthy vs slowed) | TMET-Málaga (OPEN), Sports Med 2026 summary statistics (healthy 3–6 h vs LC 9–13 h — literature-constraint tier), Wearable-Device exercise arm | synthetic exercise bouts with adaptation state F(t) and C_rec | LR/GBM on HR decay features; bi-exponential fit params | HRR regression S→R MAE within 15% of R→R; slowed-recovery class AUC in 0.75–0.85 band (NC2); synthetic must reproduce effort-coupling confound (Target 4) |
| **T4 Exertional response modeling** (HR/RR response to graded workload; chronotropic incompetence contrast) | workload→HR slope; CI flag (LIINC-style) | TMET-Málaga; LIINC summary stats (EVD-LCOV-007); frail post-surgery exercise set (OPEN) for low-capacity end | synthetic graded-exercise protocols across fitness/severity | linear HR-VO2 model; GBM | slope error S→R within 15% of R→R; CI-vs-normal contrast preserved but overlapping (AUC ≤0.85) |
| **T5 Anomaly detection** (illness/infection deviation from personal baseline) | infection-window flags (retrospective) | DETECT/Stanford published AUCs (literature-constraint: passive AUC 0.70, +symptoms 0.80, RHR-only 0.52); TemPredict deviation stats | synthetic infection episodes with background mimics (alcohol, jet lag, hard training, menstrual) | personal-baseline residual z-score; isolation forest; RHR-only baseline | Synthetic-trained detector on synthetic test must reproduce the published AUC ordering (RHR-only ≈ 0.52 < passive multimodal ~0.70 ≤ +symptoms ~0.80) and false-alarm inflation at low prevalence; S→R cannot be run raw (no open real set) → literature-constraint pass/fail |
| **T6 Phenotype stratification** (POTS-like vs healthy; ME/CFS severity grading; LC POTS-penetrance axis) | phenotype / severity class | **No open disease wearable set** → proxies: EUROBAVAR impaired subjects (reflex-gain only), PPG-DaLiA healthy as control arm; published summary statistics (§3.1) | synthetic POTS/ME/CFS/LC cohorts | LR/GBM on daily features (RHR, HRV, steps, stand-test ΔHR) | AUC must land 0.75–0.85 band (NC2); activity-matching must collapse ME/CFS stratification (NC7/pacing rule); report as **proxy-validated**, pending restricted datasets (§6) |
| **T7 Symptom-state prediction** (flare/prodrome windows; PEM symptom kernel) | flare days (RA-style), PEM symptom days | RA Forecast marginal offsets only (EVD-AUTO-005); **no open labeled dataset** → literature-constraint tier | synthetic flare/PEM episodes with medication masks and background symptom rates (EVD-LCOV-012) | within-person baseline deviation rules; mixed-effects logistic | Only *offset-direction and magnitude* validation (RHR +5 bpm etc.); **predictability claims forbidden** (NC5): any AUC >0.85 on this task = FAIL/inspection trigger |

### 5.3 Execution protocol
1. Freeze tolerances + splits + baselines (this file) and hash them into the run manifest.
2. Generate dataset per SPEC; run Levels 1–4 first; any Level-1/2 failure blocks Level 5.
3. Run matrix; report **all cells** including failures; no selective reporting.
4. **Explicit statement (binding): synthetic utility is NOT claimed until this matrix has been executed and the pre-registered criteria met.** Marketing, documentation, and downstream papers must carry this sentence until then: *"OCPE synthetic data are candidate research artifacts whose utility for any task is unestablished pending the Level-5 benchmark."*
5. Negative-control battery (§3.2) runs on the same generated data; any NC failure invalidates the release regardless of Level-5 performance.

---

## 6. CURRENTLY UNVALIDATABLE — EXPLICIT EXCLUSION DECLARATIONS

Per the independent reviewer's demand (Criterion 8.3) and VALIDATION_DATASETS §12, the following are **excluded from validation claims** in this release. Each is declared in the dataset manifest (`honesty_flags`) and in any publication:

| Exclusion | Why unvalidatable | Consequence for the dataset |
|---|---|---|
| **PEM dynamics (individual-level)** | No validated PEM detector exists; no multi-day multi-signal wearable PEM dataset exists in classic ME/CFS (EVD-MECFS-010); nearest proxy is a single long-COVID cohort (n=127); the 24–48 h delay is documented for *symptoms*, not physiological channels (CONTRADICTION Target 5) | PEM ground-truth labels emitted with `evidence: E0–E2, assumption-labeled`; physiological channels use only the slowed-recovery kernel (single-source tag); **no PEM-detection benchmark cell is offered**; NC7 enforces non-detectability |
| **Severe ME/CFS physiology** | Severe patients are systematically excluded from lab/CPET studies; all severe-tier parameters are extrapolations downward (AUDIT gap 13) | Severe tier generated from steps anchors (EVD-MECFS-002) only; flagged `extrapolated`; excluded from Level-3 positive targets beyond step counts |
| **hEDS venous pooling** | The core narrative mechanism has never been measured (no venous-compliance study; EVD-EDS-003, E0–E1); hEDS dysautonomia etiology (intrinsic vs deconditioning) unresolved (EVD-EDS-008) | Pooling perturbation in hEDS is an optional EXPERIMENTAL-flagged draw with `mechanism_untested: true`; no hEDS hemodynamic validation claim |
| **POTS raw cohort validation** | No openly downloadable diagnosed-POTS tilt/stand dataset exists; only Zenodo 20327114 (13/13, restricted-request), 2 baroreflex-impaired EUROBAVAR subjects, and published summary statistics | POTS slice is validated as "impaired-autonomic proxies + published-statistics constraints," NOT direct cohort validation, until restricted access clears (start requests now: Zenodo 20327114, RECOVER/dbGaP, All of Us Fitbit DURA) |
| **Long-COVID continuous waveforms; EDS/autoimmune wearable data; consumer-watch PPG at scale; cold-pressor beat-to-beat** | None exist at any access level (VALIDATION_DATASETS §12 items 3–6) | Literature-constraint tier only (published summary statistics with pre-registered bands) |
| **Disease-specific sleep staging** | Wearable staging accuracy unstudied in ME/CFS/LC (healthy-only κ values) | Disease-cohort staging outputs carry healthy-device confusion matrices; no disease-staging claim |
| **Multi-day full-stack synchrony** | Longest real synchronized multimodal set ~2.5 h (DaLiA) | Joint multi-day × multimodal claim validated piecewise only (§4 disclosure) |
| **ME/CFS metabolomic / long-COVID ML classifier targets** | In-sample AUROCs 94–96% (Naviaux) / 0.951 (n=126) are overfit artifacts | Permanently barred as validation targets (NC5) |

**Schedule risk register:** restricted datasets (RECOVER weeks–months; All of Us institutional DURA; Zenodo POTS on-request; MESA/SHHS DUA) gate the disease-slice claims; the cold-pressor lead is unverified; TROIKA hosting is informal (link-rot risk). Until these clear, release language is fixed per §5.3 item 4.

---

*End of benchmark specification. Levels 1–2 are executable against the engine alone; Level 3 requires only literature; Levels 4–5 require the open datasets (immediately) and restricted datasets (schedule risk). Nothing in this document asserts that the current engine (CURRENT_IMPLEMENTATION_MAP: no dataset layer, uniform-noise HRV, no sleep/circadian, sensor noise decoupled from KB) can yet pass Level 1 — the P0 engine revisions in INDEPENDENT_REVIEW_PASS2.md §4 are prerequisites.*
