"""loader.py
------------
Several files in this project (e.g. "api client.py", "sample data.py",
"scanner tab.py") intentionally use spaces instead of underscores in
their filenames. Python's `import`/`from ... import ...` syntax can't
reference a module whose filename contains a space, so those files are
loaded through this helper instead.

Usage:
    from utils.loader import load

    api_client_module = load("utils/api client.py")
    api_client_module.APIClient(...)

    # or pull specific names out directly:
    sample_data = load("utils/sample data.py")
    SAMPLE_COURSES = sample_data.SAMPLE_COURSES
"""

import importlib.util
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent  # project root
_cache: dict[str, object] = {}


def load(relative_path: str):
    """Load and return the module at `relative_path` (relative to the
    project root), e.g. load("utils/api client.py"). Results are cached
    per path, so re-importing the same module elsewhere is cheap and
    returns the same module object.
    """
    if relative_path in _cache:
        return _cache[relative_path]

    file_path = _ROOT / relative_path
    if not file_path.is_file():
        raise FileNotFoundError(f"loader.load: no such file: {file_path}")

    # Internal module name only (never seen by callers) — needs to be a
    # valid identifier for Python's import machinery bookkeeping.
    module_name = "_loaded_" + file_path.stem.replace(" ", "_").replace("-", "_")

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    _cache[relative_path] = module
    return module
