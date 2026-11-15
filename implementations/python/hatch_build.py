"""Hatchling build hook: bundle the language-independent OCPE specification.

Copies ``specification/`` (two levels up from this directory in a source
checkout) into ``src/ocpe/_spec`` so built wheels and sdists are
self-contained. When building from an sdist, ``_spec`` is already present and
the hook leaves it untouched.
"""

from pathlib import Path
import shutil

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomHook(BuildHookInterface):
    def initialize(self, version, build_data):
        root = Path(self.root)
        spec_dir = root.parent.parent / "specification"
        target = root / "src" / "ocpe" / "_spec"
        if spec_dir.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(spec_dir, target)
