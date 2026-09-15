# OCPE Disease Evidence Base: Ehlers–Danlos Syndromes (focus: hEDS / HSD)

**Prepared by:** EDS/Connective-Tissue Scientist (research swarm, Pass 1 discovery)
**Date:** 2025 (session)
**Scope:** Hypermobile EDS (hEDS) and Hypermobility Spectrum Disorder (HSD) as modeling targets for synthetic wearable datasets. Vascular EDS (vEDS, COL3A1) is flagged **OUT OF SCOPE** for wearable physiology modeling (dangerous arteriopathy; no wearable signal of interest beyond contraindications). Classical EDS (cEDS) noted only where data were collected in mixed cohorts.

## Evidence-level key
E0 hypothesis/speculation · E1 mechanistic (animal/in-vitro/small mechanistic human) · E2 observational human (cohort, case-control, clinic series) · E3 controlled human experimental (matched controls, standardized challenge) · E4 replicated quantitative (multiple controlled studies, consistent direction) · E5 meta-analysis/consensus.

**Brutal headline:** The hEDS/HSD physiological literature is thin, clinic-referral-biased, pre-2017-criteria-contaminated, and dominated by E2/E3 studies of n≈20–100. There is essentially **no E4/E5 evidence** for any physiological mechanism except (a) lower-limb proprioception deficits (E5 meta-analysis) and (b) possibly OSA prevalence (E5, small meta-analysis). The widely repeated claim "connective-tissue laxity → vascular hypercompliance → venous pooling → POTS" is **E1/E2 with direct contradictory null findings**; the largest arterial study found lower pulse-wave velocity (more elastic arteries) in EDS but this did **not** correlate with orthostatic HR/BP changes. Wearable-specific evidence: **one** 26-person WHOOP pilot (Frontiers in Neurology 2024) and one accelerometer study in adolescents. That is the entire direct wearable evidence base.

---

## 1. Definitions & epidemiology

### Claim 1.1 — 2017 hEDS diagnostic criteria define a strict clinical diagnosis of exclusion; no genetic test exists
- **Domain:** nosology | **Variable:** diagnostic status
- **Mechanism:** N/A (classificatory). 2017 hEDS criteria = (1) generalized joint hypermobility (Beighton score, age-dependent cutoffs), (2) ≥2 of: systemic features checklist / positive family history / musculoskeletal complications (pain, dislocations), (3) exclusion of alternative diagnoses and other heritable connective-tissue disorders. HSD (per Castori et al. framework) = symptomatic hypermobility failing hEDS criteria (e.g., insufficient systemic features); G-HSD, P-HSD, L-HSD, H-HSD subtypes.
- **Direction/Magnitude/Timescale:** N/A | **Population:** all ages; **Wearable relevance:** defines cohort for phenotype labels.
- **Evidence level:** E5 (international consensus classification).
- **Sources:** Malfait F et al. Am J Med Genet C Semin Med Genet. 2017;175(1):8-26. DOI: 10.1002/ajmg.c.31552. Castori M et al. Am J Med Genet C. 2017;175(1):148-157. DOI: 10.1002/ajmg.c.31539. Tinkle B et al. Am J Med Genet C. 2017;175(1):48-69. DOI: 10.1002/ajmg.c.31538.
- **Supporting:** Criteria applied in all post-2017 studies below. **Contradictory:** hEDS remains gene-negative; proteomic/RNA-seq work suggests hEDS and HSD may be one biological entity (Ritelli et al. Cells 2022;11:4040, DOI: 10.3390/cells11244040 — E1).
- **Limitations:** Inter-rater reliability of Beighton scoring moderate; prevalence estimates pre/post-2017 not comparable.
- **Implementation recommendation:** Direct evidence (classification). Use 2017 criteria labels to stratify synthetic phenotypes (hEDS vs HSD severity tiers), but treat the hEDS/HSD boundary as **artificial** for physiological parameterization — model a severity continuum.
- **Validation:** N/A for simulation; use criteria to label any real-data comparator cohorts.

### Claim 1.2 — Diagnosed prevalence of hEDS/HSD ≈ 0.2% (1 in 500); true symptomatic hypermobility prevalence much higher (~3.4%)
- **Domain:** epidemiology | **Variable:** prevalence
- **Mechanism:** N/A | **Direction:** underdiagnosis | **Magnitude:** diagnosed point prevalence 194.2/100,000 (0.19%, ~10 per 5,000-patient GP practice) in Wales, 1990–2017; general-population joint hypermobility ~18% (self-screen), symptomatic JH + widespread pain ~3.4%.
- **Timescale:** chronic, lifelong | **Population:** UK primary-care records, n=6,021 cases.
- **Wearable relevance:** sizes the market/prior for synthetic cohorts; prevalence too low for population screening claims.
- **Evidence level:** E2 (national registry, n large, but diagnosis-code-dependent).
- **Source:** Demmler JC et al. BMJ Open 2019;9:e031365. DOI: 10.1136/bmjopen-2019-031365. Mulvey MR et al. (2013, symptomatic hypermobility prevalence — cited via NASEM 2022 report, NBK584966).
- **Supporting:** NASEM 2022 consensus report (NBK584966) adopts these figures. **Contradictory:** true prevalence likely higher (screening studies find 2–3% in specialty populations; 2.7–2.8% in gender-affirming clinics — likely enrichment).
- **Limitations:** codes predate 2017 nosology; referral/diagnosis bias toward females and severe cases.
- **Implementation recommendation:** Association-level. Use ~0.2% diagnosed prevalence as base rate; do not use screening-prevalence (3.4%) numbers for the modeled clinical phenotype.
- **Validation:** cross-check against Danish national cohort (Kulas Søborg 2017; Leganger 2022).

### Claim 1.3 — Strong female predominance in diagnosed hEDS/HSD (~70–90% female)
- **Domain:** epidemiology | **Variable:** sex ratio
- **Mechanism:** unknown; hypotheses include sex hormones, pain-processing differences, referral/ascertainment bias (E0/E1).
- **Magnitude:** 70% female in Wales national cohort (Demmler 2019); 90.6% female in hEDS and 95.2% in HSD in a Mayo EDS-clinic retrospective (n=2,451; ratios 9.6:1 and 19.6:1); female diagnosis peaks at age 15–19 vs male 5–9 (8.5-year mean age-at-diagnosis difference).
- **Population:** registry + tertiary clinic. **Wearable relevance:** synthetic cohorts must be majority-female, young-to-middle-aged adult; any normative comparisons must be sex-matched.
- **Evidence level:** E2 (large registries; clinic series likely inflated by ascertainment).
- **Sources:** Demmler 2019 (above). Sex differences study, Mayo EDS Clinic 2019–2025, n=2,451: PMC12869590 (Frontiers/Am J Med Genet family; verify journal before citing formally).
- **Contradictory/null:** joint hypermobility itself is roughly equally distributed in childhood; female predominance emerges peripubertally (suggests hormonal modulation — E1).
- **Limitations:** clinic ratios (10–20:1) almost certainly overestimate true population ratio (~2–3:1 per registry).
- **Implementation recommendation:** Model sex as a major covariate (baseline HR, HRV, pain sensitivity all sex-dependent); default synthetic hEDS cohort ~75–85% female.
- **Validation:** compare generated cohort sex/age structure against Demmler 2019 distributions.

---

## 2. Vascular compliance & venous pooling

### Claim 2.1 — Arteries in EDS (all types) are more elastic (lower central pulse-wave velocity) than age-matched reference values
- **Domain:** cardiovascular mechanics | **Variable:** carotid-femoral PWV (m/s)
- **Mechanism:** abnormal collagen/ECM → increased arterial distensibility (mathematical inverse of stiffness).
- **Direction:** ↓PWV (more elastic) | **Magnitude:** central PWV 4.73 ± 0.16 m/s (SE) in EDS vs age-matched reference means ~6–11 m/s (increasing with age); age-related stiffening markedly attenuated in EDS (near-flat PWV vs age). Correlations with BP: central PWV vs supine SBP r=0.387 (p=0.002), supine DBP r=0.400 (p=0.002), seated SBP r=0.399 (p=0.002). **No correlation between PWV and orthostatic ΔBP or ΔHR (all p>0.05).**
- **Timescale:** structural, chronic | **Population:** n=60 EDS (13 hEDS, 10 classical, 8 vascular, 29 other), 49F, 36±16 y; reference n=1,455 healthy (RVASC).
- **Wearable relevance:** PWV is not a consumer-wearable measure; indirectly relevant to BP cuff surrogates and pulse-transit-time estimates; suggests lower resting BP in synthetic hEDS.
- **Evidence level:** E3 (single controlled study vs large external reference set; no contemporaneous internal controls).
- **Source:** Miller AJ et al. "Arterial Elasticity in Ehlers-Danlos Syndromes." J Pers Med 2020 (PMC7016526; verify DOI, likely 10.3390/jpm1001xxxx).
- **Supporting:** Francois et al. 1986 (Int Angiol 5:1-5) found decreased PWV in 5/27 vEDS family members; trend to lower central PWV in 9 hEDS+POTS vs 9 matched controls (Cheng JL et al. Clin Auton Res 2017;27:113-116, DOI: 10.1007/s10286-016-0392-4).
- **Contradictory/null (important):** (1) Cheng 2017: PWV **not significantly different** in hEDS+POTS vs controls (n=9/group, underpowered). (2) Mirault T et al. J Hypertens 2015;33:1890-1896 (DOI: 10.1097/HJH.0000000000000617): carotid stiffness by ultrafast ultrasound **not different** in 37 vEDS vs 102 healthy volunteers. (3) No study has shown PWV predicts orthostatic tolerance in EDS.
- **Limitations:** pre-2017 Villefranche classification; no internal control group; medications uncontrolled.
- **Implementation recommendation:** **Association-level (E3 with two nulls).** The "connective tissue → vascular compliance" hypothesis should be modeled as a **phenotype perturbation** (modestly lower resting BP, option of increased arterial compliance parameter), NOT as a core causal mechanism of orthostatic intolerance. Effect size on orthostatic HR response is unestablished.
- **Validation:** compare simulated resting SBP/DBP distributions to Miller 2020 (supine SBP 119±11, DBP 66±8 mmHg; standing SBP 115±20, DBP 75±12, HR 90±15).

### Claim 2.2 — Increased venous pooling / venous insufficiency in the legs as the cause of orthostatic intolerance in hEDS: **hypothesis, not directly demonstrated**
- **Domain:** cardiovascular | **Variable:** calf venous compliance / venous volume shift
- **Mechanism:** lax connective tissue → distensible veins → gravitational pooling → reduced preload → compensatory tachycardia. This is the dominant pathophysiological narrative in reviews (Hakim 2017; Roma 2018).
- **Direction/Magnitude:** **No direct quantitative venous-compliance measurement in hEDS vs controls was identified in this search.** Rowe et al. 1999 hypothesized "enhanced elasticity" without measuring it; Miller 2020 (PMC7016526) states the theory "has become widely accepted despite the lack of empirical data."
- **Nearest transferable evidence:** in POTS (unselected), standing calf volume is greater and maximal venous filling times ~2× longer vs controls (E3; "Central arterial stiffness, flow-mediated dilation, and venous function in POTS," Scilit-indexed, 2025–26, Auckland/NZ group).
- **Population:** hEDS/HSD | **Wearable relevance:** would manifest as larger orthostatic HR increment; pooling proxies (dependent-limb PPG amplitude changes) theoretically measurable but unvalidated.
- **Evidence level:** **E0–E1** for hEDS specifically; E3 for POTS generally (not EDS-specific).
- **Sources:** Hakim A et al. Am J Med Genet C 2017;175:168-174. DOI: 10.1002/ajmg.c.31543 (PMID 28160388). Roma M et al. Auton Neurosci 2018;215:89-96. DOI: 10.1016/j.autneu.2018.02.006. Rowe PC et al. J Pediatr 1999;135:494-499. DOI: 10.1016/S0022-3476(99)70173-3 (PMID 10518084).
- **Contradictory/null:** De Wandele 2014 found connective-tissue laxity (skin extensibility) only "aggravates" dysautonomia (p<0.035) — a modifier, not a demonstrated cause; QSART data point to neuropathic rather than mechanical mechanism (see 3.2).
- **Limitations:** mechanism inferred from analogy; no strain-gauge plethysmography/air plethysmography venous-compliance study in hEDS located.
- **Implementation recommendation:** **Hypothesis — model as optional phenotype perturbation** (increased venous capacitance parameter) with explicit uncertainty flag; do not hard-code as causal core. OCPE should treat orthostatic tachycardia in hEDS as primarily mediated by the better-evidenced autonomic findings (below).
- **Validation:** if pooling perturbation enabled, output should reproduce HUT ΔHR distributions from Peebles 2022 / De Wandele 2016 (Claim 4.1); note this validates the output, not the mechanism.

### Claim 2.3 — Structural cardiac involvement (aortic root dilatation, MVP) in hEDS/HSD is rare and comparable to the general population (null finding)
- **Domain:** cardiovascular | **Variable:** aortic root z-score, MVP prevalence
- **Mechanism:** historically feared by analogy with vEDS/Marfan; evidence says otherwise for hEDS.
- **Magnitude:** Mayo retrospective (n=568 hEDS/HSD with echo; 481 with root measurements): aortic root dilation prevalence 2.7% (hEDS) / 0.6% (HSD); mean z-scores −0.58 (hEDS) and −0.73 (HSD) — i.e., **below** population mean. MVP 3.5% (hEDS) / 1.8% (HSD). Ritter 2017 pediatric cohort (n=325 hEDS): AoD 14.2% at z≥2.0 but **no progression** over serial echoes; ~1 z-score discrepancy between Boston and Devereux formulas.
- **Evidence level:** E2–E3 (large retrospective cohorts).
- **Sources:** Cardiac defects in hEDS/HSD retrospective cohort, PMC10982405 (2024, Mayo). Ritter A et al. Am J Med Genet A 2017;173(6):1467-1472. DOI: 10.1002/ajmg.a.38243 (PMID 28436618). Paige SL et al. Genet Med 2020;22:1583-1588. DOI: 10.1038/s41436-020-0856-8 ("Cardiac involvement in classical or hypermobile EDS is uncommon" — null). Wenstrup RJ et al. Genet Med 2002;4:112-117 (PMID 12180144): older data claiming 28% ARD (6/29 type III) — **contradicted** by later larger series; likely z-score/formula artifact.
- **Implementation recommendation:** Do **not** model aortic pathology in hEDS synthetic cohorts. vEDS (COL3A1) excluded entirely from wearable modeling scope.
- **Validation:** none needed; document as scope exclusion.

---

## 3. Autonomic interactions

### Claim 3.1 — Cardiovascular autonomic dysfunction is common in hEDS/HSD: resting sympathetic predominance, blunted sympathetic reactivity, reduced vagal modulation
- **Domain:** autonomic | **Variable:** HRV (LF/HF, SDNN, RMSSD, HF power), Valsalva BP, baroreflex sensitivity
- **Mechanism:** proposed sympathetic neurogenic dysfunction (small-fiber involvement) + connective-tissue laxity + medication effects; deconditioning and pain-induced sympathetic arousal are confounders explicitly measured.
- **Magnitude (best-controlled):** De Wandele 2014 (39 EDS-HT women vs 35 matched controls): LF/HF 1.7±1.23 vs 0.9±0.75 (p=0.002); Valsalva BP fall −19±12 vs −8±10 mmHg (p<0.001); initial tilt diastolic BP rise 7% vs 14% (p=0.032); lowered QSART responses (p<0.013), ~65% with reduced axon-reflex sweat responses; OI 74% vs 34%. Newer cohort (n=30 EDS vs 30 matched controls, PMC12781037): resting HR 87.3±11.6 vs 75.2±9.8 bpm (p<0.001); SDNN 35.4±9.7 vs 49.1±11.4 ms; RMSSD 20.7±6.9 vs 31.6±8.8 ms; HF 174±81 vs 272±106 ms²; LF/HF 3.7±1.3 vs 1.8±0.7; OI 53.3% vs 10%. Resting HR strongly inversely correlated with RMSSD (r=−0.52) and SDNN (r=−0.45).
- **Timescale:** continuous (resting tone) + acute (challenge responses) | **Population:** adult, predominantly female.
- **Wearable relevance:** **highest-relevance finding in this document** — resting HR elevation ~+8–12 bpm and RMSSD reduction ~30–35% are directly PPG/ECG-wearable measurable.
- **Evidence level:** **E4** (direction replicated across ≥3 controlled studies: Gazit 2003; De Wandele 2014; PMC12781037 2025; consistent with Miglis 2017 and De Wandele 2016) — though each study is small.
- **Sources:** De Wandele I et al. Semin Arthritis Rheum 2014;44:93-100. DOI: 10.1016/j.semarthrit.2013.12.006 (PMID 24507822). Gazit Y et al. Am J Med 2003;115:33-40. DOI: 10.1016/S0002-9343(03)00235-3 (PMID 12867232): OI (OH/POTS/unclassified) 78% (21/27 JHS) vs 10% (2/21 controls); greater SBP drop on hyperventilation (−11±7 vs −5±5 mmHg, p=0.02); alpha- and beta-adrenergic hyperresponsiveness. "HRV and Intrinsic Autonomic Coupling" 2025 (PMC12781037). Miglis MG et al. Auton Neurosci 2017;208:42-48.
- **Contradictory/null:** Miglis 2017 (POTS+hEDS vs POTS-only, n=20+20): autonomic test results **not significantly different** between groups — i.e., hEDS adds little beyond POTS diagnosis; differences were in medication burden and pain (70% vs 25% seeing pain physician). A 2024–25 tilt-table series (n=79, abstract only) found abnormal TTT rates did not differ between EDS and HSD (46.6% vs 31.6%, p=0.296) and beta-blockers blunted results. HRV effect sizes vary widely between cohorts (LF/HF 1.7 vs 3.7 across studies).
- **Limitations:** pre-2017 criteria in older studies (EDS-HT≈mixed hEDS/HSD); medication confounding pervasive; referral bias; no large prospective replication.
- **Implementation recommendation:** **Model in OCPE core autonomic module as the primary hEDS autonomic phenotype**: elevated resting sympathetic/parasympathetic ratio, resting HR +~10 bpm, RMSSD −30%, blunted BP reactivity to Valsalva/tilt. Parameterize with wide inter-individual variance (many patients are within normal range — Miglis).
- **Validation:** generated resting HRV metrics must match means±SD above; compare HUT ΔHR distribution to Claim 4.1 data.

### Claim 3.2 — Small-fiber neuropathy (sensory and autonomic) is a replicated objective finding in hEDS/EDS and a candidate mechanism for dysautonomia and pain
- **Domain:** neurological/autonomic | **Variable:** intraepidermal nerve fiber density (IENFD), QSART, thermal thresholds
- **Mechanism:** reduced small-fiber density → impaired sudomotor/vasomotor autonomic control + neuropathic pain; autonomic (C-fiber) impairment tracks with dysautonomia.
- **Magnitude:** Cazzato 2016: SFN a "common feature" across EDS types (skin biopsy, n≈24 EDS; quantitative IENFD reduction; exact means in full text). Igharo 2023 (Eur J Neurol 30:719-728): generalized SFN on biopsy in hEDS. Kersebaum 2025 (Auton Neurosci, PMID 40460600): hEDS family study — all showed A-delta fiber loss; those with dysautonomia also had C-fiber impairment and vascular hyperelasticity on microcirculation testing. De Wandele 2014: QSART reduced in ~65%.
- **Evidence level:** E2–E3 (multiple small controlled/case series; consistent direction; no meta-analysis).
- **Sources:** Cazzato D et al. Neurology 2016;87:155-159. DOI: 10.1212/WNL.0000000000002847 (PMID 27306637). Igharo D et al. Eur J Neurol 2023;30(3):719-728. Kersebaum D et al. Auton Neurosci 2025 (PMID 40460600). Fernandez A et al. J Intern Med 2022;292:957-960 (PMID 35781355).
- **Limitations:** mechanism linking SFN to orthostatic tachycardia is associative; SFN also common in fibromyalgia (shared comorbidity, possible confound).
- **Implementation recommendation:** Mechanistic context for the autonomic perturbation; **model implicitly** via the autonomic parameter changes of Claim 3.1 rather than as a separate module. Do not attempt to simulate nerve-fiber density.
- **Validation:** none direct; use as justification for autonomic perturbation ranges.

### Claim 3.3 — POTS prevalence in hEDS/HSD is elevated but estimates are wildly heterogeneous and referral-biased
- **Domain:** autonomic/orthostatic | **Variable:** POTS diagnosis rate on HUT/active stand
- **Magnitude (study-by-study, all HUT-based):** De Wandele 2016 (Rheumatology 55:1412-1420, DOI: 10.1093/rheumatology/kew032): POTS 41% (EDS-HT) vs 11% (controls) on 20-min HUT; OH ~26% (ns). Peebles 2022 (45 young women, 15/group, 2017 criteria): POTS on 10-min HUT 43% (G-HSD) vs 7% (hEDS) vs 7% (control), p<0.05; on active stand 47%/27%/13% (ns) — **hEDS NOT elevated on HUT** (contradictory finding); acute orthostatic symptoms during HUT: hEDS 100%, G-HSD 64%, control 33%. Celletti 2020 (102 reclassified hEDS/HSD, Monaldi Arch Chest Dis): POTS 48–49%, OH ~4%. Roma 2018 review: ~"half" of EDS patients with POTS. Miglis 2017: tilt orthostatic tachycardia in POTS+hEDS 39 bpm vs POTS-only 46 bpm.
- **Reverse direction (POTS→hEDS):** Miller 2020: 31% of 91 POTS patients met 2017 hEDS criteria; +24% GJH without hEDS. Boris & Bernadzikowski 2020 (362 pediatric POTS): 22.7% EDS, 39.0% HSD.
- **Evidence level:** E3 for "elevated OI symptoms" (consistent); **E2 with internal contradiction** for POTS diagnosis rates.
- **Sources:** Peebles KC et al. 2022 (PMC9305471). De Wandele 2016 (above). Celletti C et al. Monaldi Arch Chest Dis 2020 (see also Celletti 2017 BioMed Res Int, DOI: 10.1155/2017/9161865). Miller AJ et al. Auton Neurosci 2020;224:102637 (PMID 31954224; PMC7282488). Hakim 2017 (above).
- **Contradictory/null:** Peebles 2022 found POTS concentrated in G-HSD, not hEDS, during HUT — stricter 2017 hEDS criteria change the picture vs old EDS-HT studies. No OH in any group in Peebles.
- **Limitations:** tilt duration varies (10 vs 20 min); age-dependent HR criteria; active vs passive challenge disagreement; clinic cohorts.
- **Implementation recommendation:** Model orthostatic tachycardia as a **phenotype perturbation** affecting ~30–50% of the synthetic hEDS/HSD cohort, with symptom reports more prevalent than hemodynamic POTS (model symptom/physiology dissociation: 100% symptomatic in hEDS despite 7% POTS on HUT — Peebles). Do not model a single "POTS prevalence" number; sample from a range with uncertainty.
- **Validation:** simulated 10-min active-stand ΔHR distribution should place ~25–50% of the cohort above +30 bpm (+40 bpm if <19 y).

### Claim 3.4 — What explains the dysautonomia association: pooling vs deconditioning vs neuropathy — **UNKNOWN, genuinely unresolved**
- **Domain:** mechanism adjudication
- **State of knowledge:** (a) Neuropathy (SFN/QSART) — objective abnormalities (Claim 3.2) but causality to OI unproven; (b) connective-tissue vascular laxity — direct arterial data exist (Claim 2.1) but PWV does not correlate with orthostatic responses, and null studies exist; venous side unmeasured (Claim 2.2); (c) deconditioning — objectively lower MVPA demonstrated in adolescents (Claim 6.1) but no study has partialed out fitness as mediator of OI in hEDS; (d) pain-induced sympathetic arousal and (e) vasoactive medication use — identified as aggravating factors (De Wandele 2014). Deconditioning cannot be excluded as a major confounder in any existing study.
- **Evidence level:** E0 (explicitly unresolved in Hakim 2017, Roma 2018, Miller 2020 discussions).
- **Implementation recommendation:** OCPE should implement the hEDS autonomic phenotype as a **composite of separable perturbations** (autonomic-tone shift + optional pooling + optional deconditioning) with an explicit "mechanism unknown" annotation, so synthetic data don't launder an unproven causal story.
- **Validation:** sensitivity analyses varying each component; check against Miglis 2017 null (hEDS adds little autonomic abnormality beyond POTS itself).

---

## 4. Orthostatic effects (HUT / active stand)

### Claim 4.1 — Orthostatic HR/BP responses in hEDS/HSD are exaggerated for HR with preserved or mildly exaggerated BP responses; quantitative time-course data are sparse
- **Domain:** orthostatic physiology | **Variable:** ΔHR, ΔBP during HUT/active stand
- **Magnitude (available quantitative anchors):** Peebles 2022: HUT POTS rates 7% hEDS / 43% G-HSD / 7% control; active stand 27/47/13%; initial orthostatic hypotension common in all groups (~71–93%) with **no group difference** (p=1.00) — IOH is normal in young women, not an hEDS marker. De Wandele 2014: Valsalva BP fall −19±12 vs −8±10 mmHg; tilt initial DBP rise 7% vs 14%. Miller 2020 (arterial elasticity): supine→standing HR 74±13→90±15 bpm (all EDS; wide SDs). Gazit 2003: hyperventilation SBP drop −11±7 vs −5±5; cold pressor SBP rise 19±10 vs 11±13 (p=0.06, trend).
- **Timescale:** acute (seconds–minutes). **Timescale note:** no published minute-by-minute HR/BP time-series for hEDS HUT beyond categorical POTS endpoints — a genuine quantitative gap for wearable time-course synthesis.
- **Evidence level:** E3.
- **Sources:** as in Claims 2.1, 3.1, 3.3. Peebles 2022 (PMC9305471).
- **Contradictory/null:** IOH prevalence not different from controls (Peebles); OH rare/absent in young hEDS/HSD cohorts (0% in Peebles; 3.9% in Celletti 2020).
- **Implementation recommendation:** Model standing HR increment distribution with elevated mean and **large variance** (SD 15+ bpm); model BP as mostly preserved with a minority hypotensive tail (~5–25% depending on cohort definition). Do not model orthostatic hypotension as a typical hEDS feature.
- **Validation:** compare simulated active-stand ΔHR and symptom-label rates to Peebles 2022 Table 4.

---

## 5. Pain-related physiology

### Claim 5.1 — Chronic pain is near-universal in hEDS/HSD (~86–90% persistent pain; severe, multi-region, early onset)
- **Domain:** pain | **Variable:** pain prevalence/intensity
- **Magnitude:** persistent pain 86–88% (EDS vs HMS, n≈700+ comparative cohort, PMC7408708); mean NRS (7-day) 6.7–7.0/10; mean pain duration 11–14 years; mean ~19–20 pain regions. Mayo clinic series: joint pain 90.3% (hEDS F) / 94.6% (HSD F).
- **Evidence level:** E2 (large comparative observational cohorts, consistent).
- **Sources:** PMC7408708 (comparative cohort: EDS/HMS vs WAD vs spinal pain vs fibromyalgia, 2020). Benistan K, Martinez V. Am J Med Genet A 2019;179:1226-1234. Chopra P et al. Am J Med Genet C 2017;175:212-219 (pain management review).
- **Wearable relevance:** pain drives the autonomic/sleep/activity signals below; model pain as a latent variable modulating HR/HRV/activity.
- **Implementation recommendation:** Direct observational evidence; include chronic-pain latent variable in phenotype model (see 5.3 for physiological consequences).

### Claim 5.2 — Central sensitization and neuropathic components characterize hEDS pain (mechanistic)
- **Domain:** pain mechanism | **Variable:** QST, conditioned pain modulation
- **Magnitude/mechanism:** Di Stefano 2016 (Eur J Pain 20:1319-1325, DOI: 10.1002/ejp.856): central sensitization evidence in JHS/EDS-HT (lowered pressure-pain thresholds, facilitated temporal summation). SFN contributes neuropathic pain (Claim 3.2).
- **Evidence level:** E3 (controlled QST) + E2 (biopsy series).
- **Implementation recommendation:** Mechanistic support for pain→autonomic coupling; do not model QST directly.

### Claim 5.3 — Chronic pain (general, transferable evidence) reduces HRV — moderate-to-large meta-analytic effect; use as transferable prior where EDS-specific data are thin
- **Domain:** pain→autonomic | **Variable:** HF-HRV
- **Magnitude:** meta-analysis of 26 moderate-high-quality studies (51 screened in, chronic pain groups): consistent **moderate-to-large decrease in HF-HRV** (parasympathetic withdrawal); effects heavily driven by fibromyalgia studies; high heterogeneity. Koenig et al. 2016 meta-analysis (Pain Physician 19:E55-E78) concurs (reduced vagally mediated HRV in chronic pain).
- **Evidence level:** **E5** (meta-analytic) but **not EDS-specific**.
- **Sources:** Tracy LM et al. Pain 2016;157:7-29. DOI: 10.1097/j.pain.0000000000000360 (PMID 26431423). Koenig J et al. Pain Physician 2016;19:E55-E78.
- **Implementation recommendation:** Use as the **transferable quantitative prior** for pain→HRV coupling in OCPE (the EDS-specific HRV data of Claim 3.1 cannot separate pain from disease effect). Flag clearly as non-EDS evidence.
- **Validation:** check that synthetic pain-day vs pain-free-day HRV contrast falls within meta-analytic effect range (moderate: d≈0.3–0.5 on HF metrics).

### Claim 5.4 — Proprioceptive deficits in hypermobility are meta-analytically established (lower limb)
- **Domain:** sensorimotor | **Variable:** joint position sense (JPS), threshold to detection of movement
- **Magnitude:** meta-analysis (5 studies, n=254, BJHS): significantly poorer lower-limb JPS (p<0.001) and threshold detection (p<0.001); finger JPS poorer (p<0.001); shoulder JPS null (p=0.10). Recent controlled study (n=83, Beighton-stratified): greater absolute angular errors at elbow and knee (p<0.05) but **no difference** in grip strength or closed-chain functional performance.
- **Evidence level:** **E5** (meta-analysis) + E3 replication.
- **Sources:** Smith TO et al. Rheumatol Int 2013;33:2709-2716. DOI: 10.1007/s00296-013-2790-4 (PMID 23728275). Hall MG et al. Br J Rheumatol 1995;34:121-127 (PMID 7704456). 2023–25 GJH study (PMC12627509).
- **Wearable relevance:** gait instability, increased movement variability, higher injury-related activity interruptions; activity-signature differences plausible but unquantified.
- **Implementation recommendation:** Direct quantitative evidence for sensorimotor phenotype; incorporate as elevated gait-variability/activity-fragmentation parameter if OCPE models movement signatures. Note the functional-stability null (compensation) — do not assume grossly pathological gait.
- **Validation:** n/a for HR signal; constrain any gait-signature perturbation to "variability," not "inability."

---

## 6. Activity & deconditioning

### Claim 6.1 — Adolescents with HSD/hEDS are objectively less active: more sedentary time, less MVPA, more nocturnal movement
- **Domain:** activity (objective) | **Variable:** accelerometer-measured SED/MVPA/sleep movement
- **Magnitude:** 37 HSD/hEDS vs 45 healthy adolescents (13–17 y, Axivity AX3 wrist accelerometry): significantly more sedentary time, significantly less MVPA, significantly more sleep-period movement; fatigue–activity association **not confirmed** (null) after pain-catastrophizing adjustment.
- **Evidence level:** **E3** (controlled, device-measured; the only controlled accelerometry study identified).
- **Source:** Schubert-Hjalmarsson E et al. Pediatr Rheumatol Online J 2025;23:69. DOI: 10.1186/s12969-025-01124-0 (PMID 40629345; NCT05633225).
- **Contradictory/null:** fatigue not associated with measured activity — subjective fatigue ≠ objective inactivity; self-report activity bias documented elsewhere (Colley 2018 general-population self-report vs accelerometer discrepancy).
- **Implementation recommendation:** Direct wearable-relevant evidence; model reduced MVPA and elevated sedentary fraction in synthetic hEDS/HSD cohorts (effect sizes not published in abstract — obtain full text for min/day values before parameterizing). Decouple fatigue labels from activity in the generative model.
- **Validation:** compare step-count/MVPA distributions to this cohort's full-text values.

### Claim 6.2 — Kinesiophobia is highly prevalent (93% above cutoff) and drives the deconditioning cycle; it correlates with fatigue, not pain intensity
- **Domain:** behavioral/psychological | **Variable:** Tampa Scale for Kinesiophobia (TSK)
- **Magnitude:** Celletti 2013 (n=42, JHS/EDS-HT): 93% above TSK cutoff; multivariate association with fatigue severity (FSS) only, **not** with pain intensity (null). Pilates pragmatic trial (n=420, 200 completers): online Pilates reduced pain and kinesiophobia and improved function, but **objective activity levels did not change** (null on activity outcome).
- **Evidence level:** E2 (uncontrolled cohort) + E3 (pragmatic controlled trial).
- **Sources:** Celletti C et al. "Evaluation of Kinesiophobia and Its Correlations with Pain and Fatigue in JHS/EDS-HT" (PMC3725998). Buryk-Iggers S et al. Arch Rehabil Res Clin Transl 2022;4:100189. DOI: 10.1016/j.arrct.2022.100189 (systematic review of exercise in EDS). Russek L et al. "An Online Pilates Program for People with Hypermobility," J Multidiscip Healthc (Clarkson trial).
- **Implementation recommendation:** Model kinesiophobia as a behavioral modifier of activity level (latent variable), not a physiological parameter. The Pilates null warns against assuming symptom improvement normalizes activity.
- **Validation:** activity-level distribution should remain stable under simulated symptom improvement unless behavioral modifier is toggled.

### Claim 6.3 — Deconditioning vs disease: cannot currently be separated
- **Domain:** mechanism adjudication | **Evidence level:** E0
- **Content:** No study has established whether reduced aerobic capacity, muscle weakness, or autonomic abnormalities in hEDS are primary or secondary to inactivity. Exercise-intervention systematic review (Buryk-Iggers 2022) shows improvements with training (supporting reversibility of at least part of the phenotype) but studies are small and high risk of bias (PEDro/ROBINS-I rated).
- **Implementation recommendation:** Include a deconditioning axis (fitness level) in synthetic cohorts, sampled independently of disease-severity axis, to avoid baking in an unproven causal coupling.

---

## 7. Sleep

### Claim 7.1 — Poor subjective sleep quality in ~61% of EDS; severe fatigue in ~77%; bidirectional pain–sleep–fatigue coupling
- **Domain:** sleep (subjective) | **Variable:** PSQI, ESS, MFI
- **Magnitude:** n=252 physician-diagnosed EDS (Moss et al., Penn State): PSQI>5 in 61%; waking unrefreshed 68%; insomnia 33%; ESS>10 in 31%; daytime fatigue 45%. Classical and hypermobile subtypes reported worst sleep. Separate cohort (n=273): severe fatigue 77%, associated with worse sleep disturbance, pain, and psychological distress (as cited in MDPI sleep review).
- **Evidence level:** E2.
- **Sources:** Moss C et al. (Sleep 2018 abstract supplement; reported in MDPI "Sleep Characteristics in Individuals with EDS" 2025, 2076-3271/13/3/85). Pediatric: pain and poor sleep quality in non-vascular EDS (PMC6528463).
- **Wearable relevance:** degraded sleep efficiency and fragmentation — wearable-detectable; adolescent accelerometry (Claim 6.1) objectively confirms increased nocturnal movement.
- **Implementation recommendation:** Direct observational evidence; model elevated sleep fragmentation and reduced efficiency in ~60% of cohort. Pain and sleep should be coupled latent variables.

### Claim 7.2 — Objective sleep pathology: OSA prevalence markedly elevated in EDS (32% vs 6% matched controls)
- **Domain:** sleep (objective) | **Variable:** AHI by respiratory polygraphy
- **Magnitude:** 100 EDS (46% hypermobile type) vs 100 age/sex/weight/height-matched controls: OSA (AHI≥5) 32% vs 6%; OR 5.3 (95% CI 2.5–11.2), p<0.001; ESS median 11 (7–14) vs 7 (5–10); no difference in aortic dimensions or BP. Meta-analysis of OSA in joint hypermobility exists (Sedky 2019, J Clin Sleep Med 15:293-299, DOI: 10.5664/jcsm.7636) — small study pool. Pediatric replication: Stöberl 2019 (Respiration 97:284-291, DOI: 10.1159/000494328).
- **Evidence level:** **E3–E4** (well-matched parallel cohort + meta-analysis).
- **Sources:** Gaisl T et al. Thorax 2017;72:729-735. DOI: 10.1136/thoraxjnl-2016-209560 (PMID 28073822). Guilleminault C et al. Chest 2013;144:1503-1511 (PMID 23929538). Sedky 2019 (above).
- **Implementation recommendation:** Direct quantitative evidence; include an OSA-comorbidity branch (~30% of EDS cohort) with its own nocturnal SpO2/HR signature if OCPE models overnight signals. Note this is a **comorbidity perturbation**, not core hEDS physiology.
- **Validation:** compare overnight HR-variability/ODI patterns to OSA reference signatures.

---

## 8. Thermoregulation

### Claim 8.1 — Thermoregulatory dysfunction: suggestive but **thin evidence** — label as such
- **Domain:** thermoregulation | **Variable:** sweat output (QSART), self-reported heat/cold intolerance
- **Magnitude:** De Wandele 2014: ~65% of EDS-HT had reduced axon-reflex sweat responses (QSART, sudomotor dysfunction). Mayo sex-difference cohort: self-reported heat intolerance 51.1% (HSD F) vs 28.4% (M); cold intolerance ~49% (F) — **self-report only**. Secondary review literature (ScienceDirect dermatology review citing De Wandele/Hakim) hypothesizes hypohidrosis-related heat-illness risk, compounded by anticholinergic medications.
- **Evidence level:** E3 for sudomotor deficit (QSART, one controlled study, n=39); **E0–E1** for actual thermoregulatory/core-temperature consequences (no direct core-temperature or heat-chamber study in hEDS identified).
- **Sources:** De Wandele 2014 (above); Mayo cohort (PMC12869590); review: "Global warming, heat-related illnesses, and the dermatologist" (S2352647520301350).
- **Implementation recommendation:** **Defer** a thermoregulation module for hEDS, or implement only as reduced sweating gain (phenotype perturbation) with explicit E1 flag. No core-temperature perturbation is justified by current evidence.
- **Validation:** none available; mark as open research gap.

---

## 9. Comorbidity structure (hEDS × POTS × ME/CFS × MCAS × fibromyalgia)

### Claim 9.1 — Quantified overlap rates (direction matters; both directions listed)
- **hEDS in POTS:** 31% of 91 POTS patients met 2017 hEDS criteria (Miller 2020; Auton Neurosci 224:102637; PMID 31954224); pediatric POTS: 22.7% EDS + 39.0% HSD (Boris & Bernadzikowski 2020). Self-reported EDS in POTS cohorts 42–46% (inflated).
- **POTS in hEDS/HSD (clinic samples):** 41–49% on HUT (De Wandele 2016; Celletti 2020); 7–27% in stricter 2017-criteria young cohorts (Peebles 2022). EDS-clinic-based claims of "up to 78–90%" (Gazit OI 78%; NIH webinar citing clinic studies) are **referral-biased — treat as upper bounds, not prevalences**.
- **hEDS/hypermobility in ME/CFS:** hEDS 12–19–20% (n=229 cohort cited in NINDS ME/CFS Roadmap 2024 and PMC10208411 review); joint hypermobility 50–81% of ME/CFS. ME/CFS registry (n=815, Mudie 2024): 15.5% joint hypermobility; hypermobility+EDS subgroup had significantly worse HRQoL and multi-domain symptom burden.
- **Fibromyalgia × hypermobility:** co-occurrence 68–90% in a meta-study cited by Pollack (NINDS 2024) — **verify primary source before quantitative use (E2, wide range)**.
- **MCAS × EDS:** no controlled prevalence study identified; reviewed by Seneviratne SL et al. Am J Med Genet C 2017;175:226-236 and Monaco A et al. Immunol Res 2022;70:419-431 (DOI: 10.1007/s12026-022-09280-1). Clinic self-report MCAS ~17% in one gender-clinic hEDS sample; Mayo cohort shows mast-cell symptom enrichment in HSD females. **Evidence level E2 at best.**
- **Registry comorbidity burden:** Danish nationwide cohort (1,319 EDS vs 46,700 matched): GI functional disorders, hernias, asthma, pneumonia, osteoporosis significantly more frequent (Leganger J et al. Disabil Rehabil 2022;44:189-193; PMID 32412854). Wales case-control: elevated odds across 16/20 disease chapters incl. mental disorders (OR 4.16, 95% CI 3.29–5.27) and musculoskeletal (OR 9.36, 7.98–11.00) (Demmler 2019).
- **Implementation recommendation:** Use the following defensible sampling rates for synthetic hEDS cohorts: comorbid POTS ~30–40% (range 7–49% by ascertainment), ME/CFS-level fatigue phenotype ~40–77%, MCAS label ~15–20% (low confidence), OSA ~30%. Sample comorbidities jointly (they cluster) rather than independently. All rates are **association-level (E2/E3)**.
- **Validation:** joint comorbidity marginals vs Miller 2020, De Wandele 2016, Leganger 2022.

---

## 10. Wearable evidence (direct)

### Claim 10.1 — Direct wearable studies in EDS: exactly two identified. The field is essentially empty.
1. **WHOOP strap, 26 hEDS adults, 6 months, wavelet HRV vs GI symptoms** (Front Neurol 2024;15:1499582, DOI: 10.3389/fneur.2024.1499582): 4,615 symptom-days; high-GI-symptom days (score 7.59±1.28) vs low (2.58±1.27). **No significant group-level difference in standard HRV metrics** between high- and low-symptom days (population-level null); individual-level F-tests showed VLF/ULF variance differences in ~76–92% of sampled signals; LF/HF 5.92±1.29 (high) vs 6.64±1.45 (low), ns. Daily symptom means: fatigue 5.84±1.64, pain 5.44±1.60, brain fog 5.1±1.94; awakenings 1.91±1.77/night. Cohort 92% female, mean age 44.6.
2. **Accelerometry, 37 HSD/hEDS adolescents vs 45 controls** (Claim 6.1): sedentary ↑, MVPA ↓, nocturnal movement ↑.
- **Evidence level:** E2/E3 pilots.
- **Key lesson for OCPE:** the WHOOP null at group level + individual-level significance is the single most important empirical anchor for synthetic-data design: **hEDS wearable signatures are likely dominated by intra-individual (within-person, flare-day) variability, not stable group-level offsets.** Synthetic datasets must generate realistic within-person day-to-day variance and person-specific baselines, or they will fail to reproduce the one real wearable dataset that exists.
- **Nearest transferable wearable evidence (non-EDS):** chronic-pain HRV meta-analyses (Claim 5.3); POTS calf-volume/compression literature; fibromyalgia wearable HRV proxy studies (e.g., MDPI Sensors 2025, 25:2618).
- **Implementation recommendation:** Use (1) and (2) as ground-truth anchors; generate day-level symptom–HRV coupling at the individual level (random slopes), with group-mean differences kept small/null for symptom-day contrasts, per the WHOOP findings.
- **Validation:** fit synthetic within-person HRV-vs-symptom distributions to reproduce ~76–92% individual-level F-test significance rate and null group-level mean differences from Front Neurol 2024.

---

## Consolidated implementation priorities for OCPE

| Mechanism | Evidence | Verdict |
|---|---|---|
| Resting autonomic shift (↑HR ~+10 bpm, ↓RMSSD ~30%, ↑LF/HF) | E4 (3+ small controlled studies) | **Core phenotype perturbation** |
| Orthostatic tachycardia (POTS-like) in subset | E3, heterogeneous, referral-biased | Phenotype perturbation, 30–50% of cohort, wide variance |
| ↑Arterial elasticity (↓PWV) / venous pooling | E3 with two nulls; venous side unmeasured | Optional perturbation; **not** causal core |
| Small-fiber neuropathy | E2–E3 | Implicit (drives autonomic params) |
| Chronic pain (~88%, NRS ~7) → ↓HF-HRV | E2 (EDS) + E5 (transferable meta) | Latent variable with transferable quantitative coupling |
| Reduced MVPA / ↑sedentary time | E3 (adolescents) | Direct; parameterize from full text |
| Kinesiophobia → activity suppression | E2/E3 | Behavioral modifier |
| Sleep fragmentation + OSA branch (32%) | E2 + E3/E4 | Core (fragmentation) + comorbidity branch (OSA) |
| Sudomotor deficit/thermoregulation | E3 (sweat) / E0–E1 (thermoreg) | **Defer** or minimal perturbation |
| Aortic/cardiac structural disease | E2–E3 null | **Exclude** from model |
| vEDS (COL3A1) | — | **Out of scope entirely** |

## Top evidence gaps (for swarm coordinator)
1. No direct venous-compliance/pooling measurement in hEDS — core narrative mechanism untested.
2. No minute-resolution HUT HR/BP time-series published for hEDS — cannot parameterize orthostatic time-course directly.
3. No adequately controlled adult actigraphy; the only device study is adolescent (n=37).
4. Whether dysautonomia is disease-intrinsic vs deconditioning/pain/medication-driven is unresolved (no mediation analysis exists).
5. hEDS-specific pain→HRV effect sizes confounded; only transferable chronic-pain meta-analytic priors available.
6. Thermoregulation: no core-temperature or heat-stress data at all.
7. Wearable evidence = one 26-person WHOOP pilot + one adolescent accelerometer study; group-level symptom–HRV coupling was null.
8. All prevalence estimates pre-2017 vs post-2017 criteria are not commensurable; clinic-based POTS/hEDS overlap rates are referral-biased upper bounds.
