# tests/utils/constants.py
"""Package metadata constants for test utilities."""

from pathlib import Path


# Project root directory (tests/utils/constants.py -> project root)
PROJ_ROOT = Path(__file__).resolve().parent.parent.parent.resolve()

# Package name used for imports and module paths
PROGRAM_PACKAGE = "apathetic_schema"

# Script name for the stitched distribution
PROGRAM_SCRIPT = "apathetic_schema"

# Config file name (used by patch_everywhere for stitch detection)
PROGRAM_CONFIG = "apathetic_schema"

# Path to the bundler script (relative to project root)
# Uses the serger CLI installed in the environment, not a local bin script.
BUNDLER_SCRIPT = "serger"

# Stitch hints for patch_everywhere (paths that indicate stitched modules)
PATCH_STITCH_HINTS = {"/dist/", "stitched", f"{PROGRAM_SCRIPT}.py"}
