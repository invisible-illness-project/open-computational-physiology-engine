# OCPE Disease Evidence Review — Long COVID / Post-Acute Sequelae of SARS-CoV-2 (PASC)

**Prepared by:** Long COVID Scientist (research swarm), Pass 1 = discovery
**Date:** 2026 (search session); literature covered through late 2025
**Evidence scale:** E0 hypothesis / E1 mechanistic / E2 observational human / E3 controlled human experimental / E4 replicated quantitative / E5 meta-analysis/consensus
**Core framing:** Long COVID is **heterogeneous**. No single physiological signature is demonstrated across all cases. Several physiological phenotypes (autonomic/exercise-limitation, respiratory, sleep/circadian) have reproducible *group-level* signals; none is validated as a diagnostic biomarker (RECOVER n≈10,000 routine-lab study found no clinically useful lab biomarker). Mechanistic hypotheses (microclots, viral persistence, autoantibodies) remain E0–E1 and should **not** be implemented as grounded physiological perturbations; they justify phenotype-level surrogates instead.

---

## 1. Definitions & Phenotyping

### Claim 1.1 — Consensus case definitions exist but are symptom-based
- **Claim:** Post-COVID-19 condition = symptoms usually ≥3 months from onset, lasting ≥2 months, not otherwise explained (WHO, Delphi, n=265 panelists, 2 rounds).
- **Phenotype:** all. **Domain:** definition. **Variable:** symptom duration. **Direction:** n/a. **Magnitude:** n/a. **Timescale:** onset 3 mo, duration ≥2 mo.
- **Evidence:** E5 (international consensus, not data-derived). Source: Soriano JB et al., *Lancet Infect Dis* 2022;22:e102–e107. DOI 10.1016/S1473-3099(21)00703-9; PMID 34951953. Children/adolescents: separate WHO Delphi definition 2023.
- **Limitations:** no physiological/biomarker anchor; deliberately broad; sensitivity/specificity unknown.
- **Implementation:** use as **cohort eligibility gate** (≥3 mo post-infection, ≥2 mo symptoms), not as a generative phenotype.
- **Validation:** synthetic cohorts should reproduce WHO-compatible symptom duration distributions.

### Claim 1.2 — RECOVER data-driven symptom index and 4 clusters
- **Claim:** In RECOVER-Adult (n=9,764; 89% infected; 71% female; median age 47), 12 symptoms scored into a PASC index (threshold ≥12); 37 symptoms had adjusted OR ≥1.5 (infected vs uninfected). PEM showed the largest contrast (28% vs 7%, aOR 5.2, 95% CI 3.9–6.8), fatigue (38% vs 17%, aOR 2.9), dizziness (23% vs 7%, aOR 3.4), brain fog (20% vs 4%, aOR 4.5), GI (25% vs 10%, aOR 2.7). Four unbiased clusters: (1) smell/taste loss (lowest burden); (2) PEM+fatigue, some dizziness/GI, no brain fog; (3) brain fog (100%) + PEM (99%); (4) high multi-symptom burden, worst QoL.
- **Population:** n=9,764; ≥6 mo post-infection; mixed pre-/post-Omicron; Omicron-era incidence subset n=2,231 → 10% (8.8–11%) PASC+ at 6 mo.
- **Evidence:** E2 (large prospective observational with uninfected controls; cluster analysis). Source: Thaweethai T et al., *JAMA* 2023;329:1934–1946. DOI 10.1001/jama.2023.8823; PMID 37278994. 2024 update of index (LCRI): PMID 39693079.
- **Supporting:** independent EHR subphenotyping (N3C/RECOVER; Reese JT et al., *eBioMedicine* 2023;87:104413) reproduces overlapping cardiorespiratory/neuro/fatigue subtypes.
- **Contradictory/limitations:** clusters are symptom self-report, not physiological endotypes; volunteer/ascertainment bias (RECOVER enriched for symptomatic volunteers); no physiological measurement defined the clusters; cluster 1 (smell/taste) has no plausible wearable signature.
- **Implementation:** treat the 4 clusters as **observation-level symptom labels**, NOT as physiological generative phenotypes. Physiological generative model should be built on mechanistic axes (below) that map approximately onto clusters 2–4.
- **Validation:** phenotype prevalence mix in synthetic data ≈ cluster prevalences; PEM as highest-contrast symptom.

### Claim 1.3 — Long COVID trajectories are heterogeneous; most 3-month cases persist at 1 year
- **Claim:** In prospectively followed Omicron-era RECOVER adults (n=3,659, infected after 2021-12-01, surveys at 3/6/9/12/15 mo), 10.3% met LCRI criteria at 3 mo; 81% of those continued persistent or intermittent symptoms a year later; 8 trajectories identified (persistent, intermittent, worsening, resolving, varying severity). Female sex and acute hospitalization predicted persistently severe course.
- **Evidence:** E2. Source: Thaweethai T et al., *Nat Commun* 2025;16:9557.
- **Supporting:** WHO/IHME estimate — of people developing post-COVID-19 condition (3.7% of infections by end-2021), 15.1% still symptomatic at 12 mo.
- **Limitations:** Omicron-era only; self-report; survivorship/attrition bias.
- **Implementation:** **timescale heterogeneity is itself a latent variable** — generate symptom/physiology trajectories (resolved ~19%, intermittent, persistent, worsening) rather than static phenotypes.
- **Validation:** trajectory-class proportions; ~10% incidence at 3 mo (Omicron-era, vaccinated-majority) as calibration target.

### Claim 1.4 — ME/CFS is a measurable subphenotype of long COVID
- **Claim:** Post-COVID ME/CFS (IOM 2015 criteria) incidence 2.66 per 100 person-years (95% CI 2.63–2.70) vs 0.93 (0.91–0.95) in propensity-matched uninfected; HR 4.93 (3.62–6.71). Prevalence 4.5% (531/11,785) of infected vs 0.6% (9/1,439) uninfected at ≥6 mo. 88.7% of post-COVID ME/CFS also met RECOVER PASC criteria; 45% of them mapped to cluster 4. PEM most common ME/CFS symptom in infected (24.0% overall; 29.1% post-acute infected; 15.9% acute infected); OI 25.0% post-acute infected.
- **Evidence:** E2/E3 (prospective cohort with propensity-matched controls; non-hospitalized only). Source: Vernon SD et al. (RECOVER), *J Gen Intern Med* 2025. DOI 10.1007/s11606-024-09290-9.
- **Supporting:** INSPIRE registry 3–4% ME/CFS prevalence; Hickie 2006 (11% ME/CFS 6 mo post EBV/Q fever/RRV) shows this is a generic post-infective phenomenon.
- **Limitations:** self-reported criteria; selection bias; hospitalised excluded; mostly Omicron/vaccinated.
- **Implementation:** **ME/CFS-like phenotype = composable severe tier** (see Section 9); prevalence parameter ~4.5% of infected, enriched in cluster-4 analogue.

---

## 2. Autonomic domain (POTS / orthostatic intolerance / HRV / small-fiber neuropathy)

### Claim 2.1 — Orthostatic intolerance symptoms are common; true POTS prevalence is contested (0–30%, up to 79% in small clinic samples)
- **Claim:** Self-reported OI ~25% in post-acute infected (RECOVER, above). Consensus-criteria POTS after COVID ranges widely: 0% in a rigorous HUTT case-control study; ~29% (22/75) among referrals to a specialized autonomic center (post-COVID subgroup); 79% (26/33) of a small PASC sample using active-stand test.
- **Magnitude+distribution:** bimodal-by-method: referral/clinic and active-stand → 30–79%; gold-standard 40-min HUTT with consensus criteria → 0% met full POTS criteria in symptomatic long COVID case-control study (though orthostatic HR rises and symptoms common).
- **Population:** n=33 PASC (Seeley); n=75 post-COVID referrals (Fedorowski group); case-control HUTT study (n≈100s across arms; PMC12551903).
- **Evidence:** E2 overall; strong internal contradiction. Sources: Seeley MC et al., *Am J Med* 2023 (DOI 10.1016/j.amjmed.2023.06.010); Fanni G et al. (Fedorowski group), *J Neurol* 2025 (DOI 10.1007/s00415-025-13518-x); case-control HUTT study PMC12551903 (2025); review: Ormiston CK et al., *Heart Rhythm* 2022;19:1880–1889 (DOI 10.1016/j.hrthm.2022.07.014).
- **Contradictory (critical):** the discrepancy is largely **methodological** — active-stand/NASA-lean over-diagnose vs 30–40 min HUTT; referral-center enrichment; many "POTS-like" long COVID patients have orthostatic tachycardia/intolerance *below* consensus thresholds or delayed/transient OH.
- **Implementation:** implement an **"orthostatic dysregulation" latent axis**, not binary POTS: graded orthostatic HR increment (ΔHR 0–>30 bpm on stand/tilt), with consensus-POTS tail (~small % of long COVID; pre-pandemic POTS background 0.2–1% for reference). Avoid hard-coding 30% prevalence.
- **Validation:** distribution of standing ΔHR in synthetic cohort vs Seeley/HUTT studies; symptom OI ~25%.

### Claim 2.2 — Heart rate variability is reduced at group level; direction consistent for SDNN, inconsistent for RMSSD/LF/HF
- **Claim:** Post-COVID/long COVID cohorts show lower SDNN vs controls across most small cross-sectional studies (e.g., SDNN 122.4±30.9 vs 161.3±30.8 ms, p<0.0001, ~20 wk post-infection; SDNN-24 111.6±38.7 vs 133.4 ms in n=47 vs 44); RMSSD results inconsistent (some lower, some NS, one subgroup higher); LF/HF inconsistent.
- **Magnitude:** SDNN ↓ ~15–25% (~10–40 ms) at group level; resting HR +5–7 bpm in some clinic samples (e.g., 82.3±9.2 vs 75.8 bpm).
- **Evidence:** E2, with a systematic review (PMC10137929, 2023) concluding SDNN decrease is the most consistent finding, RMSSD/LF/HF inconsistent; all included studies cross-sectional → cannot exclude deconditioning/confounding. E2: PMC9821736.
- **Supporting (experimental-grade):** LIINC ambulatory monitoring (Durstenfeld 2023): chronotropic-incompetence subgroup had lower ambulatory max HR (−29 bpm), higher minimum HR (+12.6 bpm), lower HRV (SDNN −59 ms, 24–95 CI).
- **Limitations:** no large prospective controlled wearable HRV dataset with pre-infection baseline; confounding by activity reduction, sleep, BMI, medications.
- **Implementation:** composable perturbation: **SDNN −15–25% (lognormal spread), RMSSD −10–20% with partial (≈50% of phenotyped cases) penetrance, resting HR +1–3 bpm chronic** (larger in dysautonomia tier). Tie magnitude to autonomic-axis severity, not to "long COVID" globally.
- **Validation:** group-mean ΔSDNN/ΔRMSSD vs the controlled studies above; ensure non-long-COVID synthetic controls show no shift.

### Claim 2.3 — Small-fiber neuropathy: positive in selected symptomatic subgroups; null in largest controlled biopsy series
- **Claim:** Skin-biopsy SFN found in 46% of *painful* long COVID (n=26; proximal>distal, non-length-dependent; Falco et al.); Yale NeuroCOVID case-control: 16 biopsy-confirmed post-COVID SFN, 92% with ME/CFS-type PEM, iCPET (n=7) showed neurovascular dysregulation (PMID 38630952). BUT a ~100-patient long-COVID biopsy study with recovered-COVID controls found **no difference** in sensory or autonomic fiber densities despite large symptom-score differences (LCCS study; vjneurology report).
- **Evidence:** E2 with a directly contradictory, better-controlled null. Replication status: unresolved.
- **Implementation:** do **not** implement SFN as a general long-COVID mechanism. At most, a low-penetrance "neuropathic pain" flag in the severe/multi-symptom tier with no primary wearable signal.
- **Validation:** n/a for wearables; keep as E1/E2 annotation.

---

## 3. Exercise / exertion domain

### Claim 3.1 — Peak VO2 is modestly reduced at group level >3 months post-infection (meta-analytic)
- **Claim:** Systematic review/meta-analysis of CPET studies (38 studies, 2,160 participants; 9 controlled studies: 464 symptomatic vs 359 recovered): mean peak VO2 −4.9 mL/kg/min (95% CI −6.4 to −3.4) in symptomatic vs recovered, low certainty, moderate heterogeneity, high risk of bias. A second pooling (39 studies, 2,209 individuals; 9 studies, 404 infected) found −7.4 mL/kg/min (3.7–11.0) vs uninfected, driven by hospitalized/persistently symptomatic samples.
- **Patterns in reduced-capacity cases:** deconditioning common; chronotropic incompetence (5 studies); dysfunctional breathing/ventilatory inefficiency; peripheral O2-extraction impairment; cardiac limitation uncommon.
- **Evidence:** E5 (meta-analysis) but explicitly low-certainty. Source: Durstenfeld MS et al., *JAMA Netw Open* 2022;5(10):e2236057. DOI 10.1001/jamanetworkopen.2022.36057.
- **Implementation:** composable perturbation on exercise-capacity axis: **peak VO2 −5 (±5) mL/kg/min in symptomatic tier; −7 to −10 in severe/PEM tier; ~0 in asymptomatic post-infection**. Distribution, not constant.
- **Validation:** synthetic CPET-analogue (if model includes exertion HR/VO2 coupling) group means vs −4.9 CI.

### Claim 3.2 — Chronotropic incompetence is a distinct cardiopulmonary phenotype (LIINC)
- **Claim:** n=60 (median 17.6 mo post-infection, 87% non-hospitalized): symptomatic participants peak VO2 22.7±8.1 vs 29.6±7.0 mL/kg/min (adjusted −5.2, CI 2.1–8.3); reduced capacity (<85% predicted) 49% vs 16%; chronotropic incompetence (AHRR<80%) 30% vs 5% (OR 17.6); CI subgroup peak HR −49 bpm vs normal (119 vs 170), HRR1 −7.9 bpm. Early (≈6 mo) hsCRP/IL-6/TNF inversely correlated with later peak VO2. CMR/arrhythmia negative (no myocarditis signal).
- **Evidence:** E2 (single cohort, no uninfected controls, selection bias acknowledged). Source: Durstenfeld MS et al. 2023, PMC10686699 (*Open Forum Infect Dis* 2023).
- **Implementation:** **chronotropic-incompetence latent trait**: blunted exertional HR slope (peak HR % age-predicted ~86% vs 94%), attenuated HRR1, in ~30% of symptomatic phenotype. Composable with dysautonomia axis (shared mechanism hypothesized).
- **Validation:** exertional HR-curve parameters; correlation of CI trait with reduced peak VO2.

### Claim 3.3 — Invasive CPET shows peripheral O2-extraction impairment (preload failure/neurovascular dysregulation) in selected long-haulers
- **Claim:** Singh/Systrom iCPET, n=10 recovered COVID with exertional intolerance vs 10 matched controls (~1 yr post mild COVID): peak VO2 70±11% vs 131±45% predicted; impaired systemic O2 extraction (EO2 0.49±0.1 vs 0.78±0.1); preserved cardiac index (7.8 vs 8.4 L/min/m²); VE/VCO2 slope 35±5 vs 27±5; low biventricular filling pressures → argues against simple deconditioning.
- **Evidence:** E2 (tiny n, selected). Source: Singh I et al., *Chest* 2022;161:54–63. DOI 10.1016/j.chest.2021.08.010; PMID 34389297. Convergent: Joseph et al. *Chest* 2021 ME/CFS iCPET; pyridostigmine RCT (E3, ME/CFS) increased preload/VO2.
- **Implementation:** informs the **exercise-axis mechanism** (peripheral extraction/venous-return defect), not directly wearable-visible. Map to exertional HR overshoot + early fatigue in wearable proxies.
- **Validation:** pattern-level (normal central, impaired peripheral) if OCPE simulates exertion physiology.

### Claim 3.4 — PEM is the highest-specificity symptom; 2-day CPET evidence in long COVID is contradictory
- **Claim:** PEM in long COVID: 28% vs 7% (RECOVER, aOR 5.2); 80% of a long-COVID 2-day CPET sample met PEM criteria (n=15). ME/CFS literature (E4): day-2 decrements in VO2peak/workload at ventilatory/anaerobic threshold (replicated across small studies, e.g., van Campen 2020, Keller 2014; Stevens methodology, Front Pediatr 2018, PMID 30234078). In long COVID specifically: n=15 study found **no** day-1→day-2 CPET decrement despite 80% PEM (PMID 39490617, 2024); a larger retrospective study (long COVID n=79, ME/CFS n=84, controls n=71) found significant day-2 VO2/workload decrements **at VAT** in both patient groups vs controls, no between-patient-group difference (DOI 10.1007/s12018-026-09326-0, 2026).
- **Evidence:** PEM prevalence E2 (large); day-2 decrement E4 in ME/CFS, E2 and internally contradictory in long COVID (resolution may depend on PEM+ enrichment and VAT vs peak endpoint).
- **Implementation:** PEM phenotype = **delayed (12–48 h) post-exertion symptom/physiology flare**: implement as exertion-triggered state transition (reduced activity, elevated HR/lower HRV next 24–48 h) rather than a second-day VO2 decrement, which is not robustly demonstrated in long COVID itself.
- **Validation:** wearable-observable pattern: post-exertion day-1/2 activity ↓, nocturnal HR ↑/HRV ↓ (see Claim 8.5).

---

## 4. Cardiovascular domain (resting HR, BP, endothelium)

### Claim 4.1 — Acute COVID-19 produces a prolonged, multiphasic resting-HR elevation measurable by wearables (KEY, replicated)
- **Claim:** DETECT/Fitbit cohort (n=234 COVID+, 641 symptomatic COVID−): RHR took on average **79 days** to return to baseline after symptom onset (vs ~32 days step count, ~24 days sleep in the positive group; negative group normalized much faster). A biphasic RHR pattern: acute spike, relative normalization ~weeks 2–3, then a second prolonged elevation in a subset; **13.7% (32/234) had RHR elevation ≥5 bpm persisting >133 days**, correlated with more cough/body aches/dyspnea acutely.
- **Evidence:** E4 (objective wearable data, within-person pre-infection baselines, symptomatic test-negative controls; findings qualitatively reproduced). Source: Radin JM et al., *JAMA Netw Open* 2021;4(7):e2115959. DOI 10.1001/jamanetworkopen.2021.15959.
- **Supporting:** UK citizen-science case-control (n=1,200 COVID+, wearable+app; *Lancet Digit Health* 2024; PMC11832456): replicated the triphasic RHR course (initial rise → dip wk 2–3 → chronic elevation in a subset lasting >12 wk); estimated 7.0% (84/1,200) had a long-term HR change at 12 wk using Bayesian structural time series (vs 13.7% in Radin).
- **Limitations:** self-selected wearable owners; symptom data only acute-phase in Radin (no long-COVID symptom linkage); no mechanistic attribution.
- **Implementation (high priority):** **post-infection RHR trajectory module**: acute ΔRHR +5–15 bpm (days −4 to +7 around symptom onset), partial normalization weeks 2–3, then persistent low-grade elevation **+1–3 bpm (tail: ≥5 bpm) in 7–14% of infected**, decaying over 2–5 months. This is the best-validated long-COVID-adjacent wearable signal and should be a standalone "post-acute infection response" layer on which phenotype perturbations compose.
- **Validation:** fraction with RHR ≥5 bpm at 12 wk ≈ 7–14%; mean time-to-baseline ≈ 79 d in the prolonged subset; step/sleep recovery faster than RHR.

### Claim 4.2 — Acute-phase wearable detection of COVID-19 is proven; discrimination is moderate
- **Claim:** Mishra/Snyder (5,262 smartwatch users; 32 COVID+): 81% (26/32) had detectable HR/steps/sleep alterations; 63% detectable pre-symptomatically; anomalies up to 9 days before symptom onset. DETECT (Quer/Radin, n=30,529; 3,811 symptomatic; 54 pos/279 neg): symptoms+sensors AUC 0.80 (IQR 0.73–0.86) vs 0.71 symptoms alone. Independent caveat study (PLOS ONE 2022): AUC 0.75 using all data but 0.63 pre-test-result only — part of the signal is **behavioral response to a positive test**, not physiology.
- **Evidence:** E3/E4 (controlled discrimination with within-person baselines). Sources: Mishra T et al., *Nat Biomed Eng* 2020;4:1208–1220, DOI 10.1038/s41551-020-00640-6; Quer G et al., *Nat Med* 2021;27:73–77, DOI 10.1038/s41591-020-1123-x, PMID 33122860; caveat: *PLOS ONE* 2022, DOI 10.1371/journal.pone.0277350.
- **Implementation:** defines the **acute-infection perturbation envelope** (ΔRHR, ΔHRV, Δsteps, Δsleep, onset lead time) for OCPE's infection-event generator; behavior/notification artifacts should be modeled separately from physiology.
- **Validation:** detector trained on synthetic data should reach AUC ≈0.75–0.80 (symptomatic window), not higher.

### Claim 4.3 — Oura/temperature: pre-symptomatic fever-like temperature deviations detectable
- **Claim:** TemPredict/UCSF (50 COVID+ cases): continuous finger temperature flagged fever-like deviations in 76% of cases, including pre-symptomatic window (avg skin temp +0.63°C at fever onset, p=0.024 in related analyses).
- **Evidence:** E2 (small, retrospective). Source: Mason AE/Smarr BL et al., TemPredict, *Sci Rep* 2022 (first cohort); UCSF press summary.
- **Implementation:** skin-temperature channel: +0.5–1.0°C deviation for 2–7 days around acute infection; no demonstrated *chronic* temperature signature in long COVID (do not add one).
- **Validation:** pre-symptomatic detection rate ~60–76%.

### Claim 4.4 — Endothelial dysfunction persists post-acutely (small meta-analytic signal)
- **Claim:** Meta-analysis (4 observational studies, n=465, post-acute): brachial FMD −3.35% (95% CI −4.90 to −1.81; I²=85%) vs healthy controls. Case-control (Ambrosino 2021): convalescents FMD ~4% vs controls ~5–6% overall; effect driven by males (females NS: 6.1±2.9 vs 5.3±3.4, p=0.362).
- **Evidence:** E5 (meta) built on E2 studies with high heterogeneity and confounding. Sources: PMC9487834 (meta-analysis, 2022; cf. Theofilis *Arch Cardiovasc Dis* 2022;115:675); Ambrosino P et al., *Biomedicines* 2021;9:957.
- **Limitations:** FMD not wearable-accessible; possible selection/confounding; no outcome linkage.
- **Implementation:** mechanistic backdrop only (E2); **no direct wearable signal** — optional correlate for exertional intolerance axis.
- **Validation:** none in wearable domain.

### Claim 4.5 — Routine cardiovascular labs/hemodynamics at rest are essentially normal in long COVID
- **Claim:** RECOVER (n=10,094; 8,746 infected, 1,348 uninfected): prior infection → platelets 265.9 vs 275.2 ×10⁹/L; HbA1c 5.58% vs 5.46%; uACR 81.9 vs 43.0 mg/g (all small); PASC≥12 vs 0 → **no meaningful differences** in any of 25 routine labs incl. NT-proBNP, troponin, D-dimer; hsCRP 5.01 vs 4.23 mg/L (small, clusters 1 & 4).
- **Evidence:** E2 (large, prospective, propensity-weighted, systematic symptom capture) — this is the key **null/boundary** result. Source: Erlandson KM et al., *Ann Intern Med* 2024;177:1209–1221.
- **Implementation:** OCPE should NOT give long-COVID synthetics globally elevated troponin/BNP/D-dimer/CRP. Mild hsCRP elevation allowed only in high-burden tier (~+0.8 mg/L mean shift).
- **Validation:** lab-mimic variables in synthetic data must show near-null group differences.

---

## 5. Respiratory domain

### Claim 5.1 — DLCO impairment is common after *hospitalized* COVID, not in mild/non-hospitalized long COVID
- **Claim:** Meta-analysis (hospital-discharge cohorts): DLCO<80% predicted in 48% (41–56%) at 0–3 mo, 33% (23–44%) at 3–6 mo, 43% (22–65%) at ≥6 mo; FVC<80% ~10–13%. Mean DLCO improves longitudinally (83.9 → 91.2 → 97.3% predicted). In a pneumonia-survivor cohort, abnormal DLCO 60.4% with CT-extent the main predictor (AUC 0.78).
- **Evidence:** E5 (meta-analysis; hospitalized-skewed). Sources: PMC8528387 (*Front Med* 2021, respiratory outcomes meta); PMC11635270.
- **Limitations:** mostly hospitalized; not applicable to the non-hospitalized long-COVID majority (RECOVER ~91% non-hospitalized); DLCO not wearable-accessible.
- **Implementation:** **severity-conditional**: DLCO/spirometry deficits only in a post-hospitalization sub-phenotype (proportion ≈10% of long COVID); SpO2 dips/exertional desaturation should be rare in mild-tier synthetics.
- **Validation:** DLCO-analog prevalence by acute-severity stratum.

### Claim 5.2 — Dysfunctional breathing/breathing-pattern disorder explains dyspnea in ~30% of dyspneic long COVID (normal PFT/VO2)
- **Claim:** CPET-classified dysfunctional breathing in 29.4% of 51 long-COVID patients with persistent dyspnea (mostly erratic/periodic-deep-sigh, *without* hyperventilation; normal DLCO median 85% pred; peak VO2 22.9 mL/min/kg); case series n=48: hyperventilation 20.8%, erratic/sighing 47.1%, mixed 33.3%, Nijmegen ≥23 in 68.9%, normal PFTs; BPAT-based study: 30% BPD prevalence in breathless long COVID. Dyspnea without hypoxemia is the norm in this subgroup.
- **Evidence:** E2 (clinic-referred, selection-biased; true population prevalence unknown). Sources: Frésard I et al., *BMJ Open Respir Res* 2022;9:e001126; Genecand L et al., 2023 (PMC10347459); CHEST review (UHasselt preprint).
- **Implementation:** **respiratory-pattern latent trait** in ~30% of dyspneic-tier synthetics: elevated/erratic respiratory rate, sigh frequency, mild hypocapnia-pattern (if modeled), normal SpO2. Composable with autonomic axis (recognized BPD–dysautonomia interplay).
- **Validation:** breathing-rate variability/sigh-rate parameters; SpO2 must remain normal in this phenotype.

---

## 6. Inflammatory / metabolic domain

### Claim 6.1 — Persistent routine inflammation markers are inconsistent and small (see Claim 4.5 for RECOVER null)
- **Claim:** Targeted studies report inflammatory signatures: IL-1β/IL-6/TNF triad associated with PASC (Schultheiss C et al., *Cell Rep Med* 2022;3:100663); persistent complement dysregulation/thromboinflammation in active long COVID (Cervia-Hasler et al., *Science* 2024;383:eadg7942; 113 patients, 39 controls, >6,500 proteins; 6-mo diagnostic signature); inflammatory protein subcategory (Talla et al., *Nat Commun* 2023;14:3417); partial convergence (Baillie et al., *Med* 2024;5:239–253). BUT RECOVER n=10,094 found no clinically useful routine-lab signal, and hsCRP mean shift only ~+0.8–1.0 mg/L in high-burden clusters.
- **Evidence:** E1/E2 (proteomics, single-to-few cohorts, awaiting independent replication) vs E2-large null for routine markers.
- **Implementation:** inflammation as **low-amplitude latent covariate** (hsCRP +0.5–1.0 mg/L in severe tier; none in mild tiers). Do NOT simulate large CRP/IL-6 elevations as a general long-COVID feature.
- **Validation:** hsCRP distribution vs Erlandson table.

### Claim 6.2 — Microclots / viral persistence / autoimmunity: mechanistic hypotheses, not demonstrated physiology
- **Claim:** Fibrinaloid microclots reported by a single research cluster (Pretorius/Kell group, e.g., *Cardiovasc Diabetol* 2021); independent groups have failed to replicate under standardized handling; Cochrane-style review concluded the microclot link "remains a hypothesis"; no RCT of apheresis/fibrinolytics. Viral persistence (spike/RNA in tissues months later) supported by several tissue studies but causal link to symptoms unproven. Autoantibody findings inconsistent across cohorts.
- **Evidence:** E0–E1. Do not implement as grounded perturbations.
- **Implementation:** these hypotheses may *motivate* the autonomic/exercise axes but contribute no validated parameters.

### Claim 6.3 — Modest increase in incident diabetes/insulin resistance post-COVID
- **Claim:** New-onset diabetes meta-analyses: RR 1.41 (95% CI 1.07–1.84; 12 studies, >48M participants; *Diabetes Res Clin Pract* 2025); another meta: RR 1.41 (1.38–1.44) but driven by one nationwide cohort — excluding it, RR 1.72 (0.77–3.85, NS). Biomarker pooling: HbA1c SMD 1.44 (0.36–2.52), HOMA-IR SMD 0.96 (0.33–1.58); FBG inconsistent (SMD 0.77, −0.40–1.94). RECOVER: HbA1c 5.58% vs 5.46% infected vs uninfected (attenuated when pre-existing diabetes excluded).
- **Evidence:** E5 (meta) but fragile; E2 for insulin-resistance signal. Effect concentrated in severe/hospitalized acute illness and corticosteroid exposure.
- **Implementation:** **metabolic drift as severity-conditioned**: small HbA1c shift (~+0.1%) and insulin-resistance propensity in post-hospitalized tier; rest-HR/long-term-activity effects may partially mediate. Not a distinct wearable phenotype.
- **Validation:** HbA1c group means vs RECOVER; incident-diabetes RR ≈1.4 only in severe stratum.

---

## 7. Sleep / circadian domain

### Claim 7.1 — Sleep disturbance is prevalent and increases with time-since-infection
- **Claim:** Meta-analysis (63 studies): sleep disorders in ~24% at 3–6 mo, 29% at 6–9 mo, 30% at >12 mo post-infection. RECOVER: sleep disturbance in 32% of PASC cases; unrefreshing sleep reported by 19.8% of post-acute infected (vs ~6% uninfected; ME/CFS-domain item). Stanford long-COVID clinic (n=200, ASQ): any sleep complaint 87%, insomnia 42.5%, sleep-related breathing complaints 57.5%, EDS 28.5%, extreme chronotype 11%; acute hospitalization → insomnia OR 4.41 (1.27–15.36). Cleveland Clinic PASC: 41.3% moderate-severe sleep disturbance.
- **Evidence:** E5 (meta, symptom-report based) + E2 clinic samples. Sources: meta via Wilson A et al., *Healthcare* 2025 (MDPI 13:2611); Thaweethai 2023.
- **Limitations:** mostly self-report; clinic samples enriched; circadian-phase data sparse (no large actigraphy/DLMO studies).
- **Implementation:** **sleep latent axis**: sleep-onset latency ↑, WASO ↑, sleep efficiency −5–15%, unrefreshing-sleep flag, ~30–40% penetrance in symptomatic tier; possible delayed-phase tendency (~10%). Composable with PEM/autonomic axes.
- **Validation:** prevalence ~30% at >6 mo in synthetic symptomatic cohort.

### Claim 7.2 — Wearable-measured sleep changes are mostly acute-phase; chronic objective sleep data are thin
- **Claim:** DETECT/related: sleep minutes increased more in COVID+ than COVID− after symptom onset (+47.9 vs +16.6 min; AUC 0.66); sleep returned to baseline faster (~24 d) than RHR (~79 d) in prolonged cases (Radin 2021). No large, controlled, *chronic-phase* wearable sleep-architecture dataset exists; long-COVID wearable sleep claims rest on small studies.
- **Evidence:** E3/E4 for acute; E2 (sparse) for chronic.
- **Implementation:** acute: sleep +30–60 min/night during infection week; chronic: rely on Claim 7.1 symptom-level perturbation (efficiency/latency), explicitly flagged as lower-confidence.

---

## 8. Wearable evidence specific to long COVID discrimination/monitoring (KEY)

### Claim 8.1 — Prolonged RHR elevation post-infection is the best-replicated long-COVID-adjacent wearable signal (see Claim 4.1; magnitudes: acute +5–15 bpm, chronic tail +1–3 bpm, ≥5 bpm in 7–14% at 12 wk, mean 79 d to baseline in prolonged subset)

### Claim 8.2 — Long-COVID-specific ML discrimination from longitudinal HR is promising but likely optimistic
- **Claim:** PLOS Digit Health 2024 (n=126 acute infections; HR dynamics features + symptoms): combined model ROC-AUC 0.951, PR-AUC 0.859 for long-COVID status. ResearchSquare preprint (Fitbit/Oura-scale): detected long-COVID users show persistent nightly RHR elevation and RMSSD suppression for months vs acute-only users who return to baseline.
- **Evidence:** E2 (small n, retrospective feature engineering, overfitting risk high; no external validation).
- **Implementation:** use as **upper bound**: OCPE synthetic long-COVID should be *detectable* from HR/HRV trajectories at AUC ≤0.85 in realistic conditions; if a trivial classifier hits >0.95, perturbations are probably too stereotyped.
- **Validation:** classifier AUC target band 0.75–0.85 (symptom-informed) on synthetic data.

### Claim 8.3 — Within-person wearable HRV/HR predict day-level symptom crashes in long COVID/ME/CFS-type illness
- **Claim:** High-density mHealth dataset (n=4,244 observations, ~125 observations/participant, 60-s morning PPG + evening symptoms): morning HR↑ and HRV↓ predicted same-evening crash/fatigue/brain-fog worsening; walk-forward AUC 0.82–0.85 vs 0.73–0.83 without biometrics. Separate study (AMMES/2025): long-COVID patients show lower HRV across daily activities and sleep (p<0.027); HRV remains depressed 24 h after exercise at/above first ventilatory threshold (VT1) in patients but not controls (p=0.010) — proposed as a wearable PEM threshold marker.
- **Evidence:** E2/E3 (prospective within-person design; wearables in free-living conditions). Sources: PMC13022203 (2025); AMMES conference report 2025.
- **Implementation (high value for OCPE):** **PEM trigger-response dynamics**: exercise bouts above VT1-equivalent → next-24-h HRV suppression (−10–30%) and resting/sleep HR elevation, plus activity reduction 24–72 h. Implement only in PEM+ phenotype (~25–30% of symptomatic long COVID; 80%+ in ME/CFS tier).
- **Validation:** lagged HR/HRV↔symptom coupling; post-exertion recovery slope differences vs synthetic controls.

### Claim 8.4 — Acute-detection performance numbers to mirror (see Claim 4.2: AUC 0.80 DETECT; 81% case detection, 63% pre-symptomatic, up to 9 d lead — Mishra; 76% temperature flag — TemPredict)

### Claim 8.5 — Post-exertion wearable autonomic signature is the closest thing to an objective PEM correlate
(See Claim 8.3.) Convergent with 2-day CPET logic but observable continuously; note 2-day CPET lab results themselves are contradictory in long COVID (Claim 3.4), so model the *ambulatory* version.

---

## 9. Heterogeneity, trajectory, and modifiers

### Claim 9.1 — Variant and vaccination strongly modulate incidence
- **Claim:** ZOE (vaccinated, matched): long COVID (≥4 wk) 4.5% (2,501/56,003) Omicron vs 10.8% (4,469/41,361) Delta; OR 0.24–0.50 depending on time since vaccination (Antonelli M et al., *Lancet* 2022;399:2263–2264). RECOVER Omicron-era: 10% PASC+ at 6 mo (stricter index). Vaccination meta-analyses: any dose vs none OR 0.77 (0.70–0.85, 10 studies, Omicron era; PMC12644529, 2025); booster vs none OR 0.74 (0.63–0.86); booster vs primary OR 0.77 (0.65–0.92). Earlier systematic review (Byambasuren O et al., *BMJ Med* 2023;2:e000385): 10/12 studies showed significant reduction, ORs 0.22–1.03 (1 dose), 0.25–1.02 (2 doses), high heterogeneity, low certainty.
- **Evidence:** E5 (meta) for vaccination; E2 large for variant effect.
- **Implementation:** **incidence modifiers** in the generative prior: multiply long-COVID probability by ~0.5 (Omicron vs Delta era) and by ~0.7–0.8 (vaccinated), ×~0.75 booster. Female sex and acute hospitalization increase persistent-severe trajectory probability.
- **Validation:** stratified incidence in synthetic cohorts.

### Claim 9.2 — Symptom duration distribution is heavy-tailed
- **Claim:** Of Omicron-era LC at 3 mo, 81% persist/intermittent at 1 yr (RECOVER trajectories); IHME/WHO: 15.1% of PCC cases still symptomatic at 12 mo (hospitalized-era weighted); ZOE: median acute symptom duration shorter in Omicron.
- **Implementation:** sample duration from a heavy-tailed mixture: rapid recovery (~19% by 12 mo), relapsing-remitting (intermittent trajectories common), persistent-severe minority (~10–20% of LC).
- **Validation:** survival curve of synthetic symptoms vs RECOVER 8-trajectory proportions.

### Claim 9.3 — Background-rate caution (ascertainment)
- **Claim:** Uninfected RECOVER participants still report PEM 7%, fatigue 17%, brain fog 4%, OI ~6%, ME/CFS criteria 0.6% — synthetic "control" populations must carry non-zero background symptom/wearable-noise rates to avoid trivial classification.
- **Evidence:** E2 (RECOVER uninfected arm).
- **Implementation:** all long-COVID perturbations must be **excess-over-background**, not absolute.

---

## 10. Phenotype-composability table (OCPE design target)

| Phenotype axis (latent) | Proposed penetrance (of symptomatic LC) | Key wearable parameters (direction, magnitude, timescale) | Evidence level | Composability recommendation |
|---|---|---|---|---|
| Post-acute infection response (standalone layer, all infected) | 100% acute; prolonged tail 7–14% | RHR +5–15 bpm acute → +1–3 bpm (tail ≥5 bpm) × 2–5 mo; steps ↓ (~32 d); sleep +30–60 min acute (~24 d); skin temp +0.5–1.0 °C acute | E4 | **Standalone base layer**; phenotypes compose on top |
| Autonomic dysregulation (POTS-like/OI) | ~25% symptom-level; consensus-POTS small % | Standing ΔHR graded 0–>30 bpm; resting HR +1–3 bpm chronic; SDNN −15–25%; RMSSD −10–20% (partial penetrance); exertional HR slope blunted if CI co-present | E2 (contradictory for POTS dx) | **Composable latent**; correlate with cluster-4 analogue |
| Chronotropic incompetence | ~30% of symptomatic (LIINC; selection-biased) | Peak HR %pred ~86% vs 94%; AHRR <80%; HRR1 −8 bpm; higher min HR | E2 | Composable with autonomic axis (shared mechanism) |
| PEM / ME/CFS-like (severe tier) | 4.5% of infected full ME/CFS; PEM+ ~25–30% of symptomatic | Post-exertion (VT1+) 24–72 h: HRV −10–30%, nocturnal HR ↑, activity ↓; delayed flare 12–48 h | E2–E3 (ambulatory); E4 in ME/CFS only | **Composable severe tier**; do not require day-2 VO2 decrement |
| Exercise-capacity reduction | ~49% symptomatic (clinic) vs 16% recovered | Peak VO2 −5 (±5) mL/kg/min; severe −7 to −10; peripheral-extraction pattern | E5 (low certainty) | Composable; severity-scaled |
| Dysfunctional breathing | ~30% of dyspneic | Erratic respiratory rate, sigh pattern, normal SpO2, normal PFT | E2 | Composable with autonomic axis |
| Post-hospitalization cardiopulmonary (DLCO-type) | ~10% of LC (acute-severity gated) | Exertional SpO2 dips (rare), low VO2 ceiling | E5 (hospitalized only) | **Standalone severity-stratified module**, not in mild LC |
| Sleep/circadian disturbance | ~30–40% symptomatic | Sleep efficiency −5–15%, latency ↑, unrefreshing flag, delayed phase ~10% | E5 (symptom meta) / E2 (objective thin) | **Composable latent** |
| Inflammatory/metabolic drift | severity-gated | No direct wearable signal; optional resting HR/HRV covariance | E2/E5-fragile | Background covariate only; NOT a wearable phenotype |
| Smell/taste (RECOVER cluster 1) | — | No wearable signal | E2 | Symptom label only; exclude from physiological generator |

---

## 11. Cross-cutting limitations (apply to all claims)

1. **Control-group problems**: many studies lack uninfected or recovered controls; RECOVER uninfected arm shows non-trivial background symptom rates (PEM 7%).
2. **Referral/ascertainment bias**: clinic samples (POTS 79%, DB 30%, SFN 46%) cannot be read as population prevalences.
3. **Replication status young**: complement/proteomic signatures, SFN, microclots, 2-day CPET in LC — all single-to-few cohorts or contradicted; flagged per claim.
4. **Behavioral contamination of wearable signals**: part of acute "detection" signal reflects behavior change after a positive test (PLOS ONE 2022 caveat).
5. **Era dependence**: most physiological studies used pre-Omicron, largely unvaccinated, often previously hospitalized samples; magnitudes likely overestimate current-era mild-case effects.
6. **No validated biomarker**: RECOVER labs null (Erlandson 2024) is the boundary condition for any synthetic-data realism check.

## 12. Validation strategy for OCPE long-COVID module

1. Reproduce DETECT/Radin statistics: fraction with RHR ≥5 bpm at 12 wk (7–14%); mean 79 d normalization in prolonged subset; triphasic RHR course.
2. Detector calibration: symptom+sensor classifier on synthetic acute COVID should reach AUC 0.75–0.80, not >0.9.
3. Long-COVID discrimination from chronic HR/HRV trajectories: AUC target band 0.75–0.85; >0.95 → perturbations too stereotyped.
4. Group-mean checks: peak VO2 −4.9 (−6.4, −3.4) symptomatic vs recovered; SDNN −15–25%; hsCRP near-null except severe tier; HbA1c +0.1% infected vs uninfected.
5. Phenotype prevalences: PEM ~25–30% of symptomatic (excess over 7% background); ME/CFS 4.5%; OI symptoms ~25%; sleep disturbance ~30%; Omicron/vaccinated incidence scaling (×0.5, ×0.7–0.8).
6. Trajectory distribution: 8-class mix with ~81% of 3-mo cases persistent/intermittent at 12 mo.
7. Negative controls: synthetic uninfected cohorts must retain background symptom rates; no troponin/BNP/D-dimer/CRP elevation in mild LC.

## 13. Key references (verified identifiers only)

1. Soriano JB et al. Lancet Infect Dis 2022;22:e102–7. DOI 10.1016/S1473-3099(21)00703-9. PMID 34951953.
2. Thaweethai T et al. JAMA 2023;329:1934–46. DOI 10.1001/jama.2023.8823. PMID 37278994.
3. Vernon SD et al. (RECOVER). J Gen Intern Med 2025. DOI 10.1007/s11606-024-09290-9.
4. Erlandson KM et al. Ann Intern Med 2024;177:1209–21. (RECOVER labs null.)
5. Thaweethai T et al. Long COVID trajectories, RECOVER-Adult. Nat Commun 2025;16:9557.
6. Radin JM et al. JAMA Netw Open 2021;4(7):e2115959. DOI 10.1001/jamanetworkopen.2021.15959.
7. Quer G et al. Nat Med 2021;27:73–7. DOI 10.1038/s41591-020-1123-x. PMID 33122860.
8. Mishra T et al. Nat Biomed Eng 2020;4:1208–20. DOI 10.1038/s41551-020-00640-6.
9. Durstenfeld MS et al. JAMA Netw Open 2022;5(10):e2236057. DOI 10.1001/jamanetworkopen.2022.36057. (CPET meta.)
10. Durstenfeld MS et al. (LIINC CPET/chronotropic incompetence). Open Forum Infect Dis 2023 (PMC10686699).
11. Singh I et al. Chest 2022;161:54–63. DOI 10.1016/j.chest.2021.08.010. PMID 34389297. (iCPET.)
12. Two-day CPET LC n=15: PMID 39490617 (2024). Larger 2-day CPET LC vs ME/CFS vs controls: DOI 10.1007/s12018-026-09326-0 (2026).
13. Seeley MC et al. Am J Med 2023. DOI 10.1016/j.amjmed.2023.06.010. (POTS 79% active-stand.)
14. HUTT case-control long COVID autonomic study 2025 (PMC12551903). (POTS 0% consensus.)
15. Fanni G et al. J Neurol 2025. DOI 10.1007/s00415-025-13518-x. (29% POTS in referrals.)
16. SFN Yale case-control: PMID 38630952 (2024). Falco et al. painful-LC SFN 46% (via PMC11343176). Null biopsy series: LCCS (~100 LC vs recovered controls; vjneurology report).
17. Frésard I et al. BMJ Open Respir Res 2022;9:e001126. Genecand L et al. 2023 (PMC10347459). (Dysfunctional breathing.)
18. DLCO meta-analysis: PMC8528387 (2021). DLCO prediction: PMC11635270.
19. FMD meta-analysis: PMC9487834 (2022); Ambrosino P et al. Biomedicines 2021;9:957.
20. Antonelli M et al. Lancet 2022;399:2263–4. (Omicron 4.5% vs Delta 10.8%.)
21. Byambasuren O et al. BMJ Med 2023;2:e000385. Vaccination meta 2025 (PMC12644529).
22. New-onset diabetes meta: Diabetes Res Clin Pract 2025 (RR 1.41, 1.07–1.84); Front Endocrinol 2026 meta (HbA1c/HOMA-IR SMDs).
23. Cervia-Hasler C et al. Science 2024;383:eadg7942. DOI 10.1126/science.adg7942. Schultheiss C et al. Cell Rep Med 2022;3:100663. Talla A et al. Nat Commun 2023;14:3417. Baillie K et al. Med 2024;5:239–53.
24. Sleep: Wilson A et al. Healthcare 2025;13:2611; 63-study meta (2022) cited therein.
25. Long-COVID wearable ML: PLOS Digit Health 2024 (DOI 10.1371/journal.pdig.0001093); within-person crash prediction PMC13022203 (2025); AMMES HRV/VT1 PEM study 2025.
26. UK citizen-science wearable long COVID: Lancet Digit Health 2024 (PMC11832456).
27. Microclots: Pretorius/Kell group (Cardiovasc Diabetol 2021 onward); Cochrane-style review conclusion = hypothesis only; independent non-replication under standardized handling (see Section 6, Claim 6.2).
