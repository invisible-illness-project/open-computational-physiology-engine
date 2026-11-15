"""Engine tests: schema + semantic validation, including negative cases."""

import pytest

from ocpe import load, validate
from ocpe.loader import load_registry
from ocpe.validator import validate_instance, validate_registry, validate_observation
from ocpe import units


def _write_pkg(tmp_path, pid, manifest_extra="", doc=""):
    pkg = tmp_path / pid
    pkg.mkdir()
    (pkg / "package.yaml").write_text(
        f'id: {pid}\nname: {pid}\nversion: "1.0.0"\nocpe_spec: ">=0.1.0 <0.2.0"\n'
        f'description: test\ncontents: [doc.yaml]\n{manifest_extra}'
    )
    (pkg / "doc.yaml").write_text(f'ocpe: "0.1"\npackage: {pid}\nentities:\n{doc}')
    return pkg


def test_repo_packages_validate_clean():
    reg = load_registry()
    rep = validate_registry(reg)
    assert rep.ok, [str(i) for i in rep.issues if i.severity == "error"]


def test_namespace_violation_flagged(tmp_path):
    pkg = _write_pkg(tmp_path, "nsviol", doc="  - {id: ocpe:other/x, kind: concept, label: X, concept_type: phenomenon}\n")
    reg = load_registry([pkg], include_core=True)
    rep = validate_registry(reg, ["nsviol"])
    assert any(i.code == "namespace" for i in rep.errors)


def test_undeclared_dependency_flagged(tmp_path):
    pkg = _write_pkg(tmp_path, "depfree", doc="  - {id: ocpe:depfree/x, kind: relationship, label: r, subject: ocpe:core/causes, predicate: CAUSES, object: ocpe:cardiovascular/heart-rate}\n")
    reg = load_registry([pkg], include_core=True)
    rep = validate_registry(reg, ["depfree"])
    assert any(i.code == "undeclared-dependency" for i in rep.errors)


def test_dimension_mismatch_flagged(tmp_path):
    doc = (
        "  - id: ocpe:dimwrong/x\n    kind: variable\n    label: X\n"
        "    dimension: volume\n    canonical_unit: mm[Hg]\n"
    )
    pkg = _write_pkg(tmp_path, "dimwrong", doc=doc)
    reg = load_registry([pkg], include_core=True)
    rep = validate_registry(reg, ["dimwrong"])
    assert any(i.code == "dimension-mismatch" for i in rep.errors)


def test_unknown_unit_flagged(tmp_path):
    doc = (
        "  - id: ocpe:unitwrong/x\n    kind: variable\n    label: X\n"
        "    dimension: volume\n    canonical_unit: furlongs\n"
    )
    pkg = _write_pkg(tmp_path, "unitwrong", doc=doc)
    reg = load_registry([pkg], include_core=True)
    rep = validate_registry(reg, ["unitwrong"])
    assert any(i.code == "unit" for i in rep.errors)


def test_model_equation_undeclared_symbol_flagged(tmp_path):
    doc = (
        "  - id: ocpe:symbad/m\n    kind: model\n    label: M\n    formalism: ode\n"
        "    symbols: [{symbol: x, role: state}]\n"
        "    equations: [{id: eq1, expression_latex: 'x = y', inputs: [x], outputs: [z]}]\n"
    )
    pkg = _write_pkg(tmp_path, "symbad", doc=doc)
    reg = load_registry([pkg], include_core=True)
    rep = validate_registry(reg, ["symbad"])
    codes = {i.code for i in rep.errors}
    assert "undeclared-symbol" in codes


def test_deprecated_requires_deprecation_block(tmp_path):
    doc = "  - {id: ocpe:dep/x, kind: concept, label: X, concept_type: phenomenon, status: deprecated}\n"
    pkg = _write_pkg(tmp_path, "dep", doc=doc)
    reg = load_registry([pkg], include_core=True)
    rep = validate_registry(reg, ["dep"])
    assert any(i.code == "deprecation" for i in rep.errors)


def test_observation_validation():
    reg = load_registry()
    ok = validate_observation(
        {"quantity": "ocpe:cardiovascular/heart-rate", "value": 72, "unit": "/min", "value_kind": "measured"},
        reg,
    )
    assert ok.ok, [str(i) for i in ok.issues]
    # latent constructs cannot be 'measured'
    bad = validate_observation(
        {"quantity": "ocpe:autonomic/sympathetic-tone", "value": 0.5, "unit": "1", "value_kind": "measured"},
        reg,
    )
    assert any(i.code == "latent-measured" for i in bad.errors)
    # dimension-mismatched unit rejected
    wrong = validate_observation(
        {"quantity": "ocpe:cardiovascular/heart-rate", "value": 72, "unit": "mm[Hg]", "value_kind": "measured"},
        reg,
    )
    assert any(i.code == "unit" for i in wrong.errors)


def test_units_conversion():
    assert abs(units.convert(1.0, "/s", "/min") - 60.0) < 1e-9
    assert abs(units.convert(4500.0, "mL", "L") - 4.5) < 1e-9
    with pytest.raises(units.UnitError):
        units.convert(1.0, "mL", "mm[Hg]")


def test_schema_layer_direct():
    rep = validate_instance({"id": "ocpe:x/y"}, "variable.schema.json")
    assert not rep.ok  # missing kind/label/dimension/canonical_unit
