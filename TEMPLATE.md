# [Publication Title]

---
publication:
  title: "Example Title"
  doi: "10.xxxx/xxxx"
  pmid: null
  pmcid: null
  journal: "Example Journal"
  year: 2026
  authors:
    - "Author One"
  evidence_level: "Level 1"
  study_type: "Randomized Controlled Trial"
  confidence_score: 9

population:
  cohorts:
    - cohort_id: "example_cohort"
      sample_size: 100
      sex:
        male: 50
        female: 50
        other: 0
      age:
        mean: 40.0
        sd: 5.0
        min: 18.0
        max: 65.0
      bmi:
        mean: 24.5
        sd: 2.1
      health_status: "Healthy"
      severity: "unspecified"
      medications: []
      comorbidities: []
      inclusion_criteria: []
      exclusion_criteria: []

variables:
  - name: "Heart Rate"
    symbol: "HR"
    units: "bpm"
    baseline_value:
      mean: 70.0
      sd: 10.0
      median: null
      range_min: 50.0
      range_max: 95.0
    measurement_method: "ECG"
    sampling_frequency: 250.0

mathematical_models:
  - model_name: "Example Model"
    equations:
      - label: "Eq 1"
        latex: "y = m x + c"
    parameters:
      - symbol: "m"
        name: "Slope Coefficient"
        value: 1.5
        units: "dimensionless"
        phenotype_values: []
        description: "Rate of change"
    assumptions:
      - "Linear relationship holds true within normal physiological range"

relationships:
  - relationship_id: "X_to_Y"
    cause: "X"
    effect: "Y"
    type: "direct_proportional"
    strength: "1.5"
    equation_ref: "Eq 1"
    evidence_level: "Level 1"
    citations:
      - "10.xxxx/xxxx"

sensor_validation:
  sensor_modality: "dry-electrode ECG"
  sampling_frequency: 1000.0
  signal_processing: "Bandpass filtering (0.05-150 Hz)"
  accuracy_metrics:
    - parameter: "RR"
      icc: 0.99
      concordance: 0.99
      pearson_r: 0.99
      bias: 0.1
      loa_lower: -2.0
      loa_upper: 2.0
      exercise_intensity: "rest"
  failure_modes:
    - "High motion artifacts"
  motion_artifacts_handling: "Manual exclusion of segments with >5% artifact"

conflicts:
  - topic: "Discrepancy in Y"
    description: "Brief description of the conflict"
    possible_explanations:
      - "Different electrode placement"
---

## Supporting Text and Audit Trail

Provide brief notes, direct quotes, and other qualitative data that justify the parameters entered above.

### Study Design and Recruitment
*   *Quote/Reference:* "..."

### Mathematical Model Derivation
*   *Quote/Reference:* "..."

### Sensor Calibration and Validation
*   *Quote/Reference:* "..."

### Scientific Critique and Confidence Scoring
*   *Justification:* "Confidence score of 9 assigned because..."
