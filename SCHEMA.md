# Knowledge Base Schema Definitions

This schema defines the structure of the literature review files and central registries (variables, models, relationships) for the Invisible Illness Project. The goal is to enforce machine readability, strict data types, explicit unit requirements, and absolute traceability for downstream mathematical modeling.

---

## 1. Publication Review Schema (`knowledge_base/publications/*.md`)

Every reviewed publication must be a Markdown file with a YAML frontmatter block. The frontmatter must contain:

```yaml
publication:
  title: string           # Exact title of the paper
  doi: string             # Digital Object Identifier (canonical)
  pmid: string            # PubMed ID (if available, else null)
  pmcid: string           # PubMed Central ID (if available, else null)
  journal: string         # Full journal name
  year: integer           # Year of publication
  authors: list of string # Full names of all authors
  evidence_level: string  # Standard level (e.g., Level 1: RCT, Level 4: In Silico)
  study_type: string      # E.g., clinical validation, randomized trial, in silico
  confidence_score: integer # 1 to 10 scale (justified in text)

population:
  cohorts:
    - cohort_id: string       # Unique identifier within this document
      sample_size: integer    # Number of subjects
      sex:                    # Biological sex distribution
        male: integer         # Count of males
        female: integer       # Count of females
        other: integer        # Count of other/unspecified
      age:                    # Age distribution (years)
        mean: float           # Mean age (null if not reported)
        sd: float             # Standard deviation (null if not reported)
        min: float            # Minimum age (null if not reported)
        max: float            # Maximum age (null if not reported)
      bmi:                    # Body Mass Index (kg/m^2)
        mean: float           # Mean BMI
        sd: float             # Standard deviation of BMI
      health_status: string   # "Healthy Control", "POTS", "ME/CFS", etc.
      severity: string        # Mild, moderate, severe, or "unspecified"
      medications: list of string # Medications allowed or reported
      comorbidities: list of string # Comorbidities reported
      inclusion_criteria: list of string # Specific inclusion rules
      exclusion_criteria: list of string # Specific exclusion rules

variables:
  - name: string            # Full variable name
    symbol: string          # Standard mathematical or sensing symbol (e.g., RMSSD)
    units: string           # Standard scientific units (e.g., ms, bpm, mmHg)
    baseline_value:         # Reported resting/baseline values for this cohort
      mean: float
      sd: float
      median: float
      range_min: float
      range_max: float
    measurement_method: string # ECG, dry-electrode chest strap, PPG, etc.
    sampling_frequency: float # In Hz (null if not reported)

mathematical_models:
  - model_name: string      # E.g., Baroreflex control of heart rate
    equations:
      - label: string       # Equation tag (e.g., Eq 2.11)
        latex: string       # LaTeX formatted string of the equation
    parameters:
      - symbol: string      # Parameter symbol (e.g., k_R)
        name: string        # Short name
        value: float        # Default/nominal value
        units: string       # Parameter units
        phenotype_values:   # Phenotype-specific parameter settings if applicable
          - phenotype_id: string
            value: float
        description: string # Short description
    assumptions: list of string # Underlying assumptions made by the model

relationships:
  - relationship_id: string # Unique string ID (e.g., P_au_to_H_c)
    cause: string           # Sourced variable symbol
    effect: string          # Target variable symbol
    type: string            # "direct_proportional", "inverse_proportional", "sigmoid_hill", "first_order_ode", etc.
    strength: string        # Quantified coefficient or gain if known (else null)
    equation_ref: string    # Reference to equations (e.g., "Eq 2.11")
    evidence_level: string  # Level of evidence supporting this link
    citations: list of string # DOIs/PMIDs supporting this relationship

sensor_validation:          # Required if the paper validates a wearable device
  sensor_modality: string   # E.g., dry-electrode ECG, optical photoplethysmography
  sampling_frequency: float # In Hz
  signal_processing: string # Preprocessing and filters used
  accuracy_metrics:         # Quantified error rates vs. gold standard
    - parameter: string     # Variable evaluated (e.g., RR, DFA_a1)
      icc: float            # Intraclass Correlation Coefficient (null if not reported)
      concordance: float    # Lin's Concordance Correlation Coefficient
      pearson_r: float      # Pearson's r
      bias: float           # Mean difference (units match parameter)
      loa_lower: float      # Lower Limit of Agreement
      loa_upper: float      # Upper Limit of Agreement
      exercise_intensity: string # "rest", "low_intensity", "high_intensity"
  failure_modes: list of string # Known failure modes
  motion_artifacts_handling: string # How motion artifacts are handled/detected

conflicts:                  # Discrepancies, limitations, or conflicts noted
  - topic: string
    description: string
    possible_explanations: list of string
```

---

## 2. Central Registry Schemas

### A. Central Variables Schema (`knowledge_base/variables/definitions.yaml`)
A single global dictionary registry mapping unique variable symbols to their definitions:
```yaml
variables:
  - symbol: string
    name: string
    category: string        # cardiovascular, autonomic, respiratory, sensor, etc.
    description: string
    units: string           # Standard scientific unit
    valid_range:            # Physiological limit bounds
      min: float
      max: float
```

### B. Central Relationships Schema (`knowledge_base/relationships/mechanistic_links.yaml`)
Aggregated causal links across all reviewed literature:
```yaml
relationships:
  - relationship_id: string
    cause: string
    effect: string
    type: string
    evidence_score: float   # Derived score based on study types
    supporting_publications:
      - doi: string
        citation_keys: list of string
        population_cohorts: list of string
    mathematical_ref: string # Link to models mapping this relationship
```

### C. Central Mathematical Models Schema (`knowledge_base/models/mathematical_models.yaml`)
Consolidated equations and parameters for simulation execution:
```yaml
models:
  - model_id: string
    name: string
    equations:
      - label: string
        latex: string
    parameters:
      - symbol: string
        units: string
        nominal_value: float
        phenotypes:
          - phenotype: string
            value: float
        description: string
    sources: list of string # List of DOIs
```
