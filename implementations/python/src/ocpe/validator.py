"""Structural and semantic validation of OCPE packages.

Layers:

1. **Schema** - manifests and documents against the JSON Schemas (authoritative contract).
2. **Semantic** - identifier namespaces and uniqueness, dependency declarations and
   versions, reference integrity (including model symbols), units and dimensions,
   predicate/functional-form vocabulary, alias collisions, ranges, deprecation.

Passing validation means content is well-formed, consistent and resolvable. It does
**not** mean the content is scientifically valid.
"""

from __future__ import annotations

import warnings
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

import jsonschema

from . import spec, units
from .loader import (
    EntityRecord,
    Package,
    PathLike,
    Registry,
    Report,
    base_curie,
    load_registry,
    parse_curie,
)
from .versioning import Version, satisfies

QUANTITY_KINDS = {"variable", "latent_construct", "derived_metric"}
UNIT_KEYS = {"unit", "canonical_unit"}


# --------------------------------------------------------------------------- schema layer
def _validator_for(schema_name: str):
    schema = spec.schema(schema_name)
    store = spec.schemas()
    try:  # jsonschema >= 4.18
        from referencing import Registry as RefRegistry, Resource
        from referencing.jsonschema import DRAFT7

        reg = RefRegistry().with_resources(
            [(sid, Resource(contents=doc, specification=DRAFT7)) for sid, doc in store.items()]
        )
        try:
            return jsonschema.Draft7Validator(schema, registry=reg)
        except TypeError:  # 'referencing' present but jsonschema too old for registry=
            pass
    except ImportError:  # older jsonschema without referencing
        pass
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        resolver = jsonschema.RefResolver(base_uri=schema["$id"], referrer=schema, store=store)
    return jsonschema.Draft7Validator(schema, resolver=resolver)


_CACHE: Dict[str, Any] = {}


def schema_validator(schema_name: str):
    if schema_name not in _CACHE:
        _CACHE[schema_name] = _validator_for(schema_name)
    return _CACHE[schema_name]


def _best(errors) -> List[jsonschema.ValidationError]:
    """Flatten if/then/allOf error trees to their most specific leaves."""
    out = []
    for e in errors:
        if e.context:
            out.extend(_best(e.context))
        else:
            out.append(e)
    return out


def schema_errors(instance: Any, schema_name: str) -> List[Tuple[str, str]]:
    """Return [(json-path, message)] for ``instance`` against the named schema."""
    v = schema_validator(schema_name)
    seen, out = set(), []
    for err in _best(v.iter_errors(instance)):
        path = "/".join(str(p) for p in err.absolute_path)
        key = (path, err.message)
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def validate_instance(instance: Any, schema_name: str, location: str = "") -> Report:
    rep = Report()
    for path, msg in schema_errors(instance, schema_name):
        rep.add("error", "schema", msg if len(msg) < 400 else msg[:400] + "...", f"{location}#/{path}")
    return rep


# --------------------------------------------------------------------------- helpers
def _walk(obj: Any, path: str = "") -> Iterator[Tuple[str, Any, Any]]:
    """Yield (path, key, value) for every scalar in a nested structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}/{k}"
            if isinstance(v, (dict, list)):
                yield from _walk(v, p)
            else:
                yield p, k, v
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f"{path}/{i}"
            if isinstance(v, (dict, list)):
                yield from _walk(v, p)
            else:
                yield p, None, v


def _allowed_namespaces(pkg: Package) -> Dict[str, Optional[str]]:
    allowed: Dict[str, Optional[str]] = {pkg.id: None, "core": None}
    for dep in pkg.dependencies + list(pkg.manifest.get("optional_dependencies", []) or []):
        if isinstance(dep, dict) and dep.get("package"):
            allowed[dep["package"]] = dep.get("version")
    return allowed


# --------------------------------------------------------------------------- semantic layer
def _check_package_meta(pkg: Package, reg: Registry, rep: Report) -> None:
    loc = str(pkg.manifest_path)
    rep.extend(validate_instance(pkg.manifest, "package.schema.json", loc))
    cur = spec.spec_version()
    constraint = pkg.manifest.get("ocpe_spec")
    if constraint:
        try:
            if not satisfies(cur, constraint):
                rep.add("error", "spec-incompatible", f"package requires OCPE spec {constraint!r}; engine provides {cur}", loc)
        except ValueError as exc:
            rep.add("error", "bad-constraint", str(exc), loc)
    if pkg.manifest.get("changelog") and not (pkg.path / pkg.manifest["changelog"]).exists():
        rep.add("warning", "changelog-missing", f"changelog {pkg.manifest['changelog']!r} not found", loc)
    for dep in pkg.dependencies:
        if not isinstance(dep, dict):
            continue
        name, constraint = dep.get("package"), dep.get("version", "*")
        if name == pkg.id:
            rep.add("error", "self-dependency", "package depends on itself", loc)
            continue
        target = reg.packages.get(name)
        if target is None:
            rep.add("error", "dependency-missing", f"dependency {name!r} ({constraint}) is not loaded", loc)
            continue
        try:
            if not satisfies(target.version, constraint):
                rep.add("error", "dependency-version", f"dependency {name!r} requires {constraint!r}; loaded {target.version}", loc)
        except ValueError as exc:
            rep.add("error", "bad-constraint", str(exc), loc)
    marker = spec.compatibility_rules()["releases"][0]["document_marker"]
    readable = set()
    for r in spec.compatibility_rules()["releases"]:
        if r["version"] == cur:
            readable = set(r.get("reads_documents", [marker]))
    for doc in pkg.documents:
        dloc = str(doc.path)
        rep.extend(validate_instance(doc.data, "document.schema.json", dloc))
        if doc.data.get("package") != pkg.id:
            rep.add("error", "document-package", f"document declares package {doc.data.get('package')!r}, manifest is {pkg.id!r}", dloc)
        if str(doc.data.get("ocpe")) not in readable:
            rep.add("error", "document-version", f"document written for OCPE {doc.data.get('ocpe')!r}; engine reads {sorted(readable)}", dloc)


def _check_entity(ent: EntityRecord, pkg: Package, reg: Registry, rep: Report) -> None:
    loc = f"{ent.source}::{ent.id}"
    d = ent.data
    parsed = parse_curie(ent.id)
    if parsed and parsed[0] != pkg.id:
        rep.add("error", "namespace", f"{ent.id} is in namespace {parsed[0]!r} but defined by package {pkg.id!r}", loc)
    if parsed and parsed[2]:
        rep.add("error", "id-fragment", "entity ids must not contain '#symbol' fragments", loc)

    allowed = _allowed_namespaces(pkg)
    symbols = ent.symbols() if ent.kind == "model" else {}

    # References anywhere in the entity
    for path, key, val in _walk(d):
        if not isinstance(val, str) or not val.startswith("ocpe:") or path == "/id":
            continue
        pr = parse_curie(val)
        if not pr:
            rep.add("error", "bad-reference", f"malformed OCPE reference {val!r}", f"{loc}{path}")
            continue
        ns, _local, sym = pr
        if ns not in allowed:
            rep.add("error", "undeclared-dependency", f"{val} references package {ns!r}, which is not a declared dependency of {pkg.id!r}", f"{loc}{path}")
            continue
        target = reg.get(val)
        if target is None:
            sev = "error" if ns in reg.packages else "warning"
            rep.add(sev, "unresolved-reference", f"{val} does not resolve", f"{loc}{path}")
            continue
        if sym is not None:
            if target.kind != "model":
                rep.add("error", "symbol-on-non-model", f"{val}: '#symbol' fragments are only valid on model identifiers", f"{loc}{path}")
            elif sym not in target.symbols():
                rep.add("error", "unknown-symbol", f"{val}: symbol {sym!r} not declared by {base_curie(val)}", f"{loc}{path}")
        if target.deprecated:
            rep.add("warning", "deprecated-reference", f"{val} is deprecated", f"{loc}{path}")

    # Units
    for path, key, val in _walk(d):
        if key in UNIT_KEYS and isinstance(val, str):
            msg = units.check(val)
            if msg:
                rep.add("error", "unit", msg, f"{loc}{path}")
        elif path.split("/")[-2:-1] == ["accepted_units"] and isinstance(val, str):
            msg = units.check(val)
            if msg:
                rep.add("error", "unit", msg, f"{loc}{path}")

    if ent.kind in QUANTITY_KINDS:
        dim = d.get("dimension")
        if dim and dim not in units.dimensions():
            rep.add("error", "dimension", f"unknown dimension {dim!r}", loc)
        cu = d.get("canonical_unit")
        if dim and cu and units.is_known(cu) and units.dimension_of(cu) != dim:
            rep.add("error", "dimension-mismatch", f"canonical_unit {cu!r} has dimension {units.dimension_of(cu)!r}, entity declares {dim!r}", loc)
        for u in d.get("accepted_units", []) or []:
            if dim and units.is_known(u) and units.dimension_of(u) != dim:
                rep.add("error", "dimension-mismatch", f"accepted unit {u!r} is not of dimension {dim!r}", loc)
        for i, rr in enumerate(d.get("reference_ranges", []) or []):
            u = rr.get("unit")
            if dim and u and units.is_known(u) and units.dimension_of(u) != dim:
                rep.add("error", "dimension-mismatch", f"reference range unit {u!r} is not of dimension {dim!r}", f"{loc}/reference_ranges/{i}")
        for a in d.get("aliases", []) or []:
            u = a.get("unit") if isinstance(a, dict) else None
            if dim and u and units.is_known(u) and units.dimension_of(u) != dim:
                rep.add("error", "dimension-mismatch", f"alias {a.get('value')!r} unit {u!r} is not of dimension {dim!r}", loc)

    _check_ranges(d, loc, rep)

    if ent.kind == "model":
        declared = set(symbols)
        for sym, sd in symbols.items():
            rep_target = sd.get("represents")
            target = reg.get(rep_target) if rep_target else None
            if target is not None and sd.get("unit") and target.data.get("dimension") and units.is_known(sd["unit"]):
                if units.dimension_of(sd["unit"]) != target.data["dimension"]:
                    rep.add("error", "dimension-mismatch",
                            f"symbol {sym!r} unit {sd['unit']!r} ({units.dimension_of(sd['unit'])}) does not match "
                            f"{rep_target} dimension {target.data['dimension']!r}", loc)
        seen = set()
        for s in d.get("symbols", []) or []:
            if isinstance(s, dict):
                if s.get("symbol") in seen:
                    rep.add("error", "duplicate-symbol", f"symbol {s.get('symbol')!r} declared twice", loc)
                seen.add(s.get("symbol"))
        for eq in d.get("equations", []) or []:
            for field in ("inputs", "parameters", "outputs"):
                for s in eq.get(field, []) or []:
                    if s not in declared:
                        rep.add("error", "undeclared-symbol", f"equation {eq.get('id')!r} {field} uses undeclared symbol {s!r}", loc)

    if ent.kind == "relationship":
        pred = d.get("predicate", "")
        tokens = reg.predicate_tokens()
        pred_ent = tokens.get(pred) or (reg.get(pred) if pred.startswith("ocpe:") else None)
        if pred_ent is None:
            rep.add("error", "unknown-predicate", f"predicate {pred!r} is not in the core vocabulary", loc)
        else:
            obj = reg.get(str(d.get("object", "")))
            okinds = pred_ent.data.get("object_kinds")
            if okinds and obj is not None and obj.kind not in okinds:
                rep.add("warning", "predicate-range", f"{pred} expects object of kind {okinds}; got {obj.kind}", loc)
        ff = d.get("functional_form")
        if ff and ff not in reg.functional_form_tokens() and reg.get(ff) is None:
            rep.add("error", "unknown-functional-form", f"functional form {ff!r} is not registered", loc)

    if d.get("status") == "deprecated" and not d.get("deprecation"):
        rep.add("error", "deprecation", "status 'deprecated' requires a deprecation block", loc)
    since = d.get("since")
    if since:
        try:
            if Version.parse(since) > Version.parse(pkg.version):
                rep.add("error", "since", f"'since' {since} is later than package version {pkg.version}", loc)
        except ValueError:
            pass

    _check_evidence_integrity(ent, reg, rep)


def _check_ranges(d: Dict[str, Any], loc: str, rep: Report) -> None:
    def visit(o, path):
        if isinstance(o, dict):
            if isinstance(o.get("min"), (int, float)) and isinstance(o.get("max"), (int, float)) and o["min"] > o["max"]:
                rep.add("error", "range", f"min {o['min']} > max {o['max']}", f"{loc}{path}")
            for k, v in o.items():
                visit(v, f"{path}/{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                visit(v, f"{path}/{i}")
    visit(d, "")


def _check_evidence_integrity(ent: EntityRecord, reg: Registry, rep: Report) -> None:
    """Every reference cited by an evidence claim must be a registered bibliographic record.

    Syntactically valid ``doi:``/``pmid:``/... strings are not proof that the record
    exists: packages declare their records in document-level ``references:`` lists,
    and claims may only cite declared ids. Structural integrity, not scientific validity.
    """

    def visit(node: Any, path: str) -> None:
        if isinstance(node, dict):
            ev = node.get("evidence")
            if isinstance(ev, list):
                for i, claim in enumerate(ev):
                    if not isinstance(claim, dict):
                        continue
                    for ref in claim.get("references", []) or []:
                        if str(ref) not in reg.references:
                            rep.add(
                                "error", "unresolved-evidence-reference",
                                f"evidence claim cites {ref!r}, which no loaded package declares in a 'references:' list",
                                f"{ent.source}::{ent.id}{path}/evidence/{i}",
                            )
            for k, v in node.items():
                if k != "evidence":
                    visit(v, f"{path}/{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                visit(v, f"{path}/{i}")

    visit(ent.data, "")


def _check_aliases(reg: Registry, rep: Report) -> None:
    index: Dict[Tuple[str, Optional[str]], List[str]] = {}
    for ent in reg.entities.values():
        for a in ent.data.get("aliases", []) or []:
            if isinstance(a, dict) and a.get("value"):
                index.setdefault((a["value"], a.get("scope")), []).append(ent.id)
    for (value, scope), ids in index.items():
        distinct = sorted(set(ids))
        if len(distinct) > 1:
            rep.add("error", "alias-collision", f"alias {value!r} (scope={scope}) maps to several entities: {distinct}")


def _check_dependency_cycles(reg: Registry, rep: Report) -> None:
    graph = {pid: [d.get("package") for d in p.dependencies if isinstance(d, dict)] for pid, p in reg.packages.items()}
    state: Dict[str, int] = {}

    def dfs(n, stack):
        state[n] = 1
        for m in graph.get(n, []):
            if m not in graph:
                continue
            if state.get(m) == 1:
                rep.add("error", "dependency-cycle", " -> ".join(stack + [n, m]))
            elif not state.get(m):
                dfs(m, stack + [n])
        state[n] = 2

    for n in graph:
        if not state.get(n):
            dfs(n, [])


def validate_registry(reg: Registry, packages: Optional[Iterable[str]] = None) -> Report:
    """Validate loaded packages (all, or only those whose ids are given)."""
    rep = Report()
    rep.extend(reg.issues)
    wanted = set(packages) if packages is not None else set(reg.packages)
    for pid in sorted(wanted):
        pkg = reg.packages.get(pid)
        if pkg is None:
            rep.add("error", "package-missing", f"package {pid!r} not loaded")
            continue
        _check_package_meta(pkg, reg, rep)
        for ent in reg.entities.values():
            if ent.package == pid:
                _check_entity(ent, pkg, reg, rep)
    _check_aliases(reg, rep)
    _check_dependency_cycles(reg, rep)
    return rep


def validate_paths(paths: Optional[Sequence[PathLike]] = None) -> Tuple[Registry, Report]:
    reg = load_registry(paths)
    return reg, validate_registry(reg)


MEASURABLE_OBSERVABILITY = {"directly_measurable", "indirectly_measurable", "invasive_only"}
_VALUE_KIND_MODES = {"measured": "direct", "estimated": "estimated", "derived": "derived"}


def _check_timestamp(value: Any, loc: str, rep: Report) -> None:
    from datetime import datetime

    text = str(value)
    try:
        datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        rep.add("error", "bad-timestamp", f"time {text!r} is not an ISO 8601 timestamp or interval", loc)


def validate_observation(record: Dict[str, Any], reg: Optional[Registry] = None) -> Report:
    """Validate an observation exchange record (schema + optional semantic checks).

    Semantic checks establish that the record is *interpretable*: the referenced
    quantity, method and model exist and have appropriate entity types; the
    value kind is compatible with the quantity's observability; the method
    actually declares the quantity; units match the quantity's dimension; and
    value/uncertainty types are coherent. A syntactically valid identifier is
    never treated as proof that the referenced entity exists.
    """
    rep = validate_instance(record, "observation.schema.json", "observation")
    if rep.errors or reg is None:
        return rep
    loc = "observation"
    q = reg.get(record["quantity"])
    if q is None:
        rep.add("error", "unresolved-reference", f"{record['quantity']} does not resolve", loc)
        return rep
    if q.kind not in QUANTITY_KINDS:
        rep.add("error", "not-a-quantity", f"{q.id} is a {q.kind}, not a quantity", loc)

    value_kind = record.get("value_kind")
    if q.kind == "latent_construct" and value_kind == "measured":
        rep.add("error", "latent-measured", f"{q.id} is a latent construct and cannot be 'measured'; use 'estimated'", loc)
    if (
        q.kind in ("variable", "derived_metric")
        and value_kind == "measured"
        and q.data.get("observability")
        and q.data["observability"] not in MEASURABLE_OBSERVABILITY
    ):
        rep.add("warning", "unobservable-as-measured",
                f"{q.id} has observability {q.data['observability']!r}; a 'measured' value is questionable", loc)

    msg = units.check(record["unit"], q.data.get("dimension"))
    if msg:
        rep.add("error", "unit", msg, loc)

    # Value-type compatibility with the quantity's declared value_type.
    value_type = q.data.get("value_type")
    value = record.get("value")
    if value_type == "boolean" and not isinstance(value, bool):
        rep.add("error", "value-type-mismatch", f"{q.id} is boolean-valued; got {type(value).__name__}", loc)
    elif value_type == "categorical" and not isinstance(value, str):
        rep.add("error", "value-type-mismatch", f"{q.id} is categorical; value must be a string", loc)
    elif value_type in (None, "continuous", "discrete", "ordinal") and not isinstance(value, (int, float)):
        rep.add("error", "value-type-mismatch", f"{q.id} is numeric; got {type(value).__name__}", loc)

    # Uncertainty must share the record's dimension.
    unc_unit = record.get("uncertainty_unit")
    if unc_unit and units.is_known(unc_unit) and units.is_known(record["unit"]):
        if units.dimension_of(unc_unit) != units.dimension_of(record["unit"]):
            rep.add("error", "unit", f"uncertainty_unit {unc_unit!r} does not match the value unit's dimension", loc)

    # Measurement method: must exist, must be a method, must declare the quantity.
    method_ref = record.get("method")
    if method_ref:
        m = reg.get(method_ref)
        if m is None:
            rep.add("error", "unresolved-reference", f"method {method_ref} does not resolve", loc)
        else:
            if m.kind != "measurement_method":
                rep.add("error", "bad-method-kind", f"{base_curie(method_ref)} is a {m.kind}, not a measurement_method", loc)
            else:
                declared = {base_curie(str(mm.get("target"))) for mm in m.data.get("measures", []) or [] if isinstance(mm, dict)}
                if declared and base_curie(q.id) not in declared:
                    rep.add("error", "method-does-not-measure",
                            f"method {base_curie(method_ref)} does not declare measuring {q.id}", loc)
                expected_mode = _VALUE_KIND_MODES.get(value_kind)
                if expected_mode:
                    modes = {str(mm.get("mode")) for mm in m.data.get("measures", []) or []
                             if isinstance(mm, dict) and base_curie(str(mm.get("target", ""))) == base_curie(q.id)}
                    if modes and expected_mode not in modes:
                        rep.add("warning", "method-mode-mismatch",
                                f"value_kind {value_kind!r} expects mode {expected_mode!r}; "
                                f"method declares {sorted(modes)} for {q.id}", loc)

    # Model: must exist and be a model (schema already requires the field for simulated values).
    model_ref = record.get("model")
    if model_ref:
        m = reg.get(model_ref)
        if m is None:
            rep.add("error", "unresolved-reference", f"model {model_ref} does not resolve", loc)
        elif m.kind != "model":
            rep.add("error", "bad-method-kind", f"{base_curie(model_ref)} is a {m.kind}, not a model", loc)

    if record.get("time"):
        _check_timestamp(record["time"], loc, rep)
    return rep
