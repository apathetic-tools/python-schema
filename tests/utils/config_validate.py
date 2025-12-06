# tests/utils/config_validate.py

from __future__ import annotations

import apathetic_schema


def make_summary(
    *,
    valid: bool = True,
    errors: list[str] | None = None,
    strict_warnings: list[str] | None = None,
    warnings: list[str] | None = None,
    strict: bool = True,
) -> apathetic_schema.ValidationSummary:  # type: ignore[valid-type]
    """Helper to create a clean ValidationSummary."""
    return apathetic_schema.ValidationSummary(
        valid=valid,
        errors=errors or [],
        strict_warnings=strict_warnings or [],
        warnings=warnings or [],
        strict=strict,
    )
