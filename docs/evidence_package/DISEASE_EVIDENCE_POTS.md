# OCPE Disease Evidence Base — Postural Orthostatic Tachycardia Syndrome (POTS) / Dysautonomia

**Scope:** POTS as flagship phenotype; orthostatic hypotension (OH), initial OH (IOH), and vasovagal syncope (VVS) as contrast phenotypes.
**Evidence levels:** E0 hypothesis | E1 mechanistic/preclinical | E2 observational human | E3 controlled human experimental | E4 replicated quantitative | E5 meta-analysis/consensus.
**Pass 1 (discovery) compilation. All DOIs/PMIDs cited only where actually retrieved in this pass.**
**Key caveat for modeling:** Most POTS hemodynamic numbers come from small mechanistic studies (n≈10–60) at specialist centers, predominantly adolescent/young-adult female cohorts. Tilt (HUT) and active standing give systematically different values; never mix them in one parameter set without labeling the modality.

---

## 1. Definition, Diagnostic Criteria, and the HR Threshold

### Claim 1.1 — Consensus diagnostic criteria
- **Claim:** POTS = sustained HR rise ≥30 bpm within 10 min of upright posture (≥40 bpm ages 12–19), without orthostatic hypotension (sustained drop ≥20/10 mmHg), with chronic orthostatic intolerance symptoms ≥3–6 months, relieved by recumbence, and no alternative cause of sinus tachycardia.
- **Domain / variable:** cardiac chronotropy; HR.
- **Direction / magnitude:** ΔHR ≥30 bpm (adults), ≥40 bpm (adolescents); often absolute upright HR ≥120 bpm. Canadian CCS statement adds minimum supine HR ≥60 bpm to avoid false positives in bradycardic individuals.
- **Timescale:** ΔHR must be present within 10 min and *sustained* (≥2 readings ≥1 min apart); transient first-minute tachycardia is normal and must not count.
- **Population:** consensus (Sheldon 2015 HRS; Raj 2022 CMAJ; Vernino 2021 NIH; CCS 2020).
- **Wearable modality:** PPG HR + accelerometer posture detection can replicate the supine→stand ΔHR; diagnosis additionally requires BP rule-out (not wearable-observable) and symptom correlation.
- **Evidence level:** E5.
- **Sources:** Sheldon RS et al., Heart Rhythm 2015;12:e41–63, DOI 10.1016/j.hrthm.2015.03.029. Vernino S et al., Auton Neurosci 2021 (NIH consensus; PMC via Raj 2022). Raj SR et al., CMAJ 2022;194:E378–85, DOI 10.1503/cmaj.211373 (PMC8920526). Arnold AC et al., Auton Neurosci 2018;215:3–11, DOI 10.1016/j.autneu.2018.02.005 (PMC6113123).
- **Contradictory/null:** The 30-bpm cut is arbitrary and has poor specificity at longer durations: in controls, 60% met ≥30 bpm at 10 min tilt and 80% at 30 min tilt (Plash 2013, PMC3478101); HUT exaggerates ΔHR in *both* groups, reducing specificity vs. active stand (Arnold 2018 Fig 2).
- **Limitations:** Threshold ignores distribution shape, time course, oscillation amplitude, BP and symptom data (Geddes 2020, PubMed 32078525).
- **Implementation:** Treat the 30-bpm rule as a *binary overlay on a continuous ΔHR distribution*; model ΔHR(t) as a trajectory, not a scalar.
- **Validation:** Synthetic cohorts should reproduce population-level sensitivity/specificity vs. controls at 5, 10, 30 min (Plash 2013: tilt-vs-stand ΔHR POTS 49±4/55±5/62±4 bpm; stand 44±4/–/50±4; controls ~27±3 at 5 min).

### Claim 1.2 — Diurnal variability
- **Claim:** Orthostatic tachycardia is larger in the morning than afternoon/evening, in both POTS and controls.
- **Magnitude:** POTS standing HR 108±4 bpm AM vs 100±3 bpm PM; controls 89±3 vs 80±2 bpm (Brewster 2012, n=54 POTS/26 controls; PubMed 21751966). Pediatric cohort: 100% of POTS met criteria AM, 44.2% afternoon, 27.9% evening; suggested PM cutoff ΔHRmax ≥30 bpm (sens 85%, spec 71.4%) and evening ≥25 bpm (sens 85%, spec 76.2%) (Cai 2021, Front Pediatr, DOI 10.3389/fped.2021.644461).
- **Evidence level:** E4 (replicated in two independent cohorts).
- **Wearable:** Morning-vs-evening standing HR delta is directly observable; synthetic data must include time-of-day covariate.
- **Implementation:** ΔHR time-of-day modulation (~+8–10 bpm AM bias); new mechanism layer, not a parameter rescale.
- **Validation:** Check simulated morning test positivity >> evening positivity.

---

## 2. Subtypes: Neuropathic / Hyperadrenergic / Hypovolemic — Overlapping and Continuous

### Claim 2.1 — Subtypes overlap heavily and are composable, not discrete clusters
- **Claim:** In a 378-patient subspecialty cohort (Mayo; 89.9% female, mean age 23.0±4.9 yr, mean age at diagnosis 21.0±5.6 yr), phenotype prevalence was hyperadrenergic 75.0%, hypovolemic 44.9%, neuropathic 37.8%; 41.7% had two phenotypes, 11.4% all three; 6.8% fit none.
- **Breakdown (n=352):** pure hyperadrenergic 26.4%, hyperadrenergic+hypovolemic 23.0%, hyperadrenergic+neuropathic 14.2%, triple 11.4%, pure neuropathic 7.7%, pure hypovolemic 6.0%, neuropathic+hypovolemic 4.5%, none 6.8%.
- **Definitions used:** hyperadrenergic = standing NE >600 pg/mL or ΔSBP/DBP ≥10 mmHg on HUTT; hypovolemic = 24-h urine Na <100 mmol; neuropathic = abnormal QSART or TST.
- **Symptoms did NOT differ across phenotypes** (ANOVA, Bonferroni) — phenotypes are not clinically separable by symptom report.
- **Population:** n=378 (352 fully phenotyped), 89.9% F.
- **Evidence level:** E2 (large observational, single center, referral bias).
- **Source:** Angeli AM et al., Sci Rep 2024;14:205, DOI 10.1038/s41598-023-50886-8, PMID 38168762 (PMC10761725).
- **Contradictory:** Thieben 2007 Mayo (n=152) found neuropathic 42.8% (QSART)/53.8% (TST), hypovolemic 28.9%, hyperadrenergic 29% — prevalence is definition- and referral-dependent.
- **Implementation:** **Continuous, composable mechanism dimensions** (3 independent latent severities: peripheral sympathetic denervation, volume deficit, central sympathoexcitation) with mixture-weight sampling per synthetic patient; do NOT implement 3 exclusive classes.
- **Validation:** Sampled joint distribution should reproduce Angeli 2024 two-way/three-way overlap fractions and "none" ≈7%.

### Claim 2.2 — Hyperadrenergic standing norepinephrine
- **Claim:** ~50% of POTS meet hyperadrenergic criteria by classic definitions (standing NE ≥600 pg/mL, ΔSBP ≥10 mmHg upright, sympathoexcitatory symptoms).
- **Magnitude:** Angeli 2024: standing NE 744±359 pg/mL (hyperadrenergic, n=264) vs 415±102 pg/mL (non-hyperadrenergic, n=71); distribution suggests the 600 pg/mL cut "may serve better to rule-out than rule-in." Okamoto 2024 (Vanderbilt): phenotyping cohort n=28, upright NE quartiles; treatment cohort n=38; hyperadrenergic POTS (high supine MSNA) had upright BP 122±8/76±5 vs 99±5/62±3 mmHg in low-MSNA, **with identical orthostatic ΔHR (34±8 vs 34±5 bpm, p=0.988)** — hyperadrenergia is expressed in BP, not in ΔHR magnitude.
- **Evidence level:** E3 (controlled, small) / E2 (large cohort).
- **Sources:** Garland EM et al., Neurology 2007;69:790–8 (PubMed 17709712) [NE≥3.54 nM ≈ 600 pg/mL subgroup had higher HR & BP]. Okamoto LE et al., Hypertension 2024, PMID 39109428 (PMC11483201). Angeli 2024 (above).
- **Limitations:** NE cutoff arbitrary, assay-dependent; MSNA quartile analysis small (n=7/group).
- **Implementation:** hyperadrenergic dimension → upright SBP +5 to +15 mmHg, tremulousness, higher supine HR; NE as latent variable correlated with, not identical to, ΔHR.
- **Validation:** Simulated upright BP rise only in high-hyperadrenergic stratum; ΔHR uncorrelated with NE stratum (Okamoto null replicated).

### Claim 2.3 — Neuropathic POTS: partial peripheral sympathetic denervation
- **Claim:** Subset has length-dependent postganglionic sympathetic denervation of the legs → impaired venoconstriction, dependent pooling.
- **Magnitude (Jacob 2000, NEJM 343:1008–14):** baseline femoral vein NE lower in POTS than controls (135±30 vs 215±55 pg/mL, p=0.001); leg NE spillover responses blunted vs arm (cold pressor 0.001±0.09 vs 0.12±0.12 ng/min/dL, p=0.02; nitroprusside p=0.01; tyramine p=0.04), while arm responses intact.
- **Supporting:** Abnormal QSART in 22–50% (Angeli 2024: 22.3%; literature 30–50%); reduced intraepidermal nerve fiber density on skin biopsy in subsets (Gibbons 2013, PLoS One 8:e84716).
- **Evidence level:** E3.
- **Sources:** Jacob G et al., NEJM 2000;343:1008–14 (values via retrieved abstract/text); Gibbons 2013 DOI 10.1371/journal.pone.0084716.
- **Implementation:** neuropathic dimension → blunted leg SVR response (reduced slope), increased dependent venous capacitance, acrocyanosis; preserve arm/central responses.
- **Validation:** Simulated tilt: thoracic volume fall larger, leg pooling larger in neuropathic-weighted samples.

### Claim 2.4 — Hypovolemic POTS: measured blood volume deficit and RAAS paradox
- **Claim:** Many POTS patients have true hypovolemia with paradoxically inappropriately normal renin and low aldosterone.
- **Magnitude (Raj 2005, Circulation 111:1574–82, n=15 POTS/14 controls):** plasma volume deficit −334±187 vs −10±250 mL (p<0.001); red cell volume deficit 356±128 vs 218±140 mL (p=0.01); **total blood volume deficit 689±270 vs 228±353 mL (p<0.001)** — the ~689 mL figure is VERIFIED. Renin identical (0.79 vs 0.79 ng/mL/h); aldosterone paradoxically low (190±140 vs 380±230 pmol/L, p=0.017). Fu 2010 (JACC): blood volume 60 [54–64] vs 71 [65–78] mL/kg. CO-rebreathing replication: −13.9% average deficit (PMC11999789).
- **Evidence level:** E4 (replicated by multiple methods: 131-I albumin, dye dilution, CO rebreathing).
- **Implementation:** hypovolemic dimension → total blood volume −10 to −15%, ↓preload, ↑orthostatic ΔHR; RAAS coupling weakened (aldosterone low-normal despite volume deficit).
- **Validation:** Reproduce ΔHR–blood volume negative correlation; volume expansion (1 L saline / exercise training) reduces upright HR.

---

## 3. Full Orthostatic Time Course (POTS vs Healthy)

### Claim 3.1 — The healthy standing response (reference trajectory)
- **Claim:** On standing, 500–800 mL of blood shifts below the diaphragm; normal compensation: transient HR peak within ~15–20 s, then stabilization; negligible SBP change, DBP +~5 mmHg, HR +10–20 bpm sustained.
- **Initial (0–30 s):** transient HR rise resolving by ~45 s; transient BP dip (initial OH in susceptible individuals: ≥40/20 mmHg within 15 s, recovery 30–60 s) is a *normal-variant* phenomenon, not POTS.
- **Evidence level:** E4/E5 (established physiology; Freeman 2011 consensus; Arnold 2018 review).
- **Implementation:** baseline (control) orthostatic model must include the initial transient phase (seconds) separately from the sustained phase (minutes).

### Claim 3.2 — POTS: HR rises fast, keeps rising with tilt duration, and does not plateau at 10 min
- **Claim:** In POTS, ΔHR continues to increase beyond the diagnostic 10-min window; tilt produces larger ΔHR than standing at every time point.
- **Magnitude (Plash 2013, PMC3478101, POTS n=15):** HUT ΔHR: 5 min 49±4, 10 min 55±5, 30 min 62±4 bpm. Active stand ΔHR: 5 min 44±4, 30 min 50±4 bpm. Controls at 5 min: HUT 27±3 bpm. By 30 min, 80% of healthy controls also exceeded 30 bpm (false positives).
- **Time-course detail (Orjatsalo 2020, adolescents, POTS n=25 vs non-POTS n=12; DOI 10.3389/fnins.2020.00725):** supine HR 74.6±10.2 vs 74.1±11.1; HUT 1 min 103.9±13.2 vs 99.2±13.4; HUT 2–4 min 100.8±13.4 vs 94.3±11.3; HUT final 108.6±17.8 vs 95.3±14.5; post-tilt supine 74.9±13.2 vs 71.1±8.7; ΔHR 52 (range 40–70) vs 34.75 (29–39) bpm. Note near-identical 1-min HR — **group separation develops over minutes 2–10**, not in the first minute.
- **Timescale:** most of the rise occurs in the first 1–5 min; further creep +5–15 bpm from 10→30 min.
- **Evidence level:** E4 (consistent across studies; see also Chinese adult cohort: max ΔHR 45.05±11.06 bpm, "increases gradually").
- **Contradictory:** Some POTS patients show a *delayed* tachycardia; initial transient tachycardia alone is a normal variant (Raj 2006).
- **Implementation:** Model ΔHR(t) = initial transient (shared with healthy) + sustained component rising over ~2–5 min with slow creep to 30+ min; POTS amplitude parameters on the sustained component.
- **Validation:** Simulated 1-min ΔHR overlap between groups; 5–10-min separation; tilt>stand.

### Claim 3.3 — BP trajectory in POTS: maintained or rising, not falling
- **Claim:** By definition no sustained drop ≥20/10 mmHg; many patients *increase* BP upright (hyperadrenergic subset: ΔSBP ≥10 mmHg); diastolic typically rises slightly.
- **Magnitude:** Okamoto 2024 protocol 1 (n=28): supine 109±3/67±2 → upright 115±5/73±2; orthostatic ΔSBP +7±3, ΔDBP +6±2 mmHg. Orjatsalo 2020: HUT SBP 111.1±13.4 (POTS) vs 105.7±15.3 (non-POTS).
- **Initial OH overlap:** Transient IOH does not preclude POTS diagnosis (CCS 2020); coexistence reported but not quantified in retrieved sources — flag as uncertain.
- **Evidence level:** E4.
- **Implementation:** POTS BP model: ΔSBP distribution centered ~0 to +8 mmHg (hyperadrenergic-weighted tail +10–30 mmHg); explicitly exclude the OH relationship; optional IOH transient module with its own incidence parameter.

### Claim 3.4 — Exaggerated ~0.1 Hz (Mayer-wave) HR and BP oscillations
- **Claim:** POTS patients show larger-amplitude 0.1-Hz oscillations of SBP and HR at rest and during HUT, with shortened SBP→HR phase lag, interpreted as an overactive/underdamped baroreflex loop; linked to brain-fog via CBFv oscillations.
- **Magnitude:** Geddes 2020 (n=28 POTS / 28 controls): 0.1 Hz amplitude higher, phase shorter (p<0.005), random-forest separable. Medow/Stewart 2014 (n=12/9): upright BP variability and LF power increased in POTS (24.3±4.1 mmHg²/Hz at 0.091 Hz vs control ~18.4±4.1).
- **Evidence level:** E3.
- **Sources:** Geddes J et al. 2020 (PubMed 32078525); Medow MS et al., Front Physiol 2014;5:234, DOI 10.3389/fphys.2014.00234.
- **Implementation:** baroreflex loop gain/delay parameters → increased Mayer-wave amplitude, shortened phase; this is an *altered relationship*, not a mean shift — high-value novel wearable feature.
- **Validation:** PSD at 0.04–0.13 Hz in simulated upright tachograms should exceed control distribution.

### Claim 3.5 — Recovery on lying down is fast
- **Claim:** HR falls rapidly on resuming supine posture; symptoms improve within minutes (a diagnostic feature).
- **Magnitude (n=113, 86 F, mean age 41.7; PMC3680982):** baseline 68.7±13.4 bpm; max tilt HR 109±16.9; recovery HR 84.2±20 bpm at 20 s (−23%), 78.5±18.9 at 1 min (−28%), 77.1±18.3 at 2 min (−29%). Adolescents (Orjatsalo 2020): post-tilt supine back to 74.9 bpm ≈ baseline within 1–3 min.
- **Evidence level:** E4.
- **Implementation:** recovery time constant ≪ onset time constant; ~50–70% of the ΔHR recovered within 20–60 s; no evidence of consistent overshoot/undershoot below baseline.
- **Validation:** Simulated tilt-down trace: HR within ~10 bpm of baseline by 2 min.

---

## 4. Cardiovascular Specifics

### Claim 4.1 — Stroke volume and cardiac output fall excessively on tilt
- **Claim:** Upright SV and CO are lower in POTS; orthostatic tachycardia is compensatory to inadequate venous return (thoracic hypovolemia).
- **Magnitude:** Fu 2010 (JACC 55:2858–68; n=19 completers; DOI 10.1016/j.jacc.2010.01.043, PubMed 20579544): upright SV and CO smaller, upright TPR greater than controls; LV mass 1.26 [1.12–1.37] vs 1.45 [1.34–1.57] g/kg ("small heart" / "grinch" phenotype); blood volume 60 vs 71 mL/kg. Stewart 2018 (JAHA 8:e008854, n=58 POTS/16 controls): **upright CO decreased in every POTS patient; SVR increased in every POTS patient**; low-flow subset had supine CO <4 L/min. Arnold 2013 (Neurology 80:1927–33, PMC3716342): resting SV 69±3 vs 85±7 mL (POTS vs healthy, p=0.047); resting CO 6.0±0.3 vs 5.6±0.5 L/min (NS); resting SVR 14.2±0.8 vs 13.1±1.0 (NS).
- **ME/CFS-POTS tilt cohort (van Campen 2025, J Clin Med 14:3648, n=226 POTS within ME/CFS):** %CO reduction bimodal with −15% cutoff separating hyperadrenergic-like (large HR rise, limited CO fall) from hypokinetic (large CO fall) patterns.
- **Evidence level:** E3/E4.
- **Implementation:** core altered relationship: upright SV ↓ (fraction ~−15 to −30% depending on subtype weight), HR = compensatory function of SV/preload, not an independent drive (except hyperadrenergic-central tail). SV–HR coupling is the key model equation.
- **Validation:** Tilt simulation: CO upright ↓ >10% vs control <10%; HR rise inversely correlated with SV reserve.

### Claim 4.2 — Regional venous pooling (Stewart flow phenotypes)
- **Claim:** Thoracic hypovolemia on tilt is exaggerated in all POTS variants; the *location* of pooling differentiates variants.
- **Magnitude (Stewart & Montgomery 2004, AJP-Heart 287:H1319, PMID 15117717; n=37 POTS 14 LFP/15 NFP/8 HFP, 12 controls, ages 14–21):** thoracic blood volume change at tilt: control −12±3%, low-flow POTS −25±5%, normal-flow −32±4%, high-flow −30±5%. Splanchnic volume: control +16±2%, LFP +29±3%, NFP +36±5%, HFP +17±8%. Supine: LFP ↓CI (3.0±0.3 vs 4.2±0.3 ICG l/min/m²), ↑TPR (45±8 vs 22±2), ↓blood volume (58±4 vs 72±3 mL/kg); NFP normal CI/TPR supine with splanchnic hyperemia; HFP ↑CI, ↓TPR, pelvic/leg pooling. Persistent splanchnic hyperemia during tilt in NFP (Stewart 2006, AJP-Heart 290:H665–73; PMC4513355).
- **Evidence level:** E3 (replicated within one lab; small n per subgroup).
- **Implementation:** regional compartment model: splanchnic vs pelvic/leg pooling weights as continuous subtype axes; this maps naturally onto wearable-observable surrogates (pulse pressure variability, PPG amplitude at finger vs forehead).
- **Validation:** Simulated orthostatic pulse-pressure narrowing larger in splanchnic-weighted samples.

### Claim 4.3 — Cerebral blood flow velocity and hypocapnia
- **Claim:** Upright CBFv is reduced in POTS, partly via postural hyperventilation/hypocapnia (subset ~25%, ETCO2 <30 Torr), partly via reduced CO; cerebral autoregulation results conflict across studies.
- **Magnitude:** Stewart 2018 (JAHA 8:e008854): hyperventilation subset ETCO2 <30 Torr on tilt; exogenous CO2 normalized HR, CO, SVR, CBFv and abolished POTS HR criteria — direct causal demonstration (E3). van Campen 2023 (n=226 ME/CFS-POTS, female; PMC10492011): largest ETCO2 fall and largest %CBF fall at end-tilt in the POTS subgroup vs normal-HRBP and controls (all p<0.0001); CBF–CO2 slope similar across groups (i.e., no intrinsic reactivity deficit). Novak 1998 / Low 1999: CBFv fall attributed to hypocapnic vasoconstriction; Ocon 2009: reduced CBFv even eucapnic → autoregulation abnormality; Schondorf 2005: normal autoregulation (contradiction). Medow 2014: increased CBFv *oscillations* despite normal mean CBFv.
- **Evidence level:** E3, with genuine contradiction (autoregulation intact vs impaired).
- **Implementation:** ETCO2 as a dynamic covariate (respiratory rate/sighing module); CBF symptom proxy (brain fog) driven by CO×CO2 product; keep autoregulation-gain as uncertain parameter.
- **Validation:** Simulated hyperventilation-tagged samples reproduce symptom flares and reversible normalization with CO2 clamp.

---

## 5. Autonomic Specifics

### Claim 5.1 — MSNA: exaggerated responses, normal-to-variable baseline
- **Claim:** Supine resting MSNA is usually normal in POTS; MSNA responses to orthostatic/baroreflex challenge are exaggerated in most studies.
- **Magnitude (Muenter Swift 2005, AJP-Heart, DOI 10.1152/ajpheart.01243.2004, PubMed 15863453):** MSNA response to Valsalva 48±6 vs 26±7 %baseline/mmHg (p=0.03); 30° HUT 208±30 vs 123±24 %baseline (p=0.03); 45° HUT 248±58 vs 137±27 (p=0.10); supine MSNA 16±5 vs 23±4 bursts/100 beats (NS); resting HR 82±4 vs 58±3 bpm (p=0.0001).
- **Contradictions (important):** Furlan 1998 reported *increased* resting MSNA with *blunted* tilt response (opposite pattern); Lambert 2008: tilt MSNA firing excessive but noradrenaline spillover NOT enhanced (nerve firing–release dissociation); Okamoto 2024: wide supine MSNA range, high-MSNA quartile defines hyperadrenergic phenotype with higher upright BP but **identical ΔHR**.
- **Evidence level:** E3 with heterogeneity — treat MSNA distribution as bimodal/heterogeneous, not uniformly elevated.
- **Implementation:** sympathetic drive = state-dependent gain (normal supine, exaggerated upright gain), plus a separate high-resting-MSNA tail (hyperadrenergic).

### Claim 5.2 — Cardiovagal baroreflex: modestly reduced supine gain; sympathetic baroreflex intact/greater
- **Claim:** Maximal cardiovagal baroreflex gain reduced ~25% supine; upright baroreflex curve distorted by sympathetic activation; digoxin (vagotonic) normalized supine deficit, pyridostigmine partial.
- **Magnitude:** Stewart 2021 (Hypertension 77:1234–44, DOI 10.1161/HYPERTENSIONAHA.120.16113, PMID 33423527): Gmax −25% vs controls, downward+left shift of sigmoid. Yeh 2024 (Sci Rep, DOI 10.1038/s41598-024-77065-7) corroborates baroreflex deficits. BUT: Muenter Swift 2005 sympathetic BRS trended *greater* (p=0.15); Fu 2010 and Galbreath 2011 found adult cardiovagal BRS NOT different from controls; pediatric studies show *increased* BRS predicting worse outcome (PMC5147897, n=45 children) and BRS>8.045 ms/mmHg predicting metoprolol response (AUC 0.912; Front Cardiovasc Med 2022, DOI 10.3389/fcvm.2022.930994). **Age- and method-dependent — genuinely contradictory literature.**
- **Evidence level:** E3 (conflicting).
- **Implementation:** baroreflex gain reduction as a modest parameter (−15 to −25%) with wide variance; do not hard-code; expose as latent.

### Claim 5.3 — Beta-receptor function: β2 vasodilation blunted; β1/central isoproterenol hypersensitivity in a subset
- **Claim:** Peripheral β2-mediated vasodilation is attenuated in POTS (n=9 vs 8: forearm flow +280±60% vs +400±70%, leg +120±20% vs +170±40%, p<0.001; Jacob 2006, Hypertension, PubMed 16461848); separately, some hyperadrenergic patients show marked tachycardia to isoproterenol doses inert in controls (Abe 2000; review-level evidence).
- **Evidence level:** E3.
- **Implementation:** β2 blunting → reduced vasodilatory reserve (pairs with neuropathic axis); isoproterenol sensitivity → steepened β1 dose-response in hyperadrenergic tail. Note: IST, not POTS, shows the dramatic 0.29±0.1 µg threshold (vs 1.27±0.4 controls) — do not conflate.
- **Limitations:** small n; two different receptor populations measured in different studies.

### Claim 5.4 — NET dysfunction as mechanistic proof-of-concept
- **Claim:** NET inhibition (reboxetine) in healthy subjects reproduces the POTS phenotype (orthostatic ΔHR >30 bpm); a NET loss-of-function mutation (Ala457Pro) found in one family.
- **Evidence level:** E3 (pharmacological phenocopy) / E1 (single-family genetics; not replicated as common cause).
- **Source:** Schroeder C et al. (reboxetine, cited in Benarroch 2012 review, PMC4664448; Front Physiol 2014;5:220).
- **Implementation:** NE reuptake efficiency as continuous modulator of upright NE and ΔHR.

---

## 6. Beyond Orthostasis

### Claim 6.1 — Resting physiology
- Resting HR elevated ~10–20 bpm: Muenter Swift 82±4 vs 58±3; Arnold 2013: 87±3 vs 66±4 bpm (p=0.001). Resting SV low (69±3 vs 85±7 mL), resting CO/SVR/MAP normal. Diurnal/circadian: nocturnal BP non-dipping associated with elevated skin sympathetic nerve activity (Liu 2023, J Hypertens 41:1029–36, DOI 10.1097/HJH.0000000000003465).
- **Evidence level:** E4 (resting HR elevation replicated).
- **Wearable:** resting/sleep HR is the easiest continuous discriminator (but weak alone: Welltory n=359 self-reported POTS, resting HR only ~+3 bpm with near-complete distribution overlap — resting HR alone cannot classify).

### Claim 6.2 — Exercise intolerance and exercise hemodynamics
- **Claim:** At matched absolute workload, POTS shows lower SV and higher HR; at matched *relative* workload (%VO2peak) HR response is normal — no intrinsic exercise HR dysregulation. Peak VO2 reduced in deconditioned subset but ~normal in semirecumbent testing (Arnold 2013: VO2max 24.5±0.7 mL/kg/min, similar to controls on placebo).
- **Training effect (Fu 2010; Fu 2011 Hypertension 58:167–75, PMID 21690484):** 3-month recumbent-based training ↑LV mass ~12%, ↑blood volume ~7%, ↓upright HR −9 [1–17] bpm; 10/19 no longer met POTS criteria; superior to propranolol.
- **Evidence level:** E3/E4.
- **Implementation:** exercise response = normal HR–%VO2peak relationship shifted by deconditioning/SV axis; training intervention = parameter trajectory (volume + LV mass + upright HR).

### Claim 6.3 — HRV
- **Claim (meta-analysis, E5):** Swai 2019/2020 (20 studies, 717 POTS/641 controls; PMC6936126, PubMed 31888497): HR mean difference +19.88 bpm (95% CI 15.24–24.52) after HUTT; time-domain HRV reduced (RR −162.89 ms; rMSSD −15.16 ms, both p<0.05); frequency-domain measures (LF, HF, LF/HF, normalized units) NOT significantly different (all p>0.05, I² 84–99%).
- **Interpretation:** rMSSD reduction is partly HR-driven (mathematical coupling). Do NOT model POTS as "low HRV" generically; model reduced time-domain variability with preserved-to-ambiguous frequency-domain changes. Adolescent HUT dynamics: larger HF attenuation and early LF surge in POTS (Orjatsalo 2020).
- **Contradictions:** LF higher (Stewart 2006) vs lower (Mallien 2012); HF lower (Ocon 2009) vs not (Freitas 2015) — explicitly unresolved.

### Claim 6.4 — Sleep disturbance
- **Claim:** Subjective sleep disturbance marked; objective actigraphic deficit modest; sleep-state misperception component.
- **Magnitude:** Bagai 2013 actigraphy (n=36/36; Auton Neurosci 177:260–5, DOI 10.1016/j.autneu.2013.02.021): sleep efficiency 73±13% vs 79±6% (p=0.01); WASO 63±33 vs 50±20 min (trend); objective SOL equal, subjective SOL 56±66 vs 13±9 min (p=0.001); WASO correlated with max standing HR (Rs 0.383, p=0.02); SOL correlated with upright NE (p=0.04). Bagai 2011 (J Clin Sleep Med 7:204): diminished QoL, restless sleep 53±30% vs 21±20% of days. RLS increased in POTS (PMC8020678).
- **Evidence level:** E3.
- **Wearable:** sleep efficiency/WASO/nighttime HR directly measurable; hyperarousal signature (elevated nocturnal HR, non-dipping) plausible feature.

### Claim 6.5 — Thermoregulation/heat intolerance
- **Claim:** Heat (hot showers, hot weather) is among the most universal symptom triggers; mechanism = cutaneous vasodilation compounding pooling/volume deficit; sudomotor abnormalities (reduced distal sweating on QSART/TST in 22–34%) coexist with hyperhidrosis reports in hyperadrenergic patients.
- **Evidence level:** E1/E2 (mechanistically coherent; quantitative heat-challenge studies in POTS not retrieved — gap).
- **Implementation:** ambient/skin temperature as orthostatic-stress gain modulator (vasodilatory shift of SVR setpoint).

### Claim 6.6 — Postprandial worsening
- **Claim:** ~53% report worsening after high-carbohydrate meals (survey n=8,919); small controlled study (n=12 POTS/13 controls) links postprandial exacerbation to increased GIP secretion (splanchnic vasodilator) after glucose (Breier et al., cited in Springer review 10.1007/s10286-022-00863-4).
- **Evidence level:** E2 (large survey) / E3 (small mechanistic).
- **Implementation:** meal events → transient splanchnic pooling pulse (~30–90 min post-carbohydrate) → ΔHR amplification; useful for wearable event-label correlation.

---

## 7. Wearable Evidence (empirical, not extrapolated)

**Honest status: the direct consumer-wearable POTS literature is thin (E2 at best); most "wearable signatures" are extrapolations from tilt-table physiology (E1/E2 for wearable context).**

| Study / source | Device | n | Finding | Level |
|---|---|---|---|---|
| Watson & Ward (Purdue, 2025 abstract; AbstractBook_Summer2025) | Corsano CardioWatch 2B, 30-day wear | 7 hEDS, 8 controls | Automated supine→stand detection from movement; mean standing HR increase 8.15–27.71 bpm (hEDS) vs 6.60–27.02 bpm (controls) — wide within-group variability; step count confounds HR increase | E2 (pilot) |
| Welltory dataset (welltory.com blog, n=359 self-reported POTS) | mixed PPG apps | 359 | Resting HR only ~3 bpm higher than other users; distributions overlap almost completely → resting HR alone useless for detection; orthostatic ΔHR needed | E2 (self-report label, unvalidated) |
| Cardiogram / device guidance | Apple Watch, Fitbit, Garmin, Pixel | — | Practical consensus: continuous PPG + symptom tagging captures ΔHR events; no peer-reviewed accuracy numbers for POTS classification retrieved | E0/E2 |
| Bagai 2013 | wrist actigraphy | 36/36 | Wearable-grade sleep metrics differ modestly (see 6.4) | E3 |
| NASA Lean Test (Bashir 2021, itjm.2021.1340; Lee 2020 J Transl Med 18:314) | pulse oximeter/clinical | — | 10-min passive stand replicates tilt physiology; ~33% of healthy controls meet ≥30 bpm at 10 min — sets false-positive expectation for any stand-test wearable algorithm | E2/E3 |

- **Observable signals most defensible from physiology:** (1) posture-transition ΔHR amplitude and time-to-peak (PPG+accelerometer); (2) morning>evening ΔHR asymmetry; (3) upright HR oscillation amplitude ~0.1 Hz; (4) reduced rMSSD upright; (5) elevated sleep HR / non-dipping surrogate; (6) symptom-tag correlation with ΔHR events; (7) postprandial HR bump; (8) HR spike on heat exposure; (9) HR recovery speed on lying down.
- **Not wearable-observable (must be simulated as latent):** BP (continuous cuffless unreliable), SV/CO, NE, blood volume, ETCO2, CBFv. Any synthetic wearable dataset for POTS should derive observable PPG/HR features from an underlying hemodynamic model, not generate HR alone.
- **Validation strategy:** compare synthetic ΔHR(t) distributions against Plash 2013 (tilt vs stand), Orjatsalo 2020 (minute-resolved), Cai 2021 (diurnal), Brewster 2012 (AM/PM), and Purdue pilot for free-living stand transitions; expect specificity limits (healthy tails exceed 30 bpm).

---

## 8. Heterogeneity, Demographics, Comorbidity, Medication Effects

### Claim 8.1 — Demographics
- ~80–90% female (Angeli 2024: 89.9%; Taub 2021 trial: 95.5%; reviews: 4:1–5:1 F:M; prevalence estimates 0.2%–1% US; 500k–3M affected).
- Onset predominantly adolescent/young adult: Angeli mean diagnosis age 21.0±5.6 yr; typical range 12–50; symptom onset often post-infectious (also post-COVID), post-pregnancy, post-trauma/surgery.
- Diagnostic delay ~5 years, ~7 physicians (survey data; Dysautonomia International/Shaw 2019, J Intern Med 286:438–48, DOI 10.1111/joim.12895).

### Claim 8.2 — Comorbidity overlap
- hEDS in POTS: 31% meeting 2017 criteria (n=91; PMC7282488); earlier estimates 12–22% (Wallman 2014: 18% vs 4% non-POTS autonomic clinic, 0.02% general population; J Neurol Sci 340:99). Conversely, OI in ~2/3 of hEDS, POTS in 41–49% of hEDS-with-OI (Roma 2018).
- ME/CFS overlap ~21%; autoimmune disorders ~16%; mast cell ~9% (Raj 2020 cohort figures, via Warwick review).
- GI symptoms 81.2% (Angeli); abnormal gastric emptying (rapid > delayed) associated independent of hypermobility.
- **Implementation:** comorbidity flags modulate subtype weights (hEDS → venous compliance ↑/neuropathic axis; post-viral → hypovolemic/neuropathic).

### Claim 8.3 — Medication effects on measurable physiology (for synthetic treatment scenarios)
| Drug | n / design | Physiological effect | Source / level |
|---|---|---|---|
| Propranolol 20 mg | n=54 crossover | ↓supine & standing HR (p<0.001); symptom score −4.5 vs 0 (p=0.044); 80 mg ↓HR more but symptom benefit LESS (−6 vs −2 au, p=0.041) | Raj 2009, Circulation 120:725–34, DOI 10.1161/CIRCULATIONAHA.108.846501 — E3 |
| Propranolol 20 mg (exercise) | n=11 POTS/7 controls | VO2max 24.5→27.6 mL/min/kg (p=0.024); peak HR 165→142 bpm; SV 67→81 mL (p=0.013); 80 mg propranolol / 100 mg metoprolol: no benefit | Arnold 2013, Neurology 80:1927–33 — E3 |
| Ivabradine 5–7.5 mg BID | n=22 crossover RCT (hyperadrenergic) | standing-supine ΔHR 13.1 vs 17.0 bpm (p=0.001); standing HR ~78 vs ~94 bpm; standing NE trend ↓ (p=0.056); no BP/bradycardia adverse effect | Taub 2021, JACC 77:861–71, DOI 10.1016/j.jacc.2020.12.029, PMID 33602468 — E3 (note: 3-min stand endpoint; baseline ΔHR only ~21 bpm — cohort borderline) |
| Midodrine 2.5–10 mg TID | n=20 crossover (12 neuropathic/8 hyperadrenergic) | Neuropathic: ↓HR (p=0.0002), ↑MAP (p=0.006), ↑calf VR (p=0.001), ↓calf venous capacitance; hyperadrenergic: no drug effect beyond placebo | Ross 2014, PMC3896075 — E3 |
| Midodrine 10 mg acute | n=9 POTS | standing HR 114→92.8 bpm (p<0.001); standing time unchanged (41 min) | Hoeldtke 2006, PubMed 17036177 — E3 |
| Pyridostigmine 30 mg | n=17 crossover | ↓orthostatic HR at 2–4 h; symptom improvement 4 h; no BP effect | Raj 2005, Circulation 111:2734–40, DOI 10.1161/CIRCULATIONAHA.104.497594 — E3 |
| Desmopressin | crossover | acute ↓orthostatic tachycardia + symptoms | Coffin 2012, Heart Rhythm 9:1484, PMID 22561596 — E3 |
| Fludrocortisone | — | Volume expansion rationale (hypovolemic axis); **no adequate RCT in POTS** — evidence gap (E0/E2 only); fludrocortisone RCT exists only for VVS prevention (Sheldon 2016, JACC 68:1) | E0 for POTS |
| Compression (abdominal+leg, 20–40 mmHg) | n≈25 HUT | tilt HR 109±19 (none) → 103±16 (leg) → 97±15 (abdo) → 92±14 (full) bpm (p<0.001), dose-dependent; SV and SBP better maintained | Bourne 2021, JACC 77:285–96, PubMed 33478652 — E3 |
| High-salt diet | controlled | ↑blood volume, ↓NE, ↓HR | Garland 2021 (cited in NAP workshop) — E3 |
| Exercise training 3 mo | n=19 completers | ↑LV mass 12%, ↑blood volume 7%, ↓upright HR −9 bpm; 53% remission of criteria | Fu 2010/2011 — E3 |

- **Beta-blocker pediatric meta-analysis (E5):** Deng 2019 (Front Pediatr 7:460): metoprolol response 79.5% vs 57.3% control, significant reduction in standing ΔHR.

### Claim 8.4 — Day-to-day variability
- Diurnal (Claim 1.2) + menstrual-cycle worsening + heat/meal/illness triggers + diagnostic-criteria positivity varying by time of day (100% AM vs 28–44% PM, Cai 2021) → synthetic data must include large within-subject variance; a fixed patient parameter set producing identical daily traces would be unrealistic.

---

## 9. Contrast Phenotypes (for synthetic-data discrimination tasks)

### 9.1 Classical orthostatic hypotension (cOH / nOH)
- Sustained SBP ↓≥20 or DBP ↓≥10 mmHg within 3 min of standing/≥60° tilt; HR rise typically blunted in neurogenic OH (ΔHR/ΔSBP ratio <0.5 suggests neurogenic). Mechanism: failure of TPR increase → SV low, BP low; HR compensation inadequate if autonomic failure (van Dijk 2020, PMC7082775; StatPearls NBK448192). Delayed OH: drop after 3 min (prodrome over minutes; ~54% progress to cOH over 10 yr).

### 9.2 Initial orthostatic hypotension (IOH)
- Transient SBP ↓≥40 and/or DBP ↓≥20 mmHg within 15 s of standing; recovery within 30–60 s; common in healthy young; requires beat-to-beat BP to detect; does NOT preclude POTS (Lei 2020, PMC7502506; PMC11292036). Normal active-stand physiology includes a transient dip; PPG-only wearables cannot observe it.

### 9.3 Vasovagal syncope (VVS) — time course
- Trigger (prolonged standing, pain, heat) → venous pooling → SV falls first → slow BP decline over **minutes** → presyncopal symptoms ~155 s (25–414 s) before measurable changes; CBFv decline begins ~67 s (9–198 s) BEFORE MAP falls (Dan 2002, JACC 39:1039–45) → cardioinhibition late (≤1 min before syncope; asystole ≥3 s in ~30% of tilt-induced VVS, mean 9.1±6.4 s) → LOC ~8 s after circulatory standstill → rapid recovery on supine, prodrome 1–5 min total. Contrast with POTS: sustained tachycardia, no collapse; VVS: late bradycardia+hypotension collapse. ~1/3 of POTS patients also have positional VVS episodes (overlap, not exclusion).
- **Evidence level:** E4 (replicated tilt physiology); model as separate state machine with SV-fall-first dynamics.

---

## 10. Key Contradictions / Null Findings (explicit)

1. **MSNA resting level:** normal (Muenter Swift 2005, Bonyhay 2004, Lambert 2008, Fu 2010) vs elevated (Furlan 1998) vs low (Jacob 2019). → Model resting sympathetic tone as heterogeneous distribution.
2. **Baroreflex sensitivity:** reduced ~25% (Stewart 2021, Yeh 2024) vs unchanged in adults (Fu 2010, Galbreath 2011) vs *increased* in children (PMC5147897). Age-dependent.
3. **Cerebral autoregulation:** impaired (Ocon 2009) vs intact (Schondorf 2005); CBFv fall partly explained by hypocapnia alone (Novak 1998, Low 1999).
4. **Frequency-domain HRV:** meta-analytically null (Swai 2019); individual studies contradict in both directions.
5. **HR criteria specificity:** 30-bpm threshold fails at longer durations in controls (Plash 2013: 80% positive at 30 min tilt) — the criterion is time-window-bound.
6. **Subtype distinctness:** symptoms do NOT discriminate phenotypes (Angeli 2024 null); overlap in 53% — argues strongly for continuous composable model.
7. **Deconditioning as cause vs consequence:** Burkhardt — no clear connection between deconditioning and POTS in adolescents; Arnold 2013 — near-normal VO2max in semi-recumbent POTS; vs Fu 2010 small-heart/hypovolemia responsive to training. Competing causal directions unresolved.
8. **Taub 2021 ivabradine trial:** mean baseline standing ΔHR ~21 bpm (below POTS threshold on 3-min stand) — caution using its ΔHR effect sizes as representative of severe POTS.

---

## 11. Implementation Recommendations (summary)

1. **Core generative model:** hemodynamic state machine with compartments (thoracic/splanchnic/leg volume), SV→HR baroreflex-mediated compensation with a gain that is *state-dependent* (normal supine, exaggerated upright), plus 3 continuous subtype axes (neuropathic: leg vasoconstriction gain ↓; hypovolemic: total volume −10–15%; hyperadrenergic: central drive ↑, upright BP ↑) sampled with Angeli-2024-like joint probabilities.
2. **Continuous over categorical everywhere:** ΔHR, NE, volume deficit, denervation severity all continuous; categorical POTS label = threshold crossing of ΔHR trajectory within 10-min window (time-of-day dependent).
3. **New mechanisms beyond parameter shifts:** diurnal modulation; postprandial pooling pulse; heat vasodilation gain; respiratory/hypocapnia module (25% of patients); IOH transient module; VVS state machine (separate phenotype); 0.1-Hz oscillation gain/phase alteration (baroreflex loop dynamics).
4. **Wearable synthesis:** generate underlying hemodynamic+autonomic state → derive PPG-HR, rMSSD, posture-transition events, sleep HR/dipping, symptom-tag correlation. Resting-HR-only discrimination must fail (Welltory constraint); posture-transition ΔHR with morning weighting must succeed partially (target realistic, not perfect, AUC).
5. **Validation battery:** Plash 2013 tilt-vs-stand trajectories; Orjatsalo 2020 minute-resolved HR; Brewster 2012 & Cai 2021 diurnal; Angeli 2024 subtype joint distribution & standing NE; Raj 2005 volume deficit; recovery half-time (PMC3680982); Bourne 2021 compression dose-response as intervention sanity check.

---

*Compiled Pass 1 (discovery). Known retrieval gaps: Fu 2010 SV/CO exact tilt percentages; Jacob 2000 full arm-spillover table; Breier postprandial GIP effect sizes; Stewart 2018 subgroup CBFv percentages; Bagai 2016 polysomnography detail. Flag for Pass 2 targeted extraction.*
