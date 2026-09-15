# OCPE — Synthetic Multimodal Wearable Dataset Specification

**Version:** 0.1 (design specification; no synthetic data may be claimed validated until SYNTHETIC_TO_REAL_BENCHMARK.md Level 5 completes).
**Author:** Synthetic Dataset Scientist (OCPE research swarm).
**Upstream evidence:** EVIDENCE_REGISTRY.yaml (143 claims, normalized standard E-scale: **E0 hypothesis / E1 mechanistic / E2 observational / E3 controlled experimental / E4 replicated quantitative / E5 meta-analysis-consensus**). All `EVD-*` identifiers below reference registry claim_ids with their **normalized** grades. NOTE: TEMPORAL_MODEL_EVIDENCE.md and WEARABLE_OBSERVABILITY_EVIDENCE.md use inverted/metrology scales in their own text — only the registry's normalized `evidence_strength` values are authoritative here.
**Governing audits:** EVIDENCE_AUDIT_NOTES.md (downgrades, must-not-hard-code list), CONTRADICTION_AUDIT.md (weakened/refuted claims), INDEPENDENT_REVIEW_PASS2.md (P0–P2 required revisions), CURRENT_IMPLEMENTATION_MAP.md (engine gap map).

---

## 0. HARD RULES (binding on every generated record)

These rules are extracted from WEARABLE_OBSERVABILITY_EVIDENCE.md §d, CONTRADICTION_AUDIT.md, and INDEPENDENT_REVIEW_PASS2.md §4. A record violating any rule is invalid and must be rejected by the dataset generator's own CI.

### 0.1 Latent-only variables — ground truth ONLY, never a sensor channel
The following exist **only** in the ground-truth schema (§1). No synthetic "sensor" may emit them, and no derived measurement may be a noise-free readout of them:

| Latent variable | Reason / registry anchor |
|---|---|
| Absolute blood pressure (SBP/DBP/MAP) | Cuffless BP fails ISO away from calibration (LoA ±16 mmHg SBP, drift 6.8±5.6 mmHg/week); only calibration-anchored *trend* may be emitted as a pseudo-channel with distance-from-calibration error growth (EVD-SENS-001 context; WEARABLE C3) |
| Stroke volume / cardiac output (at wrist) | No validated wrist estimator; BCG CO MAE 0.83 L/min, PE 30.2% is research-only (WEARABLE C4) |
| Systemic vascular resistance | Requires pressure AND flow; both non-observable (WEARABLE C5) |
| Venous pooling volume / venous return | Latent; only downstream ΔHR signature observable (WEARABLE C6) |
| Cerebral perfusion / CBFv | Zero wrist inference literature (WEARABLE C7) |
| Core temperature in °C (resting/febrile) | Validated only for exertional heat-stress (MAE ~0.3 °C, fit young cohorts); resting/febrile core estimation unvalidated (WEARABLE T2) |
| Hydration status | All proxies dominated by temperature/ambient/recent intake (WEARABLE M3) |
| Blood/interstitial glucose via ANY optical channel | No validated wrist-optical glucose exists; CGM only (EVD-METB-004) |
| Insulin, ketones, RER, BAT activity, endothelial stiffness, inflammatory cytokine levels | LATENT-ONLY lists in METABOLIC/AUTOIMMUNE dossiers (EVD-AUTO-011) |
| Baroreflex sensitivity in ms/mmHg | Research surrogates only (E2); index, not absolute value (WEARABLE A3) |
| PEM episode labels as sensor output | No validated individual PEM detector exists (EVD-MECFS-010; WEARABLE S2) |
| Psychological stress as ground truth | Wearables measure autonomic arousal, valence- and cause-blind (WEARABLE AC5) |

**Coupling-not-readout rule:** latents modulate observable signals through documented mechanisms (venous pooling → postural ΔHR; SV → PPG pulse amplitude; core temp → skin temp + HR; inflammation → RHR/HRV/sleep) — the engine implements the *coupling*, never the *readout*.

### 0.2 Non-trivial classifiability (anti-stereotype guard)
- Target realistic condition-classification performance band: **AUC ~0.75–0.85** for phenotype classification from wearable observables. AUC >0.95 indicates stereotyped, over-separated synthetic data and must fail CI (EVD-LCOV-013; INDEPENDENT_REVIEW Criterion 1).
- **Uninfected/healthy background symptom rates are mandatory:** PEM 7%, fatigue 17%, brain fog 4%, orthostatic intolerance ~6% in controls (EVD-LCOV-012, RECOVER n=9,764).
- **Medication masks:** beta-blockers (blunt HR/HRV/orthostatic response), steroids (RHR↑, sleep↓, decorrelate CRP-proxy), levodopa (post-dose OH), SSRIs — a cross-disease confound layer present in all cohorts (EVD-AUTO-009; INDEPENDENT_REVIEW §3 item 14).
- **Pacing confound is first-class:** ME/CFS/long-COVID behavioral activity restriction abolishes most apparent wearable group differences when activity-matched (EVD-MECFS-010, EVD-MECFS-011); pacing must be a modeled behavioral state, not noise.
- All disease resting-HR/HRV effects use **within-person deviation semantics** with overlapping magnitudes (POTS +10–20 clinic but +~3 real-world, ME/CFS +4.14, LC +1–3, RA flare +5, T2DM +5–10 bpm — INDEPENDENT_REVIEW §2 row 9).

### 0.3 Artifact realism mandatory
Every inferred feature ships with its documented mimics: motion-as-HRV, immobility-as-sleep, cold-vasoconstriction-as-BP-change, cadence-lock, slow-gait step undercount (5–30%, correlating with ME/CFS severity and elderly cohorts — an *observability* confound), alcohol/jet-lag-as-infection-anomaly (WEARABLE §d rule 3; SENSOR §7 table).

### 0.4 Uncertainty representation (must-not-be-hard-coded list)
Per EVIDENCE_AUDIT_NOTES.md §c and CONTRADICTION_AUDIT.md §E, the following enter the generator as **distributions / latent mixtures / sensitivity parameters, never point constants** (each tagged in the schema with `sampling: distribution`):
healthy orthostatic ΔHR (protocol-conditioned; Target 1); Geddes POTS parameter shifts (tier-D scenario sampling + Fu-2010 competing branch; Target 2); POTS blood-volume deficit (mixture: ~45% hypovolemic −14±10%, volume-normal remainder; Target 3); ME/CFS 2-day-CPET decrement (small mean + effort-coupling + responder subgroup ~20–40%; Target 4); PEM (symptom kernel 12–48 h delay vs physiological slowed-recovery kernel, decoupled; Target 5); fever–HR slope (age-graded ~7–13 bpm/°C, adults ~7–10; Target 7); skin-tone sensor terms (sampled, mass at ~0 for PPG-HR; Target 8); latent factor loadings (±50% sampling, copula sensitivity at r=0; Target 10); comorbidity rates (0.3–0.5× ascertainment down-weight; §5.3); baroreflex gain in POTS (−15 to −25% wide prior; EVD-POTS-010); menstrual effect sizes (EVD-TEMP-008); autonomic latencies (soft priors; EVD-TEMP-005 normalized to standard E1, AUTONOMIC E4 with wide-prior caveat).

---

## 1. GROUND-TRUTH SCHEMA (latent physiology layer)

All trajectories stored at native simulation rate (beat-event level for cardiac, 1/min for slow layers) plus resampled 1 Hz aggregate. Every field carries `unit`, `evidence_refs` (registry claim_ids), and `sampling: point|distribution|mixture|flagged-speculative`.

### 1.1 Autonomic state
| Variable | Symbol / type | Distribution & source |
|---|---|---|
| Sympathetic tone (sudomotor+vasomotor drive) | `T_sym` ∈ [0,1], float | Baseline logit-normal, person mean ~0.3 (engine default); state-modulated. MSNA norms: 24±6 bursts/min, range 9–41 (EVD-AUTN-001, E4) |
| Parasympathetic (vagal) tone | `T_para` ∈ [0,1], float | Person mean ~0.7; shared "tonic vagal gain" knob across conditions (INDEPENDENT_REVIEW §3.1). RMSSD↔vagal coupling valid at rest only, confounded by respiration/HR/device (CONTRADICTION Target 6) |
| Baroreflex gain (maximal cardiovagal) | `G_baro`, ms/mmHg | Population: phenylephrine ~15–20 young, age gradient 19.5→~5 ms/mmHg (EVD-AUTN-002). POTS: sample −15 to −25% reduction vs unchanged (genuinely unresolved; EVD-POTS-010, distribution) |
| Autonomic latencies | `tau_vagal`, `tau_sym`, s | Vagal 0.2–0.6 s (same/next beat); sympathetic 5–20 s + NE washout (EVD-AUTN-004 E4 vs EVD-TEMP-005 expert-opinion discrepancy → soft priors, wide) |
| Intrinsic heart rate | `IHR`, bpm | 118.1 − 0.57·age (EVD-AUTN-007) |
| Circadian phase | `phi_circ`, rad | Free-running τ = 24 h 11 min ± 16 min (EVD-TEMP-006); DLMO→wake 9.2 h |
| Sleep pressure / Process S | `S_sleep` ∈ [0,1] | Two-process S+C model (TEMPORAL §4, standard E5/E0-consensus) |
| Stress/arousal state | `L_stress` ∈ [0,1] | Event-kernel driven (§6); TSST effect sizes (EVD-NEUR-011); tonic anxiety shifts vmHRV g≈−0.3–−0.45, NOT reactivity (EVD-NEUR-009) |
| Inflammatory burden | `B_infl` ∈ [0,∞), float | Population CRP/IL-6–HRV meta link (|r|≈0.1, EVD-AUTO-002, E4); LPS storm reference trajectory HR +47–54% at 3–6 h (EVD-AUTO-001, E4 human experimental) |
| Metabolic reserve | `R_metab` ∈ [0,1] | ME/CFS capacity latent (EVD-MECFS-002 anchors) |
| Autonomic recovery capacity | `C_rec` ∈ [0,1] | Slowed-recovery kernel time constant: healthy 3–6 h vs long COVID 9–13 h post-VT1 exercise (CONTRADICTION Target 5, VERIFIED single study — single-source tag) |
| Hormonal state (menstrual phase) | `theta_cycle`, rad | T_cycle 28.6±3.8 d; luteal skin temp +0.2–0.3 °C, RHR +2–7 bpm, RMSSD ×~0.9, ovulatory dip (EVD-TEMP-008, E2–E3; per-person heterogeneity high) |

### 1.2 Cardiovascular state
| Variable | Type | Distribution & source |
|---|---|---|
| Heart rate (true SA-node rate) | `HR_true`, bpm, beat-level | IPFM/point-process generator (§6); population marginals: daily RHR 65.5±7.7 bpm, individual means 39.7–108.6 (EVD-POP-001, E4); sex +3 bpm F; inverted-U age shape (NOT monotonic) |
| HRmax | `HRmax`, bpm | N(208 − 0.7·age, 10.5²); women 206 − 0.88·age (EVD-POP-003, E5) |
| Blood pressure (absolute) | `SBP_true`, `DBP_true`, mmHg | **LATENT-ONLY.** NHANES II mean 127/79, SBP–DBP r=0.717; SBP +~1 mmHg/yr, DBP inverted-U (POPULATION A.4) |
| Stroke volume / cardiac output | `SV_true`, `CO_true` | **LATENT-ONLY (wrist).** SV 60–100 mL, CO 4–8 L/min; scale to lean mass (allometric exponent ~1; CO ~body-size^0.55) (POPULATION A.5) |
| Systemic vascular resistance | `SVR_true` | **LATENT-ONLY.** No wearable estimator (WEARABLE C5) |
| Total blood volume | `V_total`, mL/kg | Healthy ~71 [65–78] mL/kg; POTS mixture: ~45% hypovolemic branch deficit −14±10% (Raj/Fu/Kulapatana triangulated, CONTRADICTION Target 3, CONFIRMED direction) + volume-normal branch (EVD-POTS-004) |
| Venous pooling (postural shift) | `V_pool`, mL | **LATENT-ONLY.** 0.5–1.0 L thoracic shift on standing, bulk within 10 s (EVD-AUTN-005); regional phenotypes: thoracic Δ −12±3% control vs −25±5% low-flow POTS (EVD-POTS-007, replication: low — single lab) |
| Cerebral blood flow velocity | `CBFv_true` | **LATENT-ONLY.** Upright reduction in POTS, ~25% hypocapnia subset (EVD-POTS-008, E2/E3) |
| Ectopy burden | per-beat Bernoulli flag | 40–75% of adults show ≥1 PVC on 24-h Holter; burden ≥5% in ~7.7% palpitation outpatients (TEMPORAL §7, E4 replicated) |

### 1.3 Respiratory state
| Variable | Type | Distribution & source |
|---|---|---|
| Respiration rate | `RR_true`, brpm | KORA-FF4 n=2,224: median ~15.8, 5th–95th 12.1–20.4, ~13.8% ≥18.6 (EVD-HLTH-010, E4); weak age gradient |
| Tidal volume (relative) | `Vt_rel` | RSA amplitude scales with Vt and inverse RR independently of vagal tone — mechanistic input to HRV, not noise (CONTRADICTION Target 6; Schipke: RMSSD varies up to 37% across RR at constant HR) |
| Breathing pattern / apnea events | event flags | OSA cyclical 4-phase pattern parameterized by AHI (EVD-NEUR-012); EDS OSA 32% vs 6% (EVD-EDS-007) |

### 1.4 Metabolic state
| Variable | Type | Distribution & source |
|---|---|---|
| Interstitial glucose | `glucose_true`, mg/dL | 24-h mean ~90–99, SD 6–8; TIR(70–140) median 96%; diurnal nadir 03:00–06:00; postprandial peak 45–65 min <140 mg/dL (EVD-METB-001/002/003, E4). **Sensor-visible ONLY via CGM channel** |
| Insulin / insulin sensitivity | latent | Sleep restriction −20% IVGTT (EVD-METB-011); never sensor-visible |
| Energy expenditure | `EE_true`, kcal | Mifflin-St Jeor ±10% for 82% non-obese (EVD-METB-007); **wearable EE output must carry ≥20–30% individual error** (EVD-METB-008, E5) |
| Hydration | `H_hydr` ∈ [0,1] | **LATENT-ONLY** (WEARABLE M3); couples to blood volume and orthostatic tolerance |

### 1.5 Thermoregulatory state
| Variable | Type | Distribution & source |
|---|---|---|
| Core temperature | `T_core`, °C | **LATENT-ONLY at rest/fever.** Mean ~36.6–37.0; circadian amplitude ~0.5 °C, nadir ~2 h before habitual wake (EVD-TEMP-006) |
| Distal skin temperature (true) | `T_skin_true`, °C | Wrist mesor ~33 °C, circadian amplitude 1.2–1.4 °C (older −19%, acrophase +66–73 min earlier); luteal +0.2–0.3 °C (EVD-SENS-007; POPULATION A.7) |
| Fever episodes | event state | Fever→HR slope age-graded: ~13 bpm/°C young children → ~7–10 adults, wide inter-individual spread (EVD-AUTO-003 + CONTRADICTION Target 7, REFUTED as single constant); fever EE +10–13%/°C (EVD-AUTO-004) |

### 1.6 Phenotype, severity, events
- `phenotype`: enum {`healthy`, `pots`, `mecfs`, `long_covid`, `heds`, `autoimmune_ra`, `autoimmune_ibd`, `sle`, `t2dm`, `pd`, `irbd`, `osa`, `anxiety`, `migraine`, `vasovagal_syncope`} — **composable set**, not exclusive label (POTS subtypes: hyperadrenergic 75.0%, hypovolemic 44.9%, neuropathic 37.8%; 41.7% two, 11.4% three, 6.8% none — EVD-POTS-003, VERIFIED).
- `severity`: continuous latent functional capacity, discretized only for reporting. ME/CFS anchors: steps/day 8,235±1,004 / 5,195±1,231 / 2,031±824 for mild/moderate/severe; %predicted VO2 90/64/48 (EVD-MECFS-002, E4 downgraded from E5 clinic anchor, single-clinic tag). POTS: EQ-VAS-like continuous with ~25% disabled tail (EVD-POP-006).
- `events[]`: typed, timestamped: `stand`, `tilt`, `meal{kcal,carb_fraction}`, `exercise_bout{intensity%HRmax,duration}`, `sleep_onset/offset`, `stress_episode`, `pem_episode` (symptom kernel: onset 12–48 h, peak 24–48 h, recovery mean 12.7 d range 1–64 — EVD-MECFS-008/009, right-skewed distribution, MEAN not median per reviewer fix; physiological channel = slowed-recovery kernel hours-scale, delayed physiological second wave E0-optional), `infection_episode` (multiphasic RHR elevation, mean 79 d to baseline post-COVID — EVD-LCOV-010), `flare` (RA: RHR +5.0 bpm, mean HR +6.0, night HR elevation — EVD-AUTO-005 marginal means only, NOT the AUC-1.00 classifier claim), `medication_dose`, `menstrual_phase_transition`.

---

## 2. SENSOR OBSERVATION LAYER

Design principle (SENSOR_MODEL_EVIDENCE.md header): reproduce the *measurement chain* — physiology → transduction → sampling → noise/artifact → derived-feature error — not just clean physiology.

### 2.1 Device profiles
| Profile | Class | ECG | PPG | EDA | Temp | IMU | Resp |
|---|---|---|---|---|---|---|---|
| `research_patch` | research (Movesense-Medical-like) | 250–512 Hz, 24-bit | — | — | — | 50–100 Hz | belt 25–100 Hz |
| `polar_h10_like` | research-grade chest strap | 130 Hz ±2%, 24-bit, 0.7–40 Hz band (ST/morphology distorted by 0.7 Hz high-pass — E3) | — | — | — | — | EDR-derived |
| `empatica_e4_like` | research wristband | — | 64 Hz, 2 green + 2 red, 8-bit | 4 Hz, 0.01–100 µS | 4 Hz | 32 Hz, ±2 g (clips on heel-strike) | PPG-derived |
| `apple_watch_like` | consumer watch | intermittent 1-lead on demand | green (duty-cycled), IR background; derived HR ~1 Hz | — | wrist temp (nightly) | 25–100 Hz duty-cycled | PPG-derived |
| `oura_ring_like` | consumer ring | — | 50 Hz red/IR | — | 1-min epochs, 0.07 °C resolution | 50 Hz | PPG-derived |

Duty-cycling and background-vs-active sampling modes are part of the profile (consumer devices silently quality-gate and down-sample; EVD-SENS-003).

### 2.2 Beat generation → waveform derivation (per TEMPORAL dossier)
1. **Beat times:** IPFM core `1 = ∫[m0 + m(t)]dt`, `m(t) = C_S·sin(2π·0.1 Hz·t) + C_V·sin(2π·f_resp·t) + n_1f(t) + slow_modulators(t)`, with state-dependent C_S, C_V from slow layers; additive 1/f fractal modulator (target DFA-α1 ≈ 1.0 rest, range 0.7–1.2, EVD-TEMP-001); ectopy via Bernoulli per-beat + phase reset. Inverse-Gaussian point process (EVD-TEMP-002) is the **reference distribution for validation**, not the generator (engineering judgment, registry-normalized E0-equivalent).
2. **ECG waveform:** McSharry–Clifford 3-ODE dynamical model (Gaussian-kernel PQRST around unit circle) driven by beat times — reproduces RSA, Mayer waves, LF/HF, R-peak amplitude modulation (EVD-TEMP-011). QRS amplitude 0.5–2 mV; monitoring band 0.05–45 Hz.
3. **PPG waveform:** filtered/phase-shifted derivative of the same pulse train (engineering judgment); AC/DC perfusion index 0.5–5% finger, lower at wrist; wavelength-dependent: green 525 nm large AC, melanin-absorbed, less motion-susceptible; red/IR 660/940 nm deeper, better at rest, worse in motion (SENSOR §2.2, E3).
4. **Do NOT simulate full hemodynamics to get waveforms** (TEMPORAL §1; 1-D distributed models rejected — parameter burden unjustified for wrist-observable detail).

### 2.3 Noise / artifact model (SENSOR §7 cross-cutting artifact table + §8 state-dependent gating)
The 16 artifact classes of the dossier's cross-cutting table are implemented as a gated artifact scheduler (IMU-state + physiological-state conditional):

| # | Artifact class | Channel | Generative parameters (evidence) |
|---|---|---|---|
| 1 | Motion artifact bursts | PPG | MA amplitude ≥ pulse AC, up to >10×; quasi-periodic at step frequency (EVD-SENS-004) |
| 2 | Cadence-lock | PPG-HR | When step-rate harmonic ≈ pulse rate: HR error tens of bpm; naive estimator MAE ~26 bpm running (EVD-SENS-004). **Generate raw corrupted signal, not post-algorithm output** |
| 3 | Day/night usability | PPG | Good-quality: day 30.5–49.9%, night 67.3–70.7%; 55.9% of 24 h usable (EVD-SENS-003, E4) |
| 4 | Streaming vs on-device loss | all | BLE streaming loss up to 49% vs ≤9% on-device (EVD-SENS-003) |
| 5 | Off-body / non-wear | all | On-body 80–99.7% of recording time; shower/charge gaps (EVD-SENS-003) |
| 6 | Clock drift | all | ≤1 s/h timestamp error; cross-sensor resample-on-receive |
| 7 | BLE packet loss/jitter | all | Packet loss ~10% at BER 1e-3 w/o retransmission; connection-interval 7.5 ms–4 s alignment error |
| 8 | Electrode motion artifact | ECG | Transients 300–500 ms, amplitude 1–3× QRS, can exceed peak-to-peak ECG (NSTDB, E4) |
| 9 | Baseline wander | ECG | 0.05–1 Hz, up to ~15% of QRS, respiration/posture-coupled (E4) |
| 10 | EMG contamination | ECG | σ ≈ 0.1× QRS, broadband; shivering/exercise-gated (E4) |
| 11 | Dry/contact loss | ECG, EDA | Zero-line segments; implausible HR >200 bpm spikes; exercise-onset dry-strap gaps (E2/E3) |
| 12 | Cold vasoconstriction | PPG | Perfusion index <0.3%; quality collapse after 0–4 °C hand exposure (E3); also gates Raynaud's/low-perfusion states |
| 13 | Skin-tone attenuation | PPG | **Sampled uncertain term, mass at ~0 for HR** (Shcherbina + vs Bent null, n=9 FST-VI caveat, Koerber review inconclusive — EVD-SENS-005; never a fixed constant). SpO2: positive-bias distribution (Sjoding direction robust, magnitude 3–8 pp unstable) |
| 14 | Contact pressure / ambient light leak | PPG | Strap-tightness morphology change; blanching attenuates AC; daylight-gap spikes (E2/E3) |
| 15 | Accelerometer clipping / step false-positives | IMU | Clip at ±FSR; naive wrist step algorithm 10% accurate in non-gait tasks; wrist +20–40% vs hip free-living (EVD-SENS-008) |
| 16 | EDA thermal/humidity bias | EDA | SCL elevation with heat/humidity/season independent of arousal; >20%/2 s step artifacts flagged (EVD-SENS-006) |

Plus derived-metric degradation rows from §8: DFA-α1 LoA +58.1%/−40.9% at high intensity despite RR LoA ±~1 ms (EVD-SENS-002); HRV MAPE ~28.9% Apple Watch vs H10; arrhythmia states degrade all HR/HRV algorithms (AF sens 0.79/spec 0.91 meta context).

**State-dependent gating:** artifact intensity conditioned on IMU activity class (rhythmic locomotion worst), posture, skin-temperature/perfusion state, sleep/recumbency (best quality, 67–71% night usable), and disease state (slow-gait undercount scales with ME/CFS severity — INDEPENDENT_REVIEW §3.13).

### 2.4 Missingness model
- Per-channel Bernoulli/Markov usability: PPG day p(usable)≈0.3–0.5, night ≈0.65–0.75; EDA day 65.6% / night 75.1%; TEMP 96.1% (EVD-SENS-003).
- Non-wear episodes (showering, charging): on-body fraction 80–99.7%, daily gaps.
- Deployment-level loss: streaming up to 49% vs ≤9% on-device; profile-dependent.
- Missingness is **not MCAR**: it is state-correlated (motion, cold, low perfusion, donning) — this correlation is itself a realism requirement (Väliaho/Böttcher, E4).

### 2.5 Recommended simulator defaults (from SENSOR §9)
| Channel | fs default (alternatives) | Clean noise | Derived-feature error model |
|---|---|---|---|
| ECG strap | 130 Hz (250/500/1000) | SNR 15–25 dB; EM bursts 300–500 ms @1–3× QRS; EMG σ=0.1×QRS; BW 0.05–1 Hz | RR: N(0.4, 1 ms) rest → LoA ±2–4 ms; exercise widen 2×; patient/arrhythmic bias up to ~3 bpm, MAPE ~5% |
| PPG wrist | 64 Hz (25/32/100/128) | motion bursts ≥ pulse AC; spectral-entropy SQI; light spikes | HR: bias −0.3 bpm, σ 3.5 bpm rest; MAPE 5–10% moderate exercise; ±19–30 bpm tails severe motion; dropout day Bernoulli(0.5)/night (0.3) |
| EDA | 4 Hz (8–25) | contact zero-lines; >20%/2 s steps | SCL 2–20 µS random walk + temp bias; SCR latency N(1.8,0.4) s, rise 1–3 s, half-rec 2–10 s, amp log-normal 0.05–5 µS; NS-SCR Poisson λ 1–3/min rest → 5–10/min stress |
| Skin temp | 1 Hz (4) | σ 0.03–0.1 °C; quant 0.02–0.07 °C; bias ±0.1–0.36 °C | first-order thermal: core-coupled setpoint + circadian amp 1.2–2.2 °C + vasomotor events + ambient leak τ 2–10 min + off-body decay |
| IMU | 32 Hz (20–100) | 160–290 µg/√Hz white + 1/f; clip ±FSR | steps wrist +20–40% free-living; posture MAPE >44% wrist; slow-gait error 5–30% |
| Resp belt | 25 Hz (50–100) | relative amplitude only; drift | RR ±3 brpm (76% within ±3); PPG-derived 2–10 brpm |
| Sync | — | drift ≤1 s/h; BLE jitter | resample-on-receive, alignment uniform in CI |

---

## 3. DERIVED MEASUREMENTS (inference layer with modeled error)

Each derived metric is `estimate = f(true signal, inference algorithm error distribution)` with the error models below (WEARABLE §d table + SENSOR §2). The inference layer is **versioned separately** from ground truth so benchmarks can ablate it (WEARABLE design rule 5).

| Derived metric | Inference error model | Registry anchor |
|---|---|---|
| HR (PPG) | Bias −0.27 bpm, LoA −7.19/+6.64 bpm pooled; MAPE <10% exercise (10/11 studies); walking worst, cycling best; disease-context decoupling (POTS tachycardia ≠ intensity) | EVD-SENS-001 (E5) |
| HR (ECG strap) | Bias −0.1 to −0.2 bpm; RR LoA +4.3/−2.8 ms low intensity, tighter high; rehab/patient cohorts MAE 3.4 bpm MAPE 4.9% | EVD-SENS-002; SENSOR §1.5 |
| HRV metrics (RMSSD, SDNN, HF, LF, DFA-α1) from ECG | Nocturnal HRV MAPE 5.96–16.32%; DFA-α1 bias up to 8.6%, LoA +58.1/−40.9% high intensity | EVD-SENS-002 (E3) |
| PRV from PPG (**PRV≠HRV modeling mandatory**) | RMSSD inflation +3–6% at rest; LF/HF distortion 10–40% during sympathetic activation; supine ICC 0.955/0.980, seated 0.834/0.921, posture-transition epochs ICC ~0.5–0.7; pulse-transit-time jitter; age/sex LoA widening; ultra-short (1-min) LoA widen markedly | WEARABLE C2 chain |
| RR from PPG | MAE 0.1–2.0 brpm clean; ±2 brpm rest typical; HIIT Arms 2.13 LoA −4.28/+4.09; real-world 5–10.7 brpm; ≥2× belt error | EVD-SENS-009 |
| EDA features (SCL, NS-SCR rate, SCR amp) | Per EVD-SENS-006 dynamics; temperature/humidity offset; motion-corruption in field | EVD-SENS-006 |
| Skin temperature features (mesor, amplitude, acrophase, nightly deviation) | Sensor ±0.1–0.36 °C bias; deviation-from-personal-baseline semantics (TemPredict: +0.63 °C fever-like elevation, 93% pre-symptomatic anomaly rate — E2) | EVD-SENS-007; WEARABLE T3 |
| Steps / activity volume | MAPE 1–3% normal gait → 5–30% slow/intermittent/pathological gait; wrist +39% vs hip; algorithm-conditional marginals (same data 9,676 vs 6,540 mean — 32% shift) | EVD-SENS-008; EVD-POP-008 |
| Sleep (wake/light/deep/REM, TST, WASO, efficiency) | Per-stage confusion matrix; sleep/wake sens ≥95%; 4-stage κ 0.37–0.65 (device-specific); deep/REM duration ICC ≤0.37; wake-immobility false sleeps; device bias offsets (e.g., Fitbit light +18 min, deep −15 min); **disease-specific staging accuracy unstudied — healthy κ values only** | WEARABLE AC3/S3; AUDIT gap 17 |
| Exercise intensity / VO2 proxy | HR-based established at rest/moderate; degrades vigorous; VO2max errors 5–15%; dysautonomia decouples HR from workload (disease-context validity flag) | WEARABLE AC4 |
| Energy expenditure | Individual errors commonly ±20–30%+; median underestimate ~11%; only 18% of comparisons within ±10% vs DLW — emit with heteroscedastic error, never as precise value | EVD-METB-008 (E5) |
| Stress/arousal score | Classifier output = probability of lab-stressor-like arousal; motion-corrupted; no ecological validity (lab AUC claims do not transfer) | WEARABLE AC5 (E4 consumer) |
| Illness/infection deviation flag | Passive-only AUC ~0.70; +symptoms 0.80; RHR alone 0.52 (≈chance); high false-alarm at low prevalence; non-specific cause | WEARABLE S4 (DETECT/Stanford/meta) |
| SpO2 (where profile includes it) | Bias 0–1%, LoA ±4–6%; bias inflation below 90% (device-dependent up to 13%); skin-tone positive-bias term (sampled magnitude); motion/low-perfusion voids | EVD-SENS-001; CONTRADICTION Target 8 |
| Cuffless-BP trend (research profile only) | Calibration-anchored trend; bias toward calibration point; error growth ∝ distance; drift ~0.02 mmHg/day after day 15; occasional ISO-failing device draws (SD up to 22.5 mmHg). **Cannot certify absence of OH** (POTS criteria exclude BP drop) | WEARABLE C3 chain |
| Orthostatic ΔHR event feature | IMU transition detection + ΔHR over 10 min; free-living group overlap huge (hEDS 8.15–27.71 vs controls 6.60–27.02 bpm) — naive detector specificity poor | EVD-POTS-018 (E2) |

**Broken-sensor regimes are mandatory content:** POTS tachycardia decouples HR-intensity; ME/CFS pacing invalidates activity-EE links; dysautonomia violates PRV≈HRV during orthostatic transients (WEARABLE design rule 2).

---

## 4. METADATA SCHEMA (per record; full field types)

Every record (participant × recording day) ships with a JSON metadata document:

| Field | Type | Description |
|---|---|---|
| `record_id` | uuid4 string | unique record identifier |
| `participant_id` | string (pseudonymous) | links days within participant |
| `simulation_seed` | uint64 | full RNG seed (bit-reproducibility, engine precedent) |
| `ocpe_model_version` | semver string | engine code version |
| `code_sha256` | hex string | SHA-256 of engine source bundle |
| `kb_sha256` | hex string | SHA-256 of knowledge-base YAML bundle |
| `evidence_version` | string | EVIDENCE_REGISTRY.yaml version + SHA-256 |
| `sensor_profile` | enum | §2.1 profile id |
| `phenotypes` | array[enum] | composable phenotype set (§1.6) with per-phenotype `expression_weight` float ∈[0,1] |
| `severity` | float | continuous functional capacity + optional `severity_label` discretization |
| `demographics` | object | `age_years` float, `sex` enum, `height_cm`, `weight_kg`, `bmi`, `lean_mass_kg` (nullable), `fitzpatrick` enum I–VI (drives sampled skin-tone term), `menstrual_tracking` bool |
| `medications` | array[object] | `{class: enum(beta_blocker|ivabradine|midodrine|fludrocortisone|ssri|steroid|levodopa|stimulant), dose_class: low|standard|high, active: bool}` — mask effects per §0.2 |
| `comorbidities` | array[enum] | sampled per §5.3 joint model |
| `recording` | object | `start_ts` ISO-8601 UTC, `duration_s` int, `timezone`, `season` (seasonal RHR ±1 bpm sinusoid, EVD-POP-001 context), `device_firmware` string, `sampling_rates` map per channel |
| `events` | array[object] | §1.6 event list with `{type, t_start, t_end, params}` |
| `ground_truth` | object | references to latent trajectory arrays (§1); `includes_pem_label: bool` — PEM labels exist here ONLY, flagged `evidence: E0-E2, no validated detector` |
| `quality` | object | per-channel usable fraction, non-wear fraction, streaming loss fraction realized |
| `provenance` | object | `generation_pipeline` string, `parameter_draw_id` string (which population draw), `perturbations_applied` array with per-perturbation `{id, tier: A–D, registry_refs: [claim_ids], canonical|experimental}`, `honesty_flags` array (e.g., `neuropathic_pots_unvalidated_xfail`, `pem_physiology_speculative`) |
| `validation_split` | enum | `train|val|test` assigned at **participant level** (never day-level leakage) |
| `schema_version` | semver | this specification's version |

---

## 5. POPULATION DESIGN

### 5.1 Cohort sizes (first release)
| Cohort | n (participants) | Days/participant | Rationale |
|---|---|---|---|
| Healthy reference | 2,000 | 14 | Must sit inside Autonomic Aging (n=1,121) + Quer (n=92,457) + Lifelines (n=84,772) envelopes before any disease perturbation is judged (INDEPENDENT_REVIEW Criterion 5; VALIDATION ladder #5) |
| POTS | 800 | 14 | Demographic/severity recipes below; mixture structure needs n for tails |
| ME/CFS | 600 | 21 (multi-day needed for PEM kernels) | Severity-graded; PEM lag requires ≥2–3 wk |
| Long COVID | 600 | 21 | Trajectory heterogeneity (EVD-LCOV-002) |
| hEDS/HSD | 300 | 14 | Comorbidity-hub cohort |
| Autoimmune (RA/IBD/SLE) | 400 | 28 (flare capture) | Flare events rare; longer windows |
| Metabolic (T2DM) | 300 | 14 | EUROBAVAR/diabetes-tilt anchors |
| Neurological (PD/iRBD/OSA/anxiety/migraine) | 400 | 14 | CORE modules from NEURO dossier |
| **Total** | **~5,400** | ~90,000 participant-days | |

### 5.2 Demographic sampling recipes (POPULATION §H)
- **Healthy:** age ~census-matched uniform 18–75; sex 50/50; marginals per POPULATION §A conditioned on age/sex; latent factor structure per §G (6 factors: autonomic/vagal setpoint, cardiorespiratory fitness, body size, hemodynamic/vascular aging, circadian/sleep regularity, optional sympathetic/inflammatory) with **loading uncertainty ±50% and copula sensitivity at r=0** (CONTRADICTION Target 10 — factor structure is theory-driven E0, never empirical).
- **POTS:** female fraction 0.85–0.94; onset age = mixture (point mass/lognormal mode 14 + broad adult component, median 17, IQR 13–28; 47% adult-onset); present age = onset + duration; severity continuous with ~25% disabled tail; subtype axes per EVD-POTS-003 joint distribution (sampled, E0 weights caveat); medications BB/ivabradine/midodrine/fludrocortisone from study-arm frequencies as provisional priors (no population prevalence exists — AUDIT gap 12) (EVD-POP-006).
- **ME/CFS:** female ~0.8 (78–86%); bimodal onset N(16.0, 4.3²) + N(36.6, 10.5²), early:late ≈ 1:1.5; severity continuous with steps anchors (EVD-MECFS-002); duration mean 12±9 y; early onset OR 2.15 for severe (EVD-POP-006 context).
- **Long COVID:** ~75% female, mean age ~53 (or ~40 for POTS-LC subset); POTS penetrance as **graded latent axis 20–80% by ascertainment** (EVD-LCOV-004, vindicated by audit); ME/CFS screen+ 0.58.
- **All cohorts:** day-level within-person noise from POPULATION §C (RHR day-to-day CV ~4.6%, 5-day ICC 0.87; raw RMSSD CV ~0.37 unstandardized, lnRMSSD CV 3–13% standardized morning; sleep duration within-person SD median 0:30; steps day-to-day MAPE ~13%); seasonal RHR ±1 bpm sinusoid (peak early Jan); menstrual modulators where applicable.

### 5.3 Comorbidity joint sampling
Copula/log-linear model on {POTS, hEDS/HSD, ME/CFS, long COVID, autoimmune} with marginals and pairwise rates: hEDS-in-POTS 0.31 (prospective 2017 criteria) / 0.12–0.22 chart reviews; POTS-in-hEDS 0.175–0.927 (registry upper bound biased); hEDS-in-ME/CFS 0.12–0.19; ME/CFS-in-LC 0.58 screen+; POTS-in-LC 0.31 symptomatic / 0.07 unselected clinic (EVD-POP-007; EVD-POTS-020: ME/CFS ~21%, autoimmune ~16%, mast cell ~9% in POTS).
- **Ascertainment down-weighting mandatory:** all pairwise rates are clinic/self-report inflated → multiply by 0.3–0.5× for population-representative sampling, OR declare the synthetic cohort explicitly clinic-like and record `cohort_frame: clinic` in metadata (EVD-POP-007 guidance).
- Third-order interactions: no evidence (E0) → pairwise-sufficient log-linear structure + sensitivity analysis.

### 5.4 Healthy controls with realistic tails (CONTRADICTION Target 1 — REFUTED ">95% below 30 bpm")
Protocol-conditioned healthy orthostatic ΔHR model (the "single most consequential calibration choice"):
| Protocol | Healthy 10-min ΔHR model | >30 bpm exceedance in healthy |
|---|---|---|
| 10-min active stand, ≥1 h supine pre-rest, fasting, morning (lab) | ~+23±3 to +25±3 bpm (Plash n=28) | ~33% (specificity 67%) |
| NASA Lean Test (passive muscle-pump-removed stand) | higher | 33% meet ΔHR>30; 49% POTS-or-OH (Lee 2020) |
| 10-min tilt 60–70° | ~+34±8 bpm | ~60% (specificity 40%) |
| 30-min tilt | ~+40±4 bpm | ~80% (specificity 20%) |
| Casual short-notice free-living stand | ~+10–15 bpm | <5% |
| Adolescents (12–19 y) | 95th pct 41–48 bpm | 42% exceed 30 on 5-min tilt → pediatric criterion ≥40 bpm |
- Diurnal modulation: orthostatic tachycardia larger in morning in POTS **and** controls (EVD-POTS-002) — time-of-day is a modeled covariate.
- Initial transient (peak ~15–30 s) and sustained (1–10 min) responses are **separate parameter sets** (INDEPENDENT_REVIEW Criterion 7 fix; initial BP dip nadir ~10 s, recovery 20–30 s; EVD-HLTH-004).
- Healthy stand-event ΔHR event-to-event variability: provisional within-person CV 15–25% (no reliability study exists — POPULATION §F gap; flagged `provisional`).

---

## 6. TEMPORAL DESIGN (multi-timescale architecture)

Six-layer stack per TEMPORAL_MODEL_EVIDENCE.md §9 (data flow slow→fast only; fast→slow only via aggregated exertion load):

```
L1 SLOW LATENT MODULATORS (1/day–1/min): OU baseline drift B(t) τ≈3–7 d;
   adaptation F(t) τ≈2–6 wk (training RMSSD SMD 0.6–0.9 over 8–12 wk, EVD-TEMP-009);
   menstrual phase θ(t) 28.6±3.8 d (EVD-TEMP-008); illness/flare episode kernels;
   PEM delayed kernel on exertion history (symptom channel: delay-to-peak 24–48 h,
   recovery right-skewed mean 12.7 d range 1–64 d — EVD-MECFS-008/009;
   physiological channel: slowed-recovery hours-scale, delayed second wave E0-optional —
   CONTRADICTION Target 5)
L2 CIRCADIAN (1/min): cosinor carrier 24 h + 12 h harmonic (non-sinusoidal night trough);
   two-process S+C sleep/wake gating; masking terms on observed HR/temp (EVD-TEMP-006)
L3 EVENT LAYER (minutes–hours): meals/stress/exercise bouts → gamma kernels
   k(τ)=(τ/τ_pk)·exp(1−τ/τ_pk), rise 10–30 min, decay 1–3 h; postprandial HR +6±3 bpm
   mixed-meal default with meal-size scaling up to +10–20 (EVD-METB-005 + audit B3.1);
   postprandial HF-HRV dip 1–2 h
L4 FAST ODE CORE (10–100 Hz during transients only): ~5-compartment cardiovascular ODE +
   baroreflex Hill control (Geddes-scale, ~20–30 params — NOT Heldt/Ursino full models);
   posture/exercise inputs; 0.1 Hz Mayer oscillations emerge from feedback delay
   (EVD-TEMP-003); steady-state algebraic map outside transients
L5 BEAT GENERATOR (event-driven): IPFM + 1/f fractal noise + Bernoulli ectopy;
   m0, C_S, C_V set by L1–L4 (EVD-TEMP-001/011)
L6 MEASUREMENT MODEL (sensor rate): McSharry ECG / PPG from beat times; IMU-gated
   artifact injection; device sampling/dropout (§2)
```

**Granularity rule:** integrate beat core event-driven; ODE core only during active transients; closed-form sampling for circadian/OU/kernels; derive (don't simulate) waveforms, sleep stages (two-process state + Markov stage machine), symptom scores.

**Recording lengths:** free-living records 14–28 days/participant (cohort-dependent §5.1) at profile sampling rates; embedded protocol segments (lab days) at research-grade rates: tilt/active-stand 10 min upright + supine baseline; graded exercise to max; 2-day CPET pair (ME/CFS/LC cohorts, contested-signature flags per Target 4); TSST-like stress protocol; sleep every night.

**Event scheduling:** meals 3/day ± jitter (carb fraction sampled); exercise bouts per cohort activity level with pacing policy for ME/CFS/LC (boom-bust day-to-day variability; EVD-MECFS-011: cohort mean 5,701±2,670 steps/d with high variance); orthostatic events on every stand (IMU-detected); scheduled stand-tests 2–3/day in dysautonomia cohorts; PEM triggers when exertion exceeds capacity-state threshold (severity-dependent); illness episodes at background rates; menstrual phase continuous; medication dosing schedules create mask windows.

---

## 7. PROVENANCE & GOVERNANCE HOOKS
- Every parameter in the generated population carries `{registry_refs, E-level (normalized), tier A–D, provenance: human-experimental|human-observational|meta-analysis|in-silico|machine-fitted|engineering-judgment}` per EVIDENCE_AUDIT_NOTES.md §e recommendation (replace conflated tier/level axes).
- Tier-D parameters are **inert by default** in canonical generation (repo honesty-by-default preserved); experimental draws are labeled `mode: EXPERIMENTAL`.
- Single-source parameters (Moore PEM, van Campen CBF, RA Forecast offsets, Sports Med 2026 recovery kernel) carry `single_source: true` tags (INDEPENDENT_REVIEW §1.4).
- No canonical parameter without E-level + provenance tag; no E0/E1 value in canonical mode (audit CI rule).
- Dataset manifest = JSON-LD manifest referencing this spec, registry SHA-256, engine SHA-256, and per-cohort parameter-draw manifests.

*End of specification. Validation obligations are defined in SYNTHETIC_TO_REAL_BENCHMARK.md; no utility claim is made by this document.*
