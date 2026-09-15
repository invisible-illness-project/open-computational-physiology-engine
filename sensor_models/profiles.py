"""Knowledge-base-driven wearable device profiles.

Loads device/artifact parameter blocks from ``knowledge_base/wearables/*.yaml``
so that no scientific constant is hardcoded in sensor code (SWARM_SPEC global
rule 6). Every parameter block in the KB YAML carries:

``value`` (or ``range``), ``units``, ``distribution``, ``evidence_tier``,
``source`` (registry ``claim_id`` and/or ``doi``/``pmid``/dossier section),
``canonical_status`` and ``provisional``.

The loader resolves the KB directory relative to the repository root so it
works from any installed location, and exposes a small accessor API that
flattens the nested YAML into dotted keys (e.g. ``ecg.sampling_frequency_hz``).
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml


def _kb_wearables_dir() -> Path:
    """Locate knowledge_base/wearables relative to this file's repo root."""
    here = Path(os.path.abspath(__file__))
    # sensor_models/profiles.py -> repo root is parent of sensor_models/
    return here.parent.parent / "knowledge_base" / "wearables"


class ProfileError(RuntimeError):
    pass


def _flatten(node, prefix, out):
    if isinstance(node, dict):
        if "value" in node or "range" in node:
            out[prefix] = node
        else:
            for k, v in node.items():
                _flatten(v, f"{prefix}.{k}" if prefix else str(k), out)
    else:
        out[prefix] = node


class DeviceProfile:
    """A loaded wearable device profile with provenance-carrying parameters."""

    def __init__(self, sensor_id: str, raw: dict):
        self.sensor_id = sensor_id
        self.raw = raw
        self._flat: dict = {}
        _flatten(raw.get("sensor", {}), "", self._flat)

    def block(self, dotted_key: str) -> dict:
        """Return the raw parameter block (with provenance) for a key."""
        try:
            return self._flat[dotted_key]
        except KeyError:
            raise ProfileError(
                f"profile '{self.sensor_id}' has no parameter '{dotted_key}'. "
                f"Available: {sorted(self._flat)}"
            )

    def value(self, dotted_key: str, default=None):
        """Return the numeric/scalar value of a parameter block.

        For range-only blocks returns the range midpoint unless ``default``
        is supplied.
        """
        if dotted_key not in self._flat:
            if default is not None:
                return default
            raise ProfileError(
                f"profile '{self.sensor_id}' has no parameter '{dotted_key}'"
            )
        blk = self._flat[dotted_key]
        if blk is None:
            return default  # explicit null in YAML (e.g. unpublished quantity)
        if isinstance(blk, dict):
            if "value" in blk:
                return blk["value"]
            if "range" in blk:
                lo, hi = blk["range"]
                return 0.5 * (lo + hi)
        return blk

    def range(self, dotted_key: str):
        """Return (low, high) for a range block (value±tolerance if scalar)."""
        blk = self.block(dotted_key)
        if isinstance(blk, dict) and "range" in blk:
            return tuple(blk["range"])
        v = self.value(dotted_key)
        return (v, v)

    def provenance(self, dotted_key: str) -> dict:
        """Return evidence provenance (claim_id/doi/pmid/tier) for a key."""
        blk = self.block(dotted_key)
        if isinstance(blk, dict):
            return {
                "evidence_tier": blk.get("evidence_tier"),
                "source": blk.get("source"),
                "canonical_status": blk.get("canonical_status"),
                "provisional": blk.get("provisional", False),
                "uncertainty": blk.get("uncertainty"),
            }
        return {}


_PROFILE_CACHE: dict[str, "DeviceProfile"] = {}


def load_device_profile(sensor_id: str, *, kb_dir: os.PathLike | None = None,
                        use_cache: bool = True) -> DeviceProfile:
    """Load a device profile by sensor id from knowledge_base/wearables.

    Searches every data YAML in the wearables KB directory for
    ``sensor.id == sensor_id``.
    """
    if use_cache and sensor_id in _PROFILE_CACHE:
        return _PROFILE_CACHE[sensor_id]
    directory = Path(kb_dir) if kb_dir else _kb_wearables_dir()
    if not directory.is_dir():
        raise ProfileError(f"wearables KB directory not found: {directory}")
    for fname in sorted(os.listdir(directory)):
        if not (fname.endswith(".yaml") and not fname.endswith(".review.yaml")):
            continue
        with open(directory / fname, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not isinstance(data, dict):
            continue
        if data.get("sensor", {}).get("id") == sensor_id:
            profile = DeviceProfile(sensor_id, data)
            if use_cache:
                _PROFILE_CACHE[sensor_id] = profile
            return profile
    raise ProfileError(f"no wearable KB profile with sensor.id '{sensor_id}' in {directory}")


def load_artifact_models(*, kb_dir: os.PathLike | None = None) -> dict:
    """Load the cross-device state-dependent artifact model parameters."""
    directory = Path(kb_dir) if kb_dir else _kb_wearables_dir()
    path = directory / "artifact_models.yaml"
    if not path.is_file():
        raise ProfileError(f"artifact model KB file not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data["artifact_models"]


def artifact_value(models: dict, dotted_key: str, default=None):
    """Fetch a scalar from the artifact-models mapping (midpoint of ranges)."""
    node = models
    for part in dotted_key.split("."):
        if not isinstance(node, dict) or part not in node:
            if default is not None:
                return default
            raise ProfileError(f"artifact_models has no parameter '{dotted_key}'")
        node = node[part]
    if isinstance(node, dict):
        if "value" in node:
            return node["value"]
        if "range" in node:
            lo, hi = node["range"]
            return 0.5 * (lo + hi)
    return node
