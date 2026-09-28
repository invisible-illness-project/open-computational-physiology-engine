# ADR 0001: Sidecar Manifests and Evidence-Layered Validation

* **Status:** Accepted — Revised
* **Date:** 2026-09-27
* **Supersedes:** ADR 0001, 2026-09-10
* **Authors:** Staff Software Engineer & Computational Scientist
* **Deciders:** Engineering & Scientific Governance Team
* **Technical Area:** Knowledge Base Governance, Provenance, Model Validation, Scientific Reproducibility

---

## Context and Problem Statement

The Open Computational Physiology Engine (OCPE) relies heavily on structured scientific assets, including YAML parameter registries, physiological relationship maps, mechanistic models, perturbation definitions, literature evidence records, and publication review metadata.

These assets influence downstream numerical simulations and synthetic physiological data generation. Consequently, the project requires strong provenance, reproducibility, validation, and governance.

The original version of this ADR established a sidecar-manifest architecture in which deterministic validators, AI agents, and human experts could record review activity. It also described a sequential validation model in which human expert approval constituted the highest validation tier.

That model creates an undesirable coupling between:

1. **Whether an artifact can continue to make progress within the research system**, and
2. **Whether a human has personally reviewed and authorized the artifact for a particular downstream use.**

These are not equivalent requirements.

OCPE is intended to support an increasingly autonomous research and engineering workflow. AI agents should be able to independently inspect evidence, reproduce calculations, identify inconsistencies, challenge existing claims, propose corrections, and accumulate evidence without requiring human review before every incremental advance.

At the same time, AI-agent agreement must not be treated as equivalent to scientific truth or human expert endorsement. Multiple agents may share correlated errors, models, training data, prompts, or reasoning failures.

Therefore, OCPE requires an evidence-layered validation architecture in which:

* deterministic validation establishes machine-level correctness;
* independent AI agents can generate and challenge scientific evidence;
* multiple forms of evidence can be aggregated;
* disagreement is preserved rather than hidden;
* validation is attached to specific content snapshots;
* human review is represented explicitly as a higher-trust provenance and authorization layer;
* downstream use policies determine whether human review is mandatory.

### Core Principle

> **Human review is not a universal prerequisite for scientific or engineering progress. It is a higher-trust provenance and authorization layer applied according to downstream risk and intended use.**

AI-generated consensus is evidence, not truth.

---

# Decision Drivers

The architecture is driven by the following requirements.

### 1. Cryptographic Content Integrity

Every review and validation claim must be bound to the exact content snapshot that was evaluated.

A modification to the target asset must invalidate or supersede validation evidence associated with the previous content hash.

SHA-256 is the required content-integrity mechanism.

### 2. Separation of Scientific Content and Governance Metadata

Scientific YAML/Markdown assets must remain clean domain representations.

Operational review metadata belongs in sidecar manifests.

### 3. Autonomous Scientific Progress

Agents must be capable of reviewing, challenging, reproducing, and extending scientific artifacts without requiring a human reviewer for every iteration.

### 4. Evidence Over Voting

The system must not equate the number of agents supporting a claim with scientific truth.

Validation aggregation should consider:

* reviewer independence;
* evidence quality;
* methodological diversity;
* reproducibility;
* confidence;
* contradictions;
* computational test results;
* source quality;
* known limitations.

### 5. Explicit Disagreement

Disagreement is a first-class scientific state.

The system must preserve contradictory reviews rather than reducing them to a single majority verdict.

### 6. Reproducibility

Validation must record enough information to reproduce or audit the validation process, including:

* model/provider;
* model version;
* agent role;
* prompt or methodology version;
* tool versions;
* evidence identifiers;
* relevant parameters;
* timestamps;
* target content hash.

### 7. Risk-Proportionate Human Review

Human review requirements must depend on downstream use.

Human review is mandatory for designated high-consequence uses, including IIP production datasets and other applications designated by project governance.

Human review is encouraged, but not necessarily mandatory, for lower-risk third-party or exploratory applications.

### 8. Machine-Enforceable Use Policies

The validation system must distinguish:

* evidence state;
* review state;
* human authorization;
* downstream usage permissions.

A scientifically useful artifact may therefore be available for exploratory research while remaining prohibited from IIP production use.

---

# Considered Options

## Option 1: Human-Gated Validation

Require human approval before an artifact can advance.

**Rejected.**

This creates a human bottleneck and prevents autonomous research workflows from accumulating evidence between human review cycles.

---

## Option 2: Simple Multi-Agent Majority Voting

Allow an artifact to become validated when a specified number or percentage of agents vote for it.

**Rejected as the primary validation mechanism.**

Majority voting can be useful as one signal, but it is insufficient as a scientific validation criterion because agents may share:

* models;
* training data;
* prompts;
* source material;
* systematic biases;
* reasoning failures.

Five correlated agents do not necessarily constitute five independent pieces of evidence.

---

## Option 3: Evidence-Layered Validation with Risk-Based Human Authorization

Use deterministic validation, independent agent reviews, computational reproduction, evidence aggregation, challenge/adjudication, and explicit human review/authorization policies.

**Chosen.**

This permits autonomous progress while preserving clear boundaries around high-consequence downstream applications.

---

# Decision Outcome

We will implement **Sidecar Review Manifests with Evidence-Layered Validation**.

Every reviewed asset will have a companion manifest:

```text
path/to/asset.yaml
path/to/asset.yaml.review.yaml
```

The manifest records review events, evidence, validation state, challenges, adjudication, and downstream authorization.

Validation is not represented as a single binary `PASSED`/`FAILED` field.

Instead, the system distinguishes at least four concepts:

1. **Review Events**
2. **Evidence State**
3. **Human Review State**
4. **Usage Authorization**

---

# 1. Review Events

Every validator, agent, or human reviewer contributes an immutable review event.

Example:

```yaml
review:
  review_id: "rev-..."
  reviewed_at: "2026-09-27T18:00:00Z"

  reviewer:
    kind: "ai_agent"
    identity:
      provider: "..."
      model_name: "..."
      model_version: "..."
      agent_role: "literature_verification"
      methodology_version: "..."
      system_prompt_sha256: "..."

  target:
    path: "knowledge_base/physiology/variables.yaml"
    sha256: "..."

  scope:
    - "literature_fidelity"
    - "parameter_range"

  verdict: "SUPPORTED"

  confidence: 0.87

  findings: []
```

Allowed reviewer kinds include:

```text
validator
ai_agent
human
```

---

# 2. Evidence State

The manifest maintains a derived validation state.

Suggested states:

```text
UNREVIEWED
DETERMINISTICALLY_VALID
AGENT_REVIEWED
AGENT_SUPPORTED
AGENT_DISPUTED
ADJUDICATION_REQUIRED
COMPUTATIONALLY_REPRODUCED
HUMAN_REVIEWED
HUMAN_APPROVED
STALE
```

These states are not necessarily mutually exclusive properties of the artifact. The system should retain the underlying evidence and derive the current state from it.

For example:

```yaml
validation:
  state: "AGENT_SUPPORTED"

  deterministic:
    status: "PASSED"

  agent_evidence:
    independent_reviewers: 4
    supporting: 4
    disputing: 0

  computational:
    status: "PASSED"

  human_review:
    status: "NOT_REVIEWED"
```

---

# 3. Claim-Level Validation

Where practical, validation should occur at the level of individual scientific claims rather than only at the file level.

Example:

```yaml
claims:

  - claim_id: "claim-001"

    statement: >
      Baseline parameter X is approximately Y under condition Z.

    evidence:
      - source_id: "doi:..."
        relevance: "direct"

    reviews:

      - review_id: "rev-001"
        verdict: "SUPPORTED"

      - review_id: "rev-002"
        verdict: "SUPPORTED"

      - review_id: "rev-003"
        verdict: "DISPUTED"

    status: "DISPUTED"
```

This permits a single asset to contain:

* strongly supported claims;
* weak claims;
* disputed claims;
* unresolved claims.

The system must not collapse these into a misleading file-level `APPROVED` status.

---

# 4. Independent Agent Validation

Multiple AI agents may independently evaluate the same claim or artifact.

However, the system must distinguish **agent count** from **independent evidence streams**.

Each agent review should identify an independence group where possible.

Example:

```yaml
reviewer:
  kind: "ai_agent"

  identity:
    provider: "..."
    model_name: "..."
    model_version: "..."

  independence_group: "literature-agent-family-A"
```

The validation engine should avoid treating five agents from the same model/prompt lineage as five fully independent validators.

Independent evidence may instead come from different:

* models;
* providers;
* prompts;
* methodologies;
* source-retrieval strategies;
* computational implementations;
* reasoning approaches.

---

# 5. Evidence Aggregation

The validation engine should aggregate evidence rather than merely count votes.

At minimum, aggregation should consider:

```text
deterministic validity
source quality
reviewer independence
methodological diversity
review confidence
agreement/disagreement
computational reproduction
known limitations
unresolved findings
```

A simple majority may be recorded as a statistic:

```yaml
agent_evidence:
  supporting: 4
  disputing: 1
  abstaining: 0
```

but it must not itself establish scientific validity.

The resulting state should instead be derived from policy.

---

# 6. Challenges and Scientific Disputes

Any reviewer may challenge an existing validation claim.

A challenge is a first-class record:

```yaml
challenge:
  challenge_id: "challenge-..."
  target_claim: "claim-001"

  challenger:
    kind: "ai_agent"

  reason:
    type: "evidence_mismatch"

  statement: >
    The cited paper does not directly support the claimed parameter range.

  evidence:
    - source_id: "doi:..."

  status: "OPEN"
```

Possible challenge states:

```text
OPEN
UNDER_INVESTIGATION
RESOLVED_SUPPORT
RESOLVED_REJECTION
UNRESOLVED
```

An unresolved challenge should reduce the effective validation state even when a majority of reviewers support the original claim.

---

# 7. Adjudication

When material disagreement exists, the system may launch an adjudication workflow.

Adjudication may involve:

* additional independent agents;
* targeted literature retrieval;
* computational reproduction;
* alternative model implementations;
* sensitivity analysis;
* evidence comparison;
* human review when required by policy.

The adjudicator must preserve the underlying disagreement.

Example:

```yaml
adjudication:
  status: "RESOLVED_SUPPORT"

  basis:
    - "independent_literature_review"
    - "computational_reproduction"

  unresolved_limitations:
    - "small source cohort"
```

Adjudication is not permitted to erase previous review events.

---

# 8. Human Review

Human review is represented independently from agent validation.

Example:

```yaml
human_review:
  status: "REVIEWED"

  reviews:
    - review_id: "human-rev-001"
      reviewer:
        name: "..."
        role: "Clinical Physiologist"

      scope:
        - "clinical_plausibility"

      verdict: "APPROVED"
```

Human review may confirm, reject, qualify, or challenge agent-generated evidence.

Human review does not rewrite historical agent reviews.

---

# 9. Human Authorization

Human review and downstream authorization are separate concepts.

A human reviewer may determine that an artifact is scientifically acceptable for a particular purpose without asserting that every possible use is appropriate.

Example:

```yaml
authorization:

  exploratory_research:
    status: "ALLOWED"

  third_party_research:
    status: "ALLOWED_WITH_DISCLOSURE"

  iip_research:
    status: "ALLOWED"

  iip_production:
    status: "REQUIRES_HUMAN_APPROVAL"

  clinical:
    status: "PROHIBITED"
```

Authorization policies are enforced independently from the evidence state.

---

# 10. Default Downstream Policy

The default project policy is:

| Use                                 | Human review                                       |
| ----------------------------------- | -------------------------------------------------- |
| Internal exploration                | Not required                                       |
| Hypothesis generation               | Not required                                       |
| Agent-to-agent research             | Not required                                       |
| Internal computational experiments  | Not required unless designated high risk           |
| Third-party exploratory research    | Encouraged                                         |
| Third-party published dataset/model | Strongly encouraged / policy-dependent             |
| IIP research dataset                | Required according to project policy               |
| IIP production dataset              | **Mandatory**                                      |
| Clinical application                | **Mandatory and subject to additional governance** |
| Safety-critical application         | **Mandatory**                                      |

This table is a policy baseline and may be tightened for specific asset classes.

---

# 11. IIP Production Gate

An asset must not be included in a designated IIP production dataset unless:

1. the target content hash matches the reviewed artifact;
2. deterministic validation passes;
3. required scientific validation requirements pass;
4. required human review has occurred;
5. the human authorization explicitly covers IIP production use;
6. no unresolved critical challenge exists;
7. the manifest is internally consistent.

An agent-supported artifact may therefore progress through research workflows while remaining blocked from IIP production.

---

# 12. Third-Party Use

Third parties may use artifacts according to their authorization status.

Where human review has not occurred, the artifact should expose its validation provenance clearly.

Example:

```text
Validation:
  Agent-supported
  Human review: Not performed

Use:
  Exploratory research permitted
  IIP production prohibited
```

The system should favor transparency over presenting an artificially binary validated/unvalidated label.

---

# 13. Staleness

The target file SHA-256 must be checked whenever validation status is consumed.

If:

```text
SHA256(current asset) != target_file.sha256
```

then the associated validation evidence is stale for that content snapshot.

The manifest may retain historical evidence, but current authorization must not inherit stale validation automatically.

---

# 14. Proposed Manifest Schema

Example:

```yaml
review_manifest_version: "2.0.0"

target_file:
  path: "knowledge_base/physiology/variables.yaml"
  sha256: "..."

reviews:

  - review_id: "rev-001"
    reviewed_at: "..."
    reviewer:
      kind: "validator"
      identity:
        name: "validate_kb.py"
        version: "v2.4.0"
        commit_sha: "..."

    scope:
      - "yaml_syntax"
      - "json_schema"
      - "unit_dimensions"

    verdict: "PASSED"
    confidence: 1.0
    findings: []

  - review_id: "rev-002"
    reviewed_at: "..."
    reviewer:
      kind: "ai_agent"
      identity:
        provider: "..."
        model_name: "..."
        model_version: "..."
        agent_role: "literature_verification"
        methodology_version: "v2"
        system_prompt_sha256: "..."

      independence_group: "literature-agent-a"

    scope:
      - "literature_fidelity"
      - "parameter_range"

    verdict: "SUPPORTED"
    confidence: 0.91
    findings: []

claims:

  - claim_id: "claim-001"
    statement: "..."
    status: "SUPPORTED"

    evidence:
      - source_id: "doi:..."

    supporting_reviews:
      - "rev-002"

    challenging_reviews: []

challenges: []

adjudication:
  status: "NOT_REQUIRED"

validation:
  state: "AGENT_SUPPORTED"

  deterministic:
    status: "PASSED"

  agent_evidence:
    independent_reviewers: 3
    supporting: 3
    disputing: 0

  computational:
    status: "PASSED"

human_review:
  status: "NOT_REVIEWED"

authorization:

  exploratory_research:
    status: "ALLOWED"

  third_party_research:
    status: "ALLOWED_WITH_DISCLOSURE"

  iip_research:
    status: "ALLOWED"

  iip_production:
    status: "REQUIRES_HUMAN_APPROVAL"

  clinical:
    status: "PROHIBITED"
```

---

# 15. Verification Tooling

The existing validation tooling should be extended to support:

### `validate`

Verify:

* YAML syntax;
* schema;
* target hash;
* manifest schema;
* stale reviews;
* invalid references;
* invalid state transitions.

### `review`

Create a review event.

```bash
ocpe validate review <asset>
```

### `aggregate`

Recalculate evidence state.

```bash
ocpe validate aggregate <asset>
```

### `challenge`

Create a scientific challenge.

```bash
ocpe validate challenge <asset> --claim claim-001
```

### `authorize`

Evaluate downstream usage policy.

```bash
ocpe validate authorize <asset> --use iip-production
```

### `explain`

Produce a human-readable validation report.

```bash
ocpe validate explain <asset>
```

The report should explain **why** an asset has its current status rather than simply returning `PASS`.

---

# 16. CI/CD Enforcement

CI must enforce downstream policy rather than universally requiring human review.

For example:

```text
                    TARGET ASSET
                         │
                         ▼
                Deterministic Checks
                         │
                  ┌──────┴──────┐
                  │             │
                 FAIL          PASS
                  │             │
                BLOCK           ▼
                         Agent Evidence
                               │
                         ┌─────┴─────┐
                         │           │
                    Disagreement   Support
                         │           │
                         ▼           ▼
                    Challenge    Continue
                         │
                         ▼
                    Adjudication
                         │
                         ▼
                  Evidence State
                         │
             ┌───────────┴───────────┐
             │                       │
      Exploratory Use          High-Risk Use
             │                       │
             ▼                       ▼
       Policy Evaluation       Human Review Gate
                                     │
                                     ▼
                              Authorization
```

A low-risk exploratory workflow may proceed with agent-supported evidence.

An IIP production workflow must stop until the required human authorization exists.

---

# 17. Consequences

## Positive

### Autonomous Progress

Agents can advance research and engineering work without waiting for human review.

### Reduced Human Bottleneck

Human expertise is concentrated on high-value decisions, novel claims, disputes, and consequential downstream applications.

### Better Scientific Provenance

The system records not merely whether an artifact passed review, but why and on what evidence.

### Explicit Uncertainty

Disputed and unresolved claims remain visible rather than being hidden behind a binary approval state.

### Reproducibility

Content hashes and reviewer provenance allow validation events to be reconstructed.

### Risk-Proportionate Governance

Exploratory research and production/clinical use can operate under different validation requirements.

### Self-Auditing Knowledge Base

Agents can challenge previously accepted claims and initiate new evidence-gathering workflows.

---

## Negative / Risks

### Correlated Agent Errors

Multiple agents may reach the same incorrect conclusion.

**Mitigation:** Track independence groups and methodological diversity. Do not equate vote count with truth.

### Increased Schema Complexity

The manifest becomes more sophisticated than a simple review log.

**Mitigation:** Provide schema validation, typed Python models, CLI tooling, and generated human-readable reports.

### Evidence Aggregation Is Nontrivial

There is no universally correct mathematical formula for converting heterogeneous evidence into a single confidence value.

**Mitigation:** Preserve raw evidence and use policy-based derived states. Avoid presenting derived confidence as objective probability.

### Agent Validation Can Create False Confidence

A high-consensus result may appear more authoritative than it is.

**Mitigation:** Explicitly label AI-generated evidence and maintain separate human-review and authorization states.

### Sidecar File Growth

Every asset may accumulate substantial provenance data.

**Mitigation:** Use append-only event structures and tooling to summarize historical events while retaining machine-readable provenance.

### Human Review Remains Necessary for High-Consequence Uses

The architecture does not eliminate expert review.

**Mitigation:** Make human review a policy-controlled authorization requirement rather than a universal development bottleneck.

---

# 18. Non-Goals

This ADR does not claim that:

* AI consensus establishes scientific truth;
* AI agents replace domain experts;
* numerical agreement proves physiological validity;
* validation confidence represents a calibrated probability of correctness;
* an agent-approved artifact is automatically suitable for clinical use;
* all third-party use is automatically authorized.

The system is a **provenance and evidence-management framework**, not a replacement for scientific judgment.

---

# 19. Guiding Principle

OCPE should operate according to the following principle:

> **Agents may generate, test, reproduce, challenge, and accumulate scientific evidence autonomously. Humans determine when that evidence is sufficient for higher-consequence uses.**

This allows the computational physiology knowledge base to continue developing continuously while preserving stronger governance boundaries around IIP production datasets, clinical applications, and other designated high-risk outputs.
