# src/apathetic_schema/namespace.py
"""Shared Apathetic Schema namespace implementation.

This namespace class provides a structure to minimize global namespace pollution
when the library is embedded in a stitched script.
"""

from __future__ import annotations

from .constants import (
    ApatheticSchema_Internal_Constants,
)
from .schema import (
    ApatheticSchema_Internal_Schema,
)


# --- Apathetic Schema Namespace -------------------------------------------


class apathetic_schema(  # noqa: N801
    ApatheticSchema_Internal_Constants,
    ApatheticSchema_Internal_Schema,
):
    """Namespace for apathetic schema functionality.

    All schema validation functionality is accessed via this namespace class to
    minimize global namespace pollution when the library is embedded in a
    stitched script.
    """


# Note: All exports are handled in __init__.py
# - For library builds (installed/singlefile): __init__.py is included, exports happen
# - For embedded builds: __init__.py is excluded, no exports (only class available)
