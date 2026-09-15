#!/usr/bin/env python3
"""
KB Access Helper (Evidence Governance layer, G-P0-08 / G-P0-10).

Single, reusable entry point for loading knowledge_base YAML content with the
evidence-governance metadata resolved:

* tier -> E-level harmonization (EVIDENCE_AUDIT_NOTES.md section (e)):
    tier A ~= E4-E5 (established human direction/magnitude)
    tier B ~= E2-E3 (human, direction/semi-quantitative)
    tier C  = E0-E1 (NOT an evidence grade: provenance label for
              machine-fitted / in-silico-scaled magnitudes constrained to
              documented human ranges)
    tier D ~= E0   (machine-proposed hypothesis, unresolved -> EXPERIMENTAL)
* `canonical_status` resolution with backward-compatible defaults:
    explicit `canonical_status` field wins; otherwise tier-D (or missing
    tier) defaults to EXPERIMENTAL (fail-closed, Global rule 2), tiers A/B/C
    default to canonical.
* Phenotype/model-parameter records that `validation/provenance_gate.py` and
  the simulation engine / dataset builder can consume without re-parsing YAML.

This module is read-only with respect to the KB: it never mutates files.
Python 3 + PyYAML only (SPEC global rule 9).
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

CANONICAL = "canonical"
EXPERIMENTAL = "experimental"
CANONICAL_STATUSES = (CANONICAL, EXPERIMENTAL)

# Binding tier -> E-level mapping (SPEC G-P0-10; EVIDENCE_AUDIT_NOTES (e)).
TIER_TO_E_LEVEL: Dict[str, str] = {
    "A": "E4-E5",
    "B": "E2-E3",
    "C": "E0-E1",  # provenance label, not a grade; machine-fitted/in-silico
    "D": "E0",
}


class KBAccessError(Exception):
    """Raised for structural KB access problems (unparseable file, bad enum)."""


def tier_to_e_level(tier: Optional[str]) -> Optional[str]:
    """Map a repo evidence tier (A-D) to the harmonized E-level range string.
    Returns None when no tier is given; raises KBAccessError on unknown tiers."""
    if tier is None:
        return None
    t = str(tier).strip().upper()
    if t not in TIER_TO_E_LEVEL:
        raise KBAccessError(f"Unknown evidence tier {tier!r}; expected one of {sorted(TIER_TO_E_LEVEL)}")
    return TIER_TO_E_LEVEL[t]


def evidence_tier_of(block: Dict[str, Any]) -> Optional[str]:
    """Extract the evidence tier of a parameter/phenotype block.

    Lookup order: flat `evidence_tier`, then nested `provenance.evidence_tier`,
    then `association_evidence.evidence_tier` (phenotype-level direction tier).
    """
    if not isinstance(block, dict):
        return None
    tier = block.get("evidence_tier")
    if tier is None and isinstance(block.get("provenance"), dict):
        tier = block["provenance"].get("evidence_tier")
    if tier is None and isinstance(block.get("association_evidence"), dict):
        tier = block["association_evidence"].get("evidence_tier")
    return str(tier).strip().upper() if tier is not None else None


def resolve_canonical_status(block: Dict[str, Any]) -> str:
    """Resolve canonical_status for a KB block (backward compatible).

    1. Explicit `canonical_status` field wins (validated against the enum).
    2. Default: tier-D or untiered blocks are EXPERIMENTAL (fail-closed;
       SPEC global rule 2), tier A/B/C blocks are canonical.
    """
    if not isinstance(block, dict):
        return EXPERIMENTAL
    explicit = block.get("canonical_status")
    if explicit is not None:
        status = str(explicit).strip().lower()
        if status not in CANONICAL_STATUSES:
            raise KBAccessError(
                f"Invalid canonical_status {explicit!r}; expected one of {CANONICAL_STATUSES}")
        return status
    tier = evidence_tier_of(block)
    if tier == "D" or tier is None:
        return EXPERIMENTAL
    return CANONICAL


@dataclass
class ParameterRecord:
    """A single perturbation or model parameter with governance metadata."""
    symbol: str
    canonical_status: str
    evidence_tier: Optional[str]
    evidence_e_level: Optional[str]
    source_claim_ids: Optional[List[str]]
    provenance: Dict[str, Any]
    raw: Dict[str, Any]
    source: str = ""  # e.g. "parameters_perturbed" | "unverified_parameters" | "model_nominal"

    @property
    def experimental(self) -> bool:
        return self.canonical_status == EXPERIMENTAL


@dataclass
class PhenotypeRecord:
    """A disease/intervention phenotype with canonical/experimental split."""
    phenotype_id: str
    disease_id: str
    name: str
    canonical_status: str
    evidence_tier: Optional[str]
    evidence_e_level: Optional[str]
    source_claim_ids: Optional[List[str]]
    canonical_parameters: List[ParameterRecord] = field(default_factory=list)
    experimental_parameters: List[ParameterRecord] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def experimental(self) -> bool:
        return self.canonical_status == EXPERIMENTAL

    @property
    def all_parameters(self) -> List[ParameterRecord]:
        return self.canonical_parameters + self.experimental_parameters


def _parameter_record(block: Dict[str, Any], source: str) -> ParameterRecord:
    tier = evidence_tier_of(block)
    prov = block.get("provenance") if isinstance(block.get("provenance"), dict) else {}
    claim_ids = block.get("source_claim_ids")
    if claim_ids is None:
        claim_ids = prov.get("source_claim_ids")
    return ParameterRecord(
        symbol=str(block.get("symbol", "")),
        canonical_status=resolve_canonical_status(block),
        evidence_tier=tier,
        evidence_e_level=tier_to_e_level(tier),
        source_claim_ids=claim_ids,
        provenance=prov,
        raw=block,
        source=source,
    )


def _phenotype_record(disease_id: str, pheno: Dict[str, Any]) -> PhenotypeRecord:
    tier = evidence_tier_of(pheno)
    claim_ids = pheno.get("source_claim_ids")
    if claim_ids is None and isinstance(pheno.get("association_evidence"), dict):
        claim_ids = pheno["association_evidence"].get("source_claim_ids")
    rec = PhenotypeRecord(
        phenotype_id=str(pheno.get("id", "")),
        disease_id=disease_id,
        name=str(pheno.get("name", "")),
        canonical_status=resolve_canonical_status(pheno),
        evidence_tier=tier,
        evidence_e_level=tier_to_e_level(tier),
        source_claim_ids=claim_ids,
        raw=pheno,
    )
    for pert in pheno.get("parameters_perturbed", []) or []:
        rec.canonical_parameters.append(_parameter_record(pert, "parameters_perturbed"))
    for pert in pheno.get("unverified_parameters", []) or []:
        rec.experimental_parameters.append(_parameter_record(pert, "unverified_parameters"))
    # Defense in depth: an unverified (tier-D) parameter is never canonical
    # even if a malformed file places it under parameters_perturbed.
    still_canonical = []
    for p in rec.canonical_parameters:
        if p.evidence_tier == "D" or p.canonical_status == EXPERIMENTAL:
            rec.experimental_parameters.append(p)
        else:
            still_canonical.append(p)
    rec.canonical_parameters = still_canonical
    return rec


def _iter_data_yaml(directory: str):
    for fname in sorted(os.listdir(directory)):
        # Exclude ADR 0001 sidecar review manifests (<file>.review.yaml).
        if fname.endswith(".yaml") and not fname.endswith(".review.yaml"):
            yield os.path.join(directory, fname)


class KnowledgeBase:
    """Loaded KB view with resolved evidence-governance metadata.

    Usage:
        kb = KnowledgeBase(kb_path)          # kb_path = repo knowledge_base dir
        kb.phenotypes["heds_venous_pooling"].canonical_status  # 'experimental'
        kb.model_parameters["dV_veno_max"].evidence_e_level    # 'E0-E1'
    """

    def __init__(self, kb_path: str):
        self.kb_path = kb_path
        self.phenotypes: Dict[str, PhenotypeRecord] = {}
        self.model_parameters: Dict[str, ParameterRecord] = {}
        self._load_diseases()
        self._load_model_parameters()

    def _load_diseases(self) -> None:
        diseases_dir = os.path.join(self.kb_path, "diseases")
        if not os.path.isdir(diseases_dir):
            return
        for fpath in _iter_data_yaml(diseases_dir):
            with open(fpath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            disease = (data or {}).get("disease", {})
            disease_id = str(disease.get("id", ""))
            for pheno in disease.get("phenotypes", []) or []:
                rec = _phenotype_record(disease_id, pheno)
                self.phenotypes[rec.phenotype_id] = rec

    def _load_model_parameters(self) -> None:
        models_file = os.path.join(self.kb_path, "equations", "mathematical_models.yaml")
        if not os.path.exists(models_file):
            return
        with open(models_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for model in (data or {}).get("models", []) or []:
            for param in model.get("parameters", []) or []:
                rec = _parameter_record(param, "model_nominal")
                self.model_parameters[rec.symbol] = rec

    def canonical_phenotype_ids(self) -> List[str]:
        return sorted(pid for pid, p in self.phenotypes.items() if not p.experimental)

    def experimental_phenotype_ids(self) -> List[str]:
        return sorted(pid for pid, p in self.phenotypes.items() if p.experimental)


def load_kb(kb_path: Optional[str] = None) -> KnowledgeBase:
    """Load the knowledge base with governance metadata resolved.
    kb_path defaults to the repository's knowledge_base/ directory."""
    if kb_path is None:
        kb_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")
    return KnowledgeBase(kb_path)
