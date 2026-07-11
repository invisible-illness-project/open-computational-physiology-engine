# Computational Physiology Ontology & Schemas

This document defines the structure of the formal ontology and presents the updated metadata schemas for variables, relationships, diseases, and wearables.

---

## 1. Ontology Conceptual Graph

The ontology represents semantic physiological concepts and the causal relationships between them.

```mermaid
graph TD
    classDef concept fill:#dcfce7,stroke:#166534,stroke-width:2px;
    classDef var fill:#eff6ff,stroke:#1e40af,stroke-width:2px;
    classDef sensor fill:#fef3c7,stroke:#92400e,stroke-width:2px;

    Variable[Variable]:::concept
    Sensor[Sensor]:::concept
    Measurement[Measurement]:::concept
    Process[Process]:::concept
    Mechanism[Mechanism]:::concept
    Disease[Disease]:::concept
    Equation[Equation]:::concept

    V_RR[RR Interval]:::var
    V_RMSSD[RMSSD]:::var
    S_PPG[PPG Optical Sensor]:::sensor
    S_ECG[ECG Electrode]:::sensor
    
    V_RMSSD -->|belongs_to| HRV[Heart Rate Variability]:::var
    HRV -->|represents| Process_Vagal[Parasympathetic Regulation]:::concept
    V_RMSSD -->|derived_from| V_RR
    V_RR -->|measured_by| S_ECG
    V_RR -->|estimated_by| S_PPG
    
    Process_Vagal -->|mediated_by| Mechanism_Baro[Baroreflex Feedback Loop]:::concept
    Mechanism_Baro -->|described_by| Equation_ODE[Left Ventricle ODEs]:::concept
    Disease_POTS[POTS Phenotype]:::concept -->|perturbs| Variable
```

---

## 2. Updated Metadata Schemas

### A. Variable Schema (`knowledge_base/physiology/*.yaml`)
Every physiological or latent state variable is defined using the following structure:
```yaml
version: string
variables: # or latent_variables
  - symbol: string         # Unique short symbol (e.g. "Vau")
    name: string           # Human-readable name
    category: string       # e.g., "cardiovascular", "autonomic", "respiratory"
    description: string    # Detailed clinical/physiological description
    units: string          # Standard scientific units (e.g., "ml", "mmHg", "bps")
    valid_range:           # Valid bounds to ensure physiological plausibility
      min: float
      max: float
```

### B. Mechanistic Links Schema (`knowledge_base/ontology/mechanistic_links.yaml`)
Causal relationships representing mechanical linkages:
```yaml
version: string
relationships:
  - relationship_id: string         # Unique ID (e.g., "pcm_to_Hc")
    cause: string                   # Source variable symbol
    effect: string                  # Target variable symbol
    type: string                    # Causal shape (e.g., "sigmoid_hill", "first_order_ode")
    evidence_score: float           # 1-10 confidence metric
    supporting_publications:
      - doi: string                 # Sourced DOI
        citation_keys: list of string
        population_cohorts: list of string
    mathematical_ref: string        # Path to LaTeX equation registry
```

### C. Equation Schema (`knowledge_base/equations/definitions.yaml`)
Canonical mathematical representation:
```yaml
version: string
equations:
  - id: string            # Unique identifier
    label: string         # Equation title
    latex: string         # LaTeX mathematical formula
    inputs: list of string # Sourced state variables
    parameters: list of string # Constant symbols
    outputs: list of string # Solved state variables
    description: string   # Physical rationale
```

### D. Wearable Sensor Validation Schema (`knowledge_base/wearables/*.yaml`)
Device specifications and validation bounds:
```yaml
version: string
sensor:
  id: string
  name: string
  type: string            # e.g., "dry_electrode_ecg", "optical_ppg"
  manufacturer: string
  specifications:
    sampling_frequency: float # Hz
    rr_resolution_ms: float
  validation:
    - parameters_evaluated: list of string
      icc: float
      pearson_r: float
      bias: float
      loa_lower: float
      loa_upper: float
      exercise_intensity: string # "rest", "low_intensity", "high_intensity"
      reference_device: string
      provenance:
        doi: string
  failure_modes: list of string
  motion_artifact_handling: string
```
