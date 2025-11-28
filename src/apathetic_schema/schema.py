# src/apathetic_schema/schema.py
"""Schema validation functionality for Apathetic Schema.

This module provides schema validation using TypedDict-based schemas.
"""

from dataclasses import dataclass
from difflib import get_close_matches
from typing import Any, TypedDict, cast, get_args, get_origin

from apathetic_utils import (
    cast_hint,
    fnmatchcase_portable,
    plural,
    safe_isinstance,
    schema_from_typeddict,
)
from typing_extensions import NotRequired

from .constants import ApatheticSchema_Internal_Constants


# --- types ----------------------------------------------------------


class _SchErrAggEntry(TypedDict):
    msg: str
    contexts: list[str]


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
ApatheticSchema_SchemaErrorAggregator = dict[str, dict[str, dict[str, _SchErrAggEntry]]]


# --- dataclasses ------------------------------------------------------


@dataclass
class ApatheticSchema_ValidationSummary:  # noqa: N801
    valid: bool
    errors: list[str]
    strict_warnings: list[str]
    warnings: list[str]
    strict: bool  # strictness somewhere in our config?


# --- mixin class -----------------------------------------------------


class ApatheticSchema_Internal_Schema:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides schema validation functionality.

    This class contains all schema validation functions and types.
    When mixed into apathetic_schema, it provides schema validation methods.
    """

    # --- helpers --------------------------------------------------------

    @staticmethod
    def collect_msg(
        msg: str,
        *,
        strict: bool,
        summary: ApatheticSchema_ValidationSummary,  # modified in-place
        is_error: bool = False,
    ) -> None:
        """Route a message to the appropriate bucket.
        Errors are always fatal.
        Warnings may escalate to strict_warnings in strict mode.
        """
        if is_error:
            summary.errors.append(msg)
        elif strict:
            summary.strict_warnings.append(msg)
        else:
            summary.warnings.append(msg)

    @staticmethod
    def flush_schema_aggregators(
        *,
        summary: ApatheticSchema_ValidationSummary,
        agg: ApatheticSchema_SchemaErrorAggregator,
    ) -> None:
        def _clean_context(ctx: str) -> str:
            """Normalize context strings by removing leading 'in' or 'on'."""
            ctx = ctx.strip()
            for prefix in ("in ", "on "):
                if ctx.lower().startswith(prefix):
                    return ctx[len(prefix) :].strip()
            return ctx

        def _flush_one(
            bucket: dict[str, dict[str, Any]],
            *,
            strict: bool,
        ) -> None:
            for tag, entry in bucket.items():
                msg_tmpl = entry["msg"]
                contexts = [_clean_context(c) for c in entry["contexts"]]
                joined_ctx = ", ".join(contexts)
                rendered = msg_tmpl.format(keys=tag, ctx=f"in {joined_ctx}")
                ApatheticSchema_Internal_Schema.collect_msg(
                    rendered, strict=strict, summary=summary
                )
            bucket.clear()

        strict_bucket = agg.get(ApatheticSchema_Internal_Constants.AGG_STRICT_WARN, {})
        warn_bucket = agg.get(ApatheticSchema_Internal_Constants.AGG_WARN, {})

        if strict_bucket:
            summary.valid = False
            _flush_one(strict_bucket, strict=True)
        if warn_bucket:
            _flush_one(warn_bucket, strict=False)

    # ---------------------------------------------------------------------------
    # granular schema validator helpers (private and testable)
    # ---------------------------------------------------------------------------

    @staticmethod
    def _get_example_for_field(
        field_path: str,
        field_examples: dict[str, str] | None = None,
    ) -> str | None:
        """Get example for field if available in field_examples.

        Args:
        field_path: The full field path
            (e.g. "root.include" or "root.watch_interval")
        field_examples: Optional dict mapping field patterns to example values.
        If None, returns None (no examples available).
        """
        if field_examples is None:
            return None

        # First, try exact match (O(1) lookup)
        if field_path in field_examples:
            return field_examples[field_path]

        # Then try wildcard matches
        for pattern, example in field_examples.items():
            if "*" in pattern and fnmatchcase_portable(field_path, pattern):
                return example

        return None

    @staticmethod
    def _infer_type_label(
        expected_type: Any,
    ) -> str:
        """Return a readable label for logging (e.g. 'list[str]', 'BuildConfig')."""
        try:
            origin = get_origin(expected_type)
            args = get_args(expected_type)

            # Unwrap NotRequired to get the actual type
            if origin is NotRequired and args:
                return ApatheticSchema_Internal_Schema._infer_type_label(args[0])

            if origin is list and args:
                return f"list[{getattr(args[0], '__name__', repr(args[0]))}]"
            if isinstance(expected_type, type):
                return expected_type.__name__
            return str(expected_type)
        except Exception:  # noqa: BLE001
            return repr(expected_type)

    @staticmethod
    def _validate_scalar_value(
        context: str,
        key: str,
        val: Any,
        expected_type: Any,
        *,
        strict: bool,
        summary: ApatheticSchema_ValidationSummary,  # modified in-place
        field_path: str,
        field_examples: dict[str, str] | None = None,
    ) -> bool:
        """Validate a single non-container value against its expected type."""
        try:
            if safe_isinstance(val, expected_type):  # self-ref guard
                return True
        except Exception:  # noqa: BLE001
            # Defensive fallback — e.g. weird typing generics
            fallback_type = (
                expected_type
                if isinstance(expected_type, type)
                else type(expected_type)
            )
            if isinstance(val, fallback_type):
                return True

        exp_label = ApatheticSchema_Internal_Schema._infer_type_label(expected_type)
        example = ApatheticSchema_Internal_Schema._get_example_for_field(
            field_path, field_examples
        )
        exmsg = ""
        if example:
            exmsg = f" (e.g. {example})"

        msg = (
            f"{context}: key `{key}` expected {exp_label}{exmsg},"
            f" got {type(val).__name__}"
        )
        ApatheticSchema_Internal_Schema.collect_msg(
            msg, summary=summary, strict=strict, is_error=True
        )
        return False

    @staticmethod
    def _validate_list_value(
        context: str,
        key: str,
        val: Any,
        subtype: Any,
        *,
        strict: bool,
        summary: ApatheticSchema_ValidationSummary,  # modified in-place
        prewarn: set[str],
        field_path: str,
        field_examples: dict[str, str] | None = None,
    ) -> bool:
        """Validate a homogeneous list value.

        Delegates to scalar/TypedDict validators.
        """
        if not isinstance(val, list):
            exp_label = (
                f"list[{ApatheticSchema_Internal_Schema._infer_type_label(subtype)}]"
            )
            example = ApatheticSchema_Internal_Schema._get_example_for_field(
                field_path, field_examples
            )
            exmsg = ""
            if example:
                exmsg = f" (e.g. {example})"
            msg = (
                f"{context}: key `{key}` expected {exp_label}{exmsg},"
                f" got {type(val).__name__}"
            )
            ApatheticSchema_Internal_Schema.collect_msg(
                msg,
                strict=strict,
                summary=summary,
                is_error=True,
            )
            return False

        # Treat val as a real list for static type checkers
        items = cast_hint(list[Any], val)

        # Empty list → fine, nothing to check
        if not items:
            return True

        valid = True
        for i, item in enumerate(items):
            # Detect TypedDict-like subtypes
            if (
                isinstance(subtype, type)
                and hasattr(subtype, "__annotations__")
                and hasattr(subtype, "__total__")
            ):
                if not isinstance(item, dict):
                    ApatheticSchema_Internal_Schema.collect_msg(
                        f"{context}: key `{key}` #{i + 1} expected an "
                        " object with named keys for "
                        f"{subtype.__name__}, got {type(item).__name__}",
                        strict=strict,
                        summary=summary,
                        is_error=True,
                    )
                    valid = False
                    continue
                valid &= ApatheticSchema_Internal_Schema._validate_typed_dict(
                    f"{context}.{key}[{i}]",
                    item,
                    subtype,
                    strict=strict,
                    summary=summary,
                    prewarn=prewarn,
                    field_path=f"{field_path}[{i}]",
                    field_examples=field_examples,
                )
            else:
                valid &= ApatheticSchema_Internal_Schema._validate_scalar_value(
                    context,
                    f"{key}[{i}]",
                    item,
                    subtype,
                    strict=strict,
                    summary=summary,
                    field_path=f"{field_path}[{i}]",
                    field_examples=field_examples,
                )
        return valid

    @staticmethod
    def _dict_unknown_keys(
        context: str,
        val: Any,
        schema: dict[str, Any],
        *,
        strict: bool,
        summary: ApatheticSchema_ValidationSummary,  # modified in-place
        prewarn: set[str],
    ) -> bool:
        # --- Unknown keys ---
        val_dict = cast("dict[str, Any]", val)
        unknown: list[str] = [
            k for k in val_dict if k not in schema and k not in prewarn
        ]
        if unknown:
            joined = ", ".join(f"`{u}`" for u in unknown)

            location = context
            if "in top-level configuration." in location:
                location = "in " + location.split("in top-level configuration.")[-1]

            msg = f"Unknown key{plural(unknown)} {joined} {location}."

            hints: list[str] = []
            for k in unknown:
                close = get_close_matches(
                    k,
                    schema.keys(),
                    n=1,
                    cutoff=ApatheticSchema_Internal_Constants.DEFAULT_HINT_CUTOFF,
                )
                if close:
                    hints.append(f"'{k}' → '{close[0]}'")
            if hints:
                msg += "\nHint: did you mean " + ", ".join(hints) + "?"

            ApatheticSchema_Internal_Schema.collect_msg(
                msg.strip(), strict=strict, summary=summary
            )
            if strict:
                return False

        return True

    @staticmethod
    def _dict_fields(
        context: str,
        val: Any,
        schema: dict[str, Any],
        *,
        strict: bool,
        summary: ApatheticSchema_ValidationSummary,  # modified in-place
        prewarn: set[str],
        ignore_keys: set[str],
        field_path: str,
        field_examples: dict[str, str] | None = None,
    ) -> bool:
        valid = True

        for field, expected_type in schema.items():
            if field not in val or field in prewarn or field in ignore_keys:
                # Optional or missing field → not a failure
                continue

            inner_val = val[field]
            origin = get_origin(expected_type)
            args = get_args(expected_type)
            exp_label = ApatheticSchema_Internal_Schema._infer_type_label(expected_type)
            current_field_path = f"{field_path}.{field}" if field_path else field

            if origin is list:
                subtype = args[0] if args else Any
                valid &= ApatheticSchema_Internal_Schema._validate_list_value(
                    context,
                    field,
                    inner_val,
                    subtype,
                    strict=strict,
                    summary=summary,
                    prewarn=prewarn,
                    field_path=current_field_path,
                    field_examples=field_examples,
                )
            elif (
                isinstance(expected_type, type)
                and hasattr(expected_type, "__annotations__")
                and hasattr(expected_type, "__total__")
            ):
                # we don't pass ignore_keys down because
                # we don't recursively ignore these keys
                # and they have no depth syntax. Instead you
                # need to ignore the current level, then take ownership
                # and only validate what you want manually. calling validation
                # on anything that you aren't ignoring downstream.
                # rare case that is a lot of work, but keeps the rest
                # simple for now.
                if "in top-level configuration." in context:
                    location = field
                else:
                    location = f"{context}.{field}"
                valid &= ApatheticSchema_Internal_Schema._validate_typed_dict(
                    location,
                    inner_val,
                    expected_type,
                    strict=strict,
                    summary=summary,
                    prewarn=prewarn,
                    field_path=current_field_path,
                    field_examples=field_examples,
                )
            else:
                val_scalar = ApatheticSchema_Internal_Schema._validate_scalar_value(
                    context,
                    field,
                    inner_val,
                    expected_type,
                    strict=strict,
                    summary=summary,
                    field_path=current_field_path,
                    field_examples=field_examples,
                )
                if not val_scalar:
                    ApatheticSchema_Internal_Schema.collect_msg(
                        f"{context}: key `{field}` expected {exp_label}, "
                        f"got {type(inner_val).__name__}",
                        strict=strict,
                        summary=summary,
                        is_error=True,
                    )
                    valid = False

        return valid

    @staticmethod
    def _validate_typed_dict(
        context: str,
        val: Any,
        typedict_cls: type[Any],
        *,
        strict: bool,
        summary: ApatheticSchema_ValidationSummary,  # modified in-place
        prewarn: set[str],
        ignore_keys: set[str] | None = None,
        field_path: str = "",
        field_examples: dict[str, str] | None = None,
    ) -> bool:
        """Validate a dict against a TypedDict schema recursively.

        - Return False if val is not a dict
        - Recurse into its fields using _validate_scalar_value or _validate_list_value
        - Warn about unknown keys under strict=True
        """
        if ignore_keys is None:
            ignore_keys = set()

        if not isinstance(val, dict):
            ApatheticSchema_Internal_Schema.collect_msg(
                f"{context}: expected an object with named keys for"
                f" {typedict_cls.__name__}, got {type(val).__name__}",
                strict=strict,
                summary=summary,
                is_error=True,
            )
            return False

        if not hasattr(typedict_cls, "__annotations__"):
            xmsg = (
                "Internal schema invariant violated: "
                f"{typedict_cls!r} has no __annotations__."
            )
            raise AssertionError(xmsg)

        schema = schema_from_typeddict(typedict_cls)
        valid = True

        # --- walk through all the fields recursively ---
        if not ApatheticSchema_Internal_Schema._dict_fields(
            context,
            val,
            schema,
            strict=strict,
            summary=summary,
            prewarn=prewarn,
            ignore_keys=ignore_keys,
            field_path=field_path,
            field_examples=field_examples,
        ):
            valid = False

        # --- Unknown keys ---
        if not ApatheticSchema_Internal_Schema._dict_unknown_keys(
            context,
            val,
            schema,
            strict=strict,
            summary=summary,
            prewarn=prewarn,
        ):
            valid = False

        return valid

    # ---------------------------------------------------------------------------
    # granular schema validator
    # ---------------------------------------------------------------------------

    # --- warn_keys_once -------------------------------------------

    @staticmethod
    def warn_keys_once(
        tag: str,
        bad_keys: set[str],
        cfg: dict[str, Any],
        context: str,
        msg: str,
        *,
        strict_config: bool,
        summary: ApatheticSchema_ValidationSummary,  # modified in-place
        agg: ApatheticSchema_SchemaErrorAggregator | None,
    ) -> tuple[bool, set[str]]:
        """Warn once for known bad keys (e.g. dry-run, root-only).

        agg indexes are: severity, tag, msg, context (list[str])

        Returns (valid, found_keys).
        """
        valid = True

        # Normalize keys to lowercase for case-insensitive matching
        bad_keys_lower = {k.lower(): k for k in bad_keys}
        cfg_keys_lower = {k.lower(): k for k in cfg}
        found_lower = bad_keys_lower & cfg_keys_lower.keys()

        if not found_lower:
            return True, set()

        # Recover original-case keys for display
        found = {cfg_keys_lower[k] for k in found_lower}

        if agg is not None:
            # record context for later aggregation
            severity = (
                ApatheticSchema_Internal_Constants.AGG_STRICT_WARN
                if strict_config
                else ApatheticSchema_Internal_Constants.AGG_WARN
            )
            bucket = cast_hint(dict[str, _SchErrAggEntry], agg.setdefault(severity, {}))

            default_entry: _SchErrAggEntry = {"msg": msg, "contexts": []}
            entry = bucket.setdefault(tag, default_entry)
            entry["contexts"].append(context)
        else:
            # immediate fallback
            ApatheticSchema_Internal_Schema.collect_msg(
                f"{msg.format(keys=', '.join(sorted(found)), ctx=context)}",
                strict=strict_config,
                summary=summary,
            )

        if strict_config:
            valid = False

        return valid, found

    # --- check_schema_conformance --------------------

    @staticmethod
    def check_schema_conformance(
        cfg: dict[str, Any],
        schema: dict[str, Any],
        context: str,
        *,
        strict_config: bool,
        summary: ApatheticSchema_ValidationSummary,  # modified in-place
        prewarn: set[str] | None = None,
        ignore_keys: set[str] | None = None,
        base_path: str = "root",
        field_examples: dict[str, str] | None = None,
    ) -> bool:
        """Thin wrapper around _validate_typed_dict for root-level schema checks."""
        if prewarn is None:
            prewarn = set()
        if ignore_keys is None:
            ignore_keys = set()

        # Pretend schema is a TypedDict for uniformity
        class _AnonTypedDict(TypedDict):
            pass

        # Attach the schema dynamically to mimic schema_from_typeddict output
        _AnonTypedDict.__annotations__ = schema

        return ApatheticSchema_Internal_Schema._validate_typed_dict(
            context,
            cfg,
            _AnonTypedDict,
            strict=strict_config,
            summary=summary,
            prewarn=prewarn,
            ignore_keys=ignore_keys,
            field_path=base_path,
            field_examples=field_examples,
        )


# --- Module-level exports for backward compatibility ---------------------
# Export functions at module level for backward compatibility with tests.
# In standalone (stitched) mode, these exports are skipped to avoid collisions
# with __init__.py exports. In installed mode, these exports allow tests to
# import directly from the schema module.

# Check if we're in standalone mode (stitched build)
_is_standalone = globals().get("__STANDALONE__", False)

if not _is_standalone:
    # Export types and constants with shorter aliases for backward compatibility
    # (only in installed mode to avoid collisions with __init__.py in standalone)
    SchemaErrorAggregator = ApatheticSchema_SchemaErrorAggregator
    ValidationSummary = ApatheticSchema_ValidationSummary
    AGG_STRICT_WARN = ApatheticSchema_Internal_Constants.AGG_STRICT_WARN
    AGG_WARN = ApatheticSchema_Internal_Constants.AGG_WARN

    # Functions (exported from mixin class for backward compatibility)
    # Functions (exported from mixin class for backward compatibility)
    collect_msg = ApatheticSchema_Internal_Schema.collect_msg
    flush_schema_aggregators = ApatheticSchema_Internal_Schema.flush_schema_aggregators
    warn_keys_once = ApatheticSchema_Internal_Schema.warn_keys_once
    check_schema_conformance = ApatheticSchema_Internal_Schema.check_schema_conformance

# Private functions (always exported for testing, even in standalone mode)
# These don't conflict with __init__.py since they're private (start with _)
_get_example_for_field = (
    ApatheticSchema_Internal_Schema._get_example_for_field  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
)
_infer_type_label = (
    ApatheticSchema_Internal_Schema._infer_type_label  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
)
_validate_scalar_value = (
    ApatheticSchema_Internal_Schema._validate_scalar_value  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
)
_validate_list_value = (
    ApatheticSchema_Internal_Schema._validate_list_value  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
)
_dict_unknown_keys = (
    ApatheticSchema_Internal_Schema._dict_unknown_keys  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
)
_dict_fields = (
    ApatheticSchema_Internal_Schema._dict_fields  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
)
_validate_typed_dict = (
    ApatheticSchema_Internal_Schema._validate_typed_dict  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
)
