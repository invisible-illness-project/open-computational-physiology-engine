"""
Evidence aggregation for governance review manifests (ADR 0001 v2.0.0).

Derives a validation *state* from recorded review events, challenges and human
reviews. This is a governance summary of review activity; it never asserts that
content is scientifically correct. Split out of the pre-0.1
validation/sidecar_manifest.py without behavioural change.
"""

from pathlib import Path
from typing import List, Optional, Set

from .manifest import DerivedValidationSummary, SidecarManifest, compute_sha256


def aggregate_validation(manifest: SidecarManifest, target_path: Optional[Path] = None) -> DerivedValidationSummary:
    """
    Aggregates evidence across review events, claims, challenges, human reviews, and content hash.
    Calculates derived validation state and explanation.
    """
    explanation: List[str] = []

    # 1. Staleness check
    is_stale = False
    if target_path and target_path.exists():
        current_hash = compute_sha256(target_path)
        if manifest.target_file.sha256 and current_hash != manifest.target_file.sha256:
            is_stale = True
            explanation.append(f"STALE: Current file hash ({current_hash[:12]}...) does not match manifest hash ({manifest.target_file.sha256[:12]}...).")

    # 2. Deterministic Validation
    deterministic_reviews = [r for r in manifest.reviews if r.reviewer.kind == "validator"]
    det_status = "NOT_RUN"
    if deterministic_reviews:
        has_fail = any(r.verdict in {"FAILED", "REJECTED"} for r in deterministic_reviews)
        if has_fail:
            det_status = "FAILED"
            explanation.append("Deterministic validation checks failed.")
        else:
            det_status = "PASSED"
            explanation.append("Deterministic validation checks passed.")

    # 3. Agent Evidence & Independence Groups
    agent_reviews = [r for r in manifest.reviews if r.reviewer.kind == "ai_agent"]
    independence_groups: Set[str] = set()
    supporting_cnt = 0
    disputing_cnt = 0
    abstaining_cnt = 0

    for r in agent_reviews:
        # Determine independence group identifier
        group = r.reviewer.independence_group
        if not group:
            # Fallback to model_name or provider if independence_group not specified
            ident = r.reviewer.identity
            group = ident.model_name or ident.provider or ident.name or "default_group"

        independence_groups.add(group)

        if r.verdict in {"SUPPORTED", "PASSED", "PASSED_WITH_WARNINGS", "APPROVED"}:
            supporting_cnt += 1
        elif r.verdict in {"DISPUTED", "FAILED", "REJECTED", "NEEDS_REVISION"}:
            disputing_cnt += 1
        elif r.verdict in {"ABSTAIN", "NEUTRAL"}:
            abstaining_cnt += 1

    independent_reviewers_cnt = len(independence_groups)

    if agent_reviews:
        explanation.append(
            f"Agent evidence: {supporting_cnt} supporting, {disputing_cnt} disputing, "
            f"{abstaining_cnt} abstaining across {independent_reviewers_cnt} distinct independence groups."
        )

    # 4. Computational Reproduction
    comp_reviews = [r for r in manifest.reviews if any(s in r.scope for s in ["computational_reproduction", "simulation_verification"])]
    comp_status = "NOT_RUN"
    if comp_reviews:
        if any(r.verdict in {"PASSED", "SUPPORTED", "APPROVED"} for r in comp_reviews):
            comp_status = "PASSED"
            explanation.append("Computational reproduction succeeded.")
        elif any(r.verdict in {"FAILED", "REJECTED"} for r in comp_reviews):
            comp_status = "FAILED"
            explanation.append("Computational reproduction failed.")

    # 5. Challenges
    open_challenges = [ch for ch in manifest.challenges if ch.status in {"OPEN", "UNDER_INVESTIGATION", "UNRESOLVED"}]
    critical_challenges = [ch for ch in open_challenges if ch.severity == "CRITICAL"]

    if open_challenges:
        explanation.append(f"Open scientific challenges: {len(open_challenges)} ({len(critical_challenges)} critical).")

    # 6. Human Review
    human_approved = False
    human_rejected = False
    human_reviews = [r for r in manifest.reviews if r.reviewer.kind == "human"] or manifest.human_review.reviews

    if human_reviews:
        # Check human reviews matching current hash
        for hr in human_reviews:
            h_verdict = getattr(hr, "verdict", "REVIEWED")
            h_hash = getattr(hr, "target_sha256", None) or manifest.target_file.sha256
            if target_path and target_path.exists():
                curr_h = compute_sha256(target_path)
                if h_hash != curr_h:
                    continue  # Human review is stale for current hash
            if h_verdict == "APPROVED":
                human_approved = True
            elif h_verdict == "REJECTED":
                human_rejected = True

    if human_approved:
        explanation.append("Human expert review: APPROVED for target content hash.")
    elif manifest.human_review.status != "NOT_REVIEWED":
        explanation.append(f"Human expert review status: {manifest.human_review.status}.")
    else:
        explanation.append("Human expert review: NOT REVIEWED.")

    # Derive validation state
    if is_stale:
        state = "STALE"
    elif human_approved:
        state = "HUMAN_APPROVED"
    elif human_rejected:
        state = "ADJUDICATION_REQUIRED"
    elif critical_challenges or disputing_cnt > 0:
        if manifest.adjudication.status != "NOT_REQUIRED":
            state = "ADJUDICATION_REQUIRED"
        else:
            state = "AGENT_DISPUTED"
    elif comp_status == "PASSED" and supporting_cnt > 0:
        state = "COMPUTATIONALLY_REPRODUCED"
    elif supporting_cnt >= 1 and independent_reviewers_cnt >= 1:
        state = "AGENT_SUPPORTED"
    elif agent_reviews:
        state = "AGENT_REVIEWED"
    elif det_status == "PASSED":
        state = "DETERMINISTICALLY_VALID"
    else:
        state = "UNREVIEWED"

    summary = DerivedValidationSummary(
        state=state,
        deterministic={"status": det_status},
        agent_evidence={
            "independent_reviewers": independent_reviewers_cnt,
            "supporting": supporting_cnt,
            "disputing": disputing_cnt,
            "abstaining": abstaining_cnt,
        },
        computational={"status": comp_status},
        explanation=explanation,
    )

    manifest.validation = summary
    return summary
