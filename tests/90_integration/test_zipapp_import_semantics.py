# tests/90_integration/test_zipapp_import_semantics.py
"""Integration tests for import semantics in zipapp builds.

These tests verify that when the project is built using zipbundler,
the import semantics work correctly:
- Can import and use the module from zipapp format
- Exported constants and classes are accessible

Tests zipbundler (zipapp .pyz) builds using the actual project configuration
and source code.

These are project-specific tests that verify our code works correctly
when built with zipbundler (not testing the tool itself).
"""

# Runtime mode: only run in zipapp mode
__runtime_mode__ = "zipapp"

import importlib
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from tests.utils.constants import PROGRAM_PACKAGE, PROGRAM_SCRIPT, PROJ_ROOT


def test_zipapp_import_semantics(tmp_path: Path) -> None:
    """Test that zipapp builds maintain correct import semantics.

    This test verifies our project code works correctly when built with zipbundler:
    1. Builds apathetic_utils as a zipapp using zipbundler (from project root)
    2. Imports from the zipapp and verifies import semantics work correctly:
       - Can import and use the module from zipapp format
       - Exported constants and classes are accessible

    This verifies our project configuration and code work correctly with zipbundler.
    """
    # --- setup ---
    # Use pytest's tmp_path to avoid race conditions in parallel test execution
    test_id = id(test_zipapp_import_semantics)
    zipapp_file = tmp_path / f"{PROGRAM_SCRIPT}_{test_id}.pyz"

    # --- execute: build zipapp ---
    zipapp_cmd = [sys.executable, "-m", "zipbundler"]
    result = subprocess.run(  # noqa: S603
        [
            *zipapp_cmd,
            "-c",
            "-o",
            str(zipapp_file),
            "src",
        ],
        cwd=PROJ_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        pytest.fail(
            f"Zipbundler failed with return code {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}",
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
        # In zipapp mode, __init__.py is included, so public API is exported
        assert hasattr(zipapp_module, "apathetic_schema"), (
            f"{PROGRAM_PACKAGE}.apathetic_schema should be available"
        )
        assert hasattr(zipapp_module, "ApatheticSchema_ValidationSummary"), (
            f"{PROGRAM_PACKAGE}.ApatheticSchema_ValidationSummary should be available"
        )
        # Verify the namespace class is usable
        assert isinstance(zipapp_module.apathetic_schema, type), (
            "apathetic_schema should be a class (namespace)"
        )
        # Verify key methods are available
        assert hasattr(
            zipapp_module.apathetic_schema,
            "check_schema_conformance",
        ), "check_schema_conformance should be available on apathetic_schema class"
        assert hasattr(zipapp_module, "check_schema_conformance"), (
            "check_schema_conformance should be available as a direct export"
        )

    finally:
        # Clean up sys.path
        if str(zipapp_file) in sys.path:
            sys.path.remove(str(zipapp_file))
        # Clean up imported modules
        if PROGRAM_PACKAGE in sys.modules:
            del sys.modules[PROGRAM_PACKAGE]
