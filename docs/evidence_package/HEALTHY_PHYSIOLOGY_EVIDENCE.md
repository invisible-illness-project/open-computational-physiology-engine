# OCPE — Healthy Reference Physiological Model: Evidence Base

**Purpose:** Evidence foundation for the healthy reference model of the Open Computational Physiology Engine (OCPE). Disease models will be implemented as perturbations of these reference distributions and dynamic responses.

**Evidence scale:** E0 = hypothesis/assumption; E1 = mechanistic/theoretical; E2 = observational human; E3 = controlled human experimental; E4 = replicated quantitative; E5 = systematic review/meta-analysis/consensus guideline.

**Conventions:** Values are for healthy adults unless stated. SD = standard deviation, IQR = interquartile range, CI = confidence interval. Timescales flagged as seconds (s), minutes (min), hours (h), days (d). Citations restricted to DOIs/PMIDs/URLs actually retrieved during this review; commercial/blog sources were used only when flagged as low-authority and are marked accordingly.

---

## 1. Resting Distributions (supine/seated, awake, quiet rest)

### 1.1 Heart rate (HR)

- **Claim:** Resting HR in healthy adults is age-, sex-, and fitness-dependent; population mean is NOT 60–100 bpm — the classic 60–100 range is a clinical convention, while the actual central tendency of healthy free-living adults is lower.
  - **Magnitude/distribution:** Health eHeart study (n = 25,408 self-reported healthy individuals, 1,103,570 PPG measurements): mean resting HR decreased from 81.6 ± 14.0 bpm (age 18–20) to 74.2 ± 12.7 bpm (age 71–80); females +4.4 bpm vs males; 95th percentile uniformly <100 bpm after age 45 (~95 bpm at 61 y). Timescale: stable trait (days), with beat-to-beat and diurnal superimposed variation (s–h).
  - **Population:** US adults, 18–80 y, 50.2% female, wearable PPG (real-world, not laboratory). E2 (very large n).
  - **Source:** Avram et al., "Real-world heart rate norms in the Health eHeart study," PMC5624990… (PMC6592896), https://pmc.ncbi.nlm.nih.gov/articles/PMC6592896/
- **Claim:** Endurance training lowers resting HR by ~8–12 bpm at the group level; elite athletes commonly 40–55 bpm.
  - **Magnitude:** Master athletes (n = 50) vs sedentary controls (n = 50, men, ~49 y): resting HR 62.8 ± 6.7 vs 74.0 ± 10.4 bpm (p < 0.001). Physically active vs inactive students (n = 75/75): 68.2 ± 5.4 vs 75.6 ± 6.2 bpm. Daily-average HR in athletes vs non-athletes: 68 vs 76 bpm (n = 109 athletes, 38 non-athletes, La Gerche group, JACC 2025).
  - **E2/E4 (replicated across cohorts).** Sources: Choi et al., Clin Physiol Funct Imaging 2015 (doi:10.1111/cpf.12226); Ankur et al. 2025 (healthcare-bulletin.co.uk, low authority, E3 small); Victor Chang Institute/JACC report 2025 (news release, underlying study not inspected).
- **Claim:** Clinical convention 60–100 bpm (E5 consensus, AHA/Cleveland Clinic vital-signs guidance) — use as validation bound, not as the generative distribution.
- **Contradictory/limitations:** Wearable PPG resting HR (Health eHeart) is measured during self-selected "rest" and includes posture/activity heterogeneity; laboratory ECG supine values run lower. Within-person day-to-day resting HR SD is not well quantified in the retrieved evidence (est. ~3–6 bpm, **E0 provisional**).
- **Implementation recommendation:** Model resting HR as Normal(μ, σ) with μ(age, sex, fitness): μ ≈ 74–82 bpm declining ~7 bpm across 18→80 y, females +4.4 bpm, fitness offset −5 to −12 bpm (athletes truncated at ~40 bpm floor). σ_between ≈ 12–14 bpm young, decreasing slightly with age; σ_within(day-to-day) ≈ 3–5 bpm (provisional). Validate against Health eHeart age-decile curves.

### 1.2 Heart rate variability (RMSSD, SDNN)

- **Claim:** 24-h SDNN in healthy young–middle adults ≈ 140–160 ms, higher in men; HRV declines steeply with age, with the largest drop between the 2nd and 3rd decades.
  - **Magnitude:** 24-h SDNN 160 ± 40 ms (men) vs 147 ± 36 ms (women), n = 2,079, age 25–41 (Aeschbacher). Bonnemeier (n = 166, 20–70 y): all 24-h HRV metrics decline with age; largest decrease in decades 2–3; attenuation predominantly nocturnal. Almeida-Santos (n = 1,743, 40–100 y): linear decline of SDNN/SDANN/SDNNI; RMSSD and pNN50 U-shaped (decline 40→60, rise after 70).
  - **E2/E4 (multiple large cohorts, consistent direction).**
  - **Source:** Shaffer & Ginsberg, "An Overview of Heart Rate Variability Metrics and Norms," Front Public Health 2017, PMC5624990 (compiles Bonnemeier, Almeida-Santos, Aeschbacher, Beckers n=276).
- **Claim:** Short-term (5-min) resting norms are much lower than 24-h values; time-domain measures agree better across studies than frequency-domain.
  - **Magnitude:** Nunan et al. quantitative review of 44 short-term studies (n = 21,438 healthy adults): mean SDNN ~50 ms (5-min, free breathing), RMSSD ~42 ms; SDNN had the lowest coefficient of variation across studies; HF power (ms²) most variable; paced breathing raises all HRV indices except LF; FFT vs AR method changes LF/HF systematically. (Values summarized in PMC5624990; consult Nunan 2010 table for exact means by condition before fixing parameters.)
  - **E4 (systematic quantitative review).**
- **Claim:** Sex difference: women have higher mean HR, lower SDNN, but relatively greater HF power (vagal dominance) than men.
  - **Magnitude:** Meta-analysis of 296,247 healthy participants, 50 HRV measures (Koenig & Thayer 2016, cited in PMC5624990): women lower SDNN/SDNNI, lower total/VLF/LF power, greater HF power. E5.
- **Claim:** Within-person day-to-day reproducibility is moderate; single short recordings are noisy.
  - **Magnitude:** ICC: RMSSD 0.79, SDNN 0.57, LF 0.86, HF 0.47 (Pitzalis 1996, cited in PMC9157524); frequency-domain day-to-day CV 20–50% (Sandercock 2004). Practice: log-transform RMSSD (LnRMSSD), use weekly average of ≥3 morning supine recordings (Plews/Buchheit, athlete monitoring literature).
  - **E4.** Source: PMC9157524; PMC4652221.
- **Contradictory/limitations:** RMSSD reference ranges circulating in commercial sources (27–72 ms) lack population anchoring — do not use. HRV is strongly breathing- and HR-dependent; correcting for mean RR changes apparent age/sex effects. Ultra-short recordings (10–60 s) are acceptable for RMSSD (r ≈ 0.99 vs 5-min at 120 s, Munoz n = 3,387) but NOT for SDNN.
- **Implementation recommendation:** 5-min supine resting: RMSSD ~ LogNormal (median ~35–42 ms young adults, scale down ~25–30% per 2 decades after age 30; women similar median, men slightly higher absolute but women higher normalized HF). 24-h SDNN ~ Normal(150 ± 40 ms, age 25–41), declining thereafter. Simulate within-person day-to-day CV of ~10–15% for RMSSD (ln scale) and ~20–50% for spectral powers. Validate distributions against Nunan 2010 pooled table and Aeschbacher 24-h values.

### 1.3 Blood pressure (SBP/DBP/pulse pressure)

- **Claim:** Consensus ABPM thresholds for normotension (E5): 24-h mean < 130/80 mmHg; daytime < 135/85; nighttime < 120/70 (ESH). Office normal < 120/80 (ACC/AHA 2017).
- **Claim:** Ambulatory BP in healthy young adults is well below these thresholds.
  - **Magnitude (n = 53 healthy young adults, India, ABPM):** 24-h SBP 112.2 ± 8.2, DBP 68.9 ± 5.5; awake 120.7 ± 9.6 / 76.1 ± 6.1; asleep 103.6 ± 7.7 / 62.8 ± 5.7; nocturnal SBP dip 14.1 ± 4.6%; morning surge: pre-awakening +16.3 ± 11.5 mmHg, sleep-trough +25.1 ± 11.9 mmHg. Men higher SBP (~+7 mmHg) than women at all periods; DBP sex difference NS.
  - **E2 (moderate n).** Source: Natl Med J India, "Circadian profile of 24-hour ABPM in healthy young adults," https://nmji.in/circadian-profile-of-24-hour-ambulatory-blood-pressure-monitoring-in-healthy-young-adults/
  - Cross-checks (cited within same source): Japanese Ohasama normotensives 24-h SBP 118 ± 11.1 / DBP 69.4 ± 6.8; young multiethnic US adults (17–25 y) 24-h SBP 117–124 by ethnicity. Between-population 24-h SBP differences of ~5–10 mmHg.
- **Claim:** Population office SBP in normotensive US adults (NHANES): first-reading SBP 110.0 mmHg (95% CI 109.8–110.3) in the normal-BP category (n large, population-weighted). E2. Source: PMC3491581.
- **Pulse pressure:** resting ≈ 40 mmHg in young adults (e.g., 118/71 → PP 47 in supine; upright narrows PP as DBP rises: sitting 89/84… see §3); PP widens with age (arterial stiffening); PP > 55–60 mmHg after age 50 is a risk marker (E5 guideline-level).
- **Contradictory/limitations:** "Normal BP" is distribution-shifted by age, sex, measurement method (auscultatory vs oscillometric vs intra-arterial beat-to-beat), posture, and caffeine/time-of-day. White-coat effect inflates office readings by ~5–15 mmHg in a substantial minority.
- **Implementation recommendation:** Generate seated resting BP ~ Normal(SBP 112–118 ± 10, DBP 70–76 ± 8) for 20–40 y; add age slope (+~0.3–0.5 mmHg/y SBP in Western cohorts), male offset +5–7 mmHg SBP. Pulse pressure ~ SBP−DBP with age-dependent widening. Validate 24-h/awake/asleep means and dipping % against the ABPM table above; impose dip = 10–20% in ~85% of synthetic subjects (normodippers), with non-dipper/extreme-dipper minorities flagged.

### 1.4 Stroke volume (SV), cardiac output (CO), systemic vascular resistance (SVR)

- **Claim:** Resting supine SV 60–100 mL (varies with body size, sex, training); resting CO 4–8 L/min (classic mean 5 L/min at 70 kg); cardiac index 2.6–4.2 L/min/m².
  - **E1/E4** (established physiology; StatPearls Physiology, Stroke Volume, NBK547686; reference-range review Boland 2017, heartlungcirc.org).
- **Claim:** Resting SVR 800–1200 dyn·s/cm⁻⁵ (published reference texts variously give 770–1500; 700–1500 in some critical-care references).
  - **E1/E4.** SVR = 80 × (MAP − RAP)/CO; SVRI 1,970–2,390 dyn·s/cm⁻⁵/m².
  - Source: Boland J 2017, "Importance of Valid Reference Ranges for Cardiac Output…", Heart Lung Circ (heartlungcirc.org); ScienceDirect topic review.
- **Claim (posture dependence of resting values):** Sitting vs supine at rest: HR 89 ± 5 vs 71 ± 6 bpm; SV 55 ± 7 vs 76 ± 8 mL; LVEDV 21% lower sitting; CO similar (compensated); DBP higher sitting (84 ± 4 vs 76 ± 4 mmHg), PP lower. n = 7 normal subjects, echo, upright vs supine ergometry (E3, small n but classic). Source: Poliner et al., "Left ventricular performance in normal subjects—upright vs supine" (paulogentil.com PDF mirror).
- **Implementation recommendation:** SV ~ Normal(75 ± 12 mL supine, 70-kg reference), scale with body size/sex (women ~10–15% lower CO); CO = SV × HR with posture correction: upright SV × 0.65–0.77, HR +10–18 bpm → CO × 0.8–0.85. SVR ~ Normal(1000, 150) dyn·s/cm⁻⁵, derived consistently from MAP and CO rather than sampled independently. Validate via the identity MAP ≈ CO × SVR/80 + CVP and against measured tilt studies (§3).

### 1.5 Respiration rate

- **Claim:** Resting respiratory rate in the general adult population is centered near 15–16 brpm, roughly symmetric, with 90% between ~12 and 20 brpm; classic "12–20" range is accurate as a central range.
  - **Magnitude:** KORA-FF4 population study (n = 2,224, age 39–88): median 15.80 brpm, IQR 3.16; 5th–95th percentile 12.06–20.06; full range 9.19–28.17; U-shaped with age (minimum at 49–58 y: ~15.2–15.3; rises to ~17 by 79–88 y); 13.8% ≥ 18.6 brpm. Women ≈ men (small differences).
  - **E2 (large population cohort).** Source: Rückert-Eheberg et al. 2025, Respir Med/KORA-FF4, PMC11896064.
  - Elderly (≥65 y, Spain, cited therein): 2.5–97.5th percentile 12.0–28.2 brpm.
- **Claim:** Athletes breathe slower with larger tidal volume at rest: breathing rate 10.47 ± 0.70 vs 13.79 ± 0.90 brpm (athletes vs sedentary, n small); tidal volume 1.37 ± 0.14 vs 0.83 ± 0.07 L. E3 (small). Source: Front Physiol 2022, doi:10.3389/fphys.2022.820307.
- **Sleep:** NREM regular and slower; REM irregular/faster (see §6).
- **Limitations:** RR measurement method matters (visual counting vs impedance vs PPG-derived); awareness of measurement raises RR. No firm consensus normal values exist — current guidelines are clinical-consensus (the KORA authors state this explicitly).
- **Implementation recommendation:** Resting RR ~ Normal(15.5, 2.3) brpm, truncate 9–28; age: flat 20–50 then +~0.1 brpm/y after 60; fitness offset −2 to −3.5 brpm. Validate 5th/95th percentiles against KORA-FF4.

### 1.6 SpO2

- **Claim:** Resting SpO2 in healthy sea-level adults is tightly clustered at the top of the scale.
  - **Magnitude:** Normal 95–100% (E5 consensus, clinical); healthy pediatric reference mean 99.2%, median 99% with no age/sex differences (n large, PMC12010496) — adult values are typically ~1% lower (97–98% central tendency), but a large adult population distribution was NOT retrieved in Pass 1 (**gap; mark provisional**).
  - **E2/E5.**
- **Limitations:** Pulse oximetry has ±2% device accuracy (70–100% range), skin-pigmentation bias, and is insensitive (flat part of the oxyhemoglobin dissociation curve) — SpO2 is a poor dynamic variable in health and mainly a pathology/noise channel for OCPE.
- **Implementation recommendation:** SpO2 ~ truncated Normal(97.5, 1.0)%, clamp [95, 100]; add measurement noise σ ≈ 1–2%; altitude correction ~ −1% per ~700–1000 m above ~1500 m (E1, provisional). Revisit with adult normative dataset in Pass 2.

### 1.7 Body temperature (core and skin)

- **Claim:** Core temperature at rest ≈ 36.5–37.3 °C with circadian amplitude ~0.5 °C (see §2); resting core is lower in older adults; luteal-phase women +~0.4 °C.
  - **E4.** Source: Physiol Rev 2021 (journals.physiology.org/doi/abs/10.1152/physrev.00038.2020): nadir 04:00–06:00, peak 1–4 h before habitual bedtime, diurnal amplitude ~0.5 °C healthy; menstrual upward shift ~0.4 °C luteal vs follicular. Cleveland Clinic vital-signs range 36.5–37.3 °C (E5 consensus).
- **Claim:** Distal skin temperature (wrist/hand) mesor ≈ 33.1–33.2 °C, foot ≈ 31.9–32.1 °C, under natural living conditions; wrist skin temperature in wearables typically 33–37 °C.
  - **Magnitude:** n = 65 women (35 older, 30 young), 7-day continuous: hand mesor 33.11 ± 0.11 (older) / 33.21 (young) °C; foot mesor 31.87 / 32.12 °C. E2.
  - **Source:** Martinez-Nicolas et al., Clocks & Sleep / MDPI 2024, PMC11353769; wearable-context range: Polar (low authority, E0) 33–37 °C.
- **Implementation recommendation:** Core ~ Normal(36.8, 0.3) °C at mid-afternoon baseline with circadian sinusoid (§2); wrist skin ~ Normal(33.2, 0.8) °C with posture/ambient dependence and strong circadian rhythm (amplitude 1.2–1.4 °C hand, 1.8–2.2 °C foot). Validate against PMC11353769 mesors.

### 1.8 Electrodermal activity (EDA) tonic level

- **Claim:** Tonic skin conductance level (SCL) at palmar sites in relaxed healthy adults is typically in the low single-digit to ~10 µS range; commonly cited working range 2–20 µS.
  - **Magnitude:** Control (non-hyperhidrosis) group, median (IQR): right hand 4.4 (2.0) µS, left hand 5.9 (2.8) µS, feet 2.2–2.5 µS (n not shown in abstract; E2, clinical-control cohort). Textbook/commercial synthesis: tonic SCL 2–20 µS; NS-SCR rate 1–3/min relaxed, 5–10+/min stressed (low-authority source, flag E0/E2).
  - **Sources:** PMC11634377; ibtaura.com EDA review (NA authority — use only as orientation); Boucsein 2012 (cited but not retrieved directly).
- **Claim:** Ambient temperature increases tonic EDA significantly; phasic SCR amplitudes are robust to temperature.
  - n = 36 healthy, three temperature levels, controlled stimuli. E3. Source: Physiol Meas 2022, PMID 35609614.
- **Limitations:** SCL is extremely sensitive to site, electrode, hydration, humidity, and season (baseline EDA rises in warm months — arXiv 2508.18782 longitudinal analysis); between-study absolute values are NOT comparable. Normalize within-subject for OCPE.
- **Implementation recommendation:** Model lnSCL ~ Normal(ln 4–6 µS palmar, σ_ln ≈ 0.5); circadian/ambient offset via additive term; NS-SCR ~ Poisson(λ = 1–3/min at rest). Validate only in relative (within-subject, standardized) terms; absolute calibration to a specific hardware reference required.

---

## 2. Circadian Dynamics (timescale: hours)

### 2.1 Heart rate circadian rhythm

- **Claim:** HR shows a robust circadian rhythm with peak in early–mid afternoon and trough during sleep; predictable change (double amplitude) ≈ 15–27 bpm.
  - **Magnitude:** Healthy young adults (n = 53, ABPM): HR MESOR 81.7 bpm (95% CI 79.5–83.8), circadian amplitude 13.5 bpm (12.6–14.4), acrophase ~14:42 (CI 14:24–15:00). Females higher MESOR (88.1 vs 78.1 bpm) with identical amplitude/phase. E2. Source: NMJI study (§1.3).
  - 7-day/24-h ABPM non-diabetic controls (n = 50 comparator group): HR MESOR 70.23 ± 10.22 bpm; acrophase of SBP/DBP/HR in non-diabetics at 14:00–16:00. E2. Source: PMC4234238.
  - Free-living wearable cohort (n = 52, 30 days): HR acrophase ~16.8 h clock time; inter-day acrophase SD 1.69 h (stable within-person phase); activity acrophase leads HR by ~1.8 h. E2. Source: PMC12475046.
- **Claim:** Nighttime (sleep) HR is ~20–30% below daytime resting; lowest values 03:00–05:00.
  - Large wearable cohorts (Ultrahuman n = 532,000 users: median sleeping HR 64–67 bpm, IQR ~60–73; athletes 35–50 bpm — commercial, E2-low authority). PSG lab cohort (n = 1,047 without apnea, clinical referral population): wake-in-bed HR 61.0–62.3 vs N2 61.7–62.9, N3 64.0–64.2, REM 63.3–64.6 — i.e., in the laboratory with recumbent baseline, stage means differ by only ~2 bpm and nearly half show NO NREM HR dipping vs recumbent wake. E2.
  - **Contradiction (important for OCPE):** The magnitude of the nocturnal HR "dip" depends entirely on the daytime reference: ambulatory daytime (upright, active) → 20–30% dip; recumbent in-bed wake baseline → ~0–5% dip, with only 13.5% dipping ≥10%. Younger age and male sex predict dipping. Sources: PMC5914741 (Huang 2018); ultrahuman.com (low authority).
- **Implementation recommendation:** HR(t) = MESOR_HR + A_HR·cos(2π(t−φ)/24h), A_HR ≈ 13.5 bpm, φ ≈ 14:40 (anchor to habitual wake time; free-living peak ~16:30–17:00), MESOR from §1.1; superimpose posture/activity modulation. When simulating "sleep HR vs daytime resting," use the ambulatory-wake comparator (dip 20–30%), not the recumbent-wake comparator (~0–5%).

### 2.2 Blood pressure circadian rhythm

- **Claim:** BP peaks early–mid afternoon, dips 10–20% during sleep; morning surge at awakening.
  - **Magnitude (n = 53 healthy young):** SBP MESOR 114.7 (CI 112.4–117), amplitude 10.2 mmHg; DBP MESOR 70.7, amplitude 6.6; acrophase ~14:00–14:30. Dip 14.1 ± 4.6% (SBP). Sleep-trough morning surge 25.1 ± 11.9 mmHg; pre-awakening surge 16.3 ± 11.5 mmHg. E2. Source: NMJI study.
  - **Consensus (E5):** normal dip 10–20%; non-dipper <10%, reverse dipper (night > day) and extreme dipper (>20%) are risk phenotypes. Sources: ESH ABPM thresholds; Wisconsin Sleep Cohort (n = 497, mostly normotensive) confirms dipping as the dominant pattern (sciencedirect S1933171111000064).
- **Implementation recommendation:** SBP/DBP(t) = MESOR + A·cos model with A_SBP ≈ 10 mmHg, A_DBP ≈ 7 mmHg, φ ≈ 14:15; add awakening surge kernel: +15–25 mmHg SBP over ~30–60 min straddling wake time; assign dip phenotype: dipper (10–20%) ~80–85%, non-dipper ~10–15%, extreme/reverse ~5% (healthy young). Validate against ABPM table §1.3.

### 2.3 Core temperature circadian rhythm

- **Claim:** Core body temperature nadir 04:00–06:00, peak 1–4 h before habitual bedtime; amplitude ~0.5 °C in healthy young adults; amplitude damped 20–40% in healthy elderly; phase advances 1–2 h with age.
  - **E4** (replicated; rectal/telemetry). Sources: Physiol Rev 2021 heat-stress review (doi:10.1152/physrev.00038.2020); JCI 2017 "The aging clock" (jci.org/articles/view/90328); Nature Sci Rep srep02229 (amplitude 0.32 ± 0.03 °C, range 0.11–0.72, in a mixed elderly/dementia cohort — lower bound context).
- **Implementation recommendation:** T_core(t) = 36.9 + 0.25·cos(2π(t−φ_T)/24h) with φ_T ≈ 17:00–19:00 (peak) / nadir ≈ 04:00–06:00; amplitude 0.25 °C (half-amplitude; full swing ~0.5 °C); scale amplitude ×(1 − 0.002–0.004·(age−30)) for age > 60 clamp [0.6, 1.0]; luteal offset +0.4 °C for premenopausal women (cycle-phase covariate). Note sleep itself masks/evokes additional temperature fall — superimpose evoked component (~ −0.2–0.3 °C on sleep onset, E1, provisional).

### 2.4 Cortisol awakening response (CAR) and autonomic awakening response

- **Claim:** Awakening triggers a cortisol rise of ~50% within the first 30 min; responder rate ~75%; high intra-individual stability (r up to 0.63).
  - n = 509 adults across 4 combined studies. E4. Source: Wüst et al. 2000, PMID 12689474.
  - Circadian modulation: CAR amplitude depends on circadian phase of awakening — ≥50% increase only when awakening ~3 h before habitual wake time; no rise when awakening in afternoon/evening. E3 (forced desynchrony/constant-routine style protocols). Source: PMC9669756.
- **Claim:** Morning cardiovascular activation: HR/BP rise on waking is driven by circadian (endogenous) + postural + behavioral (activity onset) components; morning BP surge values in §2.2. The morning is the peak-incidence window for cardiovascular events (E2, replicated — cited within Tobaldini review PMC3797399).
- **Implementation recommendation:** Model awakening as (i) step+rise in sympathetic drive over ~30–45 min, (ii) CAR magnitude ~ LogNormal(median 50% of awakening level, IQR ~25–100%), gated by circadian phase per PMC9669756; combine with the postural stand response (§3) — real morning HR/BP traces = circadian rise + CAR + orthostatic challenge.

---

## 3. Orthostatic Response (supine → sit → stand → prolonged standing)

### 3.1 Initial response (0–30 s; timescale: seconds)

- **Claim:** Active standing produces a characteristic transient: BP falls to minimum within ~10 s, recovers to supine values within 20–30 s, typically with overshoot; HR rises abruptly from ~3 s (vagal withdrawal + muscle-pump "exercise reflex"), peaks ~10–15 s.
  - **Magnitude:** Initial SBP drop > 40 mmHg or DBP > 25 mmHg = abnormal (initial orthostatic hypotension, Wieling criteria). 300–800 mL blood shifted to lower body on standing. 30:15 ratio (RR at ~30th beat / ~15th beat) > 1.04 normal, age-dependent. Initial HR increase should exceed ~20 bpm in young (10–14 y) and ≥ 11 bpm at 75–80 y.
  - **E3/E4** (established autonomic testing literature). Sources: Hilz & Dütsch, "Quantitative studies of autonomic function," Muscle Nerve 2006, doi:10.1002/mus.20365; "Clinical Assessment of the ANS" review, PMC11292036; NCSU thesis compilation (mechanistic synthesis, E1).
  - Passive head-up tilt abolishes/attenuates the initial transient (no muscle pump) — active stand and tilt are NOT interchangeable.
- **Implementation recommendation:** Active stand: BP dip kernel −15 to −25 mmHg SBP nadir at 8–12 s, recovery to baseline by 20–30 s with +5–10 mmHg overshoot; HR monoexponential rise starting 2–3 s, τ ≈ 4–6 s, peak +20–30 bpm at ~15 s, then partial decay to steady state. Tilt: smaller initial dip, slower HR rise. Validate against Finapres-style continuous traces in the cited autonomic-testing literature.

### 3.2 Early stabilization (1–2 min)

- **Claim:** After the initial transient: DBP rises ~10 mmHg, sympathetic HR increase ~10 bpm above supine; baroreflex-mediated; sympathetic outflow becomes constant by ~5 min; humoral (RAAS/catecholamine) mechanisms add in beyond ~5–10 min.
  - **E4.** Sources: Hilz & Dütsch 2006 (above); NDRF autonomic disorders review (ndrf.org PDF): steady state upright = HR +10–15 bpm, DBP +~10 mmHg, SBP ~unchanged, thoracic blood volume −30%, CO −30% (this −30% figure is on the high end of the literature; see below).

### 3.3 Steady-state upright (1–30 min)

- **Claim:** SV falls ~20–33%, CO falls ~14–20%, HR rises ~10–15 bpm, MAP maintained/slightly increased via SVR rise (baroreflex).
  - **Magnitude (quantitative, MRI):** supine → 60° HUT: SV −23 mL (CI 16–30; −23%), CO −0.9 L/min (CI 0.4–1.4; −14%), HR +~3–10 bpm. n healthy; E3. Source: PMID 19650800 (Scand Cardiovasc J 2009).
  - Classic gravity-stress review: SV −33%, CO −20% upright vs supine; CO inversely linear with sin(tilt angle); HR increase insufficient to compensate SV fall. E4 (compilation of many studies; neuroyates.com PDF of "Cardiovascular adjustments to gravitational stress").
  - Mathematical model validated against in-vivo data: 70° tilt → CO −19%, stroke work −33%, RR interval −20%. E1/E3. Source: Fois et al. 2022, PMC8892183.
- **Claim (healthy orthostatic tachycardia distribution — critical for POTS contrast):** Healthy controls (n = 15, Vanderbilt): active stand ΔHR 23 ± 3 bpm at 5 min, 25 ± 3 at 10 min, 26 ± 3 at 30 min; passive tilt ΔHR 27 ± 3 (5 min), 34 ± 3 (10 min), 40 ± 4 (30 min). The 30-bpm POTS criterion has poor specificity on tilt: 60% of healthy controls exceeded it at 10-min tilt, 80% at 30-min tilt; optimal discriminators: stand-10min 29 bpm, tilt-10min ~37–38 bpm, tilt-30min 47 bpm.
  - **E3.** Source: Plash et al., "Diagnosing POTS: tilt vs stand," PMC3478101.
  - Adolescents: 97.5th percentile ΔHR 52.7 bpm on 5-min 70° tilt (n = 106, Low lab); another cohort mean ΔHR 21.5 ± 10.6 bpm at 2 min (n = 100) — hence the ≥40 bpm adolescent threshold (E2/E3; compiled by mecfsscience.org, underlying studies: Low et al.; Hawaii military-clinic study 1992).
- **Claim:** Classical orthostatic hypotension = SBP fall ≥20 or DBP ≥10 mmHg within 3 min of standing/tilt (E5 consensus).
- **Recovery on lying down:** HR/BP return to supine baseline within ~30–60 s, typically with transient bradycardic overshoot (vagal rebound); asymmetric tilt-up vs tilt-down transients with stronger under/overshoots at faster tilt rates (E3, PMC8892183).
- **Implementation recommendation:** Steady state (10-min stand): ΔHR ~ Normal(+12, 5) bpm young adults (cap distribution so >95% below 30 bpm; allow tail to 25–28); ΔDBP ~ Normal(+8, 4) mmHg; ΔSBP ~ Normal(0, 6); ΔSV ~ −23% (range −15 to −33%); ΔCO ~ −15 to −20% (recruit SVR +~25% to hold MAP). Timescales: initial transient (s), stabilization (1–2 min), drift during prolonged standing (+2–5 bpm per 10 min from plasma filtration, E1). POTS perturbation = raise ΔHR gain and reduce SVR compensation.

### 3.4 Modulators of orthostatic tolerance

- **Dehydration:** ~2–3% body-mass hypohydration increases stand-induced ΔHR; iso-osmotic hypovolemia (furosemide, −3% mass) increases cardiopulmonary baroreflex gain and modulates HR response to tilt; exercise-dehydration + LBNP: HR 119 ± 8 vs 82 ± 7 bpm, SBP 95 ± 1.7 vs 108 ± 2.3 mmHg at −50 mmHg LBNP; fluid ingestion partially restores. Mild 24-h fluid restriction (−2.3% mass, −4.1% blood volume) raised exercising HR +7 bpm but did NOT impair orthostatic tolerance (LBNP) in n = 17 — i.e., mild hypohydration effects are modest and context-dependent.
  - **E3** (controlled, small n). Sources: PMC6723555 (hydration & CV function review); Davis & Fortney 1997 (NASA); Pignanelli et al. 2026, PMID 42109236.
- **Water drinking pressor response:** 200–500 mL water raises SBP; cold water stronger than room temperature (young: +15.3 ± 9.7 room vs +22.6 ± 11.5 cold mmHg; older women: +21.8 ± 14.3 vs +41.5 ± 19.8). E3. Source: Front Neurol 2021/PMC8793880.

---

## 4. Exercise Response

### 4.1 Maximal and submaximal HR

- **Claim:** HRmax ≈ 208 − 0.7 × age (Tanaka), r = −0.90, from 351 studies / 18,712 subjects meta-regression + 514-subject lab validation; independent of sex and activity status at population level; standard error of estimate ~10–11 bpm.
  - **E5.** Source: Tanaka et al., JACC 2001, PMID 11153730. Fox 220−age has SD ~10–12 bpm and is unvalidated historically (Robergs & Landwehr 2002); female-specific Gulati 206 − 0.88 × age (n = 5,437, Circulation 2010); fit-cohort Nes/HUNT 211 − 0.64 × age (n = 3,320). Measured HRmax in a GXT validation cohort: 181.7 bpm mean with RMSE 10.7–11.7 for best equations (PMC7523886). Individual HRmax can deviate 20–30 bpm from prediction.
- **Implementation recommendation:** HRmax = 208 − 0.7·age + ε, ε ~ Normal(0, 11); never sample HR zones without this residual. HR–VO2 relation approximately linear between ~40% and 100% VO2max (E1/E4, established exercise physiology).

### 4.2 Onset kinetics

- **Claim:** HR rise at exercise onset is biphasic: rapid phase (first ~10–30 s) dominated by vagal withdrawal (feedforward/central command + muscle reflex), slower phase by sympathetic activation; the vagal component is visible as a steeper HR acceleration for small vs large workload steps.
  - **E3** (n = 15 healthy men, 50 vs 100 W step comparison — Aga Khan Univ. study, ecommons.aku.edu). Overall HR approaches steady state with roughly exponential time course (τ on the order of 30–60 s at moderate intensity, E1 — quantitative consensus value not pinned in Pass 1; mark provisional).
- **Implementation recommendation:** Two-exponential HR onset: fast component (τ ≈ 5–10 s, amplitude ∝ vagal reserve), slow component (τ ≈ 30–45 s); steady-state HR ≈ resting + (HRmax − resting) × relative intensity, with a small slow drift (cardiovascular drift, see §7) during prolonged exercise.

### 4.3 Heart-rate recovery (HRR) and vagal reactivation

- **Claim:** HRR at 1 min ≤ 12 bpm (after maximal exercise with 2-min cool-down) is abnormal and predicts mortality; per 10-bpm decrement in 1-min HRR, mortality hazard ratio 1.74 (95% CI 1.54–1.96).
  - Cole et al., NEJM 1999, n = 2,428, doi:10.1056/NEJM199910283411804 (RR 4.0 unadjusted, 2.0 adjusted). Meta-analysis of prospective cohorts (PMC5524096): per-10-bpm-decrement HR 1.74 (1 min) / 1.50 (2 min) for all-cause mortality. E5.
- **Claim:** Typical healthy HRR values: HRR1 ~ 18–25 bpm; >25 bpm common in trained individuals; HRR2 > 22 bpm normal (ACSM cutoffs). Early HRR (first 30–60 s) is predominantly vagal reactivation; later recovery adds sympathetic withdrawal; full return to baseline can take 30–60+ min after hard exercise (HR still +43 bpm at 5 min in a modeled sedentary example after maximal exercise).
  - **E3/E4.** Sources: Cole 2000 Ann Intern Med (doi:10.7326/0003-4819-132-7-200004040-00007); Imai et al. 1994 JACC (vagally mediated HRR faster in athletes, blunted in CHF; doi:10.1016/0735-1097(94)90150-3); Peanha/"Pathophysiology of Exercise HRR" PMC6932299; Front Psychol 2020 sprint HR-kinetics study (n = 24, τoff and delay quantified, doi:10.3389/fpsyg.2019.02950).
- **Contradictory finding (fitness effect):** Master athletes vs sedentary middle-aged men showed NO significant HRR1 difference (22.9 ± 5.6 vs 21.3 ± 6.7 bpm, p = 0.20; Choi 2014, n = 50/50) despite large resting-HR and VO2max differences — whereas young active vs inactive students showed a large HRR1 difference (45.7 ± 7.2 vs 31.5 ± 6.9 bpm; different protocol/submaximal). **Conclusion: fitness effect on HRR1 is protocol- and age-dependent; do not implement a single universal fitness→HRR mapping.**
- **Implementation recommendation:** HRR as biexponential decay: fast vagal component τ ≈ 20–40 s; slow sympathetic decay τ ≈ 2–10 min; HRR1 ~ Normal(20, 6) bpm for healthy adults post-maximal exercise with cool-down; shift mean +5–15 bpm for endurance-trained, −5 for sedentary (protocol-dependent). Validate against Cole-style protocol definition (position and cool-down change values materially).

---

## 5. Meal (Postprandial) Response (timescale: 15 min – 4 h)

- **Claim:** A meal reliably increases HR, SV, and CO in healthy adults.
  - **Systematic review (25 studies, 416 healthy participants, age 18–69):** HR increased in 19/19 studies (+6% to +21%); CO +9% to +100% (18/19); SV +18% to +41% (11/11). E5. Source: i-jmr.org 2024 systematic review PDF (Central Hemodynamic and Thermoregulatory Responses to eating).
  - Typical single-lab experience: HR +8 bpm, returning to baseline over ~4 h (E4, repeated within a research program; PMC6590239).
  - Dose-dependence: CO rise peaks 30–60 min post-meal; large meal (~2.5×) produces ~100% more "extra" blood delivery over 2 h and remains elevated at 2 h, vs small meal returning to baseline by 2 h (n = 4, Doppler, E3; PMID 1877363). Meal size 280 vs 560 vs 840 kcal: graded HR increases, largest after 840 kcal, separable at 15–120 min (J Appl Physiol 2021, doi:10.1152/japplphysiol.00903.2020); HR changes explained ~68% of postprandial SMA flow changes (adjusted r²).
  - Splanchnic: SMA blood flow approximately doubles postprandially (+87% high-carb, +121% high-fat meal); splanchnic blood volume +~20%, greatest after carbohydrate. E3/E4. Sources: MDPI Nutrients 2019 (10.3390/nu11081717); PMC2290234.
- **Claim:** In healthy YOUNG adults, BP is maintained postprandially (compensated by HR↑, peripheral vasoconstriction, SV/CO↑); in older adults, postprandial hypotension (≥20 mmHg SBP fall within 2 h) is common (~30–40% of elderly/nursing-home populations; systematic review PMID 38411408 ~40%).
  - Mechanism/timing: fall almost immediate, maximum 30–60 min; carbohydrate (glucose) dominant driver, protein/fat minor; magnitude depends on rate of small-intestinal nutrient delivery (intraduodenal glucose 3 kcal/min but not 1 kcal/min caused significant SBP/DBP fall + HR rise in healthy elderly, n = 8, E3; PMC2290234).
  - Healthy young typically show SBP changes within ±10–15 mmHg (E2, lower authority commercial synthesis superpower.com — treat as provisional, flagged).
- **Implementation recommendation:** Postprandial kernel: HR +6–12% (young) / +10–21% (larger meals), peak 30–60 min, decay τ ~ 60–90 min (duration ∝ meal size); CO +10–30%; SV +10–20%; SMA flow ×1.9–2.2; SBP ~ 0 ± 8 mmHg (young) vs −10 to −25 mmHg (elderly, carb-rich). Glucose/carbohydrate content as the main covariate. Validate timing against the 30–60-min peak across the 25-study review.

---

## 6. Sleep (timescale: minutes within stage; hours across night)

- **Claim:** NREM sleep = parasympathetic predominance (HF power ↑, LF/HF ↓, BRS ↑ in early cycles); REM = sympathetic surges on vagal background (LF/HF ↑, HR variability ↑, phasic HR accelerations, peripheral vasoconstriction in phasic REM).
  - **E4** (replicated across many small PSG studies). Sources: Tobaldini et al. 2013 review, PMC3797399; Cabiddu et al. 2012 (n = 11 healthy women; NREM ↑ HF coherence between HR and respiration; REM shift to sympathetic), PMID 22416233; Stein & Pu 2012 (cited).
- **Claim:** Absolute HR differences between stable sleep stages are SMALL (~2 bpm) when wake baseline is recumbent in-bed; mean values (n = 1,047 no-apnea clinical cohort): wake 62.3, N1 63.7, N2 62.9, N3 64.2, REM 64.6 bpm (short-sleep subgroup ~3–4 bpm higher in all stages); women higher sleep HR than men in all stages (N2 63.8 vs 58.1) despite lower LF/HF. Only 13.5% show ≥10% NREM HR dip vs recumbent wake (younger, male, lower BMI dip more).
  - **E2** (large cohort; contradicts naive "HR falls steeply in deep sleep" assumption). Source: Huang et al. 2018, PMC5914741.
- **Claim:** Respiration: NREM deeper/more regular (RR ~10–16 brpm), REM shallower/variable (~8–24 brpm); breathing regularity highest in N3. E3/E4 (Cabiddu 2012; wearable PPG sleep-staging feature summaries, chatppg.com — low authority but consistent with PSG literature).
- **Claim:** BP dips 10–20% in sleep (§2.2); temperature falls (circadian + evoked); core temperature nadir coincides with late-night/early-morning; REM episodes produce transient BP/HR surges — late-night REM has higher sympathetic modulation than early-night REM (links to morning CV event peak). E2/E4.
- **Implementation recommendation:** Stage-conditioned autonomic state machine: N3 = highest vagal gain (HF ↑, LF/HF minimum, BRS ↑), HR −0 to −5% vs recumbent wake but −20–30% vs ambulatory day; REM = elevated LF/HF with superimposed phasic HR bursts (+5–15 bpm, seconds, clustered with eye movements); RR: N3 Normal(13, 1.2) brpm low CV, REM Normal(16, 3) high CV; SpO2 stable 96–98% (healthy); EDA: NS-SCR rate falls in stable NREM, rises with arousals (E2, provisional). Validate stage-conditional HR/HF against Cabiddu 2012 and Huang 2018 cohorts.

---

## 7. Environmental Stressors

### 7.1 Heat

- **Claim:** Resting HR rises ~8.7–13.7 bpm per +1 °C body temperature (age-dependent; overall ~12.3 bpm/°C).
  - Acute-care observational series (temperature–HR association, confounder-adjusted); E2. Source: PMC9605188. Classic teaching value ~10 bpm/°C (fever). **Context limitation:** derived largely from febrile/acute presentations; passive-heat-stress laboratory data show similar direction with HR strongly correlated to core temperature (r = 0.92 during exercise with skin 32→39 °C; r = 0.96 across thermal conditions; Chou/Lee studies within PMC10405766 review).
- **Claim (mechanism split, E3):** Passive heat stress HR rise ≈ 40% direct cardiac temperature effect + 60% autonomic (of the autonomic portion ~75% vagal withdrawal, ~25% sympathetic activation) — baboon + human evidence compiled in the hot-skin review (PMC10405766). Skin heating alone raises HR within ~8 s (neural, before core change); core-temperature effect on effector responses outweighs skin ~9:1.
- **Claim:** Severe passive heat stress (core + skin > 39 °C) raises CO by ~3.3–6.6 L/min, directed mostly to skin; MAP maintained by CO↑ against TPR↓; SV preserved while core < ~38 °C, then falls as HR-driven shortening of filling time dominates (the "alternative mechanism": SV decline is primarily HR-mediated, supported by β-blockade and pacing experiments). Cardiovascular drift (progressive HR rise at constant workload) begins at LOWER environmental stress than the core-temperature inflection point (PSU HEAT project, n = 51 young adults, 27 F; E3; PMC10393325).
  - Sweating/EDA: tonic EDA rises with ambient temperature (§1.8, PMID 35609614); sweat onset and rate are core+skin-temperature driven (E4, classical thermoregulation).
- **Implementation recommendation:** ΔHR_heat ≈ 10 × ΔT_core (bpm/°C) + skin term (~1/9 weight), cap near HRmax-reserve; SV_heat(T_core > 38 °C) declines ~ −2 to −4 mL per +5 bpm HR; implement cardiovascular drift as slow HR ramp (onset threshold below uncompensable-heat threshold). Validate slope against PMC9605188 (12.3 bpm/°C) and drift onset against PMC10393325.

### 7.2 Cold

- **Claim:** Cold pressor test (hand in ice water, 3 min): SBP +~10–20 mmHg, DBP +~8–20 mmHg, MAP +~17 mmHg; HR response heterogeneous (two phenotypes: sustained increase in ~half; initial rise then fall in the other half).
  - n = 200 non-obese: ΔSBP 10.38 ± 6.35, ΔDBP 7.84 ± 3.72 mmHg (E3, PMC4337083); n = 56: SBP 118 ± 8 → 138 ± 14, DBP 71 ± 7 → 91 ± 11 (E3, physoc phy2.13985); n = 39: HR bimodal response (PMID 18198985). Whole-body cold: BP↑, HR/CO essentially unchanged in young adults; older adults show augmented pressor response and impaired SV maintenance (E3/E4, Front Physiol review doi:10.2478/fzm-2022-0022).
- **Implementation recommendation:** Cold stressor module: pressor response Normal(+12, 6) mmHg SBP young (+20–40 in older), HR +5 ± 5 bpm (mixture model: 50% sustained, 50% transient); distal skin temperature drops rapidly (vasoconstriction) — couple to PPG amplitude attenuation.

### 7.3 Dehydration

- Covered in §3.4. Summary parameter: per −1% body mass hypohydration, orthostatic/exercise HR +~3–8 bpm (context: exercise-heat > furosemide > mild fluid restriction); orthostatic tolerance preserved until ~2–3% loss in most healthy young adults. E3 (small n, consistent direction).

---

## 8. Cross-Variable Physiological Relationships (coupling constraints for OCPE)

| Relationship | Quantitative form | Evidence | Sources |
|---|---|---|---|
| HR ↔ SV (orthostasis) | Upright: SV −20–33%, HR +10–15 bpm, CO −14–20%; CO linear in sin(tilt angle); in POTS-like states ΔHR inversely related to ΔSVI until hyperadrenergic phenotype (ΔHR ≥ 40 bpm) breaks the relation | E3/E4 | PMID 19650800; PMC8892183; gravitational-stress review; PMC11677391 (ME/CFS tilt, healthy controls n=48) |
| HR ↔ SV (exercise/heat) | SV plateaus at ~40–60% VO2max then CO rise is HR-driven; in heat, SV decline is HR-mediated (filling time), reversible with β-blockade at matched HR | E3/E4 | PMC10405766 |
| HR ↔ respiration (RSA) | Paced 6 breaths/min deep breathing: max-min ΔHR ≥ 15 bpm normal (11–14 borderline, ≤10 abnormal); E/I ratio age-dependent 1.62 (age 16) → 1.20 (age 70); lower normal limits by decade: ≥1.36 (20s), 1.23 (30s), 1.14 (40s), 1.10 (50s), 1.06 (60s) | E3/E4 (Ewing battery, age norms: Smith 1982; Ziegler 1992; Vlčková Czech norms) | PMC8490774; PMC2941421; PLOS ONE 10.1371/journal.pone.0294441; kubios.com synthesis (low authority, direction only) |
| Posture ↔ HR/BP/CO | See §3 (full time-course model) | E3/E4 | As above |
| Temperature ↔ HR | +8.7–13.7 bpm per °C core (mean 12.3); skin:core weight ~1:9; circadian +~5–7 bpm day vs night independent component | E2/E3 | PMC9605188; PMC10405766 |
| Sleep ↔ autonomic | NREM: vagal ↑ (HF ↑, LF/HF ↓, BRS ↑); REM: sympathetic bursts, LF/HF ↑; late-night REM more sympathetic than early-night REM | E4 | PMC3797399; PMID 22416233; PMC5914741 |
| Meal ↔ HR/CO/splanchnic | HR +6–21%, CO +9–100%, SV +18–41%, SMA flow ×~2; peak 30–60 min; duration ∝ meal size | E3/E5 | i-jmr.org 2024 review; PMID 1877363; PMC6590239 |
| Circadian ↔ all | HR amplitude ~13.5 bpm; SBP ~10 mmHg; DBP ~7 mmHg; T_core ~0.5 °C; skin (distal) 1.2–2.2 °C; cortisol CAR +50% (phase-gated) | E2/E4 | §2 sources |
| Fitness ↔ HR/HRV | Resting HR −8 to −12 bpm; resting RR −3 brpm; HRV ↑; HRR1 effect inconsistent (protocol-dependent); HRmax unchanged by fitness at population level | E2–E5 (mixed) | Choi 2014; Tanaka 2001; §4.3 contradiction |
| Age ↔ autonomic | HRV ↓ steeply decades 2–3; E/I and 30:15 ratios decline (age norms above); orthostatic initial HR response declines (≥20 bpm young → ≥11 bpm at 75–80 y); T_core amplitude −20–40%; CAR preserved magnitude but phase-gated | E2/E4 | PMC5624990; Hilz & Dütsch 2006; jci.org/90328; PMC9669756 |
| Sex ↔ | Women: HR +4.4 bpm, lower SDNN but higher HF fraction, higher sleep HR (all stages), lower SBP ~ −7 mmHg, similar RR, delayed post-CAR cortisol decline | E2/E5 | Health eHeart; Koenig & Thayer meta (296k); NMJI; PMC5914741; PMID 12689474 |

---

## 9. Healthy Reference Distribution — Summary Table

Distributional reference for generative modeling (healthy adults 18–45 y unless noted). Sources and evidence level per row.

| Variable | Central value (mean±SD or median [IQR]) | Practical range (5th–95th pct) | Key modulators | Evidence | Sources |
|---|---|---|---|---|---|
| Resting HR (supine/seated) | 72 ± 11 bpm (population real-world ~74–82 by age decile) | ~55–95 bpm (athletes 40–60) | age ↓, female +4.4, fitness −8–12 | E2 (n=25k) / E4 | PMC6592896; cpf.12226 |
| RMSSD (5-min resting) | ~35–42 ms (lognormal; median) | ~15–90 ms | age ↓↓, breathing, fitness ↑ | E4 | Nunan review via PMC5624990 |
| SDNN (5-min) | ~50 ± 20 ms | ~20–90 ms | as above | E4 | PMC5624990 |
| SDNN (24-h, age 25–41) | 150 ± 38 ms (men 160±40 / women 147±36) | ~90–230 ms | age ↓, male + | E2 (n=2,079) | Aeschbacher via PMC5624990 |
| SBP/DBP (resting seated, young) | 112–118 / 70–76 (±10 / ±8) mmHg | 95–135 / 55–85 mmHg | male +5–7 SBP, age +, posture | E2/E5 | NMJI ABPM; PMC3491581; ESH |
| Pulse pressure | ~40 ± 8 mmHg (young) | 28–55 mmHg | age ↑ (stiffening), posture ↓ upright | E2/E4 | derived from above; Poliner |
| Stroke volume (supine rest) | 75 ± 12 mL (70-kg ref) | 55–100 mL | body size, sex, training, posture (−23–33% upright) | E1/E4 | NBK547686; PMID 19650800 |
| Cardiac output (rest) | 5.0 ± 1.0 L/min (CI 2.6–4.2 L/min/m²) | 4–8 L/min | body size, posture (−14–20% upright) | E1/E4 | Boland 2017; PMC8892183 |
| SVR | 1000 ± 150 dyn·s/cm⁻⁵ | 800–1200 (770–1500 texts) | derived from MAP/CO; ↑ upright ~+25% | E1/E4 | Boland 2017 |
| Respiration rate (rest) | 15.8 [IQR 3.2] brpm | 12.1–20.1 (5th–95th) | age U-shape, fitness −3, sleep stage | E2 (n=2,224) | PMC11896064 |
| SpO2 (sea level) | 97.5 ± 1.0 % (truncated) | 95–100 % | altitude, device error ±2% | E5/E2 (adult SD provisional) | consensus; PMC12010496 (pediatric anchor) |
| Core temperature | 36.8 ± 0.3 °C + circadian ±0.25 °C | 36.5–37.3 °C | circadian, luteal +0.4, age ↓ amplitude | E4/E5 | physrev.00038.2020; Cleveland Clinic |
| Wrist skin temperature | 33.2 ± 0.8 °C; foot 32.0 °C | 31–35 °C (ambient-dependent) | circadian amp 1.2–1.4 °C (hand), 1.8–2.2 (foot) | E2 (n=65) | PMC11353769 |
| EDA tonic SCL (palmar) | 4–6 µS [IQR ~2–8] (lognormal) | ~1–20 µS | site, ambient T ↑, hydration, season; within-subject normalization mandatory | E2 (provisional) | PMC11634377; PMID 35609614 |
| Orthostatic ΔHR (10-min stand) | +12 ± 5 bpm (model target; lab controls +23–25 bpm at 10 min in tilt-adjacent protocols — see note) | 95% < +25–28 bpm; POTS ≥30 | age ↓, hydration, heat, fitness | E3 | PMC3478101 (controls); Hilz & Dütsch |
| Orthostatic ΔBP | ΔSBP 0 ± 6; ΔDBP +8 ± 4 mmHg | OH if ≤ −20/−10 | baroreflex, volume status | E4/E5 | Hilz & Dütsch 2006; consensus |
| HRR (1 min post-max exercise) | ~20 ± 6 bpm (≤12 abnormal) | 10–35+ bpm | fitness (protocol-dependent), cool-down, position | E5 | NEJM199910283411804; PMC5524096 |
| HRmax | 208 − 0.7·age ± 11 bpm | ±2 SD = ±22 bpm | age only (population) | E5 | PMID 11153730 |
| Circadian HR amplitude | 13.5 bpm (half-amplitude), acrophase ~14:40 | 10–17 bpm | sex (MESOR only), chronotype | E2 | NMJI; PMC4234238 |
| Nocturnal BP dip | 14 ± 5 % | 10–20 % normal | age, sodium, genetics | E2/E5 | NMJI; Wisconsin cohort |
| Morning SBP surge (sleep-trough) | 25 ± 12 mmHg | ~10–45 mmHg | age, sex (NS) | E2 | NMJI |
| CAR (cortisol) | +~50 % within 30 min of awakening | ~25–160 %; responder rate 75% | circadian phase of awakening | E4 | PMID 12689474; PMC9669756 |
| Postprandial ΔHR | +6–21 % (peak 30–60 min) | meal-size graded | meal size/composition (carb), age | E5/E3 | i-jmr 2024 review; PMID 1877363 |
| Postprandial ΔSBP (young) | 0 ± 8 mmHg (provisional) | −10 to +10 mmHg | carb load; elderly −10 to −25 | E3 (young data sparse) | PMC2290234; PMC6590239 |
| Sleep stage HR | wake 62, N2 63, N3 64, REM 65 bpm (recumbent reference; n=1,047) | stage spread ~2 bpm | reference-frame dependent; ambulatory dip 20–30% | E2 | PMC5914741 |
| Heat: ΔHR per °C core | +8.7–13.7 bpm/°C (mean 12.3) | — | age, skin T (1:9 weight) | E2/E3 | PMC9605188; PMC10405766 |
| Cold pressor ΔBP | ΔSBP +10 ± 6; ΔDBP +8 ± 4 mmHg | up to +20/+20 | age ↑, obesity ↓ | E3 | PMC4337083; phy2.13985 |

> **Note on orthostatic ΔHR row:** The Vanderbilt healthy-control means (+23–26 bpm at 10-min stand) are higher than the classic "+10–15 bpm steady-state" teaching value because they include the full overshoot and were measured in a POTS-referral-lab protocol. For OCPE, implement the steady-state standing ΔHR distribution as Normal(+12, 5) bpm with a right tail reaching ~+28 bpm, and validate the *fraction exceeding 30 bpm* at ~2–5% for stand and ~40–60% for 10-min tilt (per PMC3478101 specificity data). Flag as the single most consequential calibration choice for the POTS boundary.

---

## 10. Timescale Architecture (for model design)

| Timescale | Phenomena |
|---|---|
| Seconds | RSA; baroreflex HR response to standing (onset ~3 s, peak ~15 s); initial BP dip nadir ~10 s; heat-skin neural HR response ~8 s; phasic SCR (1–3 s latency, 3–5 s peak) |
| Minutes | BP recovery post-stand (20–30 s–1 min); early orthostatic stabilization (1–2 min); exercise HR onset (τ ~30–60 s) and HRR fast phase; cold pressor response; postprandial onset (15–30 min) |
| Hours | Postprandial course (peak 30–60 min, resolve 2–4 h); prolonged-standing drift; cardiovascular drift in heat; CAR (30–45 min); recovery to baseline HR post-exercise (30–60+ min) |
| ~24 h | Circadian rhythms (HR, BP, T_core, skin T, cortisol, autonomic balance); sleep-stage cycling (90-min ultradian) |
| Days–weeks | Day-to-day HRV variability (CV 10–50% metric-dependent); menstrual-cycle temperature/HR effects; training adaptation of resting HR/HRV; acclimatization |

---

## 11. Key Gaps & Contradictions (for Pass 2)

1. **Adult SpO2 population distribution** (mean/SD) — not retrieved; pediatric anchor only. Provisional.
2. **Within-person day-to-day resting HR SD** — not directly quantified in retrieved sources; ~3–5 bpm assumed (E0).
3. **Exercise HR-onset time constants** — only qualitative/biphasic evidence; τ values are provisional.
4. **Healthy young postprandial BP distribution** — most quantitative PPH work is elderly; young-adult SBP change (±10 mmHg) rests partly on low-authority synthesis.
5. **EDA absolute norms** — hardware/site-dependent; no large normative dataset retrieved; implement relative/standardized only.
6. **Fitness→HRR1 mapping is contradictory** (Choi 2014 null vs student-cohort large effect) — protocol dependence must be encoded explicitly.
7. **Orthostatic steady-state ΔHR**: classic teaching (+10–15 bpm) vs tilt-lab control means (+23–26 bpm at 10-min stand) — resolved above as protocol/population difference, but this boundary needs careful validation for POTS-contrast modeling.
8. **Sleep HR "dip"** is reference-frame dependent (ambulatory day vs recumbent wake) — must be modeled as comparator-relative, not absolute.

*Document generated as Pass 1 (discovery) evidence base. All DOIs/PMIDs/PMCIDs cited were observed in search results during this review.*
