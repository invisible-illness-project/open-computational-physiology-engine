# OCPE — Scientific Debt Register (Phase 2 close)

**Purpose:** every known limitation, disclosed gate, unresolved gate, strict-xfail, and provisional/research parameter class, each with description, scientific consequence, why accepted, remediation path, and priority.
**Sources read:** `/mnt/agents/output/ocpe_repo`: `validation/release_gates.yaml`, `docs/validation_report.md`, `docs/orthostatic_reference.md`, `docs/validation_strategy.md`, `simulation/time_engine.py` (W5 comments), `tests/test_orthostatic_response.py`, `knowledge_base/diseases/pots.yaml`, `validation/provenance_gate.py`; `/mnt/agents/output/ocpe/`: `PARAMETER_SPECIFICATION.yaml` (tier classes `provisional_with_uncertainty`, `requires_further_research`), `OCPE_RESEARCH_GAP_ANALYSIS.md` (P1/P2 registers), `ADVERSARIAL_REVIEW_REPORT.md`.
**Priority scale:** HIGH = release-blocking or release-conditioning · MEDIUM = must be carried on every released record · LOW = disclosed, quality improvement.

---

## A. Gate-level debt (from `validation/release_gates.yaml`, post-W5)

### SD-01 — L3 POTS–healthy contrast below meta-analytic CI floor at small n — **HIGH (release-blocking)**
- **Description:** L3 `3.1_hypovolemic_pots_rate` FAIL. Ascertainment-matched stratum (simulated subjects meeting the ≥30 bpm 10-min HUT criterion defining EVD-POTS-011 cohort membership) contrast = **+14.83 bpm** vs meta-analytic +19.88 [15.24, 24.52] — 0.41 bpm below the CI floor at validation-cohort n=2 per group. Shortfall driven by the n=2 healthy control mean 38.23 bpm (frozen reference 34±3). Full-mixture contrast (+14.83) is informational by W5 re-specification (`839cc18`).
- **Scientific consequence:** at current Monte-Carlo size the simulated disease–healthy separation cannot be shown consistent with the E4 meta-analytic anchor.
- **Why accepted (temporarily):** the gate is INTENTIONALLY LEFT FAIL; the phenotype was deliberately **not** tuned to pass. n=2/group is a `--fast`-mode artifact; the healthy-tail and contrast statistics are under-resolved by construction at this n.
- **Remediation path:** full-mode (n=4 per group) re-run with unchanged methodology — **in progress at this writing, result unresolved**. If it fails at adequate n, the severity-mixture calibration (not the point phenotype) must be revisited against EVD-POTS-004/011 with a documented re-specification review.
- **Priority:** HIGH — the single blocking issue in `RELEASE_DECISION.md`.

### SD-02 — Hyperadrenergic ΔSBP pressor criterion unmet (0-D windkessel) — **HIGH (disclosed limitation, G-P1-01)**
- **Description:** upright ΔSBP ≥ +10 mmHg criterion (Okamoto 2024, tier A) not met; gate-measured simulated ΔSBP **+3.12 mmHg beatwise** (cycle-3 documented −4.0 mmHg; the frozen `docs/orthostatic_reference.md` still quotes −4.0 — documentary drift I-1). 0-D windkessel: pulse pressure narrows on tilt as stroke volume falls; the MAP pressor surrogate (~+5 mmHg) is present but is **not** the clinical criterion. Gate L3 `3.1_hyperadrenergic_dsbp_limitation` = DISCLOSED_LIMITATION; strict-xfail `test_hyperadrenergic_sbp_pressor_criterion`.
- **Scientific consequence:** the hyperadrenergic phenotype cannot express one of its defining clinical signatures; downstream ΔSBP-based analyses of synthetic hyperadrenergic records are invalid.
- **Why accepted:** model-structure limitation, not an evidence failure; disclosure is enforced by the evaluator (`report["limitations"]`, `[LIMITATION]`) — never silently passed. Fixing requires new model structure.
- **Remediation path:** add a pulse-pressure-generating compartment (distributed arterial segment) or emit ΔSBP from a validated surrogate with a limitation flag (GAP G-P1-01, complexity M).
- **Priority:** HIGH (carried on every hyperadrenergic record).

### SD-03 — PRCP L4 comparison protocol-mismatched; slow-ramp sim mode missing — **MEDIUM**
- **Description:** L4 `4_prcp_orthostatic_wasserstein` reclassified DISCLOSED_LIMITATION (W5, `50eb615`). Wasserstein distance 17.14 bpm between simulated healthy tilt ΔHR (licensed 10-min 70° HUT, Plash minutes 5–10 sustained anchor; sim 28.51/34.48 bpm) and 11 real PRCP episodes (slow-ramp tilt, ~3-min hold; real mean of listed episodes ≈ 14.7 bpm). Window semantics: final 60 s of hold vs final 120 s supine; simulated window minutes 2–3 post-ramp.
- **Scientific consequence:** no like-for-like external real-data comparison of the orthostatic response currently exists at L4; the PRCP numbers stay visible but cannot pass.
- **Why accepted:** matching the PRCP early-hold distribution would require de-calibrating the Plash-2013-anchored sustained response — forbidden tuning (W4-1 calibration-conflict analysis, commit `70b8d91` message). Protocol conditioning is a G-P0-09 principle.
- **Remediation path:** implement a protocol-matched **slow-ramp simulation mode** (~3-min hold) for a like-for-like PRCP comparison (logged explicitly as scientific debt in the gate record).
- **Priority:** MEDIUM.

### SD-04 — EUROBAVAR L4 gate unresolved (infrastructure) — **MEDIUM**
- **Description:** L4 `4_eurobavar_reflex_gain` UNRESOLVED: fetch fails with `SSL: CERTIFICATE_VERIFY_FAILED — self-signed certificate`. Exact error recorded in the gate.
- **Scientific consequence:** the supine→standing reflex-gain external comparison has never been executed; baroreflex gain realism is asserted from internal evidence only.
- **Why accepted:** infrastructure failure, not a scientific result; the gate fails open to `unresolved`, never to pass.
- **Remediation path:** obtain EUROBAVAR via a verified channel (manual download with certificate pinning or mirror) and execute the comparison.
- **Priority:** MEDIUM.

### SD-05 — L3 healthy-HUT ≥30 bpm tail unresolvable at n=2 — **MEDIUM**
- **Description:** L3 `3.1_healthy_hut_distribution` UNRESOLVED: measured fraction 1.00 with 95% CI [0.16, 1.00] against frozen reference band [0.40, 0.60]; mean check passes (38.23 vs 34±3). n=2 < 8 required to resolve the tail band.
- **Scientific consequence:** the healthy false-positive tail at the 30-bpm boundary — "the single most consequential calibration choice" (G-P0-09) — is unverified at current Monte-Carlo size.
- **Why accepted:** small-n limitation of `--fast` mode; mean-level consistency holds.
- **Remediation path:** full-mode re-run at n ≥ 8 per group.
- **Priority:** MEDIUM (bundled with the SD-01 re-run).

### SD-06 — Neuropathic POTS sustained-criterion model-structure gap — **HIGH (scoped xfail, G-P0-03)**
- **Description:** engine-falsified: sustained ΔHR 21.2 bpm vs ≥30 bpm criterion; flat dose-response 18.5→21.7 bpm over venomotor-denervation factor 0–0.5 (hydrostatic-gate-limited; stress-relaxation creep re-expands capacity). Geddes Eq. 2.16 tilt-onset trigger semantics not implemented for this path. Strict-xfail `test_neuropathic_experimental_sustained_criterion`; canonical generation refuses neuropathic POTS.
- **Scientific consequence:** a flagship POTS subtype cannot be shipped as canonical; denervation (Jacob 2000, tier-A direction) is real but the model structure cannot express it.
- **Why accepted:** formal scoping per SWARM_SPEC W1-C — "do NOT fix the science"; shipping silently would be the scientific defect.
- **Remediation path:** bounded stress-relaxation creep state (van Heusden 2006) and/or tilt-onset application semantics (Geddes 2022 Eq. 2.16, 10-s transition); re-run dose-response; retire the xfail or keep scoped.
- **Priority:** HIGH (exclusion must hold on every canonical build).

### SD-07 — Engine residual ~0.17 Hz mean-HR rhythm — **MEDIUM**
- **Description:** post-W4-1 the supine limit cycle (0.078 Hz, mean-HR std ~15 bpm pre-fix) is removed via carotid afferent latency tauP 2.5→0.25 s (E4-cited, EVD-TEMP-005; statics-preserving; supine std 15.2→0.92 bpm at the fix commit). A residual ~0.17 Hz mean-HR rhythm remains (~1 bpm std; gate L2.1 measures supine mean-HR std 1.05 bpm). Documented in `simulation/time_engine.py` (W5 comment): pre-W5 the RSA gate's spectral argmax locked onto this rhythm at 0.165 Hz instead of the respiration frequency.
- **Scientific consequence:** under low-RSA-amplitude trait draws the RSA-peak gate could still select the residual rhythm rather than the respiration line; transient/recovery morphology in short records carries a small non-respiratory oscillation.
- **Why accepted:** amplitude (~1 bpm) is below observable-noise relevance for the shipped channels and all L2 gates pass; full elimination would require further loop-gain restructuring beyond the evidence base.
- **Remediation path:** characterize the residual loop resonance; consider RSA-amplitude floor reporting or a guard in the RSA gate (require peak plausibility vs configured respiration); revisit if wrist-PPG channels (lower SNR) ship.
- **Priority:** MEDIUM (W5 residual risk, monitoring class).

### SD-08 — DFA-α1 thin gate margin — **LOW**
- **Description:** L2 `2.2_dfa_alpha1` measured 1.1758 against band (0.8, 1.2) — margin 0.024 to the upper edge (Task-Force-1996 5-min record, 594 beats). W4-1 measured 0.984 at the fix; the value moved with window standardization.
- **Scientific consequence:** seed/window perturbations could push the healthy fractal correlation out of band without any code change.
- **Why accepted:** in band on the licensed gate configuration; the pre-W5 record length was non-standard and is now fixed.
- **Remediation path:** re-measure across the full cohort in the n=4 re-run; if the cohort distribution hugs the edge, revisit 1/f-Mayer amplitude calibration against EVD-TEMP-001 with a documented (non-tuning) rationale.
- **Priority:** LOW (W5 residual risk).

### SD-09 — Level-5 benchmark matrix absence — **HIGH (governing)**
- **Description:** `level5_status: NOT EXECUTED — the Level-5 benchmark matrix does not exist yet`. Levels 1–4 are necessary but not sufficient; the binding sentence (*"OCPE synthetic data are candidate research artifacts whose utility for any task is unestablished pending the Level-5 benchmark"*) is carried on the gate record, the validation report, and all program deliverables.
- **Scientific consequence:** no utility claim for any task is licensed — not screening-algorithm training, not benchmarking, not education claims of realism.
- **Why accepted:** the matrix requires real-data comparators (G-P1-07: no POTS/ME-CFS/EDS open wearable corpora identified; PRCP mismatch SD-03; EUROBAVAR SD-04) that do not yet exist in curated form.
- **Remediation path:** external dataset curation (G-P1-07), pre-registered L5 matrix per `SYNTHETIC_TO_REAL_BENCHMARK.md` §5, executed and reported including failures; any NC failure invalidates the release regardless of L5 performance.
- **Priority:** HIGH.

### SD-10 — Geddes-2022 single-source backbone — **MEDIUM (G-P1-04)**
- **Description:** the core ODE parameter backbone is Geddes 2022 in-silico (tier C; e.g. hyperadrenergic kR/kH/p2H perturbations carry `evidence_tier: C`, `E0-E1`, `source_claim_ids: null — FLAG: Geddes 2022 in-silico source has no EVIDENCE_REGISTRY claim`, per `knowledge_base/diseases/pots.yaml`). The competing Fu-2010 branch (small LV + hypovolemia + intact baroreflex) is specified in the evidence layer (contradiction Target 2) but **not implemented**.
- **Scientific consequence:** POTS gain perturbations are scenario samples from a single in-silico source, partially engine-falsified (neuropathic path); branch-level structural uncertainty is unrepresented in generated data.
- **Why accepted:** tier-D discipline is applied (direction tier-B human evidence anchors; magnitudes flagged); implementing a second generative branch is a research task (complexity M–L).
- **Remediation path:** scenario-sample the Geddes set; implement the Fu branch as an alternative generative mechanism; require both branches to reach ≥30 bpm via different routes with a parameter-sensitivity report (GAP G-P1-04).
- **Priority:** MEDIUM.

---

## B. Governance debt

### SD-11 — Human (L3) review absent on all KB files; gate warning-only — **HIGH**
- **Description:** pilot manifest `provenance_gate: human_l3_review: ABSENT`, 23 warnings covering every consumed KB file. `validation/provenance_gate.py` documents the policy: "no human (L3) review → WARNING only (never a silent pass, never a hard failure while human review is pending)". W3-A finding F12: closure reviews are self-reviews by the consuming agent; the gate is satisfied in form but not in substance. The W3-A recommended fixes (reviewer identity ≠ build agent; escalate human-L3 absence to failure for release builds) are **not implemented**.
- **Scientific consequence:** given the repo's fabricated-DOI history (4/8 original disease DOIs; Pass-1 record), a canonical dataset can currently be built with zero independent human review.
- **Why accepted:** disclosed loudly (23 warnings in the shipped manifest; F12 recorded in the addendum); human review is an organizational dependency, not an engineering one.
- **Remediation path:** implement reviewer-identity check; escalate human-L3 absence from warning to failure for release builds; complete human L3 review across KB files.
- **Priority:** HIGH (release condition 6).

### SD-12 — Seed-derived `generation_timestamp` predates generating code — **LOW**
- **Description:** pilot manifest `generation_timestamp: 2026-08-23T11:56:41+00:00` is a documented seed-derived deterministic constant (W3-A verified determinism) whose calendar value predates the generating commits (2026-09). W3-A suggested renaming to `build_clock`; not applied.
- **Consequence:** mislabeled metadata; no effect on data or reproducibility.
- **Remediation path:** rename field / add `build_clock` semantics note in schema v0.2.
- **Priority:** LOW.

### SD-13 — RHR calibration mismatch beyond tolerance on POTS (and one healthy) records — **MEDIUM**
- **Description:** per-record honesty flag `rhr_calibration_mismatch_beyond_tolerance` present on all 3 POTS records (baselines 70.90 / 88.02 / 104.89 bpm) and on healthy-003 (75.50 bpm) in the shipped pilot. W3-A noted POTS baselines 72–85 vs targets 67–78 at review time.
- **Consequence:** resting-HR realism of hypovolemic personas is approximate; within-person delta semantics (G-P1-11) are the licensed reading, not absolute RHR.
- **Why accepted:** disclosed per record; the two-pass trait calibration (F11 fix) reduced but did not eliminate the mismatch.
- **Remediation path:** recalibrate RHR target mapping for hypovolemic states (W3-A non-blocking note); freeze nocturnal-RHR channel semantics (G-P1-11).
- **Priority:** MEDIUM.

---

## C. Provisional / research parameter classes (from `PARAMETER_SPECIFICATION.yaml`)

The Phase-1 parameter specification defines two non-implementable tiers whose members enter the generator only as flagged distributions/latents or stay engine-inert:

### SD-14 — `provisional_with_uncertainty` class — **MEDIUM (standing)**
- **Definition (verbatim):** "usable ONLY as distributions/mixtures/latents with explicit uncertainty; on the audit's do-not-hard-code list or single-source/contradicted."
- **Members include (examples read from the file):** carotid baroreflex 4-parameter logistic set (A1 17.1±2.7 bpm, A2 0.15±0.03, A3 99.9±5.0 mmHg, A4 55.6±1.8 bpm, Gmax −0.58±0.10; E3, n=9 single lab — point estimates, NOT population distributions); exact autonomic latencies (vagal delay U(0.2,0.6) s, vagal τ U(0.5,1.5), symp delay U(1.5,2.0), symp τ U(5,15); E4 class / E1 exact values, soft priors); accentuated-antagonism gain k ∈ U(1,3) (E1–E2, mandatory sensitivity analysis); POTS subtype mixture weights (provisional joint: hyperadrenergic 0.75 / hypovolemic 0.449 / neuropathic 0.378 with overlap structure; competing Thieben 2007 marginals recorded); population copula with Gaussian copula on evidenced cells and sensitivity analysis on provisional cells.
- **Consequence:** generated data inherit single-source uncertainty on baroreflex and subtype-composition axes.
- **Why accepted / remediation:** mandatory distribution sampling + per-record honesty flags; targeted literature extraction (G-P2-15) and the L5 program would narrow these. Pilot honesty flags show the class is live: `pooling_capacity_tierC_machine_fitted`, `rhr_calibration_machine_fitted_tierC`, `blood_volume_nadler_provisional_residual_cv`, `bmi/height_distribution_provisional_nhanes_informed`, `fitness_spectrum_provisional_proportions`, `hrv_trait_amplitude_gain_machine_calibrated`, `pulse_waveform_shape_engineering_judgment`, `skin_temp_vasomotor_coupling_engineering_judgment`.
- **Priority:** MEDIUM (standing disclosure).

### SD-15 — `requires_further_research` class — **MEDIUM (standing, engine-inert)**
- **Definition (verbatim):** "evidence absent, engine-falsified, or speculative; engine-inert or optional-flag only."
- **Members include (examples read from the file):** hEDS venous compliance (unmeasured; E0–E1; repo Cal→0.65/VMvl→987 stay tier-D engine-inert, optional flag with "mechanism untested" label); hEDS dysautonomia mechanism split (intrinsic vs deconditioning; unresolved latent, components separable); PEM delayed physiological second wave (E0, default OFF, honesty flag `extrapolated_E0` when enabled); ME/CFS tauH/taur tier-D doublings (unsourced, experimental-only).
- **Consequence:** these axes contribute no canonical signal; enabling them produces labeled extrapolation, not evidence-backed data.
- **Remediation:** external evidence (hEDS venous-compliance study; induced-PEM wearable study; severe-ME/CFS home monitoring) — listed in the gap register as the external items that would most change the model.
- **Priority:** MEDIUM (standing disclosure).

---

## D. Remaining adversarial-review minors (W3-A, carried forward)

| Item | Status |
|---|---|
| Beat count perfectly separates groups (HR-mechanism-derived record length) | NOTE — documented; padding to a fixed beat grid not implemented |
| `registry_version` has no explicit version field (content-addressed `sha:<prefix>` fallback) | NOTE — accepted, documented |
| `cgm_glucose` whitelist exception unusable (exempt from blacklist but absent from observable whitelist → `UnknownSensorInput`) | OPEN minor |
| Raj 2005 689±270 mL figure not externally re-verifiable from the sandbox (single-source, E2, n=15) | Standing single-source flag |
| n=3/group underpowers all classifier statements; AUC results to be re-tested at ≥20/group | Standing — applies to pilot NC2/metadata AUC |
| Stale docstring in `examples/generate_pilot_dataset.py` re wrist/ring canonical status (W3-A DOC minor) | Unverified at HEAD — unresolved |
| PPG validation DOI missing (G-P1-02 companion, P2 retrieval) | OPEN |

---

## E. Debt not remediated in Phase 2 (out of scope, from the gap register)

P1 items not touched and still open: G-P1-06 (PEM unvalidatable — validation exclusion registered), G-P1-07 (external validation corpora), G-P1-08 (skeletal muscle pump absent — active-stand protocols structurally out of scope; tilt-only v1), G-P1-09 (missing physiological systems: thermoregulation, accelerometry, renal/hormonal, immune; respiration and sleep-stage minima implemented under G-P0-05/06), G-P1-11 (RHR definition semantics — partial via SD-13), G-P1-12 (adult fever→HR slope heuristic), G-P1-13 (severe ME/CFS extrapolation), G-P1-15 (hardcoded uncited constants retrofit — partially covered by KB-driven sensor/governance work), G-P1-16 (tilt-onset perturbation semantics generalized). All 22 P2 and 6 P3 items stand as registered. These are tracked in `OCPE_RESEARCH_GAP_ANALYSIS.md`; none is claimed closed by this program.
