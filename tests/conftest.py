# tests/conftest.py
"""Shared test setup for project.

Each pytest run now targets a single runtime mode:
- Normal mode (default): uses src/apathetic_schema
- Stitched mode: uses dist/apathetic_schema.py when RUNTIME_MODE=stitched
- Zipapp mode: uses dist/apathetic_schema.pyz when RUNTIME_MODE=zipapp

Switch mode with: RUNTIME_MODE=stitched pytest or RUNTIME_MODE=zipapp pytest
"""

import logging
import os
import sys
from collections.abc import Generator

import apathetic_utils
import pytest

from tests.utils.constants import (
    BUNDLER_SCRIPT,
    PROGRAM_PACKAGE,
    PROGRAM_SCRIPT,
    PROJ_ROOT,
)


# early jank hook - must run before importing apathetic_logging
# so we get the stitched version if in stitched/zipapp mode
apathetic_utils.runtime_swap(
    root=PROJ_ROOT,
    package_name=PROGRAM_PACKAGE,
    script_name=PROGRAM_SCRIPT,
    bundler_script=BUNDLER_SCRIPT,
)

# Workaround: serger is being updated to set __STITCHED__, but currently sets
# __STANDALONE__ instead. Set __STITCHED__ based on __STANDALONE__ so
# detect_runtime_mode() works correctly.
if (
    PROGRAM_PACKAGE in sys.modules
    and hasattr(sys.modules[PROGRAM_PACKAGE], "__STANDALONE__")
    and sys.modules[PROGRAM_PACKAGE].__STANDALONE__
    and not hasattr(sys.modules[PROGRAM_PACKAGE], "__STITCHED__")
):
    sys.modules[PROGRAM_PACKAGE].__STITCHED__ = True  # type: ignore[attr-defined]

# Import apathetic_logging AFTER runtime_swap so we get the correct version
# In stitched builds, apathetic_logging is registered in sys.modules
# by the stitched file. In package mode, we import it normally.
if "apathetic_logging" in sys.modules:
    # Use the version from sys.modules (could be stitched or package)
    import apathetic_logging as mod_logging

    mod_logging_source = getattr(
        sys.modules["apathetic_logging"],
        "__file__",
        "unknown",
    )
    was_in_sys_modules = True
else:
    # Not in sys.modules yet, import normally
    import apathetic_logging as mod_logging

    mod_logging_source = getattr(mod_logging, "__file__", "unknown")
    was_in_sys_modules = False

safe_trace = mod_logging.makeSafeTrace("⚡️")

# Debug: show which apathetic_logging module we're using
if was_in_sys_modules:
    safe_trace(
        f"🔍 conftest: Using apathetic_logging from sys.modules: {mod_logging_source}",
    )
else:
    safe_trace(
        f"🔍 conftest: Imported apathetic_logging normally: {mod_logging_source}",
    )

# Register a logger name so getLogger() returns a named logger (not root)
# This ensures getLogger() returns a Logger instance with trace method
mod_logging.registerLogger(PROGRAM_PACKAGE)
safe_trace(
    f"🔍 conftest: Registered logger '{PROGRAM_PACKAGE}' "
    f"using apathetic_logging from: {mod_logging_source}",
)


@pytest.fixture(autouse=True)
def reset_logger_class() -> Generator[None, None, None]:
    """Reset logger class before and after each test for isolation.

    This ensures that any logging state changes in tests don't affect
    subsequent tests. Only needed if tests use logging functionality.
    """
    # Save original state
    original_logger_class = logging.getLoggerClass()

    # Clear any existing loggers
    logger_names = list(logging.Logger.manager.loggerDict.keys())
    for logger_name in logger_names:
        mod_logging.removeLogger(logger_name)

    # Reset to defaults before test
    logging.setLoggerClass(mod_logging.Logger)
    mod_logging.Logger.extendLoggingModule()

    yield

    # Clear loggers again after test
    logger_names = list(logging.Logger.manager.loggerDict.keys())
    for logger_name in logger_names:
        mod_logging.removeLogger(logger_name)

    # Restore original state after test
    logging.setLoggerClass(original_logger_class)
    mod_logging.Logger.extendLoggingModule()


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _mode() -> str:
    return os.getenv("RUNTIME_MODE", "package")


def _filter_debug_tests(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    # detect if the user is filtering for debug tests
    keywords = config.getoption("-k") or ""
    running_debug = "debug" in keywords.lower()

    if running_debug:
        return  # user explicitly requested them, don't skip

    for item in items:
        if "debug" in item.keywords:
            item.add_marker(
                pytest.mark.skip(reason="Skipped debug test (use -k debug to run)"),
            )


def _filter_runtime_mode_tests(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    mode = _mode()
    # Check if verbose mode is enabled (verbose > 0 means user wants verbose output)
    verbose = getattr(config.option, "verbose", 0)
    is_quiet = verbose <= 0

    # Only track included tests if not in quiet mode (for later reporting)
    included_map: dict[str, int] | None = {} if not is_quiet else None
    root = str(config.rootpath)
    testpaths: list[str] = config.getini("testpaths") or []

    # Identify mode-specific files by a custom variable defined at module scope
    for item in list(items):
        mod = item.getparent(pytest.Module)
        if mod is None or not hasattr(mod, "obj"):
            continue

        runtime_marker = getattr(mod.obj, "__runtime_mode__", None)

        if runtime_marker and runtime_marker != mode:
            items.remove(item)
            continue

        # Only track if not in quiet mode
        if runtime_marker and runtime_marker == mode and included_map is not None:
            file_path = str(item.fspath)
            # Make path relative to project root dir
            if file_path.startswith(root):
                file_path = os.path.relpath(file_path, root)
                for tp in testpaths:
                    if file_path.startswith(tp.rstrip("/") + os.sep):
                        file_path = file_path[len(tp.rstrip("/") + os.sep) :]
                        break

            included_map[file_path] = included_map.get(file_path, 0) + 1

    # Store results for later reporting (only if not in quiet mode)
    if included_map is not None:
        config._included_map = included_map  # type: ignore[attr-defined]  # noqa: SLF001
        config._runtime_mode = mode  # type: ignore[attr-defined]  # noqa: SLF001


# ----------------------------------------------------------------------
# Hooks
# ----------------------------------------------------------------------


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest options based on verbosity."""
    verbose = getattr(config.option, "verbose", 0)
    if verbose <= 0:
        # In quiet mode, modify reportchars to exclude skipped tests ('s')
        # The -ra flag in pytest.ini shows all, but hide skipped in quiet mode
        reportchars = getattr(config.option, "reportchars", "")
        if reportchars == "a":
            # 'a' means "all except passed", change to exclude skipped and passed output
            # Use explicit chars: f (failed), E (error), x (xfailed), X (xpassed)
            config.option.reportchars = "fExX"
        elif "s" in reportchars or "P" in reportchars:
            # Remove 's' (skipped) and 'P' (passed with output) in quiet mode
            config.option.reportchars = reportchars.replace("s", "").replace("P", "")


def pytest_report_header(config: pytest.Config) -> str:  # noqa: ARG001 # pyright: ignore[reportUnknownParameterType]
    mode = _mode()
    return f"Runtime mode: {mode}"


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Filter and record runtime-specific tests for later reporting.

    also automatically skips debug tests unless asked for
    """
    _filter_debug_tests(config, items)
    _filter_runtime_mode_tests(config, items)


def pytest_unconfigure(config: pytest.Config) -> None:
    """Print summary of included runtime-specific tests at the end."""
    included_map: dict[str, int] = getattr(config, "_included_map", {})
    mode = getattr(config, "_runtime_mode", "package")

    if not included_map:
        return

    # Only print if pytest is not in quiet mode (verbose > 0 means verbose mode)
    verbose = getattr(config.option, "verbose", 0)
    if verbose <= 0:
        return

    total_tests = sum(included_map.values())
    print(
        f"🧪 Included {total_tests} {mode}-specific tests"
        f" across {len(included_map)} files:",
    )
    for path, count in sorted(included_map.items()):
        print(f"   • ({count}) {path}")
