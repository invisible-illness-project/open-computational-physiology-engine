"""Engine tests: compatibility — deep schema-aware diffing and version bumps.

Regression coverage for the nested-comparison defect: changes to nested
equations, parameters, relationships, observations/measurement semantics,
evidence and dependencies must all be detected and classified.
"""

import pytest

from ocpe.compatibility import (
    bump_is_sufficient,
    dependency_report,
    diff_packages,
    required_bump,
)
from ocpe.loader import load_registry

from .conftest import write_package


def _model_pkg(root, version, expression="dx = -k x", nominal=1.0, predicate="REGULATES",
               deps=None, extra_entities=None, alias=None):
    entities = [
        {"id": "ocpe:vp/alpha", "kind": "concept", "label": "Alpha", "concept_type": "phenomenon"},
        {"id": "ocpe:vp/beta", "kind": "variable", "label": "Beta", "dimension": "time", "canonical_unit": "s"},
        {"id": "ocpe:vp/gamma", "kind": "relationship", "label": "Gamma",
         "subject": "ocpe:vp/alpha", "predicate": predicate, "object": "ocpe:vp/beta"},
        {"id": "ocpe:vp/m", "kind": "model", "label": "M", "formalism": "ode",
         "symbols": [{"symbol": "x", "role": "state"}, {"symbol": "k", "role": "parameter", "nominal_value": nominal}],
         "equations": [{"id": "eq1", "expression_latex": expression, "inputs": ["x"], "parameters": ["k"], "outputs": ["x"]}],
         "assumptions": ["Assumption one.", "Assumption two."],
         "evidence": [{"claim": "Initial claim.", "basis": "definitional"}]},
    ]
    if alias:
        entities[1]["aliases"] = [alias]
    if extra_entities:
        entities.extend(extra_entities)
    return write_package(root, "vp", entities=entities, version=version, deps=deps)


def _pkg(path):
    from ocpe.loader import load_package

    return load_package(path)


def _codes(changes):
    return sorted({c.change for c in changes})


# --------------------------------------------------------------------------- nested-change detection (regressions)
def test_no_changes_no_diff(tmp_path):
    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    b = _pkg(_model_pkg(tmp_path / "b", "1.0.0"))
    assert diff_packages(a, b) == []


def test_nested_equation_expression_change_detected(tmp_path):
    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    b = _pkg(_model_pkg(tmp_path / "b", "2.0.0", expression="dx = -2k x"))
    changes = diff_packages(a, b)
    assert _codes(changes) == ["equation_changed"]
    assert changes[0].severity == "major"
    assert "expression_latex" in changes[0].detail


def test_nested_equation_io_change_detected(tmp_path):
    old = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    new_dir = tmp_path / "b"
    new = _pkg(_model_pkg(new_dir, "2.0.0"))
    doc = new_dir / "vp" / "doc.yaml"
    import yaml

    data = yaml.safe_load(doc.read_text())
    data["entities"][3]["equations"][0]["inputs"] = ["x", "k"]
    doc.write_text(yaml.safe_dump(data, sort_keys=False))
    new = _pkg(new_dir / "vp")
    changes = diff_packages(old, new)
    assert "equation_changed" in _codes(changes)


def test_nested_parameter_nominal_value_change_detected(tmp_path):
    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    b = _pkg(_model_pkg(tmp_path / "b", "2.0.0", nominal=2.5))
    changes = diff_packages(a, b)
    assert _codes(changes) == ["symbol_changed"]
    assert changes[0].severity == "major"
    assert "nominal_value" in changes[0].detail


def test_parameter_added_and_removed_detected(tmp_path):
    import yaml

    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    new_dir = tmp_path / "b"
    _pkg(_model_pkg(new_dir, "1.1.0"))
    doc = new_dir / "vp" / "doc.yaml"
    data = yaml.safe_load(doc.read_text())
    data["entities"][3]["symbols"] = data["entities"][3]["symbols"] + [{"symbol": "c", "role": "constant"}]
    doc.write_text(yaml.safe_dump(data, sort_keys=False))
    changes = diff_packages(a, _pkg(new_dir / "vp"))
    assert "symbol_added" in _codes(changes)

    removed = diff_packages(_pkg(new_dir / "vp"), a)
    assert "symbol_removed" in _codes(removed)
    assert any(c.severity == "major" for c in removed if c.change == "symbol_removed")


def test_relationship_semantics_change_detected(tmp_path):
    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    b = _pkg(_model_pkg(tmp_path / "b", "2.0.0", predicate="CAUSES"))
    changes = diff_packages(a, b)
    assert _codes(changes) == ["relationship_semantics_changed"]
    assert changes[0].severity == "major"


def test_relationship_direction_and_form_change_detected(tmp_path):
    import yaml

    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    new_dir = tmp_path / "b"
    _pkg(_model_pkg(new_dir, "2.0.0"))
    doc = new_dir / "vp" / "doc.yaml"
    data = yaml.safe_load(doc.read_text())
    data["entities"][2]["direction_of_effect"] = "negative"
    data["entities"][2]["functional_form"] = "linear"
    doc.write_text(yaml.safe_dump(data, sort_keys=False))
    changes = diff_packages(a, _pkg(new_dir / "vp"))
    codes = _codes(changes)
    assert codes == ["relationship_semantics_changed"]


def test_measurement_semantics_change_detected(tmp_path):
    import yaml

    meter = [{"id": "ocpe:vp/meter", "kind": "measurement_method", "label": "Meter", "method_type": "device",
              "measures": [{"target": "ocpe:vp/beta", "mode": "direct"}]}]
    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0", extra_entities=meter))
    new_dir = tmp_path / "b"
    _pkg(_model_pkg(new_dir, "2.0.0", extra_entities=meter))
    doc = new_dir / "vp" / "doc.yaml"
    data = yaml.safe_load(doc.read_text())
    meter_ent = [e for e in data["entities"] if e["id"] == "ocpe:vp/meter"][0]
    meter_ent["measures"] = [{"target": "ocpe:vp/beta", "mode": "estimated"}]
    doc.write_text(yaml.safe_dump(data, sort_keys=False))
    changes = diff_packages(a, _pkg(new_dir / "vp"))
    assert _codes(changes) == ["measurement_semantics_changed"]
    assert changes[0].severity == "major"


def test_evidence_attachment_change_detected(tmp_path):
    import yaml

    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    new_dir = tmp_path / "b"
    _pkg(_model_pkg(new_dir, "1.1.0"))
    doc = new_dir / "vp" / "doc.yaml"
    data = yaml.safe_load(doc.read_text())
    data["entities"][3]["evidence"] = [{"claim": "Revised claim.", "basis": "definitional"}]
    doc.write_text(yaml.safe_dump(data, sort_keys=False))
    changes = diff_packages(a, _pkg(new_dir / "vp"))
    assert _codes(changes) == ["evidence_changed"]


def test_evidence_added_detected(tmp_path):
    import yaml

    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    new_dir = tmp_path / "b"
    _pkg(_model_pkg(new_dir, "1.1.0"))
    doc = new_dir / "vp" / "doc.yaml"
    data = yaml.safe_load(doc.read_text())
    data["entities"][3]["evidence"].append({"claim": "A second claim.", "basis": "expert_opinion"})
    doc.write_text(yaml.safe_dump(data, sort_keys=False))
    changes = diff_packages(a, _pkg(new_dir / "vp"))
    assert _codes(changes) == ["evidence_added"]
    assert changes[0].severity == "minor"


def test_dependency_change_detected(tmp_path):
    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0", deps=[{"package": "conf-base", "version": ">=1.0.0"}]))
    b = _pkg(_model_pkg(tmp_path / "b", "2.0.0", deps=[{"package": "conf-base", "version": ">=2.0.0"}]))
    changes = diff_packages(a, b)
    assert _codes(changes) == ["dependency_constraint_changed"]
    assert changes[0].severity == "major"


def test_dependency_added_and_removed_detected(tmp_path):
    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    b = _pkg(_model_pkg(tmp_path / "b", "1.1.0", deps=[{"package": "conf-base", "version": "*"}]))
    changes = diff_packages(a, b)
    assert _codes(changes) == ["dependency_added"]
    assert diff_packages(b, a)[0].change == "dependency_removed"
    assert diff_packages(b, a)[0].severity == "major"


def test_observation_semantics_change_detected(tmp_path):
    """value_type/observability changes on quantities are detected (they govern observation exchange)."""
    import yaml

    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    new_dir = tmp_path / "b"
    _pkg(_model_pkg(new_dir, "2.0.0"))
    doc = new_dir / "vp" / "doc.yaml"
    data = yaml.safe_load(doc.read_text())
    data["entities"][1]["value_type"] = "discrete"
    doc.write_text(yaml.safe_dump(data, sort_keys=False))
    changes = diff_packages(a, _pkg(new_dir / "vp"))
    assert _codes(changes) == ["value_type_changed"]
    assert changes[0].severity == "major"


def test_reference_range_added_detected(tmp_path):
    import yaml

    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    new_dir = tmp_path / "b"
    _pkg(_model_pkg(new_dir, "1.1.0"))
    doc = new_dir / "vp" / "doc.yaml"
    data = yaml.safe_load(doc.read_text())
    data["entities"][1]["reference_ranges"] = [
        {"range_type": "plausibility_bound", "unit": "s", "context": {"scope_note": "fixture"}, "min": 0, "max": 100}]
    doc.write_text(yaml.safe_dump(data, sort_keys=False))
    changes = diff_packages(a, _pkg(new_dir / "vp"))
    assert _codes(changes) == ["reference_range_added"]


def test_reorder_is_not_a_change(tmp_path):
    import yaml

    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    new_dir = tmp_path / "b"
    _pkg(_model_pkg(new_dir, "1.0.0"))
    doc = new_dir / "vp" / "doc.yaml"
    data = yaml.safe_load(doc.read_text())
    m = data["entities"][3]
    m["symbols"] = list(reversed(m["symbols"]))
    m["equations"] = list(reversed(m["equations"]))
    m["assumptions"] = list(reversed(m["assumptions"]))
    doc.write_text(yaml.safe_dump(data, sort_keys=False))
    assert diff_packages(a, _pkg(new_dir / "vp")) == []


def test_label_change_is_patch(tmp_path):
    import yaml

    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    new_dir = tmp_path / "b"
    _pkg(_model_pkg(new_dir, "1.0.1"))
    doc = new_dir / "vp" / "doc.yaml"
    data = yaml.safe_load(doc.read_text())
    data["entities"][0]["label"] = "Alpha reworded"
    doc.write_text(yaml.safe_dump(data, sort_keys=False))
    changes = diff_packages(a, _pkg(new_dir / "vp"))
    assert _codes(changes) == ["label_or_description_changed"]
    assert changes[0].severity == "patch"


def test_deprecation_is_minor(tmp_path):
    import yaml

    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    new_dir = tmp_path / "b"
    _pkg(_model_pkg(new_dir, "1.1.0"))
    doc = new_dir / "vp" / "doc.yaml"
    data = yaml.safe_load(doc.read_text())
    data["entities"][0]["status"] = "deprecated"
    data["entities"][0]["deprecation"] = {"deprecated_in": "1.1.0", "reason": "fixture"}
    doc.write_text(yaml.safe_dump(data, sort_keys=False))
    changes = diff_packages(a, _pkg(new_dir / "vp"))
    assert _codes(changes) == ["identifier_deprecated", "metadata_changed"]
    assert required_bump(changes) == "minor"


def test_alias_added_is_minor_removed_is_major(tmp_path):
    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    b = _pkg(_model_pkg(tmp_path / "b", "1.1.0", alias={"value": "BT", "type": "symbol"}))
    changes = diff_packages(a, b)
    assert _codes(changes) == ["alias_added"]
    assert diff_packages(b, a)[0].change == "alias_removed"
    assert diff_packages(b, a)[0].severity == "major"


def test_kind_change_and_dimension_change_detected(tmp_path):
    import yaml

    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    new_dir = tmp_path / "b"
    _pkg(_model_pkg(new_dir, "2.0.0"))
    doc = new_dir / "vp" / "doc.yaml"
    data = yaml.safe_load(doc.read_text())
    data["entities"][1]["dimension"] = "frequency"
    doc.write_text(yaml.safe_dump(data, sort_keys=False))
    changes = diff_packages(a, _pkg(new_dir / "vp"))
    assert _codes(changes) == ["dimension_changed"]


# --------------------------------------------------------------------------- required bump / sufficiency
def test_required_bump_aggregation():
    from ocpe.compatibility import Change

    assert required_bump([]) is None
    assert required_bump([Change("label_or_description_changed", "patch", "x")]) == "patch"
    assert required_bump([Change("label_or_description_changed", "patch", "x"),
                          Change("identifier_added", "minor", "y")]) == "minor"
    assert required_bump([Change("identifier_added", "minor", "y"),
                          Change("equation_changed", "major", "z")]) == "major"


def test_bump_sufficiency_semver():
    from ocpe.compatibility import Change

    major = [Change("identifier_removed", "major", "x")]
    minor = [Change("identifier_added", "minor", "x")]
    patch = [Change("label_or_description_changed", "patch", "x")]
    assert bump_is_sufficient("1.0.0", "2.0.0", major)
    assert not bump_is_sufficient("1.0.0", "1.1.0", major)
    assert bump_is_sufficient("1.0.0", "1.1.0", minor)
    assert not bump_is_sufficient("1.0.0", "1.0.1", minor)
    assert bump_is_sufficient("1.0.0", "1.0.1", patch)
    assert not bump_is_sufficient("1.0.1", "1.0.0", patch)  # version must increase


def test_bump_sufficiency_pre_1_0_minor_is_breaking():
    from ocpe.compatibility import Change

    major = [Change("equation_changed", "major", "x")]
    minor = [Change("identifier_added", "minor", "x")]
    patch = [Change("label_or_description_changed", "patch", "x")]
    assert bump_is_sufficient("0.1.0", "0.2.0", major)
    assert not bump_is_sufficient("0.1.0", "0.1.1", major)
    assert bump_is_sufficient("0.1.0", "0.1.1", minor)
    assert bump_is_sufficient("0.1.0", "0.1.1", patch)


def test_diff_ignores_manifest_release_mechanics(tmp_path):
    import yaml

    a = _pkg(_model_pkg(tmp_path / "a", "1.0.0"))
    new_dir = tmp_path / "b"
    _pkg(_model_pkg(new_dir, "1.0.1"))
    manifest = new_dir / "vp" / "package.yaml"
    data = yaml.safe_load(manifest.read_text())
    data["contents"] = ["doc.yaml", "extra.yaml"]  # release mechanics, not semantics
    manifest.write_text(yaml.safe_dump(data, sort_keys=False))
    assert diff_packages(a, _pkg(new_dir / "vp")) == []


# --------------------------------------------------------------------------- dependency report
def test_dependency_report(tmp_path):
    write_package(tmp_path, "dep-base", entities=[
        {"id": "ocpe:dep-base/x", "kind": "concept", "label": "X", "concept_type": "phenomenon"}])
    write_package(tmp_path, "dep-user", deps=[{"package": "dep-base", "version": ">=1.0.0"}], entities=[
        {"id": "ocpe:dep-user/y", "kind": "concept", "label": "Y", "concept_type": "phenomenon"}])
    reg = load_registry([str(tmp_path / "dep-base"), str(tmp_path / "dep-user")])
    rows = dependency_report(reg)
    assert rows == [{"package": "dep-user", "depends_on": "dep-base", "constraint": ">=1.0.0",
                     "loaded": "1.0.0", "satisfied": True}]


def test_dependency_cycle_detected(tmp_path):
    write_package(tmp_path, "cyc-a", deps=[{"package": "cyc-b", "version": "*"}], entities=[
        {"id": "ocpe:cyc-a/x", "kind": "concept", "label": "X", "concept_type": "phenomenon"}])
    write_package(tmp_path, "cyc-b", deps=[{"package": "cyc-a", "version": "*"}], entities=[
        {"id": "ocpe:cyc-b/x", "kind": "concept", "label": "X", "concept_type": "phenomenon"}])
    reg = load_registry([str(tmp_path / "cyc-a"), str(tmp_path / "cyc-b")])
    from ocpe.validator import validate_registry

    rep = validate_registry(reg)
    assert any(i.code == "dependency-cycle" for i in rep.errors)
