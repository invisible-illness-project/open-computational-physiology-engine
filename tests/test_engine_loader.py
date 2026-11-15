"""Engine tests: loading, CURIE grammar, registry behaviour."""

from ocpe.loader import (
    discover,
    load_package,
    load_registry,
    parse_curie,
)
from ocpe import spec


def test_parse_curie_valid():
    assert parse_curie("ocpe:cardiovascular/heart-rate") == ("cardiovascular", "heart-rate", None)
    assert parse_curie("ocpe:conditions.pots/neuropathic-pots") == ("conditions.pots", "neuropathic-pots", None)
    assert parse_curie("ocpe:models.baroreflex-geddes-2022/baroreflex-geddes-2022#RalpM") == (
        "models.baroreflex-geddes-2022", "baroreflex-geddes-2022", "RalpM")


def test_parse_curie_rejects_non_curie():
    assert parse_curie("heart-rate") is None
    assert parse_curie("ocpe:BadCase/x") is None
    assert parse_curie("ocpe:cardiovascular/Not_Kebab") is None
    assert parse_curie("") is None


def test_core_package_loads():
    reg = load_registry([], include_core=True)
    assert "core" in reg.packages
    assert len(reg.predicate_tokens()) == 12
    assert len(reg.functional_form_tokens()) == 7


def test_repo_packages_load():
    reg = load_registry()
    summary = reg.summary()
    assert summary["by_kind"]["variable"] >= 25
    assert summary["by_kind"]["relationship"] >= 10
    assert summary["by_kind"]["condition"] >= 8
    assert not reg.issues.errors


def test_duplicate_entity_ids_flagged(tmp_path):
    pkg = tmp_path / "dup"
    pkg.mkdir()
    (pkg / "package.yaml").write_text(
        'id: dup\nname: Dup\nversion: "1.0.0"\nocpe_spec: ">=0.1.0 <0.2.0"\n'
        'description: test\ncontents: [a.yaml]\n'
    )
    ent = (
        'ocpe: "0.1"\npackage: dup\nentities:\n'
        '  - {id: ocpe:dup/x, kind: concept, label: X, concept_type: phenomenon}\n'
        '  - {id: ocpe:dup/x, kind: concept, label: X2, concept_type: phenomenon}\n'
    )
    (pkg / "a.yaml").write_text(ent)
    reg = load_registry([pkg], include_core=False)
    assert any(i.code == "duplicate-id" and i.severity == "error" for i in reg.issues.issues)


def test_missing_content_file_is_load_error(tmp_path):
    pkg = tmp_path / "missing"
    pkg.mkdir()
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


def test_discover_skips_migration_archive():
    found = discover(["."])
    assert all("migration_archive" not in p.parts for p in found)
