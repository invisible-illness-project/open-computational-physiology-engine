# OCPE — Population Model Evidence: Distributions, Correlations, and Variance Structure

**Role:** Population Modeling Scientist. **Scope:** evidence-based marginal distributions, joint/correlation structure, variance decomposition, covariate models, disease-severity distributions, comorbidity co-occurrence, latent-variable architecture, and sampling-design guidance for a synthetic physiological population.

**Evidence levels:** E0 hypothesis / E1 mechanistic / E2 observational human / E3 controlled human experimental / E4 replicated quantitative / E5 meta-analysis/consensus.

---

## A. Marginal distributions (healthy adults)

### A.1 Resting heart rate (RHR)

| Measure | Value | n | Source | E-level |
|---|---|---|---|---|
| Daily RHR (Fitbit, free-living), all adults | 65.5 ± 7.7 bpm; individual mean range 39.7–108.6 | 92,457 | Quer et al. 2020, *npj Digit Med* (PMC7001906) | E2 |
| 95% central range | Men 50–80 bpm; Women 53–82 bpm | 92,457 | Quer et al. 2020 | E2 |
| Seated / supine / sleep RHR | 67.6 ± 9.8 / 63.5 ± 8.9 / 56.9 ± 6.9 bpm | ~7,000 (Fenland) | Gonzales et al. 2023, *PLOS Med* (PMC10174582) | E2 |
| Sex difference | Women +~3 bpm at all ages | 92,457 | Quer 2020; confirmed NHANES I (PMC1403631) | E4 |
| Age shape | Rises to ~50 y, then declines (inverted-U); Fitbit peak: women 40–49 y = 67.4 bpm, men 40–49 y = 64.6 bpm | 92,457 | Quer 2020; Fitbit 2018 | E2 |
| Covariate explained variance | Sex alone 4%; sex+age 6%; sex+BMI 7%; sex+sleep 5%; all four together ≤10% of between-person RHR variance | 92,457 | Quer 2020 | E2 |
| BMI relationship | U-shaped, nadir BMI ~21 (women), ~23 (men) | 92,457 | Quer 2020 | E2 |
| Sleep duration relationship | Minimum RHR at 7–7.5 h average sleep | 92,457 | Quer 2020 | E2 |
| Seasonality | Population mean swings ~2 bpm over year (peak early Jan, trough late Jul) | 92,457 | Quer 2020 | E2 |
| Device-definition offset | Daytime rest vs nocturnal RHR differ by ~3.9 bpm (54.5 vs 50.5 bpm; 433 adults, 19,242 days); SWS HR 3.5% below REM | 433 | Speed et al. via sahha.ai synthesis | E2 |

**Modeling note:** RHR distributions are device/definition dependent (±4–8 bpm offsets between "awake rest", "sleep average", "sleep minimum"). Tag the definition in the synthetic data model.

### A.2 HRV — RMSSD (10-s resting ECG, Lifelines; the best-powered age/sex reference)

Lifelines Cohort, n=84,772 healthy (59.5% women; mean age 40.8, range 13–91). Source: Tegegne et al. 2020, *Front Physiol* (PMC7734556). E2 (very large population cohort). Values = median (2nd; 98th percentile), ms. Women/men:

| Age | Women median RMSSD (2nd;98th) | Men median RMSSD (2nd;98th) |
|---|---|---|
| 13–14 | 66.5 (17.4; 232.2) | 67.4 (12.8; 213.0) |
| 15–19 | 60.7 (12.4; 225.9) | 59.9 (9.8; 213.2) |
| 20–24 | 52.1 (11.3; 205.5) | 47.6 (9.6; 174.0) |
| 25–29 | 47.5 (11.5; 180.7) | 42.3 (10.1; 172.7) |
| 30–34 | 42.3 (11.5; 161.0) | 36.9 (10.2; 140.8) |
| 35–39 | 37.9 (10.8; 141.9) | 32.8 (8.6; 123.8) |
| 40–44 | 33.9 (9.7; 123.7) | 29.0 (8.1; 105.5) |
| 45–49 | 29.2 (8.3; 109.5) | 26.0 (7.1; 95.5) |
| 50–54 | 26.6 (7.5; 96.3) | 23.7 (6.7; 87.5) |
| 55–59 | 22.5 (6.7; 83.6) | 21.0 (5.5; 89.5) |
| 60–64 | 20.5 (5.5; 79.3) | 19.1 (4.8; 86.6) |
| 65–69 | 17.8 (5.0; 83.0) | 17.7 (4.9; 110.5) |
| 70–74 | 18.3 (5.0; 115.8) | 16.0 (4.7; 161.9) |
| 75+ | 16.1 (3.5; 106.2) | 14.9 (3.7; 130.3) |

Key features (E2/E4):
- RMSSD is strongly right-skewed (mean >> median; e.g. women 20–24: mean 64.7 vs median 52.1 ms) → **model ln(RMSSD) ~ Normal**.
- Decline is steep to ~60 y then flattens; the *upper* (98th) percentile drops sharply to 60 y then re-widens (survivor/arrhythmia heterogeneity).
- Women > men by ~5.0 ms (median) at ages 20–45; ~2.5 ms at 45–59; no sex difference <20 or >60 y.
- Corrected RMSSD (cRMSSD = RMSSD/mean IBI, %) removes much of the HR dependence (van Roon et al. 2016, *Hypertension* 68:e63–65).

### A.3 HRV — SDNN / 24-h and 5-min norms

| Measure | Value | n | Source | E |
|---|---|---|---|---|
| 24-h SDNN by decade (95% range, ms): 20s 93–257; 40s 79–219; 60s 68–186; 90s 53–147 | declines to ~60% of 20s baseline by 10th decade | 260 | Umetani et al. 1998, *JACC* | E2 |
| 24-h rMSSD declines most rapidly, ~47% of baseline by 6th decade then plateaus | 260 | Umetani 1998 | E2 |
| 24-h SDNN, age 25–41 | Men 160 ± 40 ms; Women 147 ± 36 ms | 2,079 | Aeschbacher et al. (in PMC5624990) | E2 |
| 24-h Holter, mean age 63.6 | SDNN median 141 ms [IQR 119–165]; LF/HF median 3.92; LF/HF men 5.15 vs women 3.37 | 505 | KORA F3 (epub.ub.uni-muenchen.de s10654-025-01248-3) | E2 |
| 5-min supine HRV age×sex reference tables | sdNN, rmssd, pNN50 etc. by decade; steepest decline 35–54 | 1,906 | KORA S4, Voss et al. (PMC4378923) | E2 |
| Short-term RMSSD meta-norm | ~42 ms, normal range 19–75 ms | 21,438 | Nunan et al. 2010 (via FitCraft synthesis) | E5 |
| Meta-analysis, 50 HRV measures | Women: higher mean HR, lower SDNN/SDNNi, lower TP/VLF/LF, higher HF | 296,247 | Koenig & Thayer 2016 (in PMC5624990) | E5 |

Age decline summary: parasympathetic indices (RMSSD, pNN50) fall steeply 2nd→5th–6th decade (to ~25–50% of young-adult values) then plateau or (some 24-h series) U-turn after 70; global indices (SDNN, SDANN) decline roughly linearly (~5–10%/decade early, slowing later). Largest single-decade drop: 20s→30s (Bonnemeier 2003; Umetani 1998). (E4, replicated.)

### A.4 Blood pressure

| Measure | Value | n | Source | E |
|---|---|---|---|---|
| Mean SBP/DBP, US adults | 127/79 mmHg overall; women 124/77; men 130/82 | 6,667 | NHANES II (Sci.Direct S0895706106005693) | E2 |
| Median SBP by age | 115 mmHg (18–29 y) → 145 mmHg (60–74 y) | NHANES III | Handler et al. (PMC3491581) | E2 |
| SBP–DBP correlation | r = 0.717 | 6,667 | NHANES II | E2 |
| Hypertensive subpopulation means (for disease arm) | SBP 139 (137–140), DBP 77 (76–79), 2017–18 | ~2,094/cycle | NHANES trends (PMC7489367) | E2 |

Age model: SBP rises monotonically (steeper after 50); DBP rises to ~50–60 then falls (pulse pressure widens). (E5 consensus epidemiology; NHANES medians above.)

### A.5 Stroke volume / cardiac output / indexing

| Measure | Value | Source | E |
|---|---|---|---|
| Resting CO | 4–8 L/min (>60 y: 3.1–6.4) | clinical reference consensus (Radiopaedia/StatPearls NBK539905) | E5 (textbook consensus) |
| Cardiac index | 2.5–4.0 (2.2–4.1) L/min/m²; >60 y 2.1–3.2 | same | E5 |
| Stroke volume | 60–100 mL | same | E5 |
| SV index | 33–47 mL/m² (some refs 35–65) | same | E5 |
| Mean BSA | Men 1.9 m², women 1.6 m² | StatPearls | E5 |

**Indexing/allometry (E2/E4):**
- SV and CO associate more strongly with fat-free/lean mass than with BSA or weight (Strong Heart Study; CMR cohort studies) — recommend scaling SV, CO to **lean body mass** where available; else BSA with population allometric exponents.
- Allometric exponents (population cohort n=1,509, healthy subgroup n=656; Kuznetsova/Haddad group, J Hypertens 2016, PMID 27035735): LV end-diastolic dimension ~ height¹ (BSA^0.5, LBM^0.33); LVEDV ~ height^2.9; LV mass ~ height^2.7; LA volume ~ height^2.0; BSA exponents 1.7–1.8; LBM exponents ≈1.
- CMR study (KU Leuven): CO allometric coefficient to body size ~0.55 ± 0.04; SV strongly size-dependent; LVEF essentially size-independent (men ~4.2% lower than women).
- BSA indexing **overcorrects in obesity** (driven by fat mass) → index volumes/mass to height^2.7 or LBM in obese synthetic individuals.

### A.6 Respiration rate (KORA-FF4, n=2,224 adults, E2)

Median (5th;95th percentile), breaths/min, by age/sex (PMC11896064):

| Age | Men | Women |
|---|---|---|
| 39–48 | 15.4 (11.4;19.3) | 15.8 (12.1;19.6) |
| 49–58 | 15.2 (11.6;19.9) | 15.3 (11.8;19.7) |
| 59–68 | 15.7 (12.3;20.3) | 15.9 (12.3;19.8) |
| 69–78 | 16.3 (12.8;20.4) | 16.1 (12.8;19.9) |
| 79–88 | 16.9 (12.9;20.8) | — |

~13.8% of adults ≥18.6 brpm. Weak positive age gradient; minimal sex difference. (Test-retest ICC for RR 0.77–0.96 over 7 days; Guijt et al. 2007, n=26 — E3.)

### A.7 Temperature

| Measure | Value | n | Source | E |
|---|---|---|---|---|
| Core temp population mean | ~36.6–37.0 °C; individual means vary; oral 36.8 ± 0.7 °C; observed healthy oral range 33.2–38.2 °C | classic series (Mackowiak; Sund-Levander) | E4 |
| Core circadian excursion | ~0.5–1.0 °C (nadir ~2 h before habitual wake; peak late afternoon/early evening) | chronobiology consensus | E4 |
| Wrist (distal) skin temp mesor / amplitude | Young women: 33.2 °C / 1.44 °C; older women: 33.1 °C / 1.16 °C (18–19% amplitude ↓, acrophase advanced 66–73 min with age) | 65 | Herold & Cajochen group, *Geroscience* (MDPI 2308-3417/9/4/102) | E3 |
| Distal forearm skin temp | M5 (max 5-h) 35.1 °C; L10 (min 10-h) 31.4 °C | 2,187 | Tai et al. 2023, *J Clin Sleep Med* (PMC10315598) | E2 |
| Wrist temp amplitude population SD | 0.9 °C (2 SD = 1.8 °C) | ~90k (UK Biobank) | Skarke/la Fleur et al. 2023 (PMC10449859) | E2 |

### A.8 Electrodermal activity (tonic SCL)

| Measure | Value | Source | E |
|---|---|---|---|
| Tonic SCL | Range 1–40 µS; typical average 2–16 µS (palmar) | Venables & Christie 1980; Boucsein 2012 | E4 (textbook psychophysiology consensus) |
| NS-SCR rate | ~1–3/min at rest; up to 20–25/min high arousal | Boucsein 2012 | E4 |
| Phasic SCR amplitude | threshold to ~2–3 µS | Boucsein 2012 | E4 |

**No large-population age/sex-stratified SCL percentile tables exist** (explicit gap, E0 for any such stratification). SCL is highly context-, temperature- and site-dependent; treat as wide lognormal with strong within-day state dependence.

### A.9 Activity (steps/day)

| Measure | Value | n | Source | E |
|---|---|---|---|---|
| UK Biobank wrist (stepcount ML algorithm) | Median 9,076 steps/day [IQR 6,844–11,687] | 85,394 | *Am J Med* 2023 (PMC12242917) | E2 |
| UK Biobank mortality subsample | Median 6,222 [IQR 4,102–9,225] (different algorithm/cut) | 72,174 | munideporte-hosted paper | E2 |
| NHANES 2005–06 hip ActiGraph | Mean 9,676 ± 107 uncensored; 6,540 ± 106 censored (low-intensity steps removed) | 3,744 | Tudor-Locke et al. 2009 (PMID 19516163) | E2 |
| Step-band distribution (NHANES, pedometer-equivalent) | <2,500: 14.1%; 2,500–4,999: 20.6%; 5,000–7,499: 24.2%; 7,500–9,999: 19.3%; 10,000–12,499: 10.9%; ≥12,500: 10.8% | 3,744 | Tudor-Locke 2011 review | E2 |
| Health eHeart (self-reported device steps) | mean 3,491 ± 3,345 (selection bias toward low) | 66,788 | PMC6592896 | E2 |

**Warning:** step marginals are strongly algorithm/device dependent (same NHANES data: 9,676 vs 6,540 mean after censoring tweak — a 32% shift). Distributions are right-skewed; model log-normal or gamma, and parameterize per simulated device algorithm.

### A.10 Sleep (UK Biobank accelerometer, n=89,205; Wainwright/Jones et al., PLOS Med 2021, PMC8509859 — E2)

Percentiles (no psychiatric diagnosis group; h:min):

| Measure | 10th | 25th | 50th | 75th | 90th |
|---|---|---|---|---|---|
| Bedtime | 22:05 | 22:44 | 23:19 | 23:57 | 00:37 |
| Wake time | 6:09 | 6:47 | 7:24 | 8:01 | 8:36 |
| Sleep duration | 6:33 | 7:15 | 7:54 | 8:32 | 9:11 |
| Sleep efficiency | 95% | 97% | 99% | 100% | 100% |
| # awakenings | 0 | 0 | 1 | 1 | 2 |
| Within-person sleep-duration SD | 0:11 | 0:18 | 0:30 | 0:46 | 1:08 |
| Bedtime variability (SD) | 0:06 | 0:12 | 0:21 | 0:37 | 0:59 |

Also: accelerometer mean sleep duration 7.3–7.5 h (SD 0.7–0.8) (Diabetes Care 2024); WASO median 4 min. Note: actigraphic "sleep efficiency" (99% median) is much higher than PSG-based SE (typically 85–95%) — algorithm-specific; PSG-validation ICCs: TST 0.79, SE 0.85 (n=12, Springer 2025).

---

## B. Correlation structure (between-person unless noted)

**Legend:** [E] = evidence-based (r or beta reported with n); [M] = mechanistically constrained (E1); [A] = assumed/provisional (no direct evidence — see Section F).

| Pair | Estimate | n / population | Source | Level |
|---|---|---|---|---|
| RHR ↔ RMSSD | r ≈ −0.58 (children, resting); adults: RMSSD scales ~exponentially with mean RR interval; HR is the single largest determinant of RMSSD; rank-order preserved by correction | 626 children; Lifelines 84,772 (determinants paper Tegegne 2018, Heart Rhythm 15:1552) | PMC4378923-adjacent; van Roon 2016; de Geus 2019 (PMC6378407) | E2/E1 |
| HR ↔ ln(RMSSD) | Strong negative, |r| roughly 0.5–0.8 depending on recording (mechanistic: for fixed modulation depth, RMSSD ∝ RR; so RMSSD ≈ c·RR·(modulation)) | — | Monfredi 2014; Sacha 2013; van Roon 2016 | E1 |
| RHR ↔ SBP | r = 0.257 (men); regression +0.27 mmHg SBP per +1 bpm (0.20–0.25 unmedicated) | 707 Korean men; 8,541 CARDIAC | PMC6441756; Sci.Direct S0167527309005427 | E2 |
| RHR ↔ DBP | r = 0.268; +0.09–0.25 mmHg per bpm | same | same | E2 |
| SBP ↔ DBP | r = 0.717 | 6,667 | NHANES II | E2 |
| RHR ↔ VO2max | r = −0.34 (cross-sectional); −0.13 to −0.23 ml·kg⁻¹·min⁻¹ per +1 bpm (adjusted); within-person change r = −0.20 | 2,798 (Copenhagen Male Study); Fenland | heart.bmj.com 99:882; PMC10174582 | E2/E4 |
| RMSSD ↔ VO2max | r = 0.2–0.6 across small studies (athletes 0.64; T2DM 0.89 [n=77, likely inflated]); general-population large-n estimate **not available** | small samples | scielo futsal; JHSE 2024 T2DM | E2 (heterogeneous) |
| HRV (rest) ↔ HRR | r ≈ 0 (no association in 72 young men; literature mixed, correlations appear only at specific recovery windows) | 72 | Auburn dissertation (auetd) | E2 |
| RMSSD ↔ SDNN (daily obs) | strong positive (~0.8–0.9 within daily wearable data) | 424 obs | MDPI Sensors 25:4415 | E2 |
| RMSSD tracking stability (1.5 y) | >0.5 (youths); HRV stress-reactivity tracking <0.3 | 399 | Li et al. 2009 (HERO 2331351) | E2 |
| RHR long-term stability | baseline–follow-up r = 0.70 (years apart) | Fenland subsample | PMC10174582 | E2 |
| Wearable-measured sleep duration ↔ self-report | r < 0.25 (weak) | 66,214 | Research Square SleepNet UKB | E2 |
| HRV ↔ BP (resting) | **no robust population r found** — mechanistically weak/indirect (shared autonomic drive, baroreflex) | — | — | A (see F) |
| RHR ↔ body temperature | r = 0.26 (hospitalized COVID admissions); healthy-population r not found | ~2,800 | Frontiers Med 2025 | E2 (clinical, not healthy) |
| RR ↔ HR | elevated-RR group had HR 74.1 vs 64.4 bpm (confounded by disease) | 2,224 | KORA-FF4 | E2 |
| Distal skin temp rhythm amplitude ↔ sleep efficiency | quartile trend +1.47% SE per RA quartile (adj.) | 2,187 | PMC10315598 | E2 |
| Menstrual cycle → core temp | +0.3–0.5 °C post-ovulation | — | consensus | E4 |

**Age gradients (covariate→parameter, not pairwise correlations):**
- HRmax = 208 − 0.7·age (Tanaka 2001, meta-analysis 351 studies, n=18,712; E5); women-specific 206 − 0.88·age (Gulati 2010, n=5,437); fit adults 211 − 0.64·age (Nes/HUNT 2013, n=3,320). Residual SD ≈ 10–12 bpm (RMSE ~10.7 in Shookster 2020 validation, n=large clinical). **Model: HRmax ~ N(208 − 0.7·age, 10.5²).**
- HRV decline: see A.2/A.3 (RMSSD ~ −8 to −10%/decade mid-life, flattening after 60).
- BP: SBP +~1 mmHg/yr mid-life (median 115→145 across 18–74 y, NHANES III).
- RHR: inverted-U with age (Quer 2020) — do **not** model monotonic decline.
- HRR (1-min post-exercise): mean 44 ± 11 bpm at baseline, −3.6 bpm per 20 y aging (CARDIA, n=2,730; Carnethon 2012, PMC3838873); abnormal <12 bpm (Cole 1999). Protocol-dependent (supine vs cool-down shifts values ~+6 bpm).

**Sex effects summary:** RHR +3 bpm (F); RMSSD +~5 ms (F, ages 20–45 only); SDNN lower in F for 24-h recordings; LF/HF higher in M; BP higher in M until ~menopause; VO2max higher in M (absolute and per kg FFM); SV/CO scale with LBM (removes most sex difference); HRmax equations differ modestly.

---

## C. Variance decomposition (between-person / within-person day-to-day / within-day)

| Variable | Between-person SD (or CV) | Day-to-day within-person | ICC / reliability | n | Source | E |
|---|---|---|---|---|---|---|
| RHR (daily, wearable) | 7.7 bpm (CV 11.8%) | SD 3.03 bpm (women 3.10, men 2.90) → **CV ≈ 4.6%**; CV rises when mean RHR <60 bpm | 5-day ICC 0.87 (0.74–0.95) | 92,457; 17 | Quer 2020; UA thesis | E2/E3 |
| RHR measurement-context spread (same day) | — | repeatability coefficient: sleep RHR RC 5 bpm, rest RC 12 bpm, morning RC 11 bpm | — | 9×5 days | PMC36086212-adjacent (PubMed 36086212) | E3 |
| RMSSD (daily) | CV ~40–60% between persons (Lifelines mean/median ratio) | 14-day mean CV 0.37 (SD 0.16; range 0.14–0.71); athlete lnRMSSD CV 3–13%; WHOOP-derived ~5.4% weekly CV of lnRMSSD | 5-day ICC 0.66 (0.32–0.86); 7-day lab ICC 0.75–0.98; day-to-day ICC 0.33–0.93 depending on metric | 424 obs; 17; 26; Fennell n | MDPI 25:4415; Sensors 22:6723; UA; Guijt 2007; Fennell 2023 (PMC11055755) | E2/E3/E4 |
| SBP (clinic) | between-person SD ~12–19 mmHg | visit-to-visit intra-individual SD 12.2–13.5 mmHg (CV ~9%); **within-visit SD only 4.1 mmHg**; stability of VVV itself ICC 0.28 | — | >13,000 (routine care) | PMC4867495; ASCOT (ORA ox.ac.uk) | E2/E4 |
| DBP (clinic) | — | intra-individual SD 7.0–7.1 mmHg (CV ~9.3%) | — | same | same | E2 |
| Sleep duration (actigraphy) | between-person SD ~0.7–0.8 h | within-person SD median 0:30 h (90th pct 1:08); single-night ICC: weekday 0.38, weekend 0.27; 5-weekday TST ICC 0.60; SE ICC 0.76 | need 4 weekday + up to 7–9 total nights for reliability 0.7 | 9,510 (NHANES 2011–14); 89,205 (UKB) | Lee 2024 (S1389945724000066); PMC8509859; Ravesteyn thesis | E2/E4 |
| Steps/day | between-person CV ~50% | day-to-day: 2.5 (random)–4.4 (consecutive) days needed for mean-step ICC ≥0.8; MAPE ~13% at min days; PD smartwatch 4 days ICC 0.84–0.90 | — | 212,048 (Singapore); 56 | PMC8100112; MDPI 23:8971 | E2/E4 |
| Orthostatic HR response (active stand) | median RR-interval change −24.4% (−28.2;−18.8); RMSSD −51% (−65.5;−38.8); LF/HF +218% (n=45 men) | **event-to-event variability: no reliability study found** — explicit gap (E0). Treat orthostatic ΔHR as person mean + sizeable event noise (provisional within-event CV 15–25% by analogy with HRV) | — | 45 | geafs.unb.br (Brazilian cohort) | E2 + gap |
| Exercise HRmax | — | residual SD around age prediction 10–12 bpm (Tanaka validation RMSE 10.7) | — | 18,712 meta + 514 lab | Tanaka 2001 (PMID 11153730); Shookster 2020 (PMC7523886) | E5 |
| HRR | — | 1-min HRR declines 3.6 ± ~28 bpm (relative) over 20 y; test-retest CV not located — gap | — | 2,730 | CARDIA | E2 |

**Rule of thumb validated by evidence:** RHR day-to-day CV ~3–5% ✔ (4.6% in 92k); RMSSD day-to-day CV ~20–30% ✔ for raw RMSSD in uncontrolled settings (0.37), but 3–13% for **lnRMSSD under standardized morning protocols** — the discrepancy is a protocol effect, not a contradiction.

---

## D. Covariate models

| Covariate | Model form (recommended) | Evidence | E |
|---|---|---|---|
| Age → HRmax | 208 − 0.7·age + N(0, 10.5); women: 206 − 0.88·age | Tanaka 2001; Gulati 2010 | E5 |
| Age → lnRMSSD | steep exponential-ish decline 20→60 y (≈ −40% per 2 decades mid-life), plateau after 60; use Lifelines age-bin medians as lookup/spline | Lifelines n=84,772; Umetani n=260 | E2/E4 |
| Age → SDNN (24 h) | ~linear −5 to −10%/decade | Umetani; Almeida-Santos n=1,743 | E4 |
| Age → RHR | inverted-U (peak ~50 y), NOT linear | Quer n=92,457 | E2 |
| Age → SBP | ~+1 mmHg/yr; DBP rises then falls after ~55–60 | NHANES III medians; consensus | E4/E5 |
| Age → HRR | −3.6 bpm per 20 y | CARDIA | E2 |
| Age → distal skin temp rhythm | amplitude −19% (older women), acrophase +66–73 min earlier | n=65 | E3 |
| Sex → RHR | +3 bpm (F) | Quer; NHANES I | E4 |
| Sex → RMSSD | +5 ms (F) ages 20–45, vanishes >60 | Lifelines | E2 |
| Sex → LF/HF | higher in M (24-h: 5.15 vs 3.37) | KORA F3 | E2 |
| BMI → RHR | U-shape, nadir BMI 21 (F) / 23 (M) | Quer | E2 |
| Body size → SV/CO | scale to lean mass (exponent ~1); else BSA^1.7–1.8 for volumes, height^2.7 for LV mass; CO allometric coeff ~0.55 vs body size; LVEF size-independent | J Hypertens 2016 (PMID 27035735); Strong Heart; KU Leuven CMR | E2/E4 |
| Sleep duration → RHR | min at 7–7.5 h/night | Quer | E2 |
| Ethnicity | Robust differences limited: resting HRV higher in African-American vs European-American youths (Li 2009); HRR decline larger in Black participants (CARDIA); NHANES pulse slightly higher in whites than blacks (subgroups). Recommend ethnicity as small-effect modifier only, with sensitivity analysis. | Li 2009; Carnethon 2012; NHANES I | E2 |

---

## E. Disease severity distributions and comorbidity co-occurrence

### E.1 POTS — demographics & severity (sampling design)

| Parameter | Value | n | Source | E |
|---|---|---|---|---|
| Female fraction | 94% (survey, self-reported dx); >85% generally; 5:1 clinical estimate | 4,835 / 8,919 | Shaw 2019 (PMC6790699); Bourne 2021 (PMC8712580) | E2 |
| Age at onset | mean 20.7 ± 12.0 y; median 17 (IQR 13–28); **mode 14**; 47% adult-onset (>18 y) | 4,835 | Shaw 2019 | E2 |
| Race | 93% white (survey bias — do not over-interpret) | 4,835 | Shaw 2019 | E2 (biased) |
| Prevalence | 0.2–1.0% US (0.5–3 M people) | — | Vernino 2021; Cutsforth-Gregory 2020 (NBK607376) | E2 |
| Severity (functional) | ~25% disabled/unable to work; EQ-VAS median 40 (IQR 30) vs 85 normative; EQ-5D utility 0.63 vs 0.95 | — | Dysautonomia Intl; PMC10439037 | E2 |
| Diagnostic delay | median 24 mo (IQR 6–72); misdiagnosis ~75% | 4,835 | Shaw 2019 | E2 |
| Triggers | infection 41%, surgery 12%, pregnancy 9% (of the 41% reporting event onset) | 4,835 | Shaw 2019 | E2 |
| Subtypes | hypovolemic / neuropathic / hyperadrenergic — no validated prevalence distribution; treat as latent mixture with provisional weights | — | Pierson 2025 review (PMC11775448) | E0 |
| Medication prevalence | most-studied: cardioselective BB, midodrine, ivabradine, fludrocortisone; symptomatic response rates: midodrine 78%, ivabradine 75%, BB 64%. **No population prescription-prevalence distribution found — gap.** | 32 studies | Pierson 2025 systematic review | E5 (for response), E0 (for prevalence) |

### E.2 ME/CFS — severity & demographics

| Parameter | Value | n | Source | E |
|---|---|---|---|---|
| Female fraction | 78–86% (consistent across 10 countries, no difference by onset peak) | >9,000 | EMEA survey analysis (PMC13070794) | E2 |
| Onset age | **bimodal**: early peak mean 16.0 ± 4.3 y; late peak 36.6 ± 10.5 y; early onset OR 2.15 for severe/very severe disease | >9,000 | PMC13070794 | E2 |
| Severity distribution (clinic sample) | mild 42%, moderate 34%, severe 24% | 289 | Bateman Horne validation (batemanhornecenter.org PDF) | E2 |
| Severity distribution (patient survey) | very severe 2%, severe 11%, moderate 58%, mild 29%, better-than-mild 1% | 1,263 | FUNCAP55 (preprints.org 202309.2091) | E2 |
| Consensus anchor | ~25% housebound/bedbound (severe+very severe); of homebound, 16.2% bedridden | 2,138 | Conroy 2021 (PMC7909520); NICE 2021 categories | E2/E5 |
| Objective severity gradient | steps/day: mild 8,235 ± 1,004; moderate 5,195 ± 1,231; severe 2,031 ± 824; peak VO2 %predicted: 90/64/48 | 289 | Bateman Horne validation | E2 |
| Disease duration | mean 12 ± 9 y (clinic sample) | 289 | same | E2 |
| Recovery | full recovery <5% | — | ME/CFS Clinician Coalition primer | E2 |

**Modeling recommendation:** represent ME/CFS severity as a continuous latent "functional capacity" variable mapped onto steps/day and %predicted VO2 (evidence-based anchors above), with the categorical ICC/NICE scale as a discretization — not as 4 independent categories.

### E.3 Comorbidity co-occurrence (for joint sampling)

| Cell | Rate | n | Source | E |
|---|---|---|---|---|
| hEDS in POTS | 31% meeting 2017 criteria on prospective evaluation (55% had hypermobility by Beighton); chart reviews 12–22% | 91 | PMC7282488 | E2 |
| POTS in hEDS | 61.6% (self-report registry — upper bound, selection-biased); literature range 17.5–92.7% | 2,800 | Wachs 2026 (Springer); Sci.Direct S1566070226000755 | E2 (biased) |
| hEDS in ME/CFS | 12–19%; hypermobility 50–81% | — | NINDS ME/CFS Roadmap report 2024 | E2 |
| ME/CFS in long COVID | 58% screen positive (vs 0% controls); ~50% of LC meet ME/CFS criteria elsewhere | 277 LC / meta | Frontiers Neurol 2024; ANZMES synthesis | E2 |
| POTS in long COVID (highly symptomatic) | **31% diagnosed**; +27% symptomatic subthreshold; POTS-LC 91% female, mean age 40 | 467 | Björnson 2025, *Circ Arrhythm Electrophysiol* (PMID 41025260) | E2 |
| POTS in long COVID (clinic attenders, unselected) | 7% meet PoTS criteria by NASA Lean Test; 8% OH; 15% any abnormal NLT | 277 | PMID 38456315 | E2 |
| POTS↔long COVID causal direction | POTS incidence post-COVID elevated; "POTS population doubled since pandemic" (estimate) | — | Dysautonomia Intl | E2 |

**Joint-sampling guidance:** use a copula/log-linear model on {POTS, hEDS/HSD, ME/CFS, long COVID} with the marginal and pairwise rates above; note all pairwise rates are inflated by clinic/self-report ascertainment (down-weight by ~0.3–0.5× for population-representative sampling, or state the synthetic cohort is clinic-like). Third-order interactions: no evidence (E0) — assume pairwise-sufficient (log-linear) structure with sensitivity analysis.

---

## F. Correlation cells with NO usable evidence — and recommended handling

| Cell | Status | Recommended handling |
|---|---|---|
| RMSSD ↔ SBP/DBP (healthy adults, population r) | No population r located; mechanistically weak (baroreflex coupling, shared autonomic drive) | Provisional r ∈ [−0.2, 0] via Gaussian copula; sensitivity analysis at r = 0 |
| EDA (SCL) ↔ RHR/RMSSD | No population correlation; both load on sympathetic arousal within-person, but between-person coupling undocumented | Model shared *state* (stress) factor for within-person covariation; independence between persons + sensitivity |
| Core/skin temp ↔ RHR (healthy) | Only hospitalized r = 0.26 (temp–HR); healthy free-living r not found | Mechanistic coupling (fever +~7–10 bpm/°C — E1/E3) for within-person episodes; between-person r ≈ 0 |
| SV ↔ HRV; SV ↔ RHR | No direct population correlation | Couple indirectly through fitness latent factor (VO2max ↔ RHR r=−0.34 [E2]; VO2max ↔ SV mechanistic [E1]) |
| RR (respiration) ↔ RMSSD | Within-person RSA coupling strong (E1); between-person r not found | Couple within-person via respiratory sinus arrhythmia module; between-person independence + sensitivity |
| Steps ↔ RMSSD/RHR (between-person, general population) | Expected negative (fitness), but no large-n r for steps↔RMSSD; Fenland gives RHR–PAEE attenuation (~30–40% of RHR–fitness link) | Route through fitness latent factor; do not place a direct steps→RMSSD edge |
| HRV ↔ sleep duration (between-person) | Device-measured sleep ↔ self-report weak (r<0.25); nightly HRV–sleep coupling mostly within-person, heterogeneous sign | Within-person: small positive lnRMSSD effect on perceived sleep (β 0.51, n=424 obs, MDPI 25:4415); between-person r ≈ 0–0.1 provisional |
| Orthostatic ΔHR event-to-event variability | No test-retest reliability study located for active-stand ΔHR in healthy or POTS | Provisional within-person CV 15–25%; flag for empirical calibration |
| HRR ↔ RMSSD | r ≈ 0 in available small studies (n=72); mixed literature | Assume conditional independence given fitness factor; sensitivity ±0.2 |
| Latent "inflammatory tone" ↔ HRV | Mechanistic (vagal-inflammatory reflex, E1) but no population correlation anchored | Optional third latent factor; default off |

---

## G. Latent-variable architecture recommendations

**Direct factor-analytic studies of autonomic/wearable measure batteries: none located (explicit gap, E0).** The recommendations below are therefore theory- and correlation-structure-driven:

1. **"Autonomic/vagal setpoint" factor** — loadings: RMSSD (+), SDNN (+), RHR (−), HRR (+). Justification: HR–RMSSD mechanistic coupling (E1, van Roon/Monfredi/Sacha); both track fitness and age; RMSSD–SDNN correlation ~0.8–0.9 (E2). Note HRR↔HRV r≈0 conditional on fitness → keep HRR on the *fitness* factor or as a separate vagal-reactivation residual.
2. **"Cardiorespiratory fitness" factor** — loadings: VO2max (+), steps/day (+), RHR (−), RMSSD (+, via r −0.34 RHR–VO2max path), SV (+), HRR (+). Evidence: Copenhagen Male Study, Fenland (E2/E4).
3. **"Body size/composition" factor** — height, weight/BMI, lean mass, BSA; drives SV/CO via allometry (E2/E4); U-shaped link to RHR (E2).
4. **"Hemodynamic/vascular aging" factor** — SBP, DBP (r=0.717), pulse pressure, age loading; links to RHR (r≈0.26, E2).
5. **"Circadian/sleep-regularity" factor** — sleep duration, sleep-duration SD (median 0:30 h), bedtime variability, distal-temp rhythm amplitude (E2 coupling to sleep efficiency).
6. Optional **"sympathetic arousal/inflammatory tone"** factor (SCL, NS-SCR rate, RR) — E1 mechanistic, no population factor evidence; keep provisional.
7. Factor correlations: fitness↔autonomic setpoint r ≈ 0.3–0.4 (provisional, from RHR–VO2max r=−0.34); size↔hemodynamic r ≈ 0.2–0.3 (provisional); others ≈ 0 with sensitivity analysis.

**Implementation:** draw latent factor scores from a multivariate normal (correlations above), generate parameter means from factor loadings + covariate models (Section D), then add between-person residual noise (from Section A SDs after factor-explained variance) and within-person day-to-day noise (Section C CVs/ICCs) and within-day circadian/event structure. This reproduces realistic marginals *and* joint structure.

---

## H. Synthetic cohort sampling design guidance

1. **Healthy reference cohort:** age ~uniform or census-matched 18–75; sex 50/50; sample marginals per Section A with age/sex conditioning; apply Section G latent structure.
2. **POTS cohort:** female 0.85–0.94; onset age empirical distribution = mixture (point mass/lognormal at mode 14, plus broad adult component, median 17, IQR 13–28); present age = onset + delay/duration (median diagnostic delay 2 y); severity: continuous EQ-VAS-like variable with ~25% in disabled tail; comorbid hEDS 0.31 (conditional), ME/CFS co-occurrence via Section E.3; medications: BB/ivabradine/midodrine/fludrocortisone flags — no prevalence distribution exists (E0); use systematic-review study-arm frequencies as provisional priors with sensitivity analysis.
3. **ME/CFS cohort:** female ~0.8; bimodal onset N(16.0, 4.3²) + N(36.6, 10.5²) (weights by country data, ~early:late ≈ 1:1.5); severity continuous with anchors: steps 8,235/5,195/2,031 for mild/moderate/severe; duration mean 12 ± 9 y.
4. **Long-COVID cohort:** ~75% female, mean age ~53 (Frontiers 2024) or ~40 for POTS-LC subset; POTS 0.31 (highly symptomatic) or 0.07 (unselected clinic) — sample prevalence by cohort definition; ME/CFS screen+ 0.58.
5. **All cohorts:** generate day-level series with within-person SDs from Section C (RHR CV ~4.6%, RMSSD CV ~0.37 unstandardized or lnRMSSD CV 3–13% standardized, sleep duration SD ~0.5 h, steps MAPE ~13%); superimpose seasonal RHR (±1 bpm sinusoid, peak early Jan) and menstrual core-temp (+0.3–0.5 °C luteal) where relevant.

---

## I. Key source list (all verified via live retrieval; no DOIs/PMIDs fabricated)

1. Quer et al. 2020 — RHR distribution/variability, n=92,457 (PMC7001906)
2. Tegegne et al. 2020 — Lifelines RMSSD reference, n=84,772 (PMC7734556)
3. Voss et al. 2015 — KORA S4 5-min HRV, n=1,906 (PMC4378923)
4. Umetani et al. 1998 — 24-h HRV by decade, n=260 (JACC; PMC5624990 summary)
5. KORA F3 Holter HRV, n=505 (s10654-025-01248-3)
6. NHANES II BP, n=6,667 (S0895706106005693); NHANES III age medians (PMC3491581); NHANES trends (PMC7489367)
7. KORA-FF4 respiration rate, n=2,224 (PMC11896064)
8. UK Biobank sleep, n=89,205 (PMC8509859); steps n=85,394 (PMC12242917); wrist temperature (PMC10449859)
9. Tudor-Locke 2009/2011 — NHANES steps (PMID 19516163)
10. Tanaka 2001 (PMID 11153730); Gulati 2010; Nes 2013; Shookster 2020 (PMC7523886)
11. Carnethon 2012 — CARDIA HRR, n=2,730 (PMC3838873)
12. Copenhagen Male Study RHR–fitness r=−0.34 (Heart 99:882); Fenland (PMC10174582)
13. van Roon 2016 (PMID 27672028); de Geus 2019 (PMC6378407)
14. Reliability: Guijt 2007; Fennell 2023 (PMC11055755); MDPI Sensors 25:4415 & 22:6723; Lee 2024 (NHANES sleep ICC); PMC8100112 (steps, n=212,048); PMC4867495 (BP VVV)
15. Kuznetsova et al. 2016 allometry (PMID 27035735); Strong Heart; KU Leuven CMR
16. Shaw 2019 (PMC6790699); Bourne 2021 (PMC8712580); Vernino 2021 (NBK607376)
17. PMC7282488 (hEDS in POTS, n=91); Wachs 2026 (hEDS registry); NINDS ME/CFS Roadmap 2024
18. PMC13070794 (ME/CFS bimodal onset, n>9,000); Conroy 2021 (PMC7909520); FUNCAP55 (n=1,263); Bateman Horne severity validation (n=289)
19. Björnson 2025 POTS in long COVID (PMID 41025260); PMID 38456315 (NASA Lean Test)
20. Pierson et al. 2025 POTS medications systematic review (PMC11775448)
21. Boucsein 2012 (EDA norms, textbook E4); Tai 2023 (PMC10315598, skin temp, n=2,187)
