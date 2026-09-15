# OCPE — Neurological & Systemic-Autonomic Physiology: Evidence Base (Pass 1 Discovery)

**Scope:** Determine which neurological/systemic-autonomic physiology belongs in OCPE CORE (healthy-reference + generic perturbation machinery) vs phenotype-specific perturbation layers; classify wearable-observable vs latent-only variables.

**Evidence scale:** E0 hypothesis · E1 mechanistic (animal/in vitro/physiological rationale) · E2 observational human · E3 controlled human experimental · E4 replicated quantitative (multiple controlled/consistent quantitative human studies) · E5 meta-analysis / consensus.

**Citation discipline:** DOIs/PMIDs are given only where directly observed in the retrieved source text; otherwise the stable identifier (PMC ID / PubMed URL) is given and DOI is marked "not captured" rather than fabricated. Magnitudes are quoted with n and SD/CI where the source reported them.

---

## 1. PARKINSON'S DISEASE (PD)

### Claim PD-1: Cardiac sympathetic denervation is a core, quantifiable feature of PD
- **Condition:** Parkinson's disease | **Domain:** cardiac autonomic (sympathetic noradrenergic) | **Variable:** myocardial sympathetic innervation (123I-MIBG heart/mediastinum ratio; surrogate: blunted HRV, blunted pressor responses)
- **Mechanism:** Postganglionic cardiac sympathetic neurodegeneration (α-synuclein) → reduced myocardial norepinephrine uptake → denervation precedes/parallels motor disease.
- **Direction:** Reduced MIBG uptake (denervation). | **Magnitude:** Across 54 studies, 3114 PD patients (mean Hoehn & Yahr 2.5): mean early H/M ratio 1.70, delayed 1.51 vs pooled cutoffs ~1.89/1.86. Diagnostic sensitivity 0.81 (early) / 0.83 (delayed); specificity 0.86 / 0.80. In early PD (<3 y): sensitivity 68.7%, specificity 91.7% (n=600, 272 PD).
- **Timescale:** Progressive over years; detectable in early/prodromal disease.
- **Population:** PD, mean age ~65-70, H&Y ~2.5.
- **Wearable modality+signal:** **Latent only** — MIBG itself is scintigraphy. Wearable correlates = reduced HRV (PD-3), blunted orthostatic HR response, reduced BP overshoot in Valsalva. No direct wearable measure of denervation density exists.
- **Evidence level:** E5 (meta-analysis-level pooling of 54 studies) + E4 (Kawazoe n=600).
- **Source:** Comprehensive MIBG review, PMC10605004 (DOI not captured); Kawazoe et al., J Neurol Sci 2019, DOI 10.1016/j.jns.2019.07.027, PMID 31706063.
- **Supporting:** Consistent across dozens of cohorts; distinguishes PD/DLB (reduced) from MSA (usually preserved postganglionic cardiac innervation) with specificity 0.70–0.95.
- **Contradictory/null:** Normal MIBG does NOT exclude PD (esp. early; sensitivity only ~69% in first 3 years). 44% of MSA phenotypes showed discordant MIBG in one series (confounds: cardiac disease, medications, autonomic neuropathy).
- **Limitations:** H/M ratio is a lab biomarker, not a wearable signal; heterogeneity in cutoffs.
- **Implementation:** **Perturbation (PD phenotype)** — model as a latent parameter (cardiac noradrenergic gain ↓) that drives wearable-visible downstreams: blunted HRV, blunted orthostatic HR rise, OH.
- **Validation:** Synthetic PD cohorts should reproduce (a) lower RMSSD/SDNN vs matched controls, (b) ΔHR/ΔSBP <0.5 in the nOH sub-phenotype, (c) no direct "MIBG channel."

### Claim PD-2: Orthostatic hypotension affects ~30% of PD patients (consensus definition ≥20/≥10 mmHg within 3 min)
- **Condition:** PD | **Domain:** cardiovascular autonomic | **Variable:** orthostatic systolic/diastolic BP drop
- **Mechanism:** Peripheral sympathetic vasomotor failure → impaired vasoconstriction + splanchnic pooling on standing; compounded by levodopa (PD-5) and supine hypertension.
- **Direction:** BP falls on standing. | **Magnitude:** Pooled point prevalence 30.1% (95% CI 22.9–38.4%), 25 studies, random-effects meta-analysis; individual studies 9.6–64.9%; largest community cohort (n=3414) 10.6%. Subgroup estimates 25–38%. About 1/3 of patients with ≥60 mmHg SBP drops on tilt are asymptomatic.
- **Timescale:** Drop develops within 3 min of standing (delayed OH up to 10+ min in a subset); chronic, worsens with disease duration and dopaminergic load.
- **Population:** PD, mostly age 65–75, mixed disease duration.
- **Wearable modality+signal:** **Partially wearable-observable** — cuffless/ambulatory BP is not continuous on consumer wearables; proxy signature = posture transition (IMU) + attenuated HR rise (PPG/ECG) + (in severe cases) near-syncope falls. Continuous PPG pulse-wave features track BP directionally but not calibrated mmHg.
- **Evidence level:** E5.
- **Source:** Velseboer et al., systematic review/meta-analysis, PMC5199613 (DOI not captured).
- **Supporting:** nOH consensus definitions (≥20 SBP or ≥10 DBP within 3 min; ≥30 SBP if supine hypertension) — consensus statement (E5).
- **Contradictory/null:** Extreme heterogeneity (I² 79–98%) driven by setting (tertiary vs community), OH definition, and standing time; the 10.6% community estimate suggests clinic-based prevalence is inflated.
- **Limitations:** Pre-2010 literature; few population cohorts.
- **Implementation:** **Perturbation (PD phenotype), built on CORE orthostatic reflex model.** OCPE core should already model the normal baroreflex orthostatic response (HR +10–25 bpm, BP maintained); PD/MSA/PAF perturbations degrade peripheral vasomotor gain and HR compensation to different degrees.
- **Validation:** Simulate posture transitions; PD phenotype should show consensus-defined OH in ~30% of virtual patients, with distribution matching the 22.9–38.4% CI, and blunted ΔHR/ΔSBP.

### Claim PD-3: Resting HRV is reduced in PD (parasympathetic/vagal and total variability), possibly pre-motor
- **Condition:** PD | **Domain:** cardiac autonomic | **Variable:** RMSSD, SDNN (resting/ambulatory)
- **Mechanism:** Cardiac vagal + sympathetic denervation and central autonomic network degeneration.
- **Direction:** Decreased. | **Magnitude:** ARIC prospective cohort (n=12,162; 78 incident PD over 18 y): PD cases rMSSD 22.8±13.8 ms vs non-PD 29.2±23.4 ms; SDNN 32.2±13.6 vs 37.2±19.7 ms; bottom-quartile rMSSD HR 2.1 (1.0–4.3), SDNN HR 2.9 (1.4–6.1) for incident PD. Mean RR interval, LF, HF, LF/HF NOT associated.
- **Timescale:** HRV reduction detectable years before motor diagnosis (prodromal marker).
- **Population:** Community cohort, baseline age ~54.
- **Wearable modality+signal:** **Wearable-observable (ECG/PPG HRV)** — RMSSD/SDNN are standard wearable outputs; confounded by age, activity, AF, diabetes.
- **Evidence level:** E2 (single large prospective cohort) + supporting cross-sectional E2/E3 literature (reduced HRV vs controls, consistent direction).
- **Source:** ARIC analysis, PMC4529999 (DOI not captured).
- **Supporting:** Cross-sectional studies consistently show reduced time- and frequency-domain HRV in PD vs controls; recent controlled study (n=102 PD, 10 iRBD, 43 HC) found no difference in resting HR/SBP but reduced ΔSBP-HUT and lower HRV in sympathetic-dominant states (SciDirect S1353802024010320, DOI not captured).
- **Contradictory/null:** Cardiovascular Health Study (n=1587, 44 incident PD): HRV NOT associated with PD risk — direct null replication attempt. Effect sizes are modest; discriminative value at individual level is poor.
- **Limitations:** 2-min ECG in ARIC; incident-PD misclassification; comorbidity confounding (DSP, diabetes lower HRV independently — PMC10354718).
- **Implementation:** **Perturbation (PD phenotype)** — modest downward shift of RMSSD/SDNN distributions (~15–25% relative reduction), NOT a core change. Low HRV is shared with anxiety/pain/aging — explicitly a cross-phenotype confound axis in OCPE.
- **Validation:** Distribution-level (not individual-level) separation; verify overlap with anxiety and chronic-pain perturbation layers is realistic (all reduce vmHRV with g ≈ −0.3 to −0.6).

### Claim PD-4: Isolated REM sleep behavior disorder (iRBD) is detectable by wrist actigraphy and is a prodromal synucleinopathy state
- **Condition:** iRBD → PD/DLB/MSA prodrome | **Domain:** sleep motor behavior | **Variable:** abnormal movement during REM sleep; rest-activity rhythms
- **Mechanism:** Loss of REM atonia (pontine/subcoeruleus degeneration) → dream-enactment movements.
- **Direction:** Increased sleep-period movement. | **Magnitude/detection:** Multicenter validation (352 iRBD, 258 non-RBD, 4 centers, 3 device types): sleep-feature ML model AUC 0.838–0.865 across centers/devices (Axivity 50–100 Hz down to 30–60 s epoch actigraphs); sensitivity 63.2–90.0%, specificity 64.0–90.2%; rest-activity-rhythm model poor (AUC 0.52–0.82, not generalizable). Two-stage screening with prodromes (RBD symptoms, hyposmia, constipation, OH) raises specificity to 95–100% at cost of sensitivity. Single-site high-resolution model: AUC 0.916–0.954; another home study 95.2% sensitivity / 90.9% precision.
- **Timescale:** iRBD precedes phenoconversion by years; conversion 6.3%/yr, 73.5% by 12 y (Postuma 2019, n=1280); meta-analytic 33.5% at 5 y, 96.6% at 14 y.
- **Population:** iRBD, mean age ~65, ~65–75% male.
- **Wearable modality+signal:** **Wearable-observable (IMU/actigraphy)** with demonstrated accuracy (above); resolution ≥30 s epochs sufficient; needs ≥7 nights.
- **Evidence level:** E4 (multicenter external validation, replicated).
- **Source:** PMC12572274 (actigraphy multicenter, DOI not captured); nature.com s41746-026-02412-z; phenoconversion review PMC12831559; Byun et al. PMC11701292.
- **Supporting:** Convergent across device brands and continents.
- **Contradictory/null:** RAR/circadian features do NOT generalize (socioeconomic/cultural confounds). Real-world PPV collapses at 1.5% population prevalence (adjusted PPV as low as 3–9% actigraphy-only) — base-rate problem for screening claims.
- **Limitations:** Retrospective; cohort heterogeneity; prodromal (sub-PSG-threshold) RBD not captured.
- **Implementation:** **Perturbation (synucleinopathy prodrome / RBD phenotype)** — CORE sleep machinery must support REM-stage movement bursts (normally atonic). RBD = increased REM-period IMU event density/amplitude. Also a CORE-relevant confound: normal sleep movement vs pathological.
- **Validation:** Synthetic nights scored by published actigraphy feature pipelines; target AUC-band 0.84–0.92 when a classifier is trained on the synthetic data vs sleep-disorder controls.

### Claim PD-5: Levodopa acutely lowers BP and worsens/induces OH
- **Condition:** PD (medication effect) | **Domain:** cardiovascular autonomic / pharmacological | **Variable:** supine & orthostatic BP, OH incidence
- **Mechanism:** Peripheral vasodilation (renal beds), inhibition of postganglionic catecholamine release, reduced peripheral resistance; possible central hypotensive effect.
- **Direction:** BP decreases ~60 min post-dose (peak plasma). | **Magnitude:** n=164 parkinsonism patients, HUTT pre vs 60 min post 100/25 mg levodopa/DCI: supine SBP 135→126 mmHg, HR 66→63 bpm; 3-min tilt ΔSBP −2 → −11 mmHg; OH prevalence 22% → 38% (p<0.001); supine hypertension 44% → 28%. Risk of LD-induced/worsened OH strongly predicted by pre-existing neurogenic OH (OR 36, CI 10–131) and abnormal Valsalva (absent overshoot OR 9; abnormal ratio OR 6).
- **Timescale:** Onset within ~60 min of dose; possibly prolonged; repeats with each dose (chronic daily patterning).
- **Population:** Chronic levodopa-treated PD + atypical parkinsonism.
- **Wearable modality+signal:** Proxy — post-dose timing windows of increased OH events / reduced BP proxy, detectable via posture-PPG patterns + medication log.
- **Evidence level:** E3 (large standardized acute challenge; no placebo arm).
- **Source:** PMC11235727 (Eur J Neurol 2024, DOI not captured).
- **Supporting:** Mechanistic basis (E1) well described; earlier small acute studies (Sénard 1995, Noack 2014) same direction.
- **Contradictory/null:** A prior review failed to show conclusive LD→OH relationship when OH was recorded only as an adverse event — measurement-method sensitivity issue, not absence of effect.
- **Limitations:** Not placebo-controlled; single low dose; real-world doses higher (effect likely underestimated).
- **Implementation:** **Perturbation (PD phenotype — medication module)** — time-locked vasodepressor effect ~30–90 min post-dose; mandatory for realistic PD synthetic data since nearly all PD patients are medicated.
- **Validation:** Virtual levodopa dosing schedule should shift simulated OH prevalence from ~22% to ~38% in the PD-nOH subpopulation.

### Claim PD-6: PD motor signatures (rest tremor 4–6 Hz, bradykinesia, gait) are IMU-detectable
- **Condition:** PD | **Domain:** motor | **Variable:** wrist/hand acceleration spectral power, movement speed/amplitude, gait cadence
- **Mechanism:** Basal ganglia dopamine depletion → oscillatory rest tremor (classically 4–6 Hz), reduced movement amplitude/speed, shuffling gait, freezing.
- **Direction:** New spectral peak at 4–6 Hz; reduced movement amplitude. | **Detection accuracy (replicated quantitative):** Smartwatch/IMU classifiers: PD vs healthy balanced accuracy >80%, precision/recall >0.90 in several studies; A-WEAR bracelet 91.7% (k-NN); resting tremor binary detection 97% accuracy (accelerometer alone, n=6, 8 weeks); tremor severity vs UPDRS-III Spearman ρ=0.81; free-living action/rest tremor AUC 0.71–0.76 (less good). Accelerometer sampling ≥30 Hz required for tremor.
- **Timescale:** Tremor intermittent (minutes-long episodes); gait/bradykinesia continuous; fluctuations track medication ON/OFF cycles (~hours).
- **Wearable modality+signal:** **Wearable-observable (IMU ≥30 Hz)** — the single most wearable-validated signal in this entire document.
- **Evidence level:** E4 (many independent device studies; consistent).
- **Source:** Review PMC9863142; Springer chapter 10.1007/978-3-031-96899-0_26; MDPI Sensors 25(14):4313.
- **Supporting:** Convergent across devices, algorithms, settings.
- **Contradictory/null:** Free-living accuracy drops markedly (AUC ~0.71, sens 72–96%/spec 62–71%); small samples (n=6–42) dominate; essential tremor confusion common.
- **Limitations:** Lab > free-living; device placement matters.
- **Implementation:** **Perturbation (PD phenotype)** — inject 4–6 Hz wrist oscillation with realistic intermittency + amplitude envelope; bradykinesia as reduced IMU amplitude; ON/OFF modulation. Not core.
- **Validation:** Spectral peak detection, tremor-vs-voluntary-movement classifier benchmarks, ON/OFF label recovery.

---

## 2. PURE AUTONOMIC FAILURE (PAF) & MULTIPLE SYSTEM ATROPHY (MSA)

### Claim AF-1: MSA/PAF produce severe neurogenic OH with magnitude far exceeding PD — extreme-contrast phenotype
- **Condition:** MSA, PAF | **Domain:** cardiovascular autonomic | **Variable:** orthostatic SBP/DBP drop
- **Mechanism:** MSA = preganglionic/central sympathetic failure (intermediolateral column, medullary catecholaminergic neurons); PAF = postganglionic noradrenergic denervation with low supine plasma norepinephrine (MSA: normal supine NE).
- **Direction:** BP fall on standing. | **Magnitude:** MSA cohort n=444: mild OH defined 20–30/10–15 mmHg, severe OH ≥30/≥15 mmHg within 3 min; severe-OH subgroup disproportionately male, MSA-C, with supine hypertension. Documented individual drops: SBP 160→75 mmHg in <3 min (MSA case, NEJM-linked). Symptomatic OH in MSA associated with upright mean BP <80 mmHg (PD: <75 mmHg). PAF: severe nOH with ≥30 mmHg drops typical (trial inclusion criteria).
- **Timescale:** Drop within 1–3 min; delayed OH exists; progressive.
- **Wearable modality+signal:** Proxy (as PD-2): posture-transition + blunted/absent HR rise + falls; near-syncope events.
- **Evidence level:** E2/E4 (large cohort + consistent clinical-physiology literature).
- **Source:** PMC10741317; Springer 10.1007/s10286-022-00871-4; SciDirect S1353802024010320 (symptom threshold); Low's comparison table (U Toledo guide, authority NA — treat as E1/E2 teaching summary).
- **Supporting:** Consensus definitions and management literature (E5-level consensus on nOH).
- **Contradictory/null:** OH magnitude depends on baseline supine BP (supine hypertension inflates Δ); absolute upright BP, not Δ, drives symptoms in MSA.
- **Implementation:** **Perturbation (MSA/PAF phenotypes)** — these are the high-severity anchors of the nOH spectrum; contrast explicitly against POTS (tachycardic, preserved vasomotor) in the dysautonomia layer.
- **Validation:** ΔHR/ΔSBP <0.5 (usually <0.3) in virtual MSA/PAF; upright MAP <80 mmHg threshold reproduces symptom correlation.

### Claim AF-2: Orthostatic HR response is blunted in neurogenic OH — ΔHR/ΔSBP <0.5 is diagnostic
- **Condition:** nOH (PD/MSA/PAF) | **Domain:** cardiac autonomic | **Variable:** ΔHR/ΔSBP ratio on standing/tilt
- **Mechanism:** Baroreflex failure — sympathetic cardioacceleration cannot mount.
- **Direction:** Attenuated HR rise per mmHg BP fall. | **Magnitude:** Ratio <0.5 bpm/mmHg = neurogenic: sensitivity 91%, specificity 88% (Norcliffe-Kaufmann 2018, synucleinopathy autonomic failure cohort). Most nOH patients <0.3; normal autonomic response >0.5–1.0. Pilot neurodegenerative cohort: ratio 0.04 (3 min) / 0.21 (10 min).
- **Wearable modality+signal:** **Wearable-estimable in principle** — PPG/ECG HR is wearable; BP denominator needs cuff or calibrated PPG-BP. With posture IMU + HR, a "blunted compensation index" is computable even without absolute BP.
- **Evidence level:** E4 (widely cited, replicated in clinical practice; n for original study moderate).
- **Source:** PMID 29405350 (Norcliffe-Kaufmann 2018, DOI not captured); CCJM 89(1):36 review.
- **Contradictory/null:** Ratio invalid when SBP drop is small (denominator noise); affected by chronotropic drugs (beta-blockers), age.
- **Implementation:** **CORE mechanism (baroreflex HR compensation law) with phenotype-specific gain parameter.** The normal gain (>0.5–1.0) belongs in core; nOH phenotypes set gain <0.3; POTS sets HR gain exaggerated.
- **Validation:** Standing simulations across phenotypes; check ratio distributions separate nOH vs POTS vs healthy.

### Claim AF-3: Neurogenic supine hypertension coexists with nOH in ~half of patients (PAF up to 70%)
- **Condition:** MSA/PAF/PD with nOH | **Domain:** cardiovascular | **Variable:** supine BP ≥140/90 (mild 140–159, moderate 160–179, severe ≥180/≥110)
- **Mechanism:** Residual sympathetic tone (MSA), denervation supersensitivity, baroreflex failure; pressure natriuresis at night → morning worsening of OH.
- **Direction:** Supine BP elevated; nocturnal non-dipping/reverse dipping. | **Magnitude:** nSH prevalence: PD 21–46%, MSA ~50%, PAF up to 70%; ~50% of cOH/nOH populations overall. MSA cohort (n=444): SH in 15% of no-OH, 33% of mild-OH, 55% of severe-OH subgroups. Levodopa acutely reduces SH prevalence (44%→28%).
- **Wearable modality+signal:** Partially observable — nocturnal PPG-BP proxy + absent nocturnal HR/BP dipping pattern; recumbent posture from IMU.
- **Evidence level:** E4 (multiple consistent cohorts + reviews).
- **Source:** PMC7943503; PMC12746785; PMC10741317.
- **Contradictory/null:** Definitions vary (140/90 vs 150–180/≥90) → prevalence instability.
- **Implementation:** **Perturbation** — inverted circadian BP pattern is a distinctive, simulation-friendly signature (reverse dipping) vs healthy core (10–20% nocturnal dip).
- **Validation:** 24-h ABPM-like synthetic profiles: nSH phenotypes show supine ≥140/90 with upright hypotension — the "seesaw" pattern.

### Claim AF-4: MSA causes severe progressive anhidrosis (thermoregulatory failure)
- **Condition:** MSA (>PD/DLB) | **Domain:** sudomotor / thermoregulation | **Variable:** % body anhidrosis (TST), QSART
- **Mechanism:** Predominantly preganglionic (47%) or mixed (41%) sudomotor denervation; α-synuclein in autonomic pathways; sweat-gland denervation late.
- **Direction:** Reduced/absent sweating. | **Magnitude:** n=232 MSA (Mayo): TST abnormal 95%; mean anhidrosis 53.7%±34.8% (MSA-P 57% > MSA-C 48%); 64% had >40% anhidrosis; progression +6.2%/year; autopsy-proven subgroup mean 69%±29%. Clinical heat intolerance/heat-stroke risk. Only 16% spontaneously report sweating symptoms (under-recognized).
- **Wearable modality+signal:** **Partially wearable-observable** — EDA (skin conductance) is a sudomotor signal: MSA patients show blunted EDA responses + reduced EDA tonic level; skin temperature + heat-stress response abnormal. Continuous mapping of body-region anhidrosis is NOT wearable.
- **Evidence level:** E4 (large standardized single-center cohort; consistent with literature review: mean anhidrosis ~65% in MSA vs PD/DLB).
- **Source:** Coon et al., PMID 27859565 (PMC5483990); Physiol Rev 10.1152/physrev.00047.2021.
- **Contradictory/null:** A few autopsy-confirmed MSA had ≤5% anhidrosis — normal sweating does not exclude MSA.
- **Implementation:** **Perturbation (MSA phenotype)** — blunted EDA gain + impaired heat-dissipation response; creates a useful **contrast** vs POTS/anxiety (hyper-EDA) and vs stress CORE physiology. EDA gain belongs in CORE (healthy sudomotor/arousal response).
- **Validation:** EDA response amplitude to standard arousal stimuli in synthetic MSA ≪ healthy; heat-exposure scenarios show blunted sweat/EDA and exaggerated core-temp proxy rise.

### Claim AF-5: MSA sleep-disordered breathing: stridor 13–42%, OSA ~15–37%, pooled SRBD ~60%
- **Condition:** MSA | **Domain:** respiratory/sleep | **Variable:** AHI, stridor presence, SpO2 nadir
- **Magnitude:** Pooled SRBD prevalence 60.5% (95% CI 43.2–76.5%; 295 patients, 10 studies, meta-analysis); Asia 79% vs Europe 42%; stridor 13–42% (life-threatening; survival impact); MSA with SRBD: min SpO2 83.9% vs 90.3% without. RBD in up to 90–100% of MSA.
- **Wearable modality+signal:** SpO2 (PPG oximetry), respiratory rate (PPG/IMU), snore/stridor (audio — out of typical wearable scope), cyclical HR.
- **Evidence level:** E5 (meta-analysis) for SRBD prevalence; E2 for stridor.
- **Source:** Frontiers Neurol 2024 10.3389/fneur.2024.1440932; PMC6175796; Parreira 2021 (sighs, SciDirect S1389945720305633).
- **Implementation:** **Perturbation (MSA)** built on **CORE OSA/sleep-breathing machinery** (see §6). Stridor itself: deferred (audio domain).
- **Validation:** Pooled-prevalence band reproduction; SpO2 nadir distributions.

---

## 3. EPILEPSY

### Claim EP-1: Ictal tachycardia is an early, wearable-detectable autonomic seizure component
- **Condition:** Focal & generalized epilepsy | **Domain:** cardiac autonomic | **Variable:** ictal HR rise
- **Mechanism:** Ictal involvement of autonomic networks (insula/amygdala) → early sympathetic surge; usually NOT secondary to motor activity (only 6% late-onset in one series).
- **Direction:** HR increases. | **Magnitude/detection:** Wrist PPG detected ictal tachycardia (≥20% rise or >100 bpm) in 37/62 (60%) focal seizures with ECG-proven IT (n=28 patients); PPG-ECG temporal agreement <10 s in 30/37; mean IT onset only 5.0 s after EEG onset — i.e., effectively seizure-synchronous. GTCS: preictal HR 80.9±17.5 → peak postictal 149.2±19.1 bpm (70 patients, 181 GTCS).
- **Wearable modality+signal:** **Wearable-observable (PPG/ECG HR)**; motion artifact is the main failure mode (still 60% detection even with limb movements).
- **Evidence level:** E4 (multiple EMU studies, consistent).
- **Source:** PMC8470979 (PPG IT); PMC4783192 (Epilepsia 2016, DOI 10.1111/epi.13312).
- **Contradictory/null:** ~40% of IT seizures missed by wrist PPG (signal quality); not all seizures produce IT — HR-based detection alone has ceiling.
- **Implementation:** **Perturbation (epilepsy phenotype)** — event injector: rapid HR surge (20–80 bpm over ~5–30 s), with/without convulsive IMU, followed by postictal recovery (below). Requires CORE capacity for fast autonomic transients.
- **Validation:** Published detection pipelines (20%-or-100-bpm rule; HRV-ML) run on synthetic events should reproduce ~60% PPG detection band and higher ECG-band performance.

### Claim EP-2: Multimodal wearable (EDA + ACC ± PPG/HR) detects convulsive seizures with high sensitivity and low false-alarm rates
- **Condition:** Epilepsy (GTCS/focal motor) | **Domain:** multimodal wearable detection | **Variable:** EDA surge + rhythmic acceleration + HR
- **Magnitude/detection (replicated):** Poh 2012 (Empatica E-series, 80 participants, 4213 h): 94% sensitivity (15/16 GTCS), 0.74 FA/day. Onorati 2017 (69 participants, 6 sites, 5928 h, 55 convulsive seizures): best model sensitivity 94.55%, FAR 0.2%(/day). Regalia 2019 (manufacturer review): sensitivity 92–100%, inpatient FA fell from ~2.0/day to 0.2–1.0/day. Onorati 2019 (n=152): pediatric 92% sens / 1.26 FA/24h; adult 94% / 0.57 FA/24h. Böttcher (E4, ACC+EDA, gradient boosting): test sensitivity 91%, 0.37 FA/24h expanded set. Nasseri (E4, LSTM, ACC+BVP+EDA+TEMP+HR): AUC 0.98, motor seizures 93% sens / 2.3 FA/day; ALL seizure types only 47% sens / 7.2 FA/day. Yu (CNN, n=166): ACC+BVP sens 77–84%, FPR 32–35%, delay ~26 s. Pooled meta (TCS): sensitivity ~89.9%, FAR ~1.43/24h.
- **Wearable modality+signal:** **Wearable-observable (EDA + IMU + PPG)** — the most clinically validated wearable-neurology application; FDA-cleared device exists (Embrace2).
- **Evidence level:** E4→E5 (pooled estimates exist).
- **Source:** PMC13006280 (AI wearable seizure review, DOI not captured); PMC10839362 (cardiac seizure detection feasibility); Frontiers fBioE 2026 meta (10.3389/fbioe.2026.1833080); insurance-policy compilations quoting Poh 2012/Onorati 2017/Regalia 2019 (verify primary DOIs before implementation).
- **Contradictory/null:** Non-convulsive/non-motor seizures perform far worse (47% sens, high FA); SmartWatch (arm EMG-ish) detected only 16% overall, 31% of GTCS — device/algorithm heterogeneity is large; manufacturer-affiliated reports need independent confirmation.
- **Implementation:** **Perturbation (epilepsy phenotype)** — GTCS event = IMU rhythmic burst + large EDA surge + HR surge (EP-1) + postictal suppression (EP-3). False-alarm realism requires CORE to generate confounders: exercise, stress surges, clapping — this is why stress CORE (§7) matters.
- **Validation:** Train a published-style ACC+EDA classifier on synthetic GTCS vs synthetic stress/exercise; target sens ≥90%, FA ≤1/24h band; explicitly measure confusion between panic (§5) and seizure events.

### Claim EP-3: Peri/postictal respiratory and oxygen abnormalities are quantified and severe (SUDEP-relevant)
- **Condition:** Epilepsy (GCS) | **Domain:** respiratory/autonomic | **Variable:** SpO2 nadir, desaturation duration, ETCO2, apnea
- **Magnitude:** All 30 analyzed GCS had peri-ictal SpO2 <90%; mean nadir 52.6±21.4% (median 58.5, range 6–80%); mean desaturation 138±83 s; postictal CO2 elevation 409±188 s (Sainju et al., Epilepsia 2023, DOI 10.1111/epi.17691). Independent cohort (181 GTCS): SpO2 nadir 74±11%, desat 100.6±91.2 s, ETCO2 37.0±7.1 → peak 58.9±14.5 mmHg, apnea 75.7±34.9 s, postictal RR 29.6±4.3/min; postictal immobility mean 167 s, longer with PGES and severe respiratory dysfunction.
- **Wearable modality+signal:** **Wearable-observable (SpO2 via PPG oximetry, respiration, HR)** — directly simulatable in OCPE.
- **Evidence level:** E4 (two consistent EMU cohorts with full quantitative cardiorespiratory capture).
- **Source:** DOI 10.1111/epi.17691; PMC4783192 (DOI 10.1111/epi.13312).
- **Contradictory/null:** EMU setting with rapid intervention — real-world recovery may be slower; nadir distributions wide (6–80%).
- **Implementation:** **Perturbation (epilepsy phenotype)** — GTCS event includes SpO2 dip (nadir distribution ~53–74%±20), CO2 rise, possible central apnea, postictal tachycardia persisting minutes.
- **Validation:** Synthetic SpO2 traces vs EMU summary stats (nadir, duration); classifier-based hypoxemia detection.

---

## 4. MIGRAINE

### Claim MI-1: Interictal autonomic dysfunction in migraine is real but small-to-moderate; HRV findings are inconsistent
- **Condition:** Migraine (interictal) | **Domain:** autonomic | **Variable:** standard autonomic test battery (deep breathing, Valsalva, orthostatic 30:15, isometric handgrip), vmHRV
- **Direction:** Reduced cardiovagal and sympathetic test responses. | **Magnitude:** Meta-analysis (7 studies; 424 migraine vs 268 controls, standardized Novak-protocol tests): deep breathing g=−0.32 (−0.48,−0.16); orthostatic challenge g=−0.28 (−0.44,−0.13); isometric challenge g=−0.55 (−0.71,−0.39); Valsalva ratio MD=−0.17 (−0.23,−0.10). vmHRV meta (Koenig 2016, headache disorders): RMSSD g=−0.63 (−1.24,−0.02), k=6; HF-HRV only reduced when breathing controlled (g=−0.30). Ictal period: SDNN 56.9±22.1 vs 135.8±35.2 (n=18+18 cross-sectional — likely includes methodological differences; treat cautiously).
- **Wearable modality+signal:** **Wearable-observable (HRV)** but effect is small → population-level shift only; individual discrimination poor.
- **Evidence level:** E5 (two meta-analyses) with internal contradiction (below).
- **Source:** Pavelić et al. 2024, DOI 10.1186/s10194-024-01758-7; Koenig et al. 2016, DOI 10.1177/0333102415583989, PMID 25962595.
- **Contradictory/null:** Lee et al. 2019 ECG meta-analysis: NO significant difference in RMSSD, SDNN, RR interval, or Valsalva ratio (only P-wave dispersion/QTc differences); baroreflex sensitivity findings conflict across studies (increased Nilsen 2009 vs decreased others). Small-study effects likely.
- **Limitations:** Only 7 standardized-protocol studies; high heterogeneity for Valsalva (I²=94%).
- **Implementation:** **Perturbation (migraine phenotype)** — small downward vmHRV/autonomic-reflex gain shift (g ≈ −0.3); model ictal-period sympathetic/vagal withdrawal during attacks as an episodic state. Low priority vs PD/MSA/epilepsy.
- **Validation:** Distribution-level HRV shift within CI bands; ensure shift does NOT exceed anxiety/pain layers (avoid making migraine look more dysautonomic than panic disorder).

---

## 5. ANXIETY / PANIC (systemic autonomic overlap — major confound axis)

### Claim AN-1: Anxiety disorders show reduced resting vmHRV (small-to-moderate effect)
- **Condition:** Anxiety disorders (PD-panic, PTSD, GAD, SAD; NOT OCD) | **Domain:** cardiac autonomic | **Variable:** HF-HRV, RMSSD/SDNN
- **Magnitude:** Chalmers 2014 meta (36 studies; 2086 patients, 2294 controls): HF g=−0.29 (−0.41,−0.17); time-domain g=−0.45 (−0.57,−0.33). Cheng 2022 meta (99 studies; 4897 patients, 5559 controls): parasympathetic HRV g=−0.39; significant in PTSD, panic, GAD, SAD; **HRV reactivity NOT different** between patients and controls (i.e., baseline shift, not response-shift). SSRI explains part of variance (adolescent study: 15.5% of HF variance).
- **Wearable modality+signal:** **Wearable-observable (HRV)** — population-level shift; overlaps PD, migraine, pain, depression.
- **Evidence level:** E5 (two independent meta-analyses, convergent).
- **Source:** Chalmers 2014, DOI 10.3389/fpsyt.2014.00080, PMID 25071612; Cheng 2022, PMID 35340102.
- **Contradictory/null:** LF-HRV not affected (g=−0.08, ns); OCD null; Licht et al. large-N study effect disappeared controlling for psychotropics; reactivity null (Cheng 2022) — argues anxiety is a tonic, not phasic, HRV perturbation.
- **Implementation:** **Perturbation (anxiety trait layer)** — tonic vmHRV reduction (g≈−0.3 to −0.45). This is a **mandatory confound layer** when generating dysautonomia/POTS-like synthetic cohorts: POTS patients have high anxiety comorbidity and HRV signatures overlap.
- **Validation:** Synthetic anxiety layer reproduces g≈−0.3–0.45 RMSSD/HF shift without exaggerated orthostatic tachycardia (distinguishes from POTS).

### Claim AN-2: Panic attacks produce acute autonomic surges — but HR surge magnitude is modest and inconsistent (key null-inconsistent area)
- **Condition:** Panic disorder | **Domain:** acute autonomic | **Variable:** HR, EDA, respiration, BP during attacks
- **Mechanism:** Sympathoadrenal surge + hyperventilation → hypocapnia (cerebral vasoconstriction, paresthesias, dizziness) → catastrophic appraisal loop.
- **Direction:** HR up, RR up, EDA up, BP variable. | **Magnitude (surprisingly weak quantitative base):** 24-h ambulatory study (10 patients, 8 attacks): only 3/8 attacks showed HR increases beyond activity explanation; HR >110 bpm seen in the more severe subset (Taylor 1982, PMID 7187688). Lab CO2 challenge (n=15 panic + 15 controls): HR ~95–100 bpm during challenge, no significant group × CO2 interaction on HR — i.e., objective HR response did not separate patients from controls. Hyperventilation physiology (controlled hypocapnia study): HR +4.4 bpm (95% CI 1.7–7.1), MAP −3.5 mmHg (−5.2,−1.8), PP +4.8 mmHg.
- **Timescale:** Attack onset abrupt (peaks ~10 min); duration typically 15–60 min.
- **Wearable modality+signal:** **Wearable-observable (PPG-HR, EDA, respiration)** — but signature is NON-SPECIFIC: overlaps exercise, stress, seizure autonomic surges, POTS symptoms. The subjective severity ≫ objective signal magnitude.
- **Evidence level:** E2/E3 — and the controlled evidence is partially NULL (HR differentiates poorly). The common textbook claim of dramatic tachycardia (>120 bpm) in every panic attack is NOT well supported quantitatively.
- **Source:** PMID 7187688; Frontiers Psychiatry 2025 10.3389/fpsyt.2025.1533019; MDPI Brain Sci 10(9):614 (hypocapnia).
- **Supporting:** Clinical consensus on symptom pattern (E5-level clinical consensus for the symptom complex, not for magnitude).
- **Contradictory/null:** As above — ambulatory and lab data show many attacks lack large HR surges; hyperventilation itself produces only ~+4 bpm HR.
- **Implementation:** **Perturbation (panic event layer)** with REALISTIC modest magnitude: HR surge +10–30 bpm over ~1–5 min with high inter-individual variance (some attacks HR-invariant), EDA surge, respiratory rate + sighing/hypocapnia pattern, 15–60 min duration. Explicitly a confounder-generator for seizure-detection and POTS-alarm algorithms.
- **Validation:** Discriminant analysis: synthetic panic vs TSST-stress (§7) vs ictal tachycardia (EP-1) should be hard to separate by HR alone (matching reality); separable only via context/multimodality.

---

## 6. OBSTRUCTIVE SLEEP APNEA (comorbidity perturbation)

### Claim OSA-1: OSA produces a stereotyped cyclical HR/SpO2/autonomic pattern — strong CORE candidate
- **Condition:** OSA (standalone + comorbid) | **Domain:** sleep autonomic/respiratory | **Variable:** cyclical variation of heart rate (CVHR), SpO2 sawtooth, sympathetic surges
- **Mechanism:** Apnea → vagal bradycardia (diving reflex) → progressive hypoxemia → chemoreflex tachycardia → arousal sympathetic peak → recovery. Four-phase autonomic cycle per event.
- **Magnitude/pattern:** Per-event HR oscillation bradycardia→tachycardia with each apnea; SpO2 desaturations (≥3–4% by scoring definition; deep nadirs in severe disease); repetitive sympathetic activation → nocturnal BP surges, non-dipping, daytime sympathetic tone elevation.
- **Comorbidity prevalence:** PD 20–70% (vs general 2–14%; review PMID 37541789); epilepsy 33.4% pooled (meta, 26 studies; 40% adults/26% children; PMC10509561) with 38% in a 166-patient PSG study; MSA SRBD 60.5% pooled (above). Bidirectional PD↔OSA risk (adjusted HR 1.54–1.92).
- **Wearable modality+signal:** **Fully wearable-observable (SpO2, HR/PPG, respiration proxy, IMU sleep)** — consumer wearables already screen OSA via these features.
- **Evidence level:** E5 (prevalence meta-analyses) + E4 (pattern replicated universally in PSG literature).
- **Source:** PMC13095601 (CVHR/ECG review); PMID 37541789; PMC10509561; Manni 2003 PMID 12790898 (10.2% clinical series).
- **Contradictory/null:** Prevalence estimates extremely sensitive to AHI definition (AHI3A vs 4% desat) — range 10–84% in general population reports.
- **Implementation:** **CORE physiology module (sleep-breathing event generator)** — the CVHR + SpO2 sawtooth is generic machinery usable by all comorbidity phenotypes; severity (AHI) parameterized. This is the strongest candidate in this document for CORE rather than phenotype-only.
- **Validation:** Synthetic OSA nights scored by wearable OSA-screening algorithms (ODI, CVHR features) should reproduce AHI-class separation and comorbidity prevalence ranges.

---

## 7. ACUTE PSYCHOLOGICAL STRESS (CORE physiology)

### Claim ST-1: Acute psychosocial stress (TSST) reliably elevates HR, SBP, cortisol; effect sizes quantified
- **Condition:** Healthy (core) | **Domain:** integrated stress response (SAM + HPA) | **Variable:** HR, SBP/DBP, salivary cortisol, HRV, EDA
- **Direction:** HR↑, SBP↑, cortisol↑, HRV↓, PEP↓ (sympathetic↑). | **Magnitude:** Youth TSST meta (57 studies, n=5026): HR ES=0.89; SBP ES=1.17; cortisol ES=0.47; HRV ES=−0.33; PEP ES=−0.37 (Seddon 2020, PMID 32305745). Adult cortisol meta (71 sub-studies): Cohen's d=0.93 (0.82–1.04), males > females (PMID 35755200). VR-TSST (n=10 men): HR max +40% session 1 / +32% session 2 (i.e., ~+25–35 bpm typical); cortisol +88% vs baseline session 1, habituated session 2 (PMID 20451329, DOI 10.1016/j.psyneuen.2010.04.003). Cortisol peak 15–20 min post-stressor; typical responder criterion +1.5 nmol/L; responder rates ~64–>70% (protocol-dependent).
- **Timescale:** HR/SBP peak during task (minutes), recover ~10–30 min; cortisol peaks 15–20 min post-onset, recovers 30–70 min. Habituation: cortisol habituates with repetition; HR/SAM response does NOT habituate (stable across sessions).
- **Wearable modality+signal:** **Wearable-observable (HR, HRV, EDA; BP proxy)**; cortisol is latent-only (no wearable).
- **Evidence level:** E5 (two meta-analyses) + E3/E4 habituation data.
- **Source:** PMID 32305745; PMID 35755200; PMID 20451329; TSST methodology review PMC7739033.
- **Contradictory/null:** Cardiac output, RSA, DBP effects did not reach significance in youth meta; VR/online variants show attenuated cortisol responses (36–40% responder rates in some VR cohorts) — protocol fidelity matters; small TSST studies overestimate effect (r=−0.24 sample-size bias).
- **Implementation:** **CORE.** The engine's reference human must include: (a) fast SAM arm (HR +10–35 bpm, EDA surge, HRV drop, onset seconds, recovery 10–30 min), (b) slow HPA arm (cortisol latent state modulating downstream physiology, +50–100% peak at ~20 min), (c) habituation asymmetry (HPA habituates, SAM does not), (d) sex difference (male cortisol > female), (e) large inter-individual variability with responder/non-responder structure.
- **Validation:** Virtual TSST: distribution of ΔHR (~d≈0.9), ΔSBP (d≈1.2), cortisol (d≈0.5–0.9); repeat-exposure habituation of cortisol only.

### Claim ST-2: Cold pressor / acute pain pressor responses are moderate and highly variable
- **Condition:** Healthy (core) | **Domain:** sympathetic cardiovascular | **Variable:** SBP/DBP/HR during cold pressor test
- **Magnitude:** n=400 (200 non-obese/200 obese): non-obese ΔSBP +10.4±6.4 mmHg, ΔDBP +7.8±3.7; obese blunted (+7.1±5.3, p=0.006) (PMC4337083). HR response bimodal: 20/39 healthy young adults sustained HR increase, 19/39 showed HR decrease after initial rise (high inter-individual variability; Mourot, PMID 18198985, DOI 10.33549/physiolres.931360).
- **Wearable modality+signal:** HR, EDA (pain evokes strong EDA), BP proxy.
- **Evidence level:** E4 (multiple controlled studies, consistent BP direction; HR inconsistent).
- **Implementation:** **CORE (pain/sympathetic pressor module)** — used by phenotype layers (migraine attacks, chronic pain flares, injury). Do NOT hard-code a stereotyped HR response — include the bimodal responder structure.
- **Validation:** CPT simulation: ΔSBP ≈ +8–12 mmHg band; ~50/50 HR responder split in healthy young.

### Claim ST-3: Chronic pain is associated with reduced vmHRV; analgesic intervention partially reverses it
- **Condition:** Chronic pain (comorbidity) | **Domain:** cardiac autonomic | **Variable:** RMSSD, HF-HRV, LF/HF
- **Magnitude:** Chronic pain vs controls: vmHRV reduced (Koenig 2016 meta, Pain Physician, PMID 26752494; effect moderate, consistent direction across etiologies). Intervention meta (21 RCTs, n=1262): between-group LF/HF g=−0.378 (p=0.003; shift toward parasympathetic); one-group RMSSD g=1.084, HF g=0.622 — but one-group effects confounded by placebo/non-specific effects (PMID 40700127).
- **Wearable modality+signal:** HRV (wearable); pain itself is latent (self-report).
- **Evidence level:** E5 (two meta-analyses) — with caveat on intervention-effect inflation.
- **Source:** PMID 26752494; PMID 40700127 (PMC12285944).
- **Contradictory/null:** Between-group time-domain effects non-significant (SDNN g=0.435 p=0.059; RMSSD p=0.099) — intervention claim weaker than within-group suggests.
- **Implementation:** **Perturbation (comorbidity layer)** — tonic vmHRV reduction; pain flares activate CORE pressor/EDA module (ST-2). Another contributor to the shared low-HRV confound axis (AN-1, PD-3, MI-1).
- **Validation:** Layer stacking test: PD + chronic pain + anxiety synthetic patients should show additive-ish (not multiplicative) HRV reduction within observed cross-study bounds.

---

## 8. HYPERVENTILATION EPISODES

### Claim HV-1: Voluntary/involuntary hyperventilation produces small, well-characterized cardiovascular shifts plus hypocapnia symptoms
- **Condition:** Healthy + panic/POTS comorbidity | **Domain:** respiratory-autonomic | **Variable:** HR, MAP, PP, (PaCO2 latent)
- **Magnitude:** Controlled hypocapnia study: HR +4.4 bpm (1.7–7.1), MAP −3.5 mmHg (−5.2,−1.8), PP +4.8 mmHg (0.5–9.0); post-hyperventilation HR overshoot −6.0 bpm below baseline. Hyperventilation exacerbates tachycardia in POTS (Physiology 2024 abstract). Symptom threshold ~PaCO2 <25 mmHg (cerebral vasoconstriction → dizziness, paresthesias).
- **Wearable modality+signal:** Respiration rate (PPG/IMU-derived), HR; end-tidal CO2 latent-only.
- **Evidence level:** E3/E4 (controlled human experiments, small n).
- **Source:** MDPI Brain Sci 10(9):614; StatPearls NBK493167; Physiology 2024 10.1152/physiol.2024.39.S1.614.
- **Implementation:** **CORE (respiratory-CO2 coupling)** as an event module — triggered by panic layer (§5), POTS, or voluntarily; couples respiratory pattern → small HR/BP shifts + symptom-relevant hypocapnia state. Keeps synthetic panic/POTS data from over-showing tachycardia.
- **Validation:** Hyperventilation bout simulation reproduces +4–5 bpm HR, −3–4 mmHg MAP, recovery overshoot.

---

## 9. CORE vs PERTURBATION ALLOCATION TABLE

| Physiology | Allocation | Rationale (evidence) | Wearable observability |
|---|---|---|---|
| Normal orthostatic baroreflex (HR +10–25 bpm, BP maintained; ΔHR/ΔSBP >0.5–1.0) | **CORE** | Consensus physiology; required substrate for all nOH phenotypes (E5) | IMU posture + PPG/ECG HR; BP latent/proxy |
| Acute stress response (SAM: HR/EDA/HRV; HPA: cortisol latent) + habituation asymmetry + sex difference | **CORE** | TSST meta-analyses d=0.5–1.2; generic to all conditions (E5) | HR, HRV, EDA wearable; cortisol latent |
| Sleep architecture + sleep-breathing event generator (OSA CVHR + SpO2 sawtooth, AHI-parameterized) | **CORE** | Universal comorbidity machinery; prevalence E5 across PD/epilepsy/MSA (20–60%) | SpO2, HR, respiration, IMU — fully wearable |
| Pain/pressor sympathetic module (CPT-type: ΔSBP ~+8–12, bimodal HR) | **CORE** | Generic symptom→autonomy pathway (E4) | HR, EDA, BP proxy |
| Hyperventilation/hypocapnia module (HR +4–5, MAP −3–4) | **CORE** | Shared across panic, POTS, anxiety (E3/E4) | Respiration, HR; CO2 latent |
| PD: cardiac denervation latent gain, OH ~30%, HRV shift (~15–25%), RBD prodrome, tremor 4–6 Hz + bradykinesia IMU, levodopa vasodepressor module | **Perturbation** | E5/E4 per claims PD-1…PD-6 | HRV/IMU wearable; MIBG/BP latent |
| MSA/PAF: severe nOH (ΔHR/ΔSBP <0.3), supine hypertension + reverse dipping, anhidrosis (blunted EDA gain), SRBD/stridor | **Perturbation** (extreme anchors of dysautonomia spectrum) | E4/E5 per AF-1…AF-5 | EDA blunting, nocturnal patterns wearable; TST/catecholamines latent |
| Epilepsy: GTCS event (IMU convulsion + EDA surge + HR surge + SpO2 dip 53–74% + postictal apnea/hypercapnia); focal ictal tachycardia (60% PPG-detectable) | **Perturbation** | E4/E5 per EP-1…EP-3 | Multimodal wearable-validated (sens ~90%, FA 0.2–1.4/day) |
| Migraine: small interictal autonomic-reflex reduction (g≈−0.3), ictal autonomic withdrawal | **Perturbation (low priority)** | E5 but internally contradictory (MI-1) | HRV — small effect, population-level only |
| Anxiety trait (tonic vmHRV ↓ g≈−0.3–0.45) | **Perturbation (mandatory confound layer)** | E5 ×2 convergent | HRV |
| Panic attack events (HR surge +10–30 bpm, EDA, hyperventilation, 15–60 min; many attacks HR-invariant) | **Perturbation (confound generator)** | E2/E3, partially null — model modest magnitude | HR/EDA/resp — non-specific signature |
| Chronic pain layer (tonic vmHRV ↓; flare→CORE pressor) | **Perturbation** | E5 (with intervention-effect caveat) | HRV |
| MIBG uptake, plasma norepinephrine, TST % anhidrosis, cortisol, ETCO2, QSART | **Latent-only variables** | No wearable channel exists; model as hidden states driving wearable observables | None (lab-only) |

**Deferred / out of scope:** stridor audio signatures; continuous cuffless BP calibration (treat BP as semi-latent with PPG proxies); anti-CGRP autonomic effects (insufficient evidence); dementia/DLB-specific autonomic modeling (reuse PD/MSA machinery with parameter changes).

---

## 10. CROSS-CUTTING DESIGN RECOMMENDATIONS

1. **Shared low-vmHRV axis:** PD, anxiety, chronic pain, and migraine all reduce vmHRV with overlapping effect sizes (g ≈ −0.3 to −0.6). OCPE should implement ONE parameterized "tonic vagal gain" knob that phenotype layers share — this is both parsimonious and reproduces the real-world diagnostic non-specificity of wearable HRV.
2. **Contrast pairs for validation:** nOH (blunted ΔHR/ΔSBP <0.3–0.5, bradycardic relative) vs POTS (exaggerated ΔHR, preserved vasomotor) vs panic (context-bound surges, normal orthostatic reflex) — these three must be distinguishable in synthetic orthostatic-challenge scenarios, mirroring clinical differential diagnosis.
3. **Event-vs-trait distinction:** Panic, seizures, pain flares, and OH symptoms are EVENTS riding on TRAIT shifts. Evidence supports trait-level (baseline) effects for anxiety (reactivity null, Cheng 2022) — do not over-amplify phasic reactivity in anxiety layers.
4. **Base-rate honesty:** Actigraphy iRBD screening PPV collapses at realistic prevalence (1.5% → PPV 3–9%). Synthetic-data benchmark claims must report prevalence-adjusted metrics.
5. **Habituation and medication must be first-class:** cortisol habituates (SAM doesn't); levodopa shifts OH prevalence ~22%→38% post-dose. Static phenotype parameters will produce unrealistic longitudinal data without these dynamics.

## 11. KEY GAPS / FAILED SEARCHES (Pass 2 targets)
- No large quantitative ambulatory dataset of panic-attack EDA/BP found — panic magnitude evidence is thin and partially null; a dedicated Pass 2 search (Meuret, Wilhelm, Roth ambulatory respiratory work) is recommended.
- PD resting heart rate direction (higher vs unchanged) unresolved — controlled data found show no resting-HR difference; do not perturb resting HR in PD phenotype.
- Migraine wearable trigger-forecasting studies (sleep/stress→attack prediction) not retrieved in this pass.
- Primary DOIs for Poh 2012, Onorati 2017/2019, Regalia 2019 seizure-detection studies must be pulled from primary sources before implementation (retrieved via secondary compilations).
- Levodopa BP effect is E3 (no placebo arm); a placebo-controlled estimate would strengthen the medication module.
