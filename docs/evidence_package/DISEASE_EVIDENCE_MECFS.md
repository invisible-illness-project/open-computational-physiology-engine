# OCPE Disease Evidence Base — Myalgic Encephalomyelitis / Chronic Fatigue Syndrome (ME/CFS)

**Purpose:** Evidence base for generating synthetic wearable physiology datasets, with special focus on **post-exertional malaise (PEM) as a delayed, multi-day dynamic perturbation** — not a scalar.

**Evidence grading (used throughout):**
- **E0** hypothesis/mechanistic speculation
- **E1** mechanistic (biomarker/preclinical/physiology pathway)
- **E2** observational human
- **E3** controlled human experimental
- **E4** replicated quantitative (multiple independent groups)
- **E5** meta-analysis / consensus

**Key sampling caveat (applies to nearly ALL studies below):** Most lab/CPET studies recruit ambulatory mild-to-moderate patients; severe/housebound/bedbound patients (~25% of the ME/CFS population) are largely excluded because they cannot travel to a lab or tolerate exercise testing. Baseline effect sizes below therefore likely **underestimate** the population-level deviation; wearable-based severity gradients (Section 8–9) are the best source for severe-range parameters.

**A note on PEM definition across criteria:** Fukuda (1994) lists "post-exertional malaise >24 h" as one of 8 optional minor symptoms (4 of 8 required; PEM not mandatory). Canadian Consensus Criteria (CCC 2003) and ICC 2011 make PEM mandatory. IOM 2015/SEID makes PEM mandatory and adds orthostatic intolerance as an optional cardinal feature. Studies using Fukuda-only cohorts may include patients without true PEM; this drives heterogeneity in nearly every meta-analysis cited.

---

## SECTION 1 — DEFINITION / DIAGNOSIS

### CLAIM 1.1 — PEM is the hallmark, mandatory feature of modern ME/CFS definitions
- **Claim:** PEM (worsening of multi-system symptoms after previously tolerated physical/cognitive/emotional exertion) is required by CCC 2003, ICC 2011, and IOM 2015/SEID criteria; Fukuda 1994 does not require it.
- **Domain:** definition | **Variable:** case status
- **Mechanism:** n/a (nosological)
- **Direction:** n/a | **Magnitude:** PEM present in >80–95% of patients depending on criteria and phrasing (Jason et al. found self-reported PEM prevalence ranged 40.6–93.8% depending on question wording — a measurement problem, not just biology).
- **Timescale:** disease-defining feature; PEM itself operates on 12 h–weeks scale (Section 4).
- **Population:** all severities; ~836,000–2.5 M US prevalence (IOM 2015).
- **Wearable modality:** none directly; PEM defined symptomatically — no validated objective wearable test exists.
- **Evidence level:** **E5** (consensus across case definitions)
- **Source:** IOM 2015, *Beyond ME/CFS: Redefining an Illness*, National Academies Press, DOI 10.17226/19012; Carruthers et al. 2003 CCC, *J Chronic Fatigue Syndr* 11:7–115; Fukuda et al. 1994, *Ann Intern Med* 121:953–959, PMID 7978722.
- **Contradictory:** Fukuda-defined "CFS" cohorts without mandatory PEM dilute biomarker and exercise findings; some authors argue PEM is not fully specific to ME/CFS (also seen in long COVID, Gulf War illness).
- **Limitations:** PEM is still symptom-defined; quantitative thresholds (how much worsening, which domains) not standardized.
- **Implementation recommendation:** Model PEM as a latent state variable gating a multi-day perturbation kernel (Section 11); severity of the PEM phenotype should scale the kernel amplitude. Do not treat Fukuda-only synthetic cohorts as equivalent to CCC/IOM cohorts.
- **Validation strategy:** Synthetic PEM episodes should reproduce published onset-delay/duration distributions (Claims 4.1–4.3).

### CLAIM 1.2 — ME/CFS is heterogeneous; severity grading is physiologically meaningful
- **Claim:** Clinician-assigned severity grades (mild/moderate/severe) map onto large, graded differences in objective function.
- **Domain:** heterogeneity | **Variable:** steps/day, %predicted VO2 at VT, %predicted peak VO2
- **Magnitude (n=289; 42% mild, 34% moderate, 24% severe; mean duration 12±9 y):**
  - Steps/day: mild 8235±1004; moderate 5195±1231; severe 2031±824
  - %predicted VO2@VT: mild 47±11%; moderate 38±7%; severe 30±7%
  - %predicted peak VO2: mild 90±14%; moderate 64±8%; severe 48±9%
  - All p<0.0001.
- **Evidence level:** **E2/E4** (single large clinic study, objective actometer + CPET)
- **Source:** Pheby/Saffron et al., "Validation of the Severity of ME/CFS (ICC grading)," *Healthcare* 2020;8(3):273 (PMC7551321).
- **Limitations:** single-center referral clinic; ICC grading by clinicians; within-grade variability is large (e.g., mild SD ~1000 steps around 8235).
- **Implementation:** Severity must be a first-class latent variable in OCPE: mild ~8,000 steps/d, moderate ~5,000 steps/d, severe ~2,000 steps/d; PEM thresholds and autonomic deviations should scale accordingly.
- **Validation:** Marginal step-count distributions of synthetic cohort should match these tertiles.

---

## SECTION 2 — BASELINE PHYSIOLOGY VS HEALTHY (resting state)

### CLAIM 2.1 — Resting HR is modestly elevated
- **Claim:** ME/CFS patients have higher resting HR than controls.
- **Domain:** autonomic/cardiac | **Variable:** resting heart rate (bpm)
- **Direction/Magnitude:** **+4.14 bpm (MD, 95% CI ±1.30; p<.001)**; supine +4.02±2.11, seated +4.53±2.40; 43 studies (n=1766 patients, 1291 controls). High heterogeneity (I² 62–73%).
- **Timescale:** chronic baseline (seconds-to-minutes measurement; present day and night).
- **Evidence level:** **E5**
- **Source:** Nelson MJ et al. 2019, *J Transl Med* 17:268 (PMC6824690).
- **Contradictory/limitations:** The pooled difference (~4 bpm) is **smaller than typical day-to-day within-person RHR variation (~5 bpm)** — not individually diagnostic. Possible confounds: deconditioning, medications, uncontrolled breathing rate.
- **Implementation:** Add +3–5 bpm offset to baseline RHR in ME/CFS synthetic personas (severity-scaled); expect large between-study dispersion, so keep within-person noise σ ≳ 4–5 bpm.
- **Validation:** Cohort mean RHR ≈ control+4 bpm; individual values overlap controls substantially.

### CLAIM 2.2 — Resting HRV: reduced vagal / increased sympathetic modulation
- **Claim:** Resting HRV shows reduced parasympathetic indices.
- **Variable:** RMSSD, HF power, LF/HF
- **Magnitude (Nelson 2019 meta-analysis, SMD ± 95% CI):** HF power **−0.34±0.22 (p=.002)**; RMSSD **−0.37±0.32 (p=.02)**; LF/HF ratio +0.20±0.25 (p=.11, NS); LF power +0.39±0.22 (p<.001). Effect sizes **small**.
- **Evidence level:** **E5** (but small effects, fewer studies than HR)
- **Source:** Nelson et al. 2019 (PMC6824690). Supporting: Boneva et al. 2007 (*Auton Neurosci* 137:94–101, DOI 10.1016/j.autneu.2007.08.002) — population-based; higher HR + reduced HRV **persist during sleep**.
- **Contradictory:** Tak et al. 2009 meta-review found no significant difference in *daytime* resting autonomic function vs controls in some analyses; nocturnal findings conflict (Claim 7.2 — one PSG study found *lower* nocturnal HR in CFS vs tired controls, opposite of Boneva 2007). Effect sizes small and heterogeneous; LF/HF interpretation as "sympathovagal balance" is contested methodologically.
- **Implementation:** Baseline RMSSD ~ −0.35 SD (≈ −10–20% relative, depending on age/sex norms), HF −0.34 SD; keep large inter-individual overlap.
- **Validation:** Synthetic resting HRV distributions: small group-mean shift, large overlap; do NOT model ME/CFS as drastically low HRV.

### CLAIM 2.3 — Maximal HR is reduced (chronotropic incompetence)
- **Claim:** HRmax/HRpeak lower in ME/CFS.
- **Magnitude:** HRpeak (symptom-limited) **−16.62±4.68 bpm**; true criterion HRmax **−5.81±3.34 bpm** (I²=0%) — Nelson 2019 E5. In a 2-day CPET series: peak HR 157±19 (ME/CFS) vs 166±11 (controls) (Nelson 2026 null study, Front Physiol).
- **Mechanism (E1):** hypothesized sympathetic overdrive → β-receptor downregulation; chronotropic incompetence (maxHR <80% predicted) observed in 9/58 ME/CFS vs 1/25 controls in one series.
- **Evidence level:** **E4/E5**
- **Limitations:** partly confounded by effort; even criterion-based true HRmax remains lower (~6 bpm).
- **Implementation:** Peak HR ceiling −6 to −17 bpm (severity/effort dependent); a subset (~15%) shows marked chronotropic incompetence.

### CLAIM 2.4 — Orthostatic intolerance is near-universal physiologically, even with "normal" HR/BP
- **Claim:** Orthostatic stress produces exaggerated HR rise and reduced cerebral blood flow (CBF) in most ME/CFS patients, including the majority with normal HR/BP tilt responses.
- **Magnitude:**
  - HR during HUT: SMD **+0.92±0.24** (p<.001); ΔHR on standing SMD +0.86±0.46; orthostatic HR response SMD +0.50±0.27 (Nelson 2019, E5).
  - van Campen et al. 2020 (n=429 ME/CFS, 44 controls; 70° 30-min HUT): end-tilt CBF reduction **−26%** (ME/CFS) vs **−7%** (controls); −24% in the 58% with normal HR/BP response; −28% dOH; −29% POTS. Abnormal CBF (>13% reduction) in **90%** of patients. Phenotypes: 58% normal hemodynamic, 14% delayed OH, 28% POTS. (PMID 32140630, DOI 10.1016/j.cnp.2020.01.003; E3, large.)
  - Severe disease: 20°/15-min tilt → CBF −27% (n=19); seated-only challenge → CBF −24.5% vs −0.4% controls (n=100 severe; Healthcare 2020;8(4):394).
  - Post-tilt recovery: CBF reduction persists ≥10 min after return to supine (van Campen 2021, PMC8505270) — i.e., slow recovery dynamics, relevant to multi-hour timescale modeling.
  - Cardiac index during tilt: decreased **−26±7%** (severe cohort; p<.0001).
  - IOM 2015 synthesis: 42% of adults with ME/CFS develop hypotension on >10-min orthostatic tests vs 15% of controls (14 controlled studies, n=484).
- **Evidence level:** **E4** (large controlled Doppler series) for CBF; **E5** for HR responses.
- **Contradictory:** CBF-via-extracranial-Doppler method not yet independently replicated by other groups (single-group dominance, van Campen/Visser/Rowe) — treat magnitude with caution; prevalence across older HR/BP-only studies ranged 0–96%.
- **Implementation:** Orthostatic module: exaggerated ΔHR on standing (effect ~0.5–0.9 SD), widened distribution to include ~25–30% POTS-like (ΔHR ≥30 bpm), ~14% delayed OH. Time course: CBF-equivalent signal recovers slowly (>10 min post-supine).
- **Validation:** Stand-test ΔHR distribution; tilt CBF endpoints for a severe persona.

### CLAIM 2.5 — 24-h average HR does NOT differ from controls
- **Claim:** Despite elevated resting HR, daily average HR (24-h ECG) is not different.
- **Magnitude:** SMD 0.11±0.27 (p=.45), 2 studies (n=80/162) — Nelson 2019.
- **Interpretation:** lower daytime activity counterbalances higher resting HR — a modeling constraint: net daily mean HR ≈ normal even though resting and orthostatic components are elevated.
- **Evidence level:** **E2** (only 2 studies).

### CLAIM 2.6 — Activity levels are reduced and "stalled"; day-to-day variability high
- **Claim:** Objective activity (actometer/wearable steps) is reduced ~30–75% vs healthy norms, scales with severity, with high day-to-day variability (boom–bust).
- **Magnitude:** mild 5566–8235; moderate ~5000; severe ~2000 steps/day (Claims 1.2 + Rekeland 2022: mild 5566, moderate 4991, severe 1998; day-by-day variation mean 47%, range 25–79%). Mean cohort 5701±2670 steps/d (n=289).
- **Evidence level:** **E4** (two independent wearable series, n=289 and n=27)
- **Sources:** Healthcare 2020;8(3):273 (PMC7551321); Rekeland et al. 2022, *PLoS One* 17:e0274472 (DOI 10.1371/journal.pone.0274472; Fitbit Charge 3 + SenseWear, 6-month monitoring).
- **Implementation:** See Section 8. Day-level steps should be modeled with boom–bust autocorrelation structure (overexertion day → 1–7 suppressed days), not i.i.d. daily noise.

---

## SECTION 3 — EXERCISE INTOLERANCE (single-day and 2-day CPET)

### CLAIM 3.1 — Single-day VO2peak is moderately reduced
- **Claim:** Peak VO2 is lower in ME/CFS vs healthy controls.
- **Magnitude:** Pooled **−5.2 mL/kg/min (95% CI 3.8–6.6)**, 32 studies; prediction interval −1.9 to 12.2 (substantial heterogeneity, tau 3.4). CDC MCAM: peak VO2 23.4±8.6 vs 29.9±10.9 mL/kg/min, effect size **−0.66** (n=179 vs 169); VT VO2 11.4±3.4 vs 13.5±4.4 (ES −0.50).
- **Evidence level:** **E5**
- **Source:** Franklin et al. 2019, *Int J Sports Med* 40:77–87, PMID 30557887.
- **Contradictory:** Some single-day studies find no difference (Bazelmans 2001; Cook 2003); in MCAM matched-pairs subset the difference vanished (25.2±9.2 vs 25.1±9.0, ES 0.02) when patients/controls matched on activity — deconditioning vs disease debate is unresolved. Nelson 2019 noted studies with strict effort criteria found **no VO2max difference**.
- **Implementation:** Baseline VO2peak deficit ~−5 mL/kg/min mean with wide dispersion; do not make it deterministic.

### CLAIM 3.2 — 2-day CPET: Day-2 decline at ventilatory threshold is the most replicated objective PEM signature
- **Claim:** ME/CFS patients fail to reproduce Day-1 CPET values 24 h later, especially **work rate at VT**, while controls reproduce or improve.
- **Magnitude (by study):**
  - VanNess 2007 (pilot): VO2@VT −30% day 2.
  - Keller 2014 (n=22, no controls): VO2peak −13.8%, HRpeak −9 bpm, Work@peak −12.5%, VO2@VT −15.8%, **Work@VT −21.3%**; RER ≥1.1 both days (effort valid). DOI 10.1186/1479-5876-12-104.
  - Snell 2013 (n=51 vs 10): Work@VT 49.4±20.4 W → 22.2±18.1 W (**−55%**); peak VO2 21.5±4.1 → 20.4±4.5. *Phys Ther* 93:1484–1492.
  - Hodges 2018: Work@VT −12% (ME/CFS) vs +9% (controls); also vs MS. *Clin Physiol Funct Imaging* 38:639–644.
  - Nelson 2019 (n=16 vs 10): Work@VT 87.8±29.6 → 72.5±27.7 W (interaction p=.003); ROC: −6.3% to −9.8% ΔWork@VT optimal cut; ≥9.8% gives 100% specificity. J Transl Med 17:80 (PMC6417168).
  - Lien 2019 (Norway, n=18 vs 15): peak VO2 and VO2@VT significantly lower day 2; arterial lactate at VT **higher** on day 2 in ME/CFS (lower in controls).
  - van Campen 2020 male/female series (n=25 M; n=82 F): significant day-2 declines in VO2peak, VO2@VT, Work; declines comparable across severity strata (no controls).
  - **Lim 2020 meta-analysis (5 studies, 98 patients/51 controls):** Test2−Test1 ΔWork@VT: patients **−14.6 W** vs controls **+6.5 W**; patient−control difference at Work@VT: −10.8 W (test 1) → **−33.0 W (test 2)** (p=0.03–0.05); VO2peak difference NS (p=0.23). *J Clin Med* 9:4040, DOI 10.3390/jcm9124040. **E5**.
  - **Keller 2024 (largest, multicenter; n=84 ME/CFS vs 71 sedentary controls):** Day-2 declines at peak in ME/CFS: work −5.5%, exercise time −6.6%, VO2 −5.3%, VE −7.2%, HR −2.6%, O2pulse −4.0%, RPP −3.4%; at VAT: VO2 −6.8%, work −9.4%; controls declined only VCO2 −3%. Median ΔVO2peak −5.1% vs −2.0%; best threshold −9.3% → sensitivity ~33%, specificity ~90%. J Transl Med 22, DOI 10.1186/s12967-024-05410-5. **E4**.
  - **Franklin 2022 meta-analysis of repeated maximal tests:** retest Work@AT pooled **−21 W (95% CI −38 to −4)** greater decline in ME/CFS; peak work rate −8.55 W. *Fatigue* 10(3):119–135. **E5**.
- **Mechanism (E1):** earlier VT onset day 2 → earlier reliance on anaerobic metabolism; proposed causes: impaired O2 delivery (lower O2 pulse/stroke volume, narrowed pulse pressure), muscle pH dysregulation, metabolic switching. Day-2 lactate at VT elevated (Lien 2019) supports metabolic abnormality.
- **Timescale:** perturbation present 24–48 h after a single maximal effort (CPET-1 as trigger); consistent with PEM onset window.
- **Trigger-response-recovery:** Trigger = maximal CPET (~8–15 min); measurable physiological decrement at +24 h; symptom recovery 1–64 d (Claim 4.2).
- **Evidence level:** **E4/E5** — replicated across ≥6 independent labs and two meta-analyses.
- **CONTRADICTORY / NULL (important):**
  - Nelson et al. 2026 (n=58 ME/CFS vs 25 sedentary controls; Front Physiol, DOI 10.3389/fphys.2026.1816082): **no Day1→Day2 change** in peak VO2 (22.3±5.4→22.5±5.4) or VO2@VT in either group; 22% of patients vs 33% of controls had ≥1 mL/kg/min day-2 decline. Concludes 2-day CPET does not define PEM.
  - Davenport 2020 (n=51 women vs 10): day-2 peak VO2 decrement comparable between groups.
  - Vermeulen 2010: no test-retest difference in max HR or work; peak VO2 fell ~1.4 mL/kg/min but VT unchanged.
  - Effort confound: Keller 2024's own data showed Day-2 %HR reserve fell below the 80% effort criterion in the ME/CFS group — Day-2 "decline" may partly reflect inability to mount maximal effort during PEM (which is itself the phenomenon) rather than a pure peripheral capacity change.
  - Cross-study variability: Δpeak VO2 from +5.3% to −14%; ΔVO2@VT from +6.1% to −27%.
- **Limitations:** small single-center studies dominate; different ramp protocols; most cohorts mild–moderate (severe cannot complete 2-day CPET); %predicted values absent in meta-analysis.
- **Implementation:** For a PEM-episode perturbation on day +1 to +3 post-trigger: reduce achievable "VT-equivalent" intensity by 10–20% (i.e., HR/pace at which fatigue/lactate surrogates spike), peak capacity by 5–7%. Represent inter-individual response as a mixture: ~50–60% of patients show a clear Day-2 signature, others not.
- **Validation:** Synthetic 2-day CPET emulation should reproduce Lim 2020 pooled ΔWork@VT and Keller 2024 % declines; null-finding arm must remain plausible (~40% of cohorts).

### CLAIM 3.3 — Invasive CPET: preload failure and impaired peripheral O2 extraction
- **Claim:** Invasive (right-heart catheter) CPET shows cardiac preload failure and reduced peripheral oxygen extraction in ME/CFS.
- **Magnitude:** Joseph et al. 2021 (n=10 PI-ME/CFS + controls; *Chest* 160:642–651, DOI 10.1016/j.chest.2021.01.082): all patients showed impaired systemic O2 extraction (low peak a-vO2 difference); 6/10 preload failure (blunted biventricular filling pressures despite high flow). Pyridostigmine RCT (Joseph 2022, *Chest* 162:1116–1126): improved O2 extraction and exercise capacity vs placebo — causally implicating neurovascular dysregulation.
- **Related:** van Campen/Visser 2018 — cardiac index and stroke volume index falls during tilt greater in ME/CFS, unrelated to VO2peak (argues against deconditioning).
- **Evidence level:** **E3** (controlled invasive) + E1.
- **Limitations:** tiny n; single center (Systrom lab); replication pending.
- **Implementation:** During PEM-state, increase submaximal HR for a given workload (lower O2 pulse), and blunt the HR–workload slope at high intensity.

### CLAIM 3.4 — Ventilatory abnormalities: hypocapnia/hyperventilation in ~1/3
- **Claim:** Abnormal breathing patterns and persistent hypocapnia during low-level exercise in ~31% of ME/CFS vs 4% of sedentary controls.
- **Magnitude (2-day CPET cohort, n=58 vs 25; PMC12640868):** Resting PetCO2: hyperventilators 28.3±5.7 vs non-HV 36.9±4.5 mmHg; at AT 36.2±4.0 vs 42.7±4.8; at max 32.1±3.4 vs 39.8±4.8. VE/VCO2 slope elevated in HV subgroup. Hypocapnia persisted/worsened on Day 2 in ME/CFS (controls habituated).
- **Mechanism (E1):** hypocapnia → cerebral vasoconstriction → hypoperfusion (Novak 2018, *PLoS One* 13:e0204419); links breathing pattern to orthostatic/cognitive symptoms.
- **Evidence level:** **E3** (controlled, n moderate).
- **Implementation:** Add a respiratory submodule: elevated VE/VCO2 and low PetCO2 surrogate (higher breathing rate, lower SpO2-normal pattern) in ~30% of personas, amplified during PEM.

---

## SECTION 4 — PEM TIME COURSE (the core multi-day dynamic)

### CLAIM 4.1 — PEM onset is delayed (typically 12–48 h), peaks at 24–48 h, and lasts days
- **Claim:** PEM characteristically does NOT begin during/immediately after exertion; onset delayed 12–48 h, peak ~24–48 h, duration days to weeks.
- **Magnitude/distribution:**
  - Chu et al. 2018 (n=150 ME/CFS; *Front Neurol* 9:112, PMC5983853): 40% report PEM beginning <24 h consistently; **11% report consistent ≥24 h delay**; **84% endure PEM ≥24 h**; 20% last 1–2 days; **25% >3 days**; 60% report ≥1 inflammatory/flu-like symptom. Exertion triggers more symptoms than emotional stress (7±2.8 vs 5±3.3 symptoms, p<.001).
  - Stussman et al. 2020 (NIH intramural focus groups, n=43): daily-activity PEM onset 12–48 h, **peak 48 h, duration 2–7 days**; CPET-induced PEM: **immediate onset, peak 24 h, duration ≥72 h** (faster and longer than daily-life PEM). Follow-up NIH study (2025) confirmed three core symptom clusters: exhaustion, cognitive, neuromuscular.
  - VanNess 2010 (n=25 vs 23, 7-d follow-up after maximal CPET): all controls recovered ≤2 days; only 1/25 ME/CFS recovered by day 2; **60% took >5 days**; worst at 24–48 h.
  - Lapp 1997 (n=31, 12-d follow-up): mean relapse 8.82 days; 22% still in relapse at day 12.
- **Timescale:** onset delay 0–48 h (distribution, mode ~12–24 h); peak 24–48 h; recovery 1 day to >1 year (right-skewed).
- **Evidence level:** **E4** (multiple independent cohorts; consistent qualitative structure) — but mostly symptom-report, not physiological telemetry.
- **Limitations:** retrospective self-report dominates; recall bias; "onset" conflated with orthostatic symptom flare in some reports (Bateman Horne critique).
- **Implementation:** Model PEM kernel with: delay parameter d ~ Gamma(mode 18 h, range 0–48 h); rise to peak at d+12–24 h; exponential/plateau decay with τ ~2–5 days, right tail to 60+ days in ~5–10% of episodes; amplitude proportional to exertion dose above the individual's anaerobic/VT threshold.

### CLAIM 4.2 — Quantified recovery: ~2 weeks after 2-day CPET (vs 2 days in controls)
- **Claim:** After a standardized maximal 2-day CPET trigger, ME/CFS symptom severity follows a measurable multi-day trajectory with mean recovery 12.7 days.
- **Magnitude (Moore et al. 2023; n=80 ME/CFS vs 64 sedentary controls; SSS symptom scale tracked 10+ days):** recovery time **12.7±1.2 d (ME/CFS) vs 2.1±0.2 d (controls)**, p<.0001; patient range **1–64 days** (one unrecovered at 1 year; <10% >3 weeks). Pharmacokinetic one-compartment fit: peak symptoms **+1.5 units above pre-CPET baseline occurring ~24 h after CPET-2**, decay ~0.10±0.02 units/day (return to baseline up to ~3 weeks).
- **Evidence level:** **E3/E4** (controlled, quantitative, n=144; single study — needs replication).
- **Source:** Moore GE et al. 2023, *Medicina* 59(3):571, DOI 10.3390/medicina59030571, PMID 36984572.
- **Implementation:** This is the single best quantitative trigger-response-recovery template for OCPE: peak at +24 h post-second-exertion, amplitude ~+35–40% over baseline symptom load, decay 0.1 units/day, tail to 64 d. Also: pre-test anticipation reduced symptoms (baseline 5.70 vs pre-CPET 4.02) — model a "stress/anticipation" component.
- **Validation:** Synthetic symptom-trajectory distribution should match median ~12 d, IQR roughly 5–21 d, 5–10% beyond 3 weeks.

### CLAIM 4.3 — Fatigue response to acute exercise is exaggerated and delayed (meta-analysis)
- **Claim:** Exercise elevates fatigue in ME/CFS more than controls, with the largest group difference **≥4 h post-exercise** (up to 96 h).
- **Magnitude:** Loy et al. 2016 meta-analysis (*Fatigue*, PMC5026555): significant group difference at ≥4 h post-exercise; effects persisted days. Barhorst 2022 meta-analysis (15 studies, 306 ME/CFS): small-to-moderate increase in pain post-exercise. Davenport 2023: ~60–65% of ME/CFS report increased fatigue 1 week post-exercise.
- **Evidence level:** **E5** (meta-analysis) for symptom-level fatigue; heterogeneity high.
- **Implementation:** Wearable-relevant corollary: subjective crash builds over hours — align synthetic symptom scores with the PEM kernel of Claim 4.1, not instantaneous with exertion.

### CLAIM 4.4 — Physiological (molecular) trajectories over 0.5–72+ h post-exertion exist but are not yet wearable-visible
- **Claim:** Post-exertion gene-expression, epigenetic, and cytokine changes track the PEM window (0.5 h → 48–72 h).
- **Magnitude:**
  - Light et al. 2009 (n=19 vs 16; *J Pain* 10:1099–112, PMID 19647494, DOI 10.1016/j.jpain.2009.06.003): after 25 min moderate exercise (70% predicted max HR), CFS showed greater increases in mRNA for metabolite-sensing receptors (ASIC3, P2X4, P2X5), adrenergic (α2A, β1, β2), COMT, IL-10, TLR4, sustained **0.5–48 h**; controls no change.
  - Light et al. 2012 (n=48 CFS vs 49 controls; *J Intern Med* 271:64–81, PMID 21615807): **71% of patients** showed sustained 48-h post-exercise upregulation; **29% (orthostatic-intolerance-enriched subgroup)** showed α2A *decrease* only — molecular heterogeneity mirroring clinical subtypes.
  - Meyer/Cook 2013 (*Fatigue* 1): sustained upregulation of NR3C1 (glucocorticoid receptor) and α2A for **72 h** post-maximal exercise, correlated with pain/fatigue/confusion.
  - Milivojevic/Chetsang et al. 2025 (PMC12429597): dynamic DNA-methylation clusters at 0/24/48 h post-2-day-CPET (98% ME/CFS-specific; endothelial/inflammation/immune pathways) — n=5, pilot.
  - Cytokines: IL-6/IL-1β increases larger at 8 h post-exercise in ME/CFS (Sandler 2016 context); Moneghetti 2018 (Stanford): differential cytokine responses during submaximal exercise.
- **Evidence level:** **E3** (controlled experimental) with partial E4 (Light replicated in larger sample; not yet independently replicated by other labs at scale).
- **Limitations:** blood-based, not wearable; small n; MS patients show partial overlap (fatigue but not metabolite-receptor signature).
- **Implementation:** These justify a *mechanistic latent state* (inflammatory/metabolite-sensing activation) with 0.5–48 h evolution, but wearable signals must be inferred downstream (HR, HRV, temperature, activity suppression) — do not model gene expression directly.

### CLAIM 4.5 — Autonomic physiological changes during PEM: reduced parasympathetic reactivation and delayed recovery
- **Claim:** During/after exertion, ME/CFS shows blunted autonomic withdrawal-recovery dynamics lasting hours; HRV stays depressed post-exercise.
- **Magnitude:**
  - Van Oosterwijck et al. 2021 (n=40): reduced parasympathetic **reactivation** after exercise; HR still significantly elevated 10 min post-exercise vs controls; diminished sympathetic and parasympathetic modulation during exercise itself (chronotropic blunting).
  - VanNess 2023 (n=2, serial CPET, continuous HRV): pilot case data only.
  - Long COVID wearable analogue (n=127 LC vs 21 controls; continuous wearable HRV; *Sports Med* 2026, Springer): HRV (RMSSD) remained significantly lower **up to 24 h** after exercise at/above VT1 in patients, whereas controls recovered within 3–6 h; nighttime HRV reduced dose-dependently with exercise intensity/duration; authors propose VT1 as practical PEM threshold. (Direct ME/CFS multi-day wearable HRV equivalent does NOT yet exist — nearest proxy.)
- **Timescale:** hours (HRV recovery 3–6 h in controls; >9–13 h, up to 24 h in patients).
- **Evidence level:** **E3** (ME/CFS lab studies) + **E2** (long COVID wearable field study, extrapolation).
- **Contradictory:** Nelson 2019 meta found no difference in HR recovery (HRR, 2 studies, high heterogeneity) — recovery-HR findings conflict.
- **Implementation:** During PEM episode: reduce RMSSD/HF by ~15–30% relative to persona baseline for 24–72 h; slow the post-exercise HR recovery time constant (~2–3× normal); delay nocturnal HRV rebound by 6–12 h after trigger days.

### CLAIM 4.6 — What changes during PEM that wearables can see: the current (thin) evidence inventory
- **Claim:** Direct multi-day wearable observation of PEM episodes in ME/CFS is sparse; the defensible wearable-observable PEM signature set is:
  1. **Activity collapse:** step count suppression for 1–7+ days after overexertion (boom–bust pattern; day-to-day variation 47%, range 25–79% — Rekeland 2022; severity-graded means, Healthcare 2020). [E4]
  2. **Elevated resting/nocturnal HR** during symptom exacerbation (clinical reports + autonomic studies; quantitative multi-day PEM HR data lacking). [E2, weak]
  3. **Depressed HRV (RMSSD/HF)** for 24–72 h post-trigger (lab E3 + long COVID wearable E2 proxy). [E3/E2]
  4. **Sleep disruption / longer time in bed** during crash (meta-analysis baseline differences + qualitative PEM reports). [E2]
  5. **Orthostatic HR response exaggerated** during PEM (patients report worsened OI; van Campen post-exertional data suggestive). [E2]
  6. **Skin temperature:** anecdotal low-grade fever/flu-like reports during PEM (60% report inflammatory symptoms, Chu 2018); no controlled wearable temperature trajectory study found. **[E0/E1 — do not over-model]**
- **Evidence level:** mixed; explicitly flag the gap: **no published study has yet quantified multi-signal 24–72 h wearable trajectories through induced PEM in ME/CFS** (the key target niche for OCPE synthetic data).

---

## SECTION 5 — AUTONOMIC DYSFUNCTION (synthesis)

### CLAIM 5.1 — Meta-analytic autonomic profile: sympathetic up / vagal down, small effects
- **Claim:** The pooled autonomic signature is: RHR +4 bpm, RMSSD −0.37 SD, HF −0.34 SD, LF +0.39 SD, HRtilt +0.92 SD, orthostatic ΔHR +0.50 SD, HRmax −5.8 to −16.6 bpm, daily-average HR +0.11 SD (NS).
- **Evidence level:** **E5** (Nelson 2019; 64 articles).
- **Contradictory:** effect sizes small, heterogeneity I² 62–96% for several parameters; some reviews (Tak 2009) found daytime differences non-significant; HRVtilt shows no group difference (n=2 studies). No single HR parameter is diagnostic.
- **Implementation:** Use as the baseline autonomic offset vector (severity-scaled ~0.5× for mild, 1× moderate, 1.5–2× severe as a modeling prior — severe data largely absent from meta-analysis).

### CLAIM 5.2 — Nocturnal autonomic dysfunction: conflicting direction for HR, consistent HRV suppression in deep sleep
- **Claim:** Nocturnal HRV is reduced during N2/SWS (loss of normal parasympathetic rise into slow-wave sleep); nocturnal HR findings conflict (Boneva 2007: higher HR + lower HRV during sleep; Frith 2018/PMC5786834: LOWER HR but elevated LF and LF/HF during sleep in CFS vs tired controls, with failure of HF to increase from N2→N3).
- **Evidence level:** **E2/E3** (two controlled PSG+HRV studies, opposing HR direction; HRV-stage-dysregulation consistent).
- **Source:** Boneva 2007, DOI 10.1016/j.autneu.2007.08.002; Frith et al. 2018 (PMC5786834); Cvejic et al. (reduced HRV in N2 & SWS correlates with unrefreshing sleep and next-day wellbeing); Togo & Natelson 2013, DOI 10.1016/j.autneu.2013.02.015.
- **Implementation:** Model nocturnal HRV with blunted N2→SWS rise; choose nocturnal HR direction per-persona from a mixture (elevated-HR phenotype ~60%, neutral/lower ~40%) — reflecting the literature conflict rather than picking one.

---

## SECTION 6 — CARDIOVASCULAR / RESPIRATORY / METABOLIC

### CLAIM 6.1 — Hypometabolic plasma signature (metabolomics) — replicated direction, unreplicated panels
- **Claim:** Plasma metabolomics consistently show a hypometabolic pattern (reduced lipids, amino acids, TCA/purine metabolites), but specific diagnostic panels differ across labs.
- **Magnitude:** Naviaux 2016 (n=45 vs 39; PNAS 113:E5472–80, DOI 10.1073/pnas.1607571113, PMID 27573827): targeted 612 metabolites/63 pathways; **20 pathways abnormal; 80% of diagnostic metabolites decreased**; sphingolipid (top impact, 49% M/35% F), phospholipid, purine, cholesterol, BCAA, riboflavin, peroxisomal, mitochondrial pathways; AUROC 94% (M, 8 metabolites) / 96% (F, 13 metabolites) — *in-sample, not externally validated*.
- **Partial replications:** Armstrong 2012 NMR (Clin Chim Acta 413:1525–31, PMID 22728138) — amino acid disturbances; Fluge 2016 (JCI Insight 1:e89376) — impaired PDH function pattern; Germain 2017/2018 — reduced glucose/taurine/ATP/ADP, bile acids, glycerophospholipids; Nagy-Szakal 2018 (Sci Rep 8:10056, PMID 29968805); Hoel 2021 (JCI Insight 6(16), PMID 34423789) — metabolic phenotype map.
- **Contradictory:** critiques (Roerink 2017; Vogt 2016 — PNAS correspondence) on statistics/confounders; pathway overlaps between studies partial at best; no consensus diagnostic metabolite panel survives cross-lab replication. Direction (hypometabolism) replicated (E4); specific panels not (E1/E2).
- **Evidence level:** **E1/E2** overall (E4 for "direction of effect" only).
- **Implementation:** Use only as mechanistic prior for PEM amplitude/recovery modeling (e.g., slower recovery τ); no direct wearable signal.

### CLAIM 6.2 — Lactate/ventilatory abnormalities
- **Claim:** Earlier VT, elevated lactate at VT on Day-2 CPET (Lien 2019), elevated ventricular (brain) lactate at rest (Natelson 2017; also in fibromyalgia).
- **Evidence level:** **E2/E3**; **Contradictory:** Vermeulen 2010 found normal oxidative phosphorylation in PBMCs and normal CK — argues against primary muscle mitochondrial defect; Jones 2012: impaired recovery from acidosis on repeat exercise. Mitochondrial literature overall mixed (systematic review PMC7392668).
- **Implementation:** During PEM, shift the modeled lactate-equivalent/ventilatory drive upward at a given submaximal intensity (~earlier "anaerobic" signature at lower HR/work rate).

### CLAIM 6.3 — Resting cardiac output/stroke volume and blood volume
- **Claim:** Resting CO/SV largely normal; abnormalities emerge under orthostatic/exercise stress (CI −26±7% during tilt in severe; lower O2 pulse and narrowed pulse pressure at peak exercise; reports of low blood volume).
- **Evidence level:** **E2/E3**; single-lab dominance (van Campen group) for tilt CI; blood-volume findings older (Streeten 2000; small n).
- **Implementation:** Keep resting CO/SV at control distributions; perturb only under orthostatic/exertion states and during PEM.

---

## SECTION 7 — SLEEP

### CLAIM 7.1 — Objective sleep architecture is altered (meta-analysis), modestly
- **Claim:** Adults with ME/CFS show longer time in bed, longer sleep-onset latency, more wake-after-sleep-onset, lower sleep efficiency, less stage 2, more stage 3, longer REM latency; total sleep time roughly normal.
- **Magnitude (meta-analysis, 20 adult studies n=426 vs 375; 4 adolescent studies n=242 vs 235; Sleep Med Rev 2023, PMC10281648):** time in bed +26.6 min (PSG NS; actigraphy +77.2 min); sleep latency +7.2 min; TST −0.5 min (NS; actigraphy +46 min); reduced SE; REM latency longer. Adolescents: longer TIB (+72 min) and TST (+54.6 min), reduced SE.
- **Evidence level:** **E5**; **Limitations:** scoring method (R&K vs AASM) and adaptation night change some findings; high heterogeneity; actigraphy vs PSG disagree on TST/TIB.
- **Unrefreshing sleep** (up to 95% report it) is not explained by macro-architecture — best correlate is nocturnal autonomic dysregulation (Claim 5.2). [E1/E2]
- **Implementation:** Baseline sleep model: SE −3–6%, SOL +7–10 min, WASO up, slightly increased N3 fraction, TST normal; during PEM episodes: TIB +30–90 min, fragmentation ↑ for 1–7 nights.

### CLAIM 7.2 — Circadian findings are weak/inconsistent
- **Claim:** Small studies suggest delayed sleep phase/later rise time (actigraphy adolescent study: later rise time), but no replicated quantitative circadian-marker (DLMO/core temperature) meta-analytic finding.
- **Evidence level:** **E2** (small, inconsistent). **Recommendation:** model mild phase delay (+30–60 min) as persona-level option, not a core feature.

---

## SECTION 8 — ACTUAL WEARABLE / ACTIGRAPHY STUDIES IN ME/CFS

### CLAIM 8.1 — Step counts as severity-scaled objective marker
- **Data:** See Claims 1.2 & 2.6: mild 5566–8235, moderate ~5000–5200, severe ~1998–2031 steps/day; cohort mean 5701±2670; day-to-day variability 47% (25–79%).
- **Devices:** Actometer (Stichting CardioZorg), Fitbit Charge 3, SenseWear (Fitbit reads higher than SenseWear — device bias matters).
- **Evidence level:** **E4**.
- **Implementation:** Core OCPE output variable. Distributions: lognormal-ish with severity means above; CV ~0.3–0.5 within-person day-to-day, autocorrelated via boom–bust PEM kernel.

### CLAIM 8.2 — Six-month Fitbit monitoring: feasible; resting HR stable long-term
- **Data (Rekeland et al. 2022, PLoS One, DOI 10.1371/journal.pone.0274472; n=27, 6 months):** steps/day 4341→4781 between 3-month periods (p=.022); 4-week max-min swings: milder patients ~958 steps vs ~479 in high-symptom patients; steps correlate with SF-36 PF/social function and DSQ-SF; **resting HR stable over 6 months**.
- **Evidence level:** **E2** (longitudinal, small n).
- **Implementation:** Baseline RHR = stable trait; day-to-day RHR deviations (~±3–5 bpm) should be episode-linked (PEM kernel), not random drift. Boom–bust amplitude larger in milder patients (they have capacity to overexert) — counterintuitive but evidence-supported.

### CLAIM 8.3 — HR-monitor pacing thresholds (practice-based, not trial-validated)
- **Claim:** Patient-facing practice keeps HR below estimated anaerobic threshold (~RHR+15 bpm as conservative proxy) because >85% of ME/CFS patients show chronotropic incompetence making age-predicted formulas unsafe (Workwell Foundation guidance).
- **Evidence level:** **E1/E2** (rationale from CPET + chronotropic-incompetence literature; no RCT).
- **Implementation:** Useful as the *behavioral rule* driving synthetic activity patterns: activity bouts cluster below ~RHR+15; PEM triggers when HR time-above-threshold accumulates.

### CLAIM 8.4 — Multi-day wearable HRV during PEM: direct ME/CFS evidence gap; long COVID proxy
- See Claim 4.5. In long COVID (n=127, continuous HRV wearables): HRV lower during daily activities and sleep (p<.027); HRV depressed 24 h after ≥VT1 exercise (p=.010); nighttime HRV falls with exercise intensity/duration (p=.018); controls recover in 3–6 h. **No equivalent published multi-day wearable PEM dataset exists for classic ME/CFS** — OCPE synthetic data should be built to be *consistent with* lab HRV dynamics (E3) + this LC proxy, and flagged as extrapolation.

### CLAIM 8.5 — PACE trial context: self-reported improvement ≠ objective activity change
- **Claim:** The PACE trial (n=641; Lancet 2011, PMID 21334066) reported CBT/GET improved self-reported fatigue/function, but reanalysis (Wilshire et al. 2018, BMC Psychol 6:6, PMID 29562932) using the original protocol definitions found recovery rates ~7–8% across ALL arms (no significant differences), and objective activity (accelerometer) outcomes were not published as improved / showed no objective gain.
- **Evidence level:** **E4** (reanalysis of RCT data).
- **Relevance to OCPE:** Symptoms and objective activity can dissociate; synthetic datasets must not assume symptom improvement implies activity normalization. GET as a "dose escalator" in models should be treated as potentially harmful (surveys report harm in ~50% of patients undergoing GET — patient-survey evidence, E2, contested).

---

## SECTION 9 — HETEROGENEITY / SUBTYPING

### CLAIM 9.1 — Severity gradation has objective physiological correlates
- Steps/day, %predicted VO2@VT and peak VO2 all graded (Claim 1.2). Severe patients additionally: abnormal CBF on 20° tilt and even sitting (−27%, −24.5%); persistent post-tilt CBF abnormalities at 10-min recovery (E3, van Campen series).
- **Evidence level:** **E4** (steps/VO2), **E3** (CBF severe).
- **Implementation:** Severity scales: PEM kernel amplitude ↑, threshold (exertion dose to trigger) ↓, recovery τ ↑ with severity. Severe persona: ~2000 steps/d, orthostatic response triggered by sitting.

### CLAIM 9.2 — Comorbid overlap subtypes
- **POTS:** ~28% of adult ME/CFS in van Campen cohort; delayed OH ~14%; pediatric OI >96% (IOM synthesis). [E3/E2]
- **Hypermobility/EDS:** ~50–60% of pediatric ME/CFS meet Beighton ≥4 (Roma 2019; Barron 2002). [E2]
- **Fibromyalgia overlap:** Light 2012 — FM-comorbid subgroup drives pain-gene signature; FM-only has distinct baseline signature (P2X4/TRPV1/IL10 ↑). [E3]
- **Orthostatic-intolerance subgroup:** Light 2012 — α2A-decrease molecular subgroup enriched for OI history (29% of cohort). [E3]
- **Post-infectious onset:** majority (est. 60–70%) report infectious onset; Walitt 2024 NIH deep phenotyping (n=17 PI-ME/CFS; Nat Commun, DOI 10.1038/s41467-024-45107-3, PMID 38383456): altered effort preference (normal max grip but failed sustained submaximal grip; reduced TPJ activation), immune profile (increased naïve/decreased switched-memory B cells). Small n; interpretation contested by patient-scientist community. [E3, contested]
- **Implementation:** Implement comorbidity flags (POTS 25–30%, FM ~30–40%, hypermobility ~30–50% depending on age) that modulate orthostatic ΔHR, pain sensitivity and PEM kernel amplitude.

### CLAIM 9.3 — Disease-duration effects
- Duration itself not strongly linked to steps/VO2 in the severity-validation cohort (no baseline differences by duration); van Campen 2018: abnormal tilt cardiac-index changes unrelated to VO2peak (deconditioning) — supports disease-intrinsic (not merely deconditioning) autonomic/hemodynamic abnormality. [E2/E3]
- Sex: metabolomic signatures sex-specific (Naviaux 2016); most cohorts 75–85% female — model sex as effect modifier.

---

## SECTION 10 — NULL / CONTRADICTORY FINDINGS REGISTER (must-read for modeling)

1. **2-day CPET null:** Nelson 2026 (n=58 vs 25) — no day-2 change; Davenport 2020 — comparable day-2 decline in both groups; Vermeulen 2010 — no VT change. The day-2 signature is replicated but **not universal**; ~40% of ME/CFS cohorts may not show clean separation, and controls can also decline. (Section 3.2)
2. **HRV contradictions:** Tak 2009 (daytime resting ANS NS); HRVtilt no difference; nocturnal HR direction conflict (Boneva vs Frith); HRR no meta-analytic difference. Effects are small (|SMD| ~0.3–0.4).
3. **VO2max:** strict-effort-criterion studies found no VO2max difference; activity-matched subsets erase the single-day difference (MCAM matched pairs ES 0.02) — deconditioning confound unresolved.
4. **Daily-average HR:** no difference (E2).
5. **Metabolomics:** direction replicated, specific panels not; PNAS critiques re: multiple-testing/confounding.
6. **Mitochondrial function:** Vermeulen 2010 normal PBMC oxidative phosphorylation; muscle biopsy studies mixed (<50% show pH-handling abnormalities in some series).
7. **PACE/GET:** claimed objective recovery not supported on reanalysis (Wilshire 2018); context for why patient-reported outcomes and wearable outcomes must be modeled as dissociable.
8. **Sleep TST:** no difference overall — "more sleep" is a TIB/actigraphy artifact mix; do not model ME/CFS as hypersomnia.
9. **Cytokines:** Hornig 2015 found plasma cytokine signatures in early (<3 y) but not later disease; IL-6 exercise responses inconsistent across studies.

---

## SECTION 11 — IMPLEMENTATION RECOMMENDATIONS FOR OCPE (PEM as a delayed multi-day perturbation)

**A. Architecture: two-timescale model.**
- **Baseline layer (chronic, trait):** severity-scaled offsets — RHR +3–5 bpm; RMSSD/HF −0.3 SD; steps/day by severity tertile (8000/5000/2000); orthostatic ΔHR +0.5–0.9 SD; SE −3–6%, SOL +7–10 min; chronotropic ceiling −6 to −17 bpm.
- **PEM layer (episodic, dynamic):** PEM is a **latent dynamical state**, not a scalar:
  - **Trigger:** accumulated exertion dose above persona threshold (time with HR > VT-proxy ≈ RHR+15 bpm; also cognitive/emotional dose as separate input channel with ~70% potency).
  - **Delay kernel:** onset latency Gamma-distributed, mode ~12–24 h, support 0–48 h (11% of patients consistently ≥24 h).
  - **Response (24–72 h plateau):** peak at 24–48 h post-trigger. Multi-signal deltas at peak (severity-scaled):
    - steps: −40–70% vs persona baseline for 1–7 days (crash days; mild personas show largest absolute swings)
    - RHR: +3–8 bpm (episode-linked, reverting)
    - nocturnal HRV (RMSSD): −15–30%; blunted N2→SWS HRV rise
    - orthostatic ΔHR: amplified (+10–20 bpm additional on standing)
    - "VT-equivalent" sustainable intensity: −10–20% (models 2-day CPET day-2 signature)
    - sleep: TIB +30–90 min, fragmentation ↑
    - skin temperature: optional small +0.1–0.3 °C nocturnal rise in a flu-like subset (E0 — keep as toggleable flag, NOT default)
  - **Recovery:** exponential decay, τ ≈ 2–5 days; distribution: median ~12 d symptom recovery for a maximal-exercise-class trigger (Moore 2023), 5–10% tail >21 d, up to 60+ d. Incomplete recovery between episodes → baseline creep (modeled as slow state variable; patient-reported "rolling PEM").
- **Mixture modeling:** only ~50–65% of individual exertion episodes should produce a clear detectable physiological signature (mirrors 2-day CPET sensitivity ~33–60% and 60–65% 1-week fatigue prevalence); the rest produce sub-threshold or symptom-only episodes.

**B. Calibration targets (for fitting/validation):**
| Signal | Baseline ME/CFS vs control | During PEM (peak, 24–48 h) | Source level |
|---|---|---|---|
| Steps/day | 2000–8200 (severity) | −40–70% persona-relative, 1–7 d | E4 |
| RHR | +4.1 bpm (E5) | +3–8 bpm episode (E2, weak) | E5/E2 |
| RMSSD/HF | −0.34/−0.37 SD (E5) | −15–30% 24–72 h (E3+E2-proxy) | E3 |
| Orthostatic ΔHR | +0.50–0.86 SD (E5) | amplified (E2) | E5/E2 |
| HRmax | −5.8 to −16.6 bpm (E5) | VT-intensity −10–20% (E4/E5) | E5 |
| Sleep | SE −3–6%, SOL +7 min (E5) | TIB +30–90 min (E2) | E5/E2 |
| CBF tilt | −26% vs −7% (E3/E4) | worsened (E2) | E3 |

**C. Validation strategy:**
1. **Distributional:** cohort step-count tertiles match Healthcare 2020 / PLoS One 2022 means±SD; RHR offset +4±1.3 bpm; HRV SMDs within Nelson 2019 CIs.
2. **Dynamic:** simulate a 2-day CPET challenge in-silico → require reproduced Lim 2020 ΔWork@VT (−14.6 W patients vs +6.5 W controls) and Keller 2024 peak declines (−5.3% VO2) within CI, in ~50–60% of personas (matching sensitivity estimates).
3. **Trajectory:** synthetic PEM symptom/load trajectories should match Moore 2023 recovery distribution (median ~12.7 d, range 1–64 d) and Chu 2018 onset-delay/duration frequencies.
4. **Discrimination sanity-check:** a classifier trained on synthetic ME/CFS vs synthetic healthy should NOT achieve >~0.7–0.8 AUROC on any single resting wearable feature (literature effects are small with large overlap) — if it does, the synthetic effect sizes are too large.
5. **Falsifiability flags:** keep literature-null arms (Section 10) as alternative parameter draws; document which synthetic runs instantiate which evidence branch.

**D. Explicit gaps (do not fabricate):**
- No published multi-day, multi-signal wearable PEM dataset in classic ME/CFS (the exact niche OCPE fills).
- No quantitative wearable temperature data during PEM.
- Severe/bedbound patients nearly absent from all controlled physiology studies — severe personas are extrapolations (use steps and CBF-seated data as anchors).
- No validated dose-response model of exertion→PEM probability exists (only VT1-threshold rationale); the trigger function is a modeling hypothesis informed by E3/E2 evidence, not an established law.

---

## PRIMARY SOURCE LIST (verified identifiers only)
- IOM 2015. *Beyond ME/CFS: Redefining an Illness*. DOI 10.17226/19012. [E5]
- Nelson MJ et al. 2019. Altered cardiac autonomic regulation meta-analysis. *J Transl Med* 17:268. PMC6824690. [E5]
- Nelson MJ et al. 2019. Diagnostic sensitivity of 2-day CPET. *J Transl Med* 17:80. PMC6417168. [E3]
- Lim E-J et al. 2020. 2-day CPET meta-analysis. *J Clin Med* 9:4040. DOI 10.3390/jcm9124040. [E5]
- Franklin JD et al. 2019. VO2peak meta-analysis. *Int J Sports Med* 40:77–87. PMID 30557887. [E5]
- Franklin JD, Graham M. 2022. Repeated maximal exercise meta-analysis. *Fatigue* 10(3):119–135. [E5]
- Keller BA et al. 2014. *J Transl Med* 12:104. DOI 10.1186/1479-5876-12-104. [E3]
- Keller B et al. 2024. *J Transl Med* 22. DOI 10.1186/s12967-024-05410-5. [E3/E4]
- Snell CR et al. 2013. *Phys Ther* 93:1484–1492. [E3]
- VanNess JM et al. 2007. *J Chronic Fatigue Syndr* 14:77–85. [E3]
- Vermeulen RCW et al. 2010. *J Transl Med* 8:93. DOI 10.1186/1479-5876-8-93. [E3, partial null]
- Hodges LD et al. 2018. *Clin Physiol Funct Imaging* 38:639–644. [E3]
- Nelson M et al. 2026. CPET null replication. *Front Physiol*. DOI 10.3389/fphys.2026.1816082. [E3, null]
- Joseph P et al. 2021. Invasive CPET. *Chest* 160(2):642–651. DOI 10.1016/j.chest.2021.01.082. [E3]
- Joseph P et al. 2022. Pyridostigmine RCT. *Chest* 162(5):1116–1126. DOI 10.1016/j.chest.2022.04.146. [E3]
- Moore GE et al. 2023. Recovery from exercise. *Medicina* 59(3):571. DOI 10.3390/medicina59030571. PMID 36984572. [E3]
- Chu L et al. 2018. Deconstructing PEM. *Front Neurol* 9:112. PMC5983853. [E2]
- Stussman B et al. 2020. NIH intramural PEM focus groups (n=43) + NIH 2025 follow-up. [E2]
- Loy BD et al. 2016. Acute exercise fatigue meta-analysis. *Fatigue*. PMC5026555. [E5]
- Barhorst EE et al. 2022. Exercise→pain meta-analysis (15 studies). [E5]
- Light AR et al. 2009. *J Pain* 10:1099–112. DOI 10.1016/j.jpain.2009.06.003. PMID 19647494. [E3]
- Light AR et al. 2012. *J Intern Med* 271:64–81. DOI 10.1111/j.1365-2796.2011.02405.x. PMID 21615807. [E3]
- Meyer JD/Cook DB et al. 2013. *Fatigue* 1(1–2). [E3]
- Milivojevic M et al. 2025. PEM DNA-methylation. PMC12429597. [E3, pilot n=5]
- Van Oosterwijck J et al. 2021. Reduced parasympathetic reactivation. *Psychosom Med*. [E3]
- van Campen CMC et al. 2020a. CBF on tilt. *Clin Neurophysiol Pract* 5:50–58. DOI 10.1016/j.cnp.2020.01.003. PMID 32140630. [E3]
- van Campen CMC et al. 2020b. Sitting CBF in severe ME/CFS. *Healthcare* 8(4):394. [E3]
- van Campen CMC et al. 2021. Post-tilt CBF persistence. PMC8505270. [E3]
- van Campen CMC et al. 2021. 2-day CPET ME/CFS vs idiopathic chronic fatigue. *J Transl Med* 19. DOI 10.1186/s12967-021-02819-0. [E3]
- Novak P. 2018. Hypocapnic cerebral hypoperfusion. *PLoS One* 13(9):e0204419. DOI 10.1371/journal.pone.0204419. [E2]
- Hyperventilation 2-day CPET cohort (2025). PMC12640868. [E3]
- Naviaux RK et al. 2016. *PNAS* 113:E5472–80. DOI 10.1073/pnas.1607571113. PMID 27573827; critiques Roerink 2017 PMID 28126718, Vogt 2016 PMID 27810961. [E1/E2]
- Armstrong CW et al. 2012. *Clin Chim Acta* 413:1525–31. DOI 10.1016/j.cca.2012.06.022. PMID 22728138. [E2]
- Fluge Ø et al. 2016. PDH impairment. *JCI Insight* 1:e89376. [E2]
- Hoel F et al. 2021. *JCI Insight* 6(16). PMID 34423789. [E2]
- Nagy-Szakal D et al. 2018. *Sci Rep* 8:10056. PMID 29968805. [E2]
- Walitt B et al. 2024. NIH deep phenotyping. *Nat Commun*. DOI 10.1038/s41467-024-45107-3. PMID 38383456. [E3, contested interpretation]
- Objective sleep meta-analysis 2023. *Sleep Med Rev*. PMC10281648. [E5]
- Boneva RS et al. 2007. *Auton Neurosci* 137:94–101. DOI 10.1016/j.autneu.2007.08.002. [E3]
- Frith J et al. 2018. Nocturnal ANS vs tired controls. PMC5786834. [E3, contradictory HR direction]
- Togo F, Natelson BH. 2013. *Auton Neurosci* 176:85–90. DOI 10.1016/j.autneu.2013.02.015. [E3]
- Severity validation (ICC grading, n=289). *Healthcare* 2020;8(3):273. PMC7551321. [E2/E4]
- Rekeland IG et al. 2022. Fitbit 6-month activity monitoring. *PLoS One* 17:e0274472. DOI 10.1371/journal.pone.0274472. [E2]
- Long COVID wearable HRV study (n=127). *Sports Med* 2026. Springer DOI 10.1007/s40279-026-02487-4. [E2, LC proxy]
- Wilshire CE et al. 2018. PACE reanalysis. *BMC Psychol* 6:6. PMID 29562932. [E4]
- White PD et al. 2011. PACE trial. *Lancet* 377:823–836. PMID 21334066. [E3, contested]
- Mateo LJ et al. 2020. Post-exertional symptoms distinguish ME/CFS. *Work* 66:265–275. DOI 10.3233/WOR-203168. [E2]

*Compiled for OCPE. Evidence levels reflect replication status as of literature available to 2025-2026. Where findings conflict, both branches are documented rather than resolved by fiat.*
