# OCPE Disease Evidence Base — Systemic Inflammation & Autoimmune Physiology

**Author role:** Autoimmune/Inflammation Scientist (Pass 1 discovery).
**Evidence scale:** E0 hypothesis · E1 mechanistic (preclinical/theory) · E2 observational human · E3 controlled human experimental · E4 replicated quantitative · E5 meta-analysis/consensus.
**Honesty rule applied throughout:** effects with only mechanistic support are labeled `LATENT-ONLY` — OCPE may model them as internal states but must NOT emit a fabricated observable wearable signal for them.

---

## 1. Executive synthesis (read first)

1. The **strongest, most quantitative wearable-relevant evidence for "systemic inflammation"** comes from three independent pillars that agree in direction and rough magnitude:
   - **Controlled human endotoxin (LPS) challenges (E3/E4):** HR +40–55% at peak (~3–6 h post 2 ng/kg IV), core temperature +1–1.75 °C peaking 3–4 h, HRV (SDNN/RMSSD/pNN50/HF) sharply depressed 1–6 h, all normalizing by ~8–24 h. Dose-response: vital signs unchanged ≤0.5 ng/kg; HRV changes from ~1 ng/kg.
   - **Population meta-analysis of inflammation–HRV (E5, Williams 2019):** small but robust *inverse* correlations between CRP/IL-6 and SDNN/HF/RMSSD; CRP–SDNN and CRP–RMSSD each pooled from >16,000 datasets. TNF-α associations were **null** — an important negative result.
   - **Real-world wearable cohorts (E2):** RA and IBD flares show RHR +5–6 bpm, mean HR +6 bpm, nighttime HR +3–5 bpm, RMSSD circadian mesor −25%, and step reductions (~−500 to −850/day), detectable up to 4–7 weeks before clinical flares.
2. **Fever→HR coupling is replicated quantitative (E4):** ~12.3 bpm/°C in children (largest study, n=188,635 attendances), age-dependent 8.7–13.7 bpm/°C; classic adult heuristic ~10 bpm/°C is consistent but less precisely measured.
3. **Fever metabolic cost is classic E4:** +10–13% resting energy expenditure per °C (Du Bois).
4. **Sleep↔inflammation is bidirectional but effect sizes are small (E5):** sleep disturbance → IL-6 ES≈0.20, CRP ES≈0.12 (Irwin 2016, 72 studies, >50,000 participants). Typhoid vaccination → increased nighttime awakenings (E3, PSG, placebo-controlled).
5. **Autoimmune disease-specific autonomic findings are consistent but modest and confounded (E2/E5):** RA RMSSD SMD −0.90, HF SMD −0.78 vs controls (Provan 2018 meta-analysis); SLE SDNN ~69 vs ~128 ms in one classic Holter study (all patients on corticosteroids — major confound); Sjögren's autonomic dysfunction prevalence ~36%, associated with fatigue, relative tachycardia especially on standing.
6. **Medication confounds are pervasive and must be modeled:** corticosteroids (tachycardia/palpitations, insomnia, hyperglycemia; paradoxical bradycardia with high-dose IV pulse; acute HRV *increase* with dexamethasone in animal work), beta-blockers (blunt HR/HRV — actively excluded from the RA wearable cohort), biologics (tocilizumab normalizes vascular/autonomic signals within months).
7. **LATENT-ONLY effects (no empirical wearable signal exists — do not fabricate):** endothelial dysfunction→PPG waveform/stiffness-index changes from inflammation; circadian temperature amplitude blunting by low-grade inflammation; cytokine-driven sickness behavior as an independent wearable signal (manifests only via HR/HRV/steps/sleep already covered).

---

## 2. Controlled human inflammatory challenge studies (anchor domain)

### Claim C2.1 — IV endotoxin produces a stereotyped, quantified, transient physiological storm
- **Domain:** Acute systemic inflammation (experimental model of sepsis/SIRS)
- **Variables:** HR, core temperature, HRV (SDNN, RMSSD, pNN50, HF, LF/HF), MAP, WBC, cytokines
- **Mechanism:** LPS→TLR4→TNF-α (peak ~1–2 h)→IL-6/IL-1β/IL-8 (peak ~2–4 h)→ vagal afferent activation + central autonomic drive + direct pyrogenic/cardiostimulatory effects; cholinergic anti-inflammatory pathway (Tracey inflammatory reflex) provides efferent vagal restraint.
- **Direction/Magnitude:**
  - HR: +47±3% to +54±2% at peak (n=16, 2 ng/kg E. coli O:113; Dorresteijn/PMC4098335); typically reaches SIRS tachycardia criterion.
  - Temperature: monophasic fever onset 1–2 h, peak **+1–1.75 °C at 3–4 h** (38.1–38.8 °C depending on hydration), resolve 8–12 h (Duke review; Pernerstorfer 1999: 38.5±0.2 °C at 4 h after 4 ng/kg).
  - HRV: significant ↓SDNN, ↓pNN50, ↓RMSSD, ↓HF within 1–6 h at 2 ng/kg; pNN50/RMSSD also ↓ at 1 ng/kg; no HRV change at ≤0.5 ng/kg; normalize by ~24 h (Jan et al., 30 young adults, 2 ng/kg; dose-response study PMC4297222).
  - MAP: falls ~15%.
- **Timescale / trigger-response-recovery:** cytokines 1–3 h → HR/temp/HRV 2–6 h → full recovery 8–24 h. This is the canonical **acute inflammation impulse response** for OCPE: onset ~1 h, peak 3–5 h, tau ≈ 8–12 h.
- **Population:** healthy young adult volunteers (n typically 15–75 per study).
- **Wearable modality:** wrist/ring PPG HR + skin temperature + HRV fully capture this magnitude of signal. Confirmed with a continuous single-lead ECG wearable (HealthPatch) in an endotoxemia trial (Koeneman et al., Radboudumc — HRV changes tracked the immune response; hypothesis: ↑LF:HF as immune marker).
- **Evidence level: E3–E4** (replicated across dozens of independent endotoxin units: NIH CC-RE, Radboud, Vienna, Duke).
- **Sources:** Dorresteijn et al., Crit Care 2010, PMC4098335 (PMID 20398383); Jan BU et al., Ann Surg 2009 (described in d-nb.info/1274912075/34); PMC4297222 (dose-response 0.1–2 ng/kg); Pernerstorfer et al., Clin Pharmacol Ther 1999;66:51-57; Fullerton/Suffredini Duke review (dukespace.lib.duke.edu); Koeneman et al., SISNA abstract 2018 (sisna.org).
- **Contradictory/nuances:** hydrocortisone pre-treatment blunted cytokines but **did not block** the HRV depression (Alvarez et al. human study — cited in PMC2763816), i.e., even low cytokine levels can depress HRV; LF/HF behavior is inconsistent across studies (do not model LF/HF as "sympathovagal balance" — its construct validity is contested).
- **Limitations:** young healthy males over-represented; supraphysiological cytokine peaks vs chronic autoimmune inflammation; low doses (0.06–0.8 ng/kg) raise cytokines **without vital-sign changes** — direct evidence that low-grade inflammation sits BELOW the acute-vitals detection threshold, so chronic autoimmune signal must be sought in HRV/RHR distributions, not fever-scale effects.
- **Implementation recommendation (CORE):** implement a generic `acute_inflammation` impulse response: multiplicative HR gain peak +40–55%, temperature +1–1.75 °C, HRV (RMSSD/SDNN) gain ~0.4–0.7, onset 1–2 h, peak 3–5 h, recovery 8–24 h. Severity parameter = log-dose analog.
- **Validation:** replay against digitized Jan 2009 / Dorresteijn 2010 time series; RMSE on HR and temperature trajectories.

### Claim C2.2 — Typhoid vaccination is a milder, well-tolerated controlled inflammatory stimulus with measurable autonomic and behavioral effects
- **Domain:** Vaccination-challenge (subclinical inflammation)
- **Mechanism:** S. typhi vaccine → IL-6/TNF-α ↑ (≈doubling) → vagal afferent → insula/dACC interoceptive activation → sickness behavior (fatigue, confusion, impaired concentration, mood lowering).
- **Magnitude/time course:** IL-6 and TNF-α roughly **double, peaking 6–8 h** post-vaccination; CRP also rises; granulocytosis (Harrison et al. time-course, Brain Behav Immun 2013). Harrison 2009: IL-6 rise correlated with depressed mood and dACC/anterior insula fMRI activity.
- **Sleep:** late-afternoon typhoid vaccination → **increased nighttime awakenings** on PSG vs placebo (reviewed in Besedovsky et al., Physiol Rev 2019, DOI 10.1152/physrev.00010.2018). Hepatitis A and H1N1 influenza vaccination produced **no gross sleep change** (null finding, no placebo control in those studies).
- **Evidence level: E3.** Population: healthy volunteers.
- **Sources:** Harrison NA et al., Brain Behav Immun 2009;23:1165-71; time-course study Brain Behav Immun 2013 (sciencedirect S088915911300007X); Besedovsky L et al., Physiol Rev 2019;99:1325-1380.
- **Implementation recommendation (CORE):** `mild_inflammation` state: IL-6-analog ×2, small HRV depression (scaled ~10–20% of the LPS impulse), fatigue latent variable ↑, sleep fragmentation (awakenings +), duration 12–48 h. Do NOT emit fever at this level.
- **Validation:** none directly wearable; use magnitude as the low end of the dose-response anchored by C2.1.

### Claim C2.3 — Endotoxin acutely induces insulin resistance (metabolic arm)
- **Domain:** Metabolic
- **Mechanism:** TNF-α/IL-6/cortisol/FFA → adipose inflammation, impaired insulin signaling.
- **Magnitude:** insulin sensitivity index (Si, FSIGT) **−30%** (3.17±1.66 → 2.06 ×10⁻⁴ [µU·ml⁻¹·min⁻¹], p<0.005) at 24 h after 3 ng/kg IV LPS; HOMA-IR +39–46% at 24 h; β-cell function unchanged (n=20 healthy, Mehta et al., Diabetes 2010; PMC2797919, DOI 10.2337/db09-0367).
- **Evidence level: E3.**
- **Wearable relevance:** none direct (LATENT-ONLY for wearables); relevant to OCPE metabolic latent state and to steroid-confound modeling (steroids worsen insulin resistance).
- **Implementation recommendation:** latent metabolic state only; optionally couple to reduced glucose tolerance in downstream modules; NO fabricated CGM signal.

### Claim C2.4 — Fever increases resting energy expenditure ~10–13%/°C
- **Domain:** Metabolic/thermoregulation. **Magnitude:** +10–13% REE per °C (Du Bois classic; reproduced in critical-care and fever literature). **Evidence: E4 (consensus heuristic).**
- **Implementation recommendation (CORE):** REE multiplier = 1 + 0.11×(Tcore−37°C), bounded; drives elevated resting HR coherently with C4.1.
- **Limitation:** interindividual variability high (measured/predicted REE ratio 0.44–1.53 in critical illness); treat as population prior.

---

## 3. Inflammatory reflex & cytokine–autonomic coupling

### Claim C3.1 — Vagal afferents signal peripheral inflammation to the CNS; efferent vagus restrains inflammation (inflammatory reflex)
- **Mechanism (Tracey):** cytokines activate vagal afferents → nucleus tractus solitarius → sickness behavior; efferent vagal acetylcholine → α7nAChR on macrophages suppresses TNF.
- **Evidence: E1–E3.** Human support is *indirect*: HRV (vagal index) inversely correlates with CRP/IL-6 (E5, C3.2); vagus nerve stimulation reduced disease activity and TNF in a small RA pilot (Koopman et al. 2016, PNAS — E3, n=17, no sham control in phase 1). **Do not overstate:** the causal HRV→inflammation direction in humans is not established.
- **Sources:** Tracey KJ, Nature 2002;420:853-9 (DOI 10.1038/nature01321); Huston & Tracey, J Intern Med 2011;269:45-53; Koopman FA et al., PNAS 2016;113:8284-9.
- **Implementation recommendation (CORE latent):** model vagal tone as bidirectional coupling: inflammation↓vagal outflow (observable via RMSSD/HF depression); vagal tone weakly feeds back on inflammation amplitude. Label the feedback gain as E1.

### Claim C3.2 — Higher CRP/IL-6 associated with lower HRV in the general population (small, robust effect)
- **Domain:** Cross-sectional/longitudinal population physiology.
- **Magnitude (E5, Williams et al. 2019, Brain Behav Immun 80:219-226, PMID 30872091, DOI 10.1016/j.bbi.2019.03.009; 51 studies in meta-analysis):** consistent **negative** associations between inflammatory markers and HRV; **SDNN and HF-HRV most robust**; CRP–SDNN and CRP–RMSSD each pooled from >16,000 datasets. Effect sizes are small (pooled |r| on the order of 0.1) — visible only at population scale or as within-person longitudinal deviation.
- **KEY NULL:** TNF-α vs SDNN/RMSSD and IL-1 vs SDNN associations were **not significant** in the same meta-analysis (small n, likely underpowered) — do not model cytokine-specific HRV signatures.
- **Supporting:** CARDIA study (Sloan 2007, Mol Med 13:178-84: RR variability inversely related to CRP/fibrinogen); Sajadieh 2004 Eur Heart J 25:363-70 (↑HR and ↓HRV with subclinical inflammation, no heart disease); Jarczok 2014 J Intern Med (low HRV predicts ↑CRP 4 years later — supports bidirectionality).
- **Contradictory:** in MDD cohorts with careful vagus imaging, cytokine–HRV correlations were absent (PMC12140965) — heterogeneity is real.
- **Implementation recommendation (CORE):** chronic `low_grade_inflammation` latent state: RMSSD/SDNN gain 0.85–0.95, resting HR +1–4 bpm, as a slow (weeks–years) offset. Use within-person deviation semantics, not absolute thresholds.
- **Validation:** compare synthetic population distributions against Williams 2019 pooled correlations.

---

## 4. Thermoregulation

### Claim C4.1 — HR rises ~9–12 bpm per 1 °C of temperature elevation
- **Magnitude:** children: **+12.3 bpm/°C (95% CI 12.2–12.4), age-dependent 13.7 (youngest) → 8.7 (oldest) bpm/°C** (Heal et al., Emerg Med J 2022; PMC9605188; n=188,635 ED attendances — E4, largest dataset). Classic adult heuristic ~10 bpm/°C; adult-specific quantitative literature is thinner (E2/E4).
- **Mechanism:** increased metabolic rate (Q10 effect) + autonomic drive; dehydration adds independent tachycardia in real illness (confound).
- **Implementation recommendation (CORE):** HR_fever gain = 10 bpm/°C (adult default; age-interpolated 8.7–13.7 if pediatric modeled), additive with direct cytokine HR effect.
- **Validation:** in synthetic febrile episodes, HR(t)−T(t) regression should recover the planted slope.

### Claim C4.2 — Fever time course in controlled inflammation (see C2.1)
Onset 1–2 h, peak +1–1.75 °C at 3–4 h, resolution 8–12 h (E3/E4). Acetaminophen blunts peak by ~0.9 °C without blunting cytokines (Pernerstorfer 1999) — antipyretics decouple temperature from inflammation; relevant confound if OCPE models self-medication.

### Claim C4.3 — Low-grade inflammation and basal temperature / circadian amplitude
- **Status: LATENT-ONLY (E0–E1).** Mechanistically plausible (cytokines reset set-point, blunt circadian amplitude) and Oura-class wearables detect **skin**-temperature deviations of +0.6–1 °C during infections (C8.3), but there is NO quantified human evidence linking chronic low-grade autoimmune inflammation to a specific basal-temperature shift or circadian amplitude change detectable by wearables. Model as latent with no direct observable beyond what acute-fever logic produces.

---

## 5. Sleep ↔ inflammation

### Claim C5.1 — Sleep disturbance elevates inflammatory markers (small effect, meta-analytic)
- **Magnitude (E5):** Irwin et al. 2016 (Biol Psychiatry 80:40-52, DOI 10.1016/j.biopsych.2015.05.014; 72 studies, >50,000 participants): sleep disturbance → CRP **ES 0.12**, IL-6 **ES 0.20**. Experimental acute sleep deprivation effects on circulating markers are **inconsistent/null** in meta-analysis; more consistent at cellular level (NF-κB activation after one night of partial sleep loss, Irwin 2008 Biol Psychiatry 64:538-40, PMID 18561896 — E3, small n).
- **Implementation recommendation:** slow latent coupling: chronic poor sleep → low_grade_inflammation + (ES ~0.1–0.2 SD units over weeks). Do not implement acute one-night cytokine spikes as reliable.

### Claim C5.2 — Inflammation disrupts sleep (dose-dependent biphasic)
- **Evidence (E3/E4):** Pollmächer-series human endotoxin studies: **very mild** host-response activation → NREM enhancement; stronger responses (fever, large cytokine rises) → sleep disruption. Typhoid vaccination → ↑ awakenings (C2.2). Influenza/HepA vaccines → no gross sleep change (null).
- **Implementation recommendation (CORE):** inflammation severity → sleep fragmentation: awakenings ↑, WASO ↑ at moderate-to-high severity; at very mild severity, small ↑ SWS. Magnitude priors are qualitative — flag uncertainty.
- **Sources:** Besedovsky Physiol Rev 2019 (DOI 10.1152/physrev.00010.2018).

---

## 6. Autoimmune disease-specific autonomic findings

### Claim C6.1 — RA: cardiac parasympathetic dysfunction vs healthy controls (meta-analytic)
- **Magnitude (E5):** Provan et al. 2018 (Semin Arthritis Rheum 48:134-140, PMID 29291895, DOI 10.1016/j.semarthrit.2017.11.010; 35 case-control studies): RA vs controls **RMSSD SMD −0.90 (95% CI −1.35, −0.44)**; **HF SMD −0.78 (−0.99, −0.57)**; SpA effects smaller (RMSSD SMD −0.34, NS for HF). Ewing-protocol parameters lower in RA except Valsalva.
- **Representative raw values (E2):** 24-h Holter: SDNN 98.4±24.6 vs 142.3±28.4 ms; RMSSD 24.8±8.2 vs 38.6±10.4 ms (n=80 vs 80; low-tier journal — use as illustrative, not primary); CRP>5 mg/L subgroup drives most of the deficit (Saramet 2023, J Clin Med, PMC10743610: all Holter HRV parameters negatively correlated with CRP; RA with CRP≤5 mg/L ≈ controls — **inflammation dose-dependence within disease**).
- **Resting HR:** elevated in RA (Piha & Voipio-Pulkki 1993, Br J Rheumatol 32:212-5) — partly attributable to deconditioning (confound).
- **Disease-activity correlation:** HRV related to DAS28/CRP (Anichkov 2007 Int J Clin Pract 61:777-83; Adlan 2017 Auton Neurosci 208:137-145).
- **Implementation recommendation (CORE, disease-modulated):** RA active state: RMSSD gain ~0.6–0.7, RHR +3–6 bpm relative to personal remission baseline (aligns with wearable flare data, C8.1); remission with controlled CRP → near-normal gains. Tie to inflammation level, not to the RA label per se.

### Claim C6.2 — SLE: large HRV reduction reported, but heavily confounded
- **Magnitude (E2, classic):** Laghi-Pasini era Holter study (n=23 SLE vs 14 controls; PMID 8646226): SDNN 69.4 vs 127.7 ms; pNN50 16.4 vs 26.0; LF 8.34 vs 34.97; HF 3.21 vs 12.18. Autonomic dysfunction prevalence 78–91% by SDNN/LF criteria. **All patients on corticosteroids, 10/23 on cyclosporine — direction likely real, magnitude inflated/unattributable.**
- Recent work: hsCRP/MPO inversely related to sample entropy; fatigue positively related to LF/HF (n small, women with mild/inactive SLE; PMC7766283). 12-week aerobic training did **not** change HRV (null, E3, small n). Cardiovascular autonomic dysfunction also documented with COMPASS-31 in SLE (Zinglersen 2021, Lupus Sci Med, DOI 10.1136/lupus-2021-000507).
- **Implementation recommendation:** SLE as RA-like autonomic pattern with wider variance; keep medication state explicit. Evidence supports direction (↓HRV, ↑HR) but not a trustworthy disease-specific magnitude → use generic inflammation-driven gains with SLE multiplier ~1.0–1.5 and flag as E2.

### Claim C6.3 — Primary Sjögren's: mild-moderate autonomic dysfunction, fatigue-linked
- **Magnitude (E2, best cohort):** KISS prospective cohort (n=154 pSS vs 154 matched controls; Korean J Intern Med 2016; PMC5214725): SDNN 31.2 vs 24.4 ms (p=0.001), RMSSD 25.7 vs 17.1 (p=0.005), HF 132.0 vs 63.2 ms² (p<0.001); **autonomic dysfunction prevalence 35.7%**; decreased parasympathetic activity 41.6%; associated with ESSPRI **fatigue** (p=0.024), NOT with glandular signs or ESSDAI.
- **Relative tachycardia on standing:** standing RR 688 ms vs 781 ms controls (≈87 vs 77 bpm) (Cai et al. 2008, Arthritis Res Ther 10:R31, PMID 18328102, PMC2453776; n=27 vs 25). Contradictory studies exist (Tumiati 2000 found non-significant trends, n=16) — heterogeneity acknowledged (PMC8350514 review).
- **Mechanism hypothesis:** anti-M3 muscarinic receptor autoantibodies (E1, unproven).
- **Implementation recommendation:** Sjögren's profile = moderate parasympathetic withdrawal + blunted orthostatic LF response; fatigue latent coupled to autonomic dysfunction. E2 confidence.

---

## 7. Vascular / endothelial domain

### Claim C7.1 — Acute systemic inflammation causes transient endothelial dysfunction and increased arterial stiffness
- **Evidence (E3):** typhoid vaccination in healthy humans acutely impairs brachial flow-mediated dilation, recovering over 24–48 h (Hingorani et al., Circulation 2000;102:994-9 — the canonical human experiment). Chronic: RA FMD/PWV abnormal; **tocilizumab (IL-6R blockade) reversed it in 11 women: FMD 3.3±0.8 → 6.4±1.3% (3 mo) and PWV 8.2±1.2 → 7.0±1.0 m/s (6 mo)** with hsCRP 20.4 → 3.9 mg/dL (pilot, E3, no control arm).
- **Wearable observability: NONE demonstrated.** PPG-derived stiffness index is not validated against inflammation-driven vascular change. **LATENT-ONLY: do not emit a PPG waveform/stiffness signal in OCPE for inflammation.** The only wearable-visible vascular consequence flows through HR/HRV (autonomic) already covered.
- **Recommendation:** vascular state latent; optionally couple to BP in a cuff-based extension module (out of wearable scope).

---

## 8. Wearable evidence in inflammatory disease (KEY)

### Claim C8.1 — RA flares are detectable and partially predictable from consumer wearables
- **Study:** RA Forecast (Sharma/Danieletto/Hirten et al., Sci Rep 2025, DOI 10.1038/s41598-025-29748-y; PMC12486041; n=53, 88.7% female, Apple Watch 35/Fitbit 17/Oura 3; 8,183 person-days; inflammatory flare = CRP>5 mg/dL ±7 d window; symptomatic flare = RAPID-3).
- **Magnitudes (inflammatory flare vs remission, E2→ approaching E3 design rigor):**
  - RHR **63.21±2.22 vs 58.24±2.15 bpm (+5.0, p<0.0001)**
  - Mean daily HR 81.42 vs 75.44 bpm (+6.0); day HR +6.5; night HR +5.5
  - RMSSD circadian **mesor 21.5 vs 28.7 ms (−25%, p<0.001)**; circadian amplitude of RMSSD blunted (1.05 vs 3.66 ms)
  - Steps: NS for inflammatory flares (7,737 vs 8,730); **−515 steps/day for symptomatic flares** (p=0.004)
  - Prediction: combined metrics AUC ~1.00 / F1 0.95 at **28 days before flare** (caveat: imbalanced within-subject data, F1 emphasized; not yet replicated at individual level).
- **Limitations (author-stated):** CRP imputation window, medication effects uncontrolled (9.4% steroids, 37.7% biologics), 3 device types, sleep data not yet analyzed, preprint-stage at time of reporting.
- **Implementation recommendation (CORE validation target):** OCPE flare simulation should reproduce: RHR +3–6 bpm, night HR +3–5 bpm, RMSSD mesor −20–30%, steps −5–10% (symptomatic only), slow ramp over 2–4 weeks preceding flare.

### Claim C8.2 — IBD flares: similar autonomic signature, longer lead time
- **Evidence (E2):** Hirten et al., Gastroenterology 2025 (DOI 10.1053/j.gastro.2024.12.024; n=309 IBD across 36 states, Apple Watch/Fitbit/Oura): HR and RHR higher, steps lower during inflammatory and symptomatic phases; changes detectable **up to 7 weeks before flare**; per-day Apple Watch model AUC 0.98 at 49 days pre-flare; SpO2 unchanged (null — useful negative). Pilot UC HRV-patch study (n=15, 9 months; Hirten 2021, Inflamm Bowel Dis 27:1576-84, DOI 10.1093/ibd/izaa323): HRV correlated with stress and UC activity, predicted flares.
- **Independent Fitbit cohort (Yvellez, n=91 IBD):** resting HR +1 bpm → **OR 1.05 for next-day pain** (p<0.001); HRV, steps, awakenings NOT predictive of next-day pain (useful nulls).
- **Recommendation:** confirms the generic inflammation→wearable signature transfers across autoimmune diseases → supports a **single generic `systemic_inflammation` core state** with disease-specific wrappers.

### Claim C8.3 — Infection/fever wearable studies (transferable calibration anchors)
- **Mishra et al., Nat Biomed Eng 2020 (DOI 10.1038/s41551-020-00640-6, PMID 33208926):** n=5,262 cohort, 32 COVID+; **81% (26/32) had detectable HR/steps/sleep alterations; 63% detectable pre-symptom; 4 cases ≥9 days early.**
- **DETECT/Quer et al., Nat Med 2020:** n=30,529; symptoms-only AUC 0.71 → +sensor AUC **0.80**.
- **Radin et al., JAMA Netw Open 2021:** COVID RHR trajectory — initial dip ~9 days post-symptom-onset, then prolonged elevation; mean **79 days to RHR normalization** (vs 4 days non-COVID ILI); **13.7% had RHR >5 bpm above baseline for >133 days** — direct quantitative template for **post-inflammatory recovery tails** (long COVID analog for slow autoimmune flare resolution). COVID pre-symptomatic RHR median **+7 bpm, 3–7 days before symptoms** (Hopkins analysis of DETECT subset).
- **Oura/TemPredict (Sci Rep 2020, DOI 10.1038/s41598-020-78355-6):** finger skin temperature nightly deviation tracked fever onset (+0.63 °C mean at symptom onset window); fever-like temperature anomaly in **93% of cases within 7 days pre-symptom**.
- **COVI-GAPP (Ava bracelet, Risch et al., BMJ Open 2022):** HR, HRV, HRV-ratio, wrist skin temperature, RR all changed; RNN detected **68% of COVID cases 2 days pre-symptom**.
- **Radin et al., Lancet Digit Health 2020 (Fitbit ILI, n=47,250):** RHR+sleep data improved ILI prediction (correlation 0.84–0.97 with CDC estimates).
- **Recommendation (CORE):** these give the best-quantified acute-infection wearable impulse: RHR +5–7 bpm, skin temp +0.5–1 °C, sleep duration initially ↑ then disrupted, steps ↓; recovery time constant days-to-weeks (median ~2.5 months for severe COVID tail). Use as upper bound; autoimmune flares are the ~50–70% scaled version per C8.1.

### Claim C8.4 — Gout flares: step-count suppression
- **E2:** Fitbit Charge HR2, n=44 gout patients: **−841 steps/day during flares** (5,900±4,071 vs 6,972±5,214, p<0.0001); sleep unchanged (null) (Arthritis Res Ther pilot, reported via hcplive). Pain-localized flares primarily suppress activity, not sleep/autonomics — supports modeling joint-pain→activity pathway separately from systemic inflammation.

---

## 9. Medication confounds (must be explicit OCPE modifiers)

### Claim C9.1 — Corticosteroids
- **HR:** oral prednisone → tachycardia/palpitations, dose-dependent arrhythmia risk; **high-dose IV methylprednisolone pulse → paradoxical bradycardia** (case-report level, E2; Stroeder 2015, PMC4561462: HR 50 bpm 5 h after dose, Naranjo 7). Dexamethasone acutely **increased** HRV in mice (E1, PMC2763816) — direction in humans unverified.
- **Sleep:** insomnia is a common labeled effect (consensus, E5-clinical).
- **Metabolic:** hyperglycemia, insulin resistance additive with inflammation's own effect (C2.3).
- **CV risk:** dose-response (<5 mg/d prednisolone ~2× CV event risk; ≥25 mg/d ~6×) in observational data (E2).
- **Recommendation:** model steroid state as: RHR +2–8 bpm (dose-scaled, high variance), sleep efficiency −5–15%, glucose latent ↑, blunted inflammation–HRV coupling (steroids suppress CRP independently of symptoms → decorrelates flare signals — see RA Forecast limitation).

### Claim C9.2 — Beta-blockers
- Blunt HR and HRV responses to inflammation (RA Forecast **excluded** beta-blocker users for this reason). If present: cap HR impulse gain (~×0.5) and flatten chronotropic response. E5-level clinical pharmacology; no quantified inflammation-specific interaction study — apply as gain modifier with flagged uncertainty.

### Claim C9.3 — Immunosuppressants/biologics
- Effective biologic therapy normalizes autonomic/vascular signals over weeks–months (tocilizumab FMD/PWV data, C7.1; HRV improvement with inflammation control). Model as slow restoration of gains toward 1.0; a flare *despite* biologics produces attenuated signal. E2–E3.

---

## 10. What belongs in OCPE core vs disease-specific (summary of recommendations)

**CORE — generic `systemic_inflammation` latent state (severity s, dimensionless, log-scaled like LPS dose):**
- `acute_impulse`: HR gain 1+0.4–0.55·s_norm, temperature +0–1.75 °C·s_norm, RMSSD/SDNN gain 1−0.3–0.6·s_norm, onset 1–2 h, peak 3–5 h, recovery 8–24 h (E3/E4, C2.1).
- `chronic_low_grade`: RHR +1–4 bpm, RMSSD gain 0.85–0.95, slow dynamics weeks–months (E5, C3.2).
- `flare` (autoimmune): RHR +3–6 bpm, night HR +3–5 bpm, RMSSD mesor −20–30%, steps −5–15%, 2–7 week prodrome, recovery tail up to ~2.5 months (E2, C8.1–C8.3).
- `fever_coupling`: +10 bpm/°C (E4, C4.1); REE +11%/°C (E4, C2.4).
- `sleep_fragmentation`: awakenings ↑, dose-dependent biphasic NREM effect (E3–E5, C5).
- **Medication modifiers** (steroids, beta-blockers, biologics) as gain masks (C9).

**DISEASE-SPECIFIC WRAPPERS:** RA (CRP-coupled flare generator, symptomatic/inflammatory discordance — steps fall only in symptomatic flares), SLE (wider variance, steroid-dominant confounding), Sjögren's (orthostatic tachycardia emphasis, fatigue coupling), IBD (longer prodrome), gout (activity suppression only).

**LATENT-ONLY (no fabricated observable):** endothelial dysfunction/arterial stiffness (C7), insulin resistance (C2.3), basal temperature/circadian amplitude shifts in low-grade inflammation (C4.3), sickness behavior/fatigue as such (express only through steps/sleep/HR already in core), anti-M3R mechanisms (C6.3).

## 11. Validation strategy for OCPE
1. **Impulse replay:** digitize Jan 2009 / Dorresteijn 2010 LPS time series; fit acute_impulse parameters; report RMSE for HR, temperature, SDNN trajectories.
2. **Flare replay:** simulate RA inflammatory flare; verify RHR delta within 3–6 bpm and RMSSD mesor −20–30% vs RA Forecast published marginal means.
3. **Population correlation check:** synthetic cohort CRP–SDNN/RMSSD correlations should be small-negative (|r|≈0.1) matching Williams 2019; TNF-α correlation should be ~0 (null fidelity).
4. **Fever slope check:** regression of synthetic HR on synthetic temperature recovers ~10 bpm/°C (8.7–13.7 pediatric range).
5. **Confound stress test:** add steroid state; verify decorrelation of CRP-proxy from RHR signal (matching RA Forecast's stated limitation) and beta-blocker gain capping.
6. **Negative-control:** verify SpO2 shows NO flare signal (IBD null), and sleep unchanged in purely localized (gout-type) flares.

## 12. Honest gaps / open items for Pass 2
- Williams 2019 exact pooled r values per marker–HRV pair (abstract confirms significance and >16k datasets for CRP pairs; exact coefficients not extracted — do not quote specific r without the full text).
- Adult-specific fever–HR slope: the best large regression is pediatric; adult value remains a heuristic (~8–10 bpm/°C).
- No wearable study yet quantifies skin-temperature change during autoimmune flares (only infection); RA Forecast did not analyze temperature/sleep.
- No quantified human data on steroid effect sizes for RHR/sleep in autoimmune patients specifically (all indirect).
- LF/HF ratio: directionally inconsistent across endotoxin studies — excluded from OCPE core outputs.
