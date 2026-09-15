# OCPE — Current Phenotype / Perturbation Scope
**Source:** actual repository files (read in full): `knowledge_base/diseases/*.yaml` (7 disease/stressor files, 10 phenotype IDs), `knowledge_base/populations/cohorts.yaml`, `simulation/perturbations.py`, `tests/`, sidecar `.review.yaml` files. Nothing removed or replaced from existing scope; implicit scopes (healthy control) documented as found.

**Legend — implementation semantics (verified in code):**
- *Canonical* = parameters in `parameters_perturbed` are applied by `PerturbationManager` in default mode.
- *Experimental-only* = all effects live in `unverified_parameters` (tier-D, machine-proposed, UNRESOLVED); the phenotype is **computationally identical to healthy control in canonical mode** (test-enforced in `tests/test_steady_state_params.py`) and only acts under `include_experimental=True` / `enable_experimental_mode()`.
- Evidence tiers: A = established human direction/magnitude; B = human data, direction or semi-quantitative; C = machine-proposed fit / scaled from in-silico source within documented ranges; D = machine-proposed hypothesis, unresolved. Evidence levels: 1 (RCT) … 4 (in-silico).
- Known sensor modalities repo-wide: **dry-electrode ECG chest strap (Polar H10: RR/HR/RMSSD/SDNN)** and **optical PPG (HR/PRV waveform)** — the only sensor models implemented (`sensor_models/wearable_sensors.py`); no phenotype has a validated wearable-signature model beyond this.

---

## 1. Healthy Control (reference)
- **name:** Healthy Control — **repository_location:** implicit (`phenotype=None` in `BaroreflexPOTSModel`); cohort `healthy_control_cohort` in `knowledge_base/populations/cohorts.yaml` (n=25, 18–45 y); baseline params in `knowledge_base/equations/mathematical_models.yaml` (`pots_baroreflex_response_model`, 39 params); publication review `knowledge_base/publications/geddes_2022_baroreflex_pots.md`.
- **implemented:** true — **partially_implemented:** true (known structural gaps below).
- **parameters:** full 39-param nominal set (Ral 0.0622, Rvl 0.0167, Cau 1.7213, Cal 0.3726, Cvu 436.36, Es 3.0, Vd 10, kR 25, taur 12.5, RaupM 4.5292, Raupm 0.3019, p2Ru 89.97, RalpM 17.88, Ralpm 1.192, p2Ra 89.97, kE 7, tauE 12.5, EdM 0.03125, Edm 0.00025, p2E 76.62, kH 25, tauH 6.25, HM 3.3333, Hm 0.3, p2H 88.66, TotalVol 4500, VMvl 700, mvl 0.035, dV_veno_max 250, p2V 87.5, kV 8, tau_veno 12, G_sr 50, tau_sr 100, pvl_sr0 3, tauP 2.5). Tiers: 29 base params = Level-4 in-silico source (Geddes 2022), no per-param tier; 10 Cycle-2 venous params = **tier C machine-proposed fits**.
- **physiological_domains:** cardiovascular (5-compartment 0-D + LV elastance), autonomic baroreflex (4 Hill loops + venomotor), orthostatic response, circadian/sleep (logged only, uncoupled).
- **existing_evidence:** Geddes 2022 (DOI 10.1098/rsif.2022.0220, Level 4, confidence 9) — model validated against 25 healthy controls in-source; Heldt 2002 (PMID 11842064) and van Heusden 2006 (PMID 16632542) for Cycle-2 structure; Stewart 2004 pooling range (MP-01). Simulation-verified (sidecar + tests): sustained tilt ΔHR 19.49 bpm, pooling 421 mL.
- **major_missing_evidence:** no skeletal muscle pump (documented known failure; historically 76.1 bpm healthy ΔHR pre-Cycle-2); HRV is uniform ±2% noise (no RSA/LF/HF); demographic priors in `simulation/population.py` (220−age, sex ×0.90 volume, BMI, fitness factors) have **no citations**; circadian modulation of gains planned but unimplemented.

---

## 2. POTS — Postural Orthostatic Tachycardia Syndrome
**repository_location:** `knowledge_base/diseases/pots.yaml` v1.5 (header: "PROPOSED CORRECTION (not yet merged)"); sidecar with 4 reviews (validator PASSED; adversarial-doi-verifier, independent-changeset-reviewer, simulation-verification-coder — all PASSED_WITH_WARNINGS, human L3 pending). Composability is evidence-based: Angeli 2024 (Sci Rep, PMC10761725, PMID 38168762, n=378, tier A) — 41.7% of POTS patients carry two phenotypes, 11.4% all three. Cross-phenotype guard (tier B, Stewart 2002 PMID 12010910; Freeman 2002 PMID 12133874): `mvl`/`VMvl` must NOT be perturbed upward in any POTS phenotype.

### 2a. neuropathic_pots ("Neuropathic POTS")
- **implemented:** true (canonical, partial) — **partially_implemented:** true.
- **parameters:**
  - Canonical (applied): `RalpM` 17.88→11.5 mmHg·s/ml (tier C, Level 4; Geddes 2022 Table 3, factor 0.644 scaled to repo nominal); `Ralpm` 1.192→0.76 (tier C, factor 0.633). Both annotated `application.trigger: head_up_tilt_onset` with 10-s smooth transition (Geddes Eq. 2.16) — **engine does not implement tilt-onset application; applied as static baseline overrides**.
  - Experimental-only (tier D): `dV_veno_max` 250→75 ml (factor 0.30, mid evidence range; direction tier A via Jacob 2000 NP-01: 91–99% blunted leg reflex NE spillover; ~50% sudomotor denervation, Thieben 2007 NP-05). Cycle-3 simulation check COMPLETE: sustained ΔHR 21.2 bpm, target ≥30 NOT met; flat dose-response 18.5→21.7 over factor 0–0.5 (hydrostatic-gate-limited; creep re-expands capacity). "Do NOT promote to parameters_perturbed."
- **physiological_domains:** peripheral sympathetic denervation (arterial vasoconstriction + venomotor reflex), orthostatic pooling, baroreflex (central gain intact per Jacob 2019, NP-07).
- **existing_evidence:** Jacob 2000 NEJM (PMID 11018167, tier A direction / tier B magnitude, n=10); Stewart 2002 Circulation (PMID 12010910, tier B: pooling is arterial vasoconstrictor defect, venous compliance normal); Freeman 2002 (PMID 12133874, tier B: venous compliance lower); Thieben 2007 Mayo Clin Proc (NP-05); Geddes 2022 (Level 4 parameter values).
- **major_missing_evidence:** quantitative human venomotor-denervation magnitude; tilt-onset application semantics unimplemented; model structure cannot currently reproduce the sustained ≥30 bpm criterion even with full denervation (strict-xfail in `tests/test_orthostatic_response.py:212`); no wearable-signature evidence.

### 2b. hyperadrenergic_pots ("Hyperadrenergic POTS")
- **implemented:** true (canonical) — **partially_implemented:** true (SBP pressor criterion unmet).
- **parameters (canonical, applied):** `kR` 23→32, `kH` 27→34, `kE` 7→10, `p2H` 88.5→89.8 mmHg (all tier C, Level 4, Geddes 2022 Tables 3/6); `TotalVol` 4500→3900 ml (tier C, Level 2; Raj 2005 PMID 15837998 measured deficit 689±270 ml; promoted from optional after cycle-3 check: gains alone gave 25.7 bpm <30; with TotalVol=3900 → 34.2 bpm).
  - **Audit finding (this review):** `normal_value` for kR/kH/p2H (23/27/88.5) differs from KB nominals (25/25/88.66); multiplicative scaling means the actually applied values on a fresh model are kR=**34.78**, kH=**31.48**, p2H=**89.96** — not the stated 32/34/89.8.
  - Guard: `dV_veno_max` must remain intact (tier B, Okamoto 2024: gain disorder, not denervation).
- **validation_criteria (in-file, tier A):** tilt ΔHR ≥30 bpm AND upright ΔSBP ≥+10 mmHg (Okamoto 2024, PMID 39109428; ΔHR is NOT larger than other POTS: 34±8 vs 34±5 bpm, p=0.988).
- **physiological_domains:** central sympathetic gain, cardiac β-hypersensitivity (HP-04, Jacob 1999), secondary hypovolemia, Mayer-wave/Hopf bifurcation regime (Geddes 2022).
- **existing_evidence:** Okamoto 2024 (Hypertension, tier A validation signature); Muenter Swift 2005 (PMID 15863453, HP-03: MSNA 208% vs 123% on 30° HUT, tier B gain direction); Angeli 2024 (HP-02); Raj 2005 (Level 2 volume); Geddes 2022 (Level 4 gains). Simulation: MAP pressor surrogate present (+5.1 mmHg, test passes); ΔSBP criterion unmet (−4.0 mmHg; strict-xfail, 0-D pulse-pressure limitation).
- **major_missing_evidence:** upright SBP pressor response not reproducible in the 0-D arterial windkessel; quantitative mapping MSNA→Hill gains is machine-scaled; NE-level dynamics not modeled.

### 2c. hypovolemic_pots ("Hypovolemic POTS")
- **implemented:** true (canonical) — **partially_implemented:** false (meets sustained ≥30 bpm: 34.6 bpm per sidecar/test).
- **parameters (canonical, applied):** `TotalVol` 4500→3500 ml (tier C, Level 4; verified exact match to Geddes 2022 BMI-19/Nadler Eq. 2.15; concordance vs Raj 2005 measured deficit 689±270 ml ⇒ OCPE −1000 ml ≈ 1.5× measured mean — MACHINE-CALIBRATED pronounced extreme; population-mean alternative ~3800 ml documented in-file; Geddes caveat: low BV alone does not reproduce POTS dynamics).
- **physiological_domains:** blood volume homeostasis, venous return / stroke volume, compensatory tachycardia.
- **existing_evidence:** Geddes 2022 (Level 4); Raj 2005 (PMID 15837998, Level 2, gold-standard 131I-albumin, n=15) direction tier A.
- **major_missing_evidence:** magnitude exceeds measured population mean ~1.5×; no renin/aldosterone (hormonal S_horm) coupling; no measured hypovolemia→HRV wearable signature.

---

## 3. ME/CFS — Myalgic Encephalomyelitis / Chronic Fatigue Syndrome
**repository_location:** `knowledge_base/diseases/mecfs.yaml` v1.1 ("PROPOSED CORRECTION (not yet merged)"); PEM machinery in `simulation/time_engine.py`; engine hook `engine.py:132` (`is_mecfs` detection).
### mecfs_metabolic_dysfunction ("ME/CFS Metabolic Blunting")
- **implemented:** true (canonical, minimal) — **partially_implemented:** true.
- **parameters:**
  - Canonical: `HM` 3.3333→3.07 bps (~184 bpm ceiling, ×0.92; tier B, Level 2; Davenport 2019 Front Pediatr, DOI 10.3389/fped.2019.00082, Table 4: 90.6% predicted HR at VAT on CPET-2 vs 101.1% controls, p<0.01, n=47 vs 35). review_status: NEEDS REVIEW — metric-mismatch caveat (% predicted HR at VAT ≠ absolute HRmax).
  - Experimental-only (tier D, UNRESOLVED): `tauH` 6.25→12.0 s; `taur` 12.5→25.0 s ("no supporting source found").
  - Historical note: old citation 10.1186/s12967-020-02575-x was FABRICATED; old HM 2.6 bps was ~3× larger than evidence and replaced.
- **physiological_domains:** chronotropic incompetence, metabolic reserve (R_metab), inflammatory burden (B_infl), post-exertional malaise, autonomic recovery.
- **known_sensor_modalities:** HR/RR ceiling effects via Polar H10; no validated ME/CFS wearable signature modeled.
- **existing_evidence:** Davenport 2019 (tier B, semi-quantitative); Holden 2020 mitochondrial review mentioned only as the *mis*-citation context (no usable parameters).
- **major_missing_evidence:** no quantitative ME/CFS baroreflex time-constant data (tauH/taur unresolved); **PEM is dead code** — `engine.py:120` never passes `current_exertion` to `TimeEngine.step`, so the 12-h delayed PEM trigger can never fire; sleep-based recovery unreachable (is_sleeping hardcoded False); no exertion-intensity construct in the engine at all.

---

## 4. hEDS — Hypermobile Ehlers-Danlos Syndrome
**repository_location:** `knowledge_base/diseases/eds.yaml` v1.2 ("PROPOSED CORRECTION (not yet merged)").
### heds_venous_pooling ("hEDS Vascular Laxity")
- **implemented:** false in canonical mode (`parameters_perturbed: []`) — **partially_implemented:** true (experimental mode only; exercised in `tests/test_experimental_mode.py` and scenario "hEDS + Splanchnic Postprandial Pooling + Fludrocortisone").
- **parameters (experimental-only, tier D, UNRESOLVED):** `Cal` 0.3726→0.65 ml/mmHg (+75%, no quantitative source); `VMvl` 700→987 ml (×1.41 ratio preserved from pre-rescale 195.075→275; cycle-3 scale repair only, still tier D).
- **physiological_domains:** connective-tissue vascular laxity, venous pooling, dysautonomia association.
- **existing_evidence:** association-level only — Gazit 2003 (Am J Med, DOI 10.1016/S0002-9343(03)00235-3, PMID 12867232, tier B qualitative: orthostatic intolerance/OH/POTS in 78% of JHS vs 10% controls; adrenergic hyperresponsiveness; **no compliance/capacity numbers**). Old DOI 10.1016/j.amjmed.2006.10.015 was a wrong paper (asthma) — replaced.
- **major_missing_evidence:** any quantitative human hEDS vascular compliance or venous capacity measurement; parameter-level citations deliberately absent (would falsely imply support).

---

## 5. Autoimmune Dysautonomia (AIDA)
**repository_location:** `knowledge_base/diseases/autoimmune.yaml` v1.1.
### autoimmune_neuropathy ("Autoimmune Autonomic Neuropathy")
- **implemented:** false in canonical mode — **partially_implemented:** true (experimental only).
- **parameters (experimental-only, tier D, UNRESOLVED):** `kR` 25→15, `kH` 25→15 (−40% gain, no quantitative source).
- **physiological_domains:** ganglionic nicotinic AChR autoimmunity, autonomic feedback-loop gain.
- **existing_evidence:** mechanism-level — Vernino 2000 (NEJM, DOI 10.1056/NEJM200009213431204, PMID 10995864, tier B: ganglionic AChR autoantibodies → autoimmune autonomic failure); Sjögren's-AAG (PMID 19097826). Old DOI 10.1002/ana.10659 was a wrong paper — replaced.
- **major_missing_evidence:** baroreflex gain magnitudes in autoimmune autonomic neuropathy (none found); no parameter-level DOIs (deliberate).

---

## 6. Poor Sleep / Sleep Deprivation (SLEEP)
**repository_location:** `knowledge_base/diseases/poor_sleep.yaml` v1.1.
### sleep_deprivation ("Acute Sleep Deprivation")
- **implemented:** false in canonical mode — **partially_implemented:** true (experimental only). Sleep pressure/circadian *machinery* exists in `simulation/time_engine.py` but is uncoupled from parameters and sleep is never entered by the engine.
- **parameters (experimental-only, tier D, UNRESOLVED):** `kH` 25→20 (shallower HR baroreflex Hill curve encoding decreased BRS; direction tier B, magnitude machine-proposed).
- **documented unresolved_gaps (in-file):** elevated resting HR (removed misapplied `Hm` 0.3→0.8 — Hm is the 18-bpm saturation floor, not resting HR; needs p2H/HM/Hm remapping); vagal withdrawal (removed misapplied `kE` 7→5 — kE is sympathetic elastance control, not vagal).
- **physiological_domains:** autonomic balance (sympathetic↑/parasympathetic↓), baroreflex sensitivity, sleep homeostasis.
- **existing_evidence:** direction-level — Zhong 2005 (J Appl Physiol, DOI 10.1152/japplphysiol.00620.2004, PMID 15718408, tier B: 36-h deprivation, n=18, decreased spontaneous BRS). Old DOI 10.5665/sleep.2894 was a wrong paper — replaced.
- **major_missing_evidence:** BRS→kH magnitude mapping; resting-HR encoding path; chronic (vs acute) sleep restriction; any sleep-stage architecture.

---

## 7. Environmental Heat Stress (HEAT)
**repository_location:** `knowledge_base/diseases/heat.yaml` v1.1.
### environmental_heat ("Heat-Induced Vasodilation")
- **implemented:** true (canonical) — **partially_implemented:** true (compartment-mapping caveat; no temperature state).
- **parameters (canonical, applied):** `Raupm` 0.3019→0.174, `Ralpm` 1.192→0.688 mmHg·s/ml (both factor ×0.58; tier B, Level 2; Ganio 2012, DOI 10.1152/ajpheart.00941.2011, PMID 22367508: +1.2 °C core → SVC 0.094→0.163 l/min/mmHg, +73%; n=11 young men, passive heating, supine LBNP; review_status NEEDS REVIEW — whole-body SVC applied to compartmental bounds).
  - Experimental-only (tier D): `Cal` 0.3726→0.5 (direction disputed — heating causes cutaneous venoconstriction/reduced capacitance).
- **physiological_domains:** cutaneous/systemic vasodilation, orthostatic susceptibility; (no thermoregulation dynamics).
- **existing_evidence:** Ganio 2012 (tier B, semi-quantitative). Old citation 10.1152/japplphysiol.00693.2012 was FABRICATED — replaced.
- **major_missing_evidence:** compartmental (upper/lower) distribution of heat vasodilation; core-temperature state variable; sweat/hydration coupling exists only as behavior constants (hydration −0.002/beat, uncited).

---

## 8. Medication Perturbations (MEDS)
**repository_location:** `knowledge_base/diseases/medication.yaml` v1.1. Both old DOIs were FABRICATED (10.1161/01.CIR.94.11.2824, 10.1161/01.HYP.30.5.1102) — replaced.

### 8a. beta_blocker ("Beta-Adrenergic Blockade")
- **implemented:** false in canonical mode — **partially_implemented:** true (experimental only). NOTE: `examples/run_advanced_simulation.py` scenario "Hyperadrenergic POTS + Beta-Blocker under Exercise" runs in **canonical** mode, so the beta-blocker contributes nothing there; `AdvancedValidationSuite.beta_blocker_efficacy` (peak HR <145) is vacuous against it.
- **parameters (experimental-only, tier D, UNRESOLVED):** `HM` 3.3333→2.2 bps (~132 bpm ceiling, no accessible quantitative source); `kH` 25→12 (mapping questioned in-file: conflates receptor blockade with baroreflex loop gain; "consider modeling via HM (and possibly p2H) only").
- **physiological_domains:** β-1 antagonism, chronotropic/inotropic ceiling.
- **existing_evidence:** direction-level — Epstein 1965 (J Clin Invest, DOI 10.1172/JCI105282, PMID 5843708, tier B); Tesch 1985 review (PMID 2866577). Neither yields the 132 bpm cap.
- **major_missing_evidence:** quantitative HR-ceiling and gain effects of beta-blockade on baroreflex control; dose-response; drug identity (nonselective vs β1-selective).

### 8b. fludrocortisone ("Fludrocortisone Fluid Expansion")
- **implemented:** true (canonical) — **partially_implemented:** true (acute phase only; schema cannot express the chronic phase).
- **parameters (canonical, applied):** `TotalVol` 4500→5000 ml (+500 ml magnitude is an assumption; `application.temporal_scope: acute_to_early_chronic_only`; `schema_extension_required: time-varying/phase-dependent perturbations`).
- **physiological_domains:** mineralocorticoid volume expansion (acute), TPR-mediated pressor effect (chronic, **not encodable**).
- **existing_evidence:** Chobanian 1979 (NEJM, DOI 10.1056/NEJM197907123010202, PMID 449947, tier B, n=7: initial sodium retention + plasma-volume expansion; chronic: plasma volume returns to control, pressor effect TPR-mediated). The static +500 ml is CONTRADICTED for the chronic phase by its own citation.
- **major_missing_evidence:** +500 ml magnitude; chronic-phase parameterization (resistance/pressor-sensitivity mapping not proposed — requires human review); dose-response.

---

## Scope summary table

| # | Phenotype ID | File | Canonical params (tier) | Experimental-only params (tier D) | Canonical-mode effect |
|---|---|---|---|---|---|
| 0 | (healthy control) | mathematical_models.yaml | 39-param nominal set (Level 4 / tier C venous) | — | reference |
| 1 | neuropathic_pots | diseases/pots.yaml | RalpM→11.5, Ralpm→0.76 (C) | dV_veno_max→75 | active; criterion unmet even experimental |
| 2 | hyperadrenergic_pots | diseases/pots.yaml | kR→32*, kH→34*, kE→10, p2H→89.8* (C); TotalVol→3900 (C/L2) | — | active; ΔSBP signature unmet |
| 3 | hypovolemic_pots | diseases/pots.yaml | TotalVol→3500 (C) | — | active; meets criterion (34.6 bpm) |
| 4 | mecfs_metabolic_dysfunction | diseases/mecfs.yaml | HM→3.07 (B) | tauH→12, taur→25 | active (HM only); PEM dead code |
| 5 | heds_venous_pooling | diseases/eds.yaml | — | Cal→0.65, VMvl→987 | **inert (healthy-identical)** |
| 6 | autoimmune_neuropathy | diseases/autoimmune.yaml | — | kR→15, kH→15 | **inert** |
| 7 | sleep_deprivation | diseases/poor_sleep.yaml | — | kH→20 | **inert** |
| 8 | environmental_heat | diseases/heat.yaml | Raupm→0.174, Ralpm→0.688 (B) | Cal→0.5 | active |
| 9 | beta_blocker | diseases/medication.yaml | — | HM→2.2, kH→12 | **inert** |
| 10 | fludrocortisone | diseases/medication.yaml | TotalVol→5000 (B, acute only) | — | active |

*Applied values on a fresh model differ from stated perturbed values due to normal_value/KB-nominal mismatch (kR→34.78, kH→31.48, p2H→89.96).*

**No other diseases/phenotypes/perturbations exist anywhere in the repo** (verified by full-file enumeration of `knowledge_base/diseases/` and `PerturbationManager.phenotypes`; README/vision mention Long COVID, metabolic dysfunction, neurological disorders only as aspiration, with no KB entries).
