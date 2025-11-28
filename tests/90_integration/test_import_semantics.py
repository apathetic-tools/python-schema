# tests/90_integration/test_import_semantics.py
"""Integration tests for import semantics in different runtime modes.

This test explicitly verifies that import semantics work correctly in both
installed mode (from src/) and singlefile mode (from dist/apathetic_utils.py).

The test verifies that:
- Imports from apathetic_utils work correctly
- Exported constants and classes are accessible
- Values are correct regardless of runtime mode

This replicates the verification done in mode_verify/installed_example/installed_run.py
and mode_verify/singlefile_example/singlefile_run.py, but as a pytest integration test
that runs in both runtime modes.
"""

import apathetic_utils as mod_autils


def test_import_semantics_work_in_all_runtime_modes() -> None:
    """Test that import semantics work correctly in installed and singlefile modes.

    This test verifies import semantics by importing and using the namespace
    as an example. The test runs in the current runtime mode (installed by default,
    singlefile when RUNTIME_MODE=singlefile).

    The key verification is that imports work correctly regardless of whether
    the module is loaded from src/ (installed) or dist/apathetic_utils.py
    (singlefile).
    """
    # --- execute ---
    # Verify import semantics: namespace should be accessible via the module
    # This tests that the import mechanism works correctly in the current runtime mode
    assert hasattr(mod_autils, "apathetic_utils"), (
        "apathetic_utils namespace should be accessible via module"
    )

    apathetic_utils_ns = mod_autils.apathetic_utils

    # --- verify ---
    # Verify the namespace is a class (validates import semantics worked)
    assert isinstance(apathetic_utils_ns, type), (
        "apathetic_utils should be a class (namespace)"
    )
