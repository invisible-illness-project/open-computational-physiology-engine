"""Engine tests: unit registry, normalization, dimensional consistency."""

import pytest

from ocpe import units


def test_dimensions_registered():
    dims = units.dimensions()
    for name in ("dimensionless", "time", "volume", "pressure", "volume_flow", "event_rate", "frequency"):
        assert name in dims


def test_conversion_within_dimension():
    assert abs(units.convert(1.0, "/s", "/min") - 60.0) < 1e-9
    assert abs(units.convert(4500.0, "mL", "L") - 4.5) < 1e-9
    assert abs(units.convert(2.0, "min", "s") - 120.0) < 1e-9


def test_conversion_across_dimensions_rejected():
    with pytest.raises(units.UnitError):
        units.convert(1.0, "mL", "mm[Hg]")
    with pytest.raises(units.UnitError):
        units.convert(1.0, "s", "/min")


def test_normalize_alternative_spellings():
    assert units.normalize("mmHg") == "mm[Hg]"
    assert units.normalize("bpm") == "/min"
    assert units.normalize("beats/min") == "/min"
    assert units.normalize("mm[Hg]") == "mm[Hg]"


def test_unknown_unit_raises():
    with pytest.raises(units.UnitError):
        units.normalize("furlongs")
    with pytest.raises(units.UnitError):
        units.info("furlongs")


def test_check_with_expected_dimension():
    assert units.check("mL/s", "volume_flow") is None
    assert units.check("mm[Hg]", "volume_flow") is not None
    assert units.check("furlongs") is not None


def test_dimension_of():
    assert units.dimension_of("mm[Hg]") == "pressure"
    assert units.dimension_of("L/min") == "volume_flow"


def test_same_unit_conversion_is_identity():
    assert units.convert(37.0, "Cel", "Cel") == 37.0
    assert units.convert(5.0, "s", "s") == 5.0
