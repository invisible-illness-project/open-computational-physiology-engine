"""Version compatibility: dependency satisfaction and change classification between package releases.

``diff_packages`` performs a schema-aware, order-insensitive deep comparison of
two releases of the same package: every entity (including nested model symbols,
equations, evidence attachments, reference ranges and relationship semantics)
and the manifest's dependency declarations are compared field by field. Any
change to a semantically meaningful field yields a classified :class:`Change`;
the classification table lives in ``specification/versions/compatibility.yaml``.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

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
    return "minor"  # conservative default: unknown changes require at least a minor bump


# --------------------------------------------------------------------------- deep diff
def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, default=str)


# List-of-dicts paths compared by an identity key rather than by index.
_LIST_KEYS: Dict[str, Callable[[Any], Optional[str]]] = {
    "/symbols": lambda d: d.get("symbol") if isinstance(d, dict) else None,
    "/equations": lambda d: d.get("id") if isinstance(d, dict) else None,
    "/aliases": lambda d: f"{d.get('value')}@{d.get('scope')}" if isinstance(d, dict) else None,
    "/dependencies": lambda d: d.get("package") if isinstance(d, dict) else None,
    "/optional_dependencies": lambda d: d.get("package") if isinstance(d, dict) else None,
    "/references": lambda d: d.get("id") if isinstance(d, dict) else None,
    "/measures": lambda d: d.get("target") if isinstance(d, dict) else None,
    "/operationalizations": lambda d: d.get("description") if isinstance(d, dict) else None,
    "/specifications": lambda d: d.get("name") if isinstance(d, dict) else None,
}


def _list_key(path: str, item: Any) -> Optional[str]:
    """Identity key for an item of the list at ``path`` (None -> unkeyed list)."""
    fn = _LIST_KEYS.get(path)
    if fn is not None:
        return fn(item)
    if isinstance(item, dict) and "id" in item and isinstance(item["id"], str):
        return item["id"]
    return None


def _diff_values(a: Any, b: Any, path: str, out: List[Tuple[str, str, Any, Any]]) -> None:
    """Append (op, path, old, new) for every semantic difference; op is added | removed | changed."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            sub = f"{path}/{k}"
            if k not in a:
                out.append(("added", sub, None, b[k]))
            elif k not in b:
                out.append(("removed", sub, a[k], None))
            else:
                _diff_values(a[k], b[k], sub, out)
    elif isinstance(a, list) and isinstance(b, list):
        _diff_lists(a, b, path, out)
    elif a != b:
        out.append(("changed", path, a, b))


def _diff_lists(a: list, b: list, path: str, out: List[Tuple[str, str, Any, Any]]) -> None:
    keys_a = [_list_key(path, x) for x in a]
    keys_b = [_list_key(path, x) for x in b]
    if any(k is None for k in keys_a + keys_b):
        # Unkeyed list: pair equal items first (so reorders and untouched items are
        # not changes), then pair the remainder in order; leftovers are added/removed.
        remaining_b: List[Tuple[int, Any]] = []
        used_a: set = set()
        pool: List[Tuple[int, Any]] = []
        for j, y in enumerate(b):
            pool.append((j, y))
        for i, x in enumerate(a):
            for idx, (j, y) in enumerate(pool):
                if _canonical(x) == _canonical(y):
                    used_a.add(i)
                    pool.pop(idx)
                    break
        remaining_a = [(i, x) for i, x in enumerate(a) if i not in used_a]
        pairs = list(zip(remaining_a, pool))
        for (i, x), (j, y) in pairs:
            _diff_values(x, y, f"{path}/{i}", out)
        for i, x in remaining_a[len(pairs):]:
            out.append(("removed", f"{path}/{i}", x, None))
        for j, y in pool[len(pairs):]:
            out.append(("added", f"{path}/{j}", None, y))
        return
    map_a: Dict[str, list] = {}
    map_b: Dict[str, list] = {}
    for k, x in zip(keys_a, a):
        map_a.setdefault(str(k), []).append(x)
    for k, x in zip(keys_b, b):
        map_b.setdefault(str(k), []).append(x)
    for k in sorted(set(map_a) | set(map_b), key=str):
        xs, ys = map_a.get(k, []), map_b.get(k, [])
        for i in range(max(len(xs), len(ys))):
            sub = f"{path}/{k}"
            if i >= len(xs):
                out.append(("added", sub, None, ys[i]))
            elif i >= len(ys):
                out.append(("removed", sub, xs[i], None))
            else:
                _diff_values(xs[i], ys[i], sub, out)


# --------------------------------------------------------------------------- field classification
_MODEL_SEMANTIC = re.compile(r"^/(formalism|scope|assumptions|limitations|validity_domain|implementations|source)(\b|/)")
_RELATIONSHIP_SEMANTIC = re.compile(
    r"^/(subject|predicate|object|functional_form|direction_of_effect|mathematical_specification|confidence)(\b|/)")
_METHOD_SEMANTIC = re.compile(r"^/(method_type|modality|manufacturer|device_model|measures|performance|failure_modes|artifact_handling)(\b|/)")
_TEXT_FIELDS = re.compile(r"^/(label|definition|description)$")
_PATCH_FIELDS = re.compile(r"^/(notes|curation_notes|provenance|since|deprecation)$")


def _classify_field(path: str, op: str, old: Any = None, new: Any = None) -> str:
    """Map a differing field path to a change class (see versions/compatibility.yaml)."""
    if path == "/kind":
        return "identifier_kind_changed"
    if path == "/dimension":
        return "dimension_changed"
    if path == "/canonical_unit":
        return "canonical_unit_changed"
    if path == "/status":
        if new == "deprecated" and op in ("changed", "added"):
            return "identifier_deprecated"
        return "status_changed"
    if path == "/value_type":
        return "value_type_changed"
    if path == "/observability":
        return "observability_changed"
    if _TEXT_FIELDS.match(path):
        return "label_or_description_changed"
    if _PATCH_FIELDS.match(path) or path.startswith("/provenance/") or path.startswith("/curation_notes/"):
        return "curation_note_changed" if path.startswith("/curation") else "metadata_changed"
    if path.startswith("/aliases"):
        if op == "changed":
            return "alias_changed"
        return "alias_added" if op == "added" else "alias_removed"
    if path.startswith("/symbols"):
        # whole-symbol add/remove is depth 2 (/symbols/<key>); deeper paths are symbol internals
        if op == "added":
            return "symbol_added" if path.count("/") == 2 else "symbol_changed"
        if op == "removed":
            return "symbol_removed" if path.count("/") == 2 else "symbol_changed"
        return "symbol_changed"
    if path.startswith("/equations"):
        leaf = path.rsplit("/", 1)[-1]
        if leaf in ("label", "description"):
            return "label_or_description_changed"
        if op == "added":
            return "equation_added" if path.count("/") == 2 else "equation_changed"
        if op == "removed":
            return "equation_removed" if path.count("/") == 2 else "equation_changed"
        return "equation_changed"
    if path.startswith("/evidence") or "/evidence/" in path:
        if op == "added":
            return "evidence_added"
        if op == "removed":
            return "evidence_removed"
        return "evidence_changed"
    if path.startswith("/reference_ranges"):
        if op == "added":
            return "reference_range_added"
        if op == "removed":
            return "evidence_removed"
        return "reference_range_changed"
    if path.startswith("/dependencies"):
        if op == "added":
            return "dependency_added"
        if op == "removed":
            return "dependency_removed"
        leaf = path.rsplit("/", 1)[-1]
        return "metadata_changed" if leaf == "reason" else "dependency_constraint_changed"
    if path.startswith("/optional_dependencies"):
        return "metadata_changed"
    if path == "/ocpe_spec":
        return "spec_constraint_changed"
    if _RELATIONSHIP_SEMANTIC.match(path):
        return "relationship_semantics_changed"
    if _MODEL_SEMANTIC.match(path):
        return "model_semantics_changed"
    if _METHOD_SEMANTIC.match(path):
        return "measurement_semantics_changed"
    if path == "/definition":
        return "definition_removed" if op == "removed" else "label_or_description_changed"
    # Any other field: detected, conservatively classified.
    return "content_changed"


def _summarize(op: str, path: str, old: Any, new: Any) -> str:
    leaf = path.rsplit("/", 1)[-1]
    if op == "changed":
        def short(v: Any) -> str:
            s = repr(v)
            return s if len(s) <= 60 else s[:57] + "..."

        return f"{leaf}: {short(old)} -> {short(new)}"
    if op == "added":
        return f"{leaf} added"
    return f"{leaf} removed"


def _entities(pkg: Package) -> Dict[str, Dict[str, Any]]:
    return {str(e["id"]): e for e in pkg.entities() if "id" in e}


def _entity_changes(eid: str, x: Dict[str, Any], y: Dict[str, Any]) -> List[Change]:
    diffs: List[Tuple[str, str, Any, Any]] = []
    _diff_values(x, y, "", diffs)
    changes: List[Change] = []
    seen = set()
    for op, path, old, new in diffs:
        code = _classify_field(path, op, old, new)
        detail = _summarize(op, path, old, new)
        key = (code, detail)
        if key in seen:
            continue
        seen.add(key)
        changes.append(Change(code, _classify(code), eid, f"{path}: {detail}" if path else detail))
    return changes


def _manifest_changes(old: Package, new: Package) -> List[Change]:
    skip = {"version", "contents", "changelog"}  # release mechanics, not semantics
    a = {k: v for k, v in old.manifest.items() if k not in skip}
    b = {k: v for k, v in new.manifest.items() if k not in skip}
    diffs: List[Tuple[str, str, Any, Any]] = []
    _diff_values(a, b, "", diffs)
    changes: List[Change] = []
    seen = set()
    for op, path, o, n in diffs:
        code = _classify_field(path, op, o, n)
        detail = _summarize(op, path, o, n)
        key = (code, detail)
        if key in seen:
            continue
        seen.add(key)
        target = path.rsplit("/", 1)[-1]
        changes.append(Change(code, _classify(code), f"{new.id} (manifest)",
                              f"{path or target}: {detail}" if path else detail))
    return changes


def diff_packages(old: Package, new: Package) -> List[Change]:
    """Classify differences between two releases of the same package.

    Comparison covers identifiers, every semantically meaningful entity field
    (including nested equations, symbols/parameters, relationships, reference
    ranges, evidence attachments and measurement semantics) and manifest-level
    dependency/specification constraints. Pure reordering of lists is not a
    change; textual label/description/curation edits are patch-level.

    Raises:
        ValueError: if ``old`` and ``new`` have different package ids — such a
            comparison is a category error, not a change set.
    """
    if old.id != new.id:
        raise ValueError(
            f"cannot compare different packages: {old.id!r} vs {new.id!r} "
            f"(diff is defined between releases of the same package)"
        )
    changes: List[Change] = []

    a, b = _entities(old), _entities(new)
    for eid in sorted(set(a) - set(b)):
        changes.append(Change("identifier_removed", _classify("identifier_removed"), eid))
    for eid in sorted(set(b) - set(a)):
        changes.append(Change("identifier_added", _classify("identifier_added"), eid))
    for eid in sorted(set(a) & set(b)):
        changes.extend(_entity_changes(eid, a[eid], b[eid]))
    changes.extend(_manifest_changes(old, new))
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
