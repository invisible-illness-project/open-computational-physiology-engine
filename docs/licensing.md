# OCPE Licensing — Outstanding Owner Decision

**Status: UNRESOLVED. No license has been chosen. Do not assume one.**

The repository currently carries no `LICENSE` file. Software metadata says so
explicitly (`implementations/python/pyproject.toml`:
`license = { text = "UNSPECIFIED - see repository LICENSE status" }`, and the
core package manifest declares `license: UNSPECIFIED`). This is a deliberate
placeholder, not an omission to be silently fixed: choosing a license is the
project owner's decision, and it has not been made.

## What must be decided

1. **Software license** — covers `implementations/python/` (the reference
   engine and CLI), the conformance runner, and any build tooling.
   Considerations: downstream adoption by research and commercial projects;
   patent clauses (e.g. Apache-2.0 vs MIT/BSD); compatibility with the
   organization's other software.
2. **Specification/content license** — covers `specification/` (JSON Schemas,
   core YAML vocabularies), `conformance/` fixtures and vectors, and
   `docs/`. Specifications are frequently licensed differently from code
   (e.g. CC-BY-4.0 / CC0 / Apache-2.0) so that implementing the spec in any
   language is unambiguously permitted. The schemas must remain freely
   implementable for the interoperability goal to hold; test vectors should
   be usable by conformance runners in any license regime.

## Recommended resolution path

- Owner selects the software license and the specification license.
- Add `LICENSE` (software) at the repository root and, if different,
  a `specification/LICENSE` (or `docs/LICENSE`) for content.
- Replace the `UNSPECIFIED` placeholders in `pyproject.toml` and
  `specification/core/package.yaml` with the SPDX expression.
- Record the decision in `specification/versions/CHANGELOG.md`.

## Until then

- Treat the repository as **all rights reserved** for any use beyond reading.
- Do not copy conformance fixtures, schemas or engine code into other
  projects.
- External domain packages are their authors' own works; their licenses are
  declared per package in each manifest's `license` field (SPDX expression or
  `UNSPECIFIED`).
