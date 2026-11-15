"""Repository-level conformance runner.

Executes the official OCPE conformance suite (test vectors + fixture
expectations in ``conformance/``) against the installed reference engine.
Other implementations can demonstrate equivalent behavior by executing the
same vectors (see conformance/README.md).
"""

from pathlib import Path

from ocpe.vectors import run_conformance

CONFORMANCE_DIR = Path(__file__).resolve().parent.parent / "conformance"


def test_conformance_suite():
    report = run_conformance(CONFORMANCE_DIR)
    assert report["ok"], (
        f"{report['failed']} of {report['passed'] + report['failed']} conformance checks failed:\n"
        + "\n".join(f"  {f['id']}: {'; '.join(f['failures'])}" for f in report["failures"])
    )
