# OCPE — CONSOLIDATED DISEASE PHYSIOLOGY EVIDENCE (Pass 2 Integration)

**Role:** Integration Scientist consolidation of six disease/metabolic/neurological dossiers + healthy reference + Pass-2 audits.
**Inputs (source of record for full claim text):** `DISEASE_EVIDENCE_POTS.md`, `DISEASE_EVIDENCE_MECFS.md`, `DISEASE_EVIDENCE_LONGCOVID.md`, `DISEASE_EVIDENCE_EDS.md`, `DISEASE_EVIDENCE_AUTOIMMUNE.md`, `METABOLIC_PHYSIOLOGY_EVIDENCE.md`, `NEUROLOGICAL_PHYSIOLOGY_EVIDENCE.md`, `HEALTHY_PHYSIOLOGY_EVIDENCE.md`; normalized claim registry `EVIDENCE_REGISTRY.yaml` (143 claims); binding corrections from `EVIDENCE_AUDIT_NOTES.md`, `CONTRADICTION_AUDIT.md`, `INDEPENDENT_REVIEW_PASS2.md`.
**Integration rule:** this document does NOT restate claim text in full. Each condition section links registry `claim_id`s, synthesizes cross-cutting findings, applies binding downgrades, and answers the standard 8.1–8.10 question set. Where a dossier grade and a normalized grade differ, the **normalized registry grade (standard scale E0→E5) wins** and the dossier verbatim grade is preserved in `EVIDENCE_REGISTRY.yaml.dossier_evidence_strength`.

**Evidence scale (single binding convention, standard scale):** E0 hypothesis · E1 mechanistic · E2 observational human · E3 controlled human experimental · E4 replicated quantitative · E5 meta-analysis/consensus. (TEMPORAL used an inverted scale and WEARABLE_OBSERVABILITY a metrology scale; all grades here are normalized. Do not quote dossier-native grades from those two dossiers without the registry's `scale_note`.)

---

## 1. BINDING DOWNGRADES / REFUTATIONS APPLIED (Pass 2 — these override every dossier statement)

| # | Item | From → To | Consequence for generation |
|---|---|---|---|
| D1 | ME/CFS 2-day CPET day-2 decrement (EVD-MECFS-005/007) | E4/E5 → **E2/E3 + (E)** | Model small mean capacity decrement (0–7%, wide CI, workload/threshold-weighted) + explicit **effort-coupling term** (day-2 maximal effort falls during PEM; Keller 2024's own data) + responder subgroup (~20–40% show it). Null arm (Nelson 2026: 22% patients vs 33% controls decline ≥1 unit) must remain generatable. Never emit as disease law. |
| D2 | PEM delayed kernel on *physiological* channels (EVD-MECFS-008/009) | E4 symptom / → physiology **E0/E1** | Symptom kernel (onset 12–48 h, peak 24–48 h, recovery mean 12.7±1.2 d [Moore 2023 — **mean not median**], range 1–64 d) applies to symptom/affect states only. Physiological channels use the evidence-supported **slowed-recovery kernel**: post->VT1 exercise HRV/HR recovery τ ~3–6 h healthy → 9–13 h (up to 24 h) patient (Sports Med 2026 long-COVID wearable study; same-day prolongation, not a 24–48 h delayed trough). Optional delayed physiological second wave = E0 toggle, off by default. |
| D3 | Migraine interictal autonomic dysfunction (EVD-NEUR-013) | E5 → **E3** | Direct null replication (Lee 2019: all standard HRV metrics null); Valsalva I²=94%. Model small vmHRV shift g≈−0.3 at most; never more dysautonomic than the anxiety/pain layers. |
| D4 | Fever→HR slope (EVD-AUTO-003, HEALTHY §7) | "~12.3 bpm/°C general" → **age-graded: ~13 (young children) → ~10 (older children) → 7–10 bpm/°C adults** (adult ED data PMID 31345594: ~7.2 national / 6.9–10.4 adjusted) | Implement age-interpolated distribution with wide inter-individual spread; 12.3 is pediatric-only. |
| D5 | Geddes 2022 POTS parameter backbone | canonical tier-C → **scenario samples (tier D discipline)** | All 29 Geddes-base parameters + POTS perturbation magnitudes are single-source in-silico, partially engine-falsified (neuropathic 21.2 vs ≥30 bpm; hyperadrenergic ΔSBP −4.0 vs +10). Anchor independent human data (TotalVol deficit −12±5% via Raj 2005 + Fu 2010 + Kulapatana 2025 triangulation; hyperadrenergic subset via standing NE ≥600 pg/mL per Angeli 2024) and add the **competing Fu-2010 branch**: small LV mass + blood-volume deficit with *intact* baroreflex (baroreflex function statistically identical to controls) as an explicit alternative generative mechanism. |
| D6 | RA Forecast flare classifier (EVD-AUTO-005) | E4 prediction → **E2** | F1 0.95 / AUC ~1.00 are within-subject mixed-effects *associations* on imbalanced day-level data with imputed flare labels; authors state approach "may bias AUC results." Use only the within-person offsets as generative parameters: RHR +5.0 bpm, mean HR +6 bpm, night HR +5.5, RMSSD mesor −25% (21.5 vs 28.7 ms). Never emit flare-prediction performance as validated. |
| D7 | POTS HRV meta (EVD-POTS-011) | E5 → **E4** | I²=84–99% frequency-domain; pooled frequency-domain "null" is heterogeneity-driven. Model reduced time-domain variability (rMSSD −15.16 ms, partly HR-coupled) with preserved-to-ambiguous frequency domain; do NOT model POTS as generic "low HRV." |
| D8 | ME/CFS resting-HR / HRV / sleep metas (EVD-MECFS-003/004/012) | E5 → **E4** | Effects small (|SMD| ~0.3–0.4), I² 62–73%; +4 bpm RHR is below the within-person daily noise floor (~5 bpm, Quer CV 4.6%); 24-h mean HR null (SMD 0.11). Large overlap is mandatory. |
| D9 | LC peak-VO2 / vaccination / DLCO metas (EVD-LCOV-006/014/015) | E5 → **E4** (DLCO scope-restricted to hospitalized sub-phenotype ~10% of LC) | Peak VO2 −4.9 (−6.4,−3.4) mL/kg/min symptomatic-vs-recovered is low-certainty, hospitalized-driven. |
| D10 | RA HRV meta (EVD-AUTO-007) | E5 → **E4** | RMSSD SMD −0.90 but CI spans −1.35 to −0.44 (3× spread); case-control designs. |
| D11 | PD OH prevalence meta (EVD-NEUR-002) | E5 → **E4** | I² 79–98%; 9.6–64.9% range; community cohort 10.6%. OH *definition* stays E5. |
| D12 | POTS exercise-training remission (EVD-POTS-013) | E3/E4 → **E3** | Single n=19 completers-only; 53% remission not established. |
| D13 | POTS resting-HR elevation (EVD-POTS-014) | E4 → **E3** | Clinic lab +10–20 bpm vs real-world Welltory +~3 bpm with near-complete overlap — spectrum/label contradiction; resting HR alone must fail as classifier. |
| D14 | Healthy stand ΔHR "Normal(+12,5), >95% below 30" (EVD-HLTH-004 / TEMP-003) | → **protocol-conditioned distribution (E)** | Stand-10min mean ranges 12–25 bpm across protocols; NASA-lean 33% of healthy exceed 30 bpm at 10 min; Plash tilt-10min specificity 40%, tilt-30min 20%. Healthy false-positive rate at the POTS boundary is 10–33% on aggressive protocols, <5% on casual short-notice stands. Never a single Normal. |
| D15 | RMSSD as clean vagal index (EVD-POP-005 r=−0.58) | → **(E)** mechanistic-confounded | Respiration rate (up to 37% RMSSD variation at constant HR, Schipke 1999), tidal volume, HR level, and device bias are explicit inputs; population r=−0.58 anchor is children-only — use RR-scaling law + weak residual in adults (E1/E2). Within-person ΔRMSSD preferred over cross-device absolutes. |
| D16 | iRBD actigraphy combined/RAR model (EVD-NEUR-004) | AUC 0.92–0.95 → **0.84–0.87 sleep-only generalizes; RAR collapses to 0.52–0.82 (≈chance at 2/4 sites)** | Keep sleep-movement model; drop rest-activity-rhythm claims; report prevalence-adjusted PPV (3–6% at 1.5% prevalence). |
| D17 | Postprandial ΔHR | tension resolved | +6 ± 3 bpm mixed-meal default (METABOLIC controlled studies), meal-size scaled; +10–20 only large/high-carb (not TEMPORAL's unconditional +10–20). |
| D18 | PEM recovery statistic | "median 12.7 d" → **judged-recovery mean 12.7±1.1–1.2 d, range 1–64 d, right-skewed** | Fit an explicit right-skewed recovery distribution; do not use a median kernel. |
| D19 | Sensor constants | — | No fixed skin-tone PPG-HR penalty (EVD-SENS-005 contested: 4/10 studies found penalty, 4 null, 2 mixed); sample bias with mass at ~0 for PPG-HR, positive-bias distribution for SpO2 (direction robust, magnitude 3–8 pp). Wearable EE unusable for precision (MAPE >30%, all brands, E5). |
| D20 | Within-person RHR SD | E0 (HEALTHY) → **Quer 2020 within-person SD ≈3.0 bpm, CV ≈4.6%; 5-day ICC 0.87** (EVD-POP-004) | Cross-reference POPULATION; retire the weaker E0 estimate. |
| D21 | Latent factor structure (EVD-POP-005/-007) | E0 confirmed | Loadings sampled ±50%; Gaussian-copula sensitivity at r=0; comorbidity co-occurrence rates ascertainment-inflated → down-weight 0.3–0.5× for population sampling. |
| D22 | ME/CFS metabolomics / LC ML AUC / hEDS WHOOP | — | Naviaux AUROC 94–96% in-sample only (never classifier targets); LC ML AUC 0.951 → realistic band 0.75–0.85; hEDS WHOOP pilot group-level null with individual-level significance → within-person semantics mandatory. |

Additional audit-binding flags: EVD-EDS-003 venous-pooling mechanism in hEDS is E0–E1 (never measured; optional perturbation only); EVD-EDS-008 deconditioning-vs-intrinsic adjudication E0 (keep components separable); EVD-EDS-002 retained E4-borderline (direction replicated ≥3 groups, all n~30–40/arm, pre-2017 contamination); EVD-METB-013 24-h-fast autonomic shift E3-flagged (single crossover n=25, sex-dependent direction contradiction); EVD-METB-002 E3/E4-borderline (primary n=21); EVD-HLTH-006 E4 (single 25-study review); EVD-TEMP-008 menstrual effects verified-lab n=26 only (48,720-cycle source is an abstract); EVD-AUTN-009 accentuated-antagonism k~1–3 is E1/E2 for magnitude (tunable); EVD-AUTN-003 CBR logistic parameters n=9 point estimates; EVD-AUTO-008/009 SLE HRV magnitudes unattributable (100% steroid confound) and steroid wearable effects all indirect (gain modifiers with flagged uncertainty); fludrocortisone TotalVol +500 mL magnitude sampled ±50% (direction-only citation, no adequate POTS RCT — EVD-POTS-015 E0); POTS baroreflex gain EVD-POTS-010 sampled −15 to −25% wide variance (reduced Stewart 2021 vs unchanged Fu/Galbreath vs increased pediatric — genuinely unresolved); EVD-POTS-008 cerebral autoregulation = uncertain latent gain.

---

## 2. HEALTHY REFERENCE ANCHOR (what disease perturbations act on)

Disease models are perturbations of the healthy reference; the reference itself is the binding calibration layer. Registry anchors: EVD-HLTH-001..010, EVD-POP-001..008, EVD-AUTN-001..010, EVD-TEMP-001..011. Key frozen semantics (Pass-2 harmonization):

1. **RHR definition is device/definition-dependent (~4–8 bpm offsets):** freeze *nocturnal RHR* for wearable channels (Quer 2020 daily RHR 65.5±7.7, within-person SD ≈3.0) and *seated clinic RHR* for validation comparisons (Health eHeart = "real-world on-demand HR," gradients only — do not calibrate absolutes from it; two Avram misquotes corrected: 71–80 y HR SD 11.1 not 12.7; female offset +4.00 not +4.4).
2. **Orthostatic response is a protocol-conditioned, time-resolved curve** — initial transient (peak ~15–30 s) vs sustained (1–10 min) are separate parameters (D14); stand ≠ tilt ≠ NASA-lean; age strata (adolescent 95th pct 41–48 bpm). This is "the single most consequential calibration choice" (HEALTHY dossier).
3. **HRmax = 208−0.7·age, ε~N(0,11)** (EVD-POP-003/HLTH-005, E5; the repo's 220−age Fox equation is superseded).
4. **HRV structure:** 24-h SDNN ~150±38–40 ms (25–41 y); 5-min RMSSD lognormal median ~35–42 ms; day-to-day within-person CVs ~10–15% lnRMSSD, 20–50% spectral; 1/f DFA structure (EVD-TEMP-001 E4); RSA is mechanistically generated from respiration (D15).
5. **Circadian:** HR amplitude ~13.5 bpm acrophase ~14:40; SBP ~10/DBP ~7 mmHg; core T ~0.5 °C (nadir 04:00–06:00); distal skin T amplitude 1.2–2.2 °C; CAR +50% phase-gated (EVD-HLTH-009).
6. **Sleep architecture:** stage-conditioned autonomics (N3 vagal max; REM sympathetic bursts); sleep-stage HR spread only ~2 bpm vs recumbent wake — the 20–30% nocturnal "dip" is relative to *ambulatory day* (reference-frame discipline mandatory).
7. **Stress/pain/hyperventilation/OSA CORE modules** (NEURO §7–9): TSST SAM arm (HR d≈0.9, SBP d≈1.2, no habituation) + HPA arm (cortisol d≈0.5–0.9, habituates, latent); cold-pressor pressor +8–12 mmHg SBP with bimodal HR responder structure; hyperventilation +4.4 bpm / MAP −3.5; OSA 4-phase CVHR + SpO2 sawtooth parameterized by AHI.
8. **Metabolic CORE:** postprandial HR +6±3 bpm (meal-size scaled, D17); CGM-channel norms (24-h mean 90–99 mg/dL, TIR 96%) exist *only if persona wears CGM*; EE channels carry MAPE 20–35% error; glucose/insulin/RER/BAT/ketones latent-only.
9. **Menstrual modulation** (EVD-TEMP-008): luteal RHR +2–7 bpm, RMSSD −4–5 ms, distal skin T +0.2–0.3 °C — healthy core, must exist so it is not misread as flare/infection in female personas.

---

## 3. CONDITION: POTS (flagship) — registry claims EVD-POTS-001..020

Full per-claim text: `DISEASE_EVIDENCE_POTS.md` Claims 1.1–8.4 (mapped to registry EVD-POTS-001..020). Contrast phenotypes: OH/IOH/VVS (EVD-POTS-017; POTS dossier §9).

**8.1 What differs from healthy.** Sustained orthostatic ΔHR ≥30 bpm/10 min (≥40 ages 12–19) without OH (EVD-POTS-001, E5 — consensus criteria; but the 30-bpm boundary is a clinical threshold, not a physiological boundary — D14). POTS ΔHR keeps rising past 10 min and tilt > stand at every time point (EVD-POTS-005, E4: HUT 49±4/55±5/62±4 at 5/10/30 min; stand 44±4/50±4); group separation develops over minutes 2–10, not the first minute (Orjatsalo 2020). BP maintained or rising (hyperadrenergic ΔSBP ≥+10; EVD-POTS-002 hyperadrenergia expressed in BP, not ΔHR — Okamoto 2024 ΔHR 34±8 vs 34±5, p=0.988). Exaggerated 0.1-Hz Mayer-wave HR/BP oscillations with shortened phase (EVD-POTS dossier Claim 3.4, E3) — an altered *relationship*, not a mean shift. Resting HR elevation is clinic-real but spectrum-dependent (+10–20 lab vs +3 real-world — D13, E3). Fast recovery on lying down (50–70% of ΔHR recovered in 20–60 s; EVD-POTS-012, E4). Strong AM>PM diurnal modulation (EVD-POTS-002, E4; 100% criteria-positive AM vs 28–44% PM).

**8.2 Mechanisms.** Three continuous composable axes with an empirical joint distribution (EVD-POTS-003, E2: hyperadrenergic 75.0%, hypovolemic 44.9%, neuropathic 37.8%; 41.7% dual, 11.4% triple, 6.8% none; symptoms do NOT discriminate — composable dimensions, not discrete classes): (i) hypovolemia/small-heart — best-replicated objective finding, BV deficit −12 to −15% triangulated across 3 methods (EVD-POTS-004, E4; Raj 689±270 mL n=15 single-study absolute; Kulapatana ±10.38% SD ⇒ volume-normal minority exists ⇒ mixture model); (ii) neuropathic partial leg sympathetic denervation (EVD-POTS-019, E3; Jacob 2000 blunted leg NE spillover); (iii) central sympathoexcitation/NET dysfunction (EVD-POTS-009, E3 heterogeneous MSNA; reboxetine phenocopy). Upright SV/CO fall excessively; HR is compensatory to SV/preload (EVD-POTS-006, E3/E4) — SV→HR coupling is the core model equation. Postural hyperventilation/hypocapnia subset ~25% (EVD-POTS-008, E3; exogenous CO2 abolishes criteria — causal demonstration). **Competing branch (D5):** Fu 2010 — intact baroreflex; small LV mass + hypovolemia suffice; training (+12% LV mass, +7% BV) abolished criteria in 10/19 (EVD-POTS-013, E3).

**8.3 Primary vs compensatory vs downstream.** Primary (candidate): volume deficit, small cardiac size, denervation, central gain (all unresolved which is causal — deconditioning direction contested, EVD-POTS-013 + dossier §10.7). Compensatory: orthostatic tachycardia itself, exaggerated upright MSNA, splanchnic/pelvic pooling redistribution (EVD-POTS-007, E3, single-lab dominance — replication: low). Downstream: reduced rMSSD (partly mathematical HR coupling — D7/D15), sleep disturbance (EVD-POTS dossier 6.4, E3), symptom burden. Baroreflex gain itself unresolved (EVD-POTS-010, E3-conflicting: sample −15 to −25%, wide variance; do not hard-code).

**8.4 Overlaps.** hEDS 31% of POTS (2017 criteria; EVD-POTS-020); ME/CFS ~21%; autoimmune ~16%; MCAS ~9%; long-COVID POTS-like tail (graded axis, D9 below). ~1/3 of POTS also have positional VVS episodes. Orthostatic tachycardia shared with hEDS, Sjögren's, ME/CFS subset, LC subset, fasting, dehydration/heat, deconditioning, hyperventilation — and 33–60% of healthy on aggressive protocols (overlap matrix §16).

**8.5 Heterogeneity.** Subtype axes continuous with Angeli-2024 joint probabilities (provisional weights — referral-biased; Thieben disagrees); MSNA resting distribution bimodal/heterogeneous (normal/elevated/low all reported); spectrum ascertainment (clinic vs self-report) changes resting-HR effect 4×; demographics ~80–90% female, adolescent/young-adult onset, often post-infectious.

**8.6 Temporal change.** Diurnal (AM>PM), menstrual modulation, heat/meal/illness triggers, postprandial worsening (~53% high-carb; EVD-POTS-016, E2); within-subject variance is large — identical daily traces are unrealistic. Exercise training is a parameter trajectory (volume + LV mass + upright HR over 3 months). Disease course: diagnostic delay ~5 y; no validated natural-history wearable trajectory.

**8.7 Stress-response differences.** Exaggerated orthostatic gain with normal supine gain (state-dependent); heat is a near-universal trigger (E1/E2 — no quantitative heat-challenge study in POTS; gap); Valsalva/MSNA responses exaggerated upright; stress CORE (TSST) applies unchanged — no evidence of altered HPA axis per se.

**8.8 Plausible wearable appearance.** Defensible observables: posture-transition ΔHR amplitude + time-to-peak; AM>PM asymmetry; upright 0.1-Hz HR oscillation amplitude; reduced upright rMSSD; elevated sleep HR / non-dipping surrogate; postprandial HR bump; heat-exposure HR spike; fast supine recovery; symptom-tag↔ΔHR correlation. Constraints: resting-HR-only discrimination must fail (Welltory constraint, D13); stand-test false-positive expectation ~10–33% healthy on aggressive protocols; BP, SV/CO, NE, blood volume, ETCO2, CBFv all latent. Validation battery: Plash 2013 tilt-vs-stand trajectories; Orjatsalo minute-resolved; Brewster/Cai diurnal; Angeli joint distribution + standing NE; Raj volume deficit; recovery half-time; Bourne compression dose-response.

**8.9 Evidence status & binding downgrades.** D5 (Geddes backbone → scenario samples + Fu branch), D7, D12, D13, D14 apply. Must-not-hard-code: EVD-POTS-003 (subtype weights), -008 (autoregulation), -010 (BRS gain), -013, -014, -015 (fludrocortisone E0).

**8.10 Validation anchors / do-not-fabricate.** Anchors as in 8.8. Do not fabricate: wearable BP, cuffless-BP certification of no-OH (PPG-BP error ±5–10 mmHg exceeds the 20-mmHg OH threshold), venous pooling at wrist, absolute BRS, NE levels. Fludrocortisone must not appear as an evidenced POTS perturbation (no adequate RCT).

---

## 4. CONDITION: ME/CFS — registry claims EVD-MECFS-001..014

Full text: `DISEASE_EVIDENCE_MECFS.md` Sections 1–11. Core framing: PEM is a delayed, multi-day dynamic perturbation, not a scalar.

**8.1 What differs from healthy.** Baseline (trait, severity-scaled): RHR +4.14 bpm (EVD-MECFS-003, E4 after downgrade — below within-person noise floor; 24-h mean HR null); RMSSD −0.37 SD / HF −0.34 SD / LF +0.39 SD (EVD-MECFS-004, E4, small); HRpeak −16.6 / criterion HRmax −5.8 bpm (EVD-MECFS-005, E4, effort-confounded); orthostatic HR response SMD +0.50–0.92 (EVD-MECFS-006, E4); steps/day severity-graded 8235/5195/2031 mild/moderate/severe (EVD-MECFS-002, E2/E4); end-tilt CBF −26% vs −7% incl. −24% in the 58% with normal HR/BP tilt (EVD-MECFS-006; single-group dominance, replication low). Sleep: SE −3–6%, SOL +7 min, TST normal — NOT hypersomnia (EVD-MECFS-012, E4). Episodic (PEM state): see 8.6.

**8.2 Mechanisms.** Largely unresolved; candidate layers: autonomic (small vagal↓/sympathetic↑ shift), orthostatic/CBF dysregulation, exertional physiology (invasive CPET: preload failure + impaired peripheral O2 extraction, E3 tiny n; pyridostigmine RCT causal hint), ventilatory (hypocapnia in ~31%), hypometabolic metabolomic *direction* (EVD-MECFS-013, E1/E2 — panels unreplicated; AUROC 94–96% in-sample only, never a target). Post-infectious onset majority; Walitt 2024 effort-preference finding (E3, contested). PEM trigger = exertion dose above persona threshold (~VT1 proxy ≈ RHR+15 bpm; cognitive/emotional dose ~70% potency) — a modeling hypothesis informed by E3/E2, not an established law.

**8.3 Primary vs compensatory vs downstream.** Unknown and contested: activity-matching erases VO2max differences (MCAM ES 0.02) — deconditioning confound unresolved; tilt CI abnormalities unrelated to VO2peak argue disease-intrinsic hemodynamics (van Campen); both branches must remain generatable. Compensatory: pacing/activity suppression. Downstream: deconditioning, sleep fragmentation, symptom amplification. The day-2 CPET decrement is substantially effort-coupled (D1).

**8.4 Overlaps.** POTS ~28% adult (pediatric OI >96%), delayed OH ~14%, FM ~30–40%, hypermobility 30–50% (age-dependent), long-COVID ME/CFS subphenotype 4.5% of infected (EVD-LCOV-003). Step suppression, low HRV, sleep fragmentation, PEM-like flares all shared (matrix §16). Daily-mean-HR normality (EVD-MECFS-005 caveat: 24-h average null) is a strong anti-signature constraint.

**8.5 Heterogeneity.** Severity is first-class latent with objective anchors (steps/VO2 tertiles); severe/bedbound (~25%) systematically excluded from lab studies — severe-tier parameters are extrapolations downward (steps 2000/d, sitting-provoked CBF −24.5%). Nocturnal-HR direction conflict (Boneva vs Frith) → per-persona mixture (~60% elevated / ~40% neutral-lower). PEM detectability mixture: only ~50–65% of exertion episodes produce clear physiological signatures. Fukuda-only cohorts ≠ CCC/IOM cohorts (PEM prevalence 40.6–93.8% by question wording).

**8.6 Temporal change.** PEM kernel (symptom): trigger → delay Gamma(mode 12–24 h, support 0–48 h; 11% consistently ≥24 h) → peak 24–48 h → recovery mean 12.7 d, range 1–64 d, 5–10% >3 wk (D2/D18; Moore 2023 mean-not-median). Physiological channels: slowed-recovery kernel (τ 3–6 h → 9–13 h, up to 24 h post->VT1; D2). Boom-bust activity autocorrelation (day-to-day variation 47%, range 25–79%; milder patients swing more — they retain capacity to overexert). Baseline RHR is a stable trait over 6 months; deviations are episode-linked, not random drift. Incomplete recovery → rolling-PEM baseline creep (slow state variable).

**8.7 Stress-response differences.** Exaggerated + delayed fatigue response to acute exercise, largest ≥4 h post (EVD-MECFS dossier Claim 4.3, E5 symptom-level); blunted parasympathetic reactivation post-exercise (Van Oosterwijck 2021); HRR meta-analytically null (Nelson 2019) — do not model slow HRR as established. Stress CORE unchanged otherwise.

**8.8 Plausible wearable appearance.** Defensible: step-count severity gradient + boom-bust autocorrelation (E4); post->VT1-exertion next-24-h HRV suppression −10–30% + nocturnal HR elevation + activity reduction 24–72 h (E3 lab + E2 LC wearable proxy — the only near-PEM wearable correlate); modest resting offsets with huge overlap; sleep TIB +30–90 min during crashes (E2); optional skin-T +0.1–0.3 °C flu-like subset (E0 toggle, off by default). **Classifier sanity cap: single resting feature AUROC must not exceed ~0.7–0.8.** Explicitly extrapolation-flagged: any multi-day wearable PEM channel (EVD-MECFS-010 — the direct dataset does not exist).

**8.9 Evidence status & binding downgrades.** D1 (2-day CPET → E2/E3 + effort coupling + responder subgroup), D2 (physiology kernel), D8 (metas E5→E4), D18 (mean-not-median), D22 (metabolomics). Must-not-hard-code: EVD-MECFS-007 mixture (50–60% show it; null arm generatable), -013 metabolomics.

**8.10 Validation anchors / do-not-fabricate.** Anchors: step tertiles; Nelson 2019 SMD CIs; Lim 2020 ΔWork@VT (−14.6 W vs +6.5 W) and Keller 2024 declines *within CI in ~50–60% of personas*; Moore recovery distribution; Chu onset/duration frequencies. Do not fabricate: multi-day PEM physiological telemetry as if measured; skin-fever PEM signatures; severe-patient lab physiology; symptom-improvement⇒activity-normalization coupling (PACE/Wilshire lesson — dissociable by design). PEM dynamics are a **validation exclusion** (no dataset exists to validate against).

---

## 5. CONDITION: LONG COVID — registry claims EVD-LCOV-001..015

Full text: `DISEASE_EVIDENCE_LONGCOVID.md` Claims 1.1–9.3. Core framing: heterogeneous; no validated biomarker (RECOVER n=10,094 routine-labs null, EVD-LCOV-011 — the boundary condition).

**8.1 What differs from healthy.** Nothing global — RECOVER labs null is binding; differences live in penetrant phenotype axes (§10 table of the dossier). Group-level: SDNN −15–25%, RMSSD −10–20% (~50% penetrance), resting HR +1–3 bpm chronic (EVD-LCOV-005, E2); peak VO2 −4.9 (−6.4,−3.4) mL/kg/min symptomatic vs recovered (EVD-LCOV-006, E4-downgraded, hospitalized-driven); chronotropic incompetence in ~30% symptomatic (EVD-LCOV-007, E2; peak HR −49 bpm in CI subgroup); PEM 28% vs 7% background (EVD-LCOV-001, E2, aOR 5.2 — highest-contrast symptom).

**8.2 Mechanisms.** Mostly unestablished: microclots/viral persistence/autoantibodies E0–E1 — motivate axes but contribute no parameters. Evidenced layers: post-acute infection RHR trajectory (EVD-LCOV-010, E4 — best-validated wearable signal); autonomic dysregulation axis; chronotropic-incompetence trait; peripheral O2-extraction impairment (iCPET n=10, E2); dysfunctional breathing (~30% of dyspneic, normal SpO2/PFT); sleep disturbance axis; severity-gated metabolic drift (HbA1c +0.1%, post-hospitalized tier); DLCO impairment ONLY in post-hospitalization sub-phenotype (~10%; EVD-LCOV-015, scope-restricted).

**8.3 Primary vs compensatory vs downstream.** Primary unknown. Deconditioning common in reduced-capacity cases; early hsCRP/IL-6/TNF inversely correlated with later peak VO2 (inflammatory-priming hint, E2). SFN: positive in selected painful subgroup, null in largest controlled biopsy series — do not implement as general mechanism. Compensatory: activity reduction (confounds HRV/VO2 signals). Downstream: sleep disturbance, deconditioning spiral.

**8.4 Overlaps.** ME/CFS subphenotype (4.5% of infected; 88.7% of those also PASC+); POTS-like orthostatic axis; PEM shared with ME/CFS/overtraining/infection recovery; low-HRV axis shared universally; background symptom rates in uninfected (PEM 7%, fatigue 17%, brain fog 4%, OI ~6%) mandatory in synthetic controls — all LC perturbations are excess-over-background (EVD-LCOV-012).

**8.5 Heterogeneity.** 4 RECOVER symptom clusters are observation-level labels, NOT generative endotypes; 8 trajectory classes (81% of 3-mo cases persist/intermittent at 12 mo); penetrance-weighted axes per dossier §10 table; variant (Omicron ×0.5 vs Delta) and vaccination (×0.7–0.8) incidence modifiers; female sex + hospitalization → persistent-severe.

**8.6 Temporal change.** Acute infection: triphasic RHR (spike → wk-2–3 dip → prolonged elevation in subset); mean 79 d to RHR baseline; 13.7% (Radin) / 7.0% (UK replication) with ≥5 bpm at >133 d/12 wk; steps normalize ~32 d, sleep ~24 d — RHR is the slow channel. Chronic: heavy-tailed duration mixture (~19% resolve by 12 mo, intermittent common, persistent-severe minority 10–20%).

**8.7 Stress-response differences.** Post-exertion autonomic recovery slowed (same-day prolongation 3–6 h → 9–13 h post-VT1; D2 kernel — the ambulatory PEM correlate, Claim 8.3/8.5 dossier); day-2 CPET decrement in LC itself contradictory (EVD-LCOV-009, E2: n=15 null despite 80% PEM) — implement PEM as state transition, NOT VO2 decrement.

**8.8 Plausible wearable appearance.** Best-validated: post-infection RHR trajectory module (acute +5–15 bpm; tail +1–3 bpm, ≥5 bpm in 7–14%, 2–5 mo decay) as a standalone base layer for ALL post-infection personas. Acute detection envelope: AUC 0.75–0.80 (DETECT), 63–81% case detection, up to 9 d pre-symptomatic; skin T +0.5–1.0 °C acute only (no chronic LC temperature signature — do not add one). PEM+ tier (~25–30% symptomatic): post-VT1 24–72 h HRV −10–30%, nocturnal HR↑, activity↓. Chronic discrimination ceiling: AUC band 0.75–0.85; >0.95 ⇒ too stereotyped. Behavioral contamination (positive-test behavior change) modeled separately from physiology.

**8.9 Evidence status & binding downgrades.** D9 (three metas E5→E4; DLCO scope-restricted), D2 (PEM physiology kernel), D22 (ML AUC 0.951 → band 0.75–0.85). Must-not-hard-code: EVD-LCOV-004 POTS prevalence 0–79% by method → graded orthostatic latent axis (ascertainment-dependent 20–80% penetrance), never a binary or fixed prevalence.

**8.10 Validation anchors / do-not-fabricate.** Anchors: Radin/DETECT statistics; −4.9 mL/kg/min CI; SDNN/hsCRP/HbA1c group means; phenotype prevalences (PEM ~25–30% symptomatic, ME/CFS 4.5%, OI ~25%, sleep ~30%); trajectory mix. Negative controls: uninfected synthetics retain background symptom rates; no troponin/BNP/D-dimer/CRP elevation in mild LC; SpO2 normal in dysfunctional-breathing phenotype.

---

## 6. CONDITION: hEDS / HSD — registry claims EVD-EDS-001..008

Full text: `DISEASE_EVIDENCE_EDS.md` Claims 1.1–10.1. Headline: the direct wearable evidence base is exactly two studies (26-person WHOOP pilot; 37-adolescent accelerometry). The dominant narrative mechanism (connective-tissue laxity → venous pooling → POTS) is E0–E1, never measured.

**8.1 What differs from healthy.** Resting autonomic shift (EVD-EDS-002, E4-borderline): resting HR 87.3±11.6 vs 75.2±9.8 (+~10 bpm), SDNN 35.4 vs 49.1 ms, RMSSD 20.7 vs 31.6 ms (−30–35%), LF/HF 3.7 vs 1.8; blunted Valsalva/tilt BP reactivity. Orthostatic tachycardia in a subset with huge variance (SD 15+ bpm); IOH prevalence NOT different from controls (normal in young women — not an hEDS marker); OH rare (0–4%) — do not model OH as typical. Chronic pain near-universal (86–90%, NRS ~7; EVD-EDS-006). Objectively reduced MVPA / elevated sedentary time + more nocturnal movement (E3, adolescents). Subjective sleep poor (~61% PSQI>5); OSA markedly elevated (32% vs 6%, OR 5.3; EVD-EDS-007, E3–E4).

**8.2 Mechanisms.** Genuinely unresolved (EVD-EDS-008, E0): candidates (a) small-fiber neuropathy (objective, replicated direction, E2–E3 — causality to OI unproven; also common in FM), (b) connective-tissue vascular laxity (arterial: lower PWV E3 with two nulls and NO correlation with orthostatic responses; venous side never measured — EVD-EDS-003, E0–E1), (c) deconditioning (never partialed out), (d) pain-driven sympathetic arousal, (e) vasoactive medications. Implement as composite of SEPARABLE perturbations with explicit "mechanism unknown" annotation.

**8.3 Primary vs compensatory vs downstream.** Unknown (EVD-EDS-008 E0). Exercise interventions improve symptoms (reversibility hint) but objective activity unchanged (Pilates null) — symptom/activity dissociation. Structural cardiac disease excluded (aortic/MVP rates ~population or below; E2–E3 null — do not model).

**8.4 Overlaps.** POTS 31%→hEDS; hEDS→POTS 7–49% by criteria/ascertainment (EVD-EDS-004, E2 — sample from range; clinic 78–90% OI claims are referral-biased upper bounds); ME/CFS fatigue phenotype 40–77%; FM × hypermobility 68–90% (E2, verify); MCAS ~15–20% low confidence; OSA ~30% comorbidity branch. Comorbidities sampled jointly (they cluster), with ascertainment down-weighting 0.3–0.5× (D21).

**8.5 Heterogeneity.** hEDS vs HSD boundary artificial for physiology — model severity continuum; pre/post-2017 criteria incommensurable; POTS concentrated in G-HSD not hEDS on HUT (Peebles 2022 contradiction); symptom/physiology dissociation (100% symptomatic vs 7% HUT-POTS in hEDS); ~75–85% female synthetic cohorts.

**8.6 Temporal change.** Lifelong/chronic; flare structure pain/GI-driven; WHOOP lesson: group-level null + individual-level significance ⇒ **within-person day-to-day variance and person-specific baselines are the signature** (76–92% individual F-test significance vs null group means). No longitudinal physiological course data.

**8.7 Stress-response differences.** Adrenergic hyperresponsiveness (Gazit 2003, α and β); exaggerated hyperventilation SBP drop; pain flares activate CORE pressor/EDA module (transferable chronic-pain priors: HF-HRV moderate-large decrease, E5 non-EDS — EVD-EDS-006 coupling uses transferable prior, flagged).

**8.8 Plausible wearable appearance.** Resting HR +~10 bpm / RMSSD −30% group shift with wide variance (many within normal — Miglis null: hEDS adds little beyond POTS); day-level symptom↔HRV coupling at individual level (random slopes), null group-level symptom-day contrasts; reduced MVPA/elevated sedentary fraction; elevated nocturnal movement; OSA branch nocturnal SpO2/HR sawtooth; gait-variability (not inability) if movement modeled (proprioception E5).

**8.9 Evidence status & binding downgrades.** EVD-EDS-003 → E0–E1 optional perturbation with "mechanism untested" flag; EVD-EDS-008 E0 separable components; EVD-EDS-004 sampled range; EVD-EDS-002 E4-borderline retained. WHOOP group-null is the single most important empirical anchor (D22).

**8.10 Validation anchors / do-not-fabricate.** Anchors: resting HRV means±SDs (Claim 3.1); Peebles 2022 stand/HUT ΔHR and symptom rates; WHOOP within-person significance rates; adolescent accelerometry. Do not fabricate: venous-compliance signals, minute-resolution HUT time-courses (none published — gap), thermoregulatory/core-T perturbations (E0–E1; defer or sudomotor-gain-only with flag), hEDS-specific pain→HRV effect sizes (use transferable priors).

---

## 7. CONDITION: SYSTEMIC INFLAMMATION / AUTOIMMUNE — registry claims EVD-AUTO-001..011

Full text: `DISEASE_EVIDENCE_AUTOIMMUNE.md` Claims C2.1–C9.3. Architecture verdict (endorsed): ONE generic `systemic_inflammation` core state (severity s, log-scaled like LPS dose) + disease wrappers.

**8.1 What differs from healthy.** Depends on layer: (i) acute inflammation impulse (EVD-AUTO-001, E3/E4): HR +40–55% peak at 3–6 h, core T +1–1.75 °C at 3–4 h, HRV sharply depressed 1–6 h, recovery 8–24 h (onset 1–2 h, peak 3–5 h, τ 8–12 h); dose-response: no vital-sign change ≤0.5 ng/kg LPS — low-grade inflammation sits BELOW the acute-vitals threshold. (ii) chronic low-grade (EVD-AUTO-002, E5): RHR +1–4 bpm, RMSSD/SDNN gain 0.85–0.95, |r|≈0.1 population-scale only (TNF-α null — no cytokine-specific signatures). (iii) flares (EVD-AUTO-005/006, E2): RHR +3–6 bpm, night HR +3–5 bpm, RMSSD mesor −20–30%, steps −5–15% (symptomatic flares only), 2–7 week prodrome, tail to ~2.5 months. (iv) fever coupling age-graded 7–13 bpm/°C (D4); REE +10–13%/°C (EVD-AUTO-004, E4).

**8.2 Mechanisms.** Cytokine → vagal-afferent → central autonomic drive (inflammatory reflex; human causal direction unestablished, E1 feedback gain); fever Q10 metabolic drive; sleep↔inflammation bidirectional but small (EVD-AUTO-010, E5: IL-6 ES 0.20, CRP ES 0.12); sleep disruption dose-dependent biphasic (very mild → NREM enhancement; stronger → fragmentation).

**8.3 Primary vs compensatory vs downstream.** Primary: immune activation state. Downstream: HRV/RHR/temperature/sleep/activity shifts — sickness behavior is expressed ONLY through these channels (no independent sickness-behavior signal). RA HRV deficit is inflammation-dose-dependent within disease (CRP≤5 ≈ controls) — tie gains to inflammation level, not disease label. SLE magnitudes unattributable (100% steroid confound — EVD-AUTO-008; use RA-like pattern, wider variance, SLE multiplier ~1.0–1.5, E2-flagged).

**8.4 Overlaps.** This IS the shared inflammation axis for the whole engine (matrix §16): RA, IBD, SLE, Sjögren's (orthostatic tachycardia emphasis, fatigue-coupled; autonomic dysfunction ~36%), gout (activity suppression only, sleep null), infection, long-COVID tier, ME/CFS PEM inflammatory component. Medication masks cross-cut everything (§16 row).

**8.5 Heterogeneity.** Flare symptomatic/inflammatory discordance (steps fall only in symptomatic flares; CRP imputation caveat); steroid state decorrelates CRP-proxy from RHR; beta-blockers cap HR impulse gain ~×0.5; biologics restore gains slowly; RA Forecast 88.7% female, multi-device.

**8.6 Temporal change.** Impulse 8–24 h (LPS); vaccination-mild 12–48 h; flare prodrome 2–7 weeks with slow ramp; post-inflammatory recovery tails up to ~2.5 months (Radin analog); chronic low-grade weeks–years drift.

**8.7 Stress-response differences.** Hydrocortisone blunts cytokines but does NOT block HRV depression (even low cytokines depress HRV); acetaminophen decouples temperature from inflammation (−0.9 °C) — self-medication confound; steroid paradoxical bradycardia at IV pulse doses (E2).

**8.8 Plausible wearable appearance.** Flare signature per C8.1/C8.2 (marginal means only — D6); infection envelope per C8.3 (RHR +5–7 bpm pre-symptomatic, skin T +0.5–1 °C, sleep ↑ then disrupted, steps ↓); fever HR–T slope recoverable in regression; SpO2 shows NO flare signal (IBD null — negative control); gout-type localized flares: steps −841/d, sleep unchanged. Negative-control fidelity: TNF-α–HRV correlation ~0.

**8.9 Evidence status & binding downgrades.** D4 (fever slope), D6 (RA Forecast classifier → E2, offsets survive), D10 (RA meta E5→E4). Must-not-hard-code: EVD-AUTO-008, -009 (steroid effects all indirect — gain modifiers with flagged uncertainty), -011 LATENT-ONLY list (endothelial stiffness → NO PPG morphology signal; low-grade temperature-setpoint shifts; PPG-stiffness observability — no evidence).

**8.10 Validation anchors / do-not-fabricate.** Anchors: LPS impulse replay (Jan 2009/Dorresteijn 2010 digitized series, RMSE on HR/T/SDNN); RA Forecast marginal means; Williams 2019 small-negative correlations (+ TNF null); fever slope regression; steroid decorrelation stress test. Do not fabricate: PPG stiffness/waveform inflammation signals, CGM-scale glucose from inflammation, optical glucose (M5: E0–E2, no field-valid device — never emit a "PPG-estimated glucose" channel), basal-temperature shifts in low-grade inflammation.

---

## 8. CONDITION: NEUROLOGICAL (PD / MSA / PAF / epilepsy / migraine / anxiety / panic / OSA) — registry claims EVD-NEUR-001..013

Full text: `NEUROLOGICAL_PHYSIOLOGY_EVIDENCE.md` Claims PD-1..6, AF-1..5, EP-1..3, MI-1, AN-1..2, OSA-1, ST-1..3, HV-1. CORE allocations (stress, OSA, pain-pressor, hyperventilation, orthostatic reflex) live in the healthy reference (§2 item 7).

**8.1 What differs from healthy.** PD: cardiac sympathetic denervation (MIBG latent; EVD-NEUR-001, E5), OH pooled 30.1% (EVD-NEUR-002, E4-downgraded), modest HRV reduction ~15–25% possibly prodromal (EVD-NEUR-003, E2 with CHS null replication), iRBD actigraphy AUC 0.84–0.87 (EVD-NEUR-004, E4; D16), IMU motor signatures 4–6 Hz tremor/bradykinesia (EVD-NEUR-006, E4 — most wearable-validated signal in the dossier; free-living drops to AUC 0.71–0.76), levodopa OH 22%→38% post-dose (EVD-NEUR-005, E3). MSA/PAF: severe nOH with ΔHR/ΔSBP <0.3–0.5 (EVD-NEUR-007, E4), supine hypertension + reverse dipping (~50%; PAF 70%), anhidrosis with blunted EDA gain (E4), SRBD pooled 60.5% (EVD-NEUR-012 context). Epilepsy: GTCS multimodal detection sens 92–100%, FA 0.2–1.4/day (EVD-NEUR-008, E4→E5); ictal tachycardia 60% PPG-detectable; peri-ictal SpO2 nadir 53–74%±20. Migraine: small g≈−0.3 interictal shift at most (EVD-NEUR-013, E3-downgraded). Anxiety: tonic vmHRV g≈−0.3 to −0.45, reactivity NULL (trait not phasic; EVD-NEUR-009, E5 ×2). Panic: modest surges +10–30 bpm, many attacks HR-invariant (EVD-NEUR-010, E2/E3 partially null — textbook >120 bpm stereotype refuted; hyperventilation only +4.4 bpm).

**8.2 Mechanisms.** α-synuclein autonomic neurodegeneration (PD/MSA/PAF — pre- vs postganglionic split); REM-atonia loss (RBD); ictal autonomic-network involvement; panic = sympathoadrenal surge + hypocapnia appraisal loop; anxiety = tonic central-autonomic network tone. Resting HR in PD: do NOT perturb (direction unresolved — controlled data show no difference).

**8.3 Primary vs compensatory vs downstream.** Primary: neurodegeneration/ictal events. Downstream wearable signals: HRV shift, OH, EDA blunting (MSA) vs surges (stress/panic), nocturnal patterns. Levodopa is a mandatory medication module (nearly all PD medicated): time-locked vasodepressor 30–90 min post-dose.

**8.4 Overlaps.** Low-vmHRV axis shared with anxiety/pain/depression/T2DM/inflammation/aging/sleep-loss/alcohol/beta-blockers/deconditioning (g≈−0.3 to −0.6 all) — ONE shared "tonic vagal gain" knob (endorsed). OH shared with CAN/PPH/fasting/levodopa/dehydration — contrast pair vs POTS tachycardia. OSA comorbidity across PD (20–70%), epilepsy (33%), MSA (60%) — one CORE generator parameterized by AHI. EDA surges shared across stress/pain/panic/ictal — panic-vs-seizure confusion is a REQUIRED validation test. RHR/HRV anxiety layer is a mandatory confound in POTS-like cohorts (high anxiety comorbidity).

**8.5 Heterogeneity.** OH prevalence 7-fold spread by setting; ~1/3 of ≥60-mmHg drops asymptomatic; panic bimodal (HR-invariant attacks); TSST responder/non-responder; cold-pressor HR bimodal; iRBD PPV prevalence-dependent (3–6% at 1.5% prevalence — base-rate honesty mandatory).

**8.6 Temporal change.** Prodromal HRV/RBD years before PD motor onset (conversion 6.3%/yr); levodopa daily ON/OFF patterning; cortisol habituation with repetition (SAM does not habituate); MSA anhidrosis progression +6.2%/yr; morning OH worsening via nocturnal pressure natriuresis.

**8.7 Stress-response differences.** Anxiety reactivity null ⇒ implement tonic layer only; panic events modest-magnitude with hyperventilation coupling (+4.4 bpm, MAP −3.5); MSA blunted EDA/stress responses (contrast vs POTS/anxiety hyper-EDA); neurogenic supine hypertension gives reverse-dipping (opposite direction from OSA/inflammation non-dipping — needs joint modeling).

**8.8 Plausible wearable appearance.** Seizure events: IMU burst + EDA surge + HR surge + SpO2 dip (published-pipeline replay, sens ≥90%/FA ≤1/24h band). iRBD: sleep-movement features (≥7 nights, ≥30-s epochs). PD: tremor spectral peak + blunted ΔHR/ΔSBP proxy + post-dose OH windows. Panic: context-bound HR+EDA+RR surges 15–60 min, deliberately hard to separate from stress/seizure by HR alone. nOH: blunted-compensation index from posture+HR without absolute BP. OSA: sawtooth SpO2/HR.

**8.9 Evidence status & binding downgrades.** D3 (migraine E5→E3), D11 (PD OH meta E5→E4), D16 (iRBD RAR collapse). Gaps: no large ambulatory panic EDA/BP dataset (panic magnitude genuinely unknown); seizure-study primary DOIs unpulled (dossier-flagged); levodopa effect E3 no placebo arm.

**8.10 Validation anchors / do-not-fabricate.** Anchors: Norcliffe-Kaufmann ratio distributions (nOH <0.3–0.5 vs POTS exaggerated vs healthy >0.5–1.0 — three-way orthostatic discrimination test); EMU SpO2/GTCS statistics; actigraphy AUC band 0.84–0.92 with prevalence-adjusted PPV; TSST effect-size distributions with cortisol-only habituation. Latent-only: MIBG, plasma NE, TST %anhidrosis, cortisol, ETCO2, QSART.

---

## 9. CONDITION: METABOLIC DYSFUNCTION (IR → T2DM / CAN) + fasting/meal states — registry claims EVD-METB-001..014

Full text: `METABOLIC_PHYSIOLOGY_EVIDENCE.md` M1–M36. Observability discipline: glucose/insulin/RER/BAT/ketones latent-only; HR/HRV are the primary observable carriers.

**8.1 What differs from healthy.** T2DM (even <5 y): resting tachycardia +5–10 bpm, globally reduced HRV both arms (SDNN −6–15 ms; poor control SDNN 26.6 vs 42.3), severity scales with duration (EVD-METB-014, **E2 after binding downgrade** — no meta-analysis located; cross-sectional only). Exercise: chronotropic incompetence (index 7.88 vs 10.91), blunted HRR (EVD-METB dossier M33, E3/E4). Postprandial: higher/later/prolonged glucose peaks (>180 mg/dL, >90 min), PPH 20–40% with CAN, absent HR compensation (M34, E2/E4). CAN: OH + resting tachycardia + postprandial-orthostatic compounding (M36). GV elevated pre-diagnosis (SD 18 vs 13, CV 17 vs 14, MAGE 36 vs 27; AUC 0.81 — EVD-METB-003, E2/E4).

**8.2 Mechanisms.** Autonomic neuropathy (both arms), metabolic inflexibility (resting RER 0.85–0.90, E1/E2), sleep-restriction-induced insulin resistance (−10 to −20% SI after ≥2 short nights, E3), circadian misalignment per se (+6% glucose despite insulin +22%, E3), dawn phenomenon (+20–40 mg/dL T2D vs +5–15 healthy).

**8.3 Primary vs compensatory vs downstream.** Primary: insulin resistance/neuropathy. Downstream wearables: nocturnal HRV/RHR (cleanest window), blunted exercise HR dynamics. Confounds: fitness, age, meds (beta-blockers mimic; athlete bradycardia opposite), sleep, alcohol — non-specific by construction.

**8.4 Overlaps.** Resting-HR elevation and low-HRV shared axes (matrix §16); PPH/OH shared with PD/MSA/deconditioning; postprandial HR bump shared healthy-core (disease = amplitude/duration modulation); fasting orthostatic blunting shared with dehydration/heat.

**8.5 Heterogeneity.** Duration-stratified severity; sex/protocol-dependent fasting autonomic direction (EVD-METB-013, E3-flagged); healthy glucotypes (1/3 of "healthy" show dysregulated excursions — normative means hide heterogeneity); NEAT trait σ 150–300 kcal/d.

**8.6 Temporal change.** Timescale library: postprandial 0–4 h; dawn 04:00–08:00; fasting piecewise 12→24→36→72 h (HR −4 at 24 h → baseline 36–48 h → +3–6 at 72 h, approximate-secondary flag); sleep-debt accumulation 1–7 nights; misalignment days; acclimation days–weeks; disease progression years.

**8.7 Stress-response differences.** Blunted HR rise and slow HRR1 in exercise; absent postprandial HR compensation in CAN; sleep-restriction personas show elevated nocturnal HR + reduced RMSSD as observable correlates (E2-level magnitudes).

**8.8 Plausible wearable appearance.** Nocturnal PPG-HRV shift, resting HR +5–10 bpm, exercise HRR1 <12 bpm fraction ↑, postprandial ΔHR prolonged, CGM channels (if worn) with MARD 8–13%/lag 5–15 min/compression-low artifacts; EE channels MAPE 20–35% with activity-type-dependent error (resistance training ≈ near-random).

**8.9 Evidence status & binding downgrades.** EVD-METB-014 → E2 (no meta located); EVD-METB-002 E3/E4-borderline (n=21 primary; pregnancy time-to-peak IQR 40–124 min — huge lability); EVD-METB-013 E3-flagged contradiction; TEF "10%" DOI unverified; 72-h fast HR "+3–6 bpm" secondary-source approximation; M14 EE inaccuracy E5 (negative result stands).

**8.10 Validation anchors / do-not-fabricate.** Anchors: Shah 2019 CGM percentiles (TIR 96%, CV 17%); Freckmann postprandial curves; AEGIS GV; wearable-EE vs latent-EE MAPE 20–35%; Buxton/Scheer/Morris lab effects. Do not fabricate: optical glucose, insulin/RER/BAT/ketone channels, calibrated cuffless BP for PPH (±5–10 mmHg error exceeds young-adult signal), postprandial EDA waveform (E1), "fat-burning" HR signal beyond zone heuristics (Fatmax spread 42–82% VO2max).

---

## 10. CROSS-CONDITION OVERLAP MATRIX (section 16 — binding for generation)

**Purpose (normative):** prevent OCPE from encoding nonspecific systemic physiology as disease-specific signatures. A mechanism marked **SHARED** must be implemented as a composable shared latent and must never be emitted as a discriminating feature for any single condition. Marks: **C** = healthy-core (present in healthy reference; disease modulates amplitude), **S** = SHARED across ≥2 conditions, **D** = condition-dominant (closest to specific, still with caveats), **—** = not a documented feature. Built from the 14-item candidate nonspecific-mechanism list (INDEPENDENT_REVIEW_PASS2 §3), endorsed as binding.

| Mechanism / observable axis | Healthy | POTS | ME/CFS | Long COVID | hEDS | Autoimmune/inflammation | Neurological (PD/MSA/migraine/anx/panic) | Metabolic (T2DM/CAN) | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| Orthostatic intolerance / exaggerated ΔHR | C (33–60% exceed 30 bpm on aggressive protocols — D14) | D (defining, but boundary protocol-fragile) | S (~28% POTS, 14% dOH; CBF drop near-universal) | S (graded axis 0–79% by method) | S (7–49% subset) | S (Sjögren's standing tachycardia) | S (contrast: nOH blunted) | S (CAN) | **SHARED**; only the *combination* with phenotype context approaches specificity |
| Altered autonomic response — tonic vagal gain axis (↓RMSSD/HF) | C (age/sex/fitness/breathing) | S (rMSSD −15 ms, partly HR-coupled) | S (−0.37 SD) | S (−10–20%, ~50% penetrance) | S (−30%) | S (CRP-dose-dependent) | S (g≈−0.3 to −0.6 across PD/anx/pain/migraine) | S (SDNN −6–15 ms) | **SHARED — single shared "tonic vagal gain" knob (endorsed)** |
| Impaired recovery (post-exertion / post-stressor) | C (HRR1 ~20±6; HRV recovery 3–6 h) | S (fast supine recovery is actually preserved — discriminator) | S (slowed 9–13+ h; PEM) | S (slowed 9–13 h) | — | S (flare tails ~2.5 mo) | S (habituation asymmetry) | S (blunted HRR) | **SHARED**; slowed-recovery kernel is the common physiological form (D2) |
| Reduced exercise tolerance | C (fitness axis) | S (SV-limited, deconditioning entangled) | S (−5.2 mL/kg/min, effort-coupled) | S (−4.9, CI trait 30%) | S (MVPA↓) | S (flare days) | S (PD motor) | S (CI + HRR) | **SHARED**; deconditioning axis inseparable (E0 adjudications) |
| Altered HRV (beyond vagal gain: structure/oscillations) | C (1/f, RSA, LF/HF) | D-ish (0.1-Hz Mayer-wave amplitude↑/phase↓ — altered relationship, E3) | S (nocturnal N2→SWS blunting) | S (SDNN −15–25%) | S | S (mesor ↓) | S | S | Mostly **SHARED**; only POTS Mayer-wave dynamics and ME/CFS stage-coupling are near-specific |
| Temperature dysregulation | C (circadian, menstrual, heat/cold) | S (heat intolerance trigger, E1/E2) | S (flu-like PEM subset, E0 toggle) | S (acute only; NO chronic signature) | S (sudomotor deficit; core-T E0–E1 — defer) | D (fever coupling — but generic) | S (MSA anhidrosis/blunted EDA-heat) | — | **SHARED / generic**; fever module is one core function (age-graded slope, D4) |
| Sleep disruption | C (architecture, OSA machinery) | S (efficiency −6%) | S (SE −3–6%, TIB↑ in PEM) | S (~30% penetrance) | S (~60% + OSA branch 32%) | S (biphasic dose-dependent) | S (RBD, SRBD, OSA comorbidities) | S (sleep-debt→IR) | **SHARED**; disease-specific *staging* accuracy unstudied (gap) |
| Vascular dysfunction | C (aging/stiffness) | S (pooling phenotypes) | S (preload failure) | S (FMD −3.35%, E2-high-heterogeneity) | S (narrative E0–E1!) | S (FMD/PWV, tocilizumab-reversible) | S | S (CAN/PPH) | **SHARED and largely LATENT** — no PPG-observable allowed (EVD-AUTO-011) |
| Systemic inflammation | C (low-grade variance) | — | S (PEM component) | S (hsCRP +0.8 severe tier only; labs null binding) | — | D (core domain) | S | S | **SHARED core latent** (one `systemic_inflammation` state + wrappers) |
| Step/activity suppression | C (behavior) | S | S (severity gradient + boom-bust) | S | S (MVPA↓, kinesiophobia) | S (gout −841/d; RA symptomatic-only) | S (PD) | — | **SHARED** — indistinguishable at the step channel; slow-gait undercount (5–30% error) is an observability confound correlated with ME/CFS severity and elderly PD/MSA — belongs here so severity is not overestimated from steps |
| EDA alterations | C (SCL/SCR norms, arousal) | — | — | — | S (QSART deficit, latent) | — | S (surges: stress/pain/panic/ictal; blunted: MSA) | — | **SHARED both directions**; panic-vs-seizure confusion test required; ambient heat/humidity artifact |
| Pain–autonomic coupling | C (cold-pressor module, bimodal HR) | S | S (FM overlap) | S (painful-LC SFN subgroup) | D (near-universal pain, but coupling uses transferable priors) | S (gout/IBD flares; IBD null: HRV/steps not predictive of next-day pain) | S (chronic-pain layer g moderate) | — | **SHARED** (transferable E5 prior, non-disease-specific) |
| Medication masks | C (beta-blockers etc. in healthy too) | S (propranolol/ivabradine/midodrine…) | S | S | S (vasoactive meds aggravate) | S (steroids RHR↑/sleep↓/CRP-decorrelate; biologics restore) | S (levodopa post-dose OH; SSRIs HRV) | S (beta-blocker mimics CAN) | **SHARED confound layer** — cross-disease gain masks, first-class |
| Deconditioning | C (fitness axis −8–12 bpm RHR) | S (cause-vs-consequence unresolved) | S (activity-matching erases VO2max diff) | S (common in reduced-capacity) | S (never partialed out) | S (RA RHR partly deconditioning) | S (PD elderly) | S | **SHARED latent axis, sampled independently of disease severity** |
| Post-infection state | C (acute infection envelope) | S (post-infectious onset common) | S (60–70% post-infectious) | D (defining) | — | S (infection = flare trigger) | — | S (post-COVID diabetes RR 1.4 severe tier) | **SHARED base layer** (post-acute infection RHR trajectory module) on which phenotypes compose |

### 10.0 Coverage of the 14-item candidate nonspecific-mechanism list (INDEPENDENT_REVIEW_PASS2 §3 — binding)

| Review item # | Candidate nonspecific mechanism | Where handled above |
|---|---|---|
| 1 | Low tonic vagal HRV | Matrix row 2 → SHARED latent #1 (single tonic vagal gain knob, endorsed) |
| 2 | Elevated resting HR | Matrix rows 2/9/13/14 (inflammation core, deconditioning axis, POTS D13 spectrum, steroid mask); within-person deviation semantics §11.1 |
| 3 | Exaggerated orthostatic tachycardia | Matrix row 1 → SHARED latent #4 (graded axis + D14 protocol-conditioned reference) |
| 4 | Blunted orthostatic compensation / OH | Matrix row 1 neuro/metabolic cells → condition-specific baroreflex-failure gain (§10.1 neuro) + contrast pair vs #3 |
| 5 | Activity/step suppression | Matrix row 10 → SHARED; slow-gait undercount confound folded in |
| 6 | Sleep fragmentation / ↓efficiency | Matrix row 7 → SHARED latent #5 |
| 7 | Nocturnal HR elevation / blunted dipping | Matrix rows 7/9/14; reverse-dipping (neurogenic supine HTN) vs loss-of-dip joint modeling flagged (§8.7) |
| 8 | EDA surges | Matrix row 11 → SHARED both directions; panic-vs-seizure confusion test |
| 9 | PEM-like delayed symptom flare | Matrix row 3 → SHARED latent #6 (delay-to-peak 12–48 h shared machinery; ME/CFS trigger-dose state is the condition-specific part) |
| 10 | Distal skin-temperature elevation | Matrix row 6 → SHARED/generic; fever module one core function (D4) |
| 11 | Cyclical SpO2/HR sawtooth | Matrix row 7 → one AHI-parameterized CORE generator (latent #5) |
| 12 | Menstrual-cycle RHR/RMSSD modulation | Healthy-core C column; SHARED latent #10 (mandatory core) |
| 13 | Slow-gait sensor undercount | Matrix row 10 observability-confound note |
| 14 | Medication gain masks | Matrix row 13 → SHARED latent #8 |

### 10.1 Shared latent axes recommendation (binding architectural conclusion)

**Composable SHARED latents** (implemented once in core, modulated by every condition; sampling priors per condition, never per-condition custom machinery):
1. **Tonic vagal gain** (vmHRV axis) — one knob; condition layers set distributions; RR-scaling law + respiration/HR/device confound inputs built in (D15).
2. **Systemic inflammation state** (acute impulse + chronic low-grade + flare dynamics) — one core, disease wrappers (RA/IBD/SLE/Sjögren's/gout/infection/LC-tier).
3. **Deconditioning/fitness axis** — sampled independently of disease severity; no baked causal coupling.
4. **Orthostatic dysregulation axis** — graded ΔHR 0→>30 bpm latent continuum with protocol-conditioned healthy reference; POTS label = threshold crossing on top (never a binary disease switch).
5. **Sleep-fragmentation axis + OSA event generator** (AHI-parameterized) — one generator, comorbidity branches everywhere.
6. **Post-exertional recovery kernel** — slowed-recovery (hours) as the physiological default for all conditions; delayed symptom kernel (12–48 h) for PEM-capable personas; speculative delayed physiological second wave E0-off.
7. **Post-acute-infection response layer** — standalone; all post-infectious phenotypes compose on it.
8. **Medication gain-mask layer** — beta-blockers/steroids/levodopa/SSRIs/biologics as cross-disease modifiers.
9. **Stress/pain-pressor/hyperventilation modules** — CORE (TSST, cold-pressor bimodal, hypocapnia).
10. **Menstrual-cycle + circadian modulation** — healthy core, mandatory so female disease personas are not misread.

**Condition-specific** (justified as distinct machinery, not shared):
- POTS: 3-axis subtype mixture (volume/denervation/central gain) with Angeli joint distribution + Fu-2010 competing branch; Mayer-wave loop-gain/phase alteration; fast supine recovery dynamics.
- ME/CFS: PEM trigger-dose state variable (exertion-dose accumulation above VT1 proxy) with symptom/physiology kernel decoupling and boom-bust activity autocorrelation; severity latent with step anchors.
- Long COVID: trajectory-class machinery (8 classes) + incidence modifiers (variant/vaccination).
- hEDS: only as a *composition* of shared axes + pain latent + comorbidity clustering (no unique mechanism is evidence-licensed; explicit "mechanism unknown" annotation).
- Neurological: cardiac-denervation gain (PD), baroreflex-failure gain (nOH spectrum), GTCS/ictal event injectors, RBD REM-movement generator, tremor IMU injector, levodopa module, anxiety tonic trait, panic event layer.
- Metabolic: insulin-sensitivity/GV persona parameters, CAN severity, dawn-phenomenon amplitude, CGM observation channel.
- Autoimmune wrappers: flare generators with disease-specific prodrome lengths and symptomatic/inflammatory discordance rules.

**Anti-laundering rule:** any dataset feature whose between-condition effect-size separation is smaller than the within-condition/within-person variance (per the WHOOP-null, Welltory-null, 24-h-HR-null, Nelson-small-SMD evidence) must be documented as non-discriminating, and classifier-cap sanity checks (ME/CFS ≤0.7–0.8 single-feature; LC ≤0.85) must be wired into the validation harness.

---

## 11. CROSS-CUTTING IMPLEMENTATION CONSTRAINTS (consolidated)

1. **Within-person deviation semantics** for all disease RHR/HRV claims (unify on personal-baseline deltas; between-person absolute thresholds are device/definition-dependent).
2. **Uncertainty representation, never point constants**, for the 23-item must-not-hard-code list (EVIDENCE_AUDIT_NOTES §c): POTS BRS gain, subtype weights, training remission, resting-HR effect, autoregulation gain; 2-day CPET mixture; metabolomic priors; LC POTS prevalence; LC day-2 CPET; hEDS venous pooling, POTS-in-hEDS prevalence, etiology components; skin-tone PPG error; accentuated antagonism k; CBR parameters; SLE HRV; steroid effects; population correlation cells; comorbidity rates; autonomic latencies (soft priors); within-person RHR SD; 24-h-fast shift; menstrual effect sizes.
3. **Perturbation stacking rule:** additive-on-log-scale for HRV recommended; validate per NEURO ST-3 (additive-ish within cross-study bounds). Global rule must be stated before multi-condition personas.
4. **Ground-truth retention + latent/observable discipline:** the latent-only union list (SVR, SV/CO at wrist, venous pooling, cerebral perfusion, core temperature, hydration, optical glucose, absolute BRS, PEM episode, stress ground truth, MIBG, cortisol, ETCO2, insulin, RER, BAT, ketones, endothelial stiffness, cytokines) must be enforced in the generator — no fabricated observable for any of them.
5. **Background-rate honesty:** synthetic controls carry non-zero background symptom/flare/orthostatic rates (RECOVER uninfected arm; healthy 30-bpm exceedance rates); all disease signals are excess-over-background.
6. **AUC-cap realism guards** in validation: ME/CFS single-feature ≤0.7–0.8; LC discrimination 0.75–0.85; RA-flare/IiBD classifier performances never emitted as validated; iRBD PPV prevalence-adjusted.

*End of consolidated disease evidence. Provenance: every claim reference above resolves to `EVIDENCE_REGISTRY.yaml` claim_ids; verbatim dossier grades and scale notes are preserved there. Identifier re-verification is a Pass-3 item (registry DOIs were copied verbatim, including dossier-flagged unverified ones).*
