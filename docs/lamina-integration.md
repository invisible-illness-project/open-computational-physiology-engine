# Lamina Integration Contract

Lamina is the downstream signal-processing application: ECG/PPG/EDA signal
synthesis and processing, and derived HRV metric computation from signals
(see `docs/mission.md`, "Out of scope"). OCPE is upstream of Lamina: it
supplies the measurement-method specifications, canonical quantity
identifiers and derived-metric definitions that make Lamina's outputs
interpretable by anything downstream. This document is the contract between
the two. It is grounded in `migration_archive/MIGRATION_NOTES.md`,
`packages/wearables/polar-h10.yaml`, `packages/wearables/photoplethysmography.yaml`,
`packages/autonomic/metrics.yaml` and `specification/core/identifiers.md`.

## What Lamina receives from the pre-0.1 repository

The pre-0.1 signal synthesis component was removed from the active repository
and is preserved — temporarily — under `migration_archive/`:

| Component | What it is |
|---|---|
| `sensor_models/wearable_sensors.py` | ECG/PPG signal synthesis (Polar H10 ECG simulation, PPG optical waveform synthesis) |

Once Lamina confirms extraction, the archive entry is deleted; it remains
recoverable from git history at tag `pre-architectural-refactor` (commit
`c0d8678`). Synthetic data generation itself is out of scope for OCPE, so the
component has no future in this repository — it belongs in Lamina.

## What Lamina consumes from OCPE at runtime

**Measurement-method specifications** — `packages/wearables`. Each sensor is
a `measurement_method` entity declaring what it measures (`measures`, with
`target` quantity CURIE and `mode: direct | derived`), device specifications,
context-qualified `performance` arrays, `failure_modes` and artifact
handling. The two current methods:

- `ocpe:wearables/polar-h10` — dry-electrode ECG chest strap. Measures
  `ocpe:cardiovascular/rr-interval` directly and
  `ocpe:cardiovascular/heart-rate` as device-derived from RR intervals.
  Specifications: 130 Hz sampling, 1 ms RR resolution, BLE/ANT+. Performance
  is agreement against standard 12-lead ECG, qualified by activity: at rest
  ICC 0.99, bias 0.05 ms, LoA -2.3 to 2.4 ms; at high intensity ICC 0.96,
  bias 0.2 ms, LoA -15.4 to 15.8 ms (Schaffarczyk 2022, DOI
  `10.3390/s22176536`). Artifact handling: reject beats with >15% deviation
  from rolling mean RR interval.
- `ocpe:wearables/optical-ppg` — optical PPG as implemented in consumer
  wearables. Measures `ocpe:cardiovascular/heart-rate` and
  `ocpe:cardiovascular/rr-interval` both as derived; the RR-interval entry
  carries the note that this is pulse rate variability (PRV) as an
  RR-interval proxy, and that agreement with true RR intervals is
  context-dependent. Specifications: 50 Hz sampling, green/red/infrared
  wavelengths. Artifact handling: adaptive filtering using tri-axial
  accelerometer data. Its performance figures carry a provenance gap — see
  the contract below.

The package description states the governing rule: performance figures are
agreement statistics against a reference method in specific activity contexts;
they do not transfer automatically to other populations or activities.

**Canonical identifiers** — every quantity Lamina outputs has exactly one
canonical identifier, a CURIE of the form `ocpe:<package>/<local-id>`
(grammar: `specification/core/identifiers.md`). Labels and legacy symbols
such as `HR` or `RMSSD` resolve to these identifiers but are not themselves
identifiers; Lamina labels outputs with the CURIE, not the label.

**Derived-metric definitions** — `packages/autonomic/metrics.yaml`. Two
registered derived metrics, both derived from
`ocpe:cardiovascular/rr-interval`, each with a `computation` declaration
(method, formula, input requirements, references) that is part of the
definition:

- `ocpe:autonomic/rmssd` — root mean square of successive RR differences;
  dimension time, canonical unit `ms`. Input requirements note the need for
  high sampling precision and sensitivity to ectopic beats and motion
  artifacts.
- `ocpe:autonomic/dfa-alpha-1` — short-term detrended fluctuation analysis
  scaling exponent over the approximately 4–16 beat window; dimension
  `dimensionless`, canonical unit `1`. Sensitive to nonstationarity, ectopic
  beats and motion artifacts.

Window choices and artifact handling are part of the metric definition: a
value computed with a different window or a different artifact policy is not
the registered metric, and Lamina must not label it as such.

## The contract Lamina must honor

1. **Label outputs with canonical CURIEs.** A heart-rate series is labeled
   `ocpe:cardiovascular/heart-rate`; an RMSSD computation is labeled
   `ocpe:autonomic/rmssd`. Resolution goes through the OCPE engine, so legacy
   symbols keep working as input aliases while output labels stay canonical.
2. **Report values with units and value_kind.** Every reported value carries a
   unit as a UCUM code registered in `specification/core/units.yaml` (for
   example `/min` for heart rate, `ms` for RR intervals and RMSSD) and a
   `value_kind` (`measured`, `estimated`, `derived`, `simulated`,
   `self_reported`). The concrete record format and its validation are defined
   in `docs/observation-exchange.md`.
3. **Never label PRV-derived intervals as `ocpe:cardiovascular/rr-interval`
   without the method qualifier.** The RR-interval identifier denotes the
   time interval between consecutive R-waves of the ECG. A PPG-derived
   interval is pulse rate variability — a proxy whose agreement with true RR
   intervals is context-dependent (at low intensity, ICC 0.85 vs ECG, on
   uncited figures). When Lamina exports PRV intervals it qualifies the
   quantity with the method — the observation record's `method` field
   (`ocpe:wearables/optical-ppg`) — so downstream consumers can distinguish
   direct ECG measurement from the optical proxy. Labeling PRV as an
   unqualified RR interval erases exactly the distinction the measurement
   layer exists to record.
4. **Respect provenance gaps.** The optical-PPG performance figures (rest
   heart-rate ICC 0.92 / Pearson r 0.91 / bias 0.5 per minute; low-intensity
   RR ICC 0.85 / r 0.84 / bias 2.1 ms) are preserved verbatim from the legacy
   source, which recorded no citation for them; the package flags this
   explicitly. Lamina must not cite these figures downstream — in papers,
   reports, model inputs or marketing claims — until they are re-sourced. The
   Polar H10 figures, by contrast, are cited to Schaffarczyk 2022 (DOI
   `10.3390/s22176536`) and remain context-qualified (rest, high intensity).
5. **Follow the computation declarations for derived metrics.** RMSSD and
   DFA alpha-1 are exchanged under their registered identifiers only when
   computed as declared; deviations are a different (unregistered) quantity
   and must not reuse the identifier.
6. **Never edit OCPE content locally.** Corrections, new sensors, re-sourced
   performance figures and new metrics are proposed upstream, in OCPE,
   through its governance process. Lamina carries no private fork of the
   measurement layer.
