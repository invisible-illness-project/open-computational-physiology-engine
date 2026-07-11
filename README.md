# Physiological Modeling & Autonomic Regulation Knowledge Base

This directory contains the machine-readable scientific knowledge base of the **Invisible Illness Project**. The goal of this database is to compile, validate, and organize quantitative physiological data, autonomic nervous system feedback equations, systemic disease phenotypes (POTS, ME/CFS, etc.), and wearable sensor validations.

Downstream agents will use this structured repository to:
1. Construct physiological knowledge graphs.
2. Build closed-loop cardiovascular and baroreflex mathematical simulations.
3. Validate wearable sensor data streams (e.g., Polar H10, Apple Watch) against clinical gold standards.
4. Simulate synthetic patients under orthostatic challenges (like Head-Up Tilt) and exercise stressors.

---

## Directory Structure

*   [`SCHEMA.md`](file:///home/eddiem3/development/roeh-health/physiological_modeling/SCHEMA.md): Defines the strict YAML and Markdown formatting rules for variable registries, relationship maps, equations, and literature reviews.
*   [`TEMPLATE.md`](file:///home/eddiem3/development/roeh-health/physiological_modeling/TEMPLATE.md): A blank template to copy and fill out when performing literature reviews on new publications.
*   `knowledge_base/`:
    *   `publications/`:
        *   [`geddes_2022_baroreflex_pots.md`](file:///home/eddiem3/development/roeh-health/physiological_modeling/knowledge_base/publications/geddes_2022_baroreflex_pots.md): Literature review for the computational baroreflex response model. Includes system ordinary differential equations (ODEs), nominal mechanical constants (compliances, resistances), and POTS phenotype parameter settings.
        *   [`schaffarczyk_2022_polar_h10_validation.md`](file:///home/eddiem3/development/roeh-health/physiological_modeling/knowledge_base/publications/schaffarczyk_2022_polar_h10_validation.md): Literature review for the Polar H10 sensor validation study. Details participant cohort demographics, Bland-Altman agreement metrics, intraclass correlations (ICC) vs. ECG, and motion artifact limits.
    *   `variables/`:
        *   [`definitions.yaml`](file:///home/eddiem3/development/roeh-health/physiological_modeling/knowledge_base/variables/definitions.yaml): The central registry mapping variable symbols (e.g., `pcm`, `Raup`, `DFA_a1`) to names, categories, units, and physiological ranges.
    *   `relationships/`:
        *   [`mechanistic_links.yaml`](file:///home/eddiem3/development/roeh-health/physiological_modeling/knowledge_base/relationships/mechanistic_links.yaml): Central map of causal biological linkages, detailing cause-and-effect symbols, types, evidence levels, and citation DOIs.
    *   `models/`:
        *   [`mathematical_models.yaml`](file:///home/eddiem3/development/roeh-health/physiological_modeling/knowledge_base/models/mathematical_models.yaml): Master registry of model ODEs (LaTeX formatted) and baseline/phenotype-specific constants.
*   `tools/`:
    *   [`validate_kb.py`](file:///home/eddiem3/development/roeh-health/physiological_modeling/tools/validate_kb.py): Python script that validates the syntax of the entire knowledge base against the schema, verifying variable cross-references, parameters, units, and citation identifiers.
*   `BaroreflexPOTSmodel/`:
    *   Cloned MATLAB simulation repository containing the exact driver, elastance functions, and ODE code from the Geddes et al. 2022 publication.

---

## Validation and Verification

A programmatic check should be run after editing or adding any file in the knowledge base to ensure schema compliance and maintain machine readability.

### Run Validation Script
From the `physiological_modeling/` directory, run:
```bash
python3 tools/validate_kb.py
```

### Output Expectations
A successful validation will output:
```text
Validating Knowledge Base in: /path/to/physiological_modeling
[OK] Loaded 25 central variable definitions.
[OK] Loaded 7 central relationships.
[OK] Loaded 1 central mathematical models.
Found 2 publication reviews to validate.
[OK] Validated review: 'Validity of the Polar H10 Sensor...'
[OK] Validated review: 'Postural orthostatic tachycardia syndrome...'

--- Validation Summary ---
Total Errors: 0
Total Warnings: 0
[OK] Knowledge Base validation PASSED.
```
Any errors (such as missing units, unregistered variables, or YAML syntax faults) will produce an exit code of `1` and list the specific file and line that caused the failure.
