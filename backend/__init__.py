"""Top-level package for backend code used in tests and application runtime.""" 

import os
import sys
import importlib

# Ensure that the `backend` directory is on PYTHONPATH so that `import app` works
_backend_dir = os.path.abspath(os.path.dirname(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# Guarantee that `import app` resolves to the backend's FastAPI package.
try:
    # First attempt normal import which should succeed if PYTHONPATH is correctly set.
    import app as _app_module  # type: ignore
except ModuleNotFoundError:
    # Fallback: explicitly import the module from the backend package and alias it.
    _app_module = importlib.import_module("backend.app")
    sys.modules["app"] = _app_module
else:
    # Ensure the module object is referenced under the expected fully-qualified name.
    sys.modules.setdefault("backend.app", sys.modules["app"])  # type: ignore

# Clean up to avoid leaking internal names
del os, _backend_dir, importlib 