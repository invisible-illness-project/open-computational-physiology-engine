"""Location and loading of the OCPE specification artifacts (schemas, units, meta).

Resolution order for the specification root:

1. ``OCPE_SPEC_ROOT`` environment variable,
2. the copy bundled inside the installed wheel (``ocpe/_spec``),
3. a ``specification/`` directory found by walking up from this file (source checkout).
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

MARKER = Path("core") / "meta.yaml"


def _is_spec_root(p: Path) -> bool:
    return (p / MARKER).is_file() and (p / "schemas").is_dir()


@lru_cache(maxsize=None)
def spec_root(explicit: Optional[str] = None) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    env = os.environ.get("OCPE_SPEC_ROOT")
    if env:
        candidates.append(Path(env))
    here = Path(__file__).resolve().parent
    candidates.append(here / "_spec")
    for parent in here.parents:
        candidates.append(parent / "specification")
    for c in candidates:
        if _is_spec_root(c):
            return c.resolve()
    raise FileNotFoundError(
        "OCPE specification not found. Set OCPE_SPEC_ROOT to the 'specification/' directory."
    )


def repo_root() -> Optional[Path]:
    """Source-checkout root (parent of specification/), if running from a checkout."""
    root = spec_root().parent
    return root if (root / "specification").is_dir() else None


def load_yaml(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        if path.suffix == ".json":
            return json.load(fh)
        return yaml.safe_load(fh)


@lru_cache(maxsize=None)
def schemas() -> Dict[str, Dict[str, Any]]:
    """All JSON Schemas keyed by their ``$id``."""
    out: Dict[str, Dict[str, Any]] = {}
    for f in sorted((spec_root() / "schemas").rglob("*.schema.json")):
        doc = load_yaml(f)
        out[doc["$id"]] = doc
    return out


def schema(name: str) -> Dict[str, Any]:
    """Look up a schema by file name (e.g. ``'package.schema.json'``) or ``$id``."""
    for sid, doc in schemas().items():
        if sid == name or sid.endswith("/" + name):
            return doc
    raise KeyError(name)


@lru_cache(maxsize=None)
def meta() -> Dict[str, Any]:
    return load_yaml(spec_root() / MARKER)


def spec_version() -> str:
    return str(meta()["ocpe_spec_version"])


@lru_cache(maxsize=None)
def units_registry() -> Dict[str, Any]:
    return load_yaml(spec_root() / "core" / "units.yaml")


@lru_cache(maxsize=None)
def compatibility_rules() -> Dict[str, Any]:
    return load_yaml(spec_root() / "versions" / "compatibility.yaml")


def core_package_dir() -> Path:
    return spec_root() / "core"
