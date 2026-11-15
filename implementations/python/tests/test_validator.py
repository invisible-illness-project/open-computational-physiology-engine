"""Engine tests: schema + semantic validation, observation semantics, evidence integrity."""

import pytest

from ocpe import load, validate
from ocpe.loader import load_registry
from ocpe.validator import validate_instance, validate_registry, validate_observation
from ocpe import units


def _reg(pkg_factory, pid, **kw):
    pkg = pkg_factory(pid, **kw)
    return load_registry([pkg], include_core=True)


def test_namespace_violation_flagged(pkg_factory):
    reg = _reg(pkg_factory, "nsviol", entities=[
        {"id": "ocpe:other/x", "kind": "concept", "label": "X", "concept_type": "phenomenon"}])
    rep = validate_registry(reg, ["nsviol"])
    assert any(i.code == "namespace" for i in rep.errors)


def test_undeclared_dependency_flagged(pkg_factory):
    reg = _reg(pkg_factory, "depfree", entities=[
        {"id": "ocpe:depfree/a", "kind": "concept", "label": "A", "concept_type": "phenomenon"},
        {"id": "ocpe:depfree/r", "kind": "relationship", "label": "r", "subject": "ocpe:depfree/a",
         "predicate": "CAUSES", "object": "ocpe:unloaded/x"}])
    rep = validate_registry(reg, ["depfree"])
    assert any(i.code == "undeclared-dependency" for i in rep.errors)


def test_unresolved_reference_flagged(pkg_factory):
    reg = _reg(pkg_factory, "unres", deps=[{"package": "somepkg", "version": "*"}], entities=[
        {"id": "ocpe:unres/a", "kind": "concept", "label": "A", "concept_type": "phenomenon"},
        {"id": "ocpe:unres/r", "kind": "relationship", "label": "r", "subject": "ocpe:unres/a",
         "predicate": "CAUSES", "object": "ocpe:somepkg/x"}])
    rep = validate_registry(reg, ["unres"])
    # declared but not loaded -> warning; the reference does not resolve
    assert any(i.code == "unresolved-reference" for i in rep.issues)


def test_malformed_reference_flagged(pkg_factory):
    reg = _reg(pkg_factory, "badref", entities=[
        {"id": "ocpe:badref/a", "kind": "concept", "label": "A", "concept_type": "phenomenon",
         "see_also": ["ocpe:Bad Grammar/x"]}])
    rep = validate_registry(reg, ["badref"])
    assert any(i.code == "bad-reference" for i in rep.errors)


def test_dimension_mismatch_flagged(pkg_factory):
    reg = _reg(pkg_factory, "dimwrong", entities=[
        {"id": "ocpe:dimwrong/x", "kind": "variable", "label": "X",
         "dimension": "volume", "canonical_unit": "mm[Hg]"}])
    rep = validate_registry(reg, ["dimwrong"])
    assert any(i.code == "dimension-mismatch" for i in rep.errors)


def test_unknown_unit_flagged(pkg_factory):
    reg = _reg(pkg_factory, "unitwrong", entities=[
        {"id": "ocpe:unitwrong/x", "kind": "variable", "label": "X",
         "dimension": "volume", "canonical_unit": "furlongs"}])
    rep = validate_registry(reg, ["unitwrong"])
    assert any(i.code == "unit" for i in rep.errors)


def test_unknown_dimension_flagged(pkg_factory):
    reg = _reg(pkg_factory, "dimunknown", entities=[
        {"id": "ocpe:dimunknown/x", "kind": "variable", "label": "X",
         "dimension": "surprise", "canonical_unit": "mL"}])
    rep = validate_registry(reg, ["dimunknown"])
    assert any(i.code == "dimension" for i in rep.errors)


def test_model_equation_undeclared_symbol_flagged(pkg_factory):
    reg = _reg(pkg_factory, "symbad", entities=[
        {"id": "ocpe:symbad/m", "kind": "model", "label": "M", "formalism": "ode",
         "symbols": [{"symbol": "x", "role": "state"}],
         "equations": [{"id": "eq1", "expression_latex": "x = z", "inputs": ["x"], "outputs": ["z"]}]}])
    rep = validate_registry(reg, ["symbad"])
    assert "undeclared-symbol" in {i.code for i in rep.errors}


def test_model_symbol_dimension_checked_against_represents(pkg_factory):
    reg = _reg(pkg_factory, "symdim", entities=[
        {"id": "ocpe:symdim/v", "kind": "variable", "label": "V",
         "dimension": "volume", "canonical_unit": "mL"},
        {"id": "ocpe:symdim/m", "kind": "model", "label": "M", "formalism": "ode",
         "symbols": [{"symbol": "x", "role": "state", "unit": "s", "represents": "ocpe:symdim/v"}],
         "equations": []}])
    rep = validate_registry(reg, ["symdim"])
    assert any(i.code == "dimension-mismatch" for i in rep.errors)


def test_deprecated_requires_deprecation_block(pkg_factory):
    reg = _reg(pkg_factory, "dep", entities=[
        {"id": "ocpe:dep/x", "kind": "concept", "label": "X", "concept_type": "phenomenon",
         "status": "deprecated"}])
    rep = validate_registry(reg, ["dep"])
    assert any(i.code == "deprecation" for i in rep.errors)


def test_since_later_than_package_version_flagged(pkg_factory):
    reg = _reg(pkg_factory, "sincebad", version="1.0.0", entities=[
        {"id": "ocpe:sincebad/x", "kind": "concept", "label": "X", "concept_type": "phenomenon",
         "since": "2.0.0"}])
    rep = validate_registry(reg, ["sincebad"])
    assert any(i.code == "since" for i in rep.errors)


def test_inverted_range_flagged(pkg_factory):
    reg = _reg(pkg_factory, "rangebad", entities=[
        {"id": "ocpe:rangebad/x", "kind": "variable", "label": "X",
         "dimension": "time", "canonical_unit": "s",
         "reference_ranges": [{"range_type": "plausibility_bound", "unit": "s", "context": {"scope_note": "t"},
                               "min": 10, "max": 5}]}])
    rep = validate_registry(reg, ["rangebad"])
    assert any(i.code == "range" for i in rep.errors)


def test_predicate_range_checked_as_warning(pkg_factory):
    reg = _reg(pkg_factory, "predrange", entities=[
        {"id": "ocpe:predrange/a", "kind": "concept", "label": "A", "concept_type": "phenomenon"},
        {"id": "ocpe:predrange/r", "kind": "relationship", "label": "r", "subject": "ocpe:predrange/a",
         "predicate": "MEASURED_BY", "object": "ocpe:predrange/a"}])
    rep = validate_registry(reg, ["predrange"])
    assert any(i.code == "predicate-range" and i.severity == "warning" for i in rep.issues)


def test_unknown_functional_form_flagged(pkg_factory):
    reg = _reg(pkg_factory, "ffbad", entities=[
        {"id": "ocpe:ffbad/a", "kind": "concept", "label": "A", "concept_type": "phenomenon"},
        {"id": "ocpe:ffbad/b", "kind": "concept", "label": "B", "concept_type": "phenomenon"},
        {"id": "ocpe:ffbad/r", "kind": "relationship", "label": "r", "subject": "ocpe:ffbad/a",
         "predicate": "CAUSES", "object": "ocpe:ffbad/b", "functional_form": "no_such_form"}])
    rep = validate_registry(reg, ["ffbad"])
    assert any(i.code == "unknown-functional-form" for i in rep.errors)


# --------------------------------------------------------------------------- evidence integrity
def test_evidence_citing_registered_reference_ok(pkg_factory):
    reg = _reg(pkg_factory, "evok",
               references=[{"id": "doi:10.12345/fake-fixture", "title": "Fixture reference"}],
               entities=[
                   {"id": "ocpe:evok/x", "kind": "concept", "label": "X", "concept_type": "phenomenon",
                    "evidence": [{"claim": "c", "references": ["doi:10.12345/fake-fixture"]}]}])
    rep = validate_registry(reg, ["evok"])
    assert not any(i.code == "unresolved-evidence-reference" for i in rep.errors)


def test_evidence_citing_unregistered_reference_flagged(pkg_factory):
    reg = _reg(pkg_factory, "evbad", entities=[
        {"id": "ocpe:evbad/x", "kind": "concept", "label": "X", "concept_type": "phenomenon",
         "evidence": [{"claim": "c", "references": ["doi:10.99999/never-declared"]}]}])
    rep = validate_registry(reg, ["evbad"])
    assert any(i.code == "unresolved-evidence-reference" for i in rep.errors)


def test_nested_model_evidence_checked(pkg_factory):
    reg = _reg(pkg_factory, "evnest", entities=[
        {"id": "ocpe:evnest/m", "kind": "model", "label": "M", "formalism": "ode",
         "symbols": [{"symbol": "x", "role": "state",
                      "evidence": [{"claim": "c", "references": ["pmid:999999999"]}]}],
         "equations": []}])
    rep = validate_registry(reg, ["evnest"])
    assert any(i.code == "unresolved-evidence-reference" for i in rep.errors)


# --------------------------------------------------------------------------- observation semantics
@pytest.fixture(scope="module")
def obs_registry(tmp_path_factory):
    from .conftest import write_package

    root = tmp_path_factory.mktemp("obs")
    write_package(root, "obs", entities=[
        {"id": "ocpe:obs/rate", "kind": "variable", "label": "Rate",
         "dimension": "event_rate", "canonical_unit": "/min", "value_type": "continuous",
         "observability": "directly_measurable"},
        {"id": "ocpe:obs/flag", "kind": "variable", "label": "Flag",
         "dimension": "dimensionless", "canonical_unit": "1", "value_type": "boolean"},
        {"id": "ocpe:obs/latent", "kind": "latent_construct", "label": "Latent",
         "dimension": "dimensionless", "canonical_unit": "1"},
        {"id": "ocpe:obs/abstraction", "kind": "variable", "label": "Abstraction",
         "dimension": "volume", "canonical_unit": "mL", "observability": "model_compartment"},
        {"id": "ocpe:obs/meter", "kind": "measurement_method", "label": "Meter",
         "method_type": "device",
         "measures": [{"target": "ocpe:obs/rate", "mode": "direct"},
                       {"target": "ocpe:obs/latent", "mode": "estimated"}]},
        {"id": "ocpe:obs/sim", "kind": "model", "label": "Sim", "formalism": "ode",
         "symbols": [{"symbol": "x", "role": "state"}], "equations": []},
    ])
    return load_registry([str(root / "obs")])


def test_observation_measured_ok(obs_registry):
    rep = validate_observation(
        {"quantity": "ocpe:obs/rate", "value": 72, "unit": "/min", "value_kind": "measured",
         "method": "ocpe:obs/meter", "time": "2026-11-15T10:00:00Z", "uncertainty": 2,
         "uncertainty_type": "sd"}, obs_registry)
    assert rep.ok, [str(i) for i in rep.issues]


def test_observation_unknown_quantity(obs_registry):
    rep = validate_observation(
        {"quantity": "ocpe:obs/absent", "value": 72, "unit": "/min", "value_kind": "measured"}, obs_registry)
    assert any(i.code == "unresolved-reference" for i in rep.errors)


def test_observation_concept_not_a_quantity(obs_registry):
    pkg_concept = validate_observation(
        {"quantity": "ocpe:obs/meter", "value": 72, "unit": "/min", "value_kind": "measured"}, obs_registry)
    assert any(i.code == "not-a-quantity" for i in pkg_concept.errors)


def test_observation_latent_cannot_be_measured(obs_registry):
    rep = validate_observation(
        {"quantity": "ocpe:obs/latent", "value": 0.5, "unit": "1", "value_kind": "measured"}, obs_registry)
    assert any(i.code == "latent-measured" for i in rep.errors)
    ok = validate_observation(
        {"quantity": "ocpe:obs/latent", "value": 0.5, "unit": "1", "value_kind": "estimated",
         "method": "ocpe:obs/meter"}, obs_registry)
    assert ok.ok, [str(i) for i in ok.issues]


def test_observation_unit_dimension_checked(obs_registry):
    rep = validate_observation(
        {"quantity": "ocpe:obs/rate", "value": 72, "unit": "mm[Hg]", "value_kind": "measured"}, obs_registry)
    assert any(i.code == "unit" for i in rep.errors)


def test_observation_method_must_exist_and_be_a_method(obs_registry):
    rep = validate_observation(
        {"quantity": "ocpe:obs/rate", "value": 72, "unit": "/min", "value_kind": "measured",
         "method": "ocpe:obs/rate"}, obs_registry)
    assert any(i.code == "bad-method-kind" for i in rep.errors)
    rep2 = validate_observation(
        {"quantity": "ocpe:obs/rate", "value": 72, "unit": "/min", "value_kind": "measured",
         "method": "ocpe:obs/absent-meter"}, obs_registry)
    assert any(i.code == "unresolved-reference" for i in rep2.errors)


def test_observation_method_must_declare_quantity(obs_registry):
    rep = validate_observation(
        {"quantity": "ocpe:obs/flag", "value": True, "unit": "1", "value_kind": "measured",
         "method": "ocpe:obs/meter"}, obs_registry)
    assert any(i.code == "method-does-not-measure" for i in rep.errors)


def test_observation_method_mode_mismatch_warns(obs_registry):
    rep = validate_observation(
        {"quantity": "ocpe:obs/rate", "value": 72, "unit": "/min", "value_kind": "estimated",
         "method": "ocpe:obs/meter"}, obs_registry)
    assert any(i.code == "method-mode-mismatch" and i.severity == "warning" for i in rep.issues)


def test_observation_simulated_requires_existing_model(obs_registry):
    ok = validate_observation(
        {"quantity": "ocpe:obs/rate", "value": 72, "unit": "/min", "value_kind": "simulated",
         "model": "ocpe:obs/sim"}, obs_registry)
    assert ok.ok, [str(i) for i in ok.issues]
    bad = validate_observation(
        {"quantity": "ocpe:obs/rate", "value": 72, "unit": "/min", "value_kind": "simulated"}, obs_registry)
    assert any(i.code == "schema" for i in bad.errors)
    bad2 = validate_observation(
        {"quantity": "ocpe:obs/rate", "value": 72, "unit": "/min", "value_kind": "simulated",
         "model": "ocpe:obs/meter"}, obs_registry)
    assert any(i.code == "bad-method-kind" for i in bad2.errors)


def test_observation_value_type_checked(obs_registry):
    rep = validate_observation(
        {"quantity": "ocpe:obs/flag", "value": 1, "unit": "1", "value_kind": "measured"}, obs_registry)
    assert any(i.code == "value-type-mismatch" for i in rep.errors)
    ok = validate_observation(
        {"quantity": "ocpe:obs/flag", "value": True, "unit": "1", "value_kind": "self_reported"}, obs_registry)
    assert ok.ok, [str(i) for i in ok.issues]


def test_observation_timestamp_checked(obs_registry):
    rep = validate_observation(
        {"quantity": "ocpe:obs/rate", "value": 72, "unit": "/min", "value_kind": "measured",
         "time": "not-a-time"}, obs_registry)
    assert any(i.code == "bad-timestamp" for i in rep.errors)


def test_observation_model_compartment_measured_warns(obs_registry):
    rep = validate_observation(
        {"quantity": "ocpe:obs/abstraction", "value": 100, "unit": "mL", "value_kind": "measured"}, obs_registry)
    assert any(i.code == "unobservable-as-measured" and i.severity == "warning" for i in rep.issues)


def test_observation_uncertainty_unit_dimension_checked(obs_registry):
    rep = validate_observation(
        {"quantity": "ocpe:obs/rate", "value": 72, "unit": "/min", "value_kind": "measured",
         "uncertainty": 2, "uncertainty_unit": "mm[Hg]"}, obs_registry)
    assert any(i.code == "unit" for i in rep.errors)


def test_observation_without_registry_is_schema_only():
    rep = validate_observation({"quantity": "ocpe:anything/x", "value": 1, "unit": "s", "value_kind": "measured"})
    assert rep.ok  # no registry: syntactic validation only


# --------------------------------------------------------------------------- units + schema layer
def test_units_conversion():
    assert abs(units.convert(1.0, "/s", "/min") - 60.0) < 1e-9
    assert abs(units.convert(4500.0, "mL", "L") - 4.5) < 1e-9
    with pytest.raises(units.UnitError):
        units.convert(1.0, "mL", "mm[Hg]")


def test_units_normalize_legacy_spellings():
    assert units.normalize("mmHg") == "mm[Hg]"
    assert units.normalize("bpm") == "/min"
    with pytest.raises(units.UnitError):
        units.normalize("leagues")


def test_schema_layer_direct():
    rep = validate_instance({"id": "ocpe:x/y"}, "variable.schema.json")
    assert not rep.ok  # missing kind/label/dimension/canonical_unit


def test_report_disclaimer_present():
    rep = validate_instance({"id": "ocpe:x/y"}, "variable.schema.json")
    assert "scientific validity" in rep.to_dict()["disclaimer"]
