# OCPE External Validation Dataset Inventory

**Purpose:** Independent public datasets for validating OCPE (Open Computational Physiology Engine) synthetic multimodal wearable data (ECG, PPG, EDA, respiration, temperature, IMU) across healthy and systemic-disorder phenotypes (POTS/dysautonomia, ME/CFS, long COVID, EDS, autoimmune/inflammatory, metabolic).

**Evidence discipline:** Every dataset below was verified to exist via its host page (PhysioNet, UCI, NSRR, Borealis Dataverse, Oxford ORA, Zenodo, etc.) or its primary publication during Pass 1 discovery. Population/statistics are as reported by the source; where the source did not state a statistic, the field says "not stated by source" rather than estimating. Access terms are reported as stated on the host pages.

**Access shorthand:** OPEN = downloadable without credentialing (license noted); DUA/REGISTERED = free but requires registration + data-use agreement; CREDENTIALED = requires training/institutional credentialing; REQUEST = shared by authors on request; CONTROLLED = formal application/fee or government-style access review.

---

## 1. Orthostatic physiology (tilt / active stand; beat-to-beat HR/BP)

### 1.1 Physiologic Response to Changes in Posture (PRCP) — PhysioNet
- **Host/access:** PhysioNet (physionet.org/content/prcp/), Open Access. Published 2016 on PhysioNet (recordings from an earlier MIT/Harvard tilt study, Heldt et al.).
- **Population:** 10 healthy subjects (5 male, 5 female); mean age 28.7 ± 1.2 yr (per secondary analyses of this dataset).
- **Modalities/protocol:** Continuous ECG and continuous arterial BP (Finapres), 250 Hz; supine baseline, slow tilt to 75° over 50 s, rapid tilt to 75° over 2 s, standing-up maneuver, return to supine; ~55–74 min per subject; beat annotations provided.
- **Validates for OCPE:** The core healthy-control orthostatic claim — distribution and dynamics of ΔHR, ΔBP, and RR-interval/SBP coupling during tilt and active stand, including initial transient vs steady-state response and tilt-speed dependence. This is the primary ground truth for the "healthy arm" of the orthostatic slice.
- **Limitations:** n=10 only; young healthy cohort; Finapres finger BP; no PPG/EDA/IMU; no pathological (POTS/OH) comparators.

### 1.2 EUROBAVAR dataset — eurobavar.altervista.org
- **Host/access:** Open-access download from the EUROBAVAR site (European Society of Hypertension Working Group on BP and HR Variability); described in Laude et al. 2004.
- **Population:** 21 subjects (17 F / 4 M, mean age 38.4 ± 15 yr): 12 normotensive, 4 healthy, 3 hypertensive, 1 diabetic, 1 heart-transplant; 2 subjects are baroreflex-impaired (diabetic autonomic neuropathy; recent heart transplant).
- **Modalities/protocol:** 3-lead ECG + continuous beat-to-beat finger BP (Finapres/Finometer), 500 Hz, supine and upright (standing), 10–12 min per position; 42 recordings (series A n=8, series B n=13).
- **Validates for OCPE:** Supine→standing shift in HR/BP variability and baroreflex working point; **critically, the two baroreflex-impaired subjects are the closest openly downloadable analogue of a dysautonomia phenotype** for validating "POTS-like" autonomic failure features (attenuated BRS, blunted variability).
- **Limitations:** Small, heterogeneous clinical mix; static supine/standing epochs (no transition dynamics); no wearable modalities.

### 1.3 Two-tiered response of cardiorespiratory-cerebrovascular networks to orthostatic challenge — PhysioNet
- **Host/access:** PhysioNet (physionet.org/content/cardioresp-response-orthostat/), Open Access, DOI 10.13026/73w7-x881.
- **Population:** 10 young healthy adults (9 analyzed).
- **Modalities/protocol:** Continuous ABP (cardiac cycle durations derived), breath-to-breath respiration, transcranial Doppler cerebral blood-flow velocity (both MCAs), NIRS prefrontal total hemoglobin; 30-min seated rest, 1-min stand-up, 1-min sit-down.
- **Validates for OCPE:** The immediate active-stand transient: initial SBP drop (~27 mmHg on stand-up per published Table 1), reflex tachycardia (CCD 824→696 ms), and respiration–HR–BP coupling reorganization. Validates OCPE's stand-up transient model and cardiorespiratory coupling, beyond what PRCP's tilt protocol captures.
- **Limitations:** n≈10; very short stand epochs (1 min) — cannot validate the 10-min sustained orthostatic HR criterion used in POTS diagnosis; no EDA/PPG.

### 1.4 Cerebral Vasoregulation in Diabetes — PhysioNet
- **Host/access:** PhysioNet (physionet.org/content/cerebral-vasoreg-diabetes/), Open Access.
- **Population:** Type 2 diabetes and control subjects (per-subject summary tables provided; exact n not restated here — see GE-71 summary CSV on the record page).
- **Modalities/protocol:** Head-up tilt sessions (Day 1 and Day 2) with ECG, continuous BP, cerebral blood-flow velocity, and supporting clinical variables (labs, medications, comorbidities).
- **Validates for OCPE:** Metabolic-phenotype orthostatic physiology — diabetic autonomic/vasoregulatory impairment vs controls under tilt; also supports the metabolic-disorder claim.
- **Limitations:** Disease cohort with medications/comorbidities (confounded); lab-grade signals, not wearables.

### 1.5 POTS posture/exercise raw dataset — Zenodo (restricted)
- **Host/access:** Zenodo record 20327114 ("Dataset related to article 'Effects of different postures on the hemodynamics and cardiovascular autonomic control responses to exercise in postural orthostatic tachycardia syndrome'"). **Files are restricted — access on request** (sensitive-data justification).
- **Population:** 13 POTS patients + 13 healthy controls.
- **Modalities/protocol:** ECG, respiration, beat-by-beat arterial pressure, VO2 continuously recorded on a cycle ergometer in supine and upright positions, before and during 6-min 50 W exercise.
- **Validates for OCPE:** The single most on-target dataset for a POTS phenotype claim: supine-vs-upright HR excess, reduced vagal modulation, and blunted sympathetic vasomotor control in POTS. **Action: submit an access request early; do not assume availability.**
- **Limitations:** Restricted access; small n; exercise-in-posture rather than classic 10-min stand/tilt protocol.

### 1.6 Autonomic Aging (Jena) — PhysioNet
- **Host/access:** PhysioNet (physionet.org/content/autonomic-aging-cardiovascular/), Open Access, DOI 10.13026/2hsy-t491; Sci Data 2022 descriptor.
- **Population:** 1,121 rigorously screened healthy volunteers, spanning adulthood (supine rest, Jena University Hospital).
- **Modalities/protocol:** ECG (lead II, 1000 Hz) + continuous non-invasive BP (CNAP/Task Force Monitor), 8–45 min (mean ~19 min) supine resting recordings; demographics incl. sex, BMI.
- **Validates for OCPE:** Population-level healthy priors — age/sex/BMI-conditioned distributions of resting HR, HRV (decline with age), BP variability, baroreflex-adjacent metrics. Anchors the "healthy" envelope against which POTS-like slices are compared. (Recorded supine on a tilt table; no upright challenge in the release.)
- **Limitations:** Supine rest only (no orthostatic challenge in shared data); single-center, German cohort; lab equipment.

**Orthostatic POTS-specific open data: honest statement.** No openly downloadable tilt-table/active-stand dataset of diagnosed POTS patients was found in Pass 1. The nearest resources are (a) the restricted Zenodo POTS record above (request access), (b) the 2 baroreflex-impaired EUROBAVAR subjects, and (c) published summary statistics from the POTS literature (e.g., the PSB 2026 Faros-ECG POTS study by Choi et al. reports 66 POTS vs 20 control wearable recordings but the data are not released). For a POTS-like slice, OCPE should combine (a)–(c) rather than claim direct external validation.

---

## 2. ECG (waveform/HRV realism; ambulatory; posture/activity annotation)

### 2.1 MIT-BIH Arrhythmia Database — PhysioNet
- **Host/access:** PhysioNet, Open Access.
- **Population:** 48 half-hour two-channel ambulatory ECG records from 47 subjects, recorded 1975–1979 (Beth Israel Hospital); >100,000 annotated beats.
- **Validates for OCPE:** Beat-level morphology and rhythm realism of ambulatory ECG; annotated arrhythmia ground truth for testing OCPE's beat-detection and rhythm-diversity claims.
- **Limitations:** 1970s Holter technology and era-specific noise; arrhythmia-clinic selection bias; only 30 min per subject; **no posture/activity annotation** — use for waveform realism, not behavioral context.

### 2.2 MIT-BIH Normal Sinus Rhythm Database (nsrdb) — PhysioNet
- **Host/access:** PhysioNet, Open Access.
- **Population:** 18 subjects (5 men 26–45 yr; 13 women 20–50 yr) without significant arrhythmias; ~24 h Holter ECG each.
- **Validates for OCPE:** Healthy long-duration HRV statistics (circadian trends, SDNN/RMSSD distributions) for the healthy synthetic arm.
- **Limitations:** Small n; healthy-only; old recordings; no activity labels.

### 2.3 Fantasia Database — PhysioNet
- **Host/access:** PhysioNet, Open Access.
- **Population:** 40 rigorously screened healthy subjects: 20 young (21–34 yr) and 20 elderly (68–85 yr), balanced by sex.
- **Modalities/protocol:** ECG + respiration, 250 Hz, 120 min supine (watching a film); uncalibrated continuous BP in half of subjects.
- **Validates for OCPE:** Healthy resting ECG/HRV and cardiorespiratory coupling with an explicit age contrast; simultaneous respiration makes it a joint ECG–respiration realism check (e.g., respiratory sinus arrhythmia magnitude by age).
- **Limitations:** Supine only; 1990s-era acquisition (powerline/baseline artifacts present — arguably useful as artifact reference); no wearable context.

### 2.4 Icentia11k Single-Lead Continuous ECG — PhysioNet
- **Host/access:** PhysioNet; license **CC BY-NC-SA 4.0** (non-commercial).
- **Population:** ~11,000 patients (CardioSTAT monitors), continuous single-lead ECG up to ~2 weeks; rhythm annotations.
- **Validates for OCPE:** Long-duration (multi-day) ECG realism: day/night HR patterns, ectopy burden distributions, nonstationarity at scale — things 30-min datasets cannot validate.
- **Limitations:** Non-commercial license restricts downstream OCPE release policies if derived artifacts are shared; patient (not healthy) population; single-lead.

### 2.5 PTB-XL — PhysioNet (context note)
- Large 12-lead clinical ECG dataset (open); useful only if OCPE claims anything about 12-lead morphology. **Not posture-annotated, not wearable** — low priority for the wearable slice; listed to prevent mis-scoping.

**Note on posture-annotated ECG:** true ambulatory ECG with posture labels is essentially only available inside multimodal wearable datasets (PPG-DaLiA, WESAD, ScientISST MOVE chest ECG + accelerometry — see §3/§4). Treat those as the ECG-with-context validators.

---

## 3. PPG (pulse oximetry / wrist PPG with ground truth)

### 3.1 PPG-DaLiA — UCI ML Repository
- **Host/access:** UCI ML Repository (dataset 465-companion; DOI 10.24432/C5Q30B-era record), **CC BY 4.0**; also at University of Siegen. Sensors 2019 descriptor (Reiss et al., DOI 10.3390/s19143079).
- **Population:** 15 healthy subjects (8 F / 7 M), aged 21–55, BMI 20.2–27.6.
- **Modalities/protocol:** Wrist Empatica E4 (PPG 64 Hz, 3-axis ACC 32 Hz, EDA, temperature) + chest RespiBAN (ECG 700 Hz, respiration 700 Hz, ACC); 8 daily-life activities (sitting, stairs, table soccer, cycling, driving, lunch, walking, working) + transitions, ~2.5 h/subject; ECG-derived HR ground truth (8-s windows, 2-s shift); labeled activities.
- **Validates for OCPE:** The single best all-round wearable validator: PPG–ECG coupling (HR error distribution vs activity), motion-artifact dependence on activity type, EDA/temperature wrist dynamics, and cross-device (chest vs wrist) synchrony claims. Directly calibrates the PPG motion-artifact model.
- **Limitations:** n=15; E4-generation wrist PPG (green LED, 64 Hz) — not phone/watch-diverse; healthy young/mid adults only.

### 3.2 BIDMC PPG and Respiration Dataset — PhysioNet
- **Host/access:** PhysioNet (physionet.org/content/bidmc/), Open Access; subset of MIMIC-II matched waveform database.
- **Population:** 53 critically ill adults (ages 19–90+, 32 F), 8-min recordings.
- **Modalities:** ECG, PPG (pulse oximeter), impedance pneumography, all 125 Hz; HR/RR/SpO2 numerics at 1 Hz; **two independent manual breath annotations**.
- **Validates for OCPE:** PPG–respiration modulation realism (baseline wander, amplitude/frequency modulation used for RR estimation) and ICU-grade PPG waveform morphology including low-perfusion variants; SpO2 numerics for plausibility ranges.
- **Limitations:** Critically ill, supine, motion-limited — a *clean-signal* reference, not a wearable-motion one; short segments.

### 3.3 MIMIC-III Waveform Database Matched Subset / MIMIC Waveform Databases — PhysioNet
- **Host/access:** PhysioNet; **credentialed** (CITI "Data or Specimens Only Research" training + signed DUA; approval ~1–2 weeks). A derived **open** benchmark also exists: "A PPG Benchmark Dataset for Cardiorespiratory Analysis" (MIMIC-III-Ext-PPG, physionet.org/content/mimic-iii-ext-ppg/) with 30-s PPG (±ECG/ABP/RESP) segments and metadata.
- **Population:** Tens of thousands of ICU patients (matched subset links waveforms to clinical records).
- **Validates for OCPE:** Scale and diversity of clinical PPG/ECG/ABP/RESP waveforms; pathological waveform families (sepsis, arrhythmia) for the systemic-disorder envelope; co-registered multimodality for cross-channel consistency checks.
- **Limitations:** Credentialed access (not redistributable); bedside-monitor context; no labels of activity/posture; waveform quality highly variable (which is itself usable as a noise reference).

### 3.4 BUT PPG (Brno Smartphone PPG Database) — PhysioNet
- **Host/access:** PhysioNet (physionet.org/content/butppg/), Open Access (CC BY per descriptor).
- **Population:** v1: 48 recordings, 12 subjects (6 F/6 M, 21–61 yr); v2.0.0 adds a second session (records 112001+; 3,840 10-s PPG segments incl. ear + finger, 25 F/25 M records, ages 19–76) with ACC and SpO2/BP/glycaemia spot values.
- **Modalities:** Smartphone-camera PPG (30 Hz), reference 1-lead ECG (Bittium Faros, 1000 Hz), ACC (100 Hz, v2), rest and motion conditions; **expert-consensus binary quality labels + reference HR**.
- **Validates for OCPE:** PPG signal-quality-label calibration — the fraction of 10-s segments deemed unusable at rest vs motion, and smartphone-PPG artifact morphology. Directly validates the missingness/quality-flag sub-model for camera-based PPG.
- **Limitations:** Smartphone PPG (not wrist); short 10-s segments; small subject count.

### 3.5 Stanford / Apple Heart Study-derived open sets
- **Not available.** No open dataset derived from the Apple Heart Study or comparable large consumer-PPG cohorts was identified; treat as a gap (§12).

---

## 4. EDA (electrodermal activity with ground-truth protocols)

### 4.1 WESAD (Wearable Stress and Affect Detection) — UCI ML Repository
- **Host/access:** UCI dataset 465 (DOI 10.24432/C57K5T), CC BY 4.0 (UCI donation terms); also mirrored at University of Siegen.
- **Population:** 15 subjects (12 M / 3 F; mean age 27.5).
- **Modalities/protocol:** Chest RespiBAN @700 Hz: ECG, EDA, EMG, respiration, temperature, 3-axis ACC; wrist Empatica E4: BVP 64 Hz, EDA 4 Hz, temp 4 Hz, ACC 32 Hz. Protocol: baseline (~20 min neutral reading), stress (Trier Social Stress Test: public speaking + mental arithmetic, ~10 min), amusement (~6.5 min), meditation; self-report questionnaires included.
- **Validates for OCPE:** EDA tonic/phasic dynamics under a validated stressor (TSST) at two body sites; cross-modality stress response (HR, HRV, respiration rate, temperature) with protocol-phase ground truth. The reference dataset for OCPE's autonomic-stress claim and for EDA–HR–respiration covariation.
- **Limitations:** n=15, strong male skew; lab protocol; short conditions.

### 4.2 Wearable Device Dataset from Induced Stress and Structured Exercise Sessions — PhysioNet/Zenodo
- **Host/access:** PhysioNet (physionet.org/content/wearable-device-dataset/) and Zenodo record 13993658; Open Access; Sci Data 2025 descriptor (Hongn et al.).
- **Population:** Healthy volunteers aged 18–30: 36 stress sessions, 30 aerobic, 31 anaerobic exercise sessions.
- **Modalities/protocol:** Empatica E4 only (BVP 64 Hz, EDA 4 Hz, skin temp 4 Hz, ACC 32 Hz, IBI/HR); stress protocol with math + emotional tasks interleaved with rest and self-reported stress; aerobic vs anaerobic stationary-bike routines; event tags.
- **Validates for OCPE:** Wrist-only stress and exercise responses at consumer-wearable fidelity — validates the E4-like device model, EDA stress reactivity, and BVP-quality degradation under cycling exercise.
- **Limitations:** No ECG ground truth (IBI is PPG-derived); young adults only; wrist-only.

### 4.3 PPG and EDA dataset for stress assessment (UnivPM, Ancona) — Mendeley Data
- **Host/access:** Mendeley Data (linked from Data in Brief 2024, PMC10847510); open.
- **Population:** 29 subjects (21 M / 8 F), ages 20–60.
- **Modalities/protocol:** Empatica E4 (PPG, EDA, temp, ACC) during a 5-task work-like stress protocol (Lego assembly, mental arithmetic, oral presentation) with rest segments; raw + filtered + analysed data.
- **Validates for OCPE:** Independent replication sample for EDA/PPG stress-response distributions with a wider age range than WESAD.
- **Limitations:** No ECG ground truth; tasks are idiosyncratic; moderate size.

### 4.4 A Non-EEG Dataset for Assessment of Neurological Status — PhysioNet
- **Host/access:** PhysioNet, Open Access (UT Dallas QoL Lab).
- **Population:** 20 healthy subjects.
- **Modalities/protocol:** EDA, temperature, acceleration, HR, SpO2 across physical/emotional/cognitive stress and rest conditions.
- **Validates for OCPE:** Secondary EDA/HR stress-reactivity check with a different device stack and protocol family.
- **Limitations:** Small n; derived HR (not raw ECG); limited documentation compared to WESAD.

---

## 5. Respiration (reference capnography/belt + wearable signals)

### 5.1 CapnoBase (IEEE TBME Respiratory Rate Benchmark) — Borealis Dataverse
- **Host/access:** Borealis Dataverse (doi:10.5683/SP2/NLB8IT), open download.
- **Population:** 42 cases — children and adults during elective surgery/anesthesia, 8-min recordings.
- **Modalities:** PPG, ECG, and **reference capnography** (CO2 waveform) with breath annotations.
- **Validates for OCPE:** The cleanest respiration ground truth: capnography-anchored RR distributions and PPG/ECG respiratory-modulation depth across pediatric and adult physiology.
- **Limitations:** Anesthetized/sedated patients (atypical autonomic state); short segments; not wearable.

### 5.2 BIDMC PPG and Respiration (see §3.2)
- Dual-annotator breath labels on impedance pneumography — validates RR estimation coupling between respiration, PPG, and ECG in awake/ICU-adjacent conditions.

### 5.3 Vortal dataset — King's College London (on request)
- **Host/access:** Shared with academic researchers **on request** (contact research.data@kcl.ac.uk); reported in Charlton et al., Physiol Meas 2016.
- **Population:** 57 healthy volunteers: young (18–39 yr) and elderly (>70 yr).
- **Modalities/protocol:** ECG, PPG (finger/ear), impedance pneumography + **reference oral-nasal pressure**; 10 min supine rest in all; young subjects also walking/running/recovery.
- **Validates for OCPE:** Age contrast in cardiorespiratory coupling with a high-quality respiratory reference, plus exercise-state respiration.
- **Limitations:** Not self-serve (email request); small n per subgroup.

### 5.4 PPG-DaLiA / WESAD chest respiration (see §3.1/§4.1)
- RespiBAN chest respiration (700 Hz) synchronized with wrist PPG/EDA/ACC — validates wearable-context respiratory signals during activity (DaLiA) and stress (WESAD).

---

## 6. Activity / free-living accelerometry

### 6.1 CAPTURE-24 — Oxford Research Archive
- **Host/access:** ORA (doi:10.5287/bodleian:NGx0JOMP5), **CC BY 4.0**; Sci Data 2024 descriptor.
- **Population:** 151 participants (66% women; broad adult age groups), Oxfordshire, 2014–2016 convenience sample.
- **Modalities/protocol:** Axivity AX3 wrist tri-axial accelerometer, 100 Hz, ±8 g, ~24 h each; 3,883 h total, 2,562 h annotated with Compendium of Physical Activities codes (camera + sleep diary ground truth); includes sleep labels.
- **Validates for OCPE:** Free-living IMU realism — activity-type distribution, intensity (mg) distributions, non-wear patterns, day/night activity structure, and accelerometer–posture statistics that drive OCPE's IMU sub-model and its coupling to HR.
- **Limitations:** Accelerometry only (no simultaneous physiological channels); ~24 h per participant; UK convenience sample.

### 6.2 ScientISST MOVE — PhysioNet
- **Host/access:** PhysioNet (physionet.org/content/scientisst-move-biosignals/, DOI 10.13026/hyxq-r919), Open Access; also Zenodo.
- **Population:** 17 healthy volunteers (10 M / 7 F; median age 24); ~10.5 sensor-simultaneous hours total.
- **Modalities/protocol:** Chest band + armband + Empatica E4: dual-view ECG, EDA, PPG, plus EMG, wrist temperature, chest + wrist ACC; annotated everyday activities (lift object, greet, gesticulate, jump, walk, run) in naturalistic settings.
- **Validates for OCPE:** IMU + multimodal physiology during **unscripted daily movement** — validates motion-artifact injection for ECG/EDA/PPG simultaneously and same-modality cross-device signal-quality differences.
- **Limitations:** Small n and short sessions; young cohort.

### 6.3 UK Biobank accelerometry (context)
- ~100k participants with 7-day Axivity wrist data — the population-scale reference, but **application-only with fees (CONTROLLED)**. Use CAPTURE-24 for iteration; cite UK Biobank summary statistics where needed.

---

## 7. Sleep

### 7.1 MESA Sleep (Multi-Ethnic Study of Atherosclerosis) — NSRR
- **Host/access:** sleepdata.org (National Sleep Research Resource) — free with registration + DUA (REGISTERED).
- **Population:** 2,237 adults (45–84 yr; white, Black, Hispanic, Chinese-American) in the sleep ancillary exam; ~2,060 with actigraphy used in published benchmarks.
- **Modalities/protocol:** One night in-home PSG + **7-day wrist actigraphy (Actiwatch Spectrum)** + sleep diary/questionnaires; PSG scored per AASM.
- **Validates for OCPE:** Multi-day actigraphy realism: sleep-wake distributions, night-to-night variability, rest-activity rhythms in a diverse older cohort — validates the multi-day wear and sleep-regularity claims (relevant to ME/CFS/long-COVID sleep-disruption phenotypes at cohort level).
- **Limitations:** DUA required; older cohort; epoch-level actigraphy (not raw 100 Hz acceleration in the standard release).

### 7.2 SHHS (Sleep Heart Health Study) — NSRR
- **Host/access:** sleepdata.org, REGISTERED (DUA).
- **Population:** 6,441 enrolled (age ≥40); 5,804 shared on NSRR; baseline in-home PSG (1995–98), 3,295 with second PSG (2001–03).
- **Validates for OCPE:** Overnight ECG/oximetry/respiration physiology during sleep at scale — nocturnal HR and SpO2 distributions, sleep-disordered-breathing signal families (useful negative/positive contrast for healthy-sleep claims).
- **Limitations:** PSG-era montage, not wearables; DUA; older adults.

### 7.3 Sleep-EDF Expanded — PhysioNet
- **Host/access:** PhysioNet (physionet.org/content/sleep-edfx/), Open Access (ODC-BY/ODbL).
- **Population:** 197 whole-night PSGs: Sleep Cassette — 153 recordings from 78 healthy subjects (25–101 yr); Sleep Telemetry — 44 recordings from 22 subjects with mild sleep-onset difficulty (temazepam study).
- **Modalities:** EEG (Fpz-Cz, Pz-Oz), EOG, chin EMG, event markers; some records include respiration and body temperature; expert R&K hypnograms.
- **Validates for OCPE:** Nocturnal autonomic baseline structure across sleep stages (for ECG/HR + temperature night-time models); healthy vs mildly-disrupted sleep contrast.
- **Limitations:** EEG-centric; wearable-relevant channels (respiration/temp) only in subsets; 1987–1994 recordings.

### 7.4 CAP Sleep Database — PhysioNet
- **Host/access:** PhysioNet (physionet.org/content/capslpdb/), Open Access (ODC-BY).
- **Population/content:** 108 PSG recordings: 16 healthy + pathological groups (insomnia, narcolepsy, RBD, PLM, sleep-disordered breathing, bruxism) with CAP A-phase annotations.
- **Validates for OCPE:** Sleep-pathology contrast set for phenotypic diversity of nocturnal signals (EEG-centric but includes ECG/resp channels in many records).
- **Limitations:** Small per-pathology counts; not wearable.

---

## 8. Autonomic physiology (stress challenges; cold pressor; mental arithmetic)

### 8.1 WESAD (see §4.1) — TSST (public speaking + mental arithmetic) with full multimodal ground truth. Primary validator.

### 8.2 Stress Recognition in Automobile Drivers (DriveDB) — PhysioNet
- **Host/access:** PhysioNet (physionet.org/content/drivedb/), Open Access.
- **Population/protocol:** 17–24 drives (reports differ; at least 16–17 drivers), ≥50-min real-world drives (rest/highway/city) around Boston.
- **Modalities:** ECG, EMG (trapezius), EDA (hand and foot), respiration; ECG 496 Hz (other channels lower).
- **Validates for OCPE:** Field-context autonomic stress response with real motion/noise — tests OCPE's claim that lab-calibrated stress physiology transfers to naturalistic recordings.
- **Limitations:** **Stress ratings are NOT publicly released** (only signal data) — validation must use condition (rest/city/highway) as proxy label; 1990s-era recordings.

### 8.3 SWELL-KW (knowledge-work stress) — Radboud/TNO
- **Host/access:** Dataset site (cs.ru.nl/~skoldijk/SWELL-KW/); historically distributed for research (registration/request via site); HRV-derived feature set also mirrored on Kaggle.
- **Population:** 25 subjects (17 M / 8 F, mean age ~25), ~3 h each of office work under neutral, time-pressure, and interruption conditions.
- **Modalities:** HRV (Mobi ECG-derived), skin conductance, computer logging, Kinect posture, FaceReader; questionnaire ground truth (NASA-TLX, RSME, SAM).
- **Validates for OCPE:** Low-intensity cognitive-stress autonomic signature (mild HRV/EDA shifts) — complements WESAD's high-intensity TSST; relevant to dysautonomia-like orthostatic/cognitive symptom provocation at realistic intensity.
- **Limitations:** Access path is semi-formal (site request); young student-heavy sample.

### 8.4 Cold-pressor datasets
- No open beat-to-beat cardiovascular cold-pressor dataset was confirmed. A review of wearable PPG resources (Charlton & Marozas, PMC7612541) lists a "Pulse transit time during vasoconstriction" dataset (86 subjects, ECG + BP, ~35-min wrist and finger recordings during **cold pressor and active-stand tests**) — a strong lead, but its host and access terms were **not verified** in this pass; confirm before use.
- **Do not confuse with** the **Pulse Transit Time PPG Dataset** on PhysioNet (physionet.org/content/pulse-transit-time-ppg/, OPEN, verified): 22 healthy subjects (6 F; ages 20–53), 66 records of multi-site/multi-wavelength finger PPG (6 channels), 3-lead ECG (500 Hz), IMU (500 Hz), sensor-pressure load cells, sensor temperatures, and SBP/DBP/SpO2/HR numerics across **sitting, walking, running** — its released protocol contains **no cold-pressor arm**. Still useful for PTT/BP-coupling and multi-wavelength PPG realism claims.
- The **EMPA pain dataset** (ECG/EDA/EMG during hand cold-pressor; cited in a 2026 Springer resampling paper) exists but distribution terms are not clearly open — verify before relying on it.
- **Honest gap:** cold-pressor cardiovascular ground truth otherwise must come from published summary statistics.

### 8.5 A Wearable Exam Stress Dataset — PhysioNet
- **Host/access:** PhysioNet, Open Access.
- **Population/protocol:** 10 university students, Empatica E4 during Midterm 1, Midterm 2, Final exams (1.5–3 h sessions) — real-world (not lab) stress.
- **Validates for OCPE:** Ecological validity of stress physiology (long-duration, ambulatory exam stress) vs lab TSST.
- **Limitations:** n=10; no ECG reference.

---

## 9. Exercise physiology (CPET / graded exercise)

### 9.1 Treadmill Maximal Exercise Tests (TMET, University of Málaga) — PhysioNet
- **Host/access:** PhysioNet (physionet.org/content/treadmill-exercise-cardioresp/), Open Access, DOI 10.13026/7ezk-j442.
- **Population:** 992 maximal graded treadmill tests from 857 amateur/professional athletes, ages 10–63 (2008–2018).
- **Modalities/protocol:** Breath-by-breath VO2, VCO2, RR, VE + HR (Mortara 12-lead ECG) + treadmill speed; ramp or step protocols; warmup, maximal effort, walking recovery; ~575k breath-level rows.
- **Validates for OCPE:** The full dynamic range of HR–respiration–ventilation coupling: HR kinetics at onset, linear HR-VO2 slope, ventilatory thresholds, HR recovery — the quantitative heart of OCPE's exercise claim.
- **Limitations:** Athletic population (selection bias toward fit); HR is monitor-derived (not raw ECG waveform); VO2/VCO2/VE missing for 30 tests.

### 9.2 Wearable Device Dataset stress + aerobic/anaerobic exercise (see §4.2)
- Wrist-worn complement to TMET: wearable-fidelity HR/EDA/temp during structured aerobic vs anaerobic cycling.

### 9.3 Wearable-based signals during physical exercises from patients with frailty after open-heart surgery — PhysioNet
- **Host/access:** PhysioNet (DOI 10.13026/mp8k-7p27), Open Access.
- **Population/protocol:** Frail post-cardiac-surgery patients performing physical exercises with wearable signal capture.
- **Validates for OCPE:** Impaired-capacity exercise physiology — the "low-fitness/disorder" end of the exercise response envelope (contrast to TMET athletes).
- **Limitations:** Small clinical cohort; check record page for exact n before quoting.

### 9.4 Wrist PPG During Exercise (Jarchi & Casson) — PhysioNet
- **Host/access:** PhysioNet (physionet.org/content/wrist/), Open Access.
- **Population:** 8 healthy subjects (5 M / 3 F).
- **Modalities:** Wrist PPG (Shimmer 3 GSR+, 256 Hz) + ACC + gyroscope + reference chest ECG; treadmill walk/run, exercise bike low/high resistance (4–10 min bouts).
- **Validates for OCPE:** PPG-under-exercise artifact severity vs ECG truth; complements TROIKA.

### 9.5 TROIKA / IEEE SP Cup 2015 training set
- **Host/access:** Publicly distributed via the authors' (Zhang) site for research; 12 subjects on treadmill at speeds up to 15 km/h, two-channel wrist PPG + ACC + ECG (the SP-Cup release also includes arm-exercise recordings from additional subjects).
- **Validates for OCPE:** Worst-case PPG motion artifact (running) — lower bound of PPG usability the artifact model must reproduce.
- **Limitations:** Informal hosting (link rot risk); small n; exercise-only.

---

## 10. Systemic-disorder phenotypes (ME/CFS, long COVID, POTS, EDS, autoimmune, metabolic)

### 10.1 RECOVER (NIH long COVID) — BioData Catalyst / dbGaP
- **Access:** CONTROLLED. Adult-cohort survey + lab data (>14,600 participants, >92,000 visits at 79 sites) available on NHLBI BioData Catalyst; aggregate exploration is open, **individual-level data require eRA Commons credentials + dbGaP Data Access Request**. Larger data releases (48M datapoints across ~30k adults/children) rolling out on BDC.
- **Validates for OCPE:** Long-COVID phenotyping at cohort level (symptom clusters, labs) — constrains the phenotype priors; **note: wearable/continuous-physiology streams are not the current release focus**.
- **Limitations:** Application timeline (weeks–months); current subset is survey/lab, not waveforms.

### 10.2 All of Us Research Program Fitbit — Researcher Workbench
- **Access:** Registered/Controlled Tier via institutional DURA, identity verification, training, and Data User Code of Conduct; analysis must run in the cloud Workbench. ~59k participants with any Fitbit data (v8 era); minute-resolution HR, steps, sleep + EHR/survey linkage incl. COVID surveys.
- **Validates for OCPE:** Free-living multi-year HR/activity/sleep distributions and their linkage to diagnoses (incl. POTS/long-COVID ICD codes) at population scale — the strongest available constraint on day-level wearable statistics and missingness patterns.
- **Limitations:** Institutional DURA required; no data export (results export only, with disclosure rules); Fitbit-derived metrics, not raw PPG.

### 10.3 Scripps DETECT (Fitbit/Apple/Garmin/Oura; COVID + long COVID follow-up)
- **Access:** No public raw-data release identified. Data collected via MyDataHelps; publications (Nature Medicine 2020; Lancet Digital Health long-COVID follow-up with participants enrolled 2020–2023) report cohort results. Access appears collaboration-based.
- **Validates for OCPE:** Published summary statistics (RHR deviations around infection/vaccination; long-COVID subgroup analyses) can serve as **literature-constraint validation** of infection/illness-response models.
- **Limitations:** Data not downloadable; device-aggregated daily metrics only.

### 10.4 COVID Collab (King's College London / Mass Science, Fitbit + Oura)
- **Access:** Non-profit app-based study; per its FAQ, data are stored for research use but **no public dataset release was identified**. Treat as literature-constraint only unless a collaboration agreement is obtained.

### 10.5 ME/CFS wearable datasets
- **None openly available.** Representative public evidence: the arXiv-documented ME/CFS/long-COVID severity study (MetaMotionS wearable; uptime/HUA/steps) states the dataset is "available from authors upon request" (REQUEST); the Bateman Horne Center UpTime work is published but the underlying data are not openly posted; a UK Biobank CFS-accelerometer biomarker project (ID 41746) used application-only data and is closed.
- **Validates for OCPE:** Only via published distributional summaries (daily uptime, step counts) — a weak, honest validation tier for the ME/CFS activity envelope.

### 10.6 POTS (see §1.5) — Zenodo 20327114 (REQUEST) is the only identified POTS raw dataset; PSB-2026 Faros-ECG POTS cohort (66 POTS / 20 controls) is **not released**.

### 10.7 Metabolic phenotype: Cerebral Vasoregulation in Diabetes (§1.4) — open tilt data in T2D; TMET (§9.1) for fitness/metabolic capacity. EUROBAVAR includes diabetic-autonomic-neuropathy subjects.

### 10.8 EDS / hypermobility and autoimmune/inflammatory phenotypes
- **No public wearable datasets identified** for EDS or for systemic autoimmune disease (e.g., lupus, RA) with continuous physiology. Inflammatory-response modeling can borrow infection-response statistics from DETECT/Oura publications (literature-constraint tier). This is a genuine coverage gap (§12).

---

## 11. Sensor noise / artifact realism (motion artifact, missingness, quality labels)

### 11.1 PPG-DaLiA (§3.1) — activity-labeled wrist PPG with ECG truth: activity-conditional artifact severity and HR-error distributions. Primary artifact calibrator.

### 11.2 BUT PPG (§3.4) — expert binary quality labels (rest vs motion) on smartphone PPG: quality-flag classifier calibration and missingness-rate priors.

### 11.3 CSL Pulse Oximetry Artifact Labels — Borealis Dataverse
- **Host/access:** Borealis (doi:10.5683/SP2/SJAKCB), open download (Karlen, 2021).
- **Content:** Pulse-oximetry PPG with artifact labels (per citation in Sensors 2025 review; inspect the record for exact n/labels before quoting statistics).
- **Validates for OCPE:** Expert-labeled PPG artifact segments — trains/tests OCPE's artifact-class conditional distributions.

### 11.4 ScientISST MOVE (§6.2) — dual-device same-modality recordings in naturalistic motion: empirical cross-device quality degradation curves.

### 11.5 Wrist PPG During Exercise (§9.4) + TROIKA (§9.5) — severe-motion artifact anchors.

### 11.6 PhysioNet/CinC 2015 Challenge (Reducing False Arrhythmia Alarms in the ICU)
- **Host/access:** PhysioNet, Open Access (challenge set).
- **Content:** ICU monitor waveforms (ECG/PPG/ABP) around true/false arrhythmia alarms.
- **Validates for OCPE:** Artifact-driven false-alarm physiology — realistic corruption patterns (leads-off, low perfusion, motion) superimposed on pathological rhythms.
- **Limitations:** ICU context; alarm-centric sampling.

---

## 12. Coverage gaps (no suitable public dataset found — stated honestly)

1. **POTS tilt-table/active-stand raw data (diagnosed cohorts): none openly downloadable.** Only Zenodo 20327114 (13 POTS/13 controls, restricted-request) and unreleased study data. OCPE POTS validation must combine restricted requests + baroreflex-impaired EUROBAVAR subjects + published summary statistics.
2. **ME/CFS raw wearable data:** none open; request-only or application-only sources exist.
3. **Long COVID continuous wearable waveforms:** none open; RECOVER (surveys/labs; controlled), DETECT/COVID Collab (no release), All of Us Fitbit (tiered, aggregate-metric level).
4. **EDS/hypermobility and autoimmune/inflammatory wearable datasets:** none identified at any access level.
5. **Cold-pressor cardiovascular challenge (beat-to-beat):** no confirmed open release.
6. **Consumer-watch PPG at scale (Apple Heart Study, Fitbit Heart Study, Huawei, Garmin):** no open derivatives; All of Us offers only Fitbit-derived metrics, not raw PPG.
7. **Multi-day synchronized full-stack wearable data (ECG+PPG+EDA+resp+temp+IMU) in free living:** not found — longest synchronized multimodal sets are ~2.5 h (PPG-DaLiA); multi-day sets are single-modality (actigraphy/Fitbit metrics). OCPE's multi-day multimodal claim can therefore only be validated piecewise (multi-day statistics from MESA/All of Us × multimodal coupling from DaLiA/WESAD).
8. **Orthostatic challenge with continuous BP in large n:** the only large-n open autonomic set (Autonomic Aging, n=1,121) is supine-rest-only; tilt/stand sets are n≤21.

---

## 13. Recommended validation priority ladder — first OCPE release (healthy vs POTS-like orthostatic slice; ECG/PPG/EDA/resp/temp/IMU)

Ordered by (relevance × accessibility × modality coverage):

1. **Physiologic Response to Changes in Posture (PRCP), PhysioNet, OPEN** — the orthostatic ground truth: beat-to-beat ECG+continuous BP through slow tilt, rapid tilt, and stand-up in 10 healthy adults. Validates ΔHR/ΔBP magnitude, transient vs steady-state time course, and RR–SBP coupling for the healthy arm. *Do this first; it is free and immediate.*
2. **PPG-DaLiA, UCI, CC BY 4.0** — validates the full wearable modality stack against chest-ECG/respiration truth across 8 labeled daily activities: PPG-HR error vs motion, EDA/temp wrist dynamics, IMU-artifact coupling. Anchors artifact realism and multimodal synchrony.
3. **WESAD, UCI, CC BY 4.0** — validates autonomic stress physiology (TSST) across chest+wrist EDA, ECG, PPG, respiration, temperature with protocol ground truth: resting vs stress distributions the POTS-like slice borrows for sympathetic-overdrive parameterization.
4. **EUROBAVAR, open download** — supine vs standing beat-to-beat ECG+BP including 2 baroreflex-impaired (dysautonomia-analogue) subjects; the only open path to validating attenuated baroreflex / blunted-variability claims in the POTS-like arm.
5. **Autonomic Aging (Jena, n=1,121), PhysioNet, OPEN** — population priors: age/sex-conditioned resting HR, HRV, and BP distributions to certify that OCPE's healthy cohort sits inside the real human envelope before any disorder perturbation is judged.

**Parallel restricted-access track (start applications now; they gate the POTS claim):** Zenodo 20327114 (POTS posture/exercise; request), RECOVER on BioData Catalyst (dbGaP DAR), All of Us Fitbit (institutional DURA). Until these clear, present POTS-like validation as "impaired-autonomic proxies + published-statistics constraints," not direct cohort validation.

**Second release (exercise + sleep + multi-day):** TMET-Málaga (exercise dose-response), MESA/SHHS via NSRR DUA (sleep + 7-day actigraphy), CAPTURE-24 (free-living IMU), Icentia11k (multi-day ECG, non-commercial), BUT PPG + CSL artifact labels (quality/missingness model).
