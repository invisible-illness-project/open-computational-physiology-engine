"""
Tests for the evidence-governance layer (G-P0-08 / G-P0-10, agent W1-B).

Covers:
  1. Tier -> E-level harmonization mapping (EVIDENCE_AUDIT_NOTES (e)).
  2. canonical_status resolution incl. the backward-compatible default
     (tier-D or untiered blocks default to EXPERIMENTAL — fail-closed).
  3. The harmonized real KB resolves to the documented de-facto state.
  4. Provenance-gate fail-closed behavior:
     - missing review            -> MissingReviewError
     - STALE after hash tamper   -> StaleReviewError   (modify file post-review)
     - missing evidence tier     -> MissingEvidenceTierError
     - missing provenance        -> MissingProvenanceError
     - experimental in canonical -> ExperimentalPerturbationError
     - experimental w/o opt-in   -> ExperimentalModeOptInRequired
     - human-L3 absence          -> WARNING, never a silent pass, never an error
  5. Whole-KB canonical preflight passes (post-harmonization) with human-L3
     warnings present.
  6. Dead inline `phenotypes:` blocks are gone from mathematical_models.yaml.
"""
import os
import shutil
import sys

import pytest
import yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.kb_access import (  # noqa: E402
    CANONICAL, EXPERIMENTAL, KBAccessError, KnowledgeBase,
    evidence_tier_of, resolve_canonical_status, tier_to_e_level,
)
from tools.review_tracker import record_review  # noqa: E402
from validation.provenance_gate import (  # noqa: E402
    ExperimentalModeOptInRequired, ExperimentalPerturbationError,
    MissingEvidenceTierError, MissingProvenanceError, MissingReviewError,
    ProvenanceGateError, StaleReviewError,
    check_review_status, gate_generation_mode, gate_kb_file,
    gate_phenotype_selection, preflight_dataset_build,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(REPO_ROOT, "knowledge_base")


# ---------------------------------------------------------------------------
# 1. Tier -> E-level mapping
# ---------------------------------------------------------------------------

def test_tier_to_e_level_mapping():
    assert tier_to_e_level("A") == "E4-E5"
    assert tier_to_e_level("B") == "E2-E3"
    assert tier_to_e_level("C") == "E0-E1"  # provenance label, not a grade
    assert tier_to_e_level("D") == "E0"
    assert tier_to_e_level(None) is None
    with pytest.raises(KBAccessError):
        tier_to_e_level("Z")


# ---------------------------------------------------------------------------
# 2. canonical_status resolution + defaults
# ---------------------------------------------------------------------------

def test_canonical_status_explicit_wins():
    assert resolve_canonical_status({"canonical_status": "experimental",
                                     "evidence_tier": "A"}) == EXPERIMENTAL
    assert resolve_canonical_status({"canonical_status": "canonical",
                                     "provenance": {"evidence_tier": "D"}}) == CANONICAL


def test_canonical_status_defaults_fail_closed():
    # tier D defaults to experimental (Global rule 2)
    assert resolve_canonical_status({"provenance": {"evidence_tier": "D"}}) == EXPERIMENTAL
    # missing tier defaults to experimental (fail-closed on unprovenanced blocks)
    assert resolve_canonical_status({}) == EXPERIMENTAL
    # tiers A/B/C default to canonical
    for tier in ("A", "B", "C"):
        assert resolve_canonical_status({"evidence_tier": tier}) == CANONICAL
    # nested provenance tier is honored
    assert resolve_canonical_status({"provenance": {"evidence_tier": "C"}}) == CANONICAL
    with pytest.raises(KBAccessError):
        resolve_canonical_status({"canonical_status": "bogus"})


# ---------------------------------------------------------------------------
# 3. Real KB resolves to the documented de-facto state (G-P0-08)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def kb():
    return KnowledgeBase(KB_DIR)


def test_kb_canonical_experimental_split(kb):
    canonical = kb.canonical_phenotype_ids()
    experimental = kb.experimental_phenotype_ids()
    # canonical-eligible per their tiers (SPEC G-P0-08 formalization)
    for pid in ("neuropathic_pots", "hyperadrenergic_pots", "hypovolemic_pots",
                "environmental_heat", "fludrocortisone", "mecfs_metabolic_dysfunction"):
        assert pid in canonical, pid
    # experimental-only, engine-inert in canonical mode
    for pid in ("heds_venous_pooling", "autoimmune_neuropathy",
                "sleep_deprivation", "beta_blocker"):
        assert pid in experimental, pid


def test_kb_tier_d_parameters_are_experimental(kb):
    # neuropathic dV_veno_max (tier D) must be experimental even though the
    # phenotype itself is canonical.
    np_ = kb.phenotypes["neuropathic_pots"]
    assert not np_.experimental
    exp_symbols = [p.symbol for p in np_.experimental_parameters]
    assert "dV_veno_max" in exp_symbols
    dvp = next(p for p in np_.experimental_parameters if p.symbol == "dV_veno_max")
    assert dvp.evidence_tier == "D"
    assert dvp.evidence_e_level == "E0"
    # canonical tier-C parameters stay canonical
    assert {p.symbol for p in np_.canonical_parameters} == {"RalpM", "Ralpm"}


def test_kb_registry_claim_ids_only_where_unambiguous(kb):
    # Unambiguous citation<->registry matches
    assert "EVD-POTS-019" in (kb.phenotypes["neuropathic_pots"].source_claim_ids or [])
    assert "EVD-POTS-004" in (kb.phenotypes["hypovolemic_pots"].source_claim_ids or [])
    assert "EVD-EDS-002" in (kb.phenotypes["heds_venous_pooling"].source_claim_ids or [])
    # Zhong 2005 / Vernino 2000 / Chobanian 1979 have no registry claims -> null
    assert kb.phenotypes["sleep_deprivation"].source_claim_ids is None
    assert kb.phenotypes["autoimmune_neuropathy"].source_claim_ids is None
    assert kb.phenotypes["fludrocortisone"].source_claim_ids is None


def test_model_parameters_harmonized(kb):
    assert len(kb.model_parameters) == 36
    for sym, rec in kb.model_parameters.items():
        assert rec.canonical_status == CANONICAL, sym
        assert rec.evidence_tier == "C", sym
        assert rec.evidence_e_level == "E0-E1", sym
        assert rec.provenance, sym


# ---------------------------------------------------------------------------
# 4. Generation-mode gate (G-P0-08)
# ---------------------------------------------------------------------------

def test_generation_mode_gate(kb):
    assert gate_generation_mode("canonical") == "canonical"
    with pytest.raises(ExperimentalModeOptInRequired):
        gate_generation_mode("experimental")  # no explicit opt-in
    assert gate_generation_mode("experimental", allow_experimental=True) == "experimental"
    with pytest.raises(ProvenanceGateError):
        gate_generation_mode("bogus-mode")


def test_canonical_mode_refuses_experimental_phenotype(kb):
    for pid in ("heds_venous_pooling", "autoimmune_neuropathy",
                "sleep_deprivation", "beta_blocker"):
        with pytest.raises(ExperimentalPerturbationError):
            gate_phenotype_selection(kb.phenotypes[pid], mode="canonical")
        # allowed only with explicit experimental opt-in
        gate_phenotype_selection(kb.phenotypes[pid], mode="experimental",
                                 allow_experimental=True)


def test_canonical_mode_accepts_canonical_phenotype(kb):
    for pid in ("neuropathic_pots", "hypovolemic_pots", "environmental_heat"):
        gate_phenotype_selection(kb.phenotypes[pid], mode="canonical")


# ---------------------------------------------------------------------------
# 5. File-level gate: review freshness, tamper, tier/provenance (G-P0-10)
# ---------------------------------------------------------------------------

@pytest.fixture()
def kb_file_factory(tmp_path):
    """Creates tmp KB-like files (under a diseases/ dir so the gate applies
    disease content checks) with optional sidecar reviews."""
    def _make(content: str, name: str = "fake.yaml", record: bool = True):
        subdir = tmp_path / "diseases"
        subdir.mkdir(exist_ok=True)
        path = subdir / name
        path.write_text(content, encoding="utf-8")
        if record:
            record_review(target_path=path, kind="ai_agent",
                          name="governance-test", scope=["test"],
                          comments="test review", verdict="REVIEWED")
        return path
    return _make


DISEASE_OK = """
disease:
  id: "fake"
  name: "Fake"
  canonical_status: "canonical"
  evidence_tier: "B"
  provenance:
    source_claim_ids: null
  phenotypes:
    - id: "fake_pheno"
      name: "Fake Pheno"
      canonical_status: "experimental"
      evidence_tier: "D"
      provenance:
        evidence_tier: "D"
      parameters_perturbed:
        - symbol: "kR"
          canonical_status: "experimental"
          provenance:
            evidence_tier: "D"
"""


def test_gate_missing_review(kb_file_factory):
    path = kb_file_factory(DISEASE_OK, record=False)
    result = gate_kb_file(path, mode="canonical")
    assert not result.ok
    assert any(isinstance(e, MissingReviewError) for e in result.errors)


def test_gate_hash_tamper_rejected(kb_file_factory):
    """Modify a file AFTER its review was recorded -> gate must reject (STALE)."""
    path = kb_file_factory(DISEASE_OK)
    status = check_review_status(path)
    assert status.state == "FRESH"
    # tamper: append content after the review
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n# tampered after review\n")
    status = check_review_status(path)
    assert status.state == "STALE"
    result = gate_kb_file(path, mode="canonical")
    assert not result.ok
    assert any(isinstance(e, StaleReviewError) for e in result.errors)


def test_gate_missing_evidence_tier(kb_file_factory):
    # strip BOTH the flat and nested tier from the phenotype block
    content = DISEASE_OK.replace(
        '      canonical_status: "experimental"\n      evidence_tier: "D"\n      provenance:\n        evidence_tier: "D"\n',
        '      canonical_status: "experimental"\n      provenance:\n        review_status: "no tier here"\n')
    assert 'evidence_tier: "D"\n      provenance' not in content
    path = kb_file_factory(content)
    result = gate_kb_file(path, mode="canonical")
    assert not result.ok
    assert any(isinstance(e, MissingEvidenceTierError) for e in result.errors)


def test_gate_missing_provenance(kb_file_factory):
    content = DISEASE_OK.replace(
        "          canonical_status: \"experimental\"\n          provenance:\n            evidence_tier: \"D\"\n",
        "          canonical_status: \"experimental\"\n")
    path = kb_file_factory(content)
    result = gate_kb_file(path, mode="canonical")
    assert not result.ok
    assert any(isinstance(e, MissingProvenanceError) for e in result.errors)


def test_gate_human_l3_absence_is_warning_not_error(kb_file_factory):
    path = kb_file_factory(DISEASE_OK)  # ai_agent review only
    result = gate_kb_file(path, mode="canonical")
    assert result.ok, [str(e) for e in result.errors]
    assert any("human (L3)" in w for w in result.warnings)


def test_gate_human_review_silences_l3_warning(kb_file_factory):
    path = kb_file_factory(DISEASE_OK, record=False)
    record_review(target_path=path, kind="human", name="dr-reviewer",
                  scope=["clinical"], comments="L3 sign-off", verdict="APPROVED")
    result = gate_kb_file(path, mode="canonical")
    assert result.ok
    assert not any("human (L3)" in w for w in result.warnings)


def test_gate_clean_file_passes(kb_file_factory):
    path = kb_file_factory(DISEASE_OK)
    result = gate_kb_file(path, mode="canonical")
    assert result.ok, [str(e) for e in result.errors]


# ---------------------------------------------------------------------------
# 6. Whole-KB preflight + selection gating
# ---------------------------------------------------------------------------

def test_preflight_real_kb_canonical_passes_with_l3_warnings():
    report = preflight_dataset_build(KB_DIR, mode="canonical")
    assert report.ok, [str(e) for e in report.errors]
    # Human-L3 absence must be surfaced as warnings (not silently passed)
    assert report.warnings
    assert all("human (L3)" in w for w in report.warnings)


def test_preflight_canonical_refuses_experimental_selection():
    report = preflight_dataset_build(
        KB_DIR, mode="canonical",
        phenotype_ids=["hypovolemic_pots", "heds_venous_pooling"])
    assert not report.ok
    assert any(isinstance(e, ExperimentalPerturbationError) for e in report.selection_errors)
    with pytest.raises(ProvenanceGateError):
        report.raise_if_failed()


def test_preflight_canonical_refuses_unprovenanced_sensor():
    # photoplethysmography.yaml carries no source citation -> experimental
    report = preflight_dataset_build(KB_DIR, mode="canonical",
                                     sensor_ids=["photoplethysmography"])
    assert not report.ok
    assert any(isinstance(e, ExperimentalPerturbationError) for e in report.selection_errors)
    # Polar H10 is cited (Schaffarczyk 2022 / EVD-SENS-002) -> canonical OK
    report2 = preflight_dataset_build(KB_DIR, mode="canonical", sensor_ids=["polar_h10"])
    assert report2.ok, [str(e) for e in report2.errors]


def test_preflight_experimental_requires_optin():
    with pytest.raises(ExperimentalModeOptInRequired):
        preflight_dataset_build(KB_DIR, mode="experimental")
    report = preflight_dataset_build(KB_DIR, mode="experimental", allow_experimental=True,
                                     phenotype_ids=["heds_venous_pooling"])
    assert report.ok, [str(e) for e in report.errors]


# ---------------------------------------------------------------------------
# 7. Dead inline phenotypes blocks are removed (G-P0-04 support)
# ---------------------------------------------------------------------------

def test_no_dead_inline_phenotypes_in_mathematical_models():
    with open(os.path.join(KB_DIR, "equations", "mathematical_models.yaml"),
              "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    for model in data.get("models", []):
        for param in model.get("parameters", []):
            assert "phenotypes" not in param, (
                f"stale inline phenotypes block survives on {param.get('symbol')}")


def test_kb_yaml_files_parse():
    for root, _, files in os.walk(KB_DIR):
        for fname in files:
            if fname.endswith(".yaml") and not fname.endswith(".review.yaml"):
                with open(os.path.join(root, fname), "r", encoding="utf-8") as f:
                    yaml.safe_load(f)
