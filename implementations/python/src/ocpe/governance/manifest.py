"""
Sidecar Manifest and Evidence-Layered Validation Engine (v2.0.0)

Implements the evidence-layered validation architecture for OCPE assets as specified
in ADR 0001 (Sidecar Manifests and Evidence-Layered Validation).
"""

import datetime
import hashlib
import os
import sys
import uuid
import yaml
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set

MANIFEST_VERSION = "2.0.0"

VALID_REVIEWER_KINDS = {"validator", "ai_agent", "human"}

VALID_VERDICTS = {
    "PASSED",
    "SUPPORTED",
    "DISPUTED",
    "PASSED_WITH_WARNINGS",
    "NEEDS_REVISION",
    "REJECTED",
    "APPROVED",
    "ABSTAIN",
}

VALIDATION_STATES = {
    "UNREVIEWED",
    "DETERMINISTICALLY_VALID",
    "AGENT_REVIEWED",
    "AGENT_SUPPORTED",
    "AGENT_DISPUTED",
    "ADJUDICATION_REQUIRED",
    "COMPUTATIONALLY_REPRODUCED",
    "HUMAN_REVIEWED",
    "HUMAN_APPROVED",
    "STALE",
}

CHALLENGE_STATUSES = {
    "OPEN",
    "UNDER_INVESTIGATION",
    "RESOLVED_SUPPORT",
    "RESOLVED_REJECTION",
    "UNRESOLVED",
}

HUMAN_REVIEW_STATUSES = {
    "NOT_REVIEWED",
    "REVIEWED",
    "APPROVED",
    "REJECTED",
    "QUALIFIED",
}

AUTHORIZATION_USES = {
    "exploratory_research",
    "third_party_research",
    "iip_research",
    "iip_production",
    "clinical",
}

AUTHORIZATION_STATUSES = {
    "ALLOWED",
    "ALLOWED_WITH_DISCLOSURE",
    "REQUIRES_HUMAN_APPROVAL",
    "PROHIBITED",
}


def compute_sha256(filepath: Path) -> str:
    """Computes SHA-256 hex digest of a target file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_sidecar_path(target_path: Path) -> Path:
    """Returns the sidecar path for a given target file (<file>.<ext>.review.yaml)."""
    return target_path.parent / f"{target_path.name}.review.yaml"


@dataclass
class Finding:
    category: str = "general"
    severity: str = "INFO"  # INFO, WARNING, CRITICAL
    message: str = ""
    location: Optional[str] = None
    path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"category": self.category, "severity": self.severity, "message": self.message}
        if self.location:
            d["location"] = self.location
        if self.path:
            d["path"] = self.path
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Finding":
        return cls(
            category=data.get("category", "general"),
            severity=data.get("severity", "INFO"),
            message=data.get("message", ""),
            location=data.get("location"),
            path=data.get("path"),
        )


@dataclass
class ReviewerIdentity:
    name: str = ""
    version: Optional[str] = None
    commit_sha: Optional[str] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    agent_role: Optional[str] = None
    methodology_version: Optional[str] = None
    system_prompt_sha256: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    role: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {}
        if self.name:
            res["name"] = self.name
        if self.version:
            res["version"] = self.version
        if self.commit_sha:
            res["commit_sha"] = self.commit_sha
        if self.provider:
            res["provider"] = self.provider
        if self.model_name:
            res["model_name"] = self.model_name
        if self.model_version:
            res["model_version"] = self.model_version
        if self.agent_role:
            res["agent_role"] = self.agent_role
        if self.methodology_version:
            res["methodology_version"] = self.methodology_version
        if self.system_prompt_sha256:
            res["system_prompt_sha256"] = self.system_prompt_sha256
        if self.parameters:
            res["parameters"] = self.parameters
        if self.role:
            res["role"] = self.role
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReviewerIdentity":
        if not isinstance(data, dict):
            return cls(name=str(data))
        return cls(
            name=data.get("name", ""),
            version=data.get("version"),
            commit_sha=data.get("commit_sha"),
            provider=data.get("provider"),
            model_name=data.get("model_name"),
            model_version=data.get("model_version"),
            agent_role=data.get("agent_role"),
            methodology_version=data.get("methodology_version"),
            system_prompt_sha256=data.get("system_prompt_sha256"),
            parameters=data.get("parameters", {}),
            role=data.get("role"),
        )


@dataclass
class Reviewer:
    kind: str  # validator, ai_agent, human
    identity: ReviewerIdentity
    independence_group: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "kind": self.kind,
            "identity": self.identity.to_dict(),
        }
        if self.independence_group:
            d["independence_group"] = self.independence_group
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Reviewer":
        kind = data.get("kind", "validator")
        identity = ReviewerIdentity.from_dict(data.get("identity", {}))
        independence_group = data.get("independence_group")
        return cls(kind=kind, identity=identity, independence_group=independence_group)


@dataclass
class ReviewEvent:
    review_id: str
    reviewed_at: str
    reviewer: Reviewer
    scope: List[str] = field(default_factory=list)
    verdict: str = "SUPPORTED"
    confidence: float = 1.0
    findings: List[Finding] = field(default_factory=list)
    comments: str = ""
    target_sha256: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "review_id": self.review_id,
            "reviewed_at": self.reviewed_at,
            "reviewer": self.reviewer.to_dict(),
            "scope": self.scope,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "findings": [f.to_dict() for f in self.findings],
        }
        if self.comments:
            d["comments"] = self.comments
        if self.target_sha256:
            d["target_sha256"] = self.target_sha256
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReviewEvent":
        findings = [Finding.from_dict(f) for f in data.get("findings", [])]
        reviewer = Reviewer.from_dict(data.get("reviewer", {}))
        return cls(
            review_id=data.get("review_id", f"rev-{uuid.uuid4()}"),
            reviewed_at=data.get("reviewed_at", datetime.datetime.now(datetime.timezone.utc).isoformat()),
            reviewer=reviewer,
            scope=data.get("scope", []),
            verdict=data.get("verdict", "SUPPORTED"),
            confidence=float(data.get("confidence", 1.0)),
            findings=findings,
            comments=data.get("comments", ""),
            target_sha256=data.get("target_sha256"),
        )


@dataclass
class ClaimEvidence:
    source_id: str
    relevance: str = "direct"

    def to_dict(self) -> Dict[str, Any]:
        return {"source_id": self.source_id, "relevance": self.relevance}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClaimEvidence":
        if isinstance(data, str):
            return cls(source_id=data)
        return cls(
            source_id=data.get("source_id", ""),
            relevance=data.get("relevance", "direct"),
        )


@dataclass
class Claim:
    claim_id: str
    statement: str
    status: str = "UNREVIEWED"  # UNREVIEWED, SUPPORTED, DISPUTED, UNRESOLVED
    evidence: List[ClaimEvidence] = field(default_factory=list)
    supporting_reviews: List[str] = field(default_factory=list)
    challenging_reviews: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "statement": self.statement,
            "status": self.status,
            "evidence": [e.to_dict() for e in self.evidence],
            "supporting_reviews": self.supporting_reviews,
            "challenging_reviews": self.challenging_reviews,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Claim":
        evidence = [ClaimEvidence.from_dict(e) for e in data.get("evidence", [])]
        return cls(
            claim_id=data.get("claim_id", f"claim-{uuid.uuid4()}"),
            statement=data.get("statement", ""),
            status=data.get("status", "UNREVIEWED"),
            evidence=evidence,
            supporting_reviews=data.get("supporting_reviews", []),
            challenging_reviews=data.get("challenging_reviews", []),
        )


@dataclass
class Challenge:
    challenge_id: str
    target_claim: Optional[str] = None
    challenger: Reviewer = field(default_factory=lambda: Reviewer("ai_agent", ReviewerIdentity(name="agent")))
    reason: Dict[str, Any] = field(default_factory=dict)
    statement: str = ""
    evidence: List[ClaimEvidence] = field(default_factory=list)
    status: str = "OPEN"  # OPEN, UNDER_INVESTIGATION, RESOLVED_SUPPORT, RESOLVED_REJECTION, UNRESOLVED
    severity: str = "CRITICAL"  # CRITICAL, MINOR
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    resolved_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "challenge_id": self.challenge_id,
            "challenger": self.challenger.to_dict(),
            "reason": self.reason,
            "statement": self.statement,
            "evidence": [e.to_dict() for e in self.evidence],
            "status": self.status,
            "severity": self.severity,
            "created_at": self.created_at,
        }
        if self.target_claim:
            d["target_claim"] = self.target_claim
        if self.resolved_at:
            d["resolved_at"] = self.resolved_at
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Challenge":
        challenger = Reviewer.from_dict(data.get("challenger", {}))
        evidence = [ClaimEvidence.from_dict(e) for e in data.get("evidence", [])]
        reason = data.get("reason", {})
        if isinstance(reason, str):
            reason = {"type": reason}
        return cls(
            challenge_id=data.get("challenge_id", f"challenge-{uuid.uuid4()}"),
            target_claim=data.get("target_claim"),
            challenger=challenger,
            reason=reason,
            statement=data.get("statement", ""),
            evidence=evidence,
            status=data.get("status", "OPEN"),
            severity=data.get("severity", "CRITICAL"),
            created_at=data.get("created_at", datetime.datetime.now(datetime.timezone.utc).isoformat()),
            resolved_at=data.get("resolved_at"),
        )


@dataclass
class Adjudication:
    status: str = "NOT_REQUIRED"  # NOT_REQUIRED, OPEN, IN_PROGRESS, RESOLVED_SUPPORT, RESOLVED_REJECTION
    basis: List[str] = field(default_factory=list)
    unresolved_limitations: List[str] = field(default_factory=list)
    adjudicator: Optional[ReviewerIdentity] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "status": self.status,
            "basis": self.basis,
            "unresolved_limitations": self.unresolved_limitations,
        }
        if self.adjudicator:
            d["adjudicator"] = self.adjudicator.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Adjudication":
        if not isinstance(data, dict):
            return cls()
        adjudicator = ReviewerIdentity.from_dict(data["adjudicator"]) if data.get("adjudicator") else None
        return cls(
            status=data.get("status", "NOT_REQUIRED"),
            basis=data.get("basis", []),
            unresolved_limitations=data.get("unresolved_limitations", []),
            adjudicator=adjudicator,
        )


@dataclass
class HumanReviewEntry:
    review_id: str
    reviewer: ReviewerIdentity
    scope: List[str]
    verdict: str  # APPROVED, REJECTED, QUALIFIED
    reviewed_at: str
    target_sha256: Optional[str] = None
    comments: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "review_id": self.review_id,
            "reviewer": self.reviewer.to_dict(),
            "scope": self.scope,
            "verdict": self.verdict,
            "reviewed_at": self.reviewed_at,
        }
        if self.target_sha256:
            d["target_sha256"] = self.target_sha256
        if self.comments:
            d["comments"] = self.comments
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HumanReviewEntry":
        return cls(
            review_id=data.get("review_id", f"human-rev-{uuid.uuid4()}"),
            reviewer=ReviewerIdentity.from_dict(data.get("reviewer", {})),
            scope=data.get("scope", []),
            verdict=data.get("verdict", "APPROVED"),
            reviewed_at=data.get("reviewed_at", datetime.datetime.now(datetime.timezone.utc).isoformat()),
            target_sha256=data.get("target_sha256"),
            comments=data.get("comments", ""),
        )


@dataclass
class HumanReviewBlock:
    status: str = "NOT_REVIEWED"  # NOT_REVIEWED, REVIEWED, APPROVED, REJECTED, QUALIFIED
    reviews: List[HumanReviewEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "reviews": [r.to_dict() for r in self.reviews],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HumanReviewBlock":
        if not isinstance(data, dict):
            return cls()
        reviews = [HumanReviewEntry.from_dict(r) for r in data.get("reviews", [])]
        return cls(
            status=data.get("status", "NOT_REVIEWED"),
            reviews=reviews,
        )


@dataclass
class AuthorizationPolicyStatus:
    status: str  # ALLOWED, ALLOWED_WITH_DISCLOSURE, REQUIRES_HUMAN_APPROVAL, PROHIBITED
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"status": self.status}
        if self.reason:
            d["reason"] = self.reason
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthorizationPolicyStatus":
        if isinstance(data, str):
            return cls(status=data)
        return cls(status=data.get("status", "PROHIBITED"), reason=data.get("reason"))


@dataclass
class DerivedValidationSummary:
    state: str = "UNREVIEWED"
    deterministic: Dict[str, Any] = field(default_factory=lambda: {"status": "NOT_RUN"})
    agent_evidence: Dict[str, Any] = field(default_factory=lambda: {"independent_reviewers": 0, "supporting": 0, "disputing": 0, "abstaining": 0})
    computational: Dict[str, Any] = field(default_factory=lambda: {"status": "NOT_RUN"})
    explanation: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state,
            "deterministic": self.deterministic,
            "agent_evidence": self.agent_evidence,
            "computational": self.computational,
            "explanation": self.explanation,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DerivedValidationSummary":
        if not isinstance(data, dict):
            return cls()
        return cls(
            state=data.get("state", "UNREVIEWED"),
            deterministic=data.get("deterministic", {"status": "NOT_RUN"}),
            agent_evidence=data.get("agent_evidence", {"independent_reviewers": 0, "supporting": 0, "disputing": 0, "abstaining": 0}),
            computational=data.get("computational", {"status": "NOT_RUN"}),
            explanation=data.get("explanation", []),
        )


@dataclass
class TargetFile:
    path: str
    sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return {"path": self.path, "sha256": self.sha256}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TargetFile":
        if not isinstance(data, dict):
            return cls(path="", sha256="")
        return cls(path=data.get("path", ""), sha256=data.get("sha256", ""))


@dataclass
class SidecarManifest:
    review_manifest_version: str = MANIFEST_VERSION
    target_file: TargetFile = field(default_factory=lambda: TargetFile("", ""))
    reviews: List[ReviewEvent] = field(default_factory=list)
    claims: List[Claim] = field(default_factory=list)
    challenges: List[Challenge] = field(default_factory=list)
    adjudication: Adjudication = field(default_factory=Adjudication)
    validation: DerivedValidationSummary = field(default_factory=DerivedValidationSummary)
    human_review: HumanReviewBlock = field(default_factory=HumanReviewBlock)
    authorization: Dict[str, AuthorizationPolicyStatus] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "review_manifest_version": self.review_manifest_version,
            "target_file": self.target_file.to_dict(),
            "reviews": [r.to_dict() for r in self.reviews],
            "claims": [c.to_dict() for c in self.claims],
            "challenges": [ch.to_dict() for ch in self.challenges],
            "adjudication": self.adjudication.to_dict(),
            "validation": self.validation.to_dict(),
            "human_review": self.human_review.to_dict(),
            "authorization": {k: v.to_dict() for k, v in self.authorization.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SidecarManifest":
        if not isinstance(data, dict):
            raise ValueError("Manifest data must be a dictionary")

        version = str(data.get("review_manifest_version", "1.0.0"))

        # Check if v1 manifest format
        if version.startswith("1.") or "review_history" in data:
            return migrate_v1_dict_to_v2(data)

        target_file = TargetFile.from_dict(data.get("target_file", {}))
        reviews = [ReviewEvent.from_dict(r) for r in data.get("reviews", [])]
        claims = [Claim.from_dict(c) for c in data.get("claims", [])]
        challenges = [Challenge.from_dict(ch) for ch in data.get("challenges", [])]
        adjudication = Adjudication.from_dict(data.get("adjudication", {}))
        validation = DerivedValidationSummary.from_dict(data.get("validation", {}))
        human_review = HumanReviewBlock.from_dict(data.get("human_review", {}))

        auth_dict: Dict[str, AuthorizationPolicyStatus] = {}
        raw_auth = data.get("authorization", {})
        if isinstance(raw_auth, dict):
            for k, v in raw_auth.items():
                auth_dict[k] = AuthorizationPolicyStatus.from_dict(v)

        return cls(
            review_manifest_version=version,
            target_file=target_file,
            reviews=reviews,
            claims=claims,
            challenges=challenges,
            adjudication=adjudication,
            validation=validation,
            human_review=human_review,
            authorization=auth_dict,
        )


def migrate_v1_dict_to_v2(data: Dict[str, Any]) -> SidecarManifest:
    """Safely converts a v1 manifest dictionary to a typed v2 SidecarManifest.
    Preserves all historical review entries as legacy reviews without fabricating fields.
    """
    target_file = TargetFile.from_dict(data.get("target_file", {}))
    raw_history = data.get("review_history", [])

    v2_reviews: List[ReviewEvent] = []
    human_entries: List[HumanReviewEntry] = []
    human_approved = False

    for item in raw_history:
        rev_id = item.get("review_id", f"rev-{uuid.uuid4()}")
        dt = item.get("reviewed_at", datetime.datetime.now(datetime.timezone.utc).isoformat())
        rev_info = item.get("reviewer", {})
        kind = rev_info.get("kind", "validator")
        identity = ReviewerIdentity.from_dict(rev_info.get("identity", {}))
        scope = item.get("scope", [])
        verdict = item.get("verdict", "PASSED")
        comments = item.get("comments", "")
        findings_data = item.get("findings", [])

        # Map legacy verdicts to valid v2 verdicts if needed
        verdict_map = {
            "PASSED": "PASSED",
            "PASSED_WITH_WARNINGS": "PASSED_WITH_WARNINGS",
            "REVIEWED": "SUPPORTED" if kind == "ai_agent" else "PASSED",
            "NEEDS_REVISION": "NEEDS_REVISION",
            "REJECTED": "REJECTED",
            "APPROVED": "APPROVED",
        }
        v2_verdict = verdict_map.get(verdict, verdict)

        findings = [Finding.from_dict(f) if isinstance(f, dict) else Finding(message=str(f)) for f in findings_data]

        rev_event = ReviewEvent(
            review_id=rev_id,
            reviewed_at=dt,
            reviewer=Reviewer(kind=kind, identity=identity),
            scope=scope,
            verdict=v2_verdict,
            findings=findings,
            comments=comments,
            target_sha256=target_file.sha256,
        )
        v2_reviews.append(rev_event)

        if kind == "human":
            h_entry = HumanReviewEntry(
                review_id=rev_id,
                reviewer=identity,
                scope=scope,
                verdict=v2_verdict,
                reviewed_at=dt,
                target_sha256=target_file.sha256,
                comments=comments,
            )
            human_entries.append(h_entry)
            if v2_verdict == "APPROVED":
                human_approved = True

    human_status = "APPROVED" if human_approved else ("REVIEWED" if human_entries else "NOT_REVIEWED")
    human_block = HumanReviewBlock(status=human_status, reviews=human_entries)

    manifest = SidecarManifest(
        review_manifest_version=MANIFEST_VERSION,
        target_file=target_file,
        reviews=v2_reviews,
        human_review=human_block,
    )
    return manifest


def load_sidecar(sidecar_path: Path) -> SidecarManifest:
    """Loads existing sidecar file or initializes a new v2 structure."""
    if sidecar_path.exists():
        try:
            with open(sidecar_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    return SidecarManifest.from_dict(data)
        except Exception as e:
            print(f"[WARN] Could not parse sidecar {sidecar_path.name}: {e}", file=sys.stderr)

    return SidecarManifest(
        review_manifest_version=MANIFEST_VERSION,
        target_file=TargetFile(path="", sha256=""),
    )


def save_sidecar(sidecar_path: Path, manifest: SidecarManifest) -> None:
    """Saves SidecarManifest to YAML file in clean v2 format."""
    data = manifest.to_dict()
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    with open(sidecar_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)
