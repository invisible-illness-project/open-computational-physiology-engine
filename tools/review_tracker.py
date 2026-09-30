#!/usr/bin/env python3
"""
Sidecar Review Tracker CLI (v2.0.0)
Manages sidecar review manifests (<filename>.<ext>.review.yaml) to trace
reviews, evidence aggregation, scientific challenges, human authorization,
and content hash integrity over time.
"""

import argparse
import datetime
import hashlib
import os
import sys
import uuid
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to Python path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    MANIFEST_VERSION,
    AUTHORIZATION_USES,
    CHALLENGE_STATUSES,
)

# ANSI Color formatting
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_CYAN = "\033[96m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"


def record_review(
    target_path: Path,
    kind: str,
    name: str,
    model_provider: Optional[str] = None,
    model_name: Optional[str] = None,
    model_version: Optional[str] = None,
    agent_role: Optional[str] = None,
    methodology_version: Optional[str] = None,
    system_prompt_sha256: Optional[str] = None,
    independence_group: Optional[str] = None,
    scope: Optional[List[str]] = None,
    findings: Optional[List[Finding]] = None,
    comments: Optional[str] = None,
    verdict: str = "SUPPORTED",
    confidence: float = 1.0,
) -> Path:
    """Records a review entry into the v2 sidecar file of target_path."""
    if not target_path.exists():
        raise FileNotFoundError(f"Target file does not exist: {target_path}")

    current_hash = compute_sha256(target_path)
    sidecar_path = get_sidecar_path(target_path)
    manifest = load_sidecar(sidecar_path)

    # Relative path from workspace root if possible
    try:
        rel_path = str(target_path.relative_to(Path.cwd()))
    except ValueError:
        rel_path = str(target_path)

    manifest.target_file.path = rel_path
    manifest.target_file.sha256 = current_hash

    identity = ReviewerIdentity(
        name=name,
        provider=model_provider,
        model_name=model_name or (name if kind == "ai_agent" else None),
        model_version=model_version,
        agent_role=agent_role,
        methodology_version=methodology_version,
        system_prompt_sha256=system_prompt_sha256,
    )

    reviewer = Reviewer(
        kind=kind,
        identity=identity,
        independence_group=independence_group,
    )

    review_entry = ReviewEvent(
        review_id=f"rev-{uuid.uuid4()}",
        reviewed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        reviewer=reviewer,
        scope=scope or ["general_validation"],
        verdict=verdict,
        confidence=confidence,
        findings=findings or [],
        comments=comments or "",
        target_sha256=current_hash,
    )

    manifest.reviews.append(review_entry)

    if kind == "human":
        human_entry = HumanReviewEntry(
            review_id=review_entry.review_id,
            reviewer=identity,
            scope=scope or ["human_review"],
            verdict=verdict,
            reviewed_at=review_entry.reviewed_at,
            target_sha256=current_hash,
            comments=comments or "",
        )
        manifest.human_review.reviews.append(human_entry)
        if verdict == "APPROVED":
            manifest.human_review.status = "APPROVED"
        elif verdict == "REJECTED":
            manifest.human_review.status = "REJECTED"
        elif manifest.human_review.status == "NOT_REVIEWED":
            manifest.human_review.status = "REVIEWED"

    # Recalculate derived validation state
    aggregate_validation(manifest, target_path)

    save_sidecar(sidecar_path, manifest)
    return sidecar_path


def show_history(target_path: Path) -> None:
    """Displays the detailed review history, claims, challenges, and freshness of target_path."""
    sidecar_path = get_sidecar_path(target_path)
    if not target_path.exists():
        print(f"{COLOR_RED}[ERROR] Target file not found: {target_path}{COLOR_RESET}", file=sys.stderr)
        return

    if not sidecar_path.exists():
        print(f"{COLOR_YELLOW}[INFO] No sidecar review file found for {target_path.name}{COLOR_RESET}")
        return

    current_hash = compute_sha256(target_path)
    manifest = load_sidecar(sidecar_path)
    recorded_hash = manifest.target_file.sha256
    reviews = manifest.reviews

    is_fresh = (current_hash == recorded_hash)
    status_str = f"{COLOR_GREEN}FRESH (SHA-256 matches content){COLOR_RESET}" if is_fresh else f"{COLOR_RED}STALE (Target file modified since last recorded review){COLOR_RESET}"

    # Recalculate summary
    summary = aggregate_validation(manifest, target_path)

    print(f"\n{COLOR_BOLD}=== Review History for: {target_path.name} ==={COLOR_RESET}")
    print(f"Target Path:      {target_path}")
    print(f"Sidecar Path:     {sidecar_path}")
    print(f"Manifest Version: {manifest.review_manifest_version}")
    print(f"Current SHA:      {current_hash[:16]}...")
    print(f"Recorded SHA:     {recorded_hash[:16]}...")
    print(f"Hash Freshness:   {status_str}")
    print(f"Derived State:    {COLOR_BOLD}{summary.state}{COLOR_RESET}")
    print(f"Human Review:     {manifest.human_review.status}")
    print(f"Total Reviews:    {len(reviews)}\n")

    if not reviews:
        print("  No review entries recorded yet.")
    else:
        for idx, entry in enumerate(reviews, 1):
            reviewer = entry.reviewer
            kind = reviewer.kind
            identity = reviewer.identity
            rev_name = identity.name or identity.model_name or "unknown"
            dt = entry.reviewed_at
            scope = ", ".join(entry.scope)
            verdict = entry.verdict
            comments = entry.comments
            findings = entry.findings
            group_str = f" (group: {reviewer.independence_group})" if reviewer.independence_group else ""

            kind_badge = f"[{kind.upper()}]"
            if kind == "human":
                kind_badge = f"{COLOR_CYAN}{kind_badge}{COLOR_RESET}"
            elif kind == "ai_agent":
                kind_badge = f"{COLOR_YELLOW}{kind_badge}{COLOR_RESET}"
            elif kind == "validator":
                kind_badge = f"{COLOR_GREEN}{kind_badge}{COLOR_RESET}"

            print(f"  {idx}. {kind_badge} {COLOR_BOLD}{rev_name}{COLOR_RESET}{group_str} ({dt})")
            print(f"     Verdict:    {verdict} (confidence: {entry.confidence:.2f})")
            print(f"     Scope:      {scope}")
            if identity.provider or identity.model_name:
                print(f"     Model/Prov: {identity.provider or 'N/A'} / {identity.model_name or 'N/A'}")
            if comments:
                print(f"     Comments:   {comments}")
            if findings:
                print(f"     Findings ({len(findings)}):")
                for f_item in findings:
                    print(f"       - [{f_item.severity}] {f_item.path or ''}: {f_item.message}")
            print()

    if manifest.challenges:
        print(f"{COLOR_BOLD}=== Scientific Challenges ({len(manifest.challenges)}) ==={COLOR_RESET}")
        for ch in manifest.challenges:
            status_color = COLOR_GREEN if "RESOLVED" in ch.status else COLOR_RED
            print(f"  - [{ch.challenge_id}] Status: {status_color}{ch.status}{COLOR_RESET} (Severity: {ch.severity})")
            print(f"    Challenger: {ch.challenger.kind} ({ch.challenger.identity.name})")
            print(f"    Statement:  {ch.statement}")
            print()


def show_explain(target_path: Path) -> None:
    """Produces human-readable validation explanation report answering 11 core governance questions."""
    if not target_path.exists():
        print(f"{COLOR_RED}[ERROR] Target file not found: {target_path}{COLOR_RESET}", file=sys.stderr)
        return

    sidecar_path = get_sidecar_path(target_path)
    if not sidecar_path.exists():
        print(f"{COLOR_YELLOW}[INFO] No sidecar manifest exists for {target_path.name}{COLOR_RESET}")
        return

    current_hash = compute_sha256(target_path)
    manifest = load_sidecar(sidecar_path)
    summary = aggregate_validation(manifest, target_path)

    print(f"\n{COLOR_BOLD}===================================================={COLOR_RESET}")
    print(f"{COLOR_BOLD}  OCPE VALIDATION REPORT & PROVENANCE EXPLANATION{COLOR_RESET}")
    print(f"{COLOR_BOLD}===================================================={COLOR_RESET}")
    print(f"Asset Target:      {target_path.name}")
    print(f"Full Path:         {target_path}")
    print(f"Sidecar Manifest:  {sidecar_path.name}\n")

    print(f"{COLOR_BOLD}1. Current Content Hash (SHA-256):{COLOR_RESET}")
    print(f"   {current_hash}")

    print(f"\n{COLOR_BOLD}2. Manifest Freshness:{COLOR_RESET}")
    is_fresh = (current_hash == manifest.target_file.sha256)
    if is_fresh:
        print(f"   {COLOR_GREEN}PASS: Target file SHA-256 matches manifest recorded hash.{COLOR_RESET}")
    else:
        print(f"   {COLOR_RED}STALE: File modified since last manifest recording (Recorded: {manifest.target_file.sha256[:12]}...).{COLOR_RESET}")

    print(f"\n{COLOR_BOLD}3. Deterministic Checks:{COLOR_RESET}")
    det_status = summary.deterministic.get("status", "NOT_RUN")
    det_color = COLOR_GREEN if det_status == "PASSED" else (COLOR_RED if det_status == "FAILED" else COLOR_YELLOW)
    print(f"   Status: {det_color}{det_status}{COLOR_RESET}")

    print(f"\n{COLOR_BOLD}4 & 5. Independent Agent Reviewers & Conclusions:{COLOR_RESET}")
    agent_revs = [r for r in manifest.reviews if r.reviewer.kind == "ai_agent"]
    indep_cnt = summary.agent_evidence.get("independent_reviewers", 0)
    print(f"   Independent Agent Count: {indep_cnt}")
    print(f"   Supporting: {summary.agent_evidence.get('supporting', 0)} | Disputing: {summary.agent_evidence.get('disputing', 0)} | Abstaining: {summary.agent_evidence.get('abstaining', 0)}")
    for r in agent_revs:
        grp = f" (group: {r.reviewer.independence_group})" if r.reviewer.independence_group else ""
        print(f"   - Agent '{r.reviewer.identity.name}'{grp}: verdict={r.verdict}, confidence={r.confidence:.2f}")

    print(f"\n{COLOR_BOLD}6 & 7. Disagreements & Open Scientific Challenges:{COLOR_RESET}")
    open_challenges = [ch for ch in manifest.challenges if ch.status in {"OPEN", "UNDER_INVESTIGATION", "UNRESOLVED"}]
    print(f"   Open Challenges: {len(open_challenges)}")
    for ch in open_challenges:
        print(f"   - [{ch.challenge_id}] [{ch.severity}] {ch.statement} (Status: {ch.status})")

    print(f"\n{COLOR_BOLD}8. Computational Reproduction:{COLOR_RESET}")
    comp_status = summary.computational.get("status", "NOT_RUN")
    comp_color = COLOR_GREEN if comp_status == "PASSED" else (COLOR_RED if comp_status == "FAILED" else COLOR_YELLOW)
    print(f"   Status: {comp_color}{comp_status}{COLOR_RESET}")

    print(f"\n{COLOR_BOLD}9. Human Expert Review:{COLOR_RESET}")
    h_status = manifest.human_review.status
    h_color = COLOR_GREEN if h_status == "APPROVED" else (COLOR_RED if h_status == "REJECTED" else COLOR_YELLOW)
    print(f"   Status: {h_color}{h_status}{COLOR_RESET}")
    for hr in manifest.human_review.reviews:
        print(f"   - {hr.reviewer.name} ({hr.reviewer.role or 'Expert'}): verdict={hr.verdict} at {hr.reviewed_at}")

    print(f"\n{COLOR_BOLD}10 & 11. Downstream Use Authorizations & Governance Explanation:{COLOR_RESET}")
    print(f"   Derived Overall State: {COLOR_BOLD}{summary.state}{COLOR_RESET}\n")

    for use in sorted(AUTHORIZATION_USES):
        status, reason = check_authorization(manifest, use, target_path)
        stat_color = COLOR_GREEN if status == "ALLOWED" else (COLOR_YELLOW if status == "ALLOWED_WITH_DISCLOSURE" else COLOR_RED)
        print(f"   - {use:<25}: {stat_color}{status:<24}{COLOR_RESET} -> {reason}")

    print(f"\n{COLOR_BOLD}Summary Rationale:{COLOR_RESET}")
    for line in summary.explanation:
        print(f"   * {line}")
    print(f"{COLOR_BOLD}===================================================={COLOR_RESET}\n")


def show_summary(dir_path: Path) -> None:
    """Scans directory for YAML/MD assets and displays evidence-layered summary table."""
    if not dir_path.exists():
        print(f"{COLOR_RED}[ERROR] Directory not found: {dir_path}{COLOR_RESET}", file=sys.stderr)
        return

    target_files: List[Path] = []
    for root, _, files in os.walk(dir_path):
        for f in files:
            if (f.endswith(".yaml") or f.endswith(".yml") or f.endswith(".md")) and not f.endswith(".review.yaml"):
                target_files.append(Path(root) / f)

    target_files.sort()

    print(f"\n{COLOR_BOLD}=== Evidence-Layered Review Summary: {dir_path} ==={COLOR_RESET}")
    print(f"Scanning {len(target_files)} target data assets.\n")

    header = f"{'Target Asset':<38} | {'State':<23} | {'Indep. Agents':<12} | {'Human Review':<14} | {'Freshness':<9}"
    print(header)
    print("-" * len(header))

    total_reviewed = 0
    total_stale = 0

    for tf in target_files:
        sidecar = get_sidecar_path(tf)
        try:
            rel_tf = str(tf.relative_to(dir_path))
        except ValueError:
            rel_tf = str(tf)

        if len(rel_tf) > 36:
            rel_tf = "..." + rel_tf[-33:]

        if not sidecar.exists():
            print(f"{rel_tf:<38} | {COLOR_YELLOW}{'UNREVIEWED':<23}{COLOR_RESET} | {'0':<12} | {'NOT_REVIEWED':<14} | {COLOR_YELLOW}{'NO_MANIFEST':<9}{COLOR_RESET}")
            continue

        manifest = load_sidecar(sidecar)
        summary = aggregate_validation(manifest, tf)

        total_reviewed += 1
        indep_agents = summary.agent_evidence.get("independent_reviewers", 0)
        h_status = manifest.human_review.status

        is_fresh = (summary.state != "STALE")
        if not is_fresh:
            total_stale += 1
            fresh_str = f"{COLOR_RED}STALE{COLOR_RESET}"
        else:
            fresh_str = f"{COLOR_GREEN}FRESH{COLOR_RESET}"

        state_color = COLOR_GREEN if summary.state in {"HUMAN_APPROVED", "COMPUTATIONALLY_REPRODUCED", "AGENT_SUPPORTED"} else (COLOR_RED if "DISPUTED" in summary.state or "STALE" in summary.state else COLOR_YELLOW)

        print(f"{rel_tf:<38} | {state_color}{summary.state:<23}{COLOR_RESET} | {indep_agents:<12} | {h_status:<14} | {fresh_str:<9}")

    print("-" * len(header))
    print(f"Summary: {total_reviewed}/{len(target_files)} manifests tracked ({total_stale} stale).\n")


def migrate_cmd(target_path: Path) -> None:
    """Migrates v1 sidecar manifest files to v2 schema."""
    if target_path.is_file():
        files = [target_path]
    else:
        files = list(target_path.glob("**/*.review.yaml"))

    count = 0
    for f in files:
        if f.name.endswith(".review.yaml"):
            try:
                manifest = load_sidecar(f)
                manifest.review_manifest_version = MANIFEST_VERSION
                save_sidecar(f, manifest)
                count += 1
                print(f"{COLOR_GREEN}[MIGRATED]{COLOR_RESET} {f.name} -> manifest version 2.0.0")
            except Exception as e:
                print(f"{COLOR_RED}[ERROR]{COLOR_RESET} Failed to migrate {f.name}: {e}")

    print(f"\nSuccessfully migrated {count} sidecar manifest(s) to v2.0.0.\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sidecar Review Tracker CLI (v2.0.0)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")

    # 'validate' subcommand
    val_p = subparsers.add_parser("validate", help="Validate asset target and manifest consistency")
    val_p.add_argument("target", type=str, help="Target file path")

    # 'record' / 'review' subcommand
    rec_p = subparsers.add_parser("record", help="Record a review entry in sidecar manifest")
    rec_p.add_argument("target", type=str, help="Target file path")
    rec_p.add_argument("--kind", choices=["human", "ai_agent", "validator"], default="human", help="Type of reviewer")
    rec_p.add_argument("--name", required=True, help="Name or identity of reviewer/model")
    rec_p.add_argument("--provider", help="AI Model Provider (e.g. Google Gemini, Anthropic)")
    rec_p.add_argument("--model-name", help="AI Model name")
    rec_p.add_argument("--model-version", help="AI Model version")
    rec_p.add_argument("--agent-role", help="Agent role (e.g. literature_verification)")
    rec_p.add_argument("--methodology-version", help="Methodology version tag")
    rec_p.add_argument("--system-prompt-hash", help="SHA-256 of system prompt")
    rec_p.add_argument("--independence-group", help="Independence group identifier")
    rec_p.add_argument("--scope", default="general", help="Comma-separated review scopes")
    rec_p.add_argument("--comments", default="", help="Review notes/comments")
    rec_p.add_argument("--verdict", default="SUPPORTED", help="Review verdict (PASSED, SUPPORTED, DISPUTED, APPROVED, REJECTED, etc.)")
    rec_p.add_argument("--confidence", type=float, default=1.0, help="Confidence score 0.0 to 1.0")

    # Also add 'review' as alias for record
    rev_p = subparsers.add_parser("review", help="Record a review entry in sidecar manifest (alias for record)")
    rev_p.add_argument("target", type=str, help="Target file path")
    rev_p.add_argument("--kind", choices=["human", "ai_agent", "validator"], default="human", help="Type of reviewer")
    rev_p.add_argument("--name", required=True, help="Name or identity of reviewer/model")
    rev_p.add_argument("--provider", help="AI Model Provider")
    rev_p.add_argument("--model-name", help="AI Model name")
    rev_p.add_argument("--model-version", help="AI Model version")
    rev_p.add_argument("--agent-role", help="Agent role")
    rev_p.add_argument("--methodology-version", help="Methodology version tag")
    rev_p.add_argument("--system-prompt-hash", help="SHA-256 of system prompt")
    rev_p.add_argument("--independence-group", help="Independence group identifier")
    rev_p.add_argument("--scope", default="general", help="Comma-separated review scopes")
    rev_p.add_argument("--comments", default="", help="Review notes/comments")
    rev_p.add_argument("--verdict", default="SUPPORTED", help="Review verdict")
    rev_p.add_argument("--confidence", type=float, default=1.0, help="Confidence score 0.0 to 1.0")

    # 'aggregate' subcommand
    agg_p = subparsers.add_parser("aggregate", help="Recalculate evidence aggregation state")
    agg_p.add_argument("target", type=str, help="Target file path")

    # 'challenge' subcommand
    chal_p = subparsers.add_parser("challenge", help="Create or update a scientific challenge")
    chal_p.add_argument("target", type=str, help="Target file path")
    chal_p.add_argument("--claim", help="Target claim ID")
    chal_p.add_argument("--statement", default="", help="Statement describing the challenge")
    chal_p.add_argument("--type", default="evidence_mismatch", help="Reason type (evidence_mismatch, parameter_out_of_bounds, etc.)")
    chal_p.add_argument("--severity", choices=["CRITICAL", "MINOR"], default="CRITICAL", help="Challenge severity")
    chal_p.add_argument("--status", choices=list(CHALLENGE_STATUSES), default="OPEN", help="Challenge status")
    chal_p.add_argument("--challenge-id", help="Challenge ID if updating an existing challenge")

    # 'authorize' subcommand
    auth_p = subparsers.add_parser("authorize", help="Evaluate downstream authorization policy")
    auth_p.add_argument("target", type=str, help="Target file path")
    auth_p.add_argument("--use", choices=list(AUTHORIZATION_USES), default="iip_production", help="Target downstream use case")

    # 'explain' subcommand
    exp_p = subparsers.add_parser("explain", help="Generate human-readable validation provenance report")
    exp_p.add_argument("target", type=str, help="Target file path")

    # 'history' subcommand
    hist_p = subparsers.add_parser("history", help="Show chronological review history of a file")
    hist_p.add_argument("target", type=str, help="Target file path")

    # 'summary' subcommand
    sum_p = subparsers.add_parser("summary", help="Show summary of review status across directory")
    sum_p.add_argument("directory", type=str, nargs="?", default="knowledge_base", help="Directory path to scan")

    # 'migrate' subcommand
    mig_p = subparsers.add_parser("migrate", help="Migrate v1 manifests to v2 schema")
    mig_p.add_argument("target", type=str, help="Target file or directory path")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "validate":
        target_path = Path(args.target).resolve()
        if not target_path.exists():
            print(f"{COLOR_RED}[ERROR] Target file not found: {target_path}{COLOR_RESET}", file=sys.stderr)
            sys.exit(1)
        sidecar = get_sidecar_path(target_path)
        manifest = load_sidecar(sidecar)
        summary = aggregate_validation(manifest, target_path)
        save_sidecar(sidecar, manifest)
        print(f"{COLOR_GREEN}[VALIDATE]{COLOR_RESET} Asset {target_path.name} state: {COLOR_BOLD}{summary.state}{COLOR_RESET}")

    elif args.command in {"record", "review"}:
        target_path = Path(args.target).resolve()
        scopes = [s.strip() for s in args.scope.split(",") if s.strip()]
        sidecar = record_review(
            target_path=target_path,
            kind=args.kind,
            name=args.name,
            model_provider=args.provider,
            model_name=args.model_name,
            model_version=args.model_version,
            agent_role=args.agent_role,
            methodology_version=args.methodology_version,
            system_prompt_sha256=args.system_prompt_hash,
            independence_group=args.independence_group,
            scope=scopes,
            comments=args.comments,
            verdict=args.verdict,
            confidence=args.confidence,
        )
        print(f"{COLOR_GREEN}[SUCCESS] Recorded {args.kind} review by '{args.name}' into {sidecar.name}{COLOR_RESET}")

    elif args.command == "aggregate":
        target_path = Path(args.target).resolve()
        if not target_path.exists():
            print(f"{COLOR_RED}[ERROR] Target file not found: {target_path}{COLOR_RESET}", file=sys.stderr)
            sys.exit(1)
        sidecar = get_sidecar_path(target_path)
        manifest = load_sidecar(sidecar)
        summary = aggregate_validation(manifest, target_path)
        save_sidecar(sidecar, manifest)
        print(f"{COLOR_GREEN}[AGGREGATED]{COLOR_RESET} {target_path.name} derived state: {COLOR_BOLD}{summary.state}{COLOR_RESET}")
        for exp in summary.explanation:
            print(f"  - {exp}")

    elif args.command == "challenge":
        target_path = Path(args.target).resolve()
        if not target_path.exists():
            print(f"{COLOR_RED}[ERROR] Target file not found: {target_path}{COLOR_RESET}", file=sys.stderr)
            sys.exit(1)
        sidecar = get_sidecar_path(target_path)
        manifest = load_sidecar(sidecar)

        c_id = args.challenge_id or f"challenge-{uuid.uuid4()}"
        existing = next((ch for ch in manifest.challenges if ch.challenge_id == c_id), None)
        if existing:
            existing.status = args.status
            if "RESOLVED" in args.status:
                existing.resolved_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
            print(f"{COLOR_GREEN}[SUCCESS] Updated challenge {c_id} status to {args.status}{COLOR_RESET}")
        else:
            new_ch = Challenge(
                challenge_id=c_id,
                target_claim=args.claim,
                challenger=Reviewer("ai_agent", ReviewerIdentity(name="agent_challenger")),
                reason={"type": args.type},
                statement=args.statement or f"Challenge raised regarding {target_path.name}",
                severity=args.severity,
                status=args.status,
            )
            manifest.challenges.append(new_ch)
            print(f"{COLOR_GREEN}[SUCCESS] Recorded scientific challenge {c_id} against {target_path.name}{COLOR_RESET}")

        aggregate_validation(manifest, target_path)
        save_sidecar(sidecar, manifest)

    elif args.command == "authorize":
        target_path = Path(args.target).resolve()
        if not target_path.exists():
            print(f"{COLOR_RED}[ERROR] Target file not found: {target_path}{COLOR_RESET}", file=sys.stderr)
            sys.exit(1)
        sidecar = get_sidecar_path(target_path)
        manifest = load_sidecar(sidecar)
        use_case = args.use.replace("-", "_")
        status, reason = check_authorization(manifest, use_case, target_path)

        stat_color = COLOR_GREEN if status == "ALLOWED" else (COLOR_YELLOW if status == "ALLOWED_WITH_DISCLOSURE" else COLOR_RED)
        print(f"\nAuthorization Check for Use Case: {COLOR_BOLD}{use_case}{COLOR_RESET}")
        print(f"Target: {target_path.name}")
        print(f"Status: {stat_color}{status}{COLOR_RESET}")
        print(f"Reason: {reason}\n")

    elif args.command == "explain":
        target_path = Path(args.target).resolve()
        show_explain(target_path)

    elif args.command == "history":
        target_path = Path(args.target).resolve()
        show_history(target_path)

    elif args.command == "summary":
        dir_path = Path(args.directory).resolve()
        show_summary(dir_path)

    elif args.command == "migrate":
        target_path = Path(args.target).resolve()
        migrate_cmd(target_path)


if __name__ == "__main__":
    main()
