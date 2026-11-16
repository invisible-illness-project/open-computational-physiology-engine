# OCPE Licensing — Decision Record

**Status: RESOLVED (owner decision, 2026-11-16).** The repository is licensed
under the **Apache License, Version 2.0**.

- License text: [`LICENSE`](../LICENSE) (repository root, verbatim Apache-2.0).
- Attribution and third-party notices: [`NOTICE`](../NOTICE).
- Copyright (c) 2026 **The Invisible Illness Project**.

## Scope: one license for the whole repository

The same license applies to everything in this repository, not just the
Python package:

| Area | Path | Covered by |
|---|---|---|
| Reference engine + CLI | `implementations/python/` | Apache-2.0 |
| Specification: JSON Schemas, core vocabularies, identifier grammar, unit registry, compatibility rules | `specification/` | Apache-2.0 |
| Conformance suite (fixtures, expected results, test vectors) | `conformance/` | Apache-2.0 |
| Documentation | `docs/`, `README.md` | Apache-2.0 |
| Build tooling, CI | `.github/`, `hatch_build.py` | Apache-2.0 |

Apache-2.0 was chosen over a split (e.g. CC-BY for content) so that
implementing the specification in any language is unambiguously permitted:
the patent grant matters for an interoperability specification, and a single
license keeps redistribution of schema files, fixtures and code together
simple. The machine-readable declarations:

- `implementations/python/pyproject.toml` — `license = "Apache-2.0"` (PEP 639
  `License-Expression`); LICENSE and NOTICE are embedded in built wheels and
  sdists under `dist-info/licenses/`.
- `specification/core/meta.yaml` — `license: Apache-2.0` (specification-level).
- `specification/core/package.yaml` — `license: Apache-2.0` (core package
  manifest field; external domain packages declare their own SPDX expression
  or `UNSPECIFIED`).

## Dependencies and contributions

**Runtime dependencies** (not bundled; each retains its own license):
PyYAML — MIT; jsonschema — MIT. Both are permissive and fully compatible
with Apache-2.0. Dev/test tooling (pytest, hatchling, build) is MIT-licensed.
No third-party source code is vendored into this repository (see NOTICE).

**Existing contributions:** every commit in this repository's history is by
The Invisible Illness Project, its maintainers, or its authorized automation
(agent/bot accounts) on the organization's behalf; there are no external
third-party contributions requiring separate consent for this licensing.

## What reusers must do

Standard Apache-2.0 conditions: retain the copyright/license notices, state
your changes, and include a copy of the license with any redistribution.
If you build a derivative work that bundles OCPE content, the attribution
notices in [`NOTICE`](../NOTICE) must remain readable per section 4(d) of
the license.

**External domain packages are NOT covered by this license.** Packages
authored by other projects declare their own license per package manifest
(`license` field, SPDX expression or `UNSPECIFIED`) and are their authors'
independent works; consuming OCPE does not impose OCPE's license on your
package content.
