"""Engine tests: identifier resolution (canonical, aliases, symbols, labels)."""

import pytest

from ocpe import load
from ocpe.resolver import AmbiguousReference, ResolutionError, Resolver


@pytest.fixture(scope="module")
def registry():
    return load()


@pytest.fixture(scope="module")
def resolver(registry):
    return Resolver(registry)


def test_resolve_canonical(resolver):
    r = resolver.resolve("ocpe:cardiovascular/heart-rate")
    assert r.id == "ocpe:cardiovascular/heart-rate"
    assert r.matched_by == "canonical"
    assert r.entity.kind == "variable"


def test_resolve_legacy_symbol_alias_with_unit(resolver):
    r = resolver.resolve("Hc", scope="legacy-kb")
    assert r.id == "ocpe:cardiovascular/heart-rate"
    assert r.unit == "/s"
    r2 = resolver.resolve("HR", scope="legacy-kb")
    assert r2.id == "ocpe:cardiovascular/heart-rate"
    assert r2.unit == "/min"


def test_resolve_model_symbol(resolver):
    r = resolver.resolve("ocpe:models.baroreflex-geddes-2022/baroreflex-geddes-2022#RalpM")
    assert r.matched_by == "symbol"
    assert r.symbol["symbol"] == "RalpM"
    assert r.unit == "mm[Hg].s/mL"
    assert "represents" in " ".join(r.notes)


def test_resolve_unknown_model_symbol_raises(resolver):
    with pytest.raises(ResolutionError):
        resolver.resolve("ocpe:models.baroreflex-geddes-2022/baroreflex-geddes-2022#NoSuchSymbol")


def test_resolve_predicate_token(resolver):
    r = resolver.resolve("REGULATES")
    assert r.id == "ocpe:core/regulates"


def test_resolve_functional_form_token(resolver):
    r = resolver.resolve("sigmoid_hill")
    assert r.id == "ocpe:core/sigmoid-hill"


def test_resolve_legacy_phenotype_alias(resolver):
    r = resolver.resolve("neuropathic_pots")
    assert r.id == "ocpe:conditions.pots/neuropathic-pots"
    assert r.matched_by == "alias"


def test_case_sensitivity_of_aliases(resolver):
    with pytest.raises(ResolutionError):
        resolver.resolve("hr")  # lowercase 'hr' is not the alias 'HR'


def test_search_finds_entities(resolver):
    hits = resolver.search("baroreflex")
    ids = {e.id for e in hits}
    assert "ocpe:autonomic/baroreflex-gain" in ids


def test_related_relationships(resolver):
    related = resolver.related("ocpe:cardiovascular/heart-rate")
    preds = {r.data["predicate"] for r in related}
    assert "REGULATES" in preds
