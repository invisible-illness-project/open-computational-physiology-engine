"""Executable conformance vectors for the OCPE semantic engine.

A vector is a language-independent, declarative test case::

    {
      "id": "unit-convert-1",
      "operation": "unit_convert",               # see OPERATIONS
      "input": {"value": 1, "from": "/s", "to": "/min"},
      "expect": {"value": 60.0}                  # subset match against the actual result
    }

The same vectors can drive implementations in any language; ``conformance/test-vectors/``
in the repository holds the official set. ``run_conformance()`` additionally executes
the fixture-based expectations in ``conformance/expected-results/`` (packages,
observations, version diffs), giving a single pass/fail report for an engine.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

from .compatibility import diff_packages, required_bump
from .loader import load_package, load_registry, parse_curie
from .resolver import Resolver
from .units import convert, dimension_of
from .validator import validate_observation, validate_registry
from .versioning import satisfies

PACKAGE_ERROR_CODE = "package-error"


def _approx(a: Any, b: Any) -> bool:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-12)
    return a == b


def _matches(actual: Dict[str, Any], expect: Dict[str, Any]) -> List[str]:
    """Return a list of unmet expectations (subset match)."""
    failures = []
    for key, want in expect.items():
        got = actual.get(key, "<missing>")
        if isinstance(want, dict) and isinstance(got, dict):
            failures.extend(f"{key}.{f}" for f in _matches(got, want))
        elif not _approx(got, want):
            failures.append(f"{key}: expected {want!r}, got {got!r}")
    return failures


# --------------------------------------------------------------------------- operations
def _registry_for(input: Dict[str, Any], base: Path) -> Any:
    pkgs = input.get("packages") or []
    paths = []
    for p in pkgs:
        candidate = base / "fixtures" / "packages" / p
        paths.append(str(candidate if candidate.is_dir() else base / "fixtures" / p))
    return load_registry(paths)


def execute_vector(vector: Dict[str, Any], base: Path) -> Dict[str, Any]:
    """Execute one vector and return the actual result."""
    op = vector["operation"]
    inp = vector.get("input") or {}
    try:
        if op == "parse_identifier":
            return {"valid": parse_curie(inp["identifier"]) is not None}
        if op == "version_satisfies":
            return {"satisfied": satisfies(inp["version"], inp["constraint"])}
        if op == "unit_convert":
            return {"value": convert(float(inp["value"]), inp["from"], inp["to"])}
        if op == "unit_dimension":
            return {"dimension": dimension_of(inp["unit"])}
        if op == "validate_package":
            pkg_dir = base / "fixtures" / "packages" / inp["package"]
            pkg_dir = pkg_dir if pkg_dir.is_dir() else base / "fixtures" / inp["package"]
            paths = [str(pkg_dir)] + [str(base / "fixtures" / "packages" / r) for r in (inp.get("requires") or [])]
            reg = load_registry(paths)
            if not reg.packages:
                return {"ok": False, "errors": [PACKAGE_ERROR_CODE]}
            only = [pid for pid in reg.packages if pid != "core"]
            rep = validate_registry(reg, only)
            return {"ok": rep.ok, "errors": sorted({i.code for i in rep.errors})}
        if op == "validate_observation":
            reg = _registry_for(inp, base)
            rep = validate_observation(inp["record"], reg)
            return {"ok": rep.ok, "errors": sorted({i.code for i in rep.errors})}
        if op == "diff_packages":
            old = load_package(base / "fixtures" / inp["old"])
            new = load_package(base / "fixtures" / inp["new"])
            changes = diff_packages(old, new)
            counts: Dict[str, int] = {}
            for c in changes:
                counts[c.change] = counts.get(c.change, 0) + 1
            return {"changes": counts, "required_bump": required_bump(changes)}
        if op == "resolve":
            reg = _registry_for(inp, base)
            res = Resolver(reg).resolve(inp["term"], scope=inp.get("scope"))
            return {"id": res.id, "matched_by": res.matched_by, "kind": res.entity.kind}
        raise ValueError(f"unknown operation {op!r}")
    except Exception as exc:  # a vector that crashes the engine is a failed vector
        return {"error": f"{type(exc).__name__}: {exc}"}


def run_vectors(path: Path) -> List[Dict[str, Any]]:
    """Execute every vector in a test-vectors file (or directory of files)."""
    files = sorted(path.glob("*.json")) if path.is_dir() else [path]
    results = []
    for f in files:
        doc = json.loads(f.read_text(encoding="utf-8"))
        for vector in doc.get("vectors", []):
            actual = execute_vector(vector, f.parent.parent)
            failures = _matches(actual, vector.get("expect") or {})
            results.append({
                "id": vector["id"],
                "file": str(f),
                "passed": not failures and "error" not in actual,
                "failures": failures + ([actual["error"]] if "error" in actual else []),
                "actual": actual,
            })
    return results


# --------------------------------------------------------------------------- fixture expectations
def _load_expectations(base: Path, name: str) -> Dict[str, Any]:
    f = base / "expected-results" / name
    return json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}


def check_package_fixtures(base: Path) -> List[Dict[str, Any]]:
    results = []
    for rel, expect in sorted(_load_expectations(base, "packages.json").items()):
        pkg_dir = base / "fixtures" / "packages" / rel
        pkg_dir = pkg_dir if pkg_dir.is_dir() else base / "fixtures" / rel
        try:
            paths = [str(pkg_dir)] + [str(base / "fixtures" / "packages" / r) for r in expect.get("requires", [])]
            reg = load_registry(paths)
            only = [pid for pid in reg.packages if pid != "core"]
            rep = validate_registry(reg, only)
            actual = {"ok": rep.ok, "errors": sorted({i.code for i in rep.errors})}
        except Exception as exc:
            actual = {"ok": False, "errors": [f"{type(exc).__name__}: {exc}"]}
        want = {k: v for k, v in expect.items() if k != "requires"}
        results.append({"id": f"package:{rel}", "passed": _matches(actual, want) == [], "failures": _matches(actual, want),
                        "actual": actual})
    return results


def check_observation_fixtures(base: Path) -> List[Dict[str, Any]]:
    import yaml

    results = []
    obs_dir = base / "fixtures" / "observations"
    if not obs_dir.is_dir():
        return results
    expectations = _load_expectations(base, "observations.json")
    for f in sorted(obs_dir.rglob("*.yaml")) + sorted(obs_dir.rglob("*.json")):
        rel = str(f.relative_to(obs_dir)).replace("\\", "/")
        expect = expectations.get(rel)
        if expect is None:
            continue
        record = yaml.safe_load(f.read_text(encoding="utf-8"))
        paths = []
        for p in expect.get("packages", []):
            candidate = base / "fixtures" / "packages" / p
            paths.append(str(candidate if candidate.is_dir() else base / "fixtures" / p))
        reg = load_registry(paths)
        rep = validate_observation(record, reg)
        actual = {"ok": rep.ok, "errors": sorted({i.code for i in rep.errors})}
        want = {k: v for k, v in expect.items() if k != "packages"}
        results.append({"id": f"observation:{rel}", "passed": _matches(actual, want) == [], "failures": _matches(actual, want),
                        "actual": actual})
    return results


def check_version_fixtures(base: Path) -> List[Dict[str, Any]]:
    results = []
    versions = base / "fixtures" / "versions"
    if not versions.is_dir():
        return results
    expectations = _load_expectations(base, "versions.json")
    for rel, expect in sorted(expectations.items()):
        pair = versions / rel
        try:
            changes = diff_packages(load_package(pair / "old"), load_package(pair / "new"))
            counts: Dict[str, int] = {}
            for c in changes:
                counts[c.change] = counts.get(c.change, 0) + 1
            actual = {"changes": counts, "required_bump": required_bump(changes)}
        except Exception as exc:
            actual = {"changes": {"<error>": 1}, "required_bump": f"{type(exc).__name__}: {exc}"}
        results.append({"id": f"versions:{rel}", "passed": _matches(actual, expect) == [], "failures": _matches(actual, expect),
                        "actual": actual})
    return results


def run_conformance(conformance_dir: Path) -> Dict[str, Any]:
    """Run vectors + fixture expectations under ``conformance_dir``; return a report."""
    conformance_dir = Path(conformance_dir)
    results = (
        run_vectors(conformance_dir / "test-vectors")
        + check_package_fixtures(conformance_dir)
        + check_observation_fixtures(conformance_dir)
        + check_version_fixtures(conformance_dir)
    )
    failed = [r for r in results if not r["passed"]]
    return {
        "conformance": str(conformance_dir),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "ok": not failed,
        "failures": [{"id": r["id"], "failures": r["failures"], "actual": r.get("actual")} for r in failed],
    }
