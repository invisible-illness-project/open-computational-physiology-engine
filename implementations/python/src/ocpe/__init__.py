"""OCPE - Open Computational Physiology Engine (Python reference implementation).

A small, model-agnostic engine for loading, validating, resolving and versioning
physiological knowledge expressed in the OCPE specification. OCPE defines the
language; domain content lives in independently versioned external packages.

Quick start::

    import ocpe
    reg = ocpe.load(["path/to/domain-package"])   # plus the bundled core vocabulary
    report = ocpe.validate(reg)                   # structural + semantic validation
    r = ocpe.Resolver(reg).resolve("ocpe:my-package/my-variable")
    print(r.id, r.entity.kind)

Validation is structural; it never asserts scientific validity.
"""

from .loader import (  # noqa: F401
    EntityRecord,
    Issue,
    LoadError,
    Package,
    Registry,
    Report,
    discover,
    load_package,
    load_registry,
    parse_curie,
)
from .resolver import AmbiguousReference, Resolution, ResolutionError, Resolver  # noqa: F401
from .validator import validate_instance, validate_observation, validate_registry  # noqa: F401
from .spec import spec_version  # noqa: F401

__version__ = "0.1.0"


def load(paths=None, include_core: bool = True) -> Registry:
    """Load packages from ``paths`` (default: only the OCPE core vocabulary).

    OCPE ships no domain content; supply the directories of the external
    domain packages you trust.
    """
    return load_registry(paths, include_core=include_core)


def validate(registry: Registry, packages=None) -> Report:
    """Validate a loaded registry (optionally only the given package ids)."""
    return validate_registry(registry, packages)
