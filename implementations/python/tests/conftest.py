"""Shared helpers for engine tests: synthetic in-memory packages (no domain content)."""

import textwrap

import pytest
import yaml

SPEC = ">=0.1.0 <0.2.0"


def write_package(root, pid, entities=None, references=None, version="1.0.0", deps=None, doc_name="doc.yaml", manifest_extra=None):
    """Create a package directory under ``root`` and return its Path."""
    pkg = root / pid
    pkg.mkdir(parents=True, exist_ok=True)
    manifest = {
        "id": pid,
        "name": pid,
        "version": version,
        "ocpe_spec": SPEC,
        "description": "synthetic test package (no scientific content)",
        "contents": [doc_name] if entities is not None or references is not None else [],
    }
    if deps:
        manifest["dependencies"] = deps
    if manifest_extra:
        manifest.update(manifest_extra)
    (pkg / "package.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    if entities is not None or references is not None:
        doc = {"ocpe": "0.1", "package": pid}
        if entities is not None:
            doc["entities"] = entities
        if references is not None:
            doc["references"] = references
        (pkg / doc_name).write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return pkg


@pytest.fixture()
def pkg_factory(tmp_path):
    return lambda pid, **kw: write_package(tmp_path, pid, **kw)
