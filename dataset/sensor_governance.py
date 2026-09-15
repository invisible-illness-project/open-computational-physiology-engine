"""Dataset-side per-block canonical_status audit (adversarial review F8).

The provenance gate (validation/provenance_gate.py -- NOT modified here)
checks only *sensor-level* ``canonical_status``.  Several canonical-status
device files nevertheless contain *parameter blocks* marked
``canonical_status: experimental`` (e.g. ``oura_ring.yaml``
``ppg.pulse_ac_amplitude``, E1/provisional; ``artifact_models.yaml``
``dropout.motion_loss_gain``).  A canonical build consuming such a block
silently launders an experimental value into a canonical record.

This module is the dataset-side guard that runs at preflight (called from
``dataset.runner.DatasetBuilder.preflight``; the gate API itself is
untouched):

  * UNREGISTERED experimental block in a consumed KB file -> REFUSE the
    canonical build (fail-closed, ExperimentalPerturbationError).  Registering
    a block requires an explicit, justified entry in
    ``EXPERIMENTAL_BLOCK_REGISTRY`` below.
  * ``neutral_noop`` entries: the block IS consumed by sensor_models, but
    only through a call site with a hard-coded fallback, and the KB value is
    byte-identical to that fallback (verified at audit time) -- excluding
    the block would not change any number.  Allowed with the honesty flag
    ``experimental_block_consumed_as_neutral_noop:*`` on every record.  If
    the KB value ever diverges from the fallback, the audit REFUSES.
  * ``excluded_unless_channels`` entries: the block is only read by sensor
    channels that are NOT part of this build's sensor configuration (e.g.
    ``polar_h10`` ``ecg.*`` blocks when only the ``rr`` channel runs).
    Allowed with the honesty flag
    ``experimental_block_excluded_by_channel_selection:*``.  Configuring a
    consuming channel flips the audit to REFUSE -- this is exactly the
    oura_ring-PPG laundering path from review F8.

Experimental generation mode is untouched (governed by the gate's own
opt-in path); this audit runs only in canonical mode.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from tools.kb_access import CANONICAL
from validation.provenance_gate import ExperimentalPerturbationError

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Registry of known experimental parameter blocks in consumed wearable KB
#: files.  Key: (file_key, dotted_parameter_key) where file_key is the
#: wearable file stem ("polar_h10") or "artifact_models" for the
#: cross-device artifact library.  Every entry carries a justification;
#: ``fallback`` (neutral_noop) is the sensor_models code-level default that
#: the KB value must equal; ``channels`` (excluded_unless_channels) lists
#: the dataset sensor channels that would consume the block.
EXPERIMENTAL_BLOCK_REGISTRY: Dict[Tuple[str, str], Dict[str, Any]] = {
    # --- polar_h10.yaml -------------------------------------------------
    ("polar_h10", "ecg.adc_full_scale_mv"): {
        "kind": "excluded_unless_channels",
        "channels": ["ecg"],
        "justification": ("front-end full-scale range is a modelling choice "
                          "(block's own uncertainty note); read only by "
                          "ChestStrapECGSensor.synthesize_ecg"),
    },
    # --- artifact_models.yaml (cross-device; always consumed) ------------
    ("artifact_models", "dropout.motion_loss_gain"): {
        "kind": "neutral_noop",
        "fallback": 1.0,
        "justification": ("sensor_models/artifacts.py dropout_burst_mask "
                          "reads it with default=1.0; KB value 1.0 is a "
                          "multiplicative no-op"),
    },
    ("artifact_models", "contact_loss.onset_prob_at_exercise_start"): {
        "kind": "neutral_noop",
        "fallback": 0.3,
        "justification": ("sensor_models/artifacts.py contact_loss_mask "
                          "reads it with default=0.3; KB value equals the "
                          "fallback"),
    },
    ("artifact_models", "ectopy.rr_error_widen_factor"): {
        "kind": "neutral_noop",
        "fallback": 2.0,
        "justification": ("sensor_models/devices.py measure_rr ectopy hook "
                          "reads it with default=2.0; KB value equals the "
                          "fallback"),
    },
    ("artifact_models", "motion_ppg.cadence_lock_strength"): {
        "kind": "excluded_unless_channels",
        "channels": ["hr"],
        "justification": ("cadence-lock is only applied in wrist-HR "
                          "derivation (devices.py derive_hr)"),
    },
    ("artifact_models", "motion_ecg.burst_rate_per_s_at_full_intensity"): {
        "kind": "excluded_unless_channels",
        "channels": ["ecg"],
        "justification": ("electrode-motion burst rate only applies to raw "
                          "ECG synthesis"),
    },
    ("artifact_models", "ambient_light.leak_amplitude"): {
        "kind": "excluded_unless_channels",
        "channels": ["ppg"],
        "justification": "ambient-light leakage only applies to PPG synthesis",
    },
    ("artifact_models", "ambient_light.spike_prob_per_s"): {
        "kind": "excluded_unless_channels",
        "channels": ["ppg"],
        "justification": "ambient-light leakage only applies to PPG synthesis",
    },
    ("artifact_models", "temperature_optical.cold_skin_temp_c"): {
        "kind": "excluded_unless_channels",
        "channels": ["ppg"],
        "justification": ("optical temperature derating only applies to PPG "
                          "synthesis"),
    },
    ("artifact_models", "temperature_optical.cold_amplitude_floor"): {
        "kind": "excluded_unless_channels",
        "channels": ["ppg"],
        "justification": ("optical temperature derating only applies to PPG "
                          "synthesis"),
    },
    ("artifact_models", "eda_steps.step_prob_per_s_at_full_intensity"): {
        "kind": "excluded_unless_channels",
        "channels": ["eda"],
        "justification": "EDA motion steps only apply to the EDA channel",
    },
}

FLAG_NEUTRAL_NOOP = "experimental_block_consumed_as_neutral_noop"
FLAG_EXCLUDED = "experimental_block_excluded_by_channel_selection"


def _flatten(node: Any, prefix: str, out: Dict[str, Any]) -> None:
    if isinstance(node, dict):
        if "value" in node or "range" in node:
            out[prefix] = node
        else:
            for k, v in node.items():
                _flatten(v, f"{prefix}.{k}" if prefix else str(k), out)


def _load_blocks(path: Path, root_key: Optional[str]) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    body = data.get(root_key) if root_key else data
    out: Dict[str, Any] = {}
    if isinstance(body, dict):
        _flatten(body, "", out)
    return out


def _experimental_blocks(path: Path, root_key: Optional[str]) -> Dict[str, Any]:
    return {k: v for k, v in _load_blocks(path, root_key).items()
            if isinstance(v, dict)
            and str(v.get("canonical_status", "")).lower() == "experimental"}


def _find_wearable_file(kb_dir: str, stem: str) -> Optional[Path]:
    """Locate a wearable KB file the way the build consumes it: the gated
    kb_dir copy first (closure), then the repository KB (sensor_models
    loads device/artifact parameters read-only from the repo KB)."""
    for base in (Path(kb_dir) / "wearables",
                 Path(_REPO_ROOT) / "knowledge_base" / "wearables"):
        cand = base / f"{stem}.yaml"
        if cand.exists():
            return cand
    return None


def _find_sensor_stem(kb_dir: str, sensor_id: str) -> Optional[str]:
    wear = Path(kb_dir) / "wearables"
    for base in (wear, Path(_REPO_ROOT) / "knowledge_base" / "wearables"):
        if not base.is_dir():
            continue
        for fname in sorted(os.listdir(base)):
            if not (fname.endswith(".yaml")
                    and not fname.endswith(".review.yaml")):
                continue
            with open(base / fname, "r", encoding="utf-8") as f:
                body = (yaml.safe_load(f) or {}).get("sensor", {})
            if body.get("id") == sensor_id:
                return fname[:-len(".yaml")]
    return None


def audit_sensor_experimental_blocks(
        kb_dir: str,
        sensor_configs: List[Dict[str, Any]],
        mode: str = CANONICAL) -> Dict[str, Any]:
    """Audit consumed wearable KB files for experimental parameter blocks.

    Returns a report dict (flags + per-block dispositions).  In canonical
    mode, raises ExperimentalPerturbationError (fail-closed) on any
    unregistered / non-neutral / channel-consumed experimental block.
    """
    report: Dict[str, Any] = {
        "mode": mode,
        "blocks": [],
        "consumed_neutral_noop": [],
        "excluded_by_channel": [],
        "flags": [],
    }
    if mode != CANONICAL:
        report["status"] = "skipped: audit binds canonical mode only"
        return report

    all_channels = sorted({ch for sc in sensor_configs
                           for ch in (sc.get("channels") or ["rr"])})
    # (file_key, path, root_key, channels_whose_build_consumes_this_file)
    targets: List[Tuple[str, Path, Optional[str], List[str]]] = []
    for sc in sensor_configs:
        sid = sc["sensor_id"]
        stem = _find_sensor_stem(kb_dir, sid)
        if stem is None:
            continue  # unknown sensor: the gate already refuses (fail-closed)
        fpath = _find_wearable_file(kb_dir, stem)
        targets.append((stem, fpath, "sensor",
                        list(sc.get("channels") or ["rr"])))
    art = _find_wearable_file(kb_dir, "artifact_models")
    if art is not None:
        targets.append(("artifact_models", art, "artifact_models",
                        all_channels))

    problems: List[str] = []
    for file_key, fpath, root_key, channels in targets:
        for dotted, blk in sorted(_experimental_blocks(fpath, root_key).items()):
            entry = EXPERIMENTAL_BLOCK_REGISTRY.get((file_key, dotted))
            disp: Dict[str, Any] = {"file": file_key, "block": dotted}
            if entry is None:
                problems.append(
                    f"{file_key}.yaml:{dotted}: experimental parameter block "
                    f"is NOT registered in dataset/sensor_governance."
                    f"EXPERIMENTAL_BLOCK_REGISTRY; canonical builds refuse "
                    f"to consume it silently (review F8). Register with a "
                    f"justified neutral_noop / excluded_unless_channels "
                    f"entry or obtain canonical status upstream.")
                disp["disposition"] = "REFUSED (unregistered)"
            elif entry["kind"] == "neutral_noop":
                value = blk.get("value")
                if value is None and "range" in blk:
                    lo, hi = blk["range"]
                    value = 0.5 * (lo + hi)
                if value == entry["fallback"]:
                    flag = f"{FLAG_NEUTRAL_NOOP}:{file_key}:{dotted}"
                    report["consumed_neutral_noop"].append(dotted)
                    report["flags"].append(flag)
                    disp["disposition"] = (
                        f"allowed: consumed but KB value {value} equals the "
                        f"sensor_models code fallback {entry['fallback']} "
                        f"(neutral no-op; flagged)")
                else:
                    problems.append(
                        f"{file_key}.yaml:{dotted}: registered as a neutral "
                        f"no-op with fallback {entry['fallback']} but the KB "
                        f"value is now {value}; the block is load-bearing "
                        f"and experimental -> canonical build refused "
                        f"(review F8)")
                    disp["disposition"] = (
                        f"REFUSED (value {value} != fallback "
                        f"{entry['fallback']})")
            elif entry["kind"] == "excluded_unless_channels":
                consuming = sorted(set(channels) & set(entry["channels"]))
                if consuming:
                    problems.append(
                        f"{file_key}.yaml:{dotted}: experimental parameter "
                        f"block would be CONSUMED by the configured channel "
                        f"(s) {consuming} (registered consuming channels: "
                        f"{entry['channels']}); canonical build refused -- "
                        f"this is the review-F8 laundering path")
                    disp["disposition"] = (
                        f"REFUSED (consumed by channels {consuming})")
                else:
                    flag = f"{FLAG_EXCLUDED}:{file_key}:{dotted}"
                    report["excluded_by_channel"].append(dotted)
                    report["flags"].append(flag)
                    disp["disposition"] = (
                        f"allowed: no configured channel consumes this "
                        f"block (configured: {channels}; consuming: "
                        f"{entry['channels']}); excluded by channel "
                        f"selection, flagged")
            report["blocks"].append(disp)

    if problems:
        raise ExperimentalPerturbationError(
            "canonical dataset build refused: experimental parameter blocks "
            "inside canonical-status wearable KB files (review F8):\n  - "
            + "\n  - ".join(problems))
    report["status"] = ("passed: all experimental blocks registered and "
                        "either neutral no-ops or excluded by channel "
                        "selection (flags recorded)")
    report["flags"] = sorted(set(report["flags"]))
    return report
