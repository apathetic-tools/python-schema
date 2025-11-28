"""Apathetic schema package."""

from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from .namespace import apathetic_schema as _apathetic_schema_class
    from .types import ApatheticSchema_ValidationSummary
    from .warn_keys_once import ApatheticSchema_SchemaErrorAggregator

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

# Export mixin classes and types directly
from .check_schema_conformance import (  # noqa: E402
    ApatheticSchema_Internal_CheckSchemaConformance,
)
from .collect_msg import ApatheticSchema_Internal_CollectMsg  # noqa: E402
from .constants import ApatheticSchema_Internal_Constants  # noqa: E402
from .flush_schema_aggregators import (  # noqa: E402
    ApatheticSchema_Internal_FlushSchemaAggregators,
)
from .types import ApatheticSchema_ValidationSummary  # noqa: E402
from .validate_typed_dict import (  # noqa: E402
    ApatheticSchema_Internal_ValidateTypedDict,
)
from .warn_keys_once import (  # noqa: E402
    ApatheticSchema_Internal_WarnKeysOnce,
    ApatheticSchema_SchemaErrorAggregator,
)


# Note: In embedded builds, __init__.py is excluded from the stitch,
# so this code never runs and no exports happen (only the class is available).
# In singlefile/installed builds, __init__.py is included, so exports happen.

__all__ = [
    "ApatheticSchema_Internal_CheckSchemaConformance",
    "ApatheticSchema_Internal_CollectMsg",
    "ApatheticSchema_Internal_Constants",
    "ApatheticSchema_Internal_FlushSchemaAggregators",
    "ApatheticSchema_Internal_ValidateTypedDict",
    "ApatheticSchema_Internal_WarnKeysOnce",
    "ApatheticSchema_SchemaErrorAggregator",
    "ApatheticSchema_ValidationSummary",
    "apathetic_schema",
]
