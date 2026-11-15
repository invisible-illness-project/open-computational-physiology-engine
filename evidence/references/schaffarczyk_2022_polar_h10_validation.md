# Validity of the Polar H10 Sensor for Heart Rate Variability Analysis during Resting State and Incremental Exercise

---
publication:
  title: "Validity of the Polar H10 Sensor for Heart Rate Variability Analysis during Resting State and Incremental Exercise in Recreational Men and Women"
  doi: "10.3390/s22176536"
  pmid: "36081005"
  pmcid: "PMC9459793"
  journal: "Sensors"
  year: 2022
  authors:
    - "Marcelle Schaffarczyk"
    - "Bruce Rogers"
    - "Rüdiger Reer"
    - "Thomas Gronwald"
  evidence_level: "Level 2 (Diagnostic/Validation study with reference standard)"
  study_type: "Wearable sensor clinical validation study"
  confidence_score: 9

population:
  cohorts:
    - cohort_id: "recreational_men_cohort"
      sample_size: 14
      sex:
        male: 14
        female: 0
        other: 0
      age:
        mean: 40.0
        sd: 14.0
      height:
        mean: 178.1
        sd: 9.0
      body_weight:
        mean: 82.2
        sd: 14.8
      health_status: "Healthy Control"
      severity: "healthy"
      medications: []
      comorbidities: []
      inclusion_criteria:
        - "Adults (>18 years) of either sex and of any fitness level"
        - "Without previous medical history, current medications, or recent illness"
      exclusion_criteria:
        - "Previous medical history, current medications, or recent illness"
        - "Failure to abstain from caffeine, alcohol, tobacco, and vigorous exercise 24 hours prior to testing"
    - cohort_id: "recreational_women_cohort"
      sample_size: 11
      sex:
        male: 0
        female: 11
        other: 0
      age:
        mean: 34.0
        sd: 10.0
      height:
        mean: 169.1
        sd: 4.3
      body_weight:
        mean: 67.8
        sd: 9.5
      health_status: "Healthy Control"
      severity: "healthy"
      medications: []
      comorbidities: []
      inclusion_criteria:
        - "Adults (>18 years) of either sex and of any fitness level"
        - "Without previous medical history, current medications, or recent illness"
      exclusion_criteria:
        - "Previous medical history, current medications, or recent illness"
        - "Failure to abstain from caffeine, alcohol, tobacco, and vigorous exercise 24 hours prior to testing"

variables:
  - name: "Average Time Between Heartbeats"
    symbol: "RR"
    units: "ms"
    baseline_value:
      mean: null
    measurement_method: "ECG (AMEDTEC CardioPart 12 Blue, lead 2) and Polar H10 Dry-Electrode chest strap"
    sampling_frequency: 1000.0
  - name: "Heart Rate"
    symbol: "HR"
    units: "bpm"
    baseline_value:
      mean: 65.0 # baseline mean derived from resting PRE text (approximate)
    measurement_method: "ECG (AMEDTEC CardioPart 12 Blue, lead 2) and Polar H10 Dry-Electrode chest strap"
    sampling_frequency: 1000.0
  - name: "Detrended Fluctuation Analysis alpha 1"
    symbol: "DFA_a1"
    units: "dimensionless"
    baseline_value:
      mean: null
    measurement_method: "Kubios HRV Premium (automatic correction window 4 to 16 beats)"
    sampling_frequency: 1000.0

sensor_validation:
  sensor_modality: "dry-electrode ECG chest strap"
  sampling_frequency: 1000.0
  signal_processing: "RR series export via Elite HRV app (v5.5.1), automatic artifact correction via Kubios HRV Premium (v3.5.0), smoothness priors detrending (lambda=500)"
  accuracy_metrics:
    - parameter: "RR"
      icc: 1.0
      concordance: 1.0
      pearson_r: 1.0
      bias: 0.2
      loa_lower: -2.2
      loa_upper: 2.6
      exercise_intensity: "rest" # PRE resting state
    - parameter: "DFA_a1"
      icc: 0.85
      concordance: 0.84
      pearson_r: 0.86
      bias: -2.1 # percent bias
      loa_lower: -18.9 # percent LoA
      loa_upper: 14.7 # percent LoA
      exercise_intensity: "rest" # PRE resting state
    - parameter: "RR"
      icc: 1.0
      concordance: 1.0
      pearson_r: 1.0
      bias: 0.1
      loa_lower: -1.2
      loa_upper: 1.6
      exercise_intensity: "rest" # POST resting state
    - parameter: "DFA_a1"
      icc: 0.85
      concordance: 0.84
      pearson_r: 0.86
      bias: 2.5 # percent bias
      loa_lower: -10.2 # percent LoA
      loa_upper: 15.6 # percent LoA
      exercise_intensity: "rest" # POST resting state
    - parameter: "RR"
      icc: 1.0
      concordance: 1.0
      pearson_r: 1.0
      bias: 0.55 # midpoint of reported range (0.4 to 0.7 ms)
      loa_lower: -2.8
      loa_upper: 4.3
      exercise_intensity: "low_intensity" # Exercise (low intensity)
    - parameter: "RR"
      icc: 1.0
      concordance: 1.0
      pearson_r: 1.0
      bias: 0.55 # midpoint of reported range (0.4 to 0.7 ms)
      loa_lower: -0.5
      loa_upper: 1.3
      exercise_intensity: "high_intensity" # Exercise (high intensity)
    - parameter: "HR"
      icc: 1.0
      concordance: 1.0
      pearson_r: 1.0
      bias: -0.15 # midpoint of reported range (-0.1 to -0.2 bpm)
      loa_lower: -0.5
      loa_upper: 0.3
      exercise_intensity: "low_intensity"
    - parameter: "HR"
      icc: 1.0
      concordance: 1.0
      pearson_r: 1.0
      bias: -0.15 # midpoint of reported range (-0.1 to -0.2 bpm)
      loa_lower: -0.7
      loa_upper: 0.4
      exercise_intensity: "high_intensity"
    - parameter: "DFA_a1"
      icc: 0.93
      concordance: 0.93
      pearson_r: 0.93
      bias: 4.75 # midpoint of reported range (0.9% to 8.6%)
      loa_lower: -9.9 # percent LoA
      loa_upper: 11.6 # percent LoA
      exercise_intensity: "low_intensity"
    - parameter: "DFA_a1"
      icc: 0.93
      concordance: 0.93
      pearson_r: 0.93
      bias: 4.75 # midpoint of reported range (0.9% to 8.6%)
      loa_lower: -40.9 # percent LoA
      loa_upper: 58.1 # percent LoA
      exercise_intensity: "high_intensity"
  failure_modes:
    - "Motion artifacts: cycling motion or upper body displacement can corrupt dry-electrode contact"
    - "Electrode-to-skin contact loss: poor sweat buildup at start of exercise (mitigated by pre-wetting) or loose strap fit"
    - "Arrhythmia-induced artifacts: atrial premature complexes (APCs) generate short RR intervals that are flagged as artifacts by filters, causing data loss"
    - "Inability to audit raw ECG: since Polar H10 primarily stores and transmits RR intervals, signal verification cannot separate actual noise from ectopic beats without concurrent reference ECG"
  motion_artifacts_handling: "Data files with artifacts >5% were excluded from evaluation (led to exclusion of 5 participants from exercise, 2 from POST rest)"

conflicts:
  - topic: "DFA a1 Divergence at High Exercise Intensity"
    description: "DFA a1 values tended to be 6% to 7.5% higher at fixed values of 0.75 and 0.5 when measured via Polar H10 compared to ECG lead 2."
    possible_explanations:
      - "Different QRS detection algorithms and sampling rates (1000 Hz in H10 vs. 500 Hz in reference ECG)"
      - "ECG lead placement differences (single-channel chest strap electrodes vs. clinical lead 2)"
      - "Individual chest shape, ventricular orientation, and subcutaneous fat distribution affecting QRS wave morphology"
---

## Supporting Text and Audit Trail

### Study Design and Recruitment
The study recruited 25 recreational athletes (14 men, 11 women).
> "Twenty-five participants (men: n = 14, age: 40 ± 14 years, height: 178.1 ± 9.0 cm, body weight: 82.2 ± 14.8 kg; women: n = 11, age: 34 ± 10 years, height: 169.1 ± 4.3 cm, body weight: 67.8 ± 9.5 kg) volunteered to take part in this study... Entry criteria included adults (>18 years) of either sex and of any fitness level without previous medical history, current medications or recent illness."

### Device Sampling and Configuration
The reference was a 12-lead ECG, compared with the Polar H10 connected to Elite HRV app.
- Reference: 12-channel ECG CardioPart 12 Blue, sampling rate 500 Hz. Lead 2 was selected for comparison.
- Wearable: Polar H10 dry-electrode chest strap, sampling rate 1000 Hz, recording via Elite HRV app (v5.5.1).
- Kubios HRV Premium version 3.5.0 was used to process both sets of RR text files, applying the automatic correction method with smoothness priors detrending ($\lambda = 500$).

### Key Findings
1.  **Linear HRV (RR and HR):** Nearly perfect agreement under all conditions.
    > "The comparisons during resting state conditions PRE and POST showed nearly perfect correlations for the linear parameters RR and HR (r = 1.00, rc = 1.00, ICC3,1 = 1.00)."
2.  **Non-Linear HRV (DFA a1):** Highly correlated, but showed significant differences and limits of agreement under exercise conditions.
    > "Although correlations were also high for DFA a1 (r > 0.86, rc > 0.84, ICC3,1 > 0.85), they were comparatively weaker... During the incremental exercise test... DFA a1 showed wider bias (0.9 to 8.6%) and LoAs of 11.6 to −9.9% during low intensity and 58.1 to −40.9% during high intensity."
3.  **Arrhythmia Pitfalls:**
    > "Since the Polar H10 only stores RR intervals and not ECG waveform recordings, it is not possible to identify or potentially correct signals with excessive artefacts... Evaluation of the lead 2 ECG waveform recordings during the same measurement window, there could be found some runs of atrial premature complexes (APC, red circles) pointing to the artifacts not really being artifacts..."
