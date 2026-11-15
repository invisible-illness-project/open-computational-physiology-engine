# OCPE — Python reference engine

Installable reference implementation of the OCPE specification (loader,
validator, resolver, units, compatibility, CLI). The normative specification
it implements lives in `../../specification/` and is bundled into the wheel as
`ocpe/_spec`, so an installed engine is self-contained.

```bash
pip install -e .
ocpe --help
```
