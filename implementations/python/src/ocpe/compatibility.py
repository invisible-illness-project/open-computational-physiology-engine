"""Version compatibility: dependency satisfaction and change classification between package releases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from . import spec
from .loader import Package, Registry
from .versioning import Version, satisfies

_RANK = {"patch": 0, "minor": 1, "major": 2}


@dataclass
class Change:
    change: str
    severity: str  # major | minor | patch
    id: str
    detail: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {"change": self.change, "severity": self.severity, "id": self.id, "detail": self.detail}


def _classify(change: str) -> str:
    rules = spec.compatibility_rules()["change_classes"]["package"]
    for sev in ("major", "minor", "patch"):
        if change in rules.get(sev, []):
            return sev
    return "patch"


def _entities(pkg: Package) -> Dict[str, Dict[str, Any]]:
    return {str(e["id"]): e for e in pkg.entities() if "id" in e}


def diff_packages(old: Package, new: Package) -> List[Change]:
    """Classify differences between two releases of the same package."""
    changes: List[Change] = []

    def add(kind, eid, detail=""):
        changes.append(Change(kind, _classify(kind), eid, detail))

    a, b = _entities(old), _entities(new)
    for eid in sorted(set(a) - set(b)):
        add("identifier_removed", eid)
    for eid in sorted(set(b) - set(a)):
        add("identifier_added", eid)
    for eid in sorted(set(a) & set(b)):
        x, y = a[eid], b[eid]
        if x.get("kind") != y.get("kind"):
            add("identifier_kind_changed", eid, f"{x.get('kind')} -> {y.get('kind')}")
        if x.get("dimension") != y.get("dimension"):
            add("dimension_changed", eid, f"{x.get('dimension')} -> {y.get('dimension')}")
        if x.get("canonical_unit") != y.get("canonical_unit"):
            add("canonical_unit_changed", eid, f"{x.get('canonical_unit')} -> {y.get('canonical_unit')}")
        if x.get("status") != "deprecated" and y.get("status") == "deprecated":
            add("identifier_deprecated", eid)
        xa = {(al.get("value"), al.get("scope")) for al in x.get("aliases", []) or []}
        ya = {(al.get("value"), al.get("scope")) for al in y.get("aliases", []) or []}
        if ya - xa:
            add("alias_added", eid, ", ".join(str(v) for v, _ in sorted(ya - xa, key=str)))
        if xa - ya:
            add("alias_removed", eid, ", ".join(str(v) for v, _ in sorted(xa - ya, key=str)))
        if len(y.get("evidence", []) or []) > len(x.get("evidence", []) or []):
            add("evidence_added", eid)
        for f in ("label", "definition", "description"):
            if x.get(f) != y.get(f):
                add("label_or_description_changed", eid, f)
                break
    return changes


def required_bump(changes: List[Change]) -> Optional[str]:
    if not changes:
        return None
    return max((c.severity for c in changes), key=_RANK.__getitem__)


def bump_is_sufficient(old_version: str, new_version: str, changes: List[Change]) -> bool:
    """Check the declared version bump against required change severity (pre-1.0: minor is breaking)."""
    need = required_bump(changes)
    o, n = Version.parse(old_version), Version.parse(new_version)
    if need is None:
        return n >= o
    if o.major == 0 and spec.compatibility_rules().get("pre_1_0_policy") == "minor-is-breaking":
        need = {"major": "minor", "minor": "patch", "patch": "patch"}[need]  # 0.y.z: shifted
        if need == "minor":
            return (n.major, n.minor) > (o.major, o.minor)
        return n > o
    if need == "major":
        return n.major > o.major
    if need == "minor":
        return (n.major, n.minor) > (o.major, o.minor)
    return n > o


def dependency_report(reg: Registry) -> List[Dict[str, Any]]:
    """Tabulate every declared dependency with its resolution status."""
    rows = []
    for pkg in reg.packages.values():
        for dep in pkg.dependencies:
            target = reg.packages.get(dep.get("package"))
            ok = bool(target) and satisfies(target.version, dep.get("version", "*"))
            rows.append({
                "package": pkg.id,
                "depends_on": dep.get("package"),
                "constraint": dep.get("version"),
                "loaded": target.version if target else None,
                "satisfied": ok,
            })
    return rows
