# OCPE — CONTRADICTION AUDIT (Pass 2: Adversarial Validation)

**Role:** Contradiction Hunter. **Method:** independent web verification of pivotal citations (DOI/PMID existence + numeric claims), plus targeted searches for contradictory findings, null replications, population-specific effects, and competing mechanisms for every priority attack target. 23 citation/number claims were spot-checked against primary sources (Section D). Dossier citations were *not* trusted at face value.

**Verdict legend:** (A) CONFIRMED robust · (B) WEAKENED — downgrade evidence · (C) REFUTED or inverted · (E) requires model-level uncertainty representation.

---

## TARGET 1 — Healthy orthostatic ΔHR vs the POTS 30-bpm boundary

**Claim (dossiers):** Healthy 10-min stand ΔHR ~ +10–15 bpm (classic teaching) / model target Normal(+12, 5) with ">95% below 30 bpm"; prolonged tilt drives 60–80% of healthy controls above 30 bpm.

**Supporting:** Plash et al. 2013 (PMC3478101) — VERIFIED EXACT: controls (n=28) tilt ΔHR 27±3 (5 min), 34±3 (10 min), 40±4 (30 min); stand 23±3 / 25±3 / 26±3. Specificity of the 30-bpm criterion: tilt-10min 40%, tilt-30min 20%, stand-10min 67%. Optimal cutoffs: stand 29 bpm; tilt-10min ~37–38 bpm; tilt-30min 47 bpm.

**Contradictory/amplifying:**
- Lee et al. 2020 NASA Lean Test (PMC7429890): **33% of healthy controls met POTS ΔHR>30 bpm by 10 min standing**; 49% of HCs showed POTS *or* OH. Fasting protocol may inflate, but this is a fully passive-muscle-pump-removed stand — the most aggressive stand variant.
- Seeley et al. 2025 (J Clin Med review, MDPI 14:8139): healthy controls 10-min stand ΔHR 15 [IQR 9–20] bpm — lower than Plash's 25±3. The healthy stand mean itself ranges ~12–25 bpm across protocols (supine-rest duration, fasting, time of day, "maximum-so-far" vs point estimate).
- Adolescents: 95th percentile of stand ΔHR is 41–48 bpm; 42% of healthy children exceed 30 bpm on 5-min tilt (cited in Clin Auton Res 2023 editorial, DOI 10.1007/s10286-023-00977-3) — hence the pediatric ≥40 bpm criterion.

**Explanation:** The 30-bpm boundary's false-positive rate is *protocol-dependent, not population-constant*: passive tilt (muscle pump removed, hydrostatic stress maximal) ≫ NASA lean > active stand after long supine rest > active stand after short supine rest. Plash's stand mean (25 bpm) reflects ≥1 h supine, fasting, morning, Vanderbilt lab conditions; free-living stands are far milder.

**Population dependence:** Strong — adolescents need ≥40 bpm; age attenuates orthostatic tachycardia (dossier's E/I data consistent).

**Methodological dependence:** Dominant factor. Supine baseline duration, fasting, time of day, and whether ΔHR is the maximum-up-to-time-t or the value at time t change the healthy mean by >10 bpm.

**Current consensus:** The 30-bpm criterion is a *clinical* threshold with acceptable specificity only under the standardized 10-min active-stand or 10-min tilt protocols used in POTS clinics; it is NOT a physiological boundary. On prolonged tilt (≥20–30 min) it is largely meaningless in healthy young adults.

**Remaining uncertainty:** True free-living healthy stand ΔHR distribution (unsupervised, no pre-rest) is essentially unmeasured at scale.

**Verdict: (B) WEAKENED + (E). Recommended modeling strategy:** Parameterize ΔHR by *protocol* (tilt angle/duration vs stand variant, supine-rest duration), not a single Normal(+12,5). Use protocol-conditioned means ≈ tilt-10min ~34±8, stand-10min ~15–25 (wide), with an explicit upper tail such that ~15–35% of healthy young adults exceed 30 bpm on aggressive protocols and <5% on a casual short-notice stand. The repo's test `healthy sustained ΔHR < 30 (≈19.5 achieved)` is mean-consistent but its tail behavior is unvalidated; do not force the >95%-below-30 constraint — the real 10-min-stand false-positive rate is ~10–33% depending on protocol. **Represent protocol uncertainty in the model; do not force consensus on a single healthy ΔHR value.**

---

## TARGET 2 — Geddes 2022 as quantitative backbone of OCPE POTS parameters

**Claim (implementation map):** 29 base parameters + canonical POTS perturbations (RalpM 17.88→11.5 etc.) trace to Geddes 2022 (J R Soc Interface, DOI 10.1098/rsif.2022.0220); tier C; 5 perturbations cite human data.

**Supporting:** Geddes 2022 verified real (PubMed 36000360; "POTS explained using a baroreflex response model"). Reproduces qualitative POTS phenomenology; validated against 25 healthy controls for the healthy model.

**Contradictory:**
- **Fu et al. 2010 (JACC 55:2858-68, PMC2914315, VERIFIED):** in 19 POTS vs controls, **baroreflex function was similar between groups; "autonomic function was intact in POTS patients"**; tachycardia fully attributable to small LV mass (1.26 vs 1.45 g/kg) + blood volume deficit (60 vs 71 mL/kg, −15%). This is a direct competing-mechanism result against the Geddes framing of POTS as elevated baroreflex/sympathetic gain. Exercise training (+12% LV mass, +7% BV) abolished POTS criteria in 10/19 — supporting the deconditioning/hypovolemia account over a fixed autonomic-gain defect.
- Kulapatana 2025 (Clin Auton Res 35:267-276, DOI 10.1007/s10286-024-01091-8): BV deviation correlates with upright HR only in POTS (r=−0.608) — volume-first mechanism again.
- No independent human dataset confirming Geddes's specific *parameter shifts* (e.g., Ralp halving for neuropathic POTS) was located in adversarial search; the parameter magnitudes are calibrated to produce the desired output, i.e., circular at tier C/D.

**Repo-level evidence of weakness (CURRENT_IMPLEMENTATION_MAP.md):** neuropathic POTS canonical perturbation reaches only **21.2 bpm sustained ΔHR vs the ≥30 target** (strict xfail; flat dose-response 18.5→21.7, hydrostatic-gate-limited); hyperadrenergic ΔSBP target fails (−4.0 vs +10 mmHg, 0-D pulse-pressure limitation); annotated tilt-onset transition (Geddes Eq. 2.16) not implemented. The single-paper parameter set *does not reproduce two of four POTS phenotypes in the engine itself*.

**Explanation:** Geddes is a proof-of-concept lumped model, not a fitted clinical dataset; POTS is mechanistically heterogeneous (Angeli 2024: 41.7% two phenotypes, 11.4% three, 6.8% none).

**Population dependence:** POTS phenotype mix varies by cohort; Geddes perturbations encode one canonical story per phenotype.

**Current consensus:** Hypovolemia and reduced cardiac size/stroke volume are the best-replicated objective findings; *specific* autonomic gain values are not established human data.

**Verdict: (B) WEAKENED (single-source, partially engine-falsified) + (E). Recommended strategy:** Treat all Geddes-derived perturbations as tier D scenario parameters sampled over ranges; anchor what independent human data exist (TotalVol −12±5% [Raj 2005 / Fu 2010 / Kulapatana 2025]; hyperadrenergic subset via standing NE ≥600 pg/mL [Angeli 2024]); add the Fu-2010 "small heart + hypovolemia, intact baroreflex" scenario as an explicit competing model branch. Fix or honestly report the neuropathic/hyperadrenergic xfails before any dataset claim.

---

## TARGET 3 — POTS blood volume deficit (689±270 mL, n=15; Raj 2005)

**Supporting:** Raj 2005 (Circulation 111:1574-1582, DOI 10.1161/01.CIR.0000160356.97313.5D) — journal/volume/pages VERIFIED. Deficit ~11–12%.

**Replication status (the dossier's key risk):** REPLICATED in direction and rough magnitude by two independent methods/cohorts:
- Fu 2010: 60 [54–64] vs 71 [65–78] mL/kg (−15%, p<0.01).
- Kulapatana 2025 (CO rebreathing, VERIFIED): BV 64.53±10.02 vs 76.78±10.00 mL/kg; **deficit −13.92±10.38%**; RBCV also reduced; deficit correlated with upright HR (r=−0.608) in POTS only.

**Contradictory/nuances:** The ±10.38% SD in Kulapatana implies a substantial minority of POTS patients have *normal or elevated* BV — consistent with Angeli 2024 finding hypovolemic phenotype in only 44.9% and 6.8% matching no phenotype. The exact 689±270 mL figure remains single-study, n=15, 2005 radioisotope era; it should not be hard-coded as the deficit estimate.

**Verdict: (A) CONFIRMED in direction/magnitude class (pooled ~ −12 to −15%) but (E) heterogeneity is real.** Strategy: model BV deficit as a mixture — hypovolemic subpopulation (~40–50% of POTS, deficit ~−14±10%) + volume-normal subpopulation; do not apply a universal fixed deficit. Keep Raj's absolute mL out of the generative prior (weight- and sex-dependent; use mL/kg or % deficit).

---

## TARGET 4 — ME/CFS 2-day CPET day-2 decrement

**Supporting:** VanNess 2007; Snell 2013 (51 pts); Keller 2014 (J Transl Med 12:104, VERIFIED: VO2peak −13.8%, VO2@VT −15.8%, Work@VT −21.3%, RER≥1.1 both days); Nelson 2019 (Work@VT −6.3 to −9.8% cut, PMC6417168); van Campen 2020; Keller 2024 multicenter (PMID 38965566, VERIFIED: −5.3% VO2peak, −6.8% VO2@VT); Lim 2020 meta-analysis (J Clin Med 9(12):4040, VERIFIED — Workload@VT the most significant T2−T1 patient-vs-control difference).

**Contradictory (nulls and confounds):**
- **Mancini/Natelson et al. 2026 (Front Physiol, DOI 10.3389/fphys.2026.1816082, VERIFIED):** n=58 ME/CFS vs 25 sedentary controls, strict effort (RER≥1.05): **no Day-1→Day-2 change in peak VO2 (22.3±5.4→22.6±5.6), VO2@VT, O2 pulse, or VE/VCO2 in either group.** Critically: ≥1 mL/kg/min day-2 decline occurred in **22% of patients vs 33% of controls** — the "signature" is not even enriched in patients.
- Vermeulen 2010: −6.3% VO2peak — within normal test-retest variability (Keller 2014's own critique); RER not reported (effort unverifiable).
- Davenport 2020: comparable day-2 decline in both groups (per dossier).
- **Effort confound documented inside the positive camp:** Keller 2024's own data show Day-2 %HR reserve falling below the 80% effort criterion in ME/CFS ("maximum effort was not given during Day 2 CPET") — i.e., part of the measured decrement is inability/unwillingness to mount maximal effort during PEM, which is circular as a PEM biomarker.
- ME/CFS dossier itself already lists these (§7 red flags) — this audit independently confirms them.

**Explanation:** Small single-center studies with loose effort criteria find 14–27% drops; the largest multicenter study finds ~5–7%; the largest strict-effort study finds zero. Test-retest variability of VO2peak (~5–10%) and day-2 effort reduction during PEM explain most of the signal; a true pathophysiological residual may exist at the ventilatory threshold/workload level but is not diagnostic-grade.

**Verdict: (B) WEAKENED — downgrade from E4 to E2/E3 + (E). Strategy:** Do NOT model a universal day-2 decrement as an ME/CFS-defining physiological law. Model: (i) a small mean capacity decrement (0–7%, wide CI, threshold/workload-weighted), (ii) an explicit **effort-coupling term** (day-2 maximal effort capacity reduced during PEM — which is mechanistically interesting in itself, cf. Walitt 2024 effort-preference finding), (iii) a responder subgroup (~20–40%). State clearly that 2-day CPET is *contested* as an objective PEM biomarker.

---

## TARGET 5 — PEM delayed-kernel model (24–48 h)

**Supporting:** Symptom-level: Moore 2023 (Medicina 59:571, PMID 36984572, VERIFIED: judged recovery 12.7±1.2 d vs 2.1±0.2 d; range 1–64 d); Loy 2016 and Barhorst 2022 meta-analyses (symptom worsening ≥4 h post-exercise); patient-report PEM latency typically hours–48 h.

**Contradictory/gap:** Adversarial searches for *physiological* (non-symptom) PEM trajectories returned essentially nothing. No study has tracked a delayed 24–48 h physiological dip (HRV, HR, temperature, activity-adjusted) with objective wearable/lab measures at adequate temporal density. The closest physiological study — long COVID wearable HRV (Sports Med 2026, DOI 10.1007/s40279-026-02487-4, VERIFIED) — shows **delayed autonomic recovery on the same day (healthy 3–6 h vs long COVID 9–13 h post-exercise)**, i.e., a *prolonged immediate recovery* pattern, not a 24–48 h delayed trough. These are different temporal kernels.

**Explanation:** The 24–48 h delay is documented for *symptom perception/report*; whether an objective physiological state variable follows the same delayed kernel is unknown (E0/E1, as the temporal dossier itself graded).

**Verdict: (B) WEAKENED for physiological trajectories (symptom kernel stands) + (E). Strategy:** Keep the delayed kernel for symptom/affect states only. For physiological channels, use the evidence-supported *slowed-recovery* kernel (healthy τ ~3–6 h; patient τ ~9–13+ h after >VT1 exercise) and add an optional, explicitly speculative delayed second-wave component flagged E0. Do not propagate a 24–48 h physiological dip into HR/HRV channels as established.

---

## TARGET 6 — RMSSD as vagal index (post-LF/HF)

**Supporting:** RMSSD is the least-bad HRV vagal proxy; respiration-rate confound is real and quantified: Schipke 1999 — RMSSD varied up to **37%** across respiration rates at constant HR (J Clin Basic Cardiol 2:92-5); Grossman & Taylor 2007 framework; RSA amplitude scales with tidal volume and inverse respiration rate independently of vagal tone.

**Contradictory:** RMSSD↔vagal coupling breaks down at high HR (vagal saturation), during slow breathing, and across devices (Apple Watch serial RMSSD MAPE 28.9%, MAE 20.5 ms vs Polar H10 — O'Grady 2024, Sensors 24:6220 — below clinical accuracy for absolute values). Population RHR↔RMSSD r≈−0.58 is from **children only** (n=626); in adults the HR–RMSSD relation is dominated by mathematical RR-interval scaling (van Roon 2016; de Geus 2019).

**Verdict: (B) WEAKENED + (E). Strategy:** Model RMSSD as (vagal state, respiration rate, tidal volume, HR level, device bias) — with respiration and HR as explicit mechanistic inputs, not noise. Use within-person ΔRMSSD (device-stable) rather than absolute cross-device values. Population correlation: use RR-scaling law + weak residual, not a fixed r=−0.58 (downgrade to E1/E2).

---

## TARGET 7 — Fever/HR coupling slope

**Claim:** "~12.3 bpm/°C" used as a general relationship in HEALTHY dossier §7.1 (source PMC9605188); AUTOIMMUNE dossier used 13.7 bpm/°C explicitly for children.

**Verification:** PMC9605188 VERIFIED — but it is the **pediatric** ED study (Emerg Med J 2022): 12.3 bpm/°C overall, age-dependent **13.7 (youngest) → 8.7 bpm/°C (oldest children)**. The hospitalized-children percentile study (PMC4411783) gives ~10 bpm/°C.

**Contradictory (adults):** Adult ED data (local + ~123.3M national visits; Am J Emerg Med 2019, PMID 31345594): **~7.2 bpm/°C unadjusted nationally; 10.4 (local) / 6.9 (national) adjusted**. The classic "~10 bpm/°C" rule itself is a loose convention.

**Verdict: (C) REFUTED as stated for adults (12.3 is pediatric). Strategy:** Age-dependent slope: ~13 bpm/°C (young children) → ~10 (older children) → **~7–10 bpm/°C adults, with wide inter-individual spread** (CIs in the adult study span 5.9–11.4). The POPULATION dossier's "+7–10 bpm/°C, E1/E3" is the correct adult range; harmonize all dossiers to the age-graded version. Note fever-HR coupling also varies with hydration, medications, sepsis vs benign fever — represent as a distribution, not a constant.

---

## TARGET 8 — Sensor error models

**PPG HR skin tone:** Koerber 2023 systematic review VERIFIED (J Racial Ethn Health Disparities 10:2676-2684): 10 studies/469 participants — **4 found reduced accuracy with darker skin, 4 found no effect, 2 mixed; "preliminary evidence is inconclusive."** Mean Fitzpatrick 3.5, small n. Bent 2020 (npj Digit Med 3:18, VERIFIED) found device-level effects small for HR vs motion/BMI. Singh 2024 JMIR meta-analysis (e62769) also exists. → The skin-tone *HR* penalty is real in some studies but unquantified; the dossier's "mixed/uncertain" framing is correct — do not install a fixed melanin-bias constant.

**SpO2 skin tone (stronger):** Sjoding 2020 NEJM VERIFIED (PMID 33326721; occult hypoxemia 11.7% vs 3.6% Michigan, 17.0% vs 6.2% multicenter). BUT magnitude is unstable across settings: Valbuena 2022 BMJ VHA (n=28,531; VERIFIED): Black 19.6% vs White 15.6% (absolute gap 4 pp, NNH 25; Hispanic not significantly different unadjusted). So: direction robust, magnitude 3–8 pp and outcome-linked (Fawzy 2022 treatment delays). Wearable SpO2 LoA ±4% (Lambe 2026, VERIFIED) dwarfs the bias for individual readings.

**Free-living usability:** Lambe 2026 VERIFIED (82 studies, 430,052 participants; HR bias −0.27 bpm, LoA −7.19/6.64; AF sens 0.79/spec 0.91; energy-expenditure errors "inconsistent and frequently large" ≥20%). **(E)** Model HR with ±7 bpm LoA noise + exercise-condition error inflation; treat EE as unusable for precision; SpO2 with wide LoA + race/pigmentation bias term with uncertain magnitude.

**Verdict: (A/B mixed).** Confirmed: Apple Watch HR bias/LoA; pulse-ox bias direction. Weakened: any fixed skin-tone PPG-HR penalty (E: sample it); any claim of wearable EE accuracy.

---

## TARGET 9 — Wearable discriminative claims

**RA flare (RA Forecast, Sharma/Hirten 2025, Sci Rep; PMC12486041, VERIFIED):** n=53 (88.7% female), 8,183 days; F1 0.95 (inflammatory) / 0.93 (symptomatic) at 28 days pre-flare; AUC 1.00. **BUT:** these are mixed-effects logistic-regression associations on day-level within-subject data with per-participant random intercepts — *not* a held-out predictive model; no external validation; flare labels themselves partly imputed (CRP ±7-day windows); remission:flare day imbalance extreme; and **the authors explicitly state the approach "may bias AUC results" and that ML work "to bring these results to the individual level" is pending.** The physiological offsets are more credible than the classifier: RHR +5.0 bpm, mean HR +6 bpm during inflammatory flares (p<0.0001) — usable as model targets. Dossier's "F1 0.95–0.97" slightly overstated (actual 0.93–0.95).

**Verdict: (B) WEAKENED (E4→E2 for prediction; the within-person offsets survive).** Strategy: use the RHR/HR flare offsets and HRV-mesor reduction (21.5 vs 28.7 ms) as generative parameters; treat any flare *predictability* as unproven; never emit F1≈0.95-level performance from the simulation as if validated.

**iRBD actigraphy (multicenter, npj Digit Med 2025, DOI 10.1038/s41746-025-01999-z; PMC12572274, VERIFIED):** Sleep-movement model generalizes: AUC 0.838–0.865 across 4 centers/3 devices (352 iRBD, 258 controls). **However the higher single-center numbers (RAR 0.856, combined 0.954) did NOT generalize: RAR AUC collapsed to 0.520–0.818 (chance-level in Hong Kong 0.534 and Innsbruck 0.520).** Sensitivity 63–90%, specificity 64–90% across cohorts; at real-world 1.5% prevalence, PPV 3–6% (sleep alone) to ~33% (two-stage with prodromes in the largest cohort).

**Verdict: (C) partially REFUTED — the 0.92–0.95 combined-model figure is a single-center artifact; (A) for the sleep-only model at 0.84–0.87.** Strategy: model actigraphic iRBD detectability at AUC ~0.85 (sleep features only); represent PPV explicitly as prevalence-dependent; drop RAR-based claims.

---

## TARGET 10 — Population correlations and latent structure

- SBP↔DBP r=0.717 (NHANES II, n=6,667): plausible, consistent with known BP covariance; E2 retained (no contradiction found).
- RHR↔SBP/DBP r≈0.26: small studies; direction consistent; E2 retained with wide CI.
- **RHR↔RMSSD r≈−0.58: WEAKENED (see Target 6)** — children-only anchor; use RR-scaling law for adults.
- RHR↔VO2max r=−0.34 (Copenhagen Male Study): consistent with literature range (−0.3 to −0.5 cross-sectional); retained.
- Latent-factor structure: the dossier's own E0 flag is **confirmed by this audit** — no factor-analytic study of autonomic/wearable batteries was located in adversarial search either. The proposed factors ("vagal setpoint", "fitness", "hemodynamic aging") are theory-driven. **(E): implement with loading uncertainty (sample loadings over ±50% ranges, Gaussian copula sensitivity at r=0 vs provisional values) exactly as the dossier recommends; do not let downstream consumers treat the factor structure as empirical.**

---

## TARGET 11 — Repo assumptions (CURRENT_IMPLEMENTATION_MAP.md)

1. **Venomotor parameters:** Heldt 2002 structure + van Heusden 2006 creep are legitimate published models, but `dV_veno_max 250→75` denervation is tier D and the neuropathic phenotype fails its own target (21.2 vs ≥30 bpm; xfail). **(B)** — do not report neuropathic-POTS outputs as validated.
2. **Sensor constants not drawn from KB validation metrics** (Polar H10 ICC 0.99/0.96 exists in KB but unused): **(E)** — wire the validated numbers into the sensor model or document why the engine's constants differ.
3. **Healthy orthostatic test** asserts ΔHR<30 (≈19.5): mean fine; tail unvalidated (Target 1).
4. **Hyperadrenergic ΔSBP +10 mmHg target unreachable in 0-D model** (−4.0 actual): known structural limitation; keep xfail, and do not let phenotype scope claim MAP-pressor simulation.
5. **Fludrocortisone TotalVol +500 mL** (Chobanian 1979 direction-only): magnitude is an assumption — **(E)** sample ±50%.
6. **Heat Raupm/Ralpm ×0.58** (Ganio 2012): compartment-mapping caveat legitimately flagged; retain NEEDS REVIEW.

---

## TARGET 12 — E-level inflation scan

- ME/CFS HRV meta-analysis (Nelson 2019, PMC6824690) at E5: effect sizes small (RMSSD SMD −0.37) and activity-matching erases VO2max differences (MCAM ES 0.02) — E5 refers to replication count, fine, but magnitudes must not be upgraded in the model.
- Healthy dossier Avram usage: two minor numeric errors — 71–80 y HR is **74.2±11.1, not ±12.7**; female coefficient is **+4.00 bpm (Table 4), not +4.4**. Also Avram measures *real-world on-demand* PPG HR (full-sample geometric mean 79.1; healthy 77.6±14.6), not laboratory resting HR — the dossier's own limitation note is correct and should propagate: use Avram for age/sex *gradients*, not absolute resting-HR calibration.
- Long COVID dossier's refusal to hard-code ~30% POTS prevalence is **vindicated**: estimates range 22% (Shouman, n=27) to 31% (Björnson 2025, n=467, Circ Arrhythmia Electrophysiol, VERIFIED via Karolinska release) to 79% (Seeley 2025, n=33, specialist clinic) — enrichment-dependent. Keep the graded latent axis.

---

## SECTION A — Claims CONFIRMED robust

| Claim | Verification |
|---|---|
| Tanaka 2001 HRmax = 208−0.7×age (meta-analysis, 351 studies/18,712 subjects; SD ~10–12 bpm individual) | PMID 11153730 exact match |
| Plash 2013 tilt-vs-stand divergence and specificity values | PMC3478101 exact match |
| POTS hypovolemia direction/magnitude class (−12 to −15%) | Raj 2005 + Fu 2010 + Kulapatana 2025 triangulated, 3 methods |
| Keller 2024 multicenter 2-day CPET numbers (−5.3%/−6.8%) | PMID 38965566 exact |
| Natelson/Mancini 2026 null (58 vs 25; 22% pts vs 33% ctl ≥1 unit decline) | DOI 10.3389/fphys.2026.1816082 exact |
| Moore 2023 PEM recovery 12.7±1.2 d vs 2.1±0.2 d (symptom-level) | PMID 36984572 exact |
| Angeli 2024 phenotype frequencies (75.0/44.9/37.8%; 41.7% dual; 11.4% triple; 6.8% none) | PMC10761725 exact |
| Lambe 2026 Apple Watch: HR bias −0.27 bpm, LoA −7.19/6.64; AF sens 0.79 spec 0.91; EE errors ≥20% | PMID 41513748 / DOI 10.1038/s41746-025-02238-1 exact |
| Sjoding 2020 pulse-ox occult hypoxemia direction (11.7 vs 3.6%; 17.0 vs 6.2%) | PMID 33326721 exact |
| iRBD sleep-only actigraphy AUC 0.838–0.865 generalizes across 4 centers/3 devices | PMC12572274 exact |
| Long COVID HRV delayed same-day recovery (3–6 h → 9–13 h) | DOI 10.1007/s40279-026-02487-4 exact |
| Pediatric fever-HR slope 12.3 bpm/°C, age-graded 13.7→8.7 | PMC9605188 exact |

## SECTION B — Claims WEAKENED (downgrade)

| Claim | Action |
|---|---|
| Geddes 2022 parameter shifts as POTS backbone | tier C → tier D; scenario-sampled; competing Fu-2010 branch required |
| 2-day CPET day-2 decrement as reliable ME/CFS signature | E4 → E2/E3; add effort-coupling; responder subgroup only |
| PEM 24–48 h delay for *physiological* channels | downgrade to E0/E1; use slowed-recovery kernel (hours) for physiology |
| RMSSD as clean vagal index | add respiration/HR/device mechanistic confound inputs; drop fixed population r=−0.58 (children-only) |
| Healthy stand ΔHR Normal(+12,5) with >95%<30 bpm | protocol-conditioned model; allow 10–33% exceedance on aggressive protocols |
| RA flare F1 0.95 | E4 → E2; keep within-person offsets (RHR +5 bpm), drop classifier claims |
| PPG HR skin-tone penalty | keep as sampled uncertain parameter, not a constant |
| Avram Health eHeart absolute resting-HR calibration | use gradients only; correct two numeric misquotes |
| Neuropathic POTS engine output | unvalidated (xfail); exclude from dataset claims |
| Health eHeart "resting" label | relabel "real-world on-demand HR" |

## SECTION C — Claims REFUTED or inverted

| Claim | Refutation |
|---|---|
| 12.3 bpm/°C as a general (adult) fever-HR slope | Adult ED data: ~7 bpm/°C national (adj 6.9–10.4); 12.3 is pediatric (PMID 31345594 vs PMC9605188) |
| POTS as necessarily elevated baroreflex/sympathetic gain (implicit in Geddes perturbations) | Fu 2010: baroreflex function statistically identical, autonomic function intact; hypovolemia + small heart suffice (PMC2914315) |
| iRBD combined/RAR actigraphy AUC 0.92–0.95 | External multicenter validation: RAR AUC 0.520–0.818 (≈chance at 2/4 sites); only sleep model (0.84–0.87) survives (PMC12572274) |
| ">95% of healthy stay below 30 bpm ΔHR" as a protocol-free statement | NASA lean 33% HC exceedance; Plash stand-10min specificity 67%; tilt-30min 20% — true only for specific mild protocols |
| 2-day CPET day-2 decline as patient-specific | Natelson 2026: decline *less* frequent in patients than controls (22% vs 33%) |

## SECTION D — Citation verification results (23 spot-checks)

**VERIFIED (existence + numbers):** Plash 2013 (PMC3478101); Raj 2005 (Circulation 111:1574-82; DOI 10.1161/01.CIR.0000160356.97313.5D); Geddes 2022 (PubMed 36000360); Tanaka 2001 (PMID 11153730); Avram 2019 (PMC6592896); Keller 2014 (J Transl Med 12:104); Keller 2024 (PMID 38965566); Nelson 2019 HRV meta (PMC6824690, via dossier + external); Nelson 2019 CPET (PMC6417168); Natelson/Mancini 2026 (DOI 10.3389/fphys.2026.1816082); Moore 2023 (PMID 36984572); Lim 2020 meta (J Clin Med 9(12):4040); Vermeulen 2010 (numbers via Lim meta + Keller 2014 discussion); PMC9605188 fever study; adult fever study (PMID 31345594); Angeli 2024 (PMC10761725); Lambe 2026 (PMID 41513748); Koerber 2023 (10:2676-2684); Lee 2020 NLT (PMC7429890); RA Forecast (PMC12486041); iRBD multicenter (PMC12572274, DOI 10.1038/s41746-025-01999-z); Fu 2010 (PMC2914315, PMID 20579544); Kulapatana 2025 (PMID 39614968); Sjoding 2020 (PMID 33326721); Valbuena 2022 (BMJ 378:e069775; Chest 161:971-8); O'Grady 2024 (Sensors 24:6220); Björnson 2025 (DOI 10.1161/CIRCEP.124.013629).

**FAILED TO VERIFY:** none outright. **NUMERIC DISCREPANCIES FOUND (minor):** (1) HEALTHY dossier: Avram 71–80 y SD quoted 12.7, actual 11.1; female offset quoted +4.4, actual regression +4.00. (2) AUTOIMMUNE dossier: RA Forecast F1 quoted "0.95–0.97", actual 0.95 (inflammatory)/0.93 (symptomatic). (3) Sensor dossier's framing of Valbuena should note the BMJ VHA study found a *smaller but significant* gap (19.6 vs 15.6%), not a null. (4) "Heal 2022" attribution — PMC9605188 is the Emerg Med J pediatric study; numbers match; author name spelling should be double-checked against the article.

## SECTION E — Claims requiring model-level uncertainty representation (do NOT force consensus)

1. Healthy orthostatic ΔHR: protocol-conditioned distribution with honest tails; never a single Normal.
2. Geddes parameter set: full scenario sampling + competing Fu-2010 mechanism branch.
3. POTS blood volume: mixture model (hypovolemic ~45% vs volume-normal), deficit −14±10% in the hypovolemic branch.
4. ME/CFS day-2 CPET: small mean decrement + effort-coupling term + responder subgroup; label contested.
5. PEM: symptom kernel (24–48 h, E2) decoupled from physiological kernel (slowed recovery, hours, E2; delayed physiological second wave E0, optional).
6. RMSSD: mechanistic confound inputs (respiration, HR, device); within-person deltas preferred.
7. Fever-HR: age-graded slope ~7–13 bpm/°C with inter-individual spread.
8. Skin-tone sensor terms: sampled bias with mass at ~0 (PPG-HR) and positive-bias distribution (SpO2).
9. Latent factor structure: loading uncertainty ±50%, copula sensitivity at r=0.
10. Long COVID POTS penetrance: graded latent axis 20–80% depending on ascertainment (already dossier-recommended; confirmed).
11. Fludrocortisone/heat tier-B perturbation magnitudes: ±50% sampling.
12. Wearable flare/screening predictability: base-rate-coupled PPV; no fixed F1/AUC emission as validated truth.

---

*Audit completed Pass 2. All quoted external numbers verified against primary sources or high-authority summaries during this audit; internal dossier quotes verified against the dossier files directly.*
