"""Identifier resolution: canonical CURIEs, model-symbol references, aliases and labels."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .loader import EntityRecord, Registry, base_curie, parse_curie


class ResolutionError(LookupError):
    pass


class AmbiguousReference(ResolutionError):
    def __init__(self, term: str, candidates: List["Resolution"]):
        self.term = term
        self.candidates = candidates
        ids = ", ".join(f"{c.id} (scope={c.scope})" for c in candidates)
        super().__init__(f"{term!r} is ambiguous: {ids}. Supply a scope.")


@dataclass
class Resolution:
    id: str
    entity: EntityRecord
    matched_by: str  # canonical | symbol | alias | label | predicate-token | functional-form-token
    term: str
    scope: Optional[str] = None
    unit: Optional[str] = None
    symbol: Optional[Dict[str, Any]] = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "term": self.term,
            "id": self.id,
            "kind": self.entity.kind,
            "label": self.entity.label,
            "package": self.entity.package,
            "matched_by": self.matched_by,
        }
        if self.scope:
            d["scope"] = self.scope
        if self.unit:
            d["unit"] = self.unit
        if self.symbol:
            d["symbol"] = self.symbol
        if self.entity.deprecated:
            dep = self.entity.data.get("deprecation", {})
            d["deprecated"] = True
            if dep.get("replaced_by"):
                d["replaced_by"] = dep["replaced_by"]
        if self.notes:
            d["notes"] = self.notes
        return d


class Resolver:
    def __init__(self, registry: Registry):
        self.registry = registry
        self._alias: Dict[str, List[Tuple[Optional[str], EntityRecord, Dict[str, Any]]]] = {}
        self._label: Dict[str, List[EntityRecord]] = {}
        for ent in registry.entities.values():
            for a in ent.data.get("aliases", []) or []:
                if isinstance(a, dict) and a.get("value"):
                    self._alias.setdefault(str(a["value"]), []).append((a.get("scope"), ent, a))
            self._label.setdefault(ent.label.casefold(), []).append(ent)

    # ------------------------------------------------------------------ main API
    def resolve(self, term: str, scope: Optional[str] = None) -> Resolution:
        """Resolve a CURIE, CURIE#symbol, predicate/functional-form token, alias or label.

        Aliases are case-sensitive. Labels are matched case-insensitively and only
        if no alias matches. Ambiguous matches raise :class:`AmbiguousReference`.
        """
        term = str(term).strip()
        parsed = parse_curie(term)
        if parsed:
            return self._resolve_curie(term, parsed)
        if term.startswith("ocpe:"):
            raise ResolutionError(f"{term!r} is not a syntactically valid OCPE identifier")

        tokens = self.registry.predicate_tokens()
        if term in tokens:
            return Resolution(tokens[term].id, tokens[term], "predicate-token", term)
        forms = self.registry.functional_form_tokens()
        if term in forms:
            return Resolution(forms[term].id, forms[term], "functional-form-token", term)

        hits = self._alias.get(term, [])
        if scope is not None:
            hits = [h for h in hits if h[0] == scope or h[0] is None]
        if hits:
            # Several aliases may point at the same entity; ambiguity only if entities differ.
            distinct = {h[1].id for h in hits}
            if len(distinct) > 1:
                raise AmbiguousReference(term, [self._alias_res(term, h) for h in hits])
            return self._alias_res(term, hits[0])

        labels = self._label.get(term.casefold(), [])
        if len(labels) == 1:
            return Resolution(labels[0].id, labels[0], "label", term)
        if len(labels) > 1:
            raise AmbiguousReference(term, [Resolution(e.id, e, "label", term) for e in labels])
        raise ResolutionError(f"Cannot resolve {term!r}")

    def try_resolve(self, term: str, scope: Optional[str] = None) -> Optional[Resolution]:
        try:
            return self.resolve(term, scope)
        except ResolutionError:
            return None

    def aliases_of(self, curie: str) -> List[Dict[str, Any]]:
        ent = self.registry.get(curie)
        return list(ent.data.get("aliases", []) or []) if ent else []

    def search(self, text: str, limit: int = 20) -> List[EntityRecord]:
        """Case-insensitive substring search over ids, labels, aliases and definitions."""
        q = text.casefold()
        scored = []
        for ent in self.registry.entities.values():
            fields = [
                (ent.id.casefold(), 4),
                (ent.label.casefold(), 3),
                (" ".join(str(a.get("value", "")) for a in ent.data.get("aliases", []) or []).casefold(), 3),
                (str(ent.data.get("definition", "")).casefold(), 1),
                (str(ent.data.get("description", "")).casefold(), 1),
            ]
            score = sum(w for f, w in fields if q in f)
            if score:
                scored.append((-score, ent.id, ent))
        return [e for _, _, e in sorted(scored)[:limit]]

    def related(self, curie: str) -> List[EntityRecord]:
        """Relationships whose subject or object is ``curie`` (or one of its model symbols)."""
        base = base_curie(curie)
        out = []
        for rel in self.registry.by_kind("relationship"):
            s, o = str(rel.data.get("subject", "")), str(rel.data.get("object", ""))
            if base in (base_curie(s), base_curie(o)) or curie in (s, o):
                out.append(rel)
        return out

    # ------------------------------------------------------------------ helpers
    def _alias_res(self, term, hit) -> Resolution:
        scope, ent, alias = hit
        return Resolution(ent.id, ent, "alias", term, scope=scope, unit=alias.get("unit"))

    def _resolve_curie(self, term: str, parsed) -> Resolution:
        ns, local, symbol = parsed
        base = f"ocpe:{ns}/{local}"
        ent = self.registry.entities.get(base)
        if ent is None:
            if ns not in self.registry.packages:
                raise ResolutionError(f"{term}: package {ns!r} is not loaded")
            raise ResolutionError(f"{term}: not defined in package {ns!r}")
        if symbol is None:
            return Resolution(base, ent, "canonical", term)
        sym = ent.symbols().get(symbol)
        if sym is None:
            raise ResolutionError(f"{term}: symbol {symbol!r} is not declared by {base}")
        res = Resolution(term, ent, "symbol", term, unit=sym.get("unit"), symbol=sym)
        if sym.get("represents"):
            res.notes.append(f"represents {sym['represents']}")
        return res
