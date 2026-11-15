"""Engine tests: loading, CURIE grammar, registry behaviour, path containment."""

import os

import pytest

from ocpe import spec
from ocpe.loader import discover, load_package, load_registry, parse_curie


def test_parse_curie_valid():
    assert parse_curie("ocpe:example-vitals/heart-rate") == ("example-vitals", "heart-rate", None)
    assert parse_curie("ocpe:research.cardiovascular/stroke-volume") == ("research.cardiovascular", "stroke-volume", None)
    assert parse_curie("ocpe:models.demo/demo#Rtot") == ("models.demo", "demo", "Rtot")


def test_parse_curie_rejects_non_curie():
    assert parse_curie("heart-rate") is None
    assert parse_curie("ocpe:BadCase/x") is None
    assert parse_curie("ocpe:pkg/Not_Kebab") is None
    assert parse_curie("") is None


def test_core_package_loads():
    reg = load_registry([], include_core=True)
    assert "core" in reg.packages
    assert len(reg.predicate_tokens()) == 12
    assert len(reg.functional_form_tokens()) == 7


def test_core_package_validates_clean():
    from ocpe.validator import validate_registry

    reg = load_registry([])
    rep = validate_registry(reg)
    assert rep.ok, [str(i) for i in rep.errors]


def test_no_default_domain_packages():
    """OCPE ships no domain content: a default load yields only the core vocabulary."""
    reg = load_registry()
    assert list(reg.packages) == ["core"]


def test_duplicate_entity_ids_flagged(pkg_factory):
    pkg = pkg_factory("dup", entities=[
        {"id": "ocpe:dup/x", "kind": "concept", "label": "X", "concept_type": "phenomenon"},
        {"id": "ocpe:dup/x", "kind": "concept", "label": "X2", "concept_type": "phenomenon"},
    ])
    reg = load_registry([pkg], include_core=False)
    assert any(i.code == "duplicate-id" and i.severity == "error" for i in reg.issues.issues)


def test_missing_content_file_is_load_error(pkg_factory):
    pkg = pkg_factory("missing", entities=None)
    (pkg / "package.yaml").write_text(
        'id: missing\nname: Missing\nversion: "1.0.0"\nocpe_spec: ">=0.1.0 <0.2.0"\n'
        'description: test\ncontents: [nope.yaml]\n'
    )
    loaded = load_package(pkg)
    assert any(i.code == "content-missing" and i.severity == "error" for i in loaded.load_issues.issues)


def test_spec_root_resolution():
    root = spec.spec_root()
    assert (root / "core" / "meta.yaml").is_file()
    assert spec.spec_version() == "0.1.0"


def test_discover_finds_nested_packages(pkg_factory):
    a = pkg_factory("disc-a", entities=[{"id": "ocpe:disc-a/x", "kind": "concept", "label": "X", "concept_type": "phenomenon"}])
    b = pkg_factory("nest/disc-b", entities=[{"id": "ocpe:disc-b/x", "kind": "concept", "label": "X", "concept_type": "phenomenon"}])
    found = discover([a.parent])
    assert {p.name for p in found} >= {"disc-a", "disc-b"}


# --------------------------------------------------------------------------- path containment
def _pkg_with_content(tmp_path, rel):
    pkg = tmp_path / "pc"
    pkg.mkdir()
    (pkg / "package.yaml").write_text(
        'id: pc\nname: PC\nversion: "1.0.0"\nocpe_spec: ">=0.1.0 <0.2.0"\ndescription: t\n'
        f'contents: [{rel}]\n'
    )
    return pkg


def test_absolute_content_path_rejected(tmp_path):
    outside = tmp_path / "outside.yaml"
    outside.write_text("ocpe: '0.1'\npackage: pc\nentities: []\n")
    pkg = _pkg_with_content(tmp_path, str(outside))
    loaded = load_package(pkg)
    assert any(i.code == "path-escape" for i in loaded.load_issues.issues)


def test_traversal_content_path_rejected(tmp_path):
    (tmp_path / "up.yaml").write_text("ocpe: '0.1'\npackage: pc\nentities: []\n")
    pkg = _pkg_with_content(tmp_path, "../up.yaml")
    loaded = load_package(pkg)
    assert any(i.code == "path-escape" for i in loaded.load_issues.issues)


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="no symlink support")
def test_symlink_escape_rejected(tmp_path):
    outside = tmp_path / "secret.yaml"
    outside.write_text("ocpe: '0.1'\npackage: pc\nentities: []\n")
    pkg = _pkg_with_content(tmp_path, "link.yaml")
    os.symlink(outside, pkg / "link.yaml")
    loaded = load_package(pkg)
    assert any(i.code == "path-escape" for i in loaded.load_issues.issues)


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="no symlink support")
def test_internal_symlink_allowed(tmp_path):
    pkg = _pkg_with_content(tmp_path, "link.yaml")
    (pkg / "real.yaml").write_text(
        "ocpe: '0.1'\npackage: pc\nentities:\n  - {id: ocpe:pc/x, kind: concept, label: X, concept_type: phenomenon}\n"
    )
    os.symlink(pkg / "real.yaml", pkg / "link.yaml")
    loaded = load_package(pkg)
    assert not loaded.load_issues.errors
    assert [e["id"] for e in loaded.entities()] == ["ocpe:pc/x"]
