# Open Computational Physiology Engine (OCPE)

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Spec: 0.1.0 provisional](https://img.shields.io/badge/spec-0.1.0-informational)](specification/)

OCPE is an open, versioned **computational physiology interoperability
engine**. It defines the common language — schemas, canonical identifiers,
semantic contracts and validation mechanisms — through which AI agents,
researchers, computational models, applications and datasets represent and
exchange physiological knowledge.

OCPE defines **how physiological information is represented and interpreted**.
It does not own or curate the research content expressed in that language:
cardiovascular knowledge, disease definitions, clinical protocols, wearable
specifications, population definitions, literature reviews and evidence claims
all live in **independently versioned external packages** that anyone can
author, distribute and evolve without touching the OCPE repository.

OCPE is **not** a simulation engine, not a dataset generator and not a signal
processor.

- Numerical model execution, synthetic patients/cohorts, trajectory simulation → **MOSAIC**
- ECG/PPG/EDA signal processing and derived-metric computation → **Lamina**
- The language all of the above speak → **OCPE** (here)

## Repository layout

```
specification/     The normative, language-independent contract: JSON Schemas
                   (draft-07), identifier grammar, unit registry, predicate
                   vocabulary, functional forms, compatibility rules.
implementations/
  python/          The reference engine (pip-installable `ocpe` package + CLI):
                   loader, schema+semantic validator, resolver, units,
                   compatibility differ, conformance runner.
conformance/       The official conformance suite: synthetic fixtures, expected
                   results and language-independent test vectors.
docs/              Mission, architecture, specification reference, authoring
                   guides, versioning policy, integration contracts.
tests/             Repository-level tests (conformance runner).
```

There is intentionally **no `packages/` directory**: OCPE ships no domain
content. The only bundled package is the specification-level `core` vocabulary
(predicates and functional forms).

## Quick start

```bash
pip install implementations/python          # or: pip install dist/ocpe-*.whl

ocpe validate path/to/domain-package        # schema + semantic validation
ocpe resolve ocpe:my-package/my-variable    # identifier / alias / symbol resolution
ocpe diff old-release/ new-release/         # classify changes between package versions
ocpe check-observation record.yaml          # validate an observation exchange record
ocpe conformance conformance/               # run the official conformance suite
```

Python API:

```python
import ocpe

reg = ocpe.load(["path/to/domain-package"])  # + the bundled core vocabulary
report = ocpe.validate(reg)
assert report.ok

r = ocpe.Resolver(reg).resolve("ocpe:my-package/my-variable")
print(r.id, r.entity.kind)
```

Validation is **structural and semantic**: it establishes that content is
well-formed, internally consistent and resolvable. It never asserts scientific
validity.

## Who OCPE is for

- **AI agents** producing or consuming structured physiological knowledge
  (see `docs/ai-agent-guide.md`).
- **Researchers** exchanging variables, relationships, models and evidence
  without reimplementing incompatible schemas (see
  `docs/package-authoring-guide.md`).
- **Model authors** declaring a computational model's identity, inputs,
  outputs, parameters, assumptions, units and evidence — execution not
  included, execution elsewhere (see `docs/mosaic-integration.md`).
- **Application and dataset authors** describing physiological measurements
  with canonical identifiers and units (see `docs/observation-exchange.md`).
- **Engine implementers** building OCPE-compatible tooling in any language
  (see `docs/implementation-guide.md` and `docs/conformance-guide.md`).

## Documentation

| Document | Contents |
|---|---|
| `docs/mission.md` | Scope, principles, what OCPE owns vs. what downstream owns |
| `docs/architecture.md` | Layers, dependencies, extension points |
| `docs/specification-reference.md` | The schemas and shared machinery, field by field |
| `docs/package-authoring-guide.md` | How to author an external domain package |
| `docs/ai-agent-guide.md` | Contract for AI agents authoring or consuming OCPE content |
| `docs/versioning-policy.md` | Identifier stability, version compatibility, change classes |
| `docs/observation-exchange.md` | The observation/measurement exchange contract |
| `docs/conformance-guide.md` | The conformance suite and how to demonstrate interoperability |
| `docs/implementation-guide.md` | Building an OCPE engine in another language |
| `docs/mosaic-integration.md` / `docs/lamina-integration.md` | Downstream integration boundaries |

## Status

Specification 0.1.0, provisional. The engine is a lightweight, deterministic
Python implementation with no scientific-computing dependencies (PyYAML +
jsonschema only). Architectural decisions are recorded in the repository's
commit history and summarized in `docs/architecture.md`.

**Licensing:** [Apache License 2.0](LICENSE) — applies to the entire
repository: the reference engine, the specification (JSON Schemas and core
vocabularies), the conformance suite and the documentation. Attribution and
third-party notices live in [NOTICE](NOTICE). See
[docs/licensing.md](docs/licensing.md) for the decision record.
