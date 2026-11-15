"""OCPE - Open Computational Physiology Engine (Python reference implementation).

A small, model-agnostic engine for loading, validating, resolving and versioning
physiological knowledge expressed in the OCPE specification.

Quick start::

    import ocpe
    reg = ocpe.load()                       # repository packages (or ocpe.load([...paths]))
    report = ocpe.validate(reg)             # structural + semantic validation
    r = ocpe.Resolver(reg).resolve("Hc", scope="legacy-kb")
    print(r.id, r.unit)                     # ocpe:cardiovascular/heart-rate /s

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
    """Load packages from ``paths`` (default: the repository's packages/ directory)."""
    return load_registry(paths, include_core=include_core)


def validate(registry: Registry, packages=None) -> Report:
    """Validate a loaded registry (optionally only the given package ids)."""
    return validate_registry(registry, packages)
