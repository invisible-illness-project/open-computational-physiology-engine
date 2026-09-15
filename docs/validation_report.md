# OCPE Validation Report - Release Gates L1-L4 + Negative Controls

**Governing statement (binding):** *OCPE synthetic data are candidate research artifacts whose utility for any task is unestablished pending the Level-5 benchmark.*

**Level-5 status:** NOT EXECUTED - the Level-5 synthetic-to-real benchmark matrix does not exist yet. Levels 1-4 are necessary but not sufficient; no utility claim for OCPE synthetic data is made or implied by this report.

Generated from gate context seed 20260915, commit `efcffb70914b96b74f6b09b08231e00876517afc`, started 2026-09-16T02:59:38. Licensed cohort: 4 healthy + 4 hypovolemic-POTS subjects, 10-min HUT (300 s supine + 600 s tilt + 60 s recovery, dt=0.02).

## Summary

| status | count |
|---|---|
| pass | 15 |
| fail | 6 |
| unresolved | 2 |
| disclosed_limitation | 1 |

## Cross-gate synthesis

- **F1 (engine-level, blocking for L2 timescale/L4 signal anchors):** the supine mean-HR baseline of the ODE core oscillates with std ~14.5 bpm (healthy supine reference: quasi-stationary, RMSSD-equivalent wander of a few bpm). The oscillation is structural: verified invariant to integration dt (0.01 vs 0.02) and to OU-layer disablement during gate development. It propagates into 6 gates: oscillatory tilt transients/recovery (2.1 battery), DFA-alpha1 ~1.5 vs [0.8, 1.2], RSA peak misplaced below the respiration line, resting RMSSD far above published norms, and early-tilt overshoot driving the PRCP Wasserstein distance beyond the 3 bpm target. Mean-level responses are unaffected and pass (baseline HR, sustained delta-HR, circadian amplitude, meal response, clinical contrasts). Correction target: simulation/ baroreflex loop damping (W1-A ownership); do NOT widen these bands.
- **F2 (real-data anchor):** simulated healthy early-tilt delta-HR (minutes 2-3) [24.23535622306757, 29.23847068381314, 31.93620810324863, 28.733042068221934] sits above the PRCP real episodes [15.255836673931881, 18.89207989478026, 16.632170782571606, 16.24305205607486, 25.02966923310614, 11.480411914880705, 10.534008067247598, 2.2700633653135895, 6.127170517848398, 16.960277913251304, 18.50953884034812] (W1 = 14.178107518737413 bpm vs target <= 3). Consistent with F1 (exaggerated early orthostatic response); not a sampling artifact (matched windows disclosed).
- **Unresolved (L3/3.1_healthy_hut_distribution):** n=4 < 8: tail band (0.40-0.60) not resolvable at this Monte-Carlo size; measured fraction 1.00 95% CI [0.40, 1.00]; mean check PASS
- **Unresolved (L4/4_eurobavar_reflex_gain):** download/parse failed (exact reason recorded)

## Results

| gate | check | target | measured | status | evidence |
|---|---|---|---|---|---|
| L1 | 1.5_determinism | same seed -> bit-identical engine output (time/state/RR) | {keys_compared: [Hc, Vau, pau, rr_intervals_ms, time], mismatches: {}} | PASS | SYNTHETIC_TO_REAL_BENCHMARK L1.5; engine seeded-determinism precedent |
| L1 | 1.2_volume_conservation | ODE mass conservation: sum(stressed V_i) drift < 1e-6*TotalVol over a full tilt run; unstressed offset constant | {convention: state compartments are STRESSED volumes (p=V/C); unstressed     remainder implicit and constant (Geddes-scale ODE), drift_rel_totalvol: 0.0,   max_sumV_drift_ml: 0.0, n_steps: 15139, offset_drift_rel: 0.0... | PASS | L1.2; Geddes-scale ODE (EVD-TEMP-003 context) |
| L1 | kernel_restoration_ralpm | meal_postprandial_pooling: plateau RalpM = baseline x0.75; EXACT baseline after recovery | {baseline: 17.88, expected_plateau: 13.41, final: 17.88, plateau: 13.41,   plateau_ok: true, restored_exactly: true, symbol: RalpM} | PASS | G-P0-01 compounding fix; EVD-HLTH-006 timing |
| L1 | kernel_restoration_es | exercise_bout: plateau Es = baseline x1.3; EXACT baseline after recovery | {baseline: 3.0, expected_plateau: 3.9, final: 3.0, plateau: 3.9, plateau_ok: true,   restored_exactly: true, symbol: Es} | PASS | G-P0-01 compounding fix; EVD-HLTH-006 timing |
| L1 | 1.4_identifiability | all ODE params carry E-level governance metadata; +/-20% kH perturbation below PPG LoA +/-7 bpm -> non_identifiable | {parameter_semantics: 'population priors, never per-subject estimates',   practical_demo: {delta_hr_bpm_from_param_perturbation: 2.918992, label: non_identifiable,     observation_noise_loa_bpm: 7.0}, structural: {mis... | PASS | L1.4; EVD-TEMP-010 (structural unidentifiability, E4) |
| L1 | 1.6_honesty_gating | tier-D inert in canonical mode; perturbations carry E-level + claim ids; provenance gate refuses hash-tampered KB | {experimental_inert: true, experimental_phenotype: autoimmune_neuropathy,   perturbations_tagged: true, tamper_detail: "refused as required: provenance\     \ gate REFUSED dataset build (1 refusal(s), mode=canonical):... | PASS | L1.6; EVIDENCE_AUDIT_NOTES §e; ADR 0001 |
| L1 | 1.7_scale_harmonization | consumed KB tiers map to E0-E5; unrecognized tier -> EXPERIMENTAL (fail-closed) | {all_tiers_standard: true, offenders: [], unknown_scale_fails_closed: true} | PASS | L1.7; EVIDENCE_AUDIT_NOTES §0 action item |
| L1 | schema_provenance_contract_hooks | dataset/schema.py hooks (schema + provenance + scientific contract incl. latent-boundary guard) pass on all records | {errors: [], n_records: 2} | PASS | dataset/schema.py; master prompt §18/§21; rule 3 |
| L1 | 1.5_record_determinism | same dataset_seed -> byte-identical record.yaml/derived.json | {identical: true, record: hut60_short} | PASS | L1.5; dataset/schema.py deterministic_build_timestamp |
| L2 | 2.1_tilt_trajectory_battery | healthy bench tilt: baseline 55-75 bpm; sustained proxy +15..+40; transient 3-35; recovery residual within +/-10 bpm at ~45 s | {band_sources: {bench_sustained_proxy_dhr_bpm: 'EV-head-up-tilt (bench proxy,       G-P0-09 flagged)', initial_transient_peak_bpm: EV-head-up-tilt initial_0_30s,     recovery_residual_bpm_45s: EV-active-stand recovery... | FAIL | EVENT_PROTOCOLS EV-supine-rest / EV-head-up-tilt / EV-active-stand (EVD-HLTH-004) |
| L2 | 2.1_meal_response | postprandial HR elevation within (2.0, 15.0) bpm (mixed meal +6+/-3; EVD-HLTH-006) | {plateau_dhr_bpm: 10.175424, plateau_window_s: [64.0, 152.0], time_scale: 0.03} | PASS | EV-meal (EVD-HLTH-006, EVD-METB-005) |
| L2 | 2.1_exercise_response | bout HR elevation within (5.0, 70.0) bpm; recovery below bout plateau (EV-exercise-constant-load / EV-recovery) | {bout_dhr_bpm: 6.318207, es_plateau_bounded: true, late_recovery_dhr_bpm: 7.057323} | FAIL | EV-exercise-constant-load (EVD-TEMP-004/EVD-HLTH-005) |
| L2 | 2.2_dfa_alpha1 | DFA-alpha1 (4-16 beats) in (0.8, 1.2) healthy awake | {dfa_alpha1: 1.515317} | FAIL | EVD-TEMP-001 (E4) |
| L2 | 2.2_rsa_peak | RSA/HF spectral peak tracks respiration rate (\|f_peak - f_resp\| <= 0.05 Hz) | {hf_peak_hz: 0.160535, lf_hf_ratio: 12.647855, respiration_hz: 0.258605} | FAIL | EVD-TEMP-003; TEMPORAL §1 (RSA confound built-in) |
| L2 | 2.2_circadian_amplitude | circadian HR amplitude within (11.0, 16.0) bpm (~13.5; acrophase ~14:40) | {acrophase_h: 9.398113, amplitude_bpm: 13.500987, days: 2, mesor_bpm: 58.065886} | PASS | EVD-HLTH-003 (E2/E4 cosinor anchor) |
| L3 | 3.1_healthy_hut_distribution | healthy HUT sustained dHR mean 34+/-tol and >=30 bpm fraction in [0.40, 0.60] (frozen reference, tails preserved) | {ci95_fraction_ge_30bpm: [0.397635, 1.0], comparison: {consistent_with_healthy_reference: false,     evidence_level: E3, mean_within_reference: true, n_samples: 4, protocol_id: hut_60_70_10min,     reference_fraction_... | UNRESOLVED | healthy_reference.yaml hut_60_70_10min; Plash 2013 (EVD-HLTH-004); CONTRADICTION Target 1 |
| L3 | 3.1_hypovolemic_pots_rate | hypovolemic-POTS >=30 bpm sustained rate >= 0.5 (severity mixture, tails reported) AND patient-minus-control +19.88 bpm within CI [15.24, 24.52] | {contrast_bpm: 18.535878, contrast_ci95_target: [15.24, 24.52], n_pots: 4,   pots_samples_bpm: [29.934924, 48.86654, 62.932814, 71.811576], rate_ci95: [     0.19412, 0.993691], rate_ge_30bpm: 0.75} | PASS | EVD-POTS-011 (E4, meta +19.88 [15.24-24.52]); EVD-POTS-004 (Raj 2005 severity mixture); CONTRADICTION Target 1/3 |
| L3 | 3.1_hyperadrenergic_dsbp_limitation | evaluator surfaces the delta-SBP pressor-criterion failure as a DISCLOSED LIMITATION (not a pass) | {delta_SBP_beatwise_mmHg: 0.569633, limitation_surfaced: true, limitations: [     'hyperadrenergic_pots: upright delta-SBP pressor criterion (Okamoto       2024, tier A, required >= +10 mmHg) NOT met - simulated delta... | DISCLOSED_LIMITATION | G-P0-03 companion; GAP G-P1-01; tests/test_orthostatic_response.py strict-xfail |
| L4 | 4_prcp_orthostatic_wasserstein | Wasserstein(sim healthy tilt dHR, PRCP real dHR) <= 3.0 bpm | {n_real_episodes: 11, n_sim_subjects: 4, real_delta_hr_bpm: [15.255837,     18.89208, 16.632171, 16.243052, 25.029669, 11.480412, 10.534008, 2.270063,     6.127171, 16.960278, 18.509539], sim_delta_hr_bpm: [24.235356,... | FAIL | PRCP (PhysioNet, OPEN, Heldt et al.); benchmark §L4 |
| L4 | 4_eurobavar_reflex_gain | EUROBAVAR supine->standing reflex-gain comparison | {fetch_error: 'URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED]     certificate verify failed: self-signed certificate (_ssl.c:1010)>'} | UNRESOLVED | VALIDATION_DATASETS §1.2 |
| L4 | 4_resting_hrv_norms | healthy resting RMSSD median within (19.0, 60.0) ms (ln-normal median ~35-42 ms young; EV-supine-rest) | {n: 4, rmssd_median_ms: 179.057015, rmssd_values_ms: [147.618122, 210.495908,     78.105779, 226.474985], sdnn_median_ms: 301.031132} | FAIL | EV-supine-rest (EVD-HLTH-001/002); published norms (literature-constraint tier, no download) |
| NC | NC_parity_nuisance_channels | group-conditional nuisance channels forbidden (sampling rate, noise, missingness, record length, device distribution) | {channels_checked: [device_profile, engine_dt, hrv_model, hrv_noise, licensed_protocol,     missingness_model, record_devices, record_length_samples, seed_policy],   mismatches: {}} | PASS | master prompt §14; SWARM_SPEC rule 5 (anti-laundering) |
| NC | NC2_trivial_separability_auc | healthy-vs-hypovolemic-POTS LOOCV logistic AUC < 0.95; honest band (0.75, 0.85) reported (NC2) | {auc_full_features: 0.625, auc_resting_features_only: 0.6875, ceiling: 0.95,   features: [baseline_hr_bpm, sustained_dhr_bpm, initial_transient_bpm,     rmssd_ms, sdnn_ms, dfa_alpha1, lf_hf_ratio], honest_band_NC2: [0... | PASS | benchmark NC2 (EVD-LCOV-013 overfit counter-example); reviewer Criterion 1; rule 5 |
| NC | NC_demographics_disclosure | demographic differences are evidence-based (POTS 85-94% female, young onset; EVD-POP-006) and disclosed; not nuisance parity | {healthy: {age_mean: 35.911746, female_fraction: 0.5, n: 4}, hypovolemic_pots: {     age_mean: 26.375222, female_fraction: 0.75, n: 4}} | PASS | EVD-POP-006; dataset/cohort.py recipes |

## Notes

- **L1/1.2_volume_conservation**: state convention: compartments hold STRESSED volumes; benchmark 1.2 invariant applied to the conserved quantity
- **L1/1.4_identifiability**: ODE parameters are population priors with documented uncertainty, never per-subject estimates
- **L2/2.1_tilt_trajectory_battery**: bench protocol = short_protocol_proxy (G-P0-09 flagged); licensed 10-min claims live in L3. Supine mean-HR std 14.5 bpm documents the engine baseline oscillation affecting transient/recovery morphology (see 2.2 gates).
- **L2/2.1_meal_response**: kernel timing compressed (time_scale) for ODE feasibility; magnitudes untouched
- **L2/2.1_exercise_response**: the Es x1.30 contractility kernel couples only weakly to HR in the ODE (+~6 bpm), and the window comparisons are dominated by the engine baseline oscillation (see 2.2 gates); reported, not tuned
- **L3/3.1_healthy_hut_distribution**: n=4 < 8: tail band (0.40-0.60) not resolvable at this Monte-Carlo size; measured fraction 1.00 95% CI [0.40, 1.00]; mean check PASS
- **L3/3.1_hypovolemic_pots_rate**: severity-mixture branch: mild deficits overlap the healthy high-normal tail BY CONSTRUCTION (pilot design); rate is reported, never tuned
- **L3/3.1_hyperadrenergic_dsbp_limitation**: 0-D windkessel limitation: pulse pressure narrows on tilt (SV falls); disclosed per W1-C, never silently passed
- **L4/4_prcp_orthostatic_wasserstein**: 11 slow-tilt episodes from 10 PRCP records; fetch warnings: None
- **L4/4_eurobavar_reflex_gain**: download/parse failed (exact reason recorded)
- **NC/NC2_trivial_separability_auc**: AUC is REPORTED, never tuned to pass; >0.95 = release failure regardless of cause. Resting-only view excludes the orthostatic diagnostic features.
- **NC/NC_demographics_disclosure**: informational: POTS demographics differ BY EVIDENCE; classifier uses signal features only
