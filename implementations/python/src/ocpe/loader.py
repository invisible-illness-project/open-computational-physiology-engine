"""Discovery and loading of OCPE packages into an in-memory :class:`Registry`.

Loading is purely structural: files are parsed and indexed. Use
:func:`ocpe.validator.validate_registry` to check conformance.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Union

import yaml

from . import spec

CURIE_RE = re.compile(
    r"^ocpe:(?P<ns>[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*)*)"
    r"/(?P<local>[a-z0-9]+(?:-[a-z0-9]+)*)(?:#(?P<symbol>[A-Za-z_][A-Za-z0-9_]*))?$"
)

PathLike = Union[str, Path]


def parse_curie(text: str):
    """Return (namespace, local_id, symbol|None) or None if ``text`` is not an OCPE reference."""
    m = CURIE_RE.match(text or "")
    if not m:
        return None
    return m["ns"], m["local"], m["symbol"]


def base_curie(text: str) -> str:
    """Strip a ``#symbol`` fragment."""
    return text.split("#", 1)[0]


# --------------------------------------------------------------------------- issues
@dataclass
class Issue:
    severity: str  # "error" | "warning" | "info"
    code: str
    message: str
    location: str = ""

    def __str__(self) -> str:
        loc = f" [{self.location}]" if self.location else ""
        return f"{self.severity.upper():7s} {self.code}: {self.message}{loc}"

    def to_dict(self) -> Dict[str, str]:
        return {"severity": self.severity, "code": self.code, "message": self.message, "location": self.location}


@dataclass
class Report:
    issues: List[Issue] = field(default_factory=list)

    def add(self, severity: str, code: str, message: str, location: str = "") -> None:
        self.issues.append(Issue(severity, code, message, location))

    def extend(self, other: "Report") -> None:
        self.issues.extend(other.issues)

    @property
    def errors(self) -> List[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[Issue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "issues": [i.to_dict() for i in self.issues],
            "disclaimer": "Structural validation only; it does not establish scientific validity.",
        }


class LoadError(Exception):
    pass


# --------------------------------------------------------------------------- model
@dataclass
class Document:
    path: Path
    data: Dict[str, Any]


@dataclass
class EntityRecord:
    id: str
    kind: str
    package: str
    data: Dict[str, Any]
    source: Path

    @property
    def label(self) -> str:
        return self.data.get("label", self.id)

    @property
    def deprecated(self) -> bool:
        return self.data.get("status") == "deprecated"

    def symbols(self) -> Dict[str, Dict[str, Any]]:
        return {s["symbol"]: s for s in self.data.get("symbols", []) or [] if isinstance(s, dict) and "symbol" in s}


@dataclass
class Package:
    id: str
    version: str
    path: Path
    manifest: Dict[str, Any]
    documents: List[Document] = field(default_factory=list)
    load_issues: Report = field(default_factory=Report)

    @property
    def manifest_path(self) -> Path:
        return self.path / "package.yaml"

    @property
    def dependencies(self) -> List[Dict[str, str]]:
        return list(self.manifest.get("dependencies", []) or [])

    def entities(self) -> Iterator[Dict[str, Any]]:
        for doc in self.documents:
            for ent in doc.data.get("entities", []) or []:
                if isinstance(ent, dict):
                    yield ent


def _read(path: Path) -> Any:
    try:
        return spec.load_yaml(path)
    except (yaml.YAMLError, ValueError) as exc:
        raise LoadError(f"{path}: cannot parse: {exc}") from exc


def _safe_content_path(root: Path, rel: str) -> Path:
    """Resolve a manifest-declared content path inside ``root``.

    Rejects absolute paths, ``..`` traversal outside the package root, and
    symlinks that escape the package root. Package content is data: it must
    live inside the package directory that declares it.
    """
    rel_str = str(rel)
    candidate = Path(rel_str)
    if candidate.is_absolute():
        raise LoadError(f"content path {rel_str!r} must be package-relative, not absolute")
    root_real = root.resolve()
    target = root_real.joinpath(*candidate.parts)
    # Lexical containment (catches '..' even when the target does not exist).
    if target != root_real and root_real not in target.parents:
        raise LoadError(f"content path {rel_str!r} escapes the package root")
    # Symlink containment (catches links that resolve outside the root).
    resolved = target.resolve()
    if resolved != root_real and root_real not in resolved.parents:
        raise LoadError(f"content path {rel_str!r} resolves outside the package root via a symlink")
    return resolved


def load_package(path: PathLike) -> Package:
    """Load a package directory (or its package.yaml)."""
    p = Path(path)
    if p.is_file():
        p = p.parent
    manifest_path = p / "package.yaml"
    if not manifest_path.is_file():
        raise LoadError(f"No package.yaml in {p}")
    manifest = _read(manifest_path)
    if not isinstance(manifest, dict):
        raise LoadError(f"{manifest_path}: manifest must be a mapping")
    pkg = Package(
        id=str(manifest.get("id", "")),
        version=str(manifest.get("version", "")),
        path=p.resolve(),
        manifest=manifest,
    )
    for rel in manifest.get("contents", []) or []:
        try:
            f = _safe_content_path(p, str(rel))
        except LoadError as exc:
            pkg.load_issues.add("error", "path-escape", str(exc), str(manifest_path))
            continue
        if not f.is_file():
            pkg.load_issues.add("error", "content-missing", f"listed content file not found: {rel}", str(manifest_path))
            continue
        try:
            data = _read(f)
        except LoadError as exc:
            pkg.load_issues.add("error", "parse-error", str(exc), str(f))
            continue
        if not isinstance(data, dict):
            pkg.load_issues.add("error", "document-shape", "document must be a mapping", str(f))
            continue
        pkg.documents.append(Document(f, data))
    return pkg


def discover(paths: Iterable[PathLike]) -> List[Path]:
    """Find package directories (containing package.yaml) under the given paths."""
    found: List[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_file() and p.name == "package.yaml":
            found.append(p.parent.resolve())
            continue
        if (p / "package.yaml").is_file():
            found.append(p.resolve())
        if p.is_dir():
            for m in sorted(p.rglob("package.yaml")):
                d = m.parent.resolve()
                if d not in found:
                    found.append(d)
    return found


def default_package_paths() -> List[Path]:
    """OCPE ships no domain content: by default only the core package loads.

    Callers supply the directories of the external domain packages they trust.
    """
    return []


# --------------------------------------------------------------------------- registry
class Registry:
    """Index of loaded packages, entities, references and aliases."""

    def __init__(self) -> None:
        self.packages: Dict[str, Package] = {}
        self.entities: Dict[str, EntityRecord] = {}
        self.references: Dict[str, Dict[str, Any]] = {}
        self.issues = Report()

    # -- construction -------------------------------------------------------
    def add_package(self, pkg: Package) -> None:
        self.issues.extend(pkg.load_issues)
        if pkg.id in self.packages:
            other = self.packages[pkg.id]
            self.issues.add(
                "error", "duplicate-package",
                f"package {pkg.id!r} loaded twice ({other.path} v{other.version} and {pkg.path} v{pkg.version})",
                str(pkg.manifest_path),
            )
            return
        self.packages[pkg.id] = pkg
        for doc in pkg.documents:
            for ent in doc.data.get("entities", []) or []:
                if not isinstance(ent, dict) or "id" not in ent:
                    continue
                eid = str(ent["id"])
                if eid in self.entities:
                    self.issues.add(
                        "error", "duplicate-id",
                        f"identifier {eid} defined more than once (also in {self.entities[eid].source})",
                        str(doc.path),
                    )
                    continue
                self.entities[eid] = EntityRecord(eid, str(ent.get("kind", "")), pkg.id, ent, doc.path)
            for ref in doc.data.get("references", []) or []:
                if isinstance(ref, dict) and "id" in ref:
                    self.references.setdefault(str(ref["id"]), ref)

    # -- queries --------------------------------------------------------------
    def get(self, curie: str) -> Optional[EntityRecord]:
        return self.entities.get(base_curie(curie))

    def by_kind(self, kind: str) -> List[EntityRecord]:
        return [e for e in self.entities.values() if e.kind == kind]

    def predicate_tokens(self) -> Dict[str, EntityRecord]:
        return {e.data.get("token"): e for e in self.by_kind("predicate") if e.data.get("token")}

    def functional_form_tokens(self) -> Dict[str, EntityRecord]:
        return {e.data.get("token"): e for e in self.by_kind("functional_form") if e.data.get("token")}

    def summary(self) -> Dict[str, Any]:
        kinds: Dict[str, int] = {}
        for e in self.entities.values():
            kinds[e.kind] = kinds.get(e.kind, 0) + 1
        return {
            "packages": {p.id: p.version for p in self.packages.values()},
            "entities": len(self.entities),
            "by_kind": dict(sorted(kinds.items())),
            "references": len(self.references),
        }


def load_registry(paths: Optional[Sequence[PathLike]] = None, include_core: bool = True) -> Registry:
    """Discover and load packages.

    With no paths, only the OCPE core vocabulary loads: OCPE ships no domain
    content. Supply the directories of the external packages you trust.
    """
    reg = Registry()
    dirs: List[Path] = []
    if include_core:
        dirs.append(spec.core_package_dir().resolve())
    for d in discover(paths if paths is not None else default_package_paths()):
        if d not in dirs:
            dirs.append(d)
    for d in dirs:
        try:
            reg.add_package(load_package(d))
        except LoadError as exc:
            reg.issues.add("error", "load-error", str(exc), str(d))
    return reg
