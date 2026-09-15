# OCPE — Pass 2 Evidence Audit Notes
**Auditor:** Evidence Auditor (Pass 2). **Inputs:** 13 Pass-1 dossiers + CURRENT_IMPLEMENTATION_MAP.md (repo source audit). **Companion artifact:** EVIDENCE_REGISTRY.yaml (143 claims; normalized E-grades + verbatim dossier grades).

---

## 0. CRITICAL STRUCTURAL FINDING — three incompatible E-scales across dossiers

The dossiers do **not** share one evidence scale:

| Dossiers | Scale semantics |
|---|---|
| HEALTHY, AUTONOMIC, POTS, MECFS, LONGCOVID, EDS, AUTOIMMUNE, METABOLIC, NEUROLOGICAL, POPULATION, SENSOR | E0 hypothesis / E1 mechanistic / E2 observational / E3 controlled experimental / E4 replicated quantitative / E5 meta-analysis-consensus |
| TEMPORAL_MODEL | **INVERTED**: E0 = established consensus ... E5 = engineering judgment |
| WEARABLE_OBSERVABILITY | **METROLOGY scale**: E0 = established standard ... E4 = speculative/marketing ... E5 = background textbook physiology |

Consequences: a naive merge of dossier E-values would invert the strongest and weakest claims of two entire dossiers. In EVIDENCE_REGISTRY.yaml, `dossier_evidence_strength` preserves the verbatim grade and `evidence_strength` is normalized to the standard scale (mapping documented per claim in `scale_note`). **Action item for the pipeline: enforce a single scale definition at the top of every future dossier; add a machine check that rejects dossiers whose scale definition does not match.**

A second cross-dossier disagreement: autonomic latencies are graded **E4 (replicated, incl. human transfer data)** in AUTONOMIC (Claim 3.1) but "expert opinion, no primary citation found" (its E4 on the inverted scale, i.e. weak) in TEMPORAL (autonomic latencies section). The AUTONOMIC grade is better supported (La Rovere review PMC6931942; Berger 1989 PMID 2912176; Saul 1991); registry carries E4 with a wide-prior caveat on the human sympathetic time constant.

---

## (a) DOWNGRADE LIST — dossier E-level appears inflated relative to its own described evidence

| # | Claim (registry ID) | Dossier E | Recommended E | Reason |
|---|---|---|---|---|
| 1 | EVD-POTS-011 (HRV meta-analysis, Swai 2019/2020) | E5 | **E4** | Single meta-analysis with I² = 84–99% on frequency-domain outcomes; the pooled frequency-domain "null" is heterogeneity-driven. Dossier itself documents LF higher-vs-lower and HF lower-vs-unchanged contradictions. |
| 2 | EVD-MECFS-003 (resting HR +4.14 bpm, 43 studies) | E5 | **E4** | I² 62–73%; pooled effect (+4 bpm) is below the within-person day-to-day RHR noise floor (~5 bpm); 24-h average HR null (SMD 0.11 NS). |
| 3 | EVD-MECFS-004 (resting HRV meta) | E5 | **E4** | Small effects (|SMD| ~0.3–0.4), fewer contributing studies, high heterogeneity, nocturnal-direction conflict (Boneva vs Frith). |
| 4 | EVD-MECFS-012 (sleep architecture meta) | E5 | **E4** | High heterogeneity; actigraphy vs PSG disagree on TST/TIB; TST null; scoring-method dependent (R&K vs AASM). |
| 5 | EVD-LCOV-006 (peak VO2 meta, Durstenfeld) | E5 | **E4** | Dossier quotes the meta-analysis's own "low certainty, moderate heterogeneity, high risk of bias" — E5 is self-contradicted. Effect driven by hospitalized samples. |
| 6 | EVD-LCOV-014 (vaccination protection meta) | E5 | **E4** | Dossier documents OR range 0.22–1.03, high heterogeneity, low certainty in the earlier review. |
| 7 | EVD-LCOV-015 (DLCO meta) | E5 | **E4, scope-restricted** | E5 grade applies only to the hospitalized sub-phenotype; must not generalize to the ~91% non-hospitalized LC population. |
| 8 | EVD-AUTO-007 (RA HRV meta, Provan 2018) | E5 | **E4** | RMSSD SMD CI spans −1.35 to −0.44 (3× spread); case-control designs; illustrative raw values from a low-tier journal. |
| 9 | EVD-NEUR-002 (PD OH prevalence meta) | E5 | **E4** | I² 79–98%; 7-fold spread across settings (9.6–64.9%); largest community cohort 10.6%. (The OH *definition* stays E5 consensus.) |
| 10 | EVD-NEUR-013 (migraine autonomic meta) | E5 | **E3** | Direct contradictory meta-analysis (Lee 2019: all standard HRV metrics null); Valsalva I² = 94%; only 7 standardized studies. An E5 with an internal null replication is not E5. |
| 11 | EVD-POTS-013 (exercise-training remission, Fu 2010/2011) | E3/E4 | **E3** | Single n=19 completers-only study; no independent replication; 53% remission must not be quoted as established. |
| 12 | EVD-POTS-014 (resting HR elevation) | E4 | **E3** | Lab replication (+10–20 bpm) is real, but the large real-world dataset (Welltory n=359) shows +~3 bpm with near-complete overlap — a spectrum/label contradiction that caps the grade. |
| 13 | EVD-METB-002 (postprandial glucose time course) | E4 | **E3/E4 borderline** | Primary numeric source is n=21; pregnancy cohort shows time-to-peak IQR 40–124 min (huge within-person lability). |
| 14 | EVD-METB-014 (T2DM resting autonomic shift) | E2/E4 | **E2** | Dossier explicitly states no meta-analysis was located; cross-sectional cohorts only. |
| 15 | EVD-HLTH-006 (postprandial hemodynamics review) | E5 | **E4** | A single recent systematic review of 25 mostly-small studies is not consensus-level; young-adult BP row rests partly on a low-authority commercial synthesis (dossier-flagged). |
| 16 | EVD-EDS-002 (hEDS resting autonomic shift) | E4 | **E4 (borderline; flag)** | Retained because direction replicated across ≥3 independent groups, but every study is n~30–40/arm with pre-2017 criteria contamination and a partial null (Miglis 2017). |
| 17 | TEMPORAL dossier globally | inverted scale | normalized | e.g., "menstrual effects E1-E2" → standard E2-E3; "autonomic latencies E4 (expert opinion)" → standard **E1**. |
| 18 | WEARABLE dossier globally | metrology scale | normalized | e.g., cuffless-BP "E1/E4" spans demonstrated-inference to speculative marketing — split per claim, not averaged. |
| 19 | EVD-METB-013 (24-h fast autonomic effects) | E3 | **E3 (flagged)** | Single randomized crossover n=25; direction contradicted by female-only study (HFnu decreased) — kept E3 but contradiction raised to *moderate*. |
| 20 | EVD-MECFS-005 / EVD-MECFS-007 (HRpeak / 2-day CPET) | E4/E5 | **E4** | HRpeak effect triple the criterion HRmax effect → effort confound; 2-day CPET has a direct null replication (Nelson 2026) and 33% sensitivity at 90% specificity. Not consensus-level. |

**"Replicated" misuse pattern to watch:** several dossiers use "replicated/consistent" for *two small studies from related labs* (e.g., Stewart-lab flow phenotypes EVD-POTS-007; van Campen CBF series EVD-MECFS-006). Single-group dominance is not independent replication — registry marks `replication: low` on these even where the dossier grade was kept.

---

## (b) FABRICATED-PRECISION FLAGS

**B1. Unverifiable / secondary / low-authority citations (copied verbatim to registry, marked):**
- METABOLIC M15 TEF "10%" — DOI 10.1186/1743-7075-1-5 flagged *unverified* by the dossier itself.
- METABOLIC M23 72-h fasting HR "+3–6 bpm" — secondary-source approximation, no primary located.
- HEALTHY: athlete daily-HR 68 vs 76 bpm from a JACC 2025 **news release** (underlying study not inspected); Polar skin-temp range (E0, commercial); superpower.com young postprandial BP (low-authority); ibtaura EDA review (NA authority).
- AUTONOMIC: neurovascular transduction "4.2 ± 0.6 cardiac cycles" from a single conference abstract (UT Arlington) — provisional E2, do not quote as established.
- POTS: postprandial GIP mechanism (Breier et al.) — effect sizes never retrieved; cited via a Springer review.
- MECFS: Bateman Horne severity anchors trace to a clinic PDF; FUNCAP55 to a preprint.
- NEUROLOGICAL: primary DOIs for Poh 2012 / Onorati / Regalia seizure-wearable studies "not yet pulled" (dossier-flagged).
- POPULATION: Speed et al. RHR-definition numbers via "sahha.ai synthesis" (secondary).

**B2. Magnitude claims without distributions (selection — full list in registry `distribution: null` fields):**
- Postprandial HR "+8 bpm" single-lab (Waalen, PMC6590239) quoted without SD.
- POTS medication effect sizes (propranolol, midodrine) — point estimates from n=9–54 crossover trials.
- PEM amplitude "+35–40%" in EVD-MECFS-009 is *derived*, not measured.
- RA Forecast flare AUC ~1.00 / F1 0.95 (28-day pre-flare) and IBD AUC 0.98 (49-day pre-flare) — within-subject imbalanced-data metrics, no external validation; treat as optimistic upper bounds, not performance targets.
- Long-COVID ML AUC 0.951 (n=126, retrospective feature engineering) — overfit; realistic band 0.75–0.85.
- ME/CFS metabolomics AUROC 94–96% — **in-sample only** (Naviaux 2016); never use as classifier targets.
- Oura menstrual dataset (48,720 cycles) — conference abstract, not peer-reviewed; the verified lab n for the same numbers is 26.
- hEDS wearable WHOOP pilot effect sizes not published in abstract (n=26) — registry carries direction only.

**B3. Cross-dossier magnitude conflicts needing adjudication before parameterization:**
1. Postprandial HR: **+5–10 bpm typical** (METABOLIC, multiple controlled studies) vs **+10–20 bpm** (TEMPORAL, clinical-review level only). Recommend +6 ± 3 bpm mixed-meal default with meal-size scaling.
2. Healthy orthostatic ΔHR: HEALTHY model target N(+12, 5) vs POTS dossier tilt-lab control means +23–26 bpm at 10 min vs TEMPORAL "+10–25 bpm". This is the POTS-boundary calibration hinge; HEALTHY dossier itself flags it as "the single most consequential calibration choice." Protocol (active stand vs tilt, referral-lab population) must be a modeled variable.
3. Autonomic latencies: see Section 0 (AUTONOMIC E4 vs TEMPORAL expert-opinion).

---

## (c) MUST-NOT-BE-HARD-CODED — uncertainty-representation list

These claims have genuine contradiction, single-source fragility, or known bias; they must enter the model as **distributions / latent mixtures / sensitivity parameters**, never point constants:

1. **EVD-POTS-010** POTS baroreflex gain (−25% Stewart 2021 vs unchanged Fu/Galbreath vs increased pediatric) — sample −15 to −25% with wide variance; genuinely unresolved.
2. **EVD-POTS-003** subtype mixture weights (Angeli n=378, referral-biased; Thieben disagrees) — provisional weights only.
3. **EVD-POTS-013** 53% training remission — single n=19.
4. **EVD-POTS-014** resting-HR effect size — spectrum-dependent (clinic vs self-report).
5. **EVD-POTS-008** cerebral autoregulation intact vs impaired — expose as uncertain latent gain.
6. **EVD-MECFS-007** 2-day CPET signature — implement as mixture (~50–60% show it); the null arm must remain generatable.
7. **EVD-MECFS-013** metabolomic panels — mechanistic prior only; AUROCs never hard-coded.
8. **EVD-LCOV-004** POTS prevalence in long COVID (0–79% by method) — graded orthostatic latent axis, not a binary or a fixed prevalence.
9. **EVD-LCOV-009** long-COVID day-2 CPET decrement — contradictory; PEM = state transition, not VO2 decrement.
10. **EVD-EDS-003** venous-pooling mechanism in hEDS — optional perturbation with explicit "mechanism untested" flag (no venous-compliance study exists).
11. **EVD-EDS-004** POTS-in-hEDS prevalence (7–49%) — sample from range.
12. **EVD-EDS-008** hEDS dysautonomia etiology (intrinsic vs deconditioning) — no mediation analysis exists; keep components separable.
13. **EVD-SENS-005** skin-tone PPG error — direction unresolved (Shcherbina vs Bent); no magnitude may be baked in.
14. **EVD-AUTN-009** accentuated-antagonism coefficient k (~1–3) — E1/E2 for magnitude; tunable with sensitivity analysis.
15. **EVD-AUTN-003** CBR logistic parameters — n=9; point estimates, not population distributions.
16. **EVD-AUTO-008** SLE HRV magnitudes — unattributable (100% steroid confound).
17. **EVD-AUTO-009** steroid RHR/sleep effects — all indirect; gain modifiers with flagged uncertainty.
18. **EVD-POP-005** unevidenced correlation cells (RMSSD↔BP, EDA↔RHR between-person, steps↔RMSSD) — provisional ranges + sensitivity analysis.
19. **EVD-POP-007** all comorbidity co-occurrence rates — ascertainment-inflated; down-weight 0.3–0.5× for population sampling or declare clinic-like cohort.
20. **EVD-TEMP-005** exact autonomic latency values — soft priors.
21. **EVD-HLTH-001** within-person day-to-day RHR SD — dossier E0-provisional (partially covered by POPULATION CV ~4.6%; reconcile before fixing).
22. **EVD-METB-013** 24-h-fast autonomic shift — single study, sex/protocol-dependent direction.
23. **EVD-TEMP-008** menstrual effect sizes — verified lab n=26; large-N source is an abstract; per-person heterogeneity high.

---

## (d) COVERAGE GAPS — required-by-design claims with no evidence at all

1. **Direct ME/CFS multi-day wearable PEM dataset does not exist** (EVD-MECFS-010): the PEM wearable signature is extrapolated from a long-COVID cohort (n=127). Any ME/CFS PEM wearable channel in synthetic data is an *assumption*, and must be labeled as such.
2. **No validated PEM detector** from wearables (WEARABLE dossier): PEM remains latent-only.
3. **hEDS venous compliance / pooling**: never measured (EVD-EDS-003); the core narrative mechanism is E0–E1.
4. **hEDS dysautonomia mechanism adjudication** (deconditioning vs intrinsic): no study partials out fitness (EVD-EDS-008).
5. **Orthostatic ΔHR event-to-event reliability**: no test-retest study in healthy or POTS (POPULATION Section F; provisional CV 15–25%).
6. **Population correlation cells**: RMSSD↔BP, EDA↔RHR/RMSSD between-person, steps↔RMSSD large-n, healthy core-temp↔RHR — all unevidenced (POPULATION Section F).
7. **Factor-analytic structure of autonomic/wearable batteries**: no direct study (POPULATION Section G is theory-driven, E0 for the architecture itself).
8. **Adult SpO2 population distribution**: pediatric anchor only (HEALTHY gap 1).
9. **Adult fever→HR slope**: the large regression (n=188,635) is pediatric; adult ~10 bpm/°C remains heuristic (EVD-AUTO-003).
10. **Large ambulatory panic dataset (EDA/BP/HR)**: none found (EVD-NEUR-010); objective panic magnitude is genuinely unknown.
11. **Fludrocortisone in POTS**: no adequate RCT (EVD-POTS-015, dossier E0) — yet it is a canonical repo perturbation (see tier audit).
12. **POTS medication prescription-prevalence distributions**: none exist (POPULATION E.1, E0); only study-arm frequencies.
13. **Severe ME/CFS physiology**: severe patients are systematically excluded from lab/CPET studies — all severe-tier parameters are extrapolations downward.
14. **Steroid wearable-effect effect sizes**: all indirect (AUTOIMMUNE gap).
15. **Low-grade-inflammation temperature-setpoint shifts and PPG-stiffness observability**: no evidence; must remain latent-only (EVD-AUTO-011).
16. **Within-person day-to-day resting-HR SD in HEALTHY dossier** (E0) — partially covered by POPULATION (Quer CV 4.6%, 5-day ICC 0.87); reconcile the two dossiers before parameterizing.
17. **Sleep staging for ME/CFS/LC by wearables**: disease-specific staging accuracy unstudied (healthy-only κ values).

---

## (e) REPO TIER STRUCTURE AUDIT (tier A–D + evidence_level 1–4 vs E0–E5)

Repo scheme (from CURRENT_IMPLEMENTATION_MAP.md §4): **A** = established human direction/magnitude; **B** = human direction/semi-quantitative; **C** = machine-proposed fit within documented ranges or scaled from in-silico source; **D** = machine-proposed hypothesis, unresolved. Separate `evidence_level` 1–4 where **4 = in-silico** (a provenance axis, not a strength axis).

**Consistency verdict: partially consistent, with four structural defects.**

Mapping sanity: A ≈ E4–E5 ✓; B ≈ E2–E3 ✓; D ≈ E0 ✓ (and the engine correctly makes tier-D values inert by default — "honesty-by-default" is the strongest part of the repo's evidence discipline). **C is not an evidence grade at all** — it is a provenance label for machine-fitted magnitudes; in E0–E5 terms most tier-C values are evidentially E0–E1 (in-silico source, human-range-constrained). This is defensible *if* labeled as such; it is not currently labeled as an evidence weakness.

Defects found:
1. **Uneven application:** only the 10 Cycle-2 venous parameters carry tier-C markers; the 29 Geddes-base parameters have **no per-parameter provenance** yet trace entirely to a Level-4 (in-silico) paper — evidentially ~E1 but functioning as canonical tier-A-equivalent in the engine. The entire canonical core is one in-silico citation deep.
2. **Tier vs evidence conflict:** hypovolemic `TotalVol=3500` is the Geddes in-silico value, ~1.5× the Raj 2005 measured deficit (689±270 mL); it is flagged "MACHINE-CALIBRATED" in-file but still treated as canonical. Under E0–E5 discipline this is a tier-C value in direct conflict with E4 human data — the human data should win the canonical slot.
3. **Untiered shadow parameters:** all constants in `symptoms.py`, `behavior.py` (meal ×0.75/×1.15, T_sym+0.3), `population.py` (HM=(220−age)/60 — note: *superseded Fox equation* vs E5 Tanaka evidence in the dossiers), `time_engine.py` (PEM 12-h delay/0.6 threshold/**2-h resolution** — flatly contradicts E4 dossier evidence: onset 12–48 h, recovery days-weeks), and `wearable_sensors.py` (σ=1 ms, dropout 0.5%) carry **no tier at all**, escaping the governance scheme. The sensor case is perverse: the KB holds E4–E5 validation data (Polar H10 LoA −2.3/+2.4 ms, ICC 0.99) that the code ignores in favor of untiered hardcoded values.
4. **Two conflated axes:** `evidence_level` 1–4 (source type, 4 = in-silico) and `evidence_tier` A–D (strength/provenance mix) are orthogonal scales presented interchangeably in files. Recommend replacing both with: E0–E5 (strength, standard scale) + a separate provenance enum {human-experimental, human-observational, meta-analysis, in-silico, machine-fitted, engineering-judgment}.
5. **Governance drift:** dead inline `phenotypes:` blocks in `mathematical_models.yaml` contradict `diseases/pots.yaml` (kR 40 vs 32, etc.); `normal_value`-vs-nominal mismatches silently change applied multiplicative perturbations (kR applies 34.78 not 32). Historical: 4 of 8 original disease-file DOIs were fabricated/wrong-paper (corrected after adversarial review) — the dossier-level citation discipline in Pass 1 was much better than the repo's original state, and the repo should adopt the registry's verbatim-DOI policy.
6. **PEM parameterization conflict (highest-priority single fix):** repo PEM = R_metab−0.5 / B_infl+3.0 triggered 12 h post-exertion, resolving in 2 h — vs registry EVD-MECFS-008/009 (E4/E3): onset 12–48 h, peak 24–48 h, recovery median ~12.7 d (range 1–64 d). Current repo constants are off by ~2 orders of magnitude on recovery and are also dead code (exertion never passed to TimeEngine).

**Recommended tier/E-scale harmonization:** tier A ⇒ registry E4–E5 required; tier B ⇒ E2–E3; tier C ⇒ provenance "machine-fitted" + strength E0–E1 + mandatory human-range citation; tier D ⇒ E0 + engine-inert (current behavior, keep). Add a CI check: no canonical parameter without an E-level and provenance tag; no E0/E1 value in canonical mode.

---

*All DOIs/PMIDs in the registry were copied verbatim from the dossiers, including identifiers the dossiers themselves flagged as unverified; verbatim copying preserves traceability but does not constitute re-verification. Identifier re-verification is a Pass-3 candidate.*
