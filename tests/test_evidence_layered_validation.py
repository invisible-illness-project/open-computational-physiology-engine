"""
Comprehensive Pytest Suite for OCPE Evidence-Layered Validation Engine (ADR 0001 v2.0.0)
"""

import os
import tempfile
import pytest
from pathlib import Path

from validation.sidecar_manifest import (
    SidecarManifest,
    ReviewEvent,
    Reviewer,
    ReviewerIdentity,
    Claim,
    Challenge,
    Adjudication,
    HumanReviewBlock,
    HumanReviewEntry,
    Finding,
    TargetFile,
    load_sidecar,
    save_sidecar,
    get_sidecar_path,
    compute_sha256,
    aggregate_validation,
    check_authorization,
    migrate_v1_dict_to_v2,
    MANIFEST_VERSION,
)


@pytest.fixture
def temp_asset_workspace(tmp_path):
    """Creates a temporary asset workspace with target file and companion sidecar."""
    asset_file = tmp_path / "sample_model.yaml"
    asset_file.write_text("model_id: test_model\nversion: 1.0.0\nparameters: []\n", encoding="utf-8")
    sidecar_file = get_sidecar_path(asset_file)
    return asset_file, sidecar_file


def test_manifest_v2_creation_and_serialization(temp_asset_workspace):
    asset_file, sidecar_file = temp_asset_workspace
    initial_hash = compute_sha256(asset_file)

    manifest = SidecarManifest(
        review_manifest_version="2.0.0",
        target_file=TargetFile(path=asset_file.name, sha256=initial_hash),
    )

    save_sidecar(sidecar_file, manifest)
    assert sidecar_file.exists()

    loaded = load_sidecar(sidecar_file)
    assert loaded.review_manifest_version == "2.0.0"
    assert loaded.target_file.sha256 == initial_hash


def test_v1_manifest_migration():
    v1_dict = {
        "review_manifest_version": "1.0.0",
        "target_file": {
            "path": "knowledge_base/physiology/variables.yaml",
            "sha256": "abc123hash",
        },
        "review_history": [
            {
                "review_id": "rev-001",
                "reviewed_at": "2026-09-11T00:00:00Z",
                "reviewer": {
                    "kind": "validator",
                    "identity": {"name": "validate_kb.py"},
                },
                "scope": ["schema_syntax"],
                "verdict": "PASSED",
                "findings": [],
                "comments": "Rule validation passed",
            },
            {
                "review_id": "rev-002",
                "reviewed_at": "2026-09-11T01:00:00Z",
                "reviewer": {
                    "kind": "human",
                    "identity": {"name": "Dr. Smith"},
                },
                "scope": ["baseline_units"],
                "verdict": "APPROVED",
                "comments": "Clinical sanity check",
            },
        ],
    }

    manifest = migrate_v1_dict_to_v2(v1_dict)
    assert manifest.review_manifest_version == "2.0.0"
    assert len(manifest.reviews) == 2
    assert manifest.reviews[0].reviewer.kind == "validator"
    assert manifest.human_review.status == "APPROVED"
    assert len(manifest.human_review.reviews) == 1
    assert manifest.human_review.reviews[0].reviewer.name == "Dr. Smith"


def test_sha256_staleness_detection(temp_asset_workspace):
    asset_file, sidecar_file = temp_asset_workspace
    initial_hash = compute_sha256(asset_file)

    manifest = SidecarManifest(
        review_manifest_version="2.0.0",
        target_file=TargetFile(path=asset_file.name, sha256=initial_hash),
        reviews=[
            ReviewEvent(
                review_id="rev-001",
                reviewed_at="2026-09-27T00:00:00Z",
                reviewer=Reviewer("ai_agent", ReviewerIdentity(name="agent1")),
                verdict="SUPPORTED",
            )
        ],
    )
    save_sidecar(sidecar_file, manifest)

    summary_before = aggregate_validation(manifest, asset_file)
    assert summary_before.state == "AGENT_SUPPORTED"

    # Modify asset content
    asset_file.write_text("model_id: test_model\nversion: 2.0.0_MODIFIED\n", encoding="utf-8")

    summary_after = aggregate_validation(manifest, asset_file)
    assert summary_after.state == "STALE"
    # Historical review entry remains preserved!
    assert len(manifest.reviews) == 1


def test_agent_evidence_and_independence_groups(temp_asset_workspace):
    asset_file, sidecar_file = temp_asset_workspace
    h = compute_sha256(asset_file)

    manifest = SidecarManifest(
        review_manifest_version="2.0.0",
        target_file=TargetFile(path=asset_file.name, sha256=h),
    )

    # 2 reviews from the SAME independence group
    r1 = ReviewEvent(
        review_id="rev-01",
        reviewed_at="2026-09-27T00:00:00Z",
        reviewer=Reviewer("ai_agent", ReviewerIdentity(name="agent-a1"), independence_group="literature-family-a"),
        verdict="SUPPORTED",
    )
    r2 = ReviewEvent(
        review_id="rev-02",
        reviewed_at="2026-09-27T01:00:00Z",
        reviewer=Reviewer("ai_agent", ReviewerIdentity(name="agent-a2"), independence_group="literature-family-a"),
        verdict="SUPPORTED",
    )
    manifest.reviews.extend([r1, r2])

    summary = aggregate_validation(manifest, asset_file)
    assert summary.agent_evidence["independent_reviewers"] == 1
    assert summary.agent_evidence["supporting"] == 2

    # Add 1 review from a DIFFERENT independence group
    r3 = ReviewEvent(
        review_id="rev-03",
        reviewed_at="2026-09-27T02:00:00Z",
        reviewer=Reviewer("ai_agent", ReviewerIdentity(name="agent-b1"), independence_group="literature-family-b"),
        verdict="SUPPORTED",
    )
    manifest.reviews.append(r3)

    summary2 = aggregate_validation(manifest, asset_file)
    assert summary2.agent_evidence["independent_reviewers"] == 2
    assert summary2.agent_evidence["supporting"] == 3


def test_agent_disagreement_and_challenges(temp_asset_workspace):
    asset_file, sidecar_file = temp_asset_workspace
    h = compute_sha256(asset_file)

    manifest = SidecarManifest(
        review_manifest_version="2.0.0",
        target_file=TargetFile(path=asset_file.name, sha256=h),
        reviews=[
            ReviewEvent(
                review_id="rev-01",
                reviewed_at="2026-09-27T00:00:00Z",
                reviewer=Reviewer("ai_agent", ReviewerIdentity(name="agent1"), independence_group="grp-a"),
                verdict="SUPPORTED",
            ),
            ReviewEvent(
                review_id="rev-02",
                reviewed_at="2026-09-27T01:00:00Z",
                reviewer=Reviewer("ai_agent", ReviewerIdentity(name="agent2"), independence_group="grp-b"),
                verdict="DISPUTED",
            ),
        ],
    )

    summary = aggregate_validation(manifest, asset_file)
    assert summary.state in {"AGENT_DISPUTED", "ADJUDICATION_REQUIRED"}

    # Add open critical challenge
    manifest.challenges.append(
        Challenge(
            challenge_id="chal-01",
            statement="Parameter range exceeds physiological limit",
            severity="CRITICAL",
            status="OPEN",
        )
    )

    status, reason = check_authorization(manifest, "exploratory_research", asset_file)
    assert status == "PROHIBITED"  # Critical open challenge prohibits exploratory research
    assert "critical scientific challenges" in reason

    status_prod, reason_prod = check_authorization(manifest, "iip_production", asset_file)
    assert status_prod == "PROHIBITED"

    # Resolve the challenge
    manifest.challenges[0].status = "RESOLVED_SUPPORT"
    manifest.challenges[0].resolved_at = "2026-09-27T03:00:00Z"

    # Now exploratory research can proceed with disclosure or allowed if deterministic pass
    status_resolved, _ = check_authorization(manifest, "exploratory_research", asset_file)
    assert status_resolved in {"ALLOWED", "PROHIBITED"}


def test_human_approval_and_iip_production_gate(temp_asset_workspace):
    asset_file, sidecar_file = temp_asset_workspace
    h = compute_sha256(asset_file)

    manifest = SidecarManifest(
        review_manifest_version="2.0.0",
        target_file=TargetFile(path=asset_file.name, sha256=h),
        reviews=[
            ReviewEvent(
                review_id="rev-val",
                reviewed_at="2026-09-27T00:00:00Z",
                reviewer=Reviewer("validator", ReviewerIdentity(name="validate_kb.py")),
                verdict="PASSED",
            ),
            ReviewEvent(
                review_id="rev-agent",
                reviewed_at="2026-09-27T01:00:00Z",
                reviewer=Reviewer("ai_agent", ReviewerIdentity(name="agent1"), independence_group="grp-a"),
                verdict="SUPPORTED",
            ),
        ],
    )

    # Without human approval, IIP production MUST be blocked
    status_no_human, reason_no_human = check_authorization(manifest, "iip_production", asset_file)
    assert status_no_human == "REQUIRES_HUMAN_APPROVAL"

    # Add human approval for current hash
    h_entry = HumanReviewEntry(
        review_id="rev-human",
        reviewer=ReviewerIdentity(name="Dr. Jane Doe", role="Clinical Physiologist"),
        scope=["clinical_safety"],
        verdict="APPROVED",
        reviewed_at="2026-09-27T02:00:00Z",
        target_sha256=h,
    )
    manifest.human_review = HumanReviewBlock(status="APPROVED", reviews=[h_entry])

    status_human, reason_human = check_authorization(manifest, "iip_production", asset_file)
    assert status_human == "ALLOWED"


def test_human_approval_cannot_bypass_stale_hash(temp_asset_workspace):
    asset_file, sidecar_file = temp_asset_workspace
    initial_h = compute_sha256(asset_file)

    manifest = SidecarManifest(
        review_manifest_version="2.0.0",
        target_file=TargetFile(path=asset_file.name, sha256=initial_h),
        reviews=[
            ReviewEvent(
                review_id="rev-val",
                reviewed_at="2026-09-27T00:00:00Z",
                reviewer=Reviewer("validator", ReviewerIdentity(name="validate_kb.py")),
                verdict="PASSED",
            )
        ],
        human_review=HumanReviewBlock(
            status="APPROVED",
            reviews=[
                HumanReviewEntry(
                    review_id="rev-human",
                    reviewer=ReviewerIdentity(name="Dr. Jane Doe"),
                    scope=["clinical_safety"],
                    verdict="APPROVED",
                    reviewed_at="2026-09-27T02:00:00Z",
                    target_sha256=initial_h,
                )
            ],
        ),
    )

    # Asset is modified
    asset_file.write_text("model_id: test_model\nmodified: true\n", encoding="utf-8")

    status, reason = check_authorization(manifest, "iip_production", asset_file)
    assert status == "PROHIBITED"
    assert "STALE" in reason


def test_manifest_yaml_override_prevention(temp_asset_workspace):
    """Verifies that manually crafting authorization: iip_production: ALLOWED in manifest YAML
    cannot bypass the policy enforcement engine."""
    asset_file, sidecar_file = temp_asset_workspace
    h = compute_sha256(asset_file)

    manifest = SidecarManifest(
        review_manifest_version="2.0.0",
        target_file=TargetFile(path=asset_file.name, sha256=h),
        reviews=[
            ReviewEvent(
                review_id="rev-agent",
                reviewed_at="2026-09-27T01:00:00Z",
                reviewer=Reviewer("ai_agent", ReviewerIdentity(name="agent1")),
                verdict="SUPPORTED",
            ),
        ],
        # Malicious / naive attempt to claim IIP production status in YAML:
        authorization={"iip_production": {"status": "ALLOWED"}},
    )

    # Policy engine MUST evaluate real evidence and reject IIP production without human approval!
    status, reason = check_authorization(manifest, "iip_production", asset_file)
    assert status == "REQUIRES_HUMAN_APPROVAL"
