# tests/90_integration/test_embedded_import_semantics.py
"""Integration tests for import semantics in built distributions.

These tests verify that when the project is built using serger or shiv,
the import semantics work correctly:
- Can import and use the module from built files
- Exported constants and classes are accessible

Tests both serger (single-file .py) and shiv (zipapp .pyz) builds
using the actual project configuration and source code.

These are project-specific tests that verify our code works correctly
when built with the tools (not testing the tools themselves).
"""

import importlib.util
import subprocess
import sys
import types
import zipfile

import apathetic_utils
import pytest

from tests.utils.constants import PROGRAM_PACKAGE, PROGRAM_SCRIPT, PROJ_ROOT


def test_serger_build_import_semantics() -> None:
    """Test that serger build of the project maintains correct import semantics.

    This test verifies our project code works correctly when built with serger:
    1. Builds the project using the actual .serger.jsonc config
    2. Imports the built file and verifies import semantics work correctly:
       - Can import and use the module from the stitched file
       - Exported constants and classes are accessible

    This verifies our project configuration and code work correctly with serger.
    """
    # --- setup ---
    # Build the project's single-file script
    serger_script = PROJ_ROOT / "bin" / "serger.py"
    config_file = PROJ_ROOT / ".serger.jsonc"
    output_file = PROJ_ROOT / "dist" / f"{PROGRAM_SCRIPT}.py"

    # Ensure dist directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # --- execute: build the project ---
    result = subprocess.run(  # noqa: S603
        [
            sys.executable,
            str(serger_script),
            "--config",
            str(config_file),
        ],
        cwd=PROJ_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        pytest.fail(
            f"Serger failed with return code {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    if not output_file.exists():
        pytest.fail(f"Stitched file not created at {output_file}")

    # Import the stitched file programmatically
    # Use a unique module name to avoid conflicts with other tests
    built_module_name = f"{PROGRAM_PACKAGE}_serger_build_{id(output_file)}"
    spec = importlib.util.spec_from_file_location(
        built_module_name,
        output_file,
    )
    if spec is None or spec.loader is None:
        pytest.fail(f"Could not create import spec for {output_file}")

    # Save all PROGRAM_PACKAGE-related modules to restore later
    original_modules = {
        name: mod
        for name, mod in sys.modules.items()
        if name == PROGRAM_PACKAGE or name.startswith(f"{PROGRAM_PACKAGE}.")
    }

    stitched_module = importlib.util.module_from_spec(spec)
    sys.modules[built_module_name] = stitched_module

    # Temporarily prevent the stitched module from registering PROGRAM_PACKAGE
    # in sys.modules during execution by temporarily removing it
    temp_removed = False
    temp_module: types.ModuleType | None = None
    if PROGRAM_PACKAGE in sys.modules:
        temp_module = sys.modules.pop(PROGRAM_PACKAGE)
        temp_removed = True

    try:
        spec.loader.exec_module(stitched_module)
    except Exception as e:  # noqa: BLE001
        pytest.fail(f"Failed to import stitched module: {e}")
    finally:
        # Restore PROGRAM_PACKAGE immediately after execution
        # to prevent any side effects
        if temp_removed and temp_module is not None:
            sys.modules[PROGRAM_PACKAGE] = temp_module
        elif PROGRAM_PACKAGE in sys.modules:
            # If it was added during execution, remove it
            del sys.modules[PROGRAM_PACKAGE]

    # --- verify: import semantics ---
    # Verify that the stitched module can be imported and used
    # Check that key exports from apathetic_schema are available
    assert hasattr(stitched_module, "check_schema_conformance"), (
        "check_schema_conformance should be available in stitched module"
    )
    assert hasattr(stitched_module, "ValidationSummary"), (
        "ValidationSummary should be available in stitched module"
    )
    # Verify they are callable/usable
    assert callable(stitched_module.check_schema_conformance), (
        "check_schema_conformance should be callable"
    )

    # Clean up - remove our test module and any submodules it might have created
    # Remove all modules that start with our built module name
    modules_to_remove = [
        name for name in list(sys.modules.keys()) if name.startswith(built_module_name)
    ]
    for name in modules_to_remove:
        del sys.modules[name]

    # Restore all original PROGRAM_PACKAGE-related modules
    # First, remove any that were added
    current_package_modules = {
        name
        for name in sys.modules
        if name == PROGRAM_PACKAGE or name.startswith(f"{PROGRAM_PACKAGE}.")
    }
    for name in current_package_modules:
        if name not in original_modules:
            del sys.modules[name]
    # Then restore the original ones
    for name, mod in original_modules.items():
        sys.modules[name] = mod


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
        assert hasattr(zipapp_module, "check_schema_conformance"), (
            f"{PROGRAM_PACKAGE}.check_schema_conformance should be available"
        )
        assert hasattr(zipapp_module, "ValidationSummary"), (
            f"{PROGRAM_PACKAGE}.ValidationSummary should be available"
        )
        # Verify they are callable/usable
        assert callable(zipapp_module.check_schema_conformance), (
            "check_schema_conformance should be callable"
        )

    finally:
        # Clean up sys.path
        if str(zipapp_file) in sys.path:
            sys.path.remove(str(zipapp_file))
        # Clean up imported modules
        if PROGRAM_PACKAGE in sys.modules:
            del sys.modules[PROGRAM_PACKAGE]
