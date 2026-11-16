"""Hatchling build hook: bundle the language-independent OCPE specification.

Copies ``specification/`` (two levels up from this directory in a source
checkout) into ``src/ocpe/_spec`` so built wheels and sdists are
self-contained. When building from an sdist, ``_spec`` is already present and
the hook leaves it untouched.

Also copies the repository-root ``LICENSE`` and ``NOTICE`` into this
directory so hatchling can embed them in the distributions as
``dist-info/licenses/`` (a single source of truth at the repository root;
the copies are build artifacts, listed in .gitignore).
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
        for name in ("LICENSE", "NOTICE"):
            source = root.parent.parent / name
            if source.is_file():
                shutil.copyfile(source, root / name)
