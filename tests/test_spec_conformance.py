"""Specification conformance tests for the repository's own packages.

These tests pin the guarantees the refactoring promises: migrated content is
well-formed, cross-package references resolve, and the legacy registry gaps
stay closed. They are structural conformance checks only; they do NOT assert
scientific validity.
"""

import pytest

from ocpe import load, validate
from ocpe.loader import parse_curie
from ocpe.versioning import satisfies
from ocpe.compatibility import dependency_report


@pytest.fixture(scope="module")
def registry():
    return load()


@pytest.fixture(scope="module")
def report(registry):
    return validate(registry)


def test_all_packages_conform(report):
    assert report.ok, [str(i) for i in report.issues if i.severity == "error"]


def test_every_identifier_matches_grammar(registry):
    for eid in registry.entities:
        assert parse_curie(eid), f"identifier grammar violation: {eid}"


def test_namespace_equals_owning_package(registry):
    for e in registry.entities.values():
        ns = parse_curie(e.id)[0]
        assert ns == e.package, f"{e.id} defined by {e.package} but in namespace {ns}"


def test_registry_gaps_stay_closed(registry):
    ids = set(registry.entities)
    # RMSSD and rr_intervals were referenced but unregistered in the legacy KB
    assert "ocpe:autonomic/rmssd" in ids
    assert "ocpe:cardiovascular/rr-interval" in ids
    # mechanistic-link functional forms were used but unregistered
    for tok in ("sigmoid_hill", "gravity_hydrostatic", "inverse_proportional", "inverse_nonlinear"):
        assert tok in registry.functional_form_tokens(), tok


def test_all_cross_package_references_resolve(registry, report):
    unresolved = [i for i in report.issues if i.code == "unresolved-reference"]
    assert not unresolved, [str(i) for i in unresolved]
    undeclared = [i for i in report.issues if i.code == "undeclared-dependency"]
    assert not undeclared, [str(i) for i in undeclared]


def test_declared_dependencies_satisfied(registry):
    rows = dependency_report(registry)
    assert rows, "expected declared dependencies (cardiovascular -> populations, conditions -> models, ...)"
    for r in rows:
        assert r["satisfied"], f"{r['package']} -> {r['depends_on']} {r['constraint']} (loaded {r['loaded']})"


def test_ocpe_spec_constraints_satisfied(registry):
    for pid, pkg in registry.packages.items():
        constraint = pkg.manifest.get("ocpe_spec")
        assert constraint and satisfies("0.1.0", constraint), f"{pid}: {constraint}"


def test_phenotype_perturbations_reference_declared_model_symbols(registry):
    model = registry.get("ocpe:models.baroreflex-geddes-2022/baroreflex-geddes-2022")
    symbols = model.symbols()
    pots = registry.get("ocpe:conditions.pots/neuropathic-pots")
    reps = pots.data["model_representations"][0]
    for block in ("parameter_perturbations", "unverified_parameter_perturbations"):
        for p in reps.get(block) or []:
            sym = p["parameter"].split("#", 1)[1]
            assert sym in symbols, f"undeclared model symbol {sym}"


def test_scientific_content_preserved(registry):
    """Spot-pin the highest-value migrated scientific content."""
    pots = registry.get("ocpe:conditions.pots/neuropathic-pots")
    data = str(pots.data)
    # compliance guard: never perturb venous compliance upward in POTS
    assert "mvl" in data and "VMvl" in data and "Stewart" in data
    hyper = registry.get("ocpe:conditions.pots/hyperadrenergic-pots")
    criteria = " ".join(c["criterion"] for c in hyper.data["model_representations"][0]["validation_criteria"])
    assert "delta-HR >= 30" in criteria and "delta-SBP >= +10" in criteria
    # model nominal parameters survived migration
    model = registry.get("ocpe:models.baroreflex-geddes-2022/baroreflex-geddes-2022")
    nominals = {s["symbol"]: s.get("nominal_value") for s in model.data["symbols"]}
    assert nominals["TotalVol"] == 4500.0
    assert nominals["RalpM"] == 17.88
    assert nominals["dV_veno_max"] == 250.0
    assert len(model.data["equations"]) == 24
