#!/usr/bin/env python3
"""
Provenance Gate (G-P0-08 / G-P0-10) — dataset-build preflight + generation-mode gate.

Fail-closed governance checks that the dataset builder (W2-F) and the
simulation engine MUST pass before generating canonical data:

1. Review governance (per tools/review_tracker.py sidecars, schema v1.0.0):
   * missing review            -> MissingReviewError
   * STALE (file modified after the last recorded review, SHA-256 mismatch)
                               -> StaleReviewError   (hash-tamper safe)
   * no human (L3) review      -> WARNING only (never a silent pass, never a
                                  hard failure while human review is pending)
2. Evidence harmonization (G-P0-10):
   * missing evidence tier     -> MissingEvidenceTierError
   * missing provenance block  -> MissingProvenanceError
3. Generation-mode policy (G-P0-08):
   * canonical mode refuses experimental phenotypes/parameters
                               -> ExperimentalPerturbationError
   * experimental mode requires explicit opt-in (allow_experimental=True)
                               -> ExperimentalModeOptInRequired

Integration API (for the orchestrator / engine / dataset builder):

    from validation.provenance_gate import (
        preflight_dataset_build, gate_generation_mode, gate_phenotype_selection,
        ProvenanceGateError)

    # (a) whole-KB preflight before a dataset build; raises on failure:
    report = preflight_dataset_build(kb_dir, mode="canonical",
                                     phenotype_ids=["hypovolemic_pots"],
                                     sensor_ids=["polar_h10"])
    report.raise_if_failed()          # fail-closed
    report.warnings                   # human-L3 pending, etc.

    # (b) engine start-up: choose the generation mode (fail-closed):
    gate_generation_mode("experimental", allow_experimental=True)

    # (c) per-phenotype selection before applying perturbations:
    kb = load_kb(kb_dir)
    gate_phenotype_selection(kb.phenotypes[pid], mode="canonical")

Python 3 + PyYAML only (SPEC global rule 9).
"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "tools"))
sys.path.insert(0, _REPO_ROOT)

from review_tracker import compute_sha256, get_sidecar_path, load_sidecar  # noqa: E402
from tools.kb_access import (  # noqa: E402
    CANONICAL,
    EXPERIMENTAL,
    KnowledgeBase,
    PhenotypeRecord,
    evidence_tier_of,
    resolve_canonical_status,
)

GENERATION_MODES = (CANONICAL, EXPERIMENTAL)

HUMAN_L3_WARNING = (
    "no human (L3) review recorded; AI-agent/validator reviews only — "
    "file is provisionally admissible pending human review"
)


# ---------------------------------------------------------------------------
# Error types
# ---------------------------------------------------------------------------

class ProvenanceGateError(Exception):
    """Base class for all provenance-gate refusals (fail-closed)."""


class MissingReviewError(ProvenanceGateError):
    """No review sidecar or empty review history for a KB file."""


class StaleReviewError(ProvenanceGateError):
    """KB file content changed after the last recorded review (hash mismatch)."""


class MissingEvidenceTierError(ProvenanceGateError):
    """A governed block carries no evidence tier."""


class MissingProvenanceError(ProvenanceGateError):
    """A governed block carries no provenance block."""


class ExperimentalPerturbationError(ProvenanceGateError):
    """Experimental content selected in canonical generation mode."""


class ExperimentalModeOptInRequired(ProvenanceGateError):
    """Experimental generation mode requested without explicit opt-in."""


# ---------------------------------------------------------------------------
# Review status
# ---------------------------------------------------------------------------

@dataclass
class ReviewStatus:
    state: str                 # FRESH | STALE | UNREVIEWED
    human_l3_present: bool
    n_reviews: int
    recorded_sha256: str = ""
    current_sha256: str = ""


def check_review_status(target_path: Path) -> ReviewStatus:
    """Freshness + human-L3 presence of one KB file per review_tracker sidecar."""
    target_path = Path(target_path)
    sidecar = get_sidecar_path(target_path)
    current_hash = compute_sha256(target_path)
    if not sidecar.exists():
        return ReviewStatus("UNREVIEWED", False, 0, "", current_hash)
    manifest = load_sidecar(sidecar)
    history = manifest.get("review_history", []) or []
    recorded = manifest.get("target_file", {}).get("sha256", "")
    human_l3 = any(
        (e.get("reviewer", {}) or {}).get("kind") == "human" for e in history
    )
    if not history:
        return ReviewStatus("UNREVIEWED", human_l3, 0, recorded, current_hash)
    state = "FRESH" if recorded == current_hash else "STALE"
    return ReviewStatus(state, human_l3, len(history), recorded, current_hash)


# ---------------------------------------------------------------------------
# File-level gate
# ---------------------------------------------------------------------------

@dataclass
class FileGateResult:
    path: str
    ok: bool
    errors: List[ProvenanceGateError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    review_status: Optional[ReviewStatus] = None


def _has_provenance(block: Dict[str, Any]) -> bool:
    """A provenance block exists (a doi is NOT required: tier-D blocks
    legitimately document the *absence* of a source)."""
    if not isinstance(block, dict):
        return False
    prov = block.get("provenance")
    return isinstance(prov, dict) and bool(prov)


def _check_governed_block(block: Dict[str, Any], label: str,
                          errors: List[ProvenanceGateError]) -> None:
    if evidence_tier_of(block) is None:
        errors.append(MissingEvidenceTierError(f"{label}: missing evidence_tier"))
    if not (_has_provenance(block) or isinstance(block.get("association_evidence"), dict)
            or block.get("evidence_tier") is not None):
        errors.append(MissingProvenanceError(f"{label}: missing provenance block"))
    # resolve_canonical_status validates the enum (raises KBAccessError on bad values)
    try:
        resolve_canonical_status(block)
    except Exception as exc:
        errors.append(ProvenanceGateError(f"{label}: {exc}"))


def gate_kb_file(target_path: Path, mode: str = CANONICAL) -> FileGateResult:
    """Gate one KB file: review freshness + tier/provenance completeness.

    Content checks apply to perturbation/parameter-bearing files
    (knowledge_base/diseases/*.yaml, equations/mathematical_models.yaml,
    equations/definitions.yaml, interventions/*.yaml, wearables/*.yaml);
    other KB files receive review-governance checks only.
    """
    import yaml

    target_path = Path(target_path)
    rel = str(target_path)
    result = FileGateResult(path=rel, ok=False)

    if not target_path.exists():
        result.errors.append(ProvenanceGateError(f"file not found: {rel}"))
        return result

    # 1. Review governance
    status = check_review_status(target_path)
    result.review_status = status
    if status.state == "UNREVIEWED":
        result.errors.append(MissingReviewError(f"{rel}: no review recorded"))
    elif status.state == "STALE":
        result.errors.append(StaleReviewError(
            f"{rel}: file modified after last recorded review "
            f"(recorded {status.recorded_sha256[:12]}..., current {status.current_sha256[:12]}...)"))
    if not status.human_l3_present:
        result.warnings.append(f"{rel}: {HUMAN_L3_WARNING}")

    # 2. Evidence-harmonization content checks (data YAML only)
    if target_path.suffix not in (".yaml", ".yml") or target_path.name.endswith(".review.yaml"):
        result.ok = not result.errors
        return result

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as exc:
        result.errors.append(ProvenanceGateError(f"{rel}: unparseable YAML: {exc}"))
        return result

    parts = target_path.parts
    if "diseases" in parts and isinstance(data, dict) and "disease" in data:
        disease = data["disease"]
        _check_governed_block(disease, f"{target_path.name}:disease", result.errors)
        for pheno in disease.get("phenotypes", []) or []:
            pid = pheno.get("id", "?")
            _check_governed_block(pheno, f"{target_path.name}:phenotype[{pid}]", result.errors)
            for section in ("parameters_perturbed", "unverified_parameters"):
                for pert in pheno.get(section, []) or []:
                    sym = pert.get("symbol", "?")
                    _check_governed_block(
                        pert, f"{target_path.name}:phenotype[{pid}].{section}[{sym}]",
                        result.errors)
    elif target_path.name == "mathematical_models.yaml":
        for model in (data or {}).get("models", []) or []:
            mid = model.get("model_id", "?")
            for param in model.get("parameters", []) or []:
                _check_governed_block(
                    param, f"{target_path.name}:model[{mid}].param[{param.get('symbol', '?')}]",
                    result.errors)
    elif target_path.name == "definitions.yaml":
        ev = (data or {}).get("evidence")
        if not isinstance(ev, dict):
            result.errors.append(MissingProvenanceError(
                f"{target_path.name}: missing top-level 'evidence' block"))
        else:
            _check_governed_block(ev, f"{target_path.name}:evidence", result.errors)
    elif target_path.name == "artifact_models.yaml":
        # Cross-device artifact library (W1-D): non-standard root key
        # `artifact_models:`; governance metadata lives at the top level.
        _check_governed_block(data or {}, f"{target_path.name}", result.errors)
    elif "interventions" in parts or "wearables" in parts:
        body = (data or {}).get("intervention") or (data or {}).get("sensor") or {}
        _check_governed_block(body, f"{target_path.name}", result.errors)

    result.ok = not result.errors
    return result


# ---------------------------------------------------------------------------
# Generation-mode gate (G-P0-08)
# ---------------------------------------------------------------------------

def gate_generation_mode(mode: str, allow_experimental: bool = False) -> str:
    """Validate a generation-mode request. Fail-closed.

    canonical    -> always allowed (returns 'canonical').
    experimental -> REQUIRES explicit opt-in allow_experimental=True, else
                    raises ExperimentalModeOptInRequired.
    """
    mode = str(mode).strip().lower()
    if mode not in GENERATION_MODES:
        raise ProvenanceGateError(
            f"unknown generation mode {mode!r}; expected one of {GENERATION_MODES}")
    if mode == EXPERIMENTAL and not allow_experimental:
        raise ExperimentalModeOptInRequired(
            "experimental generation mode requires explicit opt-in "
            "(allow_experimental=True); refusing to run experimental perturbations silently")
    return mode


def gate_phenotype_selection(phenotype: PhenotypeRecord, mode: str = CANONICAL,
                             allow_experimental: bool = False) -> PhenotypeRecord:
    """Check that one phenotype may be applied under the given generation mode.

    * canonical mode: refuses experimental phenotypes and phenotypes whose
      only effect is experimental (fail-closed, ExperimentalPerturbationError).
    * experimental mode: requires explicit opt-in (gate_generation_mode).
    Returns the phenotype record unchanged on success.
    """
    gate_generation_mode(mode, allow_experimental=allow_experimental)
    if mode == CANONICAL and phenotype.experimental:
        raise ExperimentalPerturbationError(
            f"phenotype '{phenotype.phenotype_id}' is canonical_status=experimental "
            f"(tier {phenotype.evidence_tier or 'none'}); canonical-mode generation "
            "refuses experimental perturbations — rerun in experimental mode with "
            "explicit opt-in or promote the evidence via human review")
    return phenotype


# ---------------------------------------------------------------------------
# Dataset-build preflight
# ---------------------------------------------------------------------------

@dataclass
class PreflightReport:
    mode: str
    kb_dir: str
    file_results: List[FileGateResult] = field(default_factory=list)
    selection_errors: List[ProvenanceGateError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def errors(self) -> List[ProvenanceGateError]:
        errs: List[ProvenanceGateError] = list(self.selection_errors)
        for r in self.file_results:
            errs.extend(r.errors)
        return errs

    @property
    def warnings(self) -> List[str]:
        warns: List[str] = []
        for r in self.file_results:
            warns.extend(r.warnings)
        return warns

    def raise_if_failed(self) -> "PreflightReport":
        """Fail-closed: raise ProvenanceGateError aggregating all refusals."""
        if not self.ok:
            msg = "\n  - ".join(str(e) for e in self.errors)
            raise ProvenanceGateError(
                f"provenance gate REFUSED dataset build "
                f"({len(self.errors)} refusal(s), mode={self.mode}):\n  - {msg}")
        return self


def _iter_kb_files(kb_dir: Path):
    for root, _, files in os.walk(kb_dir):
        for fname in sorted(files):
            if (fname.endswith((".yaml", ".yml", ".md"))
                    and not fname.endswith(".review.yaml")):
                yield Path(root) / fname


def preflight_dataset_build(kb_dir: Optional[str] = None,
                            mode: str = CANONICAL,
                            allow_experimental: bool = False,
                            phenotype_ids: Optional[List[str]] = None,
                            sensor_ids: Optional[List[str]] = None) -> PreflightReport:
    """Dataset-build preflight over the whole knowledge base. Fail-closed.

    Refuses (collects errors) for every KB file that is: missing review,
    STALE per review_tracker (hash-tamper safe), missing evidence tier, or
    missing provenance. Human-L3 absence is surfaced as a WARNING per file.

    In canonical mode, selecting an experimental phenotype/sensor adds an
    ExperimentalPerturbationError. Experimental mode requires explicit opt-in.

    Returns a PreflightReport; call report.raise_if_failed() to enforce.
    """
    if kb_dir is None:
        kb_dir = os.path.join(_REPO_ROOT, "knowledge_base")
    mode = gate_generation_mode(mode, allow_experimental=allow_experimental)
    report = PreflightReport(mode=mode, kb_dir=str(kb_dir))

    for fpath in _iter_kb_files(Path(kb_dir)):
        report.file_results.append(gate_kb_file(fpath, mode=mode))

    if phenotype_ids or sensor_ids:
        kb = KnowledgeBase(str(kb_dir))
        for pid in phenotype_ids or []:
            pheno = kb.phenotypes.get(pid)
            if pheno is None:
                report.selection_errors.append(
                    ProvenanceGateError(f"unknown phenotype id {pid!r}"))
                continue
            try:
                gate_phenotype_selection(pheno, mode=mode,
                                         allow_experimental=allow_experimental)
            except ProvenanceGateError as exc:
                report.selection_errors.append(exc)
        for sid in sensor_ids or []:
            sfile = _find_sensor_file(str(kb_dir), sid)
            if sfile is None:
                report.selection_errors.append(
                    ProvenanceGateError(f"unknown sensor id {sid!r}"))
                continue
            import yaml
            with open(sfile, "r", encoding="utf-8") as f:
                body = (yaml.safe_load(f) or {}).get("sensor", {})
            if mode == CANONICAL and resolve_canonical_status(body) == EXPERIMENTAL:
                report.selection_errors.append(ExperimentalPerturbationError(
                    f"sensor '{sid}' is canonical_status=experimental; canonical-mode "
                    "generation refuses it — use a canonical device profile or explicit "
                    "experimental opt-in"))
    return report


def _find_sensor_file(kb_dir: str, sensor_id: str) -> Optional[str]:
    import yaml
    wearables = os.path.join(kb_dir, "wearables")
    if not os.path.isdir(wearables):
        return None
    for fname in sorted(os.listdir(wearables)):
        if fname.endswith(".yaml") and not fname.endswith(".review.yaml"):
            fpath = os.path.join(wearables, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                body = (yaml.safe_load(f) or {}).get("sensor", {})
            if body.get("id") == sensor_id:
                return fpath
    return None
