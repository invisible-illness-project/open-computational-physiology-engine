# ADR 0001: Sidecar Manifest Pattern for Tracking YAML Review and Validation

* **Status:** Accepted
* **Date:** 2026-09-10
* **Authors:** Staff Software Engineer & Computational Scientist
* **Deciders:** Engineering & Scientific Governance Team
* **Technical Area:** Knowledge Base Governance, Provenance, & Model Validation

---

## Context and Problem Statement

The Open Computational Physiology Engine relies heavily on structured YAML assets (e.g., central variable registries, mechanistic relationship maps, phenotype mathematical models, and publication review frontmatter). These assets dictate downstream numerical simulations and physiological modeling.

To maintain scientific integrity and clinical reliability, every data asset must undergo review and validation. Crucially:
1. Both **AI agents** (e.g., LLM literature verification bots, extraction sanity checkers) and **human domain experts** (e.g., clinical physiologists, software engineers) serve as reviewers.
2. We require absolute traceability of *when* a file was reviewed, *who* or *what model* reviewed it, *what specific scope/aspects* were evaluated, and the *exact version/digest* of the content at the time of review.

We need a standardized architectural pattern for recording, storing, and verifying these review trails across the repository lifecycle.

---

## Decision Drivers

* **Cryptographic Content Integrity:** Reviews must be tightly coupled to a specific content snapshot via SHA-256 digests. Any subsequent edit to the source file must invalidate prior sign-offs.
* **Dual Identity Representation:** Equal capability to represent deterministic static analysis tools, AI agents (model ID, prompt version, parameters), and human reviewers (ORCID, email, Git handles).
* **Data File Purity:** Source YAML files containing scientific data must remain clean, read-only domain representations without operational metadata pollution.
* **Concurrent Review & Git Harmony:** Multiple reviewers (or automated agents) must be able to contribute review manifests without causing Git merge conflicts on raw data assets.
* **CI/CD & Runtime Auditability:** Automated pipelines and runtime engines must be able to programmatically verify that a YAML file has passed required review gates before simulation execution.

---

## Considered Options

1. **Option 1: Embedded Review Audit Trail (In-File Metadata Header)**
   * Storing a `review_history` block directly inside each source YAML file or Markdown frontmatter.
2. **Option 2: Sidecar Review Manifests (`.review.yaml`) [CHOSEN]**
   * Decoupling review metadata into companion files adjacent to target assets (e.g., `variables.yaml` $\rightarrow$ `variables.yaml.review.yaml`).
3. **Option 3: Git-Native Provenance (Git Notes & VCS Commit Tags)**
   * Storing structured review objects inside Git Notes (`git notes`) attached to commit SHAs or pull request metadata.

---

## Decision Outcome

**Chosen Option: Option 2 (Sidecar Review Manifests)**

We will implement **Sidecar Review Manifests** (`<filename>.<ext>.review.yaml`) co-located with every reviewed target file.

### Rationale

Option 2 provides the optimal balance of data cleanliness, Git workflow compatibility, and local file transparency:
* **Separation of Concerns:** Pure physiological models and definitions remain isolated from operational audit logs.
* **No Re-hashing Loops:** Embedded headers require hashing files *excluding* the header, creating complex parsing logic. Sidecar manifests allow straightforward SHA-256 digest computation over the exact, raw target file.
* **Conflict-Free Asynchronous Reviews:** AI agents and human reviewers can append manifest updates without editing or lock-contending on the underlying scientific dataset.
* **Tooling Simplicity:** Verification tools can resolve companion sidecar files deterministically via path conventions (e.g., `path/to/target.yaml` $\rightarrow$ `path/to/target.yaml.review.yaml`).

---

## Technical Specification & Schema

### 1. Sidecar File Naming Convention
For any target file `path/to/asset.yaml` (or `.md`), its companion review manifest MUST be saved at `path/to/asset.yaml.review.yaml` (or `path/to/asset.md.review.yaml`).

### 2. Manifest Schema (`review_manifest_version: "1.0.0"`)

Every sidecar manifest MUST conform to the following schema:

```yaml
review_manifest_version: "1.0.0"

target_file:
  path: "knowledge_base/physiology/variables.yaml"
  sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

review_history:
  # Level 1: Deterministic Validator
  - review_id: "rev-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
    reviewed_at: "2026-09-10T14:20:00Z"
    reviewer:
      kind: "validator" # Allowed: "validator" | "ai_agent" | "human"
      identity:
        name: "validate_kb.py"
        version: "v2.4.0"
        commit_sha: "a1b2c3d4"
    scope:
      - "yaml_syntax"
      - "json_schema"
      - "unit_dimensions"
    verdict: "PASSED" # Allowed: "PASSED" | "PASSED_WITH_WARNINGS" | "NEEDS_REVISION" | "REJECTED" | "APPROVED"
    confidence_score: 1.0
    findings: []

  # Level 2: AI Validation Agent
  - review_id: "rev-4f3a8b1c-8e2d-4190-b74a-10f8a9235e11"
    reviewed_at: "2026-09-10T14:22:15Z"
    reviewer:
      kind: "ai_agent"
      identity:
        provider: "Google Gemini"
        model_name: "gemini-1.5-pro-002"
        agent_system: "KB-Literature-Verification-Agent"
        system_prompt_sha256: "7f8a3b90..."
        parameters:
          temperature: 0.0
    scope:
      - "literature_fidelity"
      - "equation_extraction"
    verdict: "PASSED_WITH_WARNINGS"
    confidence_score: 0.94
    findings:
      - path: "variables[2].baseline_value.mean"
        severity: "WARNING" # Allowed: "INFO" | "WARNING" | "CRITICAL"
        message: "Baseline RMSSD value (24.5 ms) is at lower quartile for POTS cohort in cited DOI:10.1016/j.jacc.2021.04.012."

  # Level 3: Human Peer Review
  - review_id: "rev-c7d9a1e2-5f6a-4b3c-8d1e-9f0a1b2c3d4e"
    reviewed_at: "2026-09-10T16:05:12Z"
    reviewer:
      kind: "human"
      identity:
        name: "Dr. Jane Doe"
        email: "jdoe@roeh-health.org"
        orcid: "0000-0002-1825-0097"
        git_handle: "@jdoe-physio"
        role: "Clinical Physiologist"
    scope:
      - "clinical_plausibility"
      - "model_equation_approval"
    verdict: "APPROVED"
    confidence_score: 1.0
    findings:
      - path: "variables[2]"
        severity: "INFO"
        message: "Manually verified against manuscript Table 2. Value confirmed correct."
```

---

## Review & Validation Workflow Architecture

To enforce validation quality without bottlenecks, reviews execute across three sequential tiers:

```
[Target Asset (YAML/MD)]
          │
          ▼
 ┌──────────────────┐
 │ L1: Rule Check   │ ──(Fails)──> [Block CI / Fix Syntax]
 └────────┬─────────┘
          │ (Passes: Append L1 to .review.yaml)
          ▼
 ┌──────────────────┐
 │ L2: AI Agent     │ ──(Fails/Low Conf)──> [Flag for Human Review]
 └────────┬─────────┘
          │ (Passes: Append L2 to .review.yaml)
          ▼
 ┌──────────────────┐
 │ L3: Human Expert │ ──(Approves)──> [Append L3 Sign-off & Merge to Main]
 └──────────────────┘
```

1. **Level 1 (Automated Syntax & Schema Checker):** Pre-commit or CI task verifies YAML syntax, JSON Schema constraints, and physical unit dimensionality (e.g. using `pint`). Appends an `L1` entry upon success.
2. **Level 2 (AI Verification Agent):** Automated LLM agent checks literature extraction against source papers (DOIs/PDFs), verifying equation formulations and parameter ranges. Appends an `L2` entry with findings and confidence scores.
3. **Level 3 (Human Expert Sign-Off):** Domain expert inspects data and AI warnings, performing final clinical/scientific sign-off. Appends an `L3` entry with verdict `APPROVED`.

---

## Verification Tooling & Enforcement

A CLI module in `tools/` (extending `validate_kb.py`) will enforce compliance during CI build steps and before simulation runs:

* **Stale Check:** Asserts `target_file.sha256` in the sidecar matches `SHA-256(current_target_file)`. If hashes differ, the review status is flagged as **STALE**.
* **Gatekeeping:** Require that all files in `production` status have an `L3` human approval or an `L2` high-confidence pass matching the current SHA-256 digest.

---

## Consequences & Trade-offs

### Positive
* **Complete Auditing:** Full provenance tracing of every review event, including specific AI model versions and human ORCIDs.
* **Clean Data:** Zero schema noise inside scientific core definition files.
* **Stale Review Detection:** Cryptographic SHA-256 binding guarantees edits immediately invalidate old sign-offs.

### Negative / Mitigations
* **File Count Growth:** Adds companion `.review.yaml` files for every reviewed asset.
  * *Mitigation:* Automated scripts (`tools/validate_kb.py`) will automatically manage, create, and validate sidecar paths.
* **File Renames:** Renaming a data file requires renaming its sidecar.
  * *Mitigation:* Add pre-commit hook / helper CLI tool to automatically keep sidecar paths in sync during file move operations.
