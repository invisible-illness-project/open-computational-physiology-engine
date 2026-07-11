# Computational Physiology Engine: Architecture, Migration & Rationale

This document describes the evolved directory layout, file migration workflow, backward compatibility plan, and the engineering rationale for the Scientific Knowledge Base.

---

## 1. Updated Repository Architecture

The evolved architecture isolates mathematical representation, clinical knowledge, software implementation, and sensor validations into independent conceptual layers.

```text
open-computational-physiology-engine/
│
├── knowledge_base/
│   ├── ontology/
│   │   ├── concepts.yaml           # Core conceptual classes (Variable, Sensor, etc.)
│   │   ├── relationships.yaml      # Semantic links (RMSSD belongs_to HRV, etc.)
│   │   └── mechanistic_links.yaml  # Causal biological links (pcm to Hc, etc.)
│   │
│   ├── physiology/
│   │   ├── variables.yaml          # Registries of observable variables (Vau, plv, etc.)
│   │   └── latent_states.yaml      # Registries of latent states (T_sym, T_para, etc.)
│   │
│   ├── diseases/
│   │   └── pots.yaml               # Phenotypic overrides (neuropathic, hyperadrenergic)
│   │
│   ├── interventions/
│   │   └── tilt_test.yaml          # Standard clinical tests protocols (HUT, exercise)
│   │
│   ├── populations/
│   │   └── cohorts.yaml            # Virtual populations / cohort demographics
│   │
│   ├── wearables/
│   │   ├── polar_h10.yaml          # Spec and accuracy metrics for ECG sensing
│   │   └── photoplethysmography.yaml # Optical sensing validations
│   │
│   ├── equations/
│   │   ├── definitions.yaml        # Canonical equations (LaTeX)
│   │   └── mathematical_models.yaml# Constants, bounds, and baseline values
│   │
│   └── publications/
│       ├── geddes_2022_baroreflex_pots.md # Review of baroreflex POTS ODE model
│       └── schaffarczyk_2022_polar_h10_validation.md # Review of Polar H10 validation
│
├── models/
│   └── baroreflex_model.py         # ODE derivatives computation, dynamic initialization
│
├── simulation/
│   └── engine.py                   # Radau stiff integrator, HRV noise, latent variables extraction
│
├── sensor_models/
│   └── wearable_sensors.py         # Polar H10 ECG simulation, PPG optical waveform synthesis
│
├── validation/
│   └── evaluator.py                # Plausibility checks, POTS clinical diagnostic test
│
├── examples/
│   └── run_simulation.py           # Demo of Healthy Control vs. POTS phenotypes
│
├── tools/
│   └── validate_kb.py              # Programmable validation checking syntax & relations
│
├── SCHEMA.md                       # Structured schema definitions and validation rules
├── TEMPLATE.md                     # Lit review template
└── README.md                       # General installation and usage guide
```

---

## 2. Migration Plan

Evolving the repository from the legacy structure was performed in the following phases:

1. **Hierarchy Setup**: Create directory layers: `ontology`, `physiology`, `diseases`, `interventions`, `populations`, `wearables`, `equations`.
2. **Schema & Variable Migration**:
   * Legacy `variables/definitions.yaml` migrated to `physiology/variables.yaml`.
   * Legacy `relationships/mechanistic_links.yaml` migrated to `ontology/mechanistic_links.yaml`.
   * Legacy `models/mathematical_models.yaml` migrated to `equations/mathematical_models.yaml`.
3. **Ontology Enrichment**:
   * Created `ontology/concepts.yaml` to define the structural classes.
   * Created `ontology/relationships.yaml` to describe semantic linkages between variables and sensors (e.g., `RMSSD` belongs to `HRV`).
4. **Physiology Isolation**:
   * Extracted `latent_states.yaml` to isolate unobserved variables (Sympathetic/Parasympathetic Tone, Blood Volume, Compliance, etc.).
5. **Disease & Sensor Isolation**:
   * Created `diseases/pots.yaml` defining overrides.
   * Created `wearables/polar_h10.yaml` and `wearables/photoplethysmography.yaml` for wearable specifications.
6. **Programmatic Verification**:
   * Re-implemented `tools/validate_kb.py` to recursively validate files in the new layout.
   * Deleted legacy directories (`variables/`, `relationships/`, `models/`) to avoid version confusion.

---

## 3. Backward Compatibility Plan

To ensure that downstream researchers can compile legacy studies, we enforce the following backward compatibility guarantees:

* **Variable Names**: State variable names (`Vau`, `Vvu`, `pcm`, `Hc`, etc.) and parameters (`Ral`, `Cau`, `Es`) remain unchanged.
* **Literature Reviews**: Frontmatter formats in `publications/` are preserved. The validator was updated to cross-reference variables in both `physiology/variables.yaml` and `physiology/latent_states.yaml`.
* **Validation Interface**: The validation tool remains executable via:
  ```bash
  python3 tools/validate_kb.py
  ```
  It validates the new paths silently, ensuring any CI/CD automation continues to pass.

---

## 4. Scientific Architecture Rationale

| Decision | Impact on Reproducibility | Impact on Extensibility | Impact on Maintainability |
| :--- | :--- | :--- | :--- |
| **Separating Equations from Executable Code** | Researchers can cite the canonical LaTeX equations in `equations/definitions.yaml` directly as the mathematical source of truth. | Future integrations in C++, Julia, or Rust can consume the same YAML files without re-writing the math. | Code adjustments to numerical solvers do not risk modifying underlying physiological assumptions. |
| **Dynamic Steady-State Initialization** | The solver calculates nominal resistances, compliances, and initial volumes using physiological formulas. This ensures baseline stability. | Adding new body compartments (e.g., kidneys) can hook into the volume-distribution formulas. | Eliminates manual "tuning" of initial parameters, which frequently introduces human errors. |
| **Isolating Disease Phenotypes** | Pathological syndromes are defined exclusively as parameter overrides of healthy biology, forcing physiological consistency. | Researchers can define new diseases (e.g., ME/CFS, Orthostatic Hypotension) by adding a single YAML file in `diseases/`. | Changes to healthy baselines automatically propagate to disease states, preventing code divergence. |
| **Formal Physiology Ontology** | Establishes a machine-readable map of semantic concepts and biological relationships. | Allows automated knowledge graph queries (e.g., finding all variables measured by a PPG sensor). | Simplifies documentation, making onboarding of new researchers and clinical collaborators efficient. |
