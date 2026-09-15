# OCPE — Metabolic Physiology Evidence Base (Pass 1: Discovery)

**Agent:** Metabolic Physiology Scientist
**Purpose:** Evidence-grounded quantitative claims for synthetic wearable data generation, with a hard observability discipline: every metabolic variable is classified as **(a) directly wearable-measurable**, **(b) indirectly inferable with stated error**, or **(c) latent-only**. Latent variables MUST NOT be given fabricated observable signals in the synthetic data engine.
**Evidence grading:** E0 hypothesis | E1 mechanistic | E2 observational human | E3 controlled human experimental | E4 replicated quantitative | E5 meta-analysis/consensus.
**Note on identifiers:** DOIs/PMIDs below were verified against search results where possible. Items marked "(secondary)" were confirmed via secondary scholarly sources but the primary record was not directly opened; items marked "(unverified ID)" give author/journal/year with no fabricated DOI/PMID.

---

## SECTION 0. Global observability rules for OCPE

1. **Blood/interstitial glucose** is wearable-observable ONLY via CGM (minimally invasive interstitial electrochemical sensor). Optical (PPG/NIR) or EDA-based glucose inference is **not validated** — see M5. In synthetic data, glucose should exist as a latent state that is *readable only if the simulated persona wears a CGM*, with CGM-specific error model (M-CGM below).
2. **Insulin, RER/substrate mix, splanchnic blood flow, beta-cell function, BAT activity** are latent-only. They may drive observable signals (HR, skin temperature, HRV) through documented transfer functions, but must never appear as directly "measured" channels.
3. **Energy expenditure** is indirectly inferable from HR + accelerometry with typical individual error of ±20–40% (M14). Synthetic "calorie" channels must carry this error distribution, not ground truth.
4. **HR/HRV** are directly wearable-measurable (PPG/ECG) and are the primary observable carriers of metabolic state (postprandial, fasting, sleep loss, autonomic neuropathy).

### CGM error model (for any simulated CGM channel)
- Overall MARD of modern systems ≈ 8–13% (FreeStyle Libre vs capillary BG 11.4–13.2%; range across systems/studies 8.8–21.4%; accuracy degrades during hypoglycemia and rapid glucose swings). [E4; Heinemann et al., *J Diabetes Sci Technol* 2020, PMC7189145]
- Physiological blood→interstitial lag: mean 9.5 ± 3.7 min (median 9 min, IQR 4 min; n=37, 108 datasets); prediction algorithms reduce apparent lag by ~4 min; post-OGTT lag can be 10–15 min. [E3; Schmelzeisen-Redeker et al., *J Diabetes Sci Technol* 2015, PMC4667340]
- In healthy adults during OGTT, FreeStyle Libre 2 showed MARD ~12.9% and a systematic negative bias of ~5–10 mg/dL vs finger-stick at all time points (n=44). [E3; Fellinger et al., cited in Sensors review, mdpi.com/1424-8220/26/2/633]
- Artifacts to simulate: compression lows (nocturnal false hypoglycemia), rate-of-change-dependent error when |dG/dt| > 1 mg/dL/min, first-day sensor inaccuracy, dropouts. Dawn-phenomenon-scale effects (10–20 mg/dL) are the same order as CGM error variance — detection thresholds must exceed sensor noise. [E3; Sci Rep 2024, s41598-024-52461-1]

---

## SECTION 1. Glucose / insulin dynamics

### M1. Normative 24-h glucose in healthy non-diabetic adults (CGM)
- **Claim:** Healthy 24-h mean interstitial glucose ≈ 90–99 mg/dL; daytime > nighttime.
- **Domain:** glucose homeostasis | **Variable:** interstitial glucose (mean, diurnal pattern)
- **Mechanism:** insulin/glucagon feedback maintaining narrow euglycemia.
- **Direction/magnitude+distribution:** Freckmann 2007 (n=21, everyday life): mean 24-h interstitial glucose 89.3 ± 6.2 mg/dL; day 93.0 ± 7.0; night 81.8 ± 6.3 mg/dL. Shah 2019 (n=153, age 7–80, blinded Dexcom G6, ≤10 d): mean glucose 98–99 mg/dL (5.4–5.5 mmol/L), >60 y group 104 mg/dL (5.8 mmol/L); median time-in-range (70–140 mg/dL) 96% (IQR 93–98); median time >140 mg/dL = 2.1% (~30 min/d); time <70 mg/dL = 1.1% (~15 min/d); time <54 mg/dL ≥2% of time in only 1% of participants.
- **Timescale:** continuous; diurnal nadir ~03:00–06:00.
- **Population:** healthy non-diabetic adults (both sexes, wide age range).
- **Wearable verdict:** **(a) directly measurable — CGM only.** 5-min sampling typical. Not observable by PPG/EDA/temperature at validated accuracy.
- **Evidence:** **E4** (two independent normative cohorts with consistent values).
- **Source:** Freckmann et al., *J Diabetes Sci Technol* 2007;1(5):695–703 (PMC2769652; unverified PMID). Shah et al., *J Clin Endocrinol Metab* 2019; PMID 31127824.
- **Supporting:** pregnancy CGM cohort (n=157, 3747 meals) fasting 88±14 mg/dL, baseline pre-meal 91±18 mg/dL (BMJ Open Diab Res Care 2024, e003989).
- **Contradictory/null:** Hall 2018 found ~1/3 of "healthy" participants showed dysregulated glucotypes with diabetic-range excursions — i.e., normative means hide real heterogeneity; the strict "always <140" rule is violated in a nontrivial minority (51% spent ≥2% time >140 mg/dL in Shah).
- **Limitations:** interstitial (not blood) values; small n in Freckmann; sensor bias ~-5 to -10 mg/dL in healthy range.
- **Implementation recommendation:** simulate 24-h glucose ~ N(90–99, SD 6–8 mg/dL) with diurnal component (~-10 mg/dL at night), right-skewed postprandial excursions; persona-level random effect for "glucotype."
- **Validation strategy:** compare synthetic distributions to Shah 2019 percentiles (TIR 96%, CV 17%).

### M2. Postprandial glucose curve in healthy adults
- **Claim:** After a mixed meal, glucose rises to a peak ~45–65 min post-meal and returns to baseline within 2–3 h; peaks almost always <140 mg/dL.
- **Variable:** postprandial glucose excursion, time-to-peak.
- **Mechanism:** nutrient absorption → insulin secretion → peripheral uptake + hepatic glucose output suppression.
- **Magnitude+distribution (Freckmann 2007, n=21):** breakfast peak 132.3 ± 16.7 mg/dL (range 101–168); lunch 118.2 ± 13.4; dinner 123.0 ± 16.9; rise over premeal: +50.2 ± 14.5 (breakfast), +38.8 ± 11.2 (lunch), +42.6 ± 18.7 (dinner) mg/dL; time-to-peak 46.0 ± 11.8 / 47.1 ± 11.5 / 49.6 ± 17.0 min. Standardized fast-absorption meals: peaks 133.2 ± 14.4 and 137.2 ± 21.1 mg/dL; high fiber/protein/fat meal: peaks only 99.2 ± 10.5 and 122.1 ± 20.4 mg/dL with slower decay. Pregnancy cohort: median time-to-peak 62 min (IQR 40–124); excursion 36 ± 22 mg/dL; rise rate ~0.5 mg/dL/min (median).
- **Timescale:** rise 0–60 min; decay 60–180 min.
- **Population:** healthy non-diabetic (and uncomplicated pregnancy).
- **Wearable verdict:** **(a) CGM directly; (b) meal *timing/confirmation* indirectly inferable from HR/skin-temp signatures (Section 2) with low specificity.**
- **Evidence:** **E4**.
- **Source:** Freckmann 2007 (PMC2769652); BMJ Open Diab Res Care 2024;12:e003989 (DOI 10.1136/bmjdrc-2023-003989 — unverified ID prefix); Hall 2018, *PLoS Biol*, DOI 10.1371/journal.pbio.2005143.
- **Supporting:** Zhang 2021 RCT (n=20) — walking 20 min *before* the individual PPG peak reduced 4-h iAUC glucose (-0.6 mmol/L·h), insulin (-28.7%), C-peptide (-28.7%) vs sitting: peak timing is individual and modifiable.
- **Contradictory/null:** peak times vary widely within individuals day-to-day (pregnancy IQR 40–124 min); single "30–60 min" rule is an approximation.
- **Limitations:** meal composition dependence is large; interstitial lag shifts CGM peaks +5–15 min vs blood.
- **Implementation recommendation:** model PPG as asymmetric excursion (rise rate ~0.5–1 mg/dL/min, peak +40 ± 15 mg/dL at 45–60 min, return by 150–180 min) with meal-macronutrient modulation (high carb: higher, earlier; high fat/fiber: lower, later, prolonged).
- **Validation strategy:** meal-challenge synthetic vs Freckmann Table 3 and pregnancy Table 3 distributions.

### M3. Glucose variability (GV) norms in non-diabetics
- **Claim:** Healthy GV: CV ≈ 14–17%, SD ≈ 13–16 mg/dL, MAGE ≈ 27–31 mg/dL; elevated GV in normoglycemic people predicts future T2D.
- **Magnitude:** Shah 2019: within-individual CV 17 ± 3%. AEGIS prospective cohort (n=497 non-diabetic, 6-d iPro2, 6-y follow-up): progressors to diabetes vs non-progressors: SD 18 vs 13 mg/dL; CV 17 vs 14%; MAGE 36 vs 27 mg/dL (all p<0.001); SD cutoff 14.9 mg/dL → AUC 0.81, sens 80%, spec 72%. Ultrahuman M1 Indian cohort: GV-SD 16.2 ± 4.85 (non-diabetic) vs 19.4 ± 6.51 (prediabetic); MAGE 30.7 ± 16.0.
- **Wearable verdict:** **(a) CGM-derived metrics only.**
- **Evidence:** **E2/E4** (prospective cohort, replicated cross-sectional).
- **Source:** Shah 2019 PMID 31127824; Rodríguez García et al., *Adv Lab Med* 2025, PMID 40160400; Sci Rep 2024 s41598-024-56933-2.
- **Contradictory:** clinical GV target CV ≤36% was defined for insulin-treated diabetes, not health screening; no consensus GV standard in non-diabetics.
- **Limitations:** GV metrics are highly inter-correlated and device/wear-duration dependent.
- **Implementation:** generate GV parameters per persona (CV ~ N(17,3)% healthy) and couple to future-T2D-risk personas (CV 17–20%).
- **Validation:** match Shah/AEGIS distributions; check SD–mean glucose correlation.

### M4. Dawn phenomenon
- **Claim:** A pre-breakfast glucose rise from the nocturnal nadir occurs in essentially all humans (circadian counter-regulation); ≥20 mg/dL rise is the CGM-defined threshold used in T2D; in healthy people the rise is modest and self-correcting.
- **Mechanism:** early-morning (≈04:00–08:00) growth hormone/cortisol/catecholamine surge → hepatic glycogenolysis/gluconeogenesis; compensated by insulin in healthy, uncompensated in diabetes.
- **Magnitude:** T2D: Δdawn ≥20 mg/dL (Monnier definition; present in >50% of T2D; adds ~0.4% to HbA1c, +12.4 mg/dL to 24-h mean glucose). Healthy: small rise, usually <10–20 mg/dL, within euglycemic range (secondary sources; no large normative quantification found — **gap**).
- **Wearable verdict:** **(a) CGM-detectable, but magnitude ≈ CGM error variance (10–20 mg/dL) → require multi-night averaging.**
- **Evidence:** **E2** (T2D cohorts) / **E1** (healthy, mechanistic).
- **Source:** Monnier et al., *Diabetes Metab* 2015;41:132–7, PMID 25457475, DOI 10.1016/j.diabet.2014.10.002; probabilistic framework: Sci Rep 2024 s41598-024-52461-1.
- **Contradictory:** no consensus CGM definition; binary thresholds misclassify given sensor error.
- **Implementation:** include circadian dawn component (+5–15 mg/dL healthy; +20–40 mg/dL T2D persona) starting ~04:00–05:00.
- **Validation:** Monnier Δdawn distribution in T2D personas.

### M5. Can glucose be inferred from PPG / EDA / HR (non-invasive optical)?
- **Claim:** **Evidence is essentially null/weak for field-valid accuracy.** Published ML studies are small (n=16–219), single-site, lack out-of-sample/generalization testing, and report errors far above clinical utility.
- **Magnitude:** reported MAE 13.5–26 mg/dL (RMSE up to 26 mg/dL), MAE 1.25–1.37 mmol/L on wristband/smartphone PPG; classification accuracy 75–92%; Clarke Error Grid Zone A+B as low as 67% (InCheck device); MARD 12.7–17.8% in the few honest reports. No regulatory-cleared optical glucose wearable exists (as of 2025).
- **Mechanistic basis:** glucose has no direct chromophore signature at PPG wavelengths; indirect hemodynamic correlates (blood viscosity, osmolarity, microvascular tone) are confounded by hydration, temperature, motion, posture, stress.
- **Wearable verdict:** **(c) effectively latent for wrist/finger optical wearables. Do NOT generate a "PPG-estimated glucose" channel as if it were signal; if simulated, it must be modeled as a high-noise, biased, non-generalizing estimator.**
- **Evidence:** **E0–E2** (feasibility-stage ML only).
- **Source:** review of non-invasive BGL ML studies, PMC12024879; PPG-MFCC study PMC12413980 (self-reported near-perfect accuracy on n=23 — methodologically implausible, treat as overfit exemplar).
- **Contradictory/null:** internal inconsistency across published accuracies (MAE 4–26 mg/dL for similar approaches) indicates no reproducible signal; FDA/CE have issued warnings against smartwatch glucose claims.
- **Limitations:** publication bias severe; most studies lack independent test sets.
- **Implementation recommendation:** glucose ← latent; CGM channel optional per persona; no optical-glucose channel.

### M6. Insulin (fasting and postprandial)
- **Claim:** Fasting insulin in healthy adults ≈ 4.5 ± 0.4 µU/mL (26–45 pmol/L); postprandial insulin rises ~5–10×, peaking ~30–60 min; beta-cell response degrades with sleep loss/circadian misalignment (Section 6).
- **Magnitude:** Buxton 2010 clamp: fasting 4.5 ± 0.4 µU/mL → 57.8 ± 2.3 µU/mL during infusion. Healthy mixed-meal study (n=10): fasting insulin 41.9 ± 2.9 pmol/L; 180-min values 46–90 pmol/L depending on meal.
- **Wearable verdict:** **(c) latent-only.** No wearable modality exists or is on the horizon. Insulin may be used as a hidden state driving glucose kinetics and postprandial HR/thermogenesis.
- **Evidence:** **E4** (clamp/IVGTT quantitative).
- **Source:** Buxton et al., *Diabetes* 2010, PMID 20585000, DOI 10.2337/db10-0696; Thota et al. 2022, PMC8924580.
- **Implementation:** latent insulin drives glucose decay rate constant; persona-level insulin-sensitivity parameter (HOMA/clamp-calibrated).

---

## SECTION 2. Postprandial cardiovascular response (healthy)

### M7. Postprandial heart rate rise
- **Claim:** HR rises promptly after meal onset, typically +5–10 bpm (range up to +10–20 bpm for large/high-carb meals), returning to baseline over 2–4 h.
- **Mechanism:** splanchnic vasodilation → baroreflex-mediated sympathetic activation + direct thermogenic/hormonal effects; increased CO via HR and SV.
- **Magnitude:** controlled meal-ECG studies: "we typically find HR increases of 8 beats/min, which gradually return to baseline over 4 hours after a meal" (Waalen et al.). Healthy elderly: HR +5–7 bpm at 60 min post-meal. Young healthy: no significant HRV change post-meal; elderly: LF/HF ↑ (sympathetic shift).
- **Timescale:** onset ~0–15 min (can begin with cephalic phase), peak ~30–60 min, decay 2–4 h.
- **Wearable verdict:** **(a) directly measurable — PPG/ECG HR.** This is the strongest wearable-detectable signature of meal ingestion. Sampling: 1-min or better. Confounders: posture, activity, caffeine, stress, circadian.
- **Evidence:** **E3/E4** (multiple controlled meal studies, consistent direction).
- **Source:** Waalen et al., *J Am Heart Assoc* 2019 (PMC6590239; unverified PMID); Yoshihara et al., *J Nutr Health Aging* elderly PPH spectral HRV study, PMID 11871771; Brocklehurst's Textbook of Geriatric Medicine (secondary).
- **Contradictory/null:** some young cohorts show statistically non-significant HR change after small meals; effect size scales with meal size/composition.
- **Implementation:** meal → HR component: +6 ± 3 bpm (mixed meal), peak 30–60 min, τ_decay ~90 min; scale by meal kcal and carb fraction; near-zero for small snacks.
- **Validation:** synthetic post-meal HR deltas vs Waalen/J-Tpeak and geriatric series.

### M8. Splanchnic/mesenteric blood flow response
- **Claim:** Postprandial superior mesenteric artery flow increases ~+70% and total splanchnic blood flow ~+50% (up to +100–200% in some reports); splanchnic blood volume increases ~20%; splanchnic share of CO rises from 20–25% (fasting) to ~35% after a large carbohydrate meal.
- **Magnitude (Perko et al., n=19, duplex + ICG dye):** SMA flow +1.46 ± 0.24 L/min (+70%, p<0.01); SBF +52%; mesenteric resistance −69%. High-fat meal SMA flow +121% vs +87% high-carb (Waalen-cited data). Postprandial exercise still reduces splanchnic flow (−22% mesenteric during cycling).
- **Wearable verdict:** **(c) latent-only** (no wearable Doppler). Drives observable HR rise and may contribute to postprandial skin-temperature fall at extremities (vasoconstriction then rebound).
- **Evidence:** **E3/E4**.
- **Source:** Perko et al., *J Physiol* 1998, PMC2231328; Monnikes/Research — meal composition duplex study, *J Clin Ultrasound*-era (sciencedirect 0016508588903642, unverified ID); Clinical Gate review (secondary).
- **Contradictory:** celiac artery flow largely unchanged post-meal; response is mainly SMA/portal.
- **Implementation:** latent splanchnic flow state driving HR (M7) and BP (M10) components; during exercise post-meal, allow competing demand → reduced splanchnic component.

### M9. Postprandial cardiac output
- **Magnitude:** CO rises ~+32% after high-carbohydrate meals vs ~+22% after high-fat meals; via HR and stroke volume increases. [E3; cited within Waalen 2019, PMC6590239]
- **Wearable verdict:** **(c) latent** (no consumer wearable CO); partially inferable from HR+PPG pulse features with large error — classify as indirect at best.

### M10. Postprandial hypotension (PPH)
- **Claim:** Healthy young adults: minimal BP change after meals (compensated). Healthy elderly: SBP falls ~11–16 mmHg at ~60 min with HR +5–7 bpm; PPH (SBP fall ≥20 mmHg) occurs in ~40% of healthy elderly and ~90% of frail geriatric patients; elderly with meal-related syncope: MAP −26 mmHg at 60 min with *absent* compensatory HR/NE response.
- **Mechanism:** splanchnic pooling (500–800 mL) + insulin/gut-peptide vasodilation; compensation requires sympathetic activation and cardioacceleration — blunted with age (β-adrenergic desensitization) and autonomic neuropathy.
- **Magnitude/timing:** nadir typically 30–60 min post-meal; duration up to 2 h. High-carb and warm meals largest; 350–480 mL water pre-meal raises BP ~20 mmHg in autonomic failure.
- **Population gradient:** young healthy (none) < healthy elderly (11–16 mmHg) < T2DM with CAN, Parkinson's, autonomic failure (≥20–40 mmHg, absent HR compensation).
- **Wearable verdict:** **(b) indirectly inferable** — no wearable cuffless BP is validated for this; detectable as *absent HR rise + symptoms context*; HR rise present in compensated elderly. Cuffless BP (PPG-based) error ±5–10 mmHg exceeds small PPH signals — do not fabricate a BP channel with false precision.
- **Evidence:** **E3** (controlled elderly cohorts), **E2** (prevalence).
- **Source:** Lipsitz et al. *J Clin Invest*-era syncope study, PMID 3766423; Vloet et al. 2010, DOI 10.4061/2010/243752; PPH review PMC9964048; intraduodenal glucose study PMC2290234.
- **Contradictory:** healthy elderly can show transient BP *rise during* the meal, then fall after.
- **Implementation:** BP latent state: young healthy ΔSBP ≈ 0 ± 5 mmHg; elderly persona ΔSBP −11 to −16 mmHg at 45–75 min; autonomic-failure persona −25 to −40 mmHg with blunted ΔHR (<+5 bpm).

### M11. Meal composition effects on cardiovascular response
- High-carbohydrate → greatest splanchnic pooling, most prolonged CO rise (+32%), largest BP fall; high-fat → larger SMA flow increase (+121%) but less BP drop; warm (>50°C) glucose drink: MAP −8.0 ± 1.1 mmHg vs cold: +3.9 ± 1.3 mmHg (elderly PPH context). [E3; PMC9964048, PMC6590239]
- **Wearable verdict:** effects appear in HR magnitude/duration (observable); composition itself is latent (log-driven).

### M12. Postprandial skin temperature and EDA
- **Claim (skin temp):** standardized liquid meal increases mean/proximal/supraclavicular skin temperature; pattern = peripheral vasoconstriction during first ~1 h, then vasodilation hours 2–3; thermic response larger in women. [E3; Márquez-Quiróz? — PMID 29907354, *Clin Nutr* 2018]
- **Claim (EDA):** direct quantitative evidence for meal-evoked EDA in healthy humans is sparse (sympathetic cholinergic sudomotor activation is plausible mechanistically; gustatory sweating is pathological). **Verdict: E1 only — do not generate a canonical postprandial EDA waveform; if included, mark as hypothesis-level with no validated magnitude.**
- **Wearable verdict:** skin temperature **(b) indirect marker** of postprandial thermogenesis with ~1–3 h lag; EDA **latent/unproven for meals**.

---

## SECTION 3. Energy expenditure

### M13. Resting metabolic rate norms and prediction equations
- **Claim:** Mifflin-St Jeor is the most accurate general-population RMR equation: within ±10% of measured RMR for 82% of non-obese and 70% of obese adults; explains 71% of variance (n=498 derivation). Harris-Benedict overestimates ~5% (up to 15%) in modern sedentary populations. Individual errors of ±150–400 kcal/d occur in 18–30% of people.
- **Equations:** Men: RMR = 10·kg + 6.25·cm − 5·age + 5; Women: −161. Katch-McArdle (LBM-based): 370 + 21.6·LBM.
- **Wearable verdict:** **(b) indirect** — RMR is latent; equation + anthropometrics is the standard estimator; wearable "resting calories" channels are equation outputs, not measurements.
- **Evidence:** **E5** (Frankenfield systematic review; consensus adoption by Academy of Nutrition & Dietetics).
- **Source:** Mifflin et al., *Am J Clin Nutr* 1990;51:241–7, PMID 2305711, DOI 10.1093/ajcn/51.2.241; Frankenfield et al., *J Am Diet Assoc* 2005;105:775–89, PMID 15883556.
- **Contradictory/null:** 29% of RMR variance unexplained by any tested variable set (genetics, thyroid status, adaptive thermogenesis); accuracy degrades with BMI >35, sarcopenic elderly, and metabolic adaptation after dieting (true RMR 100–300 kcal/d below prediction).
- **Implementation:** persona RMR = Mifflin(anthro) × lognormal(1.0, σ≈0.07) to reproduce the ~±10% individual scatter; add systematic bias −5% for metabolic-adaptation personas.

### M14. Wearable energy-expenditure estimation accuracy (the key negative result)
- **Claim:** No consumer wearable accurately measures EE. Across brands, MAPE >30% vs criterion methods; even the best devices show 10–40% error vs indirect calorimetry; vs doubly labeled water (DLW, free-living gold standard) wrist Fitbits underestimate ≈ −7% (group mean) with wide individual limits (≈ −750 to +400 kcal/d); no device <20% error in the Stanford 60-person study (2017).
- **Magnitude/distribution:** Germini 2022 (65 studies, 72 devices, 29 brands): EE MAPE >30% for all brands; steps MAPE <25% (Fitbit Charge); HR MAPE <10% (Apple Watch). Chevance 2022 Fitbit meta-analysis: pooled EE limits of agreement ≈ −12.75% to +7.41% (bias direction inconsistent across studies). Feehan 2018: free-living DLW comparison −7%; vs SenseWear median −15%; MAPE 16–30% vs ActiGraph/Actiheart. Older-adult DLW cohort: MAPE 12.25 ± 7.33%.
- **Why (mechanism of error):** HR–VO2 individual variability, motion-insensitive activities (cycling, resistance training), NEAT invisibility, no TEF/EPOC capture, algorithms trained on young homogeneous lab cohorts.
- **Wearable verdict:** **(b) indirectly inferable, error-prone.** Synthetic EE channels must embed: group-level bias ~−5 to −15%, individual MAPE 20–35%, activity-type-dependent error (resistance training ≈ near-random; steady cardio best).
- **Evidence:** **E5** (multiple convergent systematic reviews/meta-analyses).
- **Source:** Germini et al., *J Med Internet Res* 2022;24:e30791, PMID 35060915, DOI 10.2196/30791; Chevance et al., *JMIR mHealth uHealth* 2022;10:e35626, PMID 35416777, DOI 10.2196/35626; Feehan et al., *JMIR mHealth uHealth* 2018;6:e10527, PMID 30093371, DOI 10.2196/10527; Fuller et al. 2020, PMID 32897239, DOI 10.2196/18694.
- **Contradictory/null:** none found that overturn the conclusion — even 2026-era reviews show EE accuracy improved least of all metrics (still 10–40% error).
- **Validation strategy:** synthetic wearable-EE vs latent true EE should reproduce MAPE 20–35% and DLW-level bias ≈ −7%.

### M15. Thermic effect of food (TEF / diet-induced thermogenesis)
- **Claim:** TEF ≈ 10% of energy intake on a mixed diet (range ~5–15%); by macronutrient: protein 20–30%, carbohydrate 5–10%, fat 0–3% (up to 5%). TEF is the smallest TDEE component and is **invisible to wearable sensors** except via the small postprandial HR/skin-temperature signatures (M7, M12).
- **Evidence:** **E4/E5** (calorimetry literature consensus; Westerterp, *Nutr Metab* 2004, DOI 10.1186/1743-7075-1-5 — unverified ID).
- **Wearable verdict:** **(b/c)** latent EE component; only indirect thermal/HR proxy.
- **Implementation:** add postprandial EE elevation ≈ meal_kcal × TEF% distributed over 3–5 h (protein-rich meals longer/higher).

### M16. Activity energy expenditure (MET framework)
- **Claim:** MET values are population-mean intensities (1 MET = 3.5 mL O2/kg/min ≈ 1 kcal/kg/h); e.g., slow walk ~2.5–3 METs, brisk walk ~4–5, running 8 km/h ~8–9. Between-individual mechanical/metabolic efficiency varies ±20–30%, so MET-based EE for an individual carries that error. [E5; Compendium of Physical Activities — Ainsworth et al.]
- **Wearable verdict:** **(b) indirect** via accelerometer classification + MET lookup; error compounds with MET-level interindividual variance.

### M17. NEAT
- **Claim:** Non-exercise activity thermogenesis varies by hundreds of kcal/d between individuals and is largely invisible to wrist wearables (fidgeting, posture, low-amplitude movement). [E2/E4; Levine NEAT studies — secondary]
- **Wearable verdict:** **(c→b)** mostly latent; underestimate is a major driver of M14 errors. Synthetic personas need a latent NEAT trait (σ ≈ 150–300 kcal/d).

---

## SECTION 4. Substrate utilization & exercise

### M18. Fat vs carbohydrate oxidation across intensity (Fatmax / crossover)
- **Claim:** Absolute fat oxidation rises from low to moderate intensity, peaks (Fatmax), then falls to ~0 at high intensity (inverted-U); carbohydrate fraction rises monotonically (crossover concept).
- **Magnitude (Achten & Jeukendrup 2003, n=55 trained men, cycling, fasted):** maximal fat oxidation (MFO) 0.52 ± 0.15 g/min at Fatmax = 62.5 ± 9.8% VO2max (individual range ≈ 42–82% VO2max); fat oxidation negligible (Fatmin) at 86.1 ± 6.8% VO2max; day-to-day CV of Fatmax estimation ~9–9.5%. Untrained men: Fatmax ≈ 31% VO2max; large cohort (Venables): 45% (men), 52% (women) VO2max on treadmill. High carb availability/insulin blunts fat oxidation; training raises it.
- **Wearable verdict:** **(c) latent-only.** Requires indirect calorimetry (VO2+VCO2). HR can *roughly* locate an individual's Fatmax zone only after a personal calibration test; population HR-Fatmax mapping is unreliable given the 42–82% VO2max spread and HRmax error ±10 bpm. Do not fabricate a "fat-burning" signal from HR alone beyond zone heuristics.
- **Evidence:** **E4** (replicated quantitative; multiple cohorts).
- **Source:** Achten & Jeukendrup, *Int J Sports Med* 2003;24:603–8, PMID 14598198, DOI 10.1055/s-2003-43265; Achten & Jeukendrup, *Nutrition* 2004;20:716–27, DOI 10.1016/j.nut.2004.04.005; Riddell pubertal study, *J Appl Physiol* 2008, DOI 10.1152/japplphysiol.01256.2007.
- **Limitations:** stoichiometric (Frayn) equations underestimate fat oxidation above lactate threshold (bicarbonate pool shifts); fasted-state protocol inflates fat oxidation vs fed free-living.
- **Implementation:** latent substrate mix = f(relative intensity, fitness trait, fed/fasted state, sex); fat fraction curve: rise to peak ~0.5–0.6 g/min (trained) at persona Fatmax ~ N(50,10)% VO2max (untrained lower), zero by ~85–90%.

### M19. Respiratory exchange ratio (RER/RQ)
- **Magnitude:** rest (fasted, compliant prep) 0.75–0.95; low-intensity exercise 0.80–0.88; ≈1.0 near lactate/ventilatory threshold; maximal effort 1.05–1.20+. Elevated resting RER tracks recent feeding, hyperventilation, and insulin resistance (metabolic inflexibility: resting RER ~0.85–0.90, blunted fat oxidation). [E4; calorimetry consensus; korr/ADInstruments technical summaries are secondary]
- **Wearable verdict:** **(c) latent-only.** No wearable measures VCO2. Sweat lactate sensors are emerging research devices, not validated consumer signals.
- **Implementation:** latent RER drives EE partitioning and, optionally, a *simulated metabolic-cart channel* for validation scenarios only.

### M20. Lactate threshold vs ventilatory threshold vs HR
- **Claim:** LT and VT occur at similar but not identical intensities; correlation between methods r ≈ 0.67–0.95 depending on protocol and population; VT can estimate LT VO2 within ±0.2 L/min in ~80–95% of healthy individuals; HR at VT vs HR at LT share only ~45% variance (r=0.67, n=19 cyclists). VT is NOT caused by lactate per se (glycogen-depleted dissociation; McArdle patients show VT without lactate).
- **Wearable inference:** HRV-based VT estimation (DFA-α1, Kubios algorithm, n=64): error vs true VT −1 ± 11 bpm (VT1) and −1 ± 7 bpm (VT2) — promising but early. [E3; medRxiv 2024, DOI 10.1101/2024.08.14.24311967 — preprint, not peer-reviewed]
- **Wearable verdict:** thresholds **(b) indirectly inferable** from HR/HRV with ±7–16 bpm error; lactate itself **(c) latent**.
- **Evidence:** **E3/E4**.
- **Source:** Omiya et al. 2004, PMID 14566565, DOI 10.1007/s00421-003-0959-3; Plato et al. 2008, PMID 18214811, DOI 10.1055/s-2007-989453; Sullivan/Scherrer reproducibility, *Am J Cardiol* 1988 (sciencedirect 0002914988913720, unverified ID); Loat & Rhodes 1993 review, PMID 8446822.
- **Contradictory:** VT method choice (V-slope vs ventilatory equivalents) yields statistically different VT1 in some cohorts; irregular breathing biases visual detection.

### M21. HR–VO2 relationship and HRmax prediction
- **Claim:** HR–VO2 is approximately linear within an individual over ~40–85% VO2max, with nonlinearity (VO2 plateaus relative to HR) near maximum, more pronounced in fitter individuals. Between-person variability is the dominant problem: HRmax prediction error SD ≈ 10–12 bpm (Fox 220−age), ~10 bpm (Tanaka 208−0.7·age); limits of agreement span ~44 bpm; adding sex/fitness/mode variables improves prediction negligibly.
- **Magnitude:** Tanaka meta-analysis: 351 studies, 18,712 subjects → 208 − 0.7·age, SEE ~10 bpm. HRI (HR index = HR/HRrest) VO2 prediction underpredicts VO2max by ~1 MET; error worse in fit individuals. Two healthy 40-year-olds can differ by 40 bpm in true HRmax.
- **Wearable verdict:** HR **(a) directly measurable**; VO2 **(c) latent**; HR→VO2 transfer **(b) indirect, person-specific** — requires individual calibration (resting HR, known HRmax or submax test); population-level HR→EE inference carries M14-scale error.
- **Evidence:** **E5** (Tanaka meta-analysis) / **E4** (HR-VO2 linearity replicated).
- **Source:** Tanaka et al., *JACC* 2001, PMID 11153730 (secondary-verified), DOI 10.1016/S0735-1097(00)01054-8; HERITAGE equation comparison PMC3935487; university validation PMC7523886; HRI paper (WKU IJES, unverified ID).
- **Implementation:** per-persona HR–VO2 slope with latent VO2max; HRmax = 208−0.7·age + N(0, 10 bpm); near-max nonlinearity factor for fit personas.

---

## SECTION 5. Fasting (12–72 h)

### M22. Acute 24-h fast: cardiovascular/autonomic effects
- **Claim:** 24-h fasting in young healthy normotensives reduces ambulatory MAP ~−2 mmHg (81→78) and HR ~−4 bpm (69→65), increases vagal HRV (RRI 992→1059 ms; HFnu 55→62%), cardiovagal baroreflex sensitivity (+30%), and estimated stroke volume (+13%), with no change in muscle sympathetic nerve activity.
- **Magnitude:** systolic −2 ± 1, diastolic −2, MAP −2 ± 1 mmHg (ambulatory, driven by wake values; sleep BP unchanged). [E3, n=25 randomized crossover; PMC9512108]
- **Wearable verdict:** HR/HRV changes **(a) directly measurable** but small (ΔHR −4 bpm ≈ within-day HR noise); BP change below cuffless-BP resolution → effectively latent.
- **Source:** Petersen/"Influence of an acute fast on ambulatory blood pressure and autonomic cardiovascular control", *Am J Physiol Regul Integr Comp Physiol*-era 2022 (PMC9512108; unverified journal/PMID).
- **Contradictory:** female-only 24-h fast study (Herbert) reported *decreased* HFnu — direction of vagal shift may be sex/protocol dependent.

### M23. 36–72 h fast: sympathetic activation and metabolic rate
- **Claim:** As fasting extends past ~36 h: HR and plasma epinephrine/norepinephrine rise (72-h values significantly above 12-h overnight fast; BP unchanged); resting metabolic rate transiently *increases* ~day 1.5–2 (gluconeogenesis/ketogenesis cost + catecholamines), then falls below baseline with prolonged fasting (≈ −15% by ~day 10, −25% by day 30 in classic starvation series). Forearm blood flow increases at 36/72 h.
- **Evidence:** **E3** (Webber & Macdonald 1994, n=29, 12/36/72-h design — secondary verification via doctoral thesis; classic starvation data secondary via Virta review — treat as E2 historical). Insulin falls continuously over first 30 h; glucagon rises over 72 h (Højlund 2001, secondary).
- **Wearable verdict:** HR trajectory **(a) measurable**: expect U-shaped — slight fall at 24 h, rise by 48–72 h (+3–6 bpm vs fed baseline, magnitude from secondary sources — flag as approximate). Catecholamines **latent**.
- **Implementation:** fasting HR(t) piecewise: −4 bpm at 24 h → baseline at ~36–48 h → +3–6 bpm at 72 h; RMR(t): +3–5% at 36–48 h → declining after day 3.
- **Contradictory/null:** long-term Buchinger fasting (12 d, 250 kcal/d, n=16): HR unchanged (67→69 bpm, ns), SBP −6.9 mmHg, RMSSD ↑ post-fast — chronic protocols differ from acute total fasting (PMC12532600).

### M24. Ketones (β-hydroxybutyrate) during fasting
- **Magnitude:** BHB ≈ 0.1–0.2 mM after 12-h overnight fast; ≈0.66 ± 0.07 mM after 36 h; ≈2.6 mM after 60 h; asymptotes ~5–7 mM with multi-day starvation; women higher than men at matched fast duration. [E2/E3; case series n=1 PMC11085973 + classic literature secondary]
- **Wearable verdict:** **(c) latent-only** for standard wearables (breath-acetone consumer devices exist but unvalidated vs blood BHB; do not simulate as a reliable signal).

### M25. Fasting and orthostatic tolerance
- **Claim:** Fasting blunts vasoconstrictor defense of central hypovolemia: during LBNP, fasted subjects fail to raise total peripheral resistance and show slower MSNA ramp (significant only at 80%→presyncope vs 40% fed); tilt after 24–48-h fast shows greater vagal withdrawal (↓RRI, SDNN, HF) and larger HR responses after 72 h. Direction: **reduced orthostatic tolerance when fasted**, modest magnitude, small-n evidence.
- **Evidence:** **E3** (n=7–25 mechanistic studies; PMC9512108 thesis companion; Mazurak 2013 & Brown 2012 secondary).
- **Wearable verdict:** observable only as larger ΔHR on standing while fasted **(a/b)**; do not simulate orthostatic BP drops beyond ±5–10 mmHg without pathology persona.

---

## SECTION 6. Sleep–metabolism links

### M26. Sleep restriction → insulin sensitivity (controlled)
- **Claim:** 1 week of 5 h/night sleep restriction reduces insulin sensitivity ~−20% (IVGTT) and −11% (hyperinsulinemic-euglycemic clamp) in healthy men, without compensatory insulin secretion increase.
- **Magnitude:** IVGTT SI −20 ± 24% (15/19 subjects decreased, p=0.001); clamp M-value −11 ± 5.5% (90% of subjects decreased, p=0.045); salivary cortisol +51 ± 8%. Single night of partial sleep deprivation already induces measurable insulin resistance (↑ endogenous glucose production, ↓ glucose disposal; Donga 2010, clamp, n=9). Sleep fragmentation 2 nights → ↓SI + ↑ sympathetic activity (n=11).
- **Timescale:** effect detectable after 1 night; dose-dependent over days; reverses with recovery sleep.
- **Wearable verdict:** insulin sensitivity **(c) latent**; downstream correlates **(b)**: next-day fasting glucose +5–15 mg/dL (secondary CGM reports), elevated evening/nocturnal HR, reduced HRV — all small and confounded.
- **Evidence:** **E3** (multiple independent controlled lab studies, consistent direction).
- **Source:** Buxton et al., *Diabetes* 2010;59:2126–33, PMID 20585000, DOI 10.2337/db10-0696; Spiegel et al., *Lancet* 1999 (sleep debt, 11 men, ↓glucose tolerance 30–40%); review PMC3132857; Tsereteli et al., *Diabetologia* 2022;65:356–65, PMID 34845532 (PREDICT: insufficient sleep → dysregulated postprandial glucose under standardized meals).
- **Contradictory/null:** Spiegel 1999 (4 h/night × 6) found ↓glucose tolerance/effectiveness but only *nonsignificant* SI reduction — mechanism (peripheral SI vs glucose effectiveness vs secretion) differs by protocol; 2-week restriction with ad-lib food showed leptin/ghrelin effects abolished by compensatory eating (Nedeltcheva).
- **Implementation:** sleep-debt persona state variable accumulating over nights; apply −10 to −20% insulin-sensitivity multiplier after ≥2 short nights; raise next-morning glucose baseline +5–10 mg/dL; small nocturnal HR elevation (+2–4 bpm) and RMSSD reduction (−10–20%) as observable correlates (mark magnitudes as E2-level estimates).

### M27. Sleep restriction + circadian disruption (shift-work model) → RMR and postprandial glucose
- **Claim:** 3 weeks of 5.6 h/24 h sleep with recurring 28-h days: RMR −8% (~120 kcal/d), fasting glucose +8%, postprandial glucose peak +14% (AUC +15%), driven by *decreased* insulin (fasting −12%, postprandial peak −27%, integrated −27% — beta-cell under-responsivity); 3/21 participants reached prediabetic 2-h glucose; all reversed with 9-day recovery.
- **Wearable verdict:** glucose effects observable **(a) only with CGM**; RMR latent; wearable-detectable proxies: sleep duration (actigraphy) + elevated post-breakfast glucose excursion.
- **Evidence:** **E3** (single landmark inpatient RCT; n=21 completers, both young and older).
- **Source:** Buxton et al., *Sci Transl Med* 2012;4:129ra43, PMID 22496545, DOI 10.1126/scitranslmed.3003200 (PMC3678519).
- **Limitations:** extreme laboratory protocol exceeds typical social jet lag; weight loss (−1.2%) a partial confound (though uncorrelated with metabolic changes in-model).

### M28. Circadian misalignment per se (controlled, sleep held adequate)
- **Claim:** Maximal misalignment (12 h out of phase, 10-d forced desynchrony, n=10): glucose +6% (mostly postprandial) *despite* insulin +22% → insulin resistance; leptin −17%; MAP +3% during wake; 3/8 with postprandial glucose in prediabetic range; cortisol rhythm inverted.
- **Time-of-day effect (isocaloric identical meal):** postprandial glucose +6.5% at 20:00 vs 08:00 (endogenous circadian), with early-phase insulin −18% (beta-cell dysfunction in biological evening); misalignment adds +5.6% glucose via reduced insulin sensitivity (late-phase insulin +10%). [n=14 crossover]
- **Wearable verdict:** glucose **(a) CGM**; circadian phase itself latent (inferable only from sleep/activity/light patterns).
- **Evidence:** **E3** (two independent forced-desynchrony/crossover lab studies).
- **Source:** Scheer et al., *PNAS* 2009;106:4453–8, PMID 19255424, DOI 10.1073/pnas.0808180106; Morris et al., *J Clin Endocrinol Metab* 2016;101:1066–74, DOI 10.1210/jc.2015-3924 (PMC4803172; PMID unverified).
- **Implementation:** glucose tolerance multiplier by local/biological time-of-day: evening meals → +6–17% postprandial glucose; shift-worker persona with combined sleep restriction + misalignment compounds M26–M28.

---

## SECTION 7. Thermoregulation–metabolism

### M29. Cold-induced thermogenesis (CIT), mild cold
- **Claim:** Mild non-shivering cold exposure raises EE ~5–10% with large interindividual variability.
- **Magnitude:** whole-room calorimetry + 18F-FDG PET (n=24 completers): EE +5.3 ± 5.9% (p<0.001); women +9.1 ± 4.3% vs men +2.3 ± 5.3% (p=0.002) at ~19°C personalized exposure. Literature range for CIT ≈ 2–30%; ~10% typical.
- **Wearable verdict:** **(b) indirect at best** — EE rise is below wearable EE error floor (M14); skin temperature falls at extremities and supraclavicular temperature is a *research proxy* for BAT, not a validated consumer signal. BAT glucose uptake **(c) latent** (PET-only).
- **Evidence:** **E3**.
- **Source:** Patel/Muzik-group mild-cold PET study, *J Clin Endocrinol Metab* 2013 (PMC3701264; unverified PMID); meta-analysis PMC9273773 (BAT activity ↑ with cold, SMD 1.26–1.58).

### M30. Brown adipose tissue in adults & cold acclimation
- **Claim:** Metabolically active BAT is present in a substantial fraction of adults (inversely related to BMI/age/outdoor temperature); 10-day cold acclimation increases non-shivering thermogenesis from 10.8 ± 7.5% to 17.8 ± 11.1% (p<0.01) with parallel BAT recruitment, **without changing RMR**; 6-week daily 17°C exposure (2 h/d) increased BAT activity and CIT and decreased body fat mass.
- **Magnitude:** acute cold EE +11% pre-acclimation → +18% post; no skeletal-muscle mitochondrial uncoupling contribution detected.
- **Wearable verdict:** **(c) latent-only** (18F-FDG PET/CT required). Do not simulate a "BAT activity" wearable channel.
- **Evidence:** **E3/E4** (multiple independent PET-CT cohorts; NEJM 2009 trilogy established adult BAT).
- **Source:** van der Lans et al., *J Clin Invest* 2013;123:3395–403, PMID 23867626, DOI 10.1172/JCI68993; Yoneshiro et al., *J Clin Invest* 2013;123:3404–8; van Marken Lichtenbelt et al., *NEJM* 2009;360:1500–8, DOI 10.1056/NEJMoa0808718 (secondary-verified); Cypess NEJM 2009;360:1509–17 (secondary).
- **Contradictory/null:** beta-adrenergic blockade does NOT abolish human CIT (Wijers 2011) — mechanism not purely adrenergic; systemic beta-3 stimulation failed to activate BAT (Vosselman 2012) — pharmacological translation weak.

### M31. Heat acclimation / passive heat metabolic effects
- **Claim:** Passive heat acclimation in overweight humans improves glucose metabolism and shifts substrate toward fat oxidation (↓glucose oxidation); active (exercise) heat acclimation similarly reduces muscle glycogen use. [E3; PMC7379279, *J Appl Physiol* 2020-era]
- **Wearable verdict:** latent metabolic effect; observable proxies: reduced exercise HR at fixed workload, ↑ sweat rate — these are cardiovascular/thermoregulatory, not metabolic-specific (confounded).
- **Limitations:** small samples; substrate shift mechanism not fully resolved.

---

## SECTION 8. Metabolic dysfunction phenotypes (insulin resistance → T2DM)

### M32. Resting autonomic phenotype of T2DM / cardiac autonomic neuropathy (CAN)
- **Claim:** T2DM (even <5 y duration, and partly prediabetes) shows resting tachycardia and globally reduced HRV vs matched healthy controls; both sympathetic and parasympathetic arms are reduced; severity scales with disease duration.
- **Magnitude:** cross-sectional (n=160 T2DM + 40 controls): resting HR significantly ↑ in early (<5 y) and >10 y groups; RMSSD, NN50%, HF power significantly ↓ in all diabetic subgroups (D1 3.13 ± 0.91, D2 7.33 ± 0.97, D3 13.7 ± 1.65 — duration index); SDNN diabetes vs control ≈ 30.1 ± 14.4 vs 36.2 ± 15.5 ms (Park study, cited); poor control (HbA1c ≥8%): SDNN 26.6 vs 42.3 ms. LF/HF unchanged until late (D3 ↑).
- **Wearable verdict:** **(b) indirectly inferable** — elevated resting HR (+5–10 bpm typical), reduced RMSSD/SDNN are wearable-observable (PPG-HRV at night is the cleanest window) but **non-specific** (confounded by fitness, age, stress, sleep, alcohol). Cannot diagnose IR from HRV alone; use as a persona phenotype modulator.
- **Evidence:** **E2/E4** (consistent across cohorts; no large meta-analysis located in Pass 1 — flag for Pass 2).
- **Source:** *Cardiac autonomic dysfunctions in T2DM*, PMC9490161 (2022); HRR-diabetes review PMC3681282.

### M33. Exercise response in T2DM: chronotropic incompetence and blunted HRR
- **Claim:** T2DM shows lower peak HR (chronotropic incompetence), lower chronotropic index, and slower heart-rate recovery vs non-diabetic controls at matched testing.
- **Magnitude:** CPET registry: chronotropic index 7.88 ± 3.19 (T2DM) vs 10.91 ± 2.75 (controls), p<0.001; peak HR significantly lower; HRR abnormal thresholds: <12 bpm at 1 min, <22 bpm at 2 min (standard clinical cutoffs); diabetic microalbuminuria subgroup: peak HR 142.7 ± 25.6 vs 157.5 ± 20.6 bpm; HRR1 23.6 ± 13.0 vs 31.0 ± 15.5 bpm (ns trend). 12-week exercise training partially reverses (rHR, HRRes, HRR1–6, peak VO2 all ↑).
- **Wearable verdict:** **(b) indirectly inferable** during exercise — blunted HR rise and slow 1-min recovery are observable with accurate HR; specificity limited by medications (beta-blockers!), deconditioning.
- **Evidence:** **E3/E4**.
- **Source:** PMC11994578 (2025); PMC5403443 (2017); PMC3681282; HFpEF CI study PMC12449948 (context).

### M34. Postprandial phenotype in dysglycemia/T2DM
- **Claim:** Postprandial glucose peaks are higher, later, and more prolonged across the IR→prediabetes→T2DM spectrum; GV metrics already elevated in normoglycemic future-converters (M3: SD 18 vs 13, CV 17 vs 14, MAGE 36 vs 27). T2DM commonly exceeds 180 mg/dL post-meal with delayed (>90 min) peaks and slow return; PPH prevalence 20–40% in T2DM with autonomic involvement (vs ~0 in healthy young) and HR compensation is absent (M10).
- **Wearable verdict:** glucose pattern **(a) CGM**; HR/BP phenotype **(b)**.
- **Evidence:** **E2/E4**.
- **Source:** Rodríguez García 2025 PMID 40160400; PPH prevalence synthesis PMC9964048; ZOE PREDICT post-menopause PPG data (Bermingham 2022, cited in PMC12612783): 2-h glucose AUC +42% post- vs pre-menopause.

### M35. Metabolic inflexibility (insulin resistance substrate phenotype)
- **Claim:** Insulin-resistant/obese individuals show elevated resting RER (~0.85–0.90), reduced fasting fat oxidation, and blunted meal-induced suppression of lipid oxidation ("metabolic inflexibility"); exercise Fatmax shifts to lower intensity and lower MFO. [E1/E2 — concept well replicated mechanistically (Kelley & Mandarino line of work, secondary in Pass 1); precise population magnitudes flagged for Pass 2]
- **Wearable verdict:** **(c) latent-only** (requires calorimetry); do not infer from HR.

### M36. Orthostatic effects in autonomic neuropathy
- **Claim:** Diabetic CAN/autonomic failure: orthostatic hypotension (SBP drop ≥20 mmHg), resting tachycardia, exercise intolerance, prolonged QT, silent ischemia; postprandial + orthostatic stress compound (splanchnic pooling unopposed). Postprandial tilt SBP falls 40–113 mmHg in severe T1D autonomic neuropathy series. [E2/E3; PMC3681282; Chinese T1D tilt study (secondary)]
- **Wearable verdict:** **(b)** — standing ΔHR and ΔBP patterns observable in principle; cuffless BP precision inadequate for ≤20 mmHg thresholds (flag).

---

## SECTION 9. Observability-verdict master table

| # | Variable | Verdict | Wearable modality & sampling | Expected error | Main confounders | Artifacts that mimic |
|---|----------|---------|------------------------------|----------------|------------------|----------------------|
| 1 | Blood/interstitial glucose | **(a) CGM only** | interstitial electrochemical, 1–5 min | MARD 8–13%; lag 5–15 min; bias −5–10 mg/dL (healthy range) | meals, exercise, stress, circadian, sleep | compression lows; rate-of-change error >1 mg/dL/min; day-1 sensor error |
| 2 | Glucose via optical PPG/EDA | **(c) effectively latent** | none validated | MAE ≥13–26 mg/dL in small studies; no field-valid device | everything (motion, hydration, temperature) | any PPG morphology change |
| 3 | Insulin / beta-cell function | **(c) latent** | none | n/a | — | — |
| 4 | Postprandial HR rise | **(a) direct (PPG/ECG)** | 1-min HR | ±1–3 bpm device error | posture, activity, caffeine, stress | exercise, stress tachycardia, alcohol |
| 5 | Splanchnic blood flow | **(c) latent** | none (drives HR signal) | n/a | — | — |
| 6 | Postprandial BP change / PPH | **(b) weak-indirect** | cuffless PPG-BP not validated for this | ±5–10 mmHg (exceeds young-adult signal) | medications, posture, age | cuff calibration drift |
| 7 | Postprandial skin temperature | **(b) indirect** | skin thermistor, 1–5 min | ±0.1–0.3 °C sensor; physiology lag 1–3 h | ambient temperature, menstrual phase | environmental heat, fever |
| 8 | Postprandial EDA | **E1 — unproven; treat as latent** | EDA 1–10 Hz | unknown | stress, ambient humidity | stress/startle responses |
| 9 | RMR | **(b) equation-indirect** | none direct | ±10% (82% of people); up to ±25% outliers | thyroid, adaptation, body composition | — |
| 10 | Activity/total EE | **(b) indirect, error-prone** | HR+accelerometer fusion | MAPE 20–35%; DLW bias ≈ −7%; LoA −750/+400 kcal/d | activity type, fitness, NEAT | arm-motion artifacts (cycling undercount; resistance training near-random) |
| 11 | TEF | **(c→b) latent component** | none direct | ~10% of intake | meal composition | appears only inside EE noise |
| 12 | RER / fat-vs-carb oxidation | **(c) latent** | none | n/a | — | — |
| 13 | Fatmax / thresholds (LT/VT) | **(b) indirect** | HR/HRV (DFA-α1) | ±7–16 bpm at VT | protocol, breathing pattern | ectopy, HRV artifacts |
| 14 | VO2max / VO2 | **(c) latent; (b) with calibration** | HR-based estimate | ±1 MET even with HR-index models | HRmax error ±10–12 bpm | wrist PPG dropout at high intensity |
| 15 | Fasting state (24–72 h) | **(b) via HR/HRV trend** | PPG-HR, nocturnal HRV | ΔHR ±3–6 bpm signal vs noise | sleep, caffeine, illness | overtraining, illness, alcohol withdrawal |
| 16 | Ketones (BHB) | **(c) latent** | none validated | n/a | — | — |
| 17 | Sleep-restriction insulin resistance | **(c) latent; (b) proxies** | sleep actigraphy + CGM | SI effect −10–20%; glucose proxy +5–15 mg/dL | diet, activity | travel, stress |
| 18 | Circadian phase/misalignment | **(b) weak-indirect** | sleep/light/activity timing | hours-scale error | social schedule | jet lag vs insomnia |
| 19 | BAT activity / CIT | **(c) latent** | none (supraclavicular skin temp = research proxy only) | CIT 5–10% EE (below EE error floor) | season, clothing | — |
| 20 | CAN / IR autonomic phenotype | **(b) indirect, non-specific** | nocturnal PPG-HRV, resting HR, exercise HRR | SDNN effect ~−6 to −15 ms; resting HR +5–10 bpm | fitness, age, meds, sleep, alcohol | beta-blockade mimics; athlete bradycardia opposite |

---

## SECTION 10. Cross-cutting implementation & validation recommendations

1. **Architecture:** latent metabolic state vector (glucose, insulin, RER, splanchnic flow, BAT, ketones, insulin sensitivity, circadian phase) → documented transfer functions → observable channels (HR, HRV, skin temp, EDA [weak], accel) → device error models (CGM MARD/lag; PPG-HR motion artifact; EE MAPE 20–35%; cuffless-BP ±5–10 mmHg). Never expose latent variables as "sensor" channels.
2. **Persona parameters to randomize:** glucotype (M1–M3), insulin sensitivity (M26 effects), Fatmax ~ N(50,10)%VO2max with fitness correlation (M18), HRmax residual N(0,10 bpm) (M21), NEAT trait σ 150–300 kcal/d (M17), autonomic-neuropathy severity (M32–M34, M36), age-dependent PPH slope (M10), sex (postprandial skin-temp & CIT effects, M12/M29; ketones higher in women, M24).
3. **Timescale library:** PPG glucose excursion (0–3 h); postprandial HR (0–4 h); TEF (0–5 h); dawn phenomenon (04:00–08:00); fasting transitions (12→24→36→72 h piecewise, M22–M24); sleep-debt accumulation (1–7 nights, M26); circadian misalignment (days, M27–M28); cold acclimation (days–weeks, M30).
4. **Validation battery:** (i) synthetic CGM norms vs Shah 2019 percentiles; (ii) PPG curves vs Freckmann Table 3; (iii) GV distributions vs AEGIS; (iv) wearable-EE vs latent-EE MAPE 20–35%; (v) postprandial ΔHR vs Waalen/geriatric series; (vi) sleep-restriction personas show −10–20% SI and +5–15 mg/dL fasting glucose; (vii) T2DM personas: resting HR +5–10 bpm, SDNN −6–15 ms, HRR1 <12 bpm fraction ↑, PPG peaks >180 mg/dL delayed.
5. **Known gaps for Pass 2:** (a) no large meta-analysis of HRV in T2DM/CAN located (estimates from cross-sectional cohorts); (b) quantitative healthy dawn-phenomenon magnitude poorly characterized; (c) metabolic-inflexibility population magnitudes (resting RER distributions by IR status) not yet extracted from primary sources; (d) postprandial EDA essentially unstudied — keep at E0/E1; (e) orthostatic-tolerance fasting effect sizes from n≤25 studies only; (f) several classic sources (Webber & Macdonald 1994; Keys/Benedict starvation series; Westerterp TEF 2004) are secondary-verified — pull primary PDFs in Pass 2 before locking numbers.

*End of Pass 1 deliverable. All PMIDs/DOIs given were cross-checked against at least one authoritative record in search results; items explicitly marked "secondary" or "unverified ID" must not be cited as fully verified.*
