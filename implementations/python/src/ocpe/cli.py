"""``ocpe`` command-line interface.

Core commands never touch governance data. Governance commands live under the
optional ``ocpe governance`` sub-command.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__, spec, units
from .compatibility import bump_is_sufficient, dependency_report, diff_packages, required_bump
from .loader import load_package, load_registry
from .resolver import AmbiguousReference, ResolutionError, Resolver
from .validator import validate_instance, validate_observation, validate_registry


def _emit(obj, as_json: bool, text: str = "") -> None:
    if as_json:
        print(json.dumps(obj, indent=2, default=str))
    elif text:
        print(text)


def _registry(args):
    paths = args.paths or None
    return load_registry(paths)


def cmd_validate(args) -> int:
    reg = _registry(args)
    only = None
    if args.paths:
        # Only report on packages that live under the given paths (dependencies still load).
        roots = [Path(p).resolve() for p in args.paths]
        only = [pid for pid, p in reg.packages.items() if any(r == p.path or r in p.path.parents for r in roots)]
    rep = validate_registry(reg, only)
    if not args.show_info:
        rep.issues = [i for i in rep.issues if i.severity != "info"]
    if args.json:
        out = rep.to_dict()
        out["packages"] = {pid: reg.packages[pid].version for pid in (only or reg.packages)}
        _emit(out, True)
    else:
        for i in rep.issues:
            print(i)
        pk = ", ".join(f"{pid}@{reg.packages[pid].version}" for pid in sorted(only or reg.packages))
        status = "OK" if rep.ok else "FAILED"
        print(f"\n{status}: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s) across {pk}")
        print("Note: structural validation only; it does not establish scientific validity.")
    return 0 if rep.ok and not (args.strict and rep.warnings) else 1


def cmd_resolve(args) -> int:
    reg = _registry(args)
    res = Resolver(reg)
    rc = 0
    out = []
    for term in args.terms:
        try:
            r = res.resolve(term, scope=args.scope)
            d = r.to_dict()
            if args.full:
                d["entity"] = r.entity.data
            out.append(d)
            if not args.json:
                extra = f" [unit {r.unit}]" if r.unit else ""
                print(f"{term} -> {r.id} ({r.entity.kind}: {r.entity.label}) via {r.matched_by}{extra}")
        except AmbiguousReference as exc:
            rc = 2
            out.append({"term": term, "error": "ambiguous", "candidates": [c.to_dict() for c in exc.candidates]})
            if not args.json:
                print(f"{term}: {exc}", file=sys.stderr)
        except ResolutionError as exc:
            rc = 1
            out.append({"term": term, "error": str(exc)})
            if not args.json:
                print(f"{term}: {exc}", file=sys.stderr)
    _emit(out, args.json)
    return rc


def cmd_search(args) -> int:
    reg = _registry(args)
    hits = Resolver(reg).search(args.text, limit=args.limit)
    if args.json:
        _emit([{"id": e.id, "kind": e.kind, "label": e.label} for e in hits], True)
    else:
        for e in hits:
            print(f"{e.id:60s} {e.kind:20s} {e.label}")
    return 0


def cmd_show(args) -> int:
    reg = _registry(args)
    try:
        r = Resolver(reg).resolve(args.term, scope=args.scope)
    except ResolutionError as exc:
        print(exc, file=sys.stderr)
        return 1
    related = [e.data for e in Resolver(reg).related(r.id)]
    data = {"resolution": r.to_dict(), "entity": r.entity.data, "relationships": related}
    if args.json:
        _emit(data, True)
    else:
        import yaml
        print(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    return 0


def cmd_list(args) -> int:
    reg = _registry(args)
    if args.what == "packages":
        rows = [{"id": p.id, "version": p.version, "name": p.manifest.get("name"), "path": str(p.path)} for p in reg.packages.values()]
        if args.json:
            _emit(rows, True)
        else:
            for r in sorted(rows, key=lambda r: r["id"]):
                print(f"{r['id']:32s} {r['version']:10s} {r['name']}")
    else:
        ents = [e for e in reg.entities.values() if args.kind in (None, e.kind) and args.package in (None, e.package)]
        if args.json:
            _emit([{"id": e.id, "kind": e.kind, "label": e.label} for e in ents], True)
        else:
            for e in sorted(ents, key=lambda e: e.id):
                print(f"{e.id:60s} {e.kind:20s} {e.label}")
    return 0


def cmd_deps(args) -> int:
    reg = _registry(args)
    rows = dependency_report(reg)
    if args.json:
        _emit(rows, True)
    else:
        for r in rows:
            flag = "ok " if r["satisfied"] else "BAD"
            print(f"[{flag}] {r['package']} -> {r['depends_on']} {r['constraint']} (loaded: {r['loaded']})")
    return 0 if all(r["satisfied"] for r in rows) else 1


def cmd_diff(args) -> int:
    old, new = load_package(args.old), load_package(args.new)
    if old.id != new.id:
        print(f"warning: comparing different packages {old.id} vs {new.id}", file=sys.stderr)
    changes = diff_packages(old, new)
    need = required_bump(changes)
    ok = bump_is_sufficient(old.version, new.version, changes)
    data = {"old": old.version, "new": new.version, "required_bump": need, "declared_bump_sufficient": ok,
            "changes": [c.to_dict() for c in changes]}
    if args.json:
        _emit(data, True)
    else:
        for c in changes:
            print(f"{c.severity:5s} {c.change:30s} {c.id} {c.detail}")
        print(f"\n{old.id}: {old.version} -> {new.version}; required bump: {need}; declared bump sufficient: {ok}")
    return 0 if ok else 1


def cmd_units(args) -> int:
    if args.units_cmd == "convert":
        try:
            src, dst = units.normalize(args.from_unit), units.normalize(args.to_unit)
            v = units.convert(args.value, src, dst)
        except units.UnitError as exc:
            print(exc, file=sys.stderr)
            return 1
        _emit({"value": v, "unit": dst}, args.json, f"{args.value} {src} = {v:g} {dst}")
    elif args.units_cmd == "normalize":
        try:
            code = units.normalize(args.unit)
        except units.UnitError as exc:
            print(exc, file=sys.stderr)
            return 1
        info = units.info(code)
        _emit({"code": code, "dimension": info.dimension, "label": info.label}, args.json,
              f"{args.unit!r} -> {code} ({info.dimension}; {info.label})")
    else:
        reg = spec.units_registry()["units"]
        if args.json:
            _emit(reg, True)
        else:
            for code, d in reg.items():
                print(f"{code:14s} {d['dimension']:22s} {d.get('label', '')}")
    return 0


def cmd_check_observation(args) -> int:
    data = spec.load_yaml(Path(args.file))
    records = data if isinstance(data, list) else [data]
    reg = _registry(args)
    rc = 0
    for i, rec in enumerate(records):
        rep = validate_observation(rec, reg)
        for issue in rep.issues:
            print(f"record {i}: {issue}")
        rc |= 0 if rep.ok else 1
    if rc == 0:
        print(f"{len(records)} observation record(s) valid")
    return rc


def cmd_export(args) -> int:
    """Export the loaded registry as a single JSON bundle (for agents and non-Python tools)."""
    reg = _registry(args)
    bundle = {
        "ocpe_spec": spec.spec_version(),
        "packages": {p.id: {"version": p.version, "manifest": p.manifest} for p in reg.packages.values()},
        "entities": [e.data for e in sorted(reg.entities.values(), key=lambda e: e.id)],
        "references": list(reg.references.values()),
        "disclaimer": "Structural content only; inclusion does not imply scientific validation.",
    }
    text = json.dumps(bundle, indent=2, default=str)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
        print(f"wrote {args.output} ({len(bundle['entities'])} entities)")
    else:
        print(text)
    return 0


def cmd_info(args) -> int:
    reg = _registry(args)
    data = {"engine_version": __version__, "ocpe_spec": spec.spec_version(), "spec_root": str(spec.spec_root()),
            **reg.summary()}
    _emit(data, args.json, "\n".join(f"{k}: {v}" for k, v in data.items()))
    return 0


def cmd_conformance(args) -> int:
    """Run the official OCPE conformance suite (vectors + fixtures) against this engine."""
    from .vectors import run_conformance

    if args.dir:
        d = Path(args.dir)
    else:
        root = spec.repo_root()
        d = (root / "conformance") if root else Path("conformance")
    if not d.is_dir():
        print(f"conformance directory not found: {d} (supply its path)", file=sys.stderr)
        return 1
    report = run_conformance(d)
    if args.json:
        _emit(report, True)
    else:
        for f in report["failures"]:
            print(f"FAIL {f['id']}: {'; '.join(f['failures'])} (actual: {f['actual']})")
        print(f"conformance: {report['passed']} passed, {report['failed']} failed "
              f"({report['conformance']})")
    return 0 if report["ok"] else 1


def cmd_governance(argv: List[str]) -> int:
    from .governance import tracker

    try:
        tracker.main(argv)
    except SystemExit as exc:  # argparse / tracker exits
        return int(exc.code or 0)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ocpe", description="Open Computational Physiology Engine - specification and semantic interoperability tools")
    p.add_argument("--version", action="version", version=f"ocpe {__version__} (spec {spec.spec_version()})")
    sub = p.add_subparsers(dest="command")

    def common(sp, paths=True):
        if paths:
            sp.add_argument("paths", nargs="*", help="package directories (default: only the OCPE core vocabulary; supply the external packages you trust)")
        sp.add_argument("--json", action="store_true", help="machine-readable output")
        return sp

    v = common(sub.add_parser("validate", help="validate packages (schema + semantic)"))
    v.add_argument("--strict", action="store_true", help="treat warnings as failures")
    v.add_argument("--show-info", action="store_true")
    v.set_defaults(func=cmd_validate)

    r = sub.add_parser("resolve", help="resolve identifiers, symbols, aliases or labels")
    r.add_argument("terms", nargs="+")
    r.add_argument("--scope", help="alias scope (a package id or a model CURIE)")
    r.add_argument("--full", action="store_true", help="include full entity record (with --json)")
    r.add_argument("--path", dest="paths", action="append", help="package directory (repeatable)")
    r.add_argument("--json", action="store_true")
    r.set_defaults(func=cmd_resolve)

    s = sub.add_parser("search", help="full-text search")
    s.add_argument("text")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--path", dest="paths", action="append")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_search)

    sh = sub.add_parser("show", help="show an entity with its relationships")
    sh.add_argument("term")
    sh.add_argument("--scope")
    sh.add_argument("--path", dest="paths", action="append")
    sh.add_argument("--json", action="store_true")
    sh.set_defaults(func=cmd_show)

    ls = sub.add_parser("list", help="list packages or entities")
    ls.add_argument("what", choices=["packages", "entities"])
    ls.add_argument("--kind")
    ls.add_argument("--package")
    ls.add_argument("--path", dest="paths", action="append")
    ls.add_argument("--json", action="store_true")
    ls.set_defaults(func=cmd_list)

    d = common(sub.add_parser("deps", help="check declared package dependencies"))
    d.set_defaults(func=cmd_deps)

    df = sub.add_parser("diff", help="classify changes between two releases of a package")
    df.add_argument("old")
    df.add_argument("new")
    df.add_argument("--json", action="store_true")
    df.set_defaults(func=cmd_diff)

    u = sub.add_parser("units", help="unit registry tools")
    usub = u.add_subparsers(dest="units_cmd")
    uc = usub.add_parser("convert")
    uc.add_argument("value", type=float)
    uc.add_argument("from_unit")
    uc.add_argument("to_unit")
    un = usub.add_parser("normalize")
    un.add_argument("unit")
    usub.add_parser("list")
    u.add_argument("--json", action="store_true")
    u.set_defaults(func=cmd_units)

    o = sub.add_parser("check-observation", help="validate observation exchange records (YAML/JSON)")
    o.add_argument("file")
    o.add_argument("--path", dest="paths", action="append")
    o.set_defaults(func=cmd_check_observation)

    e = sub.add_parser("export", help="export loaded packages as one JSON bundle")
    e.add_argument("-o", "--output")
    e.add_argument("--path", dest="paths", action="append")
    e.set_defaults(func=cmd_export)

    i = common(sub.add_parser("info", help="engine/spec/registry summary"))
    i.set_defaults(func=cmd_info)

    c = sub.add_parser("conformance", help="run the OCPE conformance suite (vectors + fixtures)")
    c.add_argument("dir", nargs="?", help="conformance directory (default: ./conformance or the checkout's conformance/)")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_conformance)

    sub.add_parser("governance", help="OPTIONAL review-manifest tools (record, aggregate, challenge, authorize, explain, history, summary, migrate)", add_help=False)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "governance":
        return cmd_governance(argv[1:])
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    if args.command == "units" and not args.units_cmd:
        args.units_cmd = "list"
    return int(args.func(args) or 0)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
