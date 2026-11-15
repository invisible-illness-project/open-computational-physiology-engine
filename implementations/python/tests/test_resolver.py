"""Engine tests: identifier resolution (canonical, aliases, symbols, labels, tokens)."""

import pytest

from ocpe.resolver import AmbiguousReference, ResolutionError, Resolver


@pytest.fixture(scope="module")
def resolver(tmp_path_factory):
    from ocpe.loader import load_registry

    root = tmp_path_factory.mktemp("res")
    from .conftest import write_package

    write_package(root, "res", entities=[
        {"id": "ocpe:res/rate", "kind": "variable", "label": "Rate",
         "dimension": "event_rate", "canonical_unit": "/min",
         "aliases": [{"value": "RT", "type": "symbol", "unit": "/min"},
                     {"value": "rt2", "type": "abbreviation", "scope": "res"}]},
        {"id": "ocpe:res/other", "kind": "variable", "label": "Other",
         "dimension": "time", "canonical_unit": "s",
         "aliases": [{"value": "RT", "type": "symbol", "scope": "other"}]},
        {"id": "ocpe:res/m", "kind": "model", "label": "M", "formalism": "ode",
         "symbols": [{"symbol": "x", "role": "state", "unit": "mL"},
                     {"symbol": "k", "role": "parameter", "represents": "ocpe:res/rate"}]},
        {"id": "ocpe:res/rel", "kind": "relationship", "label": "rel",
         "subject": "ocpe:res/rate", "predicate": "REGULATES", "object": "ocpe:res/other"},
    ])
    return Resolver(load_registry([str(root / "res")]))


def test_resolve_canonical(resolver):
    r = resolver.resolve("ocpe:res/rate")
    assert r.id == "ocpe:res/rate"
    assert r.matched_by == "canonical"
    assert r.entity.kind == "variable"


def test_resolve_alias_with_unit(resolver):
    r = resolver.resolve("RT", scope="res")
    assert r.id == "ocpe:res/rate"
    assert r.unit == "/min"
    assert r.matched_by == "alias"


def test_resolve_unscoped_alias_ambiguous(resolver):
    with pytest.raises(AmbiguousReference):
        resolver.resolve("RT")


def test_resolve_scoped_alias(resolver):
    r = resolver.resolve("rt2", scope="res")
    assert r.id == "ocpe:res/rate"


def test_resolve_model_symbol(resolver):
    r = resolver.resolve("ocpe:res/m#x")
    assert r.matched_by == "symbol"
    assert r.symbol["symbol"] == "x"
    assert r.unit == "mL"
    r2 = resolver.resolve("ocpe:res/m#k")
    assert "represents" in " ".join(r2.notes)


def test_resolve_unknown_model_symbol_raises(resolver):
    with pytest.raises(ResolutionError):
        resolver.resolve("ocpe:res/m#nope")


def test_resolve_predicate_token(resolver):
    r = resolver.resolve("REGULATES")
    assert r.id == "ocpe:core/regulates"


def test_resolve_functional_form_token(resolver):
    r = resolver.resolve("first_order_lag")
    assert r.id == "ocpe:core/first-order-lag"


def test_case_sensitivity_of_aliases(resolver):
    with pytest.raises(ResolutionError):
        resolver.resolve("rt")


def test_resolve_by_label(resolver):
    r = resolver.resolve("Rate")
    assert r.id == "ocpe:res/rate"
    assert r.matched_by == "label"


def test_resolve_unknown_raises(resolver):
    with pytest.raises(ResolutionError):
        resolver.resolve("ocpe:res/absent")
    with pytest.raises(ResolutionError):
        resolver.resolve("ocpe:unloaded-pkg/x")
    with pytest.raises(ResolutionError):
        resolver.resolve("not a curie at all")


def test_deprecated_resolution_marks_replaced_by(tmp_path):
    from .conftest import write_package

    pkg = write_package(tmp_path, "dep", entities=[
        {"id": "ocpe:dep/old", "kind": "concept", "label": "Old", "concept_type": "phenomenon",
         "status": "deprecated",
         "deprecation": {"deprecated_in": "1.0.0", "reason": "r", "replaced_by": "ocpe:dep/new"}},
        {"id": "ocpe:dep/new", "kind": "concept", "label": "New", "concept_type": "phenomenon"},
    ])
    from ocpe.loader import load_registry

    r = Resolver(load_registry([str(pkg)])).resolve("ocpe:dep/old")
    d = r.to_dict()
    assert d["deprecated"] is True
    assert d["replaced_by"] == "ocpe:dep/new"


def test_search_finds_entities(resolver):
    hits = resolver.search("rate")
    ids = {e.id for e in hits}
    assert "ocpe:res/rate" in ids


def test_related_relationships(resolver):
    related = resolver.related("ocpe:res/rate")
    preds = {r.data["predicate"] for r in related}
    assert "REGULATES" in preds


def test_aliases_of(resolver):
    aliases = resolver.aliases_of("ocpe:res/rate")
    assert {a["value"] for a in aliases} == {"RT", "rt2"}
