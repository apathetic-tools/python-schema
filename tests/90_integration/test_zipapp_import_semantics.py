# tests/90_integration/test_zipapp_import_semantics.py
"""Integration tests for import semantics in zipapp builds.

These tests verify that when the project is built using shiv,
the import semantics work correctly:
- Can import and use the module from zipapp format
- Exported constants and classes are accessible

Tests shiv (zipapp .pyz) builds using the actual project configuration
and source code.

These are project-specific tests that verify our code works correctly
when built with shiv (not testing the tool itself).
"""

# Runtime mode: only run in zipapp mode
__runtime_mode__ = "zipapp"

import importlib
import subprocess
import sys
import zipfile

import apathetic_utils
import pytest

from tests.utils.constants import PROGRAM_PACKAGE, PROGRAM_SCRIPT, PROJ_ROOT


def test_zipapp_import_semantics() -> None:
    """Test that zipapp builds maintain correct import semantics.

    This test verifies our project code works correctly when built with shiv:
    1. Builds apathetic_utils as a zipapp using shiv (from project root)
    2. Imports from the zipapp and verifies import semantics work correctly:
       - Can import and use the module from zipapp format
       - Exported constants and classes are accessible

    This verifies our project configuration and code work correctly with shiv.
    """
    # --- setup ---
    # Build the project's zipapp
    zipapp_file = PROJ_ROOT / "dist" / f"{PROGRAM_SCRIPT}.pyz"

    # Ensure dist directory exists
    zipapp_file.parent.mkdir(parents=True, exist_ok=True)

    # --- execute: build zipapp ---
    shiv_cmd = apathetic_utils.find_shiv()
    result = subprocess.run(  # noqa: S603
        [
            shiv_cmd,
            "-c",
            PROGRAM_PACKAGE,
            "-o",
            str(zipapp_file),
            ".",
        ],
        cwd=PROJ_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        pytest.fail(
            f"Shiv failed with return code {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    if not zipapp_file.exists():
        pytest.fail(f"Zipapp file not created at {zipapp_file}")

    # Verify it's a valid zip file
    assert zipfile.is_zipfile(zipapp_file), "Zipapp should be a valid zip file"

    # --- execute: import from zipapp ---
    # Add zipapp to sys.path and import
    sys.path.insert(0, str(zipapp_file))

    try:
        # Import PROGRAM_PACKAGE from the zipapp
        zipapp_module = importlib.import_module(PROGRAM_PACKAGE)

        # --- verify: import semantics ---
        # Verify that key exports from apathetic_schema are available
        # In zipapp mode, __init__.py is included, so mixin classes are exported
        assert hasattr(
            zipapp_module, "ApatheticSchema_Internal_CheckSchemaConformance"
        ), (
            f"{PROGRAM_PACKAGE}.ApatheticSchema_Internal_CheckSchemaConformance "
            "should be available"
        )
        assert hasattr(zipapp_module, "ApatheticSchema_ValidationSummary"), (
            f"{PROGRAM_PACKAGE}.ApatheticSchema_ValidationSummary should be available"
        )
        # Verify they are usable
        assert hasattr(
            zipapp_module.ApatheticSchema_Internal_CheckSchemaConformance,
            "check_schema_conformance",
        ), "check_schema_conformance should be available on mixin class"

    finally:
        # Clean up sys.path
        if str(zipapp_file) in sys.path:
            sys.path.remove(str(zipapp_file))
        # Clean up imported modules
        if PROGRAM_PACKAGE in sys.modules:
            del sys.modules[PROGRAM_PACKAGE]
