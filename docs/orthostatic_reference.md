# OCPE Orthostatic Reference — FROZEN protocol-conditioned healthy reference (G-P0-09)

Status: **FROZEN** by Agent W1-C (`fix/orthostatic-reference`). Machine-readable twin:
`validation/healthy_reference.yaml`. Binding implementation:
`validation/evaluator.py::compute_orthostatic_metrics`.
Gap register: `docs/evidence_package/OCPE_RESEARCH_GAP_ANALYSIS.md` G-P0-09.
Evidence: `docs/evidence_package/EVENT_PROTOCOLS.yaml`, `CONTRADICTION_AUDIT.md` Target 1,
`HEALTHY_PHYSIOLOGY_EVIDENCE.md` §3, `EVIDENCE_REGISTRY.yaml` claims EVD-HLTH-004,
EVD-POTS-001, EVD-POTS-005, EVD-POTS-018.

## 1. Canonical metric semantics (ONE definition, used everywhere)

```
sustained_delta_HR = mean(HR, minutes 5–10 of tilt) − mean(HR, final 5 min supine)
initial_transient  = max(HR, first 30 s post-onset) − mean(HR, final 5 min supine)
```

- The **initial transient** (seconds: vagal withdrawal + muscle-pump exercise reflex) and the
  **sustained response** (minutes: baroreflex steady state) are different physiological phases
  (HEALTHY §3.1, E3). They are recorded separately and **never conflated** into one ΔHR number.
- The pre-freeze evaluator used a **peak** ΔHR over the first 60 s (inflated by the steep-Hill
  limit cycle) while acceptance tests used a **sustained** metric — two different metrics were
  gating "POTS vs healthy" (G-P0-09). The peak-only semantics is removed.
- Short simulated protocols (repo bench: 200 s supine + 100 s tilt) cannot reach minutes 5–10;
  the sustained metric falls back to the **final-40-s stabilized proxy**, explicitly flagged
  `short_protocol_proxy`. On that proxy the ≥30 bpm comparison is a continuity check, **not** a
  licensed clinical claim.

## 2. Protocol-conditioned healthy reference (tilt ≠ stand ≠ lean)

The healthy false-positive rate at the 30-bpm POTS boundary is a **protocol property**, not a
population constant (CONTRADICTION_AUDIT Target 1). Tails are preserved as ranges — do **not**
collapse to a single threshold.

| Protocol | Method / angle / duration | Healthy sustained ΔHR (min 5–10) | Fraction of healthy ≥ 30 bpm | Evidence | Source |
|---|---|---|---|---|---|
| Casual active stand | active stand (muscle pump on), 90°, 10 min, short-notice supine baseline | **N(+12, 5)** bpm, tail capped ≈ +28 | **< 5%** (point ~2%) | E3 | EVD-HLTH-004 (HEALTHY §3 impl. rec.) |
| Lab active stand (Vanderbilt) | active stand, 90°, 10 min; ≥1 h supine, fasting, morning | **+25 ± 3** bpm (23±3 @5 min, 26±3 @30 min); Seeley 2025 review median 15 [IQR 9–20] | **~10–33%** (Plash stand-10min specificity 67% → 33% FP; optimal cutoff 29 bpm) | E3 | EVD-HLTH-004, EVD-POTS-005 (Plash 2013, PMC3478101) |
| Head-up tilt, diagnostic | passive HUT 60–70°, 10 min, ≥10 min supine (lab ≥1 h), fasting, morning | **+34 ± 3** bpm (27±3 @5 min, 40±4 @30 min) | **~40–60%** (Plash tilt-10min specificity 40%; optimal cutoff ~37–38 bpm) | E3 | EVD-HLTH-004, EVD-POTS-001 (Plash 2013, PMC3478101) |
| Head-up tilt, prolonged | passive HUT 60–70°, 30 min | +40 ± 4 bpm @30 min (window min 25–30) | **~80%** (Plash **tilt-30-min specificity 20%**; optimal cutoff 47 bpm) | E3 | EVD-HLTH-004 (Plash 2013, PMC3478101) |
| NASA lean test | passive lean, 90°, 10 min (back to wall, feet 15 cm out, no muscle activity) | **+34 ± 8** bpm (moment approximation — see warning) | **33%** healthy meet >30 bpm; 49% show POTS *or* OH pattern | E2 | EVD-POTS-018 (Lee 2020, PMC7429890) |

**NASA-lean shape warning:** the +34±8 moments are frozen per SWARM_SPEC G-P0-09, but a Gaussian
with those moments does not reproduce the verified 33% tail. The **tail fraction is the binding
calibration target**, not the moment approximation.

### Initial-transient reference (recorded separately)

- Active stand: BP dip nadir ~10 s (abnormal if SBP −40 / DBP −25 mmHg, Wieling initial-OH
  criteria), recovery by 20–30 s with overshoot; HR onset ~3 s, peak +20–30 bpm at ~10–15 s. E3
  (EVD-HLTH-004, HEALTHY §3.1).
- Passive HUT: **smaller/absent** initial transient (no muscle pump) — active stand and tilt are
  **not interchangeable**. E3.

## 3. Criterion licensing

- The **≥30 bpm** POTS criterion (≥40 bpm ages 12–19; EVD-POTS-001, E5 consensus: HRS 2015,
  CCS 2020, NIH 2021) is licensed **only** for standardized 10-min active-stand or 10-min tilt
  protocols. It is a clinical threshold, **not a physiological boundary**; on prolonged tilt
  (≥20–30 min) it is largely meaningless in healthy young adults.
- Adolescents: 97.5th percentile of healthy stand/tilt ΔHR is 41–52.7 bpm; 42% of healthy
  children exceed 30 bpm on 5-min tilt — hence the pediatric ≥40 bpm criterion (E2/E3).
- Mandatory per-record protocol covariates (W2-F dataset generator): method, tilt angle,
  upright duration, supine-rest duration, fasting state, time of day, metric window.

## 4. Evaluator behavior (protocol conditioning)

- `PhysiologicalEvaluator.evaluate()` computes the canonical metrics and compares against
  `validation/healthy_reference.yaml` **only when the simulated protocol matches a reference
  entry's window** (method + angle + duration). The 100-s bench protocol matches nothing and is
  reported as `not_applicable` — no unlicensed comparison.
- `compare_distribution_to_reference(samples, protocol_id)` compares a simulated cohort on both
  central tendency **and** the ≥30-bpm tail fraction, per protocol.
- `validation/validation_suite.py` uses the same shared `compute_orthostatic_metrics`.

## 5. Disclosed phenotype scoping (G-P0-03 companions)

- **Neuropathic POTS** is formally scoped **experimental-xfail**: engine-falsified at 21.2 bpm
  sustained vs the ≥30 bpm criterion, with flat dose-response (18.5→21.7 bpm over denervation
  factor 0–0.5). Remediation paths: bounded stress-relaxation creep per van Heusden 2006 and/or
  Geddes 2022 Eq. 2.16 tilt-onset application semantics. Strict-xfail test with written
  justification: `tests/test_orthostatic_response.py::test_neuropathic_experimental_sustained_criterion`.
  Canonical dataset generation must reject neuropathic POTS (exclusion-marker interface proposed
  to W1-B's provenance gate — see pots.yaml annotation comments).
- **Hyperadrenergic POTS**: the upright **ΔSBP ≥ +10 mmHg** pressor criterion (Okamoto 2024,
  tier A) is **not met** by the 0-D model (simulated **−4.0 mmHg**; pulse pressure narrows on
  tilt as stroke volume falls; the MAP surrogate ~+5 mmHg is present but is not the clinical
  criterion). The evaluator **discloses this as a limitation** in every hyperadrenergic report
  (`report["limitations"]`, printed as `[LIMITATION]`) — it is never silently passed. Strict-xfail:
  `test_hyperadrenergic_sbp_pressor_criterion` (GAP register G-P1-01).
