# Open Computational Physiology Engine (OCPE)

The Open Computational Physiology Engine is an open-source, evidence-driven scientific infrastructure for representing, simulating, validating, and reasoning about human physiology. It isolates clinical/physiological facts from their execution mechanics into modular, independently reusable layers.

---

## Evolved Scientific Architecture

OCPE represents physiology through an integrated stack of biological models and behavioral feedback loops:

```text
       Scientific Literature
                 │
                 ▼
        Knowledge Extraction
                 │
                 ▼
 Computational Physiology Ontology (knowledge_base/ontology/)
                 │
                 ▼
        Evidence Graph
                 │
                 ▼
   Mathematical Models (knowledge_base/equations/)
                 │
                 ▼
Healthy Physiology Engine & Latent Physiology (simulation/)
                 │
                 ▼
 Composable Disease Perturbation Framework (simulation/perturbations.py)
                 │
                 ▼
       Population Models (simulation/population.py)
                 │
                 ▼
       Behavior Models (simulation/behavior.py)
                 │
                 ▼
        Symptom Layer (simulation/symptoms.py)
                 │
                 ▼
         Time Engine (simulation/time_engine.py)
                 │
                 ▼
       Sensor Models (sensor_models/)
                 │
                 ▼
       Synthetic Patients & Cohorts
                 │
                 ▼
   Validation Framework (validation/validation_suite.py)
```

---

## Directory Structure

*   [`SCHEMA.md`](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/SCHEMA.md): Defines schemas for variables, relationships, mathematical models, and wearable sensors.
*   [`TEMPLATE.md`](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/TEMPLATE.md): Literature review template for clinical publications.
*   [`knowledge_base/`](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/): Programmatically parsed scientific database.
    *   `ontology/`: Formal ontology definition ([concepts.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/ontology/concepts.yaml), [relationships.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/ontology/relationships.yaml), [mechanistic_links.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/ontology/mechanistic_links.yaml)).
    *   `physiology/`: Registries of observable variables ([variables.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/physiology/variables.yaml)) and unobserved latent states ([latent_states.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/physiology/latent_states.yaml)).
    *   `diseases/`: Syndrome parameters and overrides for multiple conditions ([pots.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/diseases/pots.yaml), [eds.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/diseases/eds.yaml), [mecfs.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/diseases/mecfs.yaml), etc.).
    *   `interventions/`: Standardized stressor protocols ([tilt_test.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/interventions/tilt_test.yaml)).
    *   `populations/`: Cohort demographics and priors ([cohorts.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/populations/cohorts.yaml)).
    *   `wearables/`: Sensor specs and validation errors ([polar_h10.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/wearables/polar_h10.yaml)).
    *   `equations/`: LaTeX mathematical formulas ([definitions.yaml](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/knowledge_base/equations/definitions.yaml)).
*   [`models/`](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/models/): Executable differential equation structures ([baroreflex_model.py](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/models/baroreflex_model.py)).
*   [`simulation/`](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/simulation/): Beat-by-beat ODE numerical integration solver, time engine, behaviors, symptoms, and composable perturbations.
*   [`sensor_models/`](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/sensor_models/): Wearable sensor telemetry translators ([wearable_sensors.py](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/sensor_models/wearable_sensors.py)).
*   [`validation/`](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/validation/): Physiological boundary checks, clinical evaluators, and validation suites.
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
To run the standard baseline simulation pipeline (Healthy Control vs. POTS phenotypes) and generate clinical evaluation reports:
```bash
python3 examples/run_simulation.py
```
*Simulation telemetry data is saved as `.npz` files in the `results/` directory.*

### 3. Run the Advanced Scenario Simulation
To run the advanced multi-cohort, composed-perturbation simulation demonstrating demographics, behaviors, symptoms, and the advanced validation suite:
```bash
python3 examples/run_advanced_simulation.py
```

---

## Documentation

*   [architecture.md](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/docs/architecture.md) – Evolution log, folder structures, and scientific rationale.
*   [ontology.md](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/docs/ontology.md) – Structural concepts and schemas.
*   [latent_physiology.md](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/docs/latent_physiology.md) – Autonomic tone and unobserved biological state mappings.
*   [validation_strategy.md](file:///home/eddiem3/development/roeh-health/open-computational-physiology-engine/docs/validation_strategy.md) – Plausibility criteria and clinical limits.
