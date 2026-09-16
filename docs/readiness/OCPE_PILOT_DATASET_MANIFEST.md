# OCPE Pilot Dataset Manifest — `ocpe_pilot_v1` (human-readable rendering)

**Source of truth:** `/mnt/agents/output/ocpe_repo/results/ocpe_pilot_v1/manifest.yaml` (730 lines) and `manifest_summary.txt`. Every value below is copied from those files. Companion schema doc: `docs/dataset_schema.md` (record schema v0.1.0).
**Binding sentence (from the governing benchmark, carried on this dataset):** *OCPE synthetic data are candidate research artifacts whose utility for any task is unestablished pending the Level-5 benchmark.* L5 is **NOT EXECUTED**.

## 1. Identity and provenance

| Field | Value |
|---|---|
| Dataset name / version | `ocpe_pilot_v1` / 0.1.0 |
| Schema version | 0.1.0 |
| Generation mode / canonical status | `canonical` / `canonical` |
| Generation timestamp | `2026-08-23T11:56:41+00:00` (seed-derived deterministic constant; calendar value predates the generating commits — W3-A minor, field rename to `build_clock` suggested and not applied) |
| Generating commit | `8c41cbc4c397720bd9482e2ddcc5dae393387bb5` (post-W4-2 merge; the generator and structured-HRV module exist at this commit — closes W3-A F4/F6) |
| KB bundle (`kb_version`) | sha256 `3b3e16c79f495b5db61894268ed6ca423827aee1f6f67ea30f14cae0ee3f7f46` over consumed KB data-file contents (review sidecars excluded — volatile UUID/wall-clock fields; governance freshness is gate-enforced at build time) + externally consumed wearable/artifact files hashed under `external:` labels (closes W3-A F5/F13) |
| Registry version | `sha:e37f63477527` (`docs/evidence_package/EVIDENCE_REGISTRY.yaml`, content-addressed) |
| Model version | `mathematical_models-1.0` |
| HRV source | `simulation.hrv.generate_rr_series` (W2-E IPFM); `import_error: null`; `w2e_hrv_module_available: true` |
| Spec reference | `docs/evidence_package/OCPE_DATASET_SPECIFICATION.md` v0.1; master prompt §7/§18/§21 |
| Records | 6 (all passed schema + provenance + scientific-contract hooks; fail-closed build) |

### Seeds / provenance chain

Hierarchy: `dataset_seed → subject_seed → channel seeds` (SHA-256 mixing).

| Subject | subject_seed |
|---|---|
| dataset_seed | `20260601` |
| healthy-001 | 3191279696036316925 |
| healthy-002 | 941592481323513957 |
| healthy-003 | 4305126629050427299 |
| pots_hypovolemic-001 | 4697363195449547122 |
| pots_hypovolemic-002 | 8554596375006535753 |
| pots_hypovolemic-003 | 2051306416744588553 |

## 2. Cohort design

| Cohort | n | Condition | Phenotypes | Age range | BMI range | Female fraction | Device | Frame |
|---|---|---|---|---|---|---|---|---|
| `healthy` | 3 | healthy | — | 22.4–40.5 | 23.9–29.0 | 0.667 (2/3) | polar_h10 | cohort_frame `off` |
| `pots_hypovolemic` | 3 | pots | `hypovolemic_pots` | 22.4–40.5 | 23.9–29.0 | 0.667 (2/3) | polar_h10 | cohort_frame `population`, `demographics_matched_to: healthy` |

- Demographic matching (sex/age/BMI ranges identical across cohorts) is the W4-2 fix for adversarial finding F1 (the pre-fix pilot was perfectly sex-confounded, metadata AUC 1.0). Matching is enforced by sampling, never by label manipulation.
- Mechanism-first design (rules 4/5): between-condition differences arise only from mechanism draws — blood-volume deficit resampled per subject from the evidence distribution (Raj-2005-anchored; flags `severity_resampled_from_evidence_distribution`, floor clamp documented), pooling-axis draws overlapping the healthy quantile range (575/750/950 mL healthy vs 691.1/941/662 mL POTS per `cohort.csv`), and baroreflex parameters. No disease-specific signal modification bypassing mechanism.
- Body-size scaling: expected blood volume per subject via Nadler-1962 from sampled sex/height/BMI (e.g. healthy-001 3927.7 mL expected; pots_hypovolemic-001 3884.0 mL expected with 398.5 mL deficit), flag `blood_volume_nadler_provisional_residual_cv`.
- Evidence tiers present (as recorded): E0-E1, E1, E2, E2 (direction)/E4 (magnitude, provisional), E2 (equation)/E4 (residual CV, provisional), E2/E3, E3, E4. `single_source_flags: []`.

## 3. Protocol inventory

One protocol, `hut60_bench_v1` (family `tilt_first`, total 310 s): supine_baseline 150 s → head_up_tilt 100 s at 60° → supine_recovery 60 s; ramp 14 s; covariates: fasting, morning, method head_up_tilt, supine rest 150 s, upright 100 s. No events.

**Licensing caveat (binding):** the 100-s bench tilt cannot reach the licensed minutes 5–10 sustained window; every record's derived summary is flagged `sustained_window_kind: short_protocol_proxy`. On that proxy the ≥30 bpm comparison is a continuity check, **not** a licensed clinical claim (the ≥30 bpm criterion is licensed only for standardized 10-min active-stand or 10-min tilt protocols — `validation/healthy_reference.yaml`).

## 4. Channel inventory

- One sensor: `polar_h10` (research chest strap profile, KB-driven), regime `on_device`, channels: `rr` only.
- Per record on disk (`subjects/<subject_id>/hut60_bench_v1/`): `sensors.npz` (observable channels), `ground_truth.npz` (latent physiology — ground truth only, never a sensor channel), `record.yaml` (metadata + honesty flags), `derived.json` (derived metrics + reference comparison).
- Latent boundary: enforced by the scientific-contract hook and a static guard; W3-A verified zero latent leakage in the shipped pilot (Attack 5, SYSTEM HELD). Known minor: the documented `cgm_glucose` whitelist exception is unusable (`UnknownSensorInput`).
- Sensor governance audit (canonical mode, **passed**): all 11 experimental parameter blocks registered and dispositioned — 3 consumed as neutral no-ops (KB value equals code fallback: `contact_loss.onset_prob_at_exercise_start`, `dropout.motion_loss_gain`, `ectopy.rr_error_widen_factor`) and 8 excluded by channel selection (PPG/ECG/EDA/temperature blocks on an RR-only configuration) — each flagged on every record. This closes W3-A F8.

## 5. Derived results (group separation and records)

Sustained ΔHR (short-protocol proxy) by group, verbatim:

| Group | n | Mean (bpm) | SD | Range |
|---|---|---|---|---|
| healthy | 3 | 28.93 | 5.32 | [24.92, 34.96] |
| pots (hypovolemic) | 3 | 27.28 | 11.29 | [17.96, 39.84] |

**The group ranges overlap on [24.9, 35.0] bpm BY DESIGN** (`overlap_note` in the manifest): the severity mixture makes mild deficits overlap the healthy high-normal tail — trivial separability would itself be a release failure.

Per-record derived summaries:

| Record (subject) | Baseline HR (bpm) | Sustained ΔHR (bpm) | Notable flags |
|---|---|---|---|
| healthy-001 | 70.64 | 26.90 | short_protocol_proxy |
| healthy-002 | 68.93 | 24.92 | short_protocol_proxy |
| healthy-003 | 75.50 | 34.96 | + `rhr_calibration_mismatch_beyond_tolerance` |
| pots_hypovolemic-001 | 70.90 | 39.84 | + RHR mismatch, severity resampled |
| pots_hypovolemic-002 | 88.02 | 17.96 | + RHR mismatch, severity resampled |
| pots_hypovolemic-003 | 104.89 | 24.04 | + RHR mismatch, severity resampled |

All records: `validation: {schema: pass, provenance: pass, scientific_contract: pass}`; `canonical_status: canonical`. Record IDs are content-derived UUIDs (e.g. healthy-001 `bf25dd9f-4207-5873-a21c-cceb0df114ee`).

## 6. Anti-laundering checks (verbatim results)

- **Metadata negative control (review F1):** sex/age/BMI/fitness/device metadata-only classifier — per-feature Mann-Whitney AUC + ridge-LDA multivariate (deterministic closed form). Result: **multivariate AUC 0.5; every per-feature AUC 0.5; passed** (ε = 0.1; n = 3 per condition). Manifest note: at n ≤ 3/group, per-feature AUC is exactly 0.5 only under pairwise-matched sampling.
- **Rule (recorded on the manifest):** between-condition separation comes from mechanism only (volume deficit, pooling axis, baroreflex); no label conditioning of signals; **AUC > 0.95 = release failure**.
- **Provenance gate:** `ok: true`, mode canonical, **23 warnings** — every consumed KB file carries "no human (L3) review recorded; AI-agent/validator reviews only — file is provisionally admissible pending human review" (surfaced as warnings, never silent pass; see SCIENTIFIC_DEBT_REGISTER SD-11).
- **Validation status:** all records passed; per-record `reference_comparison` blocks in `derived.json` (single-run; cohort-level comparison requires the full healthy distribution).

## 7. Intended use and prohibitions

**Intended use (candidate status only):** pipeline development and testing against the OCPE record schema; methods development with ground-truth access for debugging; reproducing the Phase-2 validation gates. The intended-use decision for a v1 dataset (screening-algorithm training vs education vs pipeline testing) remains an open governance item (G-P2-16).

**Prohibitions (binding):**
1. No utility claim for any task — the L5 benchmark matrix does not exist; the binding sentence must accompany any use or description of this dataset.
2. No clinical interpretation: the ≥30 bpm POTS criterion is not licensed on the 100-s bench protocol (short-protocol proxy); no record is a synthetic patient.
3. No use of `ground_truth.npz` latents as input features presented as observable data (latent = ground truth only; absolute BP, SV, CO, SVR, venous pooling, cerebral perfusion, core temp, hydration, BRS, PEM labels are latent-only per the dataset specification §0.1).
4. No disease-classification reporting that exceeds the anti-laundering cap without treating it as a data defect: AUC > 0.95 on this dataset indicates stereotyped/over-separated data or label leakage and must be reported as such, not as a result.
5. PEM, hEDS, neuropathic-POTS, and all tier-D/experimental content is out of scope of this canonical pilot; enabling experimental modes produces labeled extrapolation, never canonical records.
6. Do not treat the demographic matching as a population claim: n=3 per condition is a continuity pilot; all classifier-level statements at this n are underpowered (W3-A standing note: re-test at ≥20/group).
