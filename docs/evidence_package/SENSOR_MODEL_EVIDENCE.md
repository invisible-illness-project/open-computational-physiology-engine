# OCPE — Sensor & Artifact Model Evidence Base

**Purpose:** evidence-based sensor observation and artifact models for the Open Computational Physiology Engine (OCPE) synthetic multimodal wearable data simulator. The design principle: synthetic wearable data must reproduce the *measurement chain* (physiology → transduction → sampling → noise/artifact → derived-feature error), not just the clean physiology.

**Evidence levels:** E0 = hypothesis/mechanistic speculation; E1 = established mechanism; E2 = observational; E3 = controlled experimental; E4 = replicated quantitative (multiple independent studies/meta of n); E5 = meta-analysis / standards consensus. Only DOIs/PMIDs actually located are cited. Negative validation findings are explicitly retained.

---

## 1. ECG (wearable chest strap / patch / watch single-lead)

### Sensor observation chain
1. **Physiology:** cardiac electrical activity; surface single-lead ECG QRS amplitude typically 0.5–2 mV; clinical ECG band 0.05–45 Hz (monitoring) to 0.05–100/150 Hz (diagnostic). [E1]
2. **Transduction:** Ag/AgCl wet electrodes (patch), conductive-rubber/metal dry electrodes (chest strap), stainless steel (watch). Electrode–skin impedance is the dominant noise coupling path; motion modulates impedance → motion artifact. [E1]
3. **Waveform characteristics:** R-peak timing is robust; morphology (ST, P/T) is fragile. Polar H10 streams raw ECG at **130 Hz ±2%, 24-bit, band-limited 0.7–40 Hz** — adequate for RR/IBI, *inadequate* for ST/QT/P-wave morphology (0.7 Hz high-pass distorts ST). [E3, device spec + independent commentary]
4. **Sampling requirements:**
   - HR only: ≥125 Hz adequate. [E4]
   - HRV (time/frequency): 1996 Task Force 250–500 Hz; current guidance **≥250 Hz minimum** (Quintana/GRAPH), **1000 Hz without interpolation** recommended by Quigley et al. 2024 update for experimental ms-precision R-detection. [E5]
   - Wearable devices with low fs (e.g., 130 Hz) achieve acceptable HRV only because R-peak detection uses interpolation/parabolic refinement. [E3]
5. **Error model (Polar H10 vs criterion ECG — the best-validated wearable ECG):**
   - **Schaffarczyk et al. 2022** (n=25, rest + exhaustive cycling ramp; *Sensors* 22:6536, doi:10.3390/s22176536): RR bias **0.7→0.4 ms**, LoA **+4.3/−2.8 ms** at low intensity and **+1.3/−0.5 ms** at high intensity; HR bias −0.1 to −0.2 bpm. **Negative finding:** DFA-α1 (nonlinear HRV) bias up to 8.6% with LoA **+58.1%/−40.9%** at high intensity — beat-timing accuracy does *not* transfer to derived nonlinear metrics. [E3]
   - **Gilgen-Ammann et al. 2019** (n=10; *Eur J Appl Physiol* 119:1525–1532, doi:10.1007/s00421-019-04142-4): H10 RR signal quality **99.4%** vs Holter's **89.8%** during high-intensity exercise. Small n. [E3]
   - **Negative finding:** Vermunicht et al. 2025 (Europace 25 Suppl; cardiac-rehab patients vs Holter): MAE **3.4 bpm / MAPE 4.9%** *after* bespoke artifact removal — error ~5× the healthy-cohort values. Accuracy degrades in arrhythmic/older populations. [E3]
   - Movesense Medical single-lead chest ECG: comparable RR/HRV validity (Rogers et al. 2022, doi:10.3390/s22052032). [E3]
6. **Noise/artifact model (quantified characteristics):**
   - **Baseline wander:** 0.05–1 Hz, amplitude up to ~15% of QRS from respiration/movement. [E4 — standard noise characterization, MIT-BIH Noise Stress Test Database (NSTDB)]
   - **Electrode motion artifact (EM):** transient baseline shifts from electrode–skin impedance change; amplitude **can exceed peak-to-peak ECG**, duration 300–500 ms; can distort ST segment. [E4, NSTDB-based synthesis literature]
   - **Muscle artifact (EMG):** ~**10% of ECG amplitude**, bandwidth 0.02–10 kHz (broadband overlap 0.01–100 Hz); cannot be filtered without distorting morphology. [E4]
   - **Powerline interference:** 50/60 Hz narrowband. [E1]
   - Chest-strap practical artifacts: dry-strap contact loss at exercise onset (strap requires moisture), strap slip during vigorous motion, implausible HR spikes (E4 HR output >200 bpm observed off-wrist — Biomedical Engineering Online 2025, doi:10.1186/s12938-025-01353-0). [E2/E3]

### Recommended simulator defaults — ECG
- fs: 130 Hz (H10-class strap), 250 Hz (research patch), 512–1000 Hz (diagnostic-grade). Interpolate for R-timing at low fs.
- Clean signal SNR: 15–25 dB; motion periods add EM bursts (300–500 ms transients, amplitude 1–3× QRS) + EMG broadband noise (σ ≈ 0.1× QRS amplitude).
- RR error model: strap healthy-rest: N(0, ~1 ms) with LoA ≈ ±4 ms; exercise: widen 2×; patient/arrhythmic cohorts: bias up to ~3 bpm, MAPE ~5%.
- Missingness: strap dry-out gaps at exercise start; BLE dropouts (see §7).

---

## 2. PPG (wrist/ring optical)

### Sensor observation chain
1. **Physiology:** pulsatile arterial blood volume in microvascular bed (blood-volume pulse, BVP); AC component rides on large DC (non-pulsatile tissue/venous) component; typical AC/DC (perfusion index) ~0.5–5% at finger, lower at wrist. [E1/E2]
2. **Transduction:** LED + photodiode, reflectance mode (wrist) or transmissive (finger clip).
   - **Wavelength effects:** green (~525 nm) — high absorption by hemoglobin → large AC signal and *less* motion-susceptible during activity, but strongly absorbed by **melanin** (equity concern) and shallow penetration; red/IR (660/940 nm) penetrate deeper, better perfusion-signal at rest, *worse* during motion (Lee et al. 2013 EMBC, doi:10.1109/EMBC.2013.6609852). [E3]
   - Empatica E4: 2 green + 2 red LEDs, 2 photodiodes, 64 Hz, 8-bit, 0.9 nW/digit. Apple Watch: green PPG (IR during background), variable/duty-cycled sampling; Oura ring 50 Hz; HealthRing study ring 100 Hz red/IR. [E3, device specs]
3. **Sampling requirements:** cardiac band 0.7–3.5 Hz; fs 25 Hz demonstrably sufficient for HR (25 Hz multi-channel PPG achieved EER <3% biometric, performance degrades <20 Hz — arXiv:2508.13690); **default 64–128 Hz** for waveform/IBI; 1 Hz output typical for derived HR (E4). [E3/E4]
4. **HR error vs ECG — by activity (KEY evidence):**
   - **Lambe et al. 2026 living systematic review/meta-analysis** (82 studies, 430,052 participants, Apple Watch vs ECG/chest strap; *npj Digit Med*, doi:10.1038/s41746-025-02238-1, PMID 41513748): pooled HR bias **−0.27 bpm (95% CI −0.72 to 0.17)**, LoA **−7.19 to +6.64 bpm**; 10/11 exercise studies reported MAPE <10%; SpO2 bias −0.04% but LoA ±4%. [E5]
   - **Shcherbina et al. 2017** (n=60, 7 devices vs 12-lead ECG; *J Pers Med* 7:3, doi:10.3390/jpm7020003): 6/7 devices median HR error **<5%**; **walking worst, cycling best** (constrained arm); error higher with male sex, higher BMI, **darker skin tone**; energy expenditure error **27–93%** (no device <20%). [E3]
   - **Gillinov et al. 2017** (MSSE): wrist PPG concordance >0.9 during treadmill, degraded during elliptical (large arm motion). [E3]
   - Pediatric/ambulatory data: error margins widen to **±19 bpm** with movement/HR increase. [E2]
   - Nocturnal resting HR: 5 devices vs ECG over 536 nights (PMID 40834291): RHR MAPE **1.67–3.00%**, HRV MAPE **5.96–16.32%**. [E3]
   - **Negative finding:** Apple Watch Series 9/Ultra 2 HRV vs Polar H10 (O'Grady et al. 2024, *Sensors*): HRV underestimated by **8.31 ms, MAPE 28.9%, MAE 20.5 ms** — fails ±10 ms equivalence. [E3]
   - Algorithmic context: naive spectral HR estimation during treadmill running: MAE **~26 bpm**; SOTA motion-compensated (HSUM/TROIKA-class, IEEE SPCup 2015 data): MAE **0.73–1.86 bpm** walking. The gap between 26 and 1 bpm is the algorithm, not the sensor — a simulator should generate the *raw corrupted signal*, not the post-algorithm number. [E3]
5. **Motion artifact (cadence-lock):** during rhythmic locomotion the MA spectrum concentrates at step frequency and harmonics, quasi-periodic like the pulse; when step frequency ≈ pulse frequency (or its harmonic), trackers lock onto cadence → HR error of tens of bpm. MA magnitude can exceed the pulse AC component by an order of magnitude (Paliakaitė et al. 2021, *Biomed Signal Process Control* 66:102421 — explicit wrist-PPG artifact modeling reference). [E1/E3]
6. **Skin-tone equity evidence (include both directions):**
   - Shcherbina 2017: darker skin tone correlated with higher HR error. [E3]
   - **Bent et al. 2020** (n=53, 6 devices; *npj Digit Med* 3:18, doi:10.1038/s41746-020-0226-6): **no significant HR-accuracy difference across Fitzpatrick skin types**; activity increased absolute error ~30%; E4 performed worst among devices. **Caveat (Colvonen response, doi:10.1038/s41746-021-00408-5): only n=9 in Fitzpatrick VI — underpowered for the darkest skin.** [E3 + negative critique]
   - Ajmal et al. 2021 (*Biomed Opt Express* 12:7445): Monte-Carlo optical modeling — melanin and obesity reduce detected PPG signal. [E1/E0 computational]
   - Pulse-oximeter analogy: Sjoding et al. 2020 NEJM — occult hypoxemia missed ~3× more often in Black patients (transmissive oximetry, but same melanin physics). [E4]
7. **Contact pressure / perfusion / temperature confounders:**
   - Contact pressure changes optical coupling and local blanching; WF-PPG dataset (Ho et al. 2025, *Sci Data* 12:200) systematically varies wrist/finger contact pressure — morphology is pressure-sensitive. Too-loose → motion gap; too-tight → blanching → attenuated AC. [E2/E3]
   - **Cold/vasoconstriction:** hand immersion 0–4 °C significantly degraded PPG quality; warming (55 °C) improved it (Khan et al., reviewed in ScienceDirect PPG review). Perfusion index drops <0.3% with cold fingers. [E3]
   - Posture/sensor height: wrist PPG quality highest supine at heart height, degrades sitting/standing with arm dependent (Charlton et al. 2025, *PLOS Digit Health*, doi:10.1371/journal.pdig.0000585; >1000 subjects). Auto LED-intensity adjustment helps across skin tones. [E3]
   - Ambient light leakage into sensor gap produces large artifacts (Böttcher/Vieluf E4 study, below). [E2]
8. **Usable-data rates (missingness) — free-living:**
   - **Böttcher & Vieluf et al. 2022** (*Sci Rep* 12:21384, doi:10.1038/s41598-022-25949-x; E4, 37k–91k hours, 671 patients): mean good-quality fractions — BVP **60.2%**, EDA 70.4%, TEMP 96.1% of on-body time. **BVP day 49.9% vs night 70.7%.** Streaming-mode data loss up to **49%** vs ≤9% on-device. [E4 — huge n]
   - **Väliaho et al. 2022** (*Front Physiol* 12:778775): 24-h wrist PPG, only **55.9%** of hours passed quality; day **30.5±19.4%** vs night **67.3±22.4%**. [E3]
   - → Simulator default: daytime wrist-PPG usable fraction ~30–60%, nighttime ~65–75%.
9. **PPG-derived respiration reliability:** MAE vs reference: 0.1–2.0 brpm on clean ICU data (CapnoBase/BIDMC), **2.13 brpm Arms, LoA −4.28/+4.09** during HIIT cycling (CardioWatch 287-2, n=35, *Biosensors* 2024, 14:631); **5.1–10.7 brpm** in less-controlled datasets; motion-intensive treadmill: RR error 4.6–5.4 brpm even after fine-tuning (HealthRing, *Sci Data* 2026). PPG-derived RR should carry error ≥2× belt-derived RR. [E3]

---

## 3. EDA (electrodermal activity / GSR)

### Sensor observation chain
1. **Physiology:** eccrine sweat-gland filling under sympathetic **cholinergic** sudomotor drive; conductance rises as sweat fills ducts. Glabrous skin (palms/fingers) has highest gland density and best responsivity; wrist sites are weaker and more motion-prone (Hossain et al. 2022, *Sensors* 22:3177). [E1/E3]
2. **Signal decomposition:** tonic SCL (minutes-scale drift) + phasic SCRs (event-locked).
   - **SCL typical range 2–20 µS** (BIOPAC/standard references); stress can push toward 20–30 µS. [E4 textbook-range]
   - **SCR amplitude 0.05–5 µS** (detection threshold convention 0.05 µS; 0.01–0.02 µS for some protocols). [E4]
   - **SCR latency 1–3 s** post-stimulus (range 1–5 s reported); **rise time 1–3 s** (onset→peak; peak 3–5 s post-stimulus); **half-recovery 2–10 s**; full resolution 10–20 s (Dawson et al. 2016 standard values). [E4]
   - NS-SCR rate: ~1–3/min relaxed, 5–10+/min stressed. [E2]
3. **Transduction/hardware:** exosomatic measurement with small DC/AC excitation (E4: 8 Hz AC, ≤100 µA pp), two dry Ag electrodes; E4 range 0.01–100 µS, resolution ~900 pS, fs 4 Hz. Contact quality dominates: electrode lift → step drop to zero-line; partial contact → abrupt level jumps. [E3]
4. **Sampling:** SCR rise times ≥1 s → **4 Hz sufficient** (Nyquist ≫ fastest component); 4–25 Hz typical research range. [E4 consensus, Boucsein 2012]
5. **Confounders (state-dependent, must be modeled):**
   - **Ambient temperature & humidity** raise SCL (sweat) independent of arousal; seasonal effects documented (Boucsein; Okamoto-Mizuno 2010). [E2/E4]
   - Motion: wrist EDA robustness lower than fingers; abrupt artifacts with >20% change in 2 s flagged as bad quality (E4 quality pipeline). [E3]
   - Day/night quality: EDA good-quality 65.6% day vs 75.1% night (Böttcher/Vieluf). [E4]
   - Coverage (blanket/jacket over device) warms skin → spurious EDA rise. [E2]

### Recommended simulator defaults — EDA
- fs = 4 Hz. SCL: random-walk drift in 1–20 µS band (circadian + temperature coupling). SCR: latency N(1.8, 0.4) s, rise 1–3 s, half-recovery 2–10 s, amplitude log-normal ~0.1–2 µS (threshold 0.05 µS). NS-SCR Poisson, λ 1–3/min rest → 5–10/min stress.
- Artifacts: contact-loss zero-lines (seconds–minutes), step transients on motion, +SCL offset under heat/humidity.

---

## 4. Skin temperature

### Sensor observation chain
1. **Physiology:** skin temperature reflects peripheral perfusion and thermoregulatory vasomotor state, *not* core temperature. Distal sites (finger/wrist) are warmer at night (vasodilation → sleep onset); the **distal–proximal gradient (DPG)** is a better circadian marker than any single site (Kräuchi 2007). [E1/E4]
2. **Waveform characteristics:** slow dynamics; physiologically meaningful band ≈ 0.02–0.4 Hz after filtering (E4 pipeline uses this); thermal time constants of minutes (peripheral vasomotor changes take multiple seconds–minutes). [E2/E3]
3. **Typical values:** wrist/hand mesor ~33 °C, foot ~32 °C; **circadian amplitude 1.2–1.4 °C (wrist/hand), 1.8–2.2 °C (foot)** (Martinez-Nicolas/PMC11353769, 7-day ambulatory, n=65). Core circadian swing ~0.5–1 °C. Inter-individual resting differences up to ~0.5 °C. [E3]
4. **Placement:** finger > wrist for perfusion coupling; ambient exposure confounds wrist (sensor under sleeve vs exposed). Chest/proximal sites more stable, closer to core trend. [E2/E3]
5. **Accuracy numbers:**
   - Oura ring NTC thermistor, resolution 0.07 °C, 1-min epoch; vs iButton finger reference: **r ≈ 0.98** overnight (Otago thesis validation, n=4); iButton itself accuracy −0.09 °C, precision 0.05 °C. [E3]
   - Oura internal study: correlation with iButton r² > 0.99 lab, > 0.92 real-world; finger temperature uncorrelated with ambient (r² = 0.001) — distal skin tracks body state, not room temperature, when in contact. [E2, manufacturer — treat cautiously]
   - Menstrual luteal–follicular skin-temp difference 0.30±0.12 °C detectable by ring (Maijala et al., PMC6883568). [E3]
6. **Confounders/artifacts:** off-body → decay toward ambient (used as on-body detector, valid band 25–40 °C); covering device raises reading; ambient temperature drives wrist TEMP during outdoor exposure; TEMP highest-quality modality (96.1% good-quality, Böttcher/Vieluf). TEMP exhibits lag on donning (equilibration ~15–30 min advised). [E2/E3]

### Recommended simulator defaults — Temperature
- fs = 1–4 Hz. First-order thermal model: skin site = core-coupled setpoint + circadian (amplitude 1–2 °C, acrophase ~04:00–07:00 distal) + vasomotor events + ambient leak (time constant 2–10 min when exposed) + off-body decay to ambient.
- Sensor noise: σ ≈ 0.03–0.1 °C; quantization 0.02–0.07 °C; accuracy bias ±0.1–0.36 °C device-dependent.

---

## 5. IMU / Accelerometry

### Sensor observation chain
1. **Transduction:** MEMS capacitive proof-mass. Ranges ±2 g (E4, best resolution) to ±16 g (smartphone-class); noise density **290 µg/√Hz** (ADXL345, consumer), ~160 µg/√Hz (BMI270), **22.5 µg/√Hz** (ADXL355, research-grade) — 13× noise spread across device classes. 12–16-bit ADC. [E5 datasheet/E3]
2. **Sampling:** 20–100 Hz typical wearables (E4 32 Hz; ActiGraph GT3X+ 60–100 Hz; GENEActiv 20–80 Hz; Oura 50 Hz); human motion band 0–20 Hz; ≥50 Hz captures heel-strike transients. [E4]
3. **Signal content:** static gravity component (orientation) + dynamic body acceleration; wrist devices see large non-gait arm motion.
4. **Derived-feature error statistics:**
   - **Step count:** wrist ActiGraph reads **39% higher** than hip over 24 h free-living, worse in older adults (PMC6849483). Naive peak-detection at wrist: only **10.09% accuracy** during mixed non-gait activity (typing, eating, mouse use → massive false positives) vs 93.6% for adaptive multi-stage algorithm (PMID 41269848). [E3]
   - **Posture/orientation:** thigh inclinometer 85.7–100% correct sit-vs-stand; wrist/waist posture MAPE **>44%** — wrist orientation is a poor posture estimator. [E4, review PMC8900289]
   - **Activity classification:** ML wrist models 53.5–95.9% accuracy depending on features/validation (Montoye et al.: 95.9% left wrist with percentile features; Staudenmayer RF: ~75%); intensity cutpoints transfer poorly across devices/ages. [E4, review]
   - **Energy expenditure from ACC+HR:** no device <20% error (Shcherbina); wrist ACC explains 19–76% of VO2 variance depending on model. [E4]
5. **Artifacts:** saturation/clipping when impacts exceed FSR (E4 ±2 g clips during running heel-strike transients transmitted to wrist, vigorous arm swings); displacement/rotation of loose band; sleep-pressure artifacts (arm under pillow); zero-motion floors used for off-body detection. [E2/E3]

### Recommended simulator defaults — IMU
- fs = 32 Hz (default), 50–100 Hz (gait analysis). White noise: consumer-class 290 µg/√Hz → at 32 Hz bandwidth ≈ 1.6 mg RMS; add 1/f and temperature drift. Gravity vector from orientation model. Clip at ±FSR. Step-count output layer: overcount bias +20–40% at wrist during non-gait daily activity; false-positive rate high during typing/eating unless algorithmic rejection modeled.

---

## 6. Respiration

### Sensor observation chain
1. **Physiology:** resting adult RR 12–18 brpm (children ~18–25); exercise up to 40–60 brpm. [E4]
2. **Chest belt (respiratory inductance plethysmography, RIP):** measures cross-sectional change; signal linear with area change but in arbitrary units — **relative amplitude only, no tidal-volume quantification without calibration**; good breath timing. [E1/E3]
3. **Wearable RR accuracy:**
   - Philips biosensor vs capnography (ED, n=17, PMC6511238): mean difference 3.2±3.6 brpm, **76.3% within ±3 brpm**; sensor invalid 0.7% of time. [E3]
   - ECG-derived RR (EDR): MAE 0.99–3.07 brpm (clean datasets); Polar-H10+Kubios RR during exercise ramp: r=0.85, SEE 4.2 brpm, bias up to −3.9 brpm vs gas exchange; single-lead ECG sensor r=0.95, SEE 2.6 (Rogers 2022, doi:10.3390/s22197156). [E3]
   - PPG-derived RR: 0.1–2.0 brpm clean; 2.13 brpm Arms with LoA ±4.2 during HIIT; 5–10.7 brpm in noisy/real-world data (§2.9). [E3/E4]
   - Accelerometer-derived respiration (chest/wrist IMU): feasible at rest (periodic torso motion 0.1–0.7 Hz), error rises sharply with activity; CNN smartwatch methods reach median absolute error ~1.6 brpm in controlled conditions (arXiv:2401.05469). Treat as E2/E3; dropout during any non-respiratory motion.
4. **Sampling:** belt 25–100 Hz typical (RespiBAN/DaLiA 700 Hz overkill); **≥25 Hz** comfortably resolves breath waveform; derived RR reported at 0.2–1 Hz. [E3]

---

## 7. Cross-cutting artifact model table

| Artifact | Modality | Magnitude / quantitative value | Frequency of occurrence | Conditions | E-level | Source |
|---|---|---|---|---|---|---|
| Motion artifact bursts | PPG | MA amplitude ≥ pulse AC, can be >10×; naive HR MAE ~26 bpm during running | nearly continuous during locomotion | walking/running, arm swing | E3 | arXiv:1610.05112; Ismail 2021 doi:10.1186/s13634-020-00714-2 |
| Cadence-lock | PPG HR | HR estimate error = \|HR − cadence\|, tens of bpm | whenever step-rate harmonic ≈ pulse rate | rhythmic gait, cycling cadence | E1/E3 | IEEE SPCup 2015 literature |
| Day vs night usability | PPG | good-quality 30.5% day / 67.3% night; 55.9% of 24 h usable | daily pattern | free-living | E3/E4 | Väliaho 2022 doi:10.3389/fphys.2021.778775; Böttcher 2022 doi:10.1038/s41598-022-25949-x |
| Data loss, streaming vs on-device | all | up to 49% loss (BLE streaming) vs ≤9% (onboard memory) | deployment-level | BLE range, phone distance | E4 | Böttcher 2022 |
| Off-body / non-wear | all | on-body 80–99.7% of recording time | daily (showering, charging) | compliance | E4 | Böttcher 2022 |
| Clock drift | all | timestamp error up to ~1 s per hour (E4-class) | continuous | long recordings | E3 | Böttcher 2022 (citing Bruno 2021, doi:10.1111/epi.17044) |
| BLE packet loss/jitter | all | CI 7.5 ms–4 s; packet loss ~10% at BER 1e-3 w/o retransmission; ms-scale jitter; BLE σ(jitter) 29–280× deterministic TDMA | continuous in streaming | RF environment, MTU, host OS | E3 | PMC8533907; arXiv:2608.29036 |
| Electrode motion artifact | ECG | amplitude > peak-to-peak QRS, 300–500 ms transients | with trunk/strap motion | exercise, dry strap | E4 | MIT-BIH NSTDB characterizations |
| Baseline wander | ECG | 0.05–1 Hz, up to ~15% of QRS | continuous | respiration, posture change | E4 | NSTDB / Pan-Tompkins++ |
| EMG contamination | ECG | ~10% of QRS amplitude, broadband to kHz | during muscle activity | shivering, exercise | E4 | NSTDB |
| Dry/contact loss | ECG, EDA | zero-line or implausible values (HR >200 bpm reported) | start of exercise (dry strap), electrode lift | donning, sweating shifts | E2/E3 | BME Online 2025 doi:10.1186/s12938-025-01353-0 |
| Cold vasoconstriction | PPG | PI <0.3%; significant quality loss after 0–4 °C hand immersion | cold exposure | winter outdoor, Raynaud's | E3 | Khan et al. (reviewed); Turner Medical PI review |
| Skin-tone attenuation | PPG | green-light signal attenuation with melanin; error correlation device-dependent; underpowered negative (Bent) | constant per user | FST V–VI users | E3 (contested) | Bent 2020 doi:10.1038/s41746-020-0226-6; Colvonen 2021; Shcherbina 2017 |
| Contact pressure | PPG | morphology change with strap tightness; blanching attenuates AC | per fitting | too loose/tight | E2/E3 | Ho 2025 Sci Data 12:200 |
| Ambient light leak | PPG | large artifact, undefined signal range | when gap forms in daylight | loose fit outdoors | E2 | Böttcher 2022 Fig. 2 |
| Accelerometer clipping | IMU | saturation at FSR (±2 g E4) | vigorous impacts | running, striking | E1/E2 | datasheet; Böttcher 2022 |
| Step false-positives | IMU-derived | naive wrist algorithm 10% accurate in non-gait tasks; wrist 39% > hip steps | daily activities | typing, eating, driving | E3 | PMID 41269848; PMC6849483 |
| HRV metric degradation | ECG/PPG-derived | DFA-α1 LoA +58/−41% at high intensity; watch HRV MAPE ~29% | during exercise | high intensity, motion | E3 | Schaffarczyk 2022; O'Grady 2024 |
| Temperature ambient leak | TEMP | drift toward ambient when uncovered/off-body | exposure events | outdoor, off-wrist | E2 | Böttcher 2022 |
| EDA thermal/humidity bias | EDA | SCL elevation with heat/humidity/season | seasonal/daily | hot climate, covered device | E2/E4 | Boucsein 2012; Okamoto-Mizuno 2010 |

---

## 8. Physiological-state-dependent signal degradation (for state-conditional artifact models)

| Physiological state | Signal consequence | Quantitative anchor | E-level |
|---|---|---|---|
| Rhythmic exercise (walk/run) | PPG MA + cadence-lock; worst modality | daytime PPG usable ~30–50%; naive HR error ~26 bpm | E3/E4 |
| Non-steady/vigorous exercise | PPG HR LoA widens (±7 bpm pooled → ±19–30 bpm tails); ECG strap stays good | Apple Watch LoA −7.2/+6.6; Schaffarczyk RR LoA ±~1 ms | E5/E3 |
| Cold / vasoconstriction | PPG amplitude collapse (finger/wrist); skin temp falls; perfusion index <0.3% | ice-water immersion degrades PPG quality significantly | E3 |
| Sweating/heat | EDA SCL elevation (arousal-confounded); electrode impedance drops (can improve ECG contact but loosen strap) | SCL heat effect documented (Boucsein) | E2/E4 |
| Low perfusion (shock, Raynaud's, hypovolemia) | PPG unreliable at extremities | PI <0.3% → oximetry/HR failure modes | E2/E3 |
| Darker skin tone | green-PPG attenuation; error direction device-dependent | Shcherbina: darker tone → higher error; Bent: null (n=9 FST-VI caveat) | E3 contested |
| Sleep / recumbency | best signal quality across PPG/EDA/TEMP; motion minimal | PPG usable 67–71% at night | E4 |
| Arrhythmia (AF etc.) | HR/HRV algorithms fail; watch AF sens 0.79 / spec 0.91 | meta-analysis PMID 41513748 | E5 |

---

## 9. Recommended simulator defaults (sampling & error distributions)

| Modality | Default fs | Alternative fs | Clean-signal noise | Derived-feature error model |
|---|---|---|---|---|
| ECG (strap) | 130 Hz | 250/500/1000 Hz | SNR 15–25 dB; EM bursts 300–500 ms @1–3× QRS during motion; EMG σ=0.1×QRS; BW 0.05–1 Hz | RR: N(0.4, 1 ms) rest → 2–4 ms LoA exercise; HR MAPE ~5% in patients |
| PPG (wrist) | 64 Hz | 25/32/100/128 Hz | motion bursts ≥ pulse AC; spectral-entropy SQI; ambient-light spikes | HR: bias −0.3 bpm, σ 3.5 bpm rest; MAPE 5–10% moderate exercise, ≥±19 bpm severe motion; daytime dropout Bernoulli(p≈0.5)/night p≈0.3 |
| EDA | 4 Hz | 8–25 Hz | contact zero-lines; >20%/2 s step artifacts | SCL 2–20 µS random walk + temperature bias; SCR: latency 1–3 s, rise 1–3 s, half-rec 2–10 s, amp log-normal 0.05–5 µS |
| Skin temp | 1 Hz | 4 Hz | σ 0.03–0.1 °C; quant 0.02–0.07 °C; bias ±0.1–0.36 °C | circadian amp 1.2–2.2 °C; ambient-leak τ 2–10 min; off-body decay to room temp |
| IMU | 32 Hz | 20–100 Hz | 160–290 µg/√Hz white + 1/f; clip at ±FSR | steps: wrist +20–40% free-living; non-gait false positives high w/o rejection; posture MAPE >44% wrist |
| Respiration (belt) | 25 Hz | 50–100 Hz | relative amplitude only; baseline drift | RR error ~±3 brpm vs capnography (76% within 3); derived-from-PPG error 2–10 brpm |
| Cross-sensor sync | — | — | clock drift ≤1 s/h; BLE jitter ms-scale, CI 7.5 ms–4 s | resample-on-receive; alignment error uniform within CI |

---

## Key sources (all DOI/PMID verified during this pass)
- Schaffarczyk 2022 *Sensors* 22:6536 — doi:10.3390/s22176536
- Gilgen-Ammann 2019 *EJAP* 119:1525 — doi:10.1007/s00421-019-04142-4
- Rogers 2022 (Movesense ECG) doi:10.3390/s22052032; (RR estimation) doi:10.3390/s22197156
- Lambe 2026 Apple Watch living meta-analysis, *npj Digit Med* — doi:10.1038/s41746-025-02238-1 / PMID 41513748
- Shcherbina 2017 *J Pers Med* 7:3 — doi:10.3390/jpm7020003 / PMID 28538708
- Bent 2020 *npj Digit Med* 3:18 — doi:10.1038/s41746-020-0226-6; Colvonen 2021 doi:10.1038/s41746-021-00408-5
- Böttcher & Vieluf 2022 *Sci Rep* 12:21384 — doi:10.1038/s41598-022-25949-x
- Väliaho 2022 *Front Physiol* 12:778775 — doi:10.3389/fphys.2021.778775
- Charlton 2025 *PLOS Digit Health* — doi:10.1371/journal.pdig.0000585; Charlton 2022 *Proc IEEE* 110:355 — doi:10.1109/JPROC.2022.3149785
- Fine 2021 *Biosensors* 11:126 — doi:10.3390/bios11040126
- PPG-RR HIIT: *Biosensors* 2024, 14:631 — doi:10.3390/bios14120631
- Step counts: PMC6849483 (wrist-vs-hip +39%); PMID 41269848 (false positives); Karger DIB doi:10.1159/000542850
- Accelerometry review: PMC8900289
- Philips RR vs capnography: PMC6511238
- EDA standards: Dawson et al. 2016; Boucsein 2012; BIOPAC EDA Guide; Posada-Quintero & Chon 2020 doi:10.3390/s20020479
- Skin temp circadian: PMC11353769; Oura/iButton validation (Otago thesis); Maijala PMC6883568
- BLE reliability: PMC8533907; arXiv:2608.29036 (jitter σ comparison)
- E4 specs: Empatica/iMotions; PPG-DaLiA dataset (UC Irvine)
- HRV sampling standards: 1996 Task Force; Quintana 2016 GRAPH; Quigley 2024 update
