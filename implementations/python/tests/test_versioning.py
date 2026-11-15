"""Engine tests: semantic versions and version constraints."""

import pytest

from ocpe.versioning import Version, satisfies


def test_version_parsing_and_ordering():
    assert Version.parse("1.2.3") == Version(1, 2, 3)
    assert Version.parse("0.1") == Version(0, 1, 0)
    assert Version.parse("2.0.0-alpha") < Version.parse("2.0.0")
    assert Version.parse("1.0.0") < Version.parse("1.0.1") < Version.parse("1.1.0") < Version.parse("2.0.0")
    assert str(Version.parse("1.2.3-beta.1")) == "1.2.3-beta.1"


def test_version_parse_rejects_garbage():
    with pytest.raises(ValueError):
        Version.parse("not.a.version")
    with pytest.raises(ValueError):
        Version.parse("1.2.3.4")


@pytest.mark.parametrize("version,constraint,expected", [
    ("1.2.3", "*", True),
    ("1.2.3", "1.2.3", True),
    ("1.2.3", "^1.0.0", True),
    ("2.0.0", "^1.0.0", False),
    ("0.2.3", "^0.2.0", True),
    ("0.3.0", "^0.2.0", False),
    ("1.2.9", "~1.2.0", True),
    ("1.3.0", "~1.2.0", False),
    ("0.1.5", ">=0.1.0 <0.2.0", True),
    ("0.2.0", ">=0.1.0 <0.2.0", False),
    ("1.5.0", "^1.0.0 || ^2.0.0", True),
    ("3.0.0", "^1.0.0 || ^2.0.0", False),
    ("1.0.0", ">1.0.0", False),
    ("1.0.1", ">1.0.0", True),
    # pre-releases only match when the constraint mentions the same core version
    ("1.0.0-alpha", "^1.0.0", False),
    ("1.0.0-alpha", ">=1.0.0-alpha", True),
])
def test_satisfies(version, constraint, expected):
    assert satisfies(version, constraint) is expected


def test_satisfies_rejects_bad_constraint():
    with pytest.raises(ValueError):
        satisfies("1.0.0", "not-a-constraint")
