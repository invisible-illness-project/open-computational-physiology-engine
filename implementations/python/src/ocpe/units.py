"""Unit normalisation and dimensional consistency, driven by specification/core/units.yaml.

This is intentionally a *registry* lookup, not a UCUM parser: every unit used by
OCPE content must be registered, which keeps unit semantics explicit and reviewable.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Optional

from . import spec


class UnitError(ValueError):
    pass


@dataclass(frozen=True)
class UnitInfo:
    code: str
    dimension: str
    to_reference: float
    label: str


@lru_cache(maxsize=None)
def _tables():
    reg = spec.units_registry()
    units: Dict[str, UnitInfo] = {}
    legacy: Dict[str, str] = {}
    for code, d in reg["units"].items():
        units[code] = UnitInfo(code, d["dimension"], float(d["to_reference"]), d.get("label", code))
        for alt in d.get("legacy", []) or []:
            legacy[str(alt)] = code
    return units, legacy, reg["dimensions"]


def dimensions() -> Dict[str, dict]:
    return _tables()[2]


def is_known(code: str) -> bool:
    return code in _tables()[0]


def info(code: str) -> UnitInfo:
    units, _, _ = _tables()
    if code not in units:
        raise UnitError(f"Unit {code!r} is not registered in specification/core/units.yaml")
    return units[code]


def normalize(code: str) -> str:
    """Map a registered code or a legacy spelling (e.g. 'mmHg', 'bpm') to its UCUM code."""
    units, legacy, _ = _tables()
    code = "" if code is None else str(code).strip()
    if code in units:
        return code
    if code in legacy:
        return legacy[code]
    raise UnitError(f"Unknown unit {code!r}")


def dimension_of(code: str) -> str:
    return info(code).dimension


def compatible(a: str, b: str) -> bool:
    return dimension_of(a) == dimension_of(b)


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert a value between units of the same dimension (multiplicative units only)."""
    fa, fb = info(from_unit), info(to_unit)
    if fa.dimension != fb.dimension:
        raise UnitError(f"Cannot convert {from_unit!r} ({fa.dimension}) to {to_unit!r} ({fb.dimension})")
    if fa.dimension == "temperature" and from_unit != to_unit:
        raise UnitError("Temperature conversion with offsets is not supported")
    return value * fa.to_reference / fb.to_reference


def check(code: str, expected_dimension: Optional[str] = None) -> Optional[str]:
    """Return an error message, or None if ``code`` is registered (and of the expected dimension)."""
    if not is_known(code):
        hint = ""
        try:
            hint = f" (did you mean {normalize(code)!r}?)"
        except UnitError:
            pass
        return f"unit {code!r} is not a registered UCUM code{hint}"
    if expected_dimension and dimension_of(code) != expected_dimension:
        return f"unit {code!r} has dimension {dimension_of(code)!r}, expected {expected_dimension!r}"
    return None
