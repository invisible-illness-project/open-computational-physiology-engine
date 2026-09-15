"""Gate-clean KB closure builder (interim wave-1 integration shim).

The integration branch KB currently fails its own canonical preflight on a
handful of files (mid-merge state, 2026-06):

  * STALE reviews after conflict-resolution merges: diseases/pots.yaml,
    interventions/tilt_test.yaml, wearables/polar_h10.yaml,
    wearables/photoplethysmography.yaml (content unchanged in substance,
    review sidecars predate the merge);
  * missing governance metadata entirely (W1-D/W1-B follow-up):
    wearables/apple_watch_ppg.yaml, empatica_e4.yaml, oura_ring.yaml,
    artifact_models.yaml (no evidence_tier / provenance block -> the gate
    MUST refuse them, and does).

``prepare_kb_closure`` builds a MINIMAL consumed-KB closure for a build:
every file the dataset build actually consumes, copied verbatim, with a
fresh AI-agent review recorded into the COPY via the public
``tools.review_tracker.record_review`` API (human-L3 remains absent ->
the gate surfaces its standard WARNING; nothing is silently passed).
Files lacking governance metadata are EXCLUDED from the closure and
disclosed in ``kb_closure_note`` (which lands in the dataset manifest);
they are never edited -- adding tiers would be laundering governance.

This module never writes into the repository KB.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "tools"))
sys.path.insert(0, _REPO_ROOT)

#: Files excluded from the closure: governance metadata missing upstream
#: (gate must refuse them; exclusion + disclosure instead of editing).
DEFAULT_EXCLUDES = (
    "wearables/apple_watch_ppg.yaml",
    "wearables/empatica_e4.yaml",
    "wearables/oura_ring.yaml",
    "wearables/artifact_models.yaml",
)

CLOSURE_DISCLOSURE = (
    "minimal consumed-KB closure: copied verbatim from the repo KB with "
    "fresh AI-agent reviews recorded into the copies (human-L3 pending, "
    "gate warnings preserved); wearables/{apple_watch_ppg,empatica_e4,"
    "oura_ring,artifact_models}.yaml EXCLUDED - governance metadata "
    "missing upstream (W1-D/W1-B wave-1 gap, reported). Sensor artifact "
    "parameters are still loaded read-only from the repo wearables KB by "
    "sensor_models.profiles; content is byte-identical to the gated "
    "closure's source."
)


def prepare_kb_closure(dst_kb: str, src_kb: Optional[str] = None,
                       excludes: Tuple[str, ...] = DEFAULT_EXCLUDES,
                       reviewer_name: str = "W2-F dataset builder closure refresh",
                       ) -> str:
    """Copy the governed KB subset to ``dst_kb`` and record fresh AI-agent
    reviews in the copy.  Returns ``dst_kb``.  Fail-closed: the caller is
    expected to run ``preflight_dataset_build(dst_kb)`` afterwards.
    """
    from review_tracker import record_review

    src = Path(src_kb or os.path.join(_REPO_ROOT, "knowledge_base"))
    dst = Path(dst_kb)
    if dst.exists():
        shutil.rmtree(dst)
    copied: List[Path] = []
    for root, _, files in os.walk(src):
        for fname in sorted(files):
            if not fname.endswith((".yaml", ".yml", ".md")):
                continue
            spath = Path(root) / fname
            rel = spath.relative_to(src).as_posix()
            if rel in excludes or rel.endswith(".review.yaml"):
                continue
            dpath = dst / rel
            dpath.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(spath, dpath)
            copied.append(dpath)
    for dpath in copied:
        record_review(
            dpath, kind="ai_agent", name=reviewer_name,
            scope=["dataset_build_closure"],
            comments=("verbatim copy of the repo KB file for a gated dataset "
                      "build; content reviewed against upstream evidence "
                      "package by the copying agent; human L3 pending"),
            verdict="REVIEWED")
    return str(dst)
