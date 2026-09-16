# OCPE — Dataset-Readiness Report (Phase 2 Capstone)

**Program:** OCPE (Open Computational Physiology Engine) dataset-readiness program
**Phase:** 2 of 2 — engineering remediation of the 10 P0 gaps, validation-gate execution, pilot generation
**Codebase:** `/mnt/agents/output/ocpe_repo`, integration branch `swarm/dataset-readiness`, HEAD `e8829bf` ("Release gates re-run post W5 remediation")
**Gate evidence:** `validation/release_gates.yaml` + `docs/validation_report.md`, generated from gate context seed `20260915`, commit `7651fa73211700f73416933ac6dc930cfe2b29d7`, started 2026-09-16T09:55:45, `--fast` mode (licensed cohort n=2 healthy + n=2 hypovolemic-POTS)
**Governing statement (binding, reproduced verbatim from the gate record):** *OCPE synthetic data are candidate research artifacts whose utility for any task is unestablished pending the Level-5 benchmark.*
**Level-5 status:** **NOT EXECUTED** — the Level-5 benchmark matrix does not exist yet (`validation/release_gates.yaml: level5_status`). Levels 1–4 are necessary but not sufficient; no synthetic-utility claim is made or implied anywhere in this report.

---

## 1. Program scope

Phase 1 (evidence swarm, complete) produced 28 artifacts in `/mnt/agents/output/ocpe/`, including an evidence registry of 143 claims graded E0–E5 (`EVIDENCE_REGISTRY.yaml`), parameter specifications, event protocols, contradiction audits, and a gap analysis of 55 gaps (10 P0 / 17 P1 / 22 P2 / 6 P3; `OCPE_RESEARCH_GAP_ANALYSIS.md`). The governing capstone `OCPE_EVIDENCE_AND_SIMULATION_SPECIFICATION_v1.0.md` returned the verdict **NOT READY**: the project's own severity scale defines P0 as "blocks scientifically defensible dataset generation," and ten P0 gaps were open.

Phase 2 (engineering swarm, now concluding) remediated all 10 P0 gaps on branch `swarm/dataset-readiness` under `SWARM_SPEC.md` global rules (never invent a value; tier-D engine-inert in canonical mode; no latent variable as a sensor channel; no mechanism-bypassing disease signal modification; anti-laundering AUC cap; per-constant evidence metadata; regression tests with formally scoped xfails only). Two hardening waves followed the Phase-2 adversarial review: W4 (limit-cycle stabilization + dataset hardening per findings F1–F13) and W5 (gate remediation: exercise autonomic drive, respiration-process category error, DFA window standardization, PRCP gate reclassification, L3 contrast-gate re-specification).

This report is the Phase-2 capstone. Every number below was read from the cited file; nothing is restated from memory. Where a source is silent, this report says *unresolved*.

---

## 2. Remediation summary per P0 gap

Commit references are on `swarm/dataset-readiness` (see `git log`). Full mapping, tests, and gates per gap: `IMPLEMENTATION_TRACEABILITY_MATRIX.md`.

### G-P0-01 — Behavior-parameter compounding bug (engine.py:139) — REMEDIATED
- **What changed:** the engine keeps an immutable `baseline_params` snapshot per run; a new `EventKernel` class (`simulation/event_kernels.py`) composes transient parameter overlays against baseline, never against already-modified parameters; baseline restoration is exact after recovery.
- **Where:** commit `1b1b86a` ("G-P0-01/02/04/06: event kernels, PEM kernels, circadian+sleep coupling, Tanaka HRmax"); exercise-kernel extension in `6791fbe` (W5).
- **Evidence anchors (gate-measured):** L1 `kernel_restoration_ralpm` — meal plateau RalpM 13.41 = baseline 17.88 × 0.75, final 17.88, `restored_exactly: true`, PASS. L1 `kernel_restoration_es` — exercise plateau Es 3.9 = baseline 3.0 × 1.3, final 3.0, `restored_exactly: true`, PASS.
- **Residual status:** none known at gate level.

### G-P0-02 — PEM machinery dead code + constants ~2 orders of magnitude off evidence — REMEDIATED
- **What changed:** two decoupled kernels — a symptom kernel (Gamma onset 12–48 h post-exertion, peak 24–48 h, recovery mean 12.7 d, range 1–64 d) and a physiological slowed-recovery kernel; any delayed physiological "second wave" is E0-labeled and OFF by default; the exertion dead-code path is wired through the engine.
- **Where:** commit `1b1b86a`; `simulation/time_engine.py`, `simulation/event_kernels.py`; tests `tests/test_pem.py` (232 lines added in that commit).
- **Evidence anchors:** Phase-1 evidence DISEASE_EVIDENCE_MECFS.md, CONTRADICTION_AUDIT §6, Moore 2023 (recovery distribution), per `SWARM_SPEC.md` G-P0-02.
- **Residual status:** PEM remains an explicit **validation exclusion** (G-P1-06): no multi-day wearable PEM dataset exists, so PEM channels are labeled extrapolation and are outside the validation harness. This is scientific debt, disclosed — see `SCIENTIFIC_DEBT_REGISTER.md`.

### G-P0-03 — Neuropathic POTS fails its own acceptance criterion — REMEDIATED BY FORMAL SCOPING (not by science fix)
- **What changed:** per `SWARM_SPEC.md` the science was deliberately *not* fixed. Neuropathic POTS is formally scoped experimental-xfail: engine-falsified at 21.2 bpm sustained vs the ≥30 bpm criterion, flat dose-response 18.5→21.7 bpm over denervation factor 0–0.5; remediation paths documented (bounded stress-relaxation creep per van Heusden 2006; Geddes 2022 Eq. 2.16 tilt-onset application semantics). Canonical dataset generation refuses neuropathic POTS (verified live by the W3-A adversarial review: `ExperimentalPerturbationError`).
- **Where:** commit `7d0be96` (`fix/orthostatic-reference`); annotations in `knowledge_base/diseases/pots.yaml`; strict-xfail `tests/test_orthostatic_response.py::test_neuropathic_experimental_sustained_criterion`; `docs/orthostatic_reference.md` §5.
- **Companion disclosure (hyperadrenergic ΔSBP):** the upright ΔSBP ≥ +10 mmHg pressor criterion (Okamoto 2024, tier A) is **not met** — gate-measured simulated ΔSBP +3.12 mmHg beatwise (cycle-3 documented value −4.0 mmHg). 0-D windkessel limitation: pulse pressure narrows on tilt as SV falls; the MAP surrogate (~+5 mmHg) exists but is **not** the clinical criterion. Surfaced by the evaluator as a **DISCLOSED_LIMITATION** gate (L3 `3.1_hyperadrenergic_dsbp_limitation`), never silently passed; strict-xfail `test_hyperadrenergic_sbp_pressor_criterion` (GAP G-P1-01).
- **Residual status:** model-structure gaps remain open as scoped scientific debt (both strict-xfails active).

### G-P0-04 — Engine/KB parameter mismatches + dead data + Fox HRmax — REMEDIATED
- **What changed:** hyperadrenergic `normal_value`s reconciled to KB nominals so ratio-scaling applies the documented values: kR normal 25.0 → applied 32.0 (was 23 → 34.78), kH normal 25.0 → applied 34.0 (was 27 → 31.48), p2H normal 88.66 (per `knowledge_base/diseases/pots.yaml` G-P0-04 reconciliation comments); dead inline `phenotypes:` blocks removed; Fox 220−age replaced by Tanaka 208−0.7·age (E5); load-time consistency guard added.
- **Where:** commits `1b1b86a` (engine side), `ae43fb4` ("G-P0-04 KB reconciliation (hyperadrenergic normals), guard promotion, wearables governance metadata, gate artifact_models support, AI reviews recorded").
- **Residual status:** none known at gate level; L1 `1.4_identifiability` confirms all 36 ODE parameters carry E-level governance metadata (PASS).

### G-P0-05 — No structured HRV — REMEDIATED
- **What changed:** new `simulation/hrv.py` — IPFM beat generator with RSA tracking respiration, Mayer-wave 0.1 Hz component, 1/f fractal structure (DFA-α1 ≈ 1 healthy), Bernoulli ectopy with phase reset. LF/HF is explicitly **never** emitted as a sympathovagal index (binding warnings in `simulation/hrv.py`; confirmed by W3-A).
- **Where:** commit `83ef84d` ("G-P0-05: structured HRV beat generation (IPFM + RSA + Mayer + 1/f + ectopy)"), seam fix `efcffb7`, re-baseline `805db2a`; tests `tests/test_hrv.py`.
- **Evidence anchors (gate-measured):** L2 `2.2_dfa_alpha1` = 1.1758 (band 0.8–1.2; Task-Force-1996 5-min record, n=594 beats) PASS; L2 `2.2_rsa_peak` — HF peak 0.29346 Hz vs respiration 0.29322 Hz PASS; L4 `4_resting_hrv_norms` — RMSSD median 56.02 ms (band 19–60) PASS.
- **Residual status:** DFA-α1 sits 0.024 below the upper band edge (1.1758 vs 1.2) — a thin margin carried as W5 residual risk (see §7 and `SCIENTIFIC_DEBT_REGISTER.md`).

### G-P0-06 — No circadian/sleep coupling — REMEDIATED
- **What changed:** 24-h wall-time + day-index time semantics; cosinor circadian autonomic modulation; sleep/wake state machine; multi-day support with OU baseline drift; circadian/sleep outputs coupled into model parameters.
- **Where:** commit `1b1b86a`; `simulation/time_engine.py`; tests `tests/test_circadian.py`; W5 respiration-process fix `8e59250`.
- **Evidence anchors (gate-measured):** L2 `2.2_circadian_amplitude` = 13.88 bpm (band 11–16, EVD-HLTH-003 cosinor anchor ~13.5; acrophase 9.29 h, mesor 57.01 bpm, 2 days) PASS.
- **Residual status:** none known at gate level.

### G-P0-07 — No dataset-generation infrastructure — REMEDIATED
- **What changed:** full `dataset/` package: seeded cohort builder (hierarchy `dataset_seed → subject_seed → channel seeds`, SHA-256 mixing), record schema with fail-closed validation hooks (schema + provenance + scientific contract incl. latent-boundary guard), manifest with `kb_bundle_sha256`, Nadler-1962 body-size blood-volume scaling, fitness/BMI trait sampling, protocol scheduler with mandatory per-record protocol covariates.
- **Where:** commits `4290864` + merge `72f0fff` (W2-F), hardening `ef80d4d`/`8c41cbc` (W4-2); generator `examples/generate_pilot_dataset.py`; schema doc `docs/dataset_schema.md`; tests `tests/test_dataset_generation.py`.
- **Evidence anchors (gate-measured):** L1 `schema_provenance_contract_hooks` PASS (2/2 records, no errors); L1 `1.5_record_determinism` PASS (same dataset_seed → byte-identical record.yaml/derived.json).
- **Residual status:** pilot-scale only (n=3 per condition shipped); see §6.

### G-P0-08 — Canonical/experimental policy — REMEDIATED
- **What changed:** explicit `canonical_status: canonical|experimental` schema on KB blocks; generation-mode gate fail-closed in canonical mode; experimental mode requires explicit opt-in; tier-D parameters engine-inert in canonical mode; sensor governance audit refuses unregistered experimental blocks and flags per-block dispositions (W4-2 `dataset/sensor_governance.py`, closing adversarial finding F8).
- **Where:** commits `0ea4e8b` (G-P0-08/G-P0-10 governance), `aeb4cbf` (merge W1-B), `ef80d4d` (sensor governance).
- **Evidence anchors (gate-measured):** L1 `1.6_honesty_gating` PASS — tier-D inert in canonical mode (experimental phenotype autoimmune_neuropathy inert), perturbations tagged, and the provenance gate **refused** a hash-tampered KB file.
- **Residual status:** none known at gate level.

### G-P0-09 — Healthy orthostatic reference not frozen/protocol-conditioned — REMEDIATED
- **What changed:** one canonical metric semantics everywhere — `sustained_delta_HR = mean(HR, minutes 5–10 of tilt) − mean(HR, final 5 min supine)`, with the initial transient (first 30 s) recorded separately and never conflated; frozen protocol-conditioned healthy reference in `docs/orthostatic_reference.md` + `validation/healthy_reference.yaml` (FROZEN, version 1.0.0): casual stand N(+12,5) with <5% ≥30 bpm; lab stand +25±3; HUT 60–70° 10-min +34±3 with ~40–60% ≥30 bpm; HUT 30-min +40±4 with ~80% ≥30 bpm; NASA lean +34±8 with 33% ≥30 bpm (tail fraction binding, not the Gaussian moments). Tails preserved as ranges. Evaluator compares only protocol-matched windows; the 100-s bench protocol is `not_applicable` and falls back to an explicitly flagged `short_protocol_proxy`.
- **Where:** commit `7d0be96`; `validation/evaluator.py::compute_orthostatic_metrics` (shared by the validation suite); `knowledge_base/interventions/tilt_test.yaml` metadata.
- **Evidence anchors:** EVD-HLTH-004 (Plash 2013, PMC3478101), EVD-POTS-001/005/018; CONTRADICTION_AUDIT Target 1.
- **Residual status:** the frozen human-readable doc still quotes the cycle-3 hyperadrenergic ΔSBP value (−4.0 mmHg) where the current engine produces +3.12 mmHg beatwise — documentary drift, flagged (§8, inconsistency I-1).

### G-P0-10 — Evidence-scale harmonization — REMEDIATED
- **What changed:** repo tiers A–D mapped onto E0–E5; every parameter carries `evidence_tier`, `source_claim_ids`, `uncertainty`, `provenance`, `canonical_status`; `validation/provenance_gate.py` refuses KB files missing review, STALE per review_tracker, missing tier/provenance, or experimental-in-canonical; unrecognized tier scales fail closed to EXPERIMENTAL; review sidecars with AI-agent reviews recorded and human-L3 absence surfaced as WARNING (never silent pass).
- **Where:** commits `0ea4e8b`, `ae43fb4`, `abb1440`; `tools/review_tracker.py`, `tools/validate_kb.py`; ADR `docs/adr/0001-sidecar-yaml-review-validation-tracking.md`.
- **Evidence anchors (gate-measured):** L1 `1.7_scale_harmonization` PASS (all tiers standard, unknown scale fails closed); L1 `1.6_honesty_gating` PASS (tamper refused).
- **Residual status:** human (L3) review is **absent for every KB file** — 23 standing warnings on the pilot manifest; governance debt carried in `SCIENTIFIC_DEBT_REGISTER.md` (adversarial finding F12 only partially resolved).

---

## 3. Validation framework and full gate results

Framework: levels L1–L5 per `docs/evidence_package/SYNTHETIC_TO_REAL_BENCHMARK.md` (status discipline: no utility claim until the Level-5 matrix has been executed and reported, including failures; any NC failure invalidates a release regardless of Level-5 performance). Runnable gates L1–L4 + negative controls implemented in `validation/levels/` (W3-V, commit `e752ea6`). **L5 NOT EXECUTED — the benchmark matrix does not exist.**

Latest gate tally (post-W5, `--fast` mode, n=2 per group): **19 pass / 1 fail / 2 unresolved / 2 disclosed_limitation** (`validation/release_gates.yaml: summary`; reproduced in `docs/validation_report.md`). A full-mode (n=4 per group) re-run was in progress at the time of writing to determine whether the single FAIL is a small-n artifact; its result is **unresolved** at this writing.

### Full gate table (every gate, every status; values verbatim from `validation/release_gates.yaml`)

| Level | Check | Target (abridged) | Measured | Status |
|---|---|---|---|---|
| L1 | 1.5_determinism | same seed → bit-identical engine output | mismatches: {} (keys Hc, Vau, pau, rr_intervals_ms, time) | **PASS** |
| L1 | 1.2_volume_conservation | stressed-volume drift < 1e-6·TotalVol over full tilt | max drift 0.0 mL over 15,192 steps; unstressed offset 3097.42 mL constant | **PASS** |
| L1 | kernel_restoration_ralpm | meal plateau = baseline ×0.75; exact restore | 17.88 → 13.41 → 17.88; restored_exactly | **PASS** |
| L1 | kernel_restoration_es | exercise plateau = baseline ×1.3; exact restore | 3.0 → 3.9 → 3.0; restored_exactly | **PASS** |
| L1 | 1.4_identifiability | all ODE params E-tagged; ±20% kH below PPG LoA → non_identifiable | 36 params, 0 missing E-level; ΔHR −1.91 bpm vs LoA ±7 bpm → non_identifiable | **PASS** |
| L1 | 1.6_honesty_gating | tier-D inert; tampered KB refused | experimental_inert true; tamper_refused true | **PASS** |
| L1 | 1.7_scale_harmonization | KB tiers map to E0–E5; unknown tier fail-closed | all_tiers_standard; unknown_scale_fails_closed | **PASS** |
| L1 | schema_provenance_contract_hooks | schema+provenance+contract hooks pass all records | n_records 2, errors [] | **PASS** |
| L1 | 1.5_record_determinism | same dataset_seed → byte-identical records | identical: true (hut60_short) | **PASS** |
| L2 | 2.1_tilt_trajectory_battery | baseline 55–75; sustained proxy +15..+40; transient 3–35; recovery ±10 @45 s | 59.30 / +24.11 / +19.88 / +0.79 bpm — all four phases pass; supine HR std 1.05 bpm | **PASS** |
| L2 | 2.1_meal_response | postprandial ΔHR in (2, 15) bpm | +2.37 bpm (time_scale 0.03, magnitudes untouched) | **PASS** |
| L2 | 2.1_exercise_response | bout ΔHR in (5, 70); recovery < plateau | bout +46.58 bpm; late recovery +30.97 bpm; p2H reset ×1.1036 open-loop + latent offsets | **PASS** |
| L2 | 2.2_dfa_alpha1 | DFA-α1 (4–16 beats) in (0.8, 1.2) | 1.1758 (594 beats, 600 s record) | **PASS** |
| L2 | 2.2_rsa_peak | \|f_peak − f_resp\| ≤ 0.05 Hz | 0.29346 vs 0.29322 Hz; LF/HF 4.32 reported (not a sympathovagal index) | **PASS** |
| L2 | 2.2_circadian_amplitude | amplitude in (11, 16) bpm | 13.88 bpm; mesor 57.01; acrophase 9.29 h | **PASS** |
| L3 | 3.1_healthy_hut_distribution | mean 34±tol AND ≥30 bpm fraction in [0.40, 0.60] | mean 38.23 bpm (within reference); fraction 1.00, 95% CI [0.16, 1.00]; n=2 < 8 → tail not resolvable | **UNRESOLVED** |
| L3 | 3.1_hypovolemic_pots_rate | ≥30 bpm rate ≥ 0.5 AND ascertainment-matched contrast +19.88 in CI [15.24, 24.52] | rate 1.0 (CI [0.16,1.00]); stratum n=2/2; contrast +14.83 vs floor 15.24 | **FAIL** |
| L3 | 3.1_hyperadrenergic_dsbp_limitation | evaluator surfaces ΔSBP pressor-criterion failure as disclosed limitation | ΔSBP +3.12 mmHg beatwise (criterion ≥ +10); limitation_surfaced true | **DISCLOSED_LIMITATION** |
| L4 | 4_prcp_orthostatic_wasserstein | W(sim, PRCP real) ≤ 3.0 bpm — reclassified protocol-mismatched | W = 17.14 bpm; 11 real episodes (slow-ramp ~3-min hold) vs sim licensed 10-min 70° HUT (Plash min 5–10 anchor) | **DISCLOSED_LIMITATION** |
| L4 | 4_eurobavar_reflex_gain | EUROBAVAR supine→standing reflex gain | URLError: SSL CERTIFICATE_VERIFY_FAILED (self-signed certificate) | **UNRESOLVED** |
| L4 | 4_resting_hrv_norms | RMSSD median in (19, 60) ms | median 56.02 ms (47.89, 64.15); SDNN median 90.59 ms; n=2 | **PASS** |
| NC | NC_parity_nuisance_channels | no group-conditional nuisance channels | 9 channel classes checked; mismatches {} | **PASS** |
| NC | NC2_trivial_separability_auc | LOOCV logistic AUC < 0.95 (honest band 0.75–0.85 reported) | AUC 0.5 full features; 0.5 resting-only; n=2+2, 7 features | **PASS** |
| NC | NC_demographics_disclosure | demographic differences evidence-based + disclosed | healthy age 36.2, female 0.5; POTS age 23.0, female 1.0 (EVD-POP-006) | **PASS** |

### The single FAIL, precisely stated

L3 `3.1_hypovolemic_pots_rate`: the gate was re-specified in W5 (commit `839cc18`) so that the full-mixture patient-minus-control contrast is **informational** (severity mixture overlaps the healthy high-normal tail by construction — anti-trivial-separability pilot design) and the gate evaluates the **ascertainment-matched stratum**: simulated subjects meeting the ≥30 bpm 10-min HUT diagnostic criterion that defines the EVD-POTS-011 meta-analytic cohort (+19.88 bpm, 95% CI [15.24, 24.52]; 20 studies, 717 POTS / 641 controls). At validation-cohort n=2 per group the measured stratum contrast is **+14.83 bpm**, 0.41 bpm below the CI floor of 15.24. The shortfall is driven by the n=2 healthy control mean of 38.23 bpm (reference 34±3). **The phenotype was deliberately NOT tuned to pass**; the gate is INTENTIONALLY LEFT FAIL at small n pending the full-mode (n=4) re-run with unchanged methodology.

### W5 gate-remediation changes (what moved between pre-W5 and this tally)

- **Exercise autonomic drive** (commit `6791fbe`): bout HR rise now driven by an intensity-scaled cardiovagal p2H operating-point reset of baroreflex form (EVD-AUTN-008 / REL-BAROREFLEX-RESETTING), magnitude **derived open-loop** from the cited HR-reserve relation (EVD-HLTH-005), plus latent vagal-withdrawal/sympathetic offsets; measured closed-loop values reported, never tuned. L2 exercise gate PASS (+46.58 bpm bout).
- **Respiration category error** (commit `8e59250`): stage-conditioned respiration-rate distributions (awake N(15.5, 2.3)) are between-subject/occasion spreads but were resampled i.i.d. every heartbeat, causing RSA phase diffusion; fixed to occasion-mean + within-subject breath-to-breath jitter (sd 0.5 brpm). Before the fix the L2 RSA gate locked onto the engine's residual ~0.17 Hz mean-HR rhythm at 0.165 Hz instead of the respiration frequency (documented in `simulation/time_engine.py`).
- **DFA window standardization** (commit `8e59250`): DFA/RSA gates moved to the Task-Force-1996 5-min short-term standard record (600 s, 594 beats).
- **PRCP gate reclassification** (commit `50eb615`): the PRCP comparison is protocol-mismatched (real slow-ramp tilt ~3-min hold vs licensed 10-min 70° HUT Plash anchor). Closing the gap would require de-calibrating the Plash-anchored sustained response — forbidden tuning (W4-1 calibration-conflict analysis). Reclassified **disclosed_limitation**; raw numbers stay visible (W = 17.14 bpm); protocol-matched slow-ramp simulation mode logged as scientific debt.
- **L3 contrast gate re-specification** (commit `839cc18`): ascertainment-matched stratum semantics with truncation caveat disclosed (above).

---

## 4. Adversarial-review disposition summary

The W3-A adversarial review (`ADVERSARIAL_REVIEW_REPORT.md`, branch @ `efcffb7`, 231 tests passing at that time) found **2 CRITICAL + 8 MAJOR release-blocking findings** (F1–F13 numbering) plus minors, across 10 attack classes. All release-blocking findings were dispositioned in waves W4/W5:

- **F1 (CRITICAL, sex-confounded pilot → metadata AUC 1.0):** FIXED — demographic matching/stratified cohort sampling + a mandatory metadata negative control (sex/age/BMI/fitness/device classifier must sit at AUC ≤ 0.5+ε); pilot manifest: multivariate AUC 0.5, passed (commits `ef80d4d`/`8c41cbc`).
- **F4/F6 (CRITICAL, recorded commit predates the generator → broken provenance, stale pilot):** FIXED — pilot regenerated post-merge at commit `8c41cbc` with structured HRV active (`hrv_source: simulation.hrv.generate_rr_series`, `import_error: null`; per-record RMSSD resolved).
- **F2 (MAJOR, BMI/fitness/TotalVol homogeneity):** FIXED — BMI/fitness/height now sampled (pilot BMI range 23.9–29.0; Nadler-1962 body-size blood-volume scaling → heterogeneous volumes).
- **F3/F11 (MAJOR, beat-count separability; ln-RMSSD trait decoupled):** FIXED — two-pass trait calibration wires sampled HRV traits into the IPFM generator (`dataset/rr_source.py`; flags `hrv_trait_amplitude_gain_machine_calibrated` honestly disclosed per record).
- **F5/F13 (MAJOR, kb_version non-reproducible + incomplete):** FIXED — deterministic closure sidecars; externally consumed wearable/artifact files hashed under `external:` labels (`kb_version_semantics` in the manifest).
- **F8 (MAJOR, experimental parameter blocks inside canonical devices ungated):** FIXED — `dataset/sensor_governance.py` per-block audit; pilot manifest shows all 11 experimental blocks either neutral no-ops or excluded by channel selection, each flagged.
- **F7 (MAJOR, tilt transient 43–47 bpm vs 20–30 reference):** FIXED by W4-1 limit-cycle stabilization — post-fix transient 19.4–19.5 bpm; gate L2.1 transient phase now 19.88 bpm within band.
- **F9 (MAJOR, supine DFA-α1 1.35–1.61, SDNN 166–193 ms):** FIXED by W4-1 — DFA-α1 1.52→0.984 at the time of the fix; current 5-min-window gate 1.1758 (in band, thin margin); L4 RMSSD median 56.02 ms in band.
- **F10 (MAJOR, metronomic RMSSD 4.0 ms shipped):** FIXED — structured-HRV pilot; no null/metronomic RMSSD in shipped records.
- **F12 (MAJOR, self-review satisfies the provenance gate):** **PARTIALLY RESOLVED** — human-L3 absence is surfaced as 23 standing warnings in the pilot manifest and gate, but `validation/provenance_gate.py` still treats it as WARNING-only ("never a hard failure while human review is pending"); the W3-A recommendation to escalate to failure for release builds is **not implemented**. Carried as governance debt.
- **F7-companion minors:** `generation_timestamp` remains a seed-derived constant whose value (2026-08-23) predates the generating commits — still named `generation_timestamp` (the suggested rename to `build_clock` was not applied); documented in the manifest's `kb_version_semantics`/provenance block context. MINOR, open.

Full finding-by-finding table with resolution commits: `ADVERSARIAL_REVIEW_REPORT.md` → *Addendum — Remediation Wave W4/W5 Disposition*.

---

## 5. Pilot dataset results (`results/ocpe_pilot_v1`)

Human-readable rendering: `OCPE_PILOT_DATASET_MANIFEST.md`. Key numbers (verbatim from `manifest.yaml` / `manifest_summary.txt`):

- **Dataset:** `ocpe_pilot_v1` v0.1.0, schema 0.1.0, canonical mode, 6 records (3 healthy + 3 hypovolemic-POTS), single protocol `hut60_bench_v1` (310 s: 150 s supine + 100 s 60° tilt + 60 s recovery, ramp 14 s, fasting, morning), single sensor `polar_h10` (RR channel only).
- **Provenance:** `ocpe_commit: 8c41cbc4c397720bd9482e2ddcc5dae393387bb5`; `kb_version` (bundle sha256) `3b3e16c79f495b5d…`; `registry_version: sha:e37f63477527`; `model_version: mathematical_models-1.0`; `dataset_seed: 20260601` with per-subject seeds recorded.
- **Group separation (sustained ΔHR, short-protocol proxy):** healthy n=3 mean 28.93 ± 5.32 bpm [24.92, 34.96]; POTS n=3 mean 27.28 ± 11.29 bpm [17.96, 39.84]. **The group ranges overlap on [24.9, 35.0] bpm BY DESIGN** (severity mixture, anti-trivial-separability). Between-condition separation comes from mechanism only (volume deficit, pooling axis, baroreflex); no label conditioning of signals.
- **Anti-laundering:** metadata negative control (sex/age/BMI/fitness/device) multivariate AUC **0.5** — passed (ε=0.1). Per-record validation: schema + provenance + scientific-contract hooks passed on all 6 records (fail-closed build).
- **Honesty disclosures shipped in the manifest:** 23 provenance warnings (human L3 review absent on all KB files); per-record honesty flags including `rhr_calibration_mismatch_beyond_tolerance` (on POTS records and healthy-003), `severity_resampled_from_evidence_distribution` (POTS), `short_protocol_sustained_window_proxy` (all records — the 100-s bench protocol cannot reach the licensed minutes 5–10 window), pooling-capacity tier-C machine-fit flags, and the sensor-governance flag set.

---

## 6. Anti-laundering posture

- **AUC cap:** disease-classification AUC > 0.95 = release failure, regardless of cause (`SWARM_SPEC.md` rule 5; benchmark NC2). Gate NC2 measured 0.5 at n=2+2 (underpowered; the honest band 0.75–0.85 is reported as the *expected* realistic band from the dataset specification, not achieved/measured at this n).
- **Metadata negative control:** metadata-only classifier must be ≤ 0.5+ε; pilot measured 0.5 multivariate and per-feature. Enforced upstream by matched/stratified sampling, never by label manipulation.
- **Latent boundary:** no latent physiology (BP, SV, CO, SVR, venous pooling, cerebral perfusion, core temp, hydration, glucose-except-CGM, BRS) may appear as a sensor channel; static guard test + schema contract hook enforce this; W3-A verified zero latent leakage in shipped `sensors.npz`/`derived.json` (latents live only in `ground_truth.npz`, labeled ground truth only).
- **Nuisance parity:** 9 nuisance-channel classes (device profile, sampling, noise, missingness, record length, seed policy, …) checked group-conditional — mismatches {} (gate NC).
- **Group overlap by design:** severity-mixture construction makes mild hypovolemic deficits overlap the healthy high-normal tail; trivial separability would itself be a release failure.
- **No utility claims:** the binding governing sentence is carried on the gate record, the validation report, and this document.

---

## 7. Honest limitations (summary — full register in `SCIENTIFIC_DEBT_REGISTER.md`)

1. **Single FAIL open:** L3 POTS–healthy ascertainment-matched contrast +14.83 vs CI floor 15.24 bpm at n=2 per group; phenotype deliberately not tuned; full-mode (n=4) re-run pending at this writing (**unresolved**).
2. **Two disclosed_limitation gates:** hyperadrenergic ΔSBP pressor criterion unmet (0-D windkessel; +3.12 mmHg vs ≥ +10); PRCP protocol mismatch (W = 17.14 bpm; slow-ramp sim mode is scientific debt).
3. **Two unresolved gates:** L3 healthy-HUT ≥30 bpm tail unresolvable at n=2 (CI [0.16, 1.00]); EUROBAVAR fetch blocked by self-signed SSL certificate (infrastructure, not science).
4. **Two strict-xfails (model-structure gaps):** neuropathic POTS sustained criterion (21.2 vs ≥30 bpm, flat dose-response); hyperadrenergic ΔSBP (G-P1-01). Both carry written scientific justifications.
5. **Human L3 review absent** on all KB files (23 warnings); the provenance gate is warning-only here and partially self-certifying (F12 partially resolved).
6. **L5 benchmark does not exist** — no utility claim of any kind is licensed.
7. **Thin gate margins / residual risks (W5):** DFA-α1 1.1758 vs 1.2 band edge; RSA argmax can lock onto the engine's residual ~0.17 Hz mean-HR rhythm (~1 bpm std post-W4-1) under low-RSA-amplitude draws.
8. **Single-source backbone:** the core ODE is Geddes-2022 in-silico (tier-C), with the competing Fu-2010 branch specified but not implemented (G-P1-04).
9. **Test suite:** program tally 295 passed / 1 skipped / 2 xfailed (reported by the engineering swarm post-W5; **not re-executed by this writer** — pytest is unavailable in the deliverable-writing environment; the tally is marked as reported-not-verified).

---

## 8. Inconsistencies discovered between sources (documentary; none gate-blocking)

- **I-1.** `docs/orthostatic_reference.md` §5 (FROZEN, W1-C) states the hyperadrenergic simulated ΔSBP as **−4.0 mmHg**; the current gate measures **+3.12 mmHg beatwise** (the gate note itself records the cycle-3 value as −4.0). The frozen doc predates the W4-1 dynamics change and was not re-based. Direction of the disclosure unchanged (criterion still unmet); numeric drift should be re-based.
- **I-2.** The Phase-2 program summary cited a circadian gate amplitude of **13.50 bpm**; the gate record measures **13.88 bpm** (band 11–16; the evidence anchor is *~13.5*). The pass is unaffected; the measured value is 13.88.
- **I-3.** The pilot manifest enforces demographic matching (both cohorts female_fraction 0.667, age range identical 22.4–40.5 — the F1 fix), while the release-gate NC demographics check at n=2 shows POTS female_fraction 1.0 vs healthy 0.5 with the note "demographics differ BY EVIDENCE." These are different cohorts (pilot vs gate validation cohort) with different matching policies; not contradictory, but a consumer should not assume the gate cohort is demographically matched.
- **I-4.** `generation_timestamp: 2026-08-23` in the pilot manifest is a seed-derived deterministic constant whose calendar value predates the generating commits (2026-09). W3-A flagged this MINOR and suggested renaming to `build_clock`; the rename was not applied.

---

## 9. Conditions under which a real dataset release would be justified

Per the governing benchmark document, a release is justified only when **all** of the following hold:

1. **L3 contrast gate passes at adequate Monte-Carlo size** — the full-mode (n=4 or larger) re-run brings the ascertainment-matched POTS–healthy contrast within the EVD-POTS-011 CI [15.24, 24.52] **with unchanged methodology and an untuned phenotype** (or the gate is formally re-specified again with disclosed justification — a second re-specification would itself require review).
2. **Healthy-tail resolvability:** validation-cohort n ≥ 8 per group so the L3 healthy ≥30 bpm tail band [0.40, 0.60] is statistically resolvable.
3. **All L1–L4 gates pass or carry only disclosed_limitation/unresolved-for-infrastructure statuses**, with disclosed limitations carried onto every released record.
4. **Negative controls pass on the release-scale build** (NC, NC2 AUC < 0.95, metadata control ≤ 0.5+ε) at the release n, not only at pilot n.
5. **Level-5 synthetic-to-real benchmark matrix exists, is pre-registered, and is executed and reported including failures** (`SYNTHETIC_TO_REAL_BENCHMARK.md` §5). Until then the binding sentence stands: *OCPE synthetic data are candidate research artifacts whose utility for any task is unestablished pending the Level-5 benchmark.*
6. **Human (L3) review completed** across KB files, or the human-L3 absence formally accepted as a release risk by program governance (currently a warning-only state — F12).
7. **Disclosed limitations resolved or explicitly accepted:** hyperadrenergic ΔSBP structure (G-P1-01), neuropathic sustained criterion (G-P0-03), PRCP protocol-matched slow-ramp sim mode, EUROBAVAR access.

**Current position against these conditions:** conditions 3 (mostly), 4 (at pilot n) are met; conditions 1, 2, 5, 6, 7 are **not met**. The release decision is recorded in `RELEASE_DECISION.md`.
