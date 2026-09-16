# OCPE — Release Decision (Phase 2, dataset-readiness program)

<!-- VERDICT-SPOT -->
RELEASE DECISION: NOT DATASET-READY

**Date of decision basis:** post-W5 gate record `validation/release_gates.yaml` (started 2026-09-16T09:55:45, gate seed 20260915, context commit `7651fa73211700f73416933ac6dc930cfe2b29d7`), branch `swarm/dataset-readiness` HEAD `e8829bf`.
**Deciding rule:** the program's own release conditions (`SYNTHETIC_TO_REAL_BENCHMARK.md` status discipline; `SWARM_SPEC.md` global rules; Phase-1 capstone P0 criterion). Any unresolved release-blocking gate forces NOT DATASET-READY; no utility claim is licensed at any point short of an executed Level-5 benchmark.
**Governing sentence (binding, carried on all artifacts):** *OCPE synthetic data are candidate research artifacts whose utility for any task is unestablished pending the Level-5 benchmark.* Level-5 status: **NOT EXECUTED — the benchmark matrix does not exist.**

---

## 1. Gate evidence summary

Post-W5 release-gate re-run (`--fast` mode; licensed validation cohort n=2 healthy + n=2 hypovolemic-POTS; 10-min HUT protocol for L3):

| Status | Count | Gates |
|---|---|---|
| PASS | 19 | All L1 (determinism ×2, volume conservation, kernel restoration ×2, identifiability, honesty gating, scale harmonization, schema/provenance hooks); all L2 (tilt trajectory battery, meal, exercise, DFA-α1, RSA peak, circadian amplitude); L4 resting-HRV norms; all 3 negative controls (nuisance parity, NC2 separability AUC 0.5, demographics disclosure) |
| FAIL | 1 | L3 `3.1_hypovolemic_pots_rate` — see §2 |
| UNRESOLVED | 2 | L3 healthy-HUT ≥30 bpm tail (n=2 < 8; CI [0.16, 1.00]; mean check passes); L4 EUROBAVAR (self-signed SSL — infrastructure) |
| DISCLOSED_LIMITATION | 2 | L3 hyperadrenergic ΔSBP (+3.12 mmHg beatwise vs ≥ +10 criterion; 0-D windkessel); L4 PRCP Wasserstein (17.14 bpm; protocol mismatch — slow-ramp ~3-min hold vs licensed 10-min 70° HUT) |

Test suite (program tally reported by the engineering swarm; not re-executed by this writer): 295 passed / 1 skipped / 2 xfailed — the two xfails are the documented model-structure limitations (neuropathic POTS sustained criterion; hyperadrenergic ΔSBP pressor criterion), each with a written scientific justification.

All 10 Phase-1 P0 gaps are remediated or formally scoped (evidence: `OCPE_DATASET_READINESS_REPORT.md`, `IMPLEMENTATION_TRACEABILITY_MATRIX.md`). All W3-A adversarial release-blocking findings are resolved except F12 (partially — human-L3 review absent, warning-only) and the small-n statistics now concentrated in the single FAIL.

## 2. Blocking issue (single)

**B-1 — L3 POTS–healthy contrast below meta-analytic CI floor at validation-cohort n=2 per group (+14.83 vs 15.24 bpm; ascertainment-matched stratum semantics; phenotype deliberately not tuned).**

Precise statement: gate L3 `3.1_hypovolemic_pots_rate` evaluates the ascertainment-matched stratum — simulated subjects meeting the ≥30 bpm 10-min HUT diagnostic criterion that defines cohort membership in the E4 meta-analytic anchor EVD-POTS-011 (+19.88 bpm, 95% CI [15.24, 24.52]; 20 studies, 717 POTS / 641 controls). Measured stratum contrast at n=2 per group: **+14.83 bpm**, 0.41 bpm below the CI floor. The shortfall is driven by the n=2 healthy control mean of 38.23 bpm against the frozen reference 34±3 bpm. The full-mixture contrast (also +14.83 bpm at this n) is informational by the W5 gate re-specification (`839cc18`): the severity mixture overlaps the healthy high-normal tail by construction. The gate is INTENTIONALLY LEFT FAIL; no phenotype parameter was adjusted to pass it. This is plausibly a small-n artifact, but that is unproven until the full-mode re-run completes.

**Reversal condition (explicit):** a full-mode (n=4 per group) gate re-run is in progress at the time of writing. **If that re-run passes this gate with unchanged methodology — same frozen reference, same ascertainment-matched stratum semantics, same untuned phenotype, same seeds policy — and no other gate regresses, this decision reverses to DATASET-READY**, with the disclosed limitations in §3 carried onto the release. If the gate still fails at n=4, the failure is no longer attributable to Monte-Carlo size, and remediation must target the severity-mixture calibration (not the point phenotype) under a documented gate re-specification review before any release.

## 3. Disclosed limitations (carried, not blocking)

1. **Hyperadrenergic ΔSBP pressor criterion unmet** (+3.12 mmHg beatwise vs ≥ +10 mmHg, Okamoto 2024 tier A): 0-D windkessel structure narrows pulse pressure on tilt; MAP surrogate (~+5 mmHg) is not the clinical criterion. Surfaced as DISCLOSED_LIMITATION on every evaluation; strict-xfail pinned (G-P1-01).
2. **PRCP L4 comparison protocol-mismatched** (W = 17.14 bpm): real slow-ramp ~3-min holds vs simulated licensed 10-min 70° HUT anchored to Plash 2013 minutes 5–10; closing the gap would require de-calibrating the frozen healthy anchor (forbidden tuning). Protocol-matched slow-ramp simulation mode is registered scientific debt.
3. **Neuropathic POTS excluded from canonical generation** (model-structure gap: 21.2 vs ≥30 bpm, flat dose-response; strict-xfail with justification; canonical builds refuse it — verified by adversarial probe).
4. **Human (L3) review absent on all KB files** (23 standing warnings; provenance gate warning-only; adversarial finding F12 partially resolved). Any release under the reversed decision must either complete human L3 review or have this risk formally accepted by program governance.
5. **Level-5 benchmark does not exist.** Even under a reversed (DATASET-READY) decision, readiness means *engineering and gate readiness of the generation pipeline and pilot*, not utility: the binding sentence remains mandatory on every artifact until the L5 matrix exists, is pre-registered, and is executed and reported including failures.
6. **EUROBAVAR reflex-gain comparison never executed** (self-signed SSL); external baroreflex-gain realism unverified.
7. **Healthy ≥30 bpm HUT tail unverified at n=2** (CI [0.16, 1.00] vs band [0.40, 0.60]); requires n ≥ 8 per group — bundled with the B-1 re-run.
8. **Residual technical risks:** DFA-α1 0.024 below the band edge; RSA argmax vs residual ~0.17 Hz engine rhythm under low-amplitude draws; RHR calibration beyond tolerance flagged on POTS records; beat-count separability documented, unpadded.

## 4. Conditions for reversal (complete list)

This decision reverses to `RELEASE DECISION: DATASET-READY` when **all** of the following hold:

1. The full-mode (n=4 per group, or larger) gate re-run passes L3 `3.1_hypovolemic_pots_rate` under unchanged methodology, with the full gate tally showing 0 FAIL and no new unresolved/disclosed items beyond those listed in §3. *(Reversal of the verdict line is performed by patching this document at the marked spot above.)*
2. The re-run record (updated `validation/release_gates.yaml` + `docs/validation_report.md`) is committed and cites its context commit and cohort size.
3. The disclosed limitations in §3 are reproduced verbatim in the release notes of any shipped dataset.

Independently of this decision line, the following remain necessary before any *real* (non-pilot) dataset release: healthy-tail resolvability at n ≥ 8 (condition met by the same re-run if it resolves), negative controls re-verified at release n, human-L3 review completed or formally risk-accepted, and — for any utility claim whatsoever — an executed Level-5 synthetic-to-real benchmark. DATASET-READY under this document means: the pipeline and pilot satisfy the program's L1–L4 + negative-control gate discipline with all limitations disclosed. It does **not** assert synthetic-data utility for any task.

## 5. Anti-laundering attestation

- No gate was passed by tuning a phenotype to a target: the single FAIL is left failing; the PRCP gate was reclassified rather than de-calibrating the frozen anchor; the NC2 AUC (0.5 at n=2+2) is reported, never adjusted.
- Disease-classification AUC > 0.95 remains a release-failure condition; metadata-only classification at AUC ≤ 0.5+ε is enforced by construction (matched sampling) and measured on the shipped pilot (0.5).
- Latent physiology has never been emitted as a sensor channel (schema contract + static guard + adversarial probe).
- Every number in this document was read from the cited files; anything not yet measured is marked unresolved.
