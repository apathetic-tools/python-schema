# src/apathetic_schema/types.py
"""Type definitions for Apathetic Schema."""

from __future__ import annotations

from dataclasses import dataclass


# --- types ----------------------------------------------------------
# Import ApatheticSchema_SchemaErrorAggregator from warn_keys_once where it's defined
# (along with ApatheticSchema_SchErrAggEntry which is only used there)


"""
severity, tag

Aggregator structure example:
{
  "strict_warnings": {
      "dry-run": {"msg": DRYRUN_MSG, "contexts": ["in build #0", "in build #2"]},
      ...
  },
  "warnings": { ... }
}
"""


# --- dataclasses ------------------------------------------------------


@dataclass
class ApatheticSchema_ValidationSummary:  # noqa: N801
    """Validation summary dataclass.

    Tracks validation results including errors, warnings, and strict warnings.
    """

    valid: bool
    errors: list[str]
    strict_warnings: list[str]
    warnings: list[str]
    strict: bool  # strictness somewhere in our config?
