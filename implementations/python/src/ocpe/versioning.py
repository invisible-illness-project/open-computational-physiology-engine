"""Semantic versions and version constraints (no third-party dependency).

Constraint grammar (see ``common.schema.json#/definitions/version_constraint``)::

    constraint := alternative ( '||' alternative )*
    alternative := '*' | comparator+          (comparators are AND-ed)
    comparator := op? version                 op in >=, >, <=, <, =, ^, ~

``^1.2.3`` := >=1.2.3 <2.0.0 ; ``^0.2.3`` := >=0.2.3 <0.3.0 ; ``~1.2.3`` := >=1.2.3 <1.3.0.
A bare version means ``=``. Partial versions (``1.2``) are padded with zeros.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import total_ordering
from typing import List, Tuple

_SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$"
)
_COMP = re.compile(r"(>=|<=|>|<|=|\^|~)?\s*(\d+(?:\.\d+){0,2}(?:-[0-9A-Za-z.-]+)?)")


@total_ordering
@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int
    pre: Tuple = ()

    @classmethod
    def parse(cls, text: str) -> "Version":
        text = str(text).strip()
        m = _SEMVER.match(text)
        if not m:
            core, _, pre = text.partition("-")
            parts = core.split(".")
            if not (1 <= len(parts) <= 3) or not all(p.isdigit() for p in parts):
                raise ValueError(f"Invalid version: {text!r}")
            parts += ["0"] * (3 - len(parts))
            return cls(int(parts[0]), int(parts[1]), int(parts[2]), cls._pre(pre) if pre else ())
        return cls(int(m[1]), int(m[2]), int(m[3]), cls._pre(m[4]) if m[4] else ())

    @staticmethod
    def _pre(s: str) -> Tuple:
        return tuple((0, int(x)) if x.isdigit() else (1, x) for x in s.split("."))

    def _key(self):
        # A pre-release sorts before the corresponding release.
        return (self.major, self.minor, self.patch, 0 if self.pre else 1, self.pre)

    def __lt__(self, other: "Version") -> bool:
        return self._key() < other._key()

    def __str__(self) -> str:
        s = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre:
            s += "-" + ".".join(str(v) for _, v in self.pre)
        return s


def _expand(op: str, v: Version) -> List[Tuple[str, Version]]:
    if op == "^":
        if v.major > 0:
            upper = Version(v.major + 1, 0, 0)
        elif v.minor > 0:
            upper = Version(0, v.minor + 1, 0)
        else:
            upper = Version(0, 0, v.patch + 1)
        return [(">=", v), ("<", upper)]
    if op == "~":
        return [(">=", v), ("<", Version(v.major, v.minor + 1, 0))]
    return [(op or "=", v)]


def _cmp(op: str, a: Version, b: Version) -> bool:
    return {
        ">=": a >= b, ">": a > b, "<=": a <= b, "<": a < b, "=": a == b,
    }[op]


def parse_constraint(text: str) -> List[List[Tuple[str, Version]]]:
    alternatives = []
    for alt in str(text).split("||"):
        alt = alt.strip()
        if alt in ("", "*"):
            alternatives.append([])
            continue
        comps: List[Tuple[str, Version]] = []
        pos = 0
        for m in _COMP.finditer(alt):
            if alt[pos:m.start()].strip():
                raise ValueError(f"Invalid constraint: {text!r}")
            comps.extend(_expand(m[1] or "=", Version.parse(m[2])))
            pos = m.end()
        if alt[pos:].strip() or not comps:
            raise ValueError(f"Invalid constraint: {text!r}")
        alternatives.append(comps)
    return alternatives


def satisfies(version: str, constraint: str) -> bool:
    v = Version.parse(version)
    for alt in parse_constraint(constraint):
        if all(_cmp(op, v, b) for op, b in alt):
            # Pre-releases only match if the constraint mentions the same core version.
            if v.pre and not any(b.pre and (b.major, b.minor, b.patch) == (v.major, v.minor, v.patch) for _, b in alt):
                continue
            return True
    return False
