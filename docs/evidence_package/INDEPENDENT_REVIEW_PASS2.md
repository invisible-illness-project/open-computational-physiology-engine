# OCPE Pass-1 Package — Independent Scientific Review (Pass 2)

**Reviewer role:** Independent Scientific Reviewer (did not participate in Pass 1).
**Scope reviewed:** all 16 files in `/mnt/agents/output/ocpe/` (implementation map, phenotype scope, 12 evidence dossiers, validation datasets), plus targeted external spot-checks.
**Spot-checks performed (all PASSED):** Plash 2013 control orthostatic ΔHR (stand 23±3 @5 min, 25±3 @10 min — confirmed, PMC3478101); Williams 2019 inflammation–HRV meta-analysis (PMID 30872091 — confirmed); Raj 2005 blood-volume deficit ≈689 mL (confirmed); Quer 2020 n=92,457 Fitbit RHR cohort (confirmed — note: journal is *PLoS ONE* 15(2):e0227709); van Campen 2020 ME/CFS CBF tilt series (confirmed); VanNess 2010 PEM recovery (60% ME/CFS >5 d — confirmed); Lambe 2026 Apple Watch living meta-analysis, 82 studies/430,052 participants (PMID 41513748 — confirmed, real); Erlandson 2024 RECOVER routine-labs null (confirmed — *Annals of Internal Medicine*, not JAMA IM); Moore 2023 PEM recovery 12.7 d (confirmed — **but it is a MEAN ± s.e.m., not a median**).

---

## 1. Verdicts per criterion

### Criterion 1 — CONFIRMATION BIAS: **PASS**
This is the package's strongest dimension. Every disease dossier carries an explicit null/contradictory register, and the nulls are load-bearing, not decorative:
- **POTS:** 10-item contradiction section (resting MSNA normal/elevated/low; BRS reduced/unchanged/increased-in-children; autoregulation impaired vs intact; Swai 2019 frequency-domain HRV meta-analytic null; Angeli symptom-discrimination null; Taub baseline ΔHR ~21 in untreated POTS).
- **ME/CFS:** 9-item null register including the Nelson 2026 two-day-CPET null replication (spot-checked: *Front Physiol* 2026, 58 ME/CFS vs 25 controls, no Day-2 VO2 decline — real and correctly characterized), activity-matched VO2 null, PACE reanalysis.
- **Long COVID:** RECOVER routine-labs null (Erlandson 2024) used as a boundary condition; background symptom rates in uninfected controls (PEM 7%) mandated for synthetic controls; POTS-in-LC prevalence contradiction by method (0% HUTT vs 79% active stand) resolved into a graded axis rather than cherry-picked.
- **EDS:** WHOOP pilot group-level null; Miglis null (hEDS adds little beyond POTS); Peebles contradiction (POTS concentrated in G-HSD); venous-pooling narrative explicitly labeled E0–E1.
- **Neurological:** CHS null replication of ARIC HRV–PD association; Lee 2019 migraine ECG meta null; panic-attack HR surge shown to be modest/partially null (only 3/8 ambulatory attacks beyond activity; hyperventilation HR only +4.4 bpm) — actively argues against the stereotype.
- **Autoimmune:** TNF-α–HRV null within Williams 2019; SpO2 IBD null; hydrocortisone-doesn't-block-HRV-depression nuance.
- **Sensor:** skin-tone equity evidence presented in both directions with the Colvonen underpowering critique; EE-accuracy negative results (E5) prominent.

Dossiers also impose anti-confirmation *quantitative* guards: ME/CFS AUROC cap (~0.7–0.8), Long-COVID AUC ceiling guidance (0.75–0.85; >0.95 ⇒ too stereotyped). Residual risk: headline magnitudes in ME/CFS (van Campen CBF), autoimmune flares (RA Forecast AUC ~1.00 at 28 d pre-flare) still rest on single groups/studies — but the dossiers themselves flag this, so the residual risk is in *downstream use*, not in the dossiers.

### Criterion 2 — FABRICATED PRECISION: **PASS with minor CONCERNS**
The dominant practice is sound: magnitudes are quoted with n, SD/CI, named source, and E-level; implementation recommendations convert point values into distributions; several values are explicitly demoted ("provisional", "machine-calibrated", "E0"). Specific defects to fix:
1. **PEM recovery statistic mislabeled** (ME/CFS dossier): "median recovery 12.7 d (Moore 2023)" — the source reports judged-recovery **mean** 12.7±1.1 d (range 1–64 d; one unrecovered-at-1-y outlier excluded). Mean ≠ median in a right-skewed distribution; this changes the kernel tail the TEMPORAL dossier should use.
2. **Healthy within-person RHR SD** (HEALTHY): "est. ~3–6 bpm, E0 provisional" — superseded by Quer 2020 (within-person SD ≈3.0 bpm, CV ≈4.6%) already in the POPULATION dossier. Cross-reference instead of carrying a weaker E0 estimate.
3. **Fever–HR slope** (HEALTHY §7): "8.7–13.7 bpm/°C, overall ~12.3" is presented without flagging that Heal 2022 (PMC9605188) is a **pediatric ED** dataset; AUTOIMMUNE C4.1 labels this correctly and gives ~10 bpm/°C as the adult heuristic. Adopt the AUTOIMMUNE framing.
4. Single-study magnitudes promoted to implementation recommendations: PEM kernel (Moore only), ME/CFS CBF (van Campen group dominance), RA flare AUC — all flagged in-text, but they should carry an explicit "single-source" tag in the parameter tables so an engineer skimming tables cannot miss it.
5. Repo-side calibrated values (healthy sustained ΔHR ~19.5 bpm; hypovolemic TotalVol 3500 mL = ~1.5× the Raj 2005 measured deficit; hyperadrenergic kR/kH/p2H applied-value mismatches) are honestly documented as machine-calibrated — acceptable for Pass 1, must be resolved or formally justified before synthesis (see §4).

### Criterion 3 — HETEROGENEITY: **PASS with CONCERNS**
Evidence layer: good. POTS modeled as composable continuous subtype axes with an empirical joint distribution (Angeli 2024: 41.7% two phenotypes, 11.4% all three); ME/CFS severity latent with step anchors (8235/5195/2031) and mixture models for PEM detectability and nocturnal-HR direction; Long COVID penetrance-weighted phenotype axes; bimodal cold-pressor HR responders; TSST responder/non-responder structure; EDS comorbidity rates as ranges with ascertainment down-weighting; MSNA 4-fold interindividual range "model as distribution not point."
Concerns:
- **Implementation layer lags the evidence layer.** The engine exposes 3 discrete POTS presets + ME/CFS-HM only; hEDS/autoimmune/sleep-deprivation/beta-blocker phenotypes are engine-inert; POTS subtype prevalence weights are E0 (no validated distribution — acknowledged). The dossiers describe continuous composable axes; the code implements discrete presets. A synthesis plan must not let the discrete presets silently become the phenotype definition.
- **Pacing/behavioral adaptation** (ME/CFS, chronic pain) is the largest under-modeled heterogeneity axis: WEARABLE_OBSERVABILITY notes pacing abolishes most group-level signatures; this must be a first-class behavioral state, not noise.
- Comorbid overlap is documented (POPULATION co-occurrence table, NEURO shared-vmHRV axis) but there is no resolved rule for *stacking* perturbations (additive vs multiplicative HRV effects; ST-3 validation suggests additive-ish — good instinct, needs a global rule).

### Criterion 4 — MECHANISM vs WEARABLE SIGNAL: **PASS**
Best-in-class discipline. WEARABLE_OBSERVABILITY provides a ~25-row verdict master table with an explicit latent-only list (SVR, SV/CO at wrist, venous pooling, cerebral perfusion, resting/febrile core temperature, hydration, optical glucose, absolute BRS, PEM episode, stress ground truth). AUTOIMMUNE, METABOLIC, NEUROLOGICAL, and POTS each enforce "LATENT-ONLY — do not fabricate observable" rules (endothelial stiffness → no PPG morphology signal; insulin/RER/BAT/ketones latent; MIBG/cortisol/ETCO2 latent). The cuffless-BP critique is decisive and correctly propagated: PPG-BP error (±5–10 mmHg, ISO-failing, 6.8 mmHg/7d drift) exceeds the signals (PPH in young adults, 20 mmHg OH thresholds) and POTS criteria exclude a BP drop — so cuffless BP cannot certify the absence of OH; BP stays semi-latent. Minor residue: METABOLIC master table still lists a few "(b) indirect" verdicts where stated error exceeds the signal (PPH by cuffless BP in young adults) — internally it flags this, so impact is low.

### Criterion 5 — HEALTHY-REFERENCE-FIRST: **PASS with CONCERNS**
Evidence layer is rich enough: HEALTHY (distributions, protocol-conditioned orthostatic values, contradictory-findings sections), POPULATION (large-n age/sex tables for RHR/RMSSD/sleep/steps, correlation matrix with honestly-marked assumed cells, variance decomposition with ICCs), AUTONOMIC (latencies, gains, BRS by method), plus CORE stress/pain/hyperventilation/OSA modules from NEUROLOGICAL. Diseases *can* be perturbations of this reference.
Concerns:
- The **engine's healthy reference is far thinner than the evidence**: HRV is uniform ±2% noise (no RSA/1f/LF-HF structure), sleep is never entered, circadian uncoupled, no behavior layer — all documented in CURRENT_IMPLEMENTATION_MAP. The healthy reference must be upgraded (HRV structure, sleep, circadian, behavior) *before* disease perturbations can be validated against it; several disease signatures (nocturnal HRV, PEM timing, flare prodromes) live exactly in the missing structure.
- Key healthy-reference gaps the dossiers themselves flag: orthostatic event-to-event reliability unknown (POPULATION provisional CV 15–25%), within-person RHR SD (fix per §1.2), adult fever–HR slope is heuristic, day-to-day orthostatic variability.
- Two definitional axes must be frozen before disease perturbation: RHR definition (see §2, row 3) and the protocol-conditioned orthostatic response (§2, row 1).

### Criterion 6 — CROSS-DOSSIER CONSISTENCY: **CONCERNS** (see table in §2)
No fatal contradictions of direction, but: (a) **three incompatible E0–E5 evidence-scale conventions** across dossiers (plus the repo's A–D tiers) — a serious misreading hazard; (b) the healthy orthostatic ΔHR is stated four different ways across four dossiers with different implicit timescales; (c) RHR reference values differ by device/definition without a reconciliation layer; (d) smaller magnitude tensions (fever slope pediatric origin, postprandial ΔHR, PEM statistic). None are cherry-picking; all are fixable harmonization items.

### Criterion 7 — TIMESCALE DISCIPLINE: **PASS with one CONCERN**
The TEMPORAL dossier is explicitly organized by timescale with a real identifiability treatment (Pironet/Olufsen; unrecoverable parameters → population priors); disease dossiers separate delay/peak/recovery (PEM), impulse timescales (LPS: onset 1–2 h, peak 3–5 h, recovery 8–24 h), and trait-vs-event structure (NEURO: anxiety reactivity null ⇒ tonic layer, panic = event). One collapse: TEMPORAL's orthostatic band "**+10–25 bpm within ~30 s**" conflates the initial transient (peak ~15–30 s) with the sustained 1–10-min response on which the POTS criterion is defined; its validation target ("+10–25 healthy; ≥30 POTS") inherits the ambiguity. Fix by splitting initial-transient and sustained-response parameters explicitly (HEALTHY dossier already has the data to do this). Also carry PEM timing as a *distribution* (Moore mean 12.7 d, range 1–64 d), not a single τ.

### Criterion 8 — VALIDATION FEASIBILITY: **CONCERNS**
Strengths: VALIDATION_DATASETS is unusually honest — verified-host inventory, access tiers, and an explicit statement that there is **no** open POTS tilt dataset, ME/CFS raw wearable data, long-COVID waveforms, EDS/autoimmune wearable data, consumer-watch PPG at scale, or multi-day synchronized full-stack data (max ~2.5 h, DaLiA). The healthy-side ladder (PRCP, PPG-DaLiA, WESAD, EUROBAVAR, Autonomic Aging Jena) is realistic.
Weaknesses:
1. **Disease-slice validation rests on proxies + published summary statistics.** Acceptable for a first dataset, but the package lacks a *protocol*: which summary statistics, which distance metrics (e.g., per-channel distributional distances with pre-registered tolerance bands), and what constitutes failure. Several dossiers propose distribution-matching and AUC-cap sanity checks — these need consolidation into one validation harness spec.
2. **EUROBAVAR as a dysautonomia analogue is a stretch** (baroreflex-impaired, elderly, not POTS/ME-CFS); usable for reflex-gain validation only, and should be labeled as such.
3. **PEM is declared unvalidatable by the package's own inventory** (no multi-day wearable PEM dataset exists) — this should be stated as an explicit validation exclusion, with ME/CFS validation restricted to cross-sectional/severity-graded distributions.
4. Restricted datasets (RECOVER, All of Us Fitbit, Zenodo POTS 13/13-on-request) are schedule risks; the cold-pressor lead is unverified.
5. No validation of the **artifact/observation layer** is planned against free-living usable-fraction statistics already in SENSOR_MODEL (30–60% daytime PPG usability, day/night split, streaming loss) — cheap to add, high value.
6. Missing negative-control battery at the harness level (AUTOIMMUNE's SpO2-null and TNF-null fidelity checks, NEURO's panic-vs-seizure confusion test are proposed per-dossier but not unified).

### Criterion 9 — OVERALL SUFFICIENCY: **CONCERNS — sufficient as an evidence base; not yet sufficient to build a defensible dataset without the revisions in §4**
The evidence layer is defensible: well-sourced (spot-checks all passed, including several 2025–2026 citations I initially treated as suspicious), null-inclusive, observability-disciplined, heterogeneity-aware. The blockers are (1) scale/harmonization defects, (2) a wide and honestly-documented gap between the evidence and the engine (no dataset-generation layer at all; HRV/sleep/circadian/behavior missing; sensor noise decoupled from the KB), and (3) an incomplete validation harness spec for disease slices. None require new literature discovery at scale; all are integration work.

---

## 2. Cross-dossier inconsistency table

| # | Topic | Dossier A | Dossier B (+ engine) | Nature | Severity / required action |
|---|-------|-----------|----------------------|--------|---------------------------|
| 1 | **Evidence-grade scale semantics** | Most dossiers (HEALTHY, AUTONOMIC, POTS, ME/CFS, LC, EDS, AUTOIMMUNE, METABOLIC, NEURO, SENSOR, POPULATION): E0=hypothesis … E5=meta-analysis | **TEMPORAL: inverted** (E0=established consensus *best* … E5=engineering judgment); **WEARABLE_OBSERVABILITY: third convention** (E0=established standard … E5=background/textbook); repo uses tiers A–D | Same symbol, three opposite meanings — an engineer reading "E0" in TEMPORAL as "hypothesis" would invert confidence | **HIGH** — harmonize to one scale (or rename TEMPORAL/WEARABLE grades) before synthesis; add a scale legend to every file header |
| 2 | **Healthy orthostatic ΔHR** | HEALTHY generative recommendation: stand steady-state ~Normal(+12,5); Vanderbilt controls stand +23±3 @5 min/+25±3 @10 min; tilt +27/+34/+40; 60% of healthy exceed 30 bpm at 10-min tilt | AUTONOMIC: peak beat-15 +10–20, settle +10–15. TEMPORAL: "+10–25 bpm within ~30 s". NEURO CORE: "+10–25 bpm". Engine: sustained ~19.5 bpm (machine-calibrated) | Initial transient, early stand, sustained 10-min stand, and 10-min tilt are four different quantities presented with overlapping bands; the POTS ≥30 boundary sits inside the disputed zone | **HIGH** — define one protocol-conditioned, time-resolved healthy reference curve (transient vs sustained; stand vs tilt; age strata); set the engine target from it explicitly and document the false-positive rate at 10-min stand/tilt |
| 3 | **Healthy RHR reference** | HEALTHY: Health eHeart deciles 74–82 (self-selected "rest", PPG) | POPULATION: Quer 2020 daily RHR 65.5±7.7 (Fitbit; note journal = *PLoS ONE*, verify citation); Fenland seated 67.6 | Definition/device dependence (~4–8 bpm offsets) flagged in both but no canonical choice | **MEDIUM** — freeze one RHR definition per simulated channel (e.g., nocturnal RHR for wearables, seated clinic RHR for validation) and propagate |
| 4 | **Fever→HR slope** | HEALTHY: "8.7–13.7 bpm/°C, overall ~12.3" (pediatric ED data presented as general) | AUTOIMMUNE C4.1: same source correctly labeled pediatric; adult heuristic ~10 bpm/°C | Age-dependence origin lost in HEALTHY | **MEDIUM** — adopt age-interpolated slope, adult default ~10 (AUTOIMMUNE framing) |
| 5 | **Postprandial ΔHR** | TEMPORAL: "+10–20 bpm at 30–60 min (approximate)" | METABOLIC M7: +6±3 typical mixed meal, up to +10–20 for large/high-carb; HEALTHY: +6–21% | Magnitude tension (meal-size dependence) | **LOW** — reconcile to meal-size-scaled distribution |
| 6 | **PEM recovery statistic** | ME/CFS: "median 12.7 d (Moore 2023)" | Source is judged-recovery **mean** 12.7±1.1 d, range 1–64 d; TEMPORAL kernel τ≈2–8 d | Wrong statistic label + tail mismatch | **MEDIUM** — relabel, and fit an explicit right-skewed recovery distribution |
| 7 | **POTS hypovolemia magnitude** | POTS dossier: measured deficit 689±270 mL (Raj 2005 — spot-check verified) | Engine TotalVol=3500 mL (~1.5× deficit), flagged "machine-calibrated" in scope doc | Engine–evidence mismatch, documented but unresolved | **MEDIUM** — either refit to measured deficit or document the calibration offset as an explicit assumption with sensitivity analysis |
| 8 | **Hyperadrenergic POTS parameters** | Scope doc: KB nominal kR/kH/p2H vs applied values 34.78/31.48/89.96; engine ΔSBP −4.0 vs +10 criterion (strict xfail) | POTS dossier: hyperadrenergic ΔSBP rise is a defining feature | Internal engine-vs-KB inconsistency | **MEDIUM** — resolve normal_value vs KB-nominal bug class; an xfail is not a resolution |
| 9 | **Disease resting-HR elevations on the same observable** | POTS: clinic +10–20 (but wearable Welltory null +3); ME/CFS +4.1; LC +1–3; EDS ~+10; T2DM +5–10; RA flare +5 | Overlapping magnitudes from different protocols/devices | Not contradictory, but indistinguishable without the overlap matrix (§3) and within-person baseline semantics | **MEDIUM** — unify on within-person deviation semantics (as AUTOIMMUNE already recommends) |
| 10 | **RA flare predictability** | AUTOIMMUNE C8.1: AUC ~1.00/F1 0.95 at 28 d pre-flare, with imbalance caveat | Validation dossier does not list RA Forecast as an anchor | Single preprint-stage study at risk of becoming a validation target | **LOW** — do not use AUC 1.00 as a target; use the marginal means only |
| 11 | **PEM wearable proxy** | ME/CFS Claim 4.5 and LC dossier both cite the same Sports Med 2026 ambulatory VT1+/nocturnal-RMSSD study | Consistent cross-citation (good) | Single study serving two dossiers | **LOW** — tag as single-source in both |

No contradictions of *direction* were found between dossiers; all items above are harmonization/precision issues, not competing claims.

---

## 3. Candidate nonspecific-mechanism list (input to the overlap matrix)

Mechanisms/observable axes that ≥2 dossiers (or one dossier + core physiology) attach to multiple conditions — these must NOT be emitted as disease-specific signatures:

1. **Low tonic vagal HRV (↓RMSSD/HF):** PD, anxiety (g≈−0.3–−0.45), chronic pain, migraine, depression, T2DM/CAN, RA/SLE/Sjögren's, low-grade inflammation (|r|≈0.1), aging, sleep loss, alcohol, beta-blockers, deconditioning. NEURO dossier already proposes a single shared "tonic vagal gain" knob — endorse.
2. **Elevated resting HR:** deconditioning, inflammation/fever, POTS, anxiety, T2DM, steroids, sleep restriction, fasting>36 h, heat.
3. **Exaggerated orthostatic tachycardia:** POTS subtypes, hEDS/HSD, Sjögren's, ME/CFS subset, long-COVID subset, fasting, dehydration/heat, bed rest/deconditioning, hyperventilation, and ~33–60% of healthy controls at 10-min stand/tilt (NASA Lean Test / Plash tilt data).
4. **Blunted orthostatic compensation / OH:** PD/MSA/PAF (neurogenic), CAN, PPH, fasting, levodopa, dehydration — contrast pair with #3.
5. **Activity/step suppression:** PEM/pacing, gout flare, RA symptomatic flare, depression, pain, infection — indistinguishable at the step channel.
6. **Sleep fragmentation / ↓efficiency:** inflammation (dose-dependent biphasic), stress/anxiety, OSA, RBD, steroids, pain.
7. **Nocturnal HR elevation / blunted dipping:** inflammation, OSA, neurogenic supine hypertension (reverse dipping), alcohol, late meals, heat — opposite directions possible (reverse dipping vs loss of dip), needs joint modeling.
8. **EDA surges:** stress, pain/pressor, panic, ictal autonomic surges, ambient heat/humidity artifact — panic-vs-seizure confusion explicitly desired as a validation test (NEURO EP-2).
9. **Post-exertional delayed symptom flare (PEM-like):** ME/CFS, long COVID, overtraining, infection recovery — delay-to-peak 12–48 h is shared machinery.
10. **Distal skin-temperature elevation:** fever/infection, inflammation, menstrual luteal phase (+0.3 °C), meal thermogenesis, ambient heat, alcohol.
11. **Cyclical SpO2/HR (sawtooth):** OSA/SRBD as comorbidity of PD, epilepsy, MSA, and general population (prevalence-definition-sensitive 10–84%) — one CORE generator, parameterized by AHI.
12. **Menstrual-cycle RHR/RMSSD modulation (+2–7 bpm / −4–5 ms):** healthy core, must be present so it is not misread as flare/infection in female disease personas.
13. **Slow-gait sensor undercount (5–30% step error):** measurement artifact correlated with ME/CFS severity and elderly PD/MSA cohorts — an observability confound, not a mechanism, but belongs in the overlap matrix so severity is not overestimated from steps.
14. **Medication gain masks:** beta-blockers (blunt HR/HRV/orthostatic response), steroids (RHR↑, sleep↓, decorrelate CRP-proxy), levodopa (post-dose OH), SSRIs (HRV) — cross-disease confound layer.

---

## 4. Prioritized required revisions before synthesis

**P0 — blocks any defensible dataset:**
1. **Harmonize evidence scales** (§2 row 1). One E0–E5 convention across all dossiers; rename or convert TEMPORAL and WEARABLE_OBSERVABILITY grades; map repo tiers A–D onto it.
2. **Freeze the healthy orthostatic reference** (§2 row 2): a protocol-conditioned, time-resolved curve (initial transient vs sustained; stand vs tilt; age strata), with the healthy false-positive rate at the POTS ≥30 bpm/10-min boundary stated numerically. Every downstream POTS claim depends on this; the HEALTHY dossier explicitly calls it "the single most consequential calibration choice".
3. **Close the engine–evidence gap for the first dataset scope.** CURRENT_IMPLEMENTATION_MAP shows: no dataset-generation layer; HRV = uniform ±2% noise (no RSA/1f/LF-HF); sleep and circadian absent; behavior layer absent; sensor noise hardcoded and decoupled from KB; PEM dead code. Minimum for a defensible first dataset: (a) structured HRV generation consistent with POPULATION/AUTONOMIC distributions; (b) sleep-wake and circadian coupling; (c) sensor observation layer wired to SENSOR_MODEL defaults (fs, LoA, usable-fraction, day/night, cadence-lock); (d) ground-truth retention policy per WEARABLE_OBSERVABILITY design rules.
4. **Fix the statistic/precision defects** (§1.2): PEM mean-not-median + distribution; within-person RHR SD from Quer; fever slope age labeling; single-source tags on Moore/van Campen/RA Forecast-derived parameters.

**P1 — blocks disease-slice credibility:**
5. **Reconcile RHR definitions** (§2 row 3) and adopt within-person deviation semantics for all disease RHR/HRV claims (§2 row 9).
6. **Resolve engine parameter mismatches**: hypovolemia magnitude (689±270 mL or documented calibration offset + sensitivity), hyperadrenergic kR/kH/p2H applied-vs-nominal class of bug, behavior-modifier compounding bug (engine.py:139), fludrocortisone chronic-phase contradiction, heat whole-body→compartmental mapping (scope doc's own NEEDS REVIEW).
7. **Build the overlap matrix** from §3 and enforce it in generation: shared latent knobs (vagal gain, inflammation core, deconditioning, sleep fragmentation, medication masks) with disease layers as wrappers — the architecture AUTOIMMUNE §10 and NEURO §10 already converge on.
8. **Specify the validation harness** (§8): per-slice target statistics, distance metrics with pre-registered tolerances, unified negative-control battery (SpO2-null, TNF-null, panic/seizure confusion, artifact-mimic suites), artifact-layer validation against SENSOR usable-fraction statistics, explicit validation exclusions (PEM dynamics; disease waveforms absent from open data).

**P2 — strengthens but does not block:**
9. Split TEMPORAL orthostatic band into transient vs sustained parameters; carry PEM timing as a distribution.
10. State discrete-preset vs continuous-axis policy for phenotypes (engine presets must sample from the dossier joint distributions, not replace them); make pacing/behavioral adaptation a first-class state.
11. Add perturbation-stacking rule (additive-on-log-scale for HRV recommended; validate per NEURO ST-3).
12. Secondary-verified classics (METABOLIC §10 item 5; seizure-detection primary DOIs per NEURO §11) — pull primary sources before locking numbers.
13. Decide and document the intended use/claims of the first dataset (screening-algorithm training vs physiology education vs pipeline testing), since the AUC-cap guidance implies different acceptable fidelity per use.

---

## 5. What is genuinely strong (keep)

- Null/contradictory registers in every disease dossier, with quantitative anti-overfitting guards (AUROC caps).
- Latent/observable discipline with explicit "do not fabricate" lists, consistently applied across five dossiers.
- Honest validation-dataset inventory that states what does NOT exist rather than overselling proxies.
- POPULATION dossier's "correlation cells with NO evidence" table and assumed-cell markings — a model for the whole package.
- Cross-dossier convergence on shared-knob architecture (AUTOIMMUNE §10, NEURO §10, WEARABLE_OBSERVABILITY design rules) — synthesis can proceed on this skeleton once P0 items are done.

*End of Pass-2 independent review.*
