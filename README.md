# Open Computational Physiology Engine

An open-source, reproducible computational physiology platform designed as scientific infrastructure for synthetic wearable data generation, mechanistic autonomic modeling, digital twin calibration, and disease phenotype simulation (such as POTS, ME/CFS, etc.).

---

## Evolved Scientific Architecture

The engine is structured into distinct modular layers that separate clinical/physiological facts from their execution mechanics:

```text
Scientific Literature
        ↓
Knowledge Extraction
        ↓
Computational Physiology Knowledge Base (knowledge_base/)
        ↓
Mathematical Models (models/)
        ↓
Simulation Engine (simulation/)
        ↓
Sensor Models (sensor_models/)
        ↓
Synthetic Patients & Validation (validation/)
```

---

## Directory Structure

*   [`SCHEMA.md`](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/SCHEMA.md): Defines strict schemas for variables, relationships, mathematical models, and wearable sensors.
*   [`TEMPLATE.md`](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/TEMPLATE.md): Literature review template for adding new clinical publications.
*   [`knowledge_base/`](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/): Programmatically parsed scientific database.
    *   `ontology/`: Formal ontology definition ([concepts.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/ontology/concepts.yaml), [relationships.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/ontology/relationships.yaml), [mechanistic_links.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/ontology/mechanistic_links.yaml)).
    *   `physiology/`: Registries of observable variables ([variables.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/physiology/variables.yaml)) and unobserved latent states ([latent_states.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/physiology/latent_states.yaml)).
    *   `diseases/`: Syndrome parameters and overrides ([pots.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/diseases/pots.yaml)).
    *   `interventions/`: Standardized stressor protocols ([tilt_test.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/interventions/tilt_test.yaml)).
    *   `wearables/`: Sensor specs and validation errors ([polar_h10.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/wearables/polar_h10.yaml)).
    *   `equations/`: LaTeX mathematical formulas ([definitions.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/equations/definitions.yaml)).
*   [`models/`](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/models/): Executable differential equation structures ([baroreflex_model.py](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/models/baroreflex_model.py)).
*   [`simulation/`](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/simulation/): Beat-by-beat ODE numerical integration solver ([engine.py](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/simulation/engine.py)).
*   [`sensor_models/`](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/sensor_models/): Wearable sensor telemetry translators ([wearable_sensors.py](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/sensor_models/wearable_sensors.py)).
*   [`validation/`](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/validation/): Physiological boundary checks and clinical evaluators ([evaluator.py](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/validation/evaluator.py)).
*   [`docs/`](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/docs/): Reference manuals covering architecture, ontology, latent variables, and validation.

---

## Getting Started

### Prerequisites

Ensure you have Python 3 and the required computational packages installed:
```bash
pip install numpy scipy PyYAML
```

### 1. Validate the Scientific Knowledge Base
To run the automated schema and cross-reference check on the YAML database files:
```bash
python3 tools/validate_kb.py
```

### 2. Run the Multi-Cohort Posture Simulation
To run the simulation pipeline (Healthy Control vs. POTS phenotypes) and generate clinical evaluation reports:
```bash
python3 examples/run_simulation.py
```
*Simulation telemetry data is saved as `.npz` files in the `results/` directory for downstream analysis.*

---

## Documentation

*   [architecture.md](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/docs/architecture.md) – Evolution log, folder structures, and scientific rationale.
*   [ontology.md](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/docs/ontology.md) – Structural concepts and schemas.
*   [latent_physiology.md](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/docs/latent_physiology.md) – Autonomic tone and unobserved biological state mappings.
*   [validation_strategy.md](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/docs/validation_strategy.md) – Plausibility criteria and clinical limits.
