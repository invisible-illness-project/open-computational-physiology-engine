# Lamina Integration Contract

Lamina is the downstream home of **signal processing**: ECG, PPG, EDA and
respiration processing, HRV computation, signal quality assessment and
multimodal fusion. This document fixes the boundary: what Lamina owns, what
it consumes from OCPE, and the contract it must honor.

## Ownership

| Lamina owns | OCPE owns |
|---|---|
| Signal processing algorithms (filters, detectors, beat picking, quality metrics) | The identifiers for the quantities algorithms produce |
| HRV and derived-metric **computation** | Derived-metric *definitions* (algorithm declarations as package content) |
| Signal quality assessment logic | The vocabulary for declaring performance and failure modes |
| Device-level signal models (within its scope) | Measurement-method semantics packages use to describe devices |
| Raw and processed signal storage | The observation exchange record format |

## What Lamina consumes from OCPE

1. **Canonical quantity identifiers**: heart-rate variables, derived metrics
   (HRV indices), latent constructs — so Lamina's outputs label themselves
   with the same identifiers everyone else uses.
2. **Derived-metric definitions**: `derived_metric` entities declare the
   algorithm (`computation.method`, `formula`, `parameters`,
   `input_requirements`) whose exact semantics (window, artifact handling)
   Lamina must implement faithfully.
3. **Measurement-method semantics**: what a method measures, in which mode
   (`direct`/`estimated`/`derived`), with context-qualified performance.
4. **Units and dimensions**: beats vs. events-per-second, milliseconds vs.
   seconds — the registry resolves them.
5. **The observation contract** (see `docs/observation-exchange.md`): the
   format for everything Lamina emits.

## The contract Lamina must honor

1. **Output labelling.** Every computed value is emitted as an observation
   record whose `quantity` is a canonical OCPE identifier and whose
   `value_kind` is `derived` (algorithmic outputs) or `estimated` (e.g.
   latent-construct estimates) — never `measured` unless the value came
   directly from a sensor observation.
2. **Metric fidelity.** When a `derived_metric` entity declares window
   length, artifact handling or input requirements, Lamina's implementation
   conforms or documents the deviation in its own conformance metadata.
3. **Method integrity.** Records carry the producing `method` entity; a
   method's declared `measures` list is the authority on what it produces,
   and the observation validator enforces consistency.
4. **Provenance.** Processing pipelines (including AI-agent-written stages)
   are recorded in record/package provenance.
5. **No identifier minting.** Lamina never creates physiological identifiers;
   it requests/derives them in domain packages when a quantity is missing.

## Data flow

```
sensors ──► Lamina processing pipelines (ECG/PPG/EDA/respiration, HRV)
                │  emits observation records
                ▼
        OCPE observation exchange (quantity ids, units, value_kind,
        method, quality, provenance)
                │
                ▼
        applications / datasets / MOSAIC validation
```
