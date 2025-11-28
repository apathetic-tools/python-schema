"""Apathetic schema package."""

from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from .namespace import apathetic_schema as _apathetic_schema_class
    from .schema import (
        ApatheticSchema_SchemaErrorAggregator,
        ApatheticSchema_ValidationSummary,
    )

# Get reference to the namespace class
# In stitched mode: class is already defined in namespace.py (executed before this)
# In installed mode: import from namespace module
_apathetic_schema_is_standalone = globals().get("__STANDALONE__", False)

if _apathetic_schema_is_standalone:
    # Stitched mode: class already defined in namespace.py
    # Get reference to the class (it's already in globals from namespace.py)
    _apathetic_schema_raw = globals().get("apathetic_schema")
    if _apathetic_schema_raw is None:
        # Fallback: should not happen, but handle gracefully
        msg = "apathetic_schema class not found in standalone mode"
        raise RuntimeError(msg)
    # Type cast to help mypy understand this is the apathetic_schema class
    # The import gives us type[apathetic_schema], so cast to
    # type[_apathetic_schema_class]
    apathetic_schema = cast("type[_apathetic_schema_class]", _apathetic_schema_raw)
else:
    # Installed mode: import from namespace module
    # This block is only executed in installed mode, not in standalone builds
    from .namespace import apathetic_schema

    # Ensure the else block is not empty (build script may remove import)
    _ = apathetic_schema

# Import types from schema module
# Note: This import is after the namespace setup to avoid circular imports
# Import constants from constants module
from .constants import ApatheticSchema_Internal_Constants  # noqa: E402
from .schema import (  # noqa: E402
    ApatheticSchema_SchemaErrorAggregator,
    ApatheticSchema_ValidationSummary,
)


# Export with shorter names for backward compatibility
SchemaErrorAggregator = ApatheticSchema_SchemaErrorAggregator
ValidationSummary = ApatheticSchema_ValidationSummary
AGG_STRICT_WARN = ApatheticSchema_Internal_Constants.AGG_STRICT_WARN
AGG_WARN = ApatheticSchema_Internal_Constants.AGG_WARN


# Export all namespace items for convenience
# These are aliases to apathetic_schema.*

# Note: In embedded builds, __init__.py is excluded from the stitch,
# so this code never runs and no exports happen (only the class is available).
# In singlefile/installed builds, __init__.py is included, so exports happen.

# Schema validation functions
check_schema_conformance = apathetic_schema.check_schema_conformance
collect_msg = apathetic_schema.collect_msg
flush_schema_aggregators = apathetic_schema.flush_schema_aggregators
warn_keys_once = apathetic_schema.warn_keys_once


__all__ = [
    "AGG_STRICT_WARN",
    "AGG_WARN",
    "SchemaErrorAggregator",
    "ValidationSummary",
    "apathetic_schema",
    "check_schema_conformance",
    "collect_msg",
    "flush_schema_aggregators",
    "warn_keys_once",
]
