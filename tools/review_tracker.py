#!/usr/bin/env python3
"""
Review Tracker Tool (MVP)
Manages sidecar review manifests (<filename>.<ext>.review.yaml) to trace
who (human, AI model, or validator) reviewed what data file over time.
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

MANIFEST_VERSION = "1.0.0"

# ANSI Color formatting
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_CYAN = "\033[96m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"


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


def load_sidecar(sidecar_path: Path) -> Dict[str, Any]:
    """Loads existing sidecar file or initializes a new structure."""
    if sidecar_path.exists():
        try:
            with open(sidecar_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            print(f"{COLOR_YELLOW}[WARN] Could not parse existing sidecar {sidecar_path.name}: {e}{COLOR_RESET}", file=sys.stderr)
    
    return {
        "review_manifest_version": MANIFEST_VERSION,
        "target_file": {
            "path": "",
            "sha256": ""
        },
        "review_history": []
    }


def save_sidecar(sidecar_path: Path, data: Dict[str, Any]) -> None:
    """Saves sidecar dictionary to YAML file."""
    with open(sidecar_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)


def record_review(
    target_path: Path,
    kind: str,
    name: str,
    model_provider: Optional[str] = None,
    system_prompt_sha256: Optional[str] = None,
    scope: Optional[List[str]] = None,
    findings: Optional[List[Dict[str, str]]] = None,
    comments: Optional[str] = None,
    verdict: str = "REVIEWED"
) -> Path:
    """Records a review entry into the sidecar file of target_path."""
    if not target_path.exists():
        raise FileNotFoundError(f"Target file does not exist: {target_path}")

    current_hash = compute_sha256(target_path)
    sidecar_path = get_sidecar_path(target_path)
    manifest = load_sidecar(sidecar_path)

    # Determine relative path from workspace root if possible
    try:
        rel_path = str(target_path.relative_to(Path.cwd()))
    except ValueError:
        rel_path = str(target_path)

    manifest["target_file"]["path"] = rel_path
    manifest["target_file"]["sha256"] = current_hash

    # Construct identity block
    identity: Dict[str, Any] = {"name": name}
    if kind == "ai_agent":
        if model_provider:
            identity["provider"] = model_provider
        identity["model_name"] = name
        if system_prompt_sha256:
            identity["system_prompt_sha256"] = system_prompt_sha256
    elif kind == "human":
        identity["name"] = name
    elif kind == "validator":
        identity["name"] = name

    review_entry: Dict[str, Any] = {
        "review_id": f"rev-{uuid.uuid4()}",
        "reviewed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "reviewer": {
            "kind": kind,
            "identity": identity
        },
        "scope": scope or ["general_validation"],
        "verdict": verdict,
        "findings": findings or [],
        "comments": comments or ""
    }

    if "review_history" not in manifest or not isinstance(manifest["review_history"], list):
        manifest["review_history"] = []

    manifest["review_history"].append(review_entry)
    save_sidecar(sidecar_path, manifest)
    return sidecar_path


def show_history(target_path: Path) -> None:
    """Displays the chronological review history of target_path."""
    sidecar_path = get_sidecar_path(target_path)
    if not target_path.exists():
        print(f"{COLOR_RED}[ERROR] Target file not found: {target_path}{COLOR_RESET}", file=sys.stderr)
        return

    if not sidecar_path.exists():
        print(f"{COLOR_YELLOW}[INFO] No sidecar review file found for {target_path.name}{COLOR_RESET}")
        return

    current_hash = compute_sha256(target_path)
    manifest = load_sidecar(sidecar_path)
    recorded_hash = manifest.get("target_file", {}).get("sha256", "")
    history = manifest.get("review_history", [])

    is_fresh = (current_hash == recorded_hash)
    status_str = f"{COLOR_GREEN}FRESH (SHA-256 matches content){COLOR_RESET}" if is_fresh else f"{COLOR_RED}STALE (Target file modified since last recorded review){COLOR_RESET}"

    print(f"\n{COLOR_BOLD}=== Review History for: {target_path.name} ==={COLOR_RESET}")
    print(f"Target Path:    {target_path}")
    print(f"Sidecar Path:   {sidecar_path}")
    print(f"Current SHA:    {current_hash[:16]}...")
    print(f"Recorded SHA:   {recorded_hash[:16]}...")
    print(f"Hash Freshness: {status_str}")
    print(f"Total Reviews:  {len(history)}\n")

    if not history:
        print("  No review entries recorded yet.")
        return

    for idx, entry in enumerate(history, 1):
        reviewer = entry.get("reviewer", {})
        kind = reviewer.get("kind", "unknown")
        identity = reviewer.get("identity", {})
        rev_name = identity.get("name") or identity.get("model_name", "unknown")
        dt = entry.get("reviewed_at", "unknown date")
        scope = ", ".join(entry.get("scope", []))
        verdict = entry.get("verdict", "REVIEWED")
        comments = entry.get("comments", "")
        findings = entry.get("findings", [])

        kind_badge = f"[{kind.upper()}]"
        if kind == "human":
            kind_badge = f"{COLOR_CYAN}{kind_badge}{COLOR_RESET}"
        elif kind == "ai_agent":
            kind_badge = f"{COLOR_YELLOW}{kind_badge}{COLOR_RESET}"
        elif kind == "validator":
            kind_badge = f"{COLOR_GREEN}{kind_badge}{COLOR_RESET}"

        print(f"  {idx}. {kind_badge} {COLOR_BOLD}{rev_name}{COLOR_RESET} ({dt})")
        print(f"     Verdict:  {verdict}")
        print(f"     Scope:    {scope}")
        if comments:
            print(f"     Comments: {comments}")
        if findings:
            print(f"     Findings ({len(findings)}):")
            for f_item in findings:
                sev = f_item.get("severity", "INFO")
                msg = f_item.get("message", "")
                f_path = f_item.get("path", "")
                print(f"       - [{sev}] {f_path}: {msg}")
        print()


def show_summary(dir_path: Path) -> None:
    """Scans directory for YAML/MD files and displays review status summary table."""
    if not dir_path.exists():
        print(f"{COLOR_RED}[ERROR] Directory not found: {dir_path}{COLOR_RESET}", file=sys.stderr)
        return

    target_files: List[Path] = []
    for root, _, files in os.walk(dir_path):
        for f in files:
            # Look for source files (skip .review.yaml files)
            if (f.endswith(".yaml") or f.endswith(".yml") or f.endswith(".md")) and not f.endswith(".review.yaml"):
                target_files.append(Path(root) / f)

    target_files.sort()

    print(f"\n{COLOR_BOLD}=== Review Summary for: {dir_path} ==={COLOR_RESET}")
    print(f"Found {len(target_files)} target data files.\n")

    header = f"{'Target File':<40} | {'Reviews':<7} | {'Latest Reviewer':<25} | {'Freshness':<10}"
    print(header)
    print("-" * len(header))

    total_reviewed = 0
    total_stale = 0

    for tf in target_files:
        sidecar = get_sidecar_path(tf)
        rel_tf = str(tf.relative_to(dir_path)) if tf.is_relative_to(dir_path) else str(tf)
        if len(rel_tf) > 38:
            rel_tf = "..." + rel_tf[-35:]

        if not sidecar.exists():
            print(f"{rel_tf:<40} | {'0':<7} | {'None':<25} | {COLOR_YELLOW}{'UNREVIEWED':<10}{COLOR_RESET}")
            continue

        manifest = load_sidecar(sidecar)
        history = manifest.get("review_history", [])
        recorded_hash = manifest.get("target_file", {}).get("sha256", "")
        current_hash = compute_sha256(tf)
        is_fresh = (current_hash == recorded_hash)

        review_count = len(history)
        if review_count > 0:
            total_reviewed += 1
            latest_entry = history[-1]
            reviewer = latest_entry.get("reviewer", {})
            kind = reviewer.get("kind", "")
            identity = reviewer.get("identity", {})
            rname = identity.get("name") or identity.get("model_name", "unknown")
            rev_str = f"[{kind[:3].upper()}] {rname}"
            if len(rev_str) > 24:
                rev_str = rev_str[:21] + "..."
        else:
            rev_str = "None"

        if not is_fresh:
            total_stale += 1
            fresh_str = f"{COLOR_RED}STALE{COLOR_RESET}"
        else:
            fresh_str = f"{COLOR_GREEN}FRESH{COLOR_RESET}"

        print(f"{rel_tf:<40} | {review_count:<7} | {rev_str:<25} | {fresh_str:<10}")

    print("-" * len(header))
    print(f"Summary: {total_reviewed}/{len(target_files)} files reviewed ({total_stale} stale).\n")


def main():
    parser = argparse.ArgumentParser(
        description="Sidecar Review Tracker CLI (MVP)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")

    # 'record' subcommand
    record_parser = subparsers.add_parser("record", help="Record a review entry in sidecar file")
    record_parser.add_argument("target", type=str, help="Target file path")
    record_parser.add_argument("--kind", choices=["human", "ai_agent", "validator"], default="human", help="Type of reviewer")
    record_parser.add_argument("--name", required=True, help="Name or identity of reviewer/model")
    record_parser.add_argument("--model-provider", help="AI Model Provider (e.g. Google Gemini, Anthropic)")
    record_parser.add_argument("--system-prompt-hash", help="SHA-256 of system prompt for AI review")
    record_parser.add_argument("--scope", default="general", help="Comma-separated review scopes")
    record_parser.add_argument("--comments", default="", help="Review notes/comments")
    record_parser.add_argument("--verdict", default="REVIEWED", help="Review verdict")

    # 'history' subcommand
    history_parser = subparsers.add_parser("history", help="Show chronological review history of a file")
    history_parser.add_argument("target", type=str, help="Target file path")

    # 'summary' subcommand
    summary_parser = subparsers.add_parser("summary", help="Show summary of review status across directory")
    summary_parser.add_argument("directory", type=str, nargs="?", default="knowledge_base", help="Directory path to scan")

    args = parser.parse_args()

    if args.command == "record":
        target_path = Path(args.target).resolve()
        scopes = [s.strip() for s in args.scope.split(",") if s.strip()]
        sidecar = record_review(
            target_path=target_path,
            kind=args.kind,
            name=args.name,
            model_provider=args.model_provider,
            system_prompt_sha256=args.system_prompt_hash,
            scope=scopes,
            comments=args.comments,
            verdict=args.verdict
        )
        print(f"{COLOR_GREEN}[SUCCESS] Recorded {args.kind} review by '{args.name}' into {sidecar.name}{COLOR_RESET}")

    elif args.command == "history":
        target_path = Path(args.target).resolve()
        show_history(target_path)

    elif args.command == "summary":
        dir_path = Path(args.directory).resolve()
        show_summary(dir_path)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
