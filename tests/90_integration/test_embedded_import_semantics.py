# tests/90_integration/test_embedded_import_semantics.py
"""Integration tests for import semantics in built distributions.

These tests verify that when the project is built using serger or zipbundler,
the import semantics work correctly:
- Can import and use the module from built files
- Exported constants and classes are accessible

Tests serger (stitched .py) builds using the actual project
configuration and source code.

These are project-specific tests that verify our code works correctly
when built with the tools (not testing the tools themselves).
"""

import importlib.util
import subprocess
import sys
import types

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
    # Build the project's stitched script
    config_file = PROJ_ROOT / ".serger.jsonc"
    output_file = PROJ_ROOT / "dist" / f"{PROGRAM_SCRIPT}.py"

    # Ensure dist directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # --- execute: build the project ---
    result = subprocess.run(  # noqa: S603
        [
            sys.executable,
            "-m",
            "serger.__main__",
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
            f"stderr: {result.stderr}",
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
    # In stitched mode, __init__.py is excluded,
    # so only the namespace class is available
    assert hasattr(stitched_module, "apathetic_schema"), (
        "apathetic_schema namespace class should be available in stitched module"
    )
    # Verify the namespace class has the expected methods
    assert hasattr(stitched_module.apathetic_schema, "check_schema_conformance"), (
        "check_schema_conformance should be available on namespace class"
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
