"""
Downstream-use authorization (OPTIONAL, organisation-specific policy).

Implements the Invisible Illness Project default policy documented as data in
specification/governance/authorization-policy.iip.yaml. Authorization is a
separate layer from evidence and review records: OCPE content can be loaded,
validated and resolved without ever invoking this module. Split out of the
pre-0.1 validation/sidecar_manifest.py without behavioural change.
"""

from pathlib import Path
from typing import Optional, Tuple

from .aggregation import aggregate_validation
from .manifest import AUTHORIZATION_USES, SidecarManifest, compute_sha256


def check_authorization(
    manifest: SidecarManifest,
    use_case: str,
    target_path: Optional[Path] = None,
) -> Tuple[str, str]:
    """
    Enforces downstream usage policies based on evidence state, human review, open challenges, and content freshness.
    Returns (status, reason) where status is one of ALLOWED, ALLOWED_WITH_DISCLOSURE, REQUIRES_HUMAN_APPROVAL, PROHIBITED.
    """
    if use_case not in AUTHORIZATION_USES:
        return "PROHIBITED", f"Unknown use case '{use_case}'"

    # Always re-aggregate validation state first
    summary = aggregate_validation(manifest, target_path)

    # Cryptographic integrity check
    if summary.state == "STALE":
        return "PROHIBITED", "Asset content hash is STALE (target file modified since validation)."

    # Check deterministic validation
    if summary.deterministic.get("status") == "FAILED":
        return "PROHIBITED", "Asset failed deterministic validation checks."

    # Check for unresolved critical challenges
    critical_challenges = [ch for ch in manifest.challenges if ch.status in {"OPEN", "UNRESOLVED"} and ch.severity == "CRITICAL"]
    if critical_challenges:
        return "PROHIBITED", f"Asset has {len(critical_challenges)} unresolved critical scientific challenges."

    # IIP Production Rule: Mandatory human review & approval required!
    if use_case == "iip_production":
        # Check human approval specifically
        human_approved = False
        if target_path and target_path.exists():
            curr_h = compute_sha256(target_path)
            for hr in manifest.human_review.reviews:
                if hr.verdict == "APPROVED" and (hr.target_sha256 is None or hr.target_sha256 == curr_h):
                    human_approved = True
        elif summary.state == "HUMAN_APPROVED":
            human_approved = True

        if not human_approved:
            return "REQUIRES_HUMAN_APPROVAL", "IIP production use requires explicit human expert review and approval."
        return "ALLOWED", "Asset satisfies IIP production requirements (human approved, deterministic pass, valid hash)."

    # Clinical use rule
    if use_case == "clinical":
        return "PROHIBITED", "Clinical use is strictly PROHIBITED under current research engine governance."

    # Exploratory Research
    if use_case == "exploratory_research":
        if summary.state in {"DETERMINISTICALLY_VALID", "AGENT_REVIEWED", "AGENT_SUPPORTED", "COMPUTATIONALLY_REPRODUCED", "HUMAN_REVIEWED", "HUMAN_APPROVED"}:
            return "ALLOWED", "Asset is permitted for exploratory research."
        return "PROHIBITED", "Asset has not passed deterministic checks."

    # Third-Party Research
    if use_case == "third_party_research":
        if summary.state == "HUMAN_APPROVED":
            return "ALLOWED", "Asset is human-approved for third-party research."
        elif summary.state in {"AGENT_SUPPORTED", "COMPUTATIONALLY_REPRODUCED"}:
            return "ALLOWED_WITH_DISCLOSURE", "Allowed with disclosure that human review has not been completed."
        elif summary.state in {"DETERMINISTICALLY_VALID", "AGENT_REVIEWED"}:
            return "ALLOWED_WITH_DISCLOSURE", "Allowed with disclosure: deterministic/initial agent review only."
        return "PROHIBITED", "Asset is unreviewed or disputed."

    # IIP Research
    if use_case == "iip_research":
        if summary.state in {"AGENT_SUPPORTED", "COMPUTATIONALLY_REPRODUCED", "HUMAN_REVIEWED", "HUMAN_APPROVED"}:
            return "ALLOWED", "Asset is permitted for IIP research workflows."
        elif summary.state in {"DETERMINISTICALLY_VALID", "AGENT_REVIEWED"}:
            return "ALLOWED", "Asset permitted for early IIP research iteration."
        return "PROHIBITED", "Asset is unreviewed or failed validation."

    return "PROHIBITED", "Policy rule not met."
