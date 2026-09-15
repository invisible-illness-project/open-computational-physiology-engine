"""Build provenance utilities: git rev, KB bundle hash, registry version.

All functions are deterministic given the filesystem state (no wall clock),
supporting the byte-identical-rerun contract.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path
from typing import Optional

import yaml

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def repo_root() -> str:
    return _REPO_ROOT


def git_revision(cwd: Optional[str] = None) -> str:
    """Current OCPE git commit (ocpe_commit). 'unknown' outside a checkout."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=cwd or _REPO_ROOT,
            capture_output=True, text=True, timeout=15)
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def kb_bundle_sha256(kb_dir: str) -> str:
    """SHA-256 of the knowledge-base bundle (kb_version).

    Deterministic digest over every governed file: sorted relative paths +
    file contents, INCLUDING review sidecars (governance state is part of
    the KB version that produced the data).
    """
    h = hashlib.sha256()
    base = Path(kb_dir)
    for root, _, files in os.walk(base):
        for fname in sorted(files):
            if not fname.endswith((".yaml", ".yml", ".md")):
                continue
            fpath = Path(root) / fname
            rel = fpath.relative_to(base).as_posix()
            h.update(rel.encode("utf-8"))
            h.update(b"\0")
            with open(fpath, "rb") as fh:
                while True:
                    chunk = fh.read(65536)
                    if not chunk:
                        break
                    h.update(chunk)
            h.update(b"\0")
    return h.hexdigest()


def registry_version(evidence_package_dir: Optional[str] = None) -> dict:
    """EVIDENCE_REGISTRY.yaml version + SHA-256 (registry_version)."""
    d = evidence_package_dir or os.path.join(
        _REPO_ROOT, "docs", "evidence_package")
    path = os.path.join(d, "EVIDENCE_REGISTRY.yaml")
    out = {"path": os.path.relpath(path, _REPO_ROOT), "version": "unresolved",
           "sha256": "unresolved"}
    try:
        with open(path, "rb") as f:
            blob = f.read()
        out["sha256"] = hashlib.sha256(blob).hexdigest()
        data = yaml.safe_load(blob) or {}
        meta = (data.get("metadata") or data.get("registry_metadata") or {}) \
            if isinstance(data, dict) else {}
        for key in ("version", "registry_version", "schema_version"):
            if isinstance(meta, dict) and meta.get(key):
                out["version"] = str(meta[key])
                break
        else:
            # The registry is content-addressed: report the short sha as the
            # version when no explicit version field exists.
            out["version"] = "sha:" + out["sha256"][:12]
    except OSError:
        pass
    return out


def model_version() -> str:
    """Model/code version: the SCHEMA.md-adjacent repo version is unresolved;
    use the knowledge-base mathematical-models document version + git rev."""
    mm = os.path.join(_REPO_ROOT, "knowledge_base", "equations",
                      "mathematical_models.yaml")
    try:
        with open(mm, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        ver = data.get("version")
        if ver:
            return f"mathematical_models-{ver}"
    except OSError:
        pass
    return "unresolved"
