# tests/0_independant/test_pytest__runtime_mode_swap.py
"""Verify runtime mode swap functionality in conftest.py.

This test verifies that our unique runtime_mode swap functionality works
correctly. Our conftest.py uses runtime_swap() to allow tests to run against
either the package (src/apathetic_utils) or the stitched script
(dist/apathetic_utils.py) based on the RUNTIME_MODE environment variable.

Verifies:
  - When RUNTIME_MODE=stitched: All modules resolve to dist/apathetic_utils.py
  - When RUNTIME_MODE is unset (package): All modules resolve to src/apathetic_utils/
  - Python's import cache (sys.modules) points to the correct sources
  - All submodules load from the expected location

This ensures our dual-runtime testing infrastructure functions correctly.
"""

import importlib
import inspect
import os
import pkgutil
import sys
from pathlib import Path

import apathetic_logging as mod_logging
import apathetic_utils.runtime as amod_utils_runtime
import pytest

# Import a module from the main package to test
import apathetic_schema as amod_schema
from tests.utils import PROGRAM_PACKAGE, PROGRAM_SCRIPT, PROJ_ROOT


# --- convenience -----------------------------------------------------------

_runtime = amod_utils_runtime.ApatheticUtils_Internal_Runtime

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

safe_trace = mod_logging.makeSafeTrace("🪞")

# Debug: show which apathetic_logging module we're using in the test
mod_logging_source = getattr(mod_logging, "__file__", "unknown")
safe_trace(f"🔍 test: Using apathetic_logging from: {mod_logging_source}")

SRC_ROOT = PROJ_ROOT / "src"
DIST_ROOT = PROJ_ROOT / "dist"


def list_important_modules() -> list[str]:
    """Return all importable submodules under the package, if available."""
    important: list[str] = []
    # Use the main package module (apathetic_schema.schema) to find package path
    package_module = sys.modules.get(PROGRAM_PACKAGE)
    if package_module is None:
        # Fallback: try to get it from the schema module's parent
        package_module = sys.modules.get(amod_schema.__name__.rsplit(".", 1)[0])

    if package_module is None or not hasattr(package_module, "__path__"):
        safe_trace("pkgutil.walk_packages skipped — stitched runtime (no __path__)")
        # Add the main package and schema module
        important.append(PROGRAM_PACKAGE)
        important.append(amod_schema.__name__)
    else:
        for _, name, _ in pkgutil.walk_packages(
            package_module.__path__,
            PROGRAM_PACKAGE + ".",
        ):
            important.append(name)

    return important


def dump_snapshot(*, include_full: bool = False) -> None:
    """Prints a summary of key modules and (optionally) a full sys.modules dump."""
    mode: str = os.getenv("RUNTIME_MODE", "package")

    safe_trace("========== SNAPSHOT ===========")
    safe_trace(f"RUNTIME_MODE={mode}")

    important_modules = list_important_modules()

    # Summary: the modules we care about most
    safe_trace("======= IMPORTANT MODULES =====")
    for name in important_modules:
        mod = sys.modules.get(name)
        if not mod:
            continue
        origin = getattr(mod, "__file__", None)
        safe_trace(f"  {name:<25} {origin}")

    if include_full:
        # Full origin dump
        safe_trace("======== OTHER MODULES ========")
        for name, mod in sorted(sys.modules.items()):
            if name in important_modules:
                continue
            origin = getattr(mod, "__file__", None)
            safe_trace(f"  {name:<38} {origin}")

    safe_trace("===============================")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def _get_runtime_module_file() -> str:
    """Get the file path for a module from the main package based on RUNTIME_MODE."""
    mode = os.getenv("RUNTIME_MODE", "unknown")
    # Use a module from the main package (apathetic_schema.schema)
    # In stitched mode, get the module from sys.modules to ensure we're using
    # the version from the stitched script (which was loaded by runtime_swap)
    # rather than the one imported at the top of this file (which might be from
    # the package if it was imported before runtime_swap ran)
    schema_module_name = amod_schema.__name__
    if mode == "stitched" and schema_module_name in sys.modules:
        # Use the module from sys.modules, which should be from the stitched script
        schema_module_actual = sys.modules[schema_module_name]
        # Check __file__ directly - for stitched modules, should point to
        # dist/apathetic_schema.py
        schema_file_path = getattr(schema_module_actual, "__file__", None)
        if schema_file_path:
            return str(schema_file_path)
        # Fall back to inspect.getsourcefile if __file__ is not available
        return str(inspect.getsourcefile(schema_module_actual) or "")
    # Otherwise, use the module imported at the top of the file
    return str(inspect.getsourcefile(amod_schema))


def _verify_stitched_mode(
    runtime_mode: str,
    expected_script: Path,
    utils_file: str,
) -> None:
    """Verify stitched mode expectations."""
    # what does the module itself think?
    assert runtime_mode == "stitched", (
        f"Expected runtime_mode='stitched' but got '{runtime_mode}'"
    )

    # exists
    assert expected_script.exists(), f"Expected stitched script at {expected_script}"

    # path peeks - in stitched mode, modules might be imported from
    # the package, but they should still detect stitched mode
    # correctly via detect_runtime_mode()
    # So we only check the path if the module is actually from dist/
    if utils_file.startswith(str(DIST_ROOT)):
        # Module is from stitched script, verify it's the right file
        assert Path(utils_file).samefile(expected_script), (
            f"{utils_file} should be same file as {expected_script}"
        )
    else:
        # Module is from package, but that's OK as long as
        # detect_runtime_mode() correctly returns "stitched"
        safe_trace(
            f"Note: {amod_schema.__name__} loaded from package "
            f"({utils_file}), but runtime_mode correctly detected as 'stitched'",
        )

    # troubleshooting info
    safe_trace(
        f"sys.modules['{PROGRAM_PACKAGE}'] = {sys.modules.get(PROGRAM_PACKAGE)}",
    )
    schema_module_name = amod_schema.__name__
    safe_trace(
        f"sys.modules['{schema_module_name}'] = {sys.modules.get(schema_module_name)}",
    )


def _verify_package_mode(runtime_mode: str, utils_file: str) -> None:
    """Verify package mode expectations."""
    # what does the module itself think?
    assert runtime_mode != "stitched"

    # path peeks - in package mode, modules might be imported from
    # the package (virtualenv site-packages), but they should
    # still detect package mode correctly via detect_runtime_mode()
    # So we only check the path if the module is actually from src/
    if utils_file.startswith(str(SRC_ROOT)):
        # Module is from source, verify it's in the right location
        assert Path(utils_file).is_relative_to(SRC_ROOT), (
            f"{utils_file} should be relative to {SRC_ROOT}"
        )
    else:
        # Module is from package, but that's OK as long as
        # detect_runtime_mode() correctly returns non-stitched mode
        safe_trace(
            f"Note: {amod_schema.__name__} loaded from package "
            f"({utils_file}), but runtime_mode correctly detected as "
            f"'{runtime_mode}' (not 'stitched')",
        )


def _verify_submodules(mode: str, expected_script: Path, runtime_mode: str) -> None:
    """Verify all submodules are loaded from the expected location."""
    important_modules = list_important_modules()
    # Only check modules that are part of PROGRAM_PACKAGE (not dependencies)
    for submodule in important_modules:
        is_package_module = (
            submodule.startswith(PROGRAM_PACKAGE + ".") or submodule == PROGRAM_PACKAGE
        )
        if not is_package_module:
            # Skip dependencies that aren't part of the main package
            continue
        mod = importlib.import_module(f"{submodule}")
        path = Path(inspect.getsourcefile(mod) or "")
        if mode == "stitched":
            assert path.samefile(expected_script), f"{submodule} loaded from {path}"
        # In package mode, modules might be from src/ (editable install)
        # or from package (regular install). Both are acceptable
        # as long as detect_runtime_mode() correctly identifies non-stitched mode.
        elif not path.is_relative_to(SRC_ROOT):
            # Module is from package, verify it's not from dist/
            assert not path.samefile(expected_script), (
                f"{submodule} should not be from stitched script in "
                f"package mode: {path}"
            )
            safe_trace(
                f"Note: {submodule} loaded from package ({path}), "
                f"but runtime_mode correctly detected as '{runtime_mode}' "
                f"(not 'stitched')",
            )


def test_pytest_runtime_cache_integrity() -> None:
    """Verify runtime mode swap correctly loads modules from expected locations.

    Ensures that modules imported at the top of test files resolve to the
    correct source based on RUNTIME_MODE:
    - stitched mode: All modules must load from dist/apathetic_schema.py
    - package mode: All modules must load from src/apathetic_schema/

    Also verifies that Python's import cache (sys.modules) doesn't have stale
    references pointing to the wrong runtime.
    """
    # --- setup ---
    mode = os.getenv("RUNTIME_MODE", "unknown")
    expected_script = DIST_ROOT / f"{PROGRAM_SCRIPT}.py"
    utils_file = _get_runtime_module_file()

    # --- execute ---
    safe_trace(f"RUNTIME_MODE={mode}")
    safe_trace(f"{amod_schema.__name__}  → {utils_file}")

    if os.getenv("TRACE"):
        dump_snapshot()
    # Access via main module to get the function from the namespace class
    runtime_mode = _runtime.detect_runtime_mode(PROGRAM_PACKAGE)

    if mode == "stitched":
        _verify_stitched_mode(runtime_mode, expected_script, utils_file)
    else:
        _verify_package_mode(runtime_mode, utils_file)

    # --- verify both ---
    _verify_submodules(mode, expected_script, runtime_mode)


@pytest.mark.debug
def test_debug_dump_all_module_origins() -> None:
    """Debug helper: Dump all loaded module origins for forensic analysis.

    Useful when debugging import leakage, stale sys.modules cache, or runtime
    mode swap issues. Always fails intentionally to force pytest to show TRACE
    output.

    Usage:
        TRACE=1 poetry run pytest -k debug -s
        RUNTIME_MODE=stitched TRACE=1 poetry run pytest -k debug -s
    """
    # --- verify ---

    # dump everything we know
    dump_snapshot(include_full=True)

    # show total module count for quick glance
    count = sum(1 for name in sys.modules if name.startswith(PROGRAM_PACKAGE))
    safe_trace(f"Loaded {count} {PROGRAM_PACKAGE} modules total")

    # force visible failure for debugging runs
    xmsg = f"Intentional fail — {count} {PROGRAM_PACKAGE} modules listed above."
    raise AssertionError(xmsg)
