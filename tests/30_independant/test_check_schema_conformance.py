# tests/0_independant/test_check_schema_conformance.py
"""Focused tests for serger.config_validate._check_schema_conformance."""

from __future__ import annotations

import sys
from typing import Any, TypedDict

import pytest

import apathetic_schema as amod_schema
from tests.utils import make_summary


# Access internal classes only for testing private methods
# (runtime_swap handles the swap transparently)
ApatheticSchema_Internal_ValidateTypedDict = sys.modules[
    "apathetic_schema.validate_typed_dict"
].ApatheticSchema_Internal_ValidateTypedDict


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# --- Fixtures / Sample TypedDicts -------------------------------------------


class MiniBuild(TypedDict):
    include: list[str]
    out: str


# --- smoke -----------------------------------------------------


def test_check_schema_conformance_respects_prewarn() -> None:
    """Prewarned keys should be skipped during schema checking."""
    # --- setup ---
    schema: dict[str, Any] = {"include": list[str], "out": str}
    cfg: dict[str, Any] = {"include": ["src"], "out": "dist", "dry_run": True}
    prewarn = {"dry_run"}

    # --- execute ---
    summary = make_summary()
    ok = amod_schema.check_schema_conformance(
        cfg,
        schema,
        "ctx",
        strict_config=True,
        summary=summary,
        prewarn=prewarn,
    )

    # --- verify ---
    assert ok is True
    pool = summary.errors + summary.strict_warnings + summary.warnings
    assert not any("dry_run" in m and "unknown key" in m for m in pool)


# --- core behavior ---------------------------------------------------------


@pytest.mark.parametrize(
    ("schema", "cfg", "strict_config", "expected_valid"),
    [
        ({"foo": str, "bar": int}, {"foo": "hi", "bar": 42}, False, True),
        ({"foo": str}, {"foo": 123}, True, False),
        ({"items": list[str]}, {"items": ["a", "b", "c"]}, False, True),
        ({"items": list[str]}, {"items": ["a", 42]}, True, False),
    ],
)
def test_check_schema_conformance_simple_types(
    schema: dict[str, type[Any]],
    cfg: dict[str, Any],
    strict_config: bool,  # noqa: FBT001
    expected_valid: bool,  # noqa: FBT001
) -> None:
    """Test schema conformance with simple types and lists."""
    # --- setup ---
    summary = make_summary()

    # --- execute and validate ---
    result = amod_schema.check_schema_conformance(
        cfg,
        schema,
        "root",
        strict_config=strict_config,
        summary=summary,
    )
    assert result is expected_valid


def test_list_of_typeddict_allows_dicts() -> None:
    # --- setup ---
    schema: dict[str, type[Any]] = {"builds": list[MiniBuild]}
    cfg: dict[str, Any] = {"builds": [{"include": ["src"], "out": "dist"}]}
    summary = make_summary()

    # --- execute and validate ---
    assert (
        amod_schema.check_schema_conformance(
            cfg,
            schema,
            "root",
            strict_config=False,
            summary=summary,
        )
        is True
    )


def test_list_of_typeddict_rejects_non_dict() -> None:
    # --- setup ---
    schema: dict[str, type[Any]] = {"builds": list[MiniBuild]}
    cfg = {"builds": ["bad"]}
    summary = make_summary()

    # --- execute and validate ---
    assert (
        amod_schema.check_schema_conformance(
            cfg,
            schema,
            "root",
            strict_config=True,
            summary=summary,
        )
        is False
    )


def test_unknown_keys_fail_in_strict() -> None:
    # --- setup ---
    schema: dict[str, type[Any]] = {"foo": str}
    cfg: dict[str, Any] = {"foo": "x", "unknown": 1}
    summary = make_summary()

    # --- execute and validate ---
    assert (
        amod_schema.check_schema_conformance(
            cfg,
            schema,
            "ctx",
            strict_config=True,
            summary=summary,
        )
        is False
    )


def test_unknown_keys_warn_in_non_strict() -> None:
    # --- setup ---
    schema: dict[str, type[Any]] = {"foo": str}
    cfg: dict[str, Any] = {"foo": "x", "unknown": 1}
    summary = make_summary()

    # --- execute and validate ---
    assert (
        amod_schema.check_schema_conformance(
            cfg,
            schema,
            "ctx",
            strict_config=False,
            summary=summary,
        )
        is True
    )


def test_prewarn_keys_ignored() -> None:
    # --- setup ---
    schema: dict[str, type[Any]] = {"foo": str, "bar": int}
    cfg: dict[str, Any] = {"foo": 1, "bar": "oops"}
    summary = make_summary()

    # --- execute and validate ---
    # prewarn tells it to skip foo
    assert (
        amod_schema.check_schema_conformance(
            cfg,
            schema,
            "ctx",
            strict_config=True,
            summary=summary,
            prewarn={"foo"},
        )
        is False
    )


def test_list_of_typeddict_with_invalid_inner_type() -> None:
    # --- setup ---
    schema = {"builds": list[MiniBuild]}
    cfg: dict[str, Any] = {"builds": [{"include": [123], "out": "dist"}]}
    summary = make_summary()

    # --- execute and validate ---
    assert (
        amod_schema.check_schema_conformance(
            cfg,
            schema,
            "root",
            strict_config=True,
            summary=summary,
        )
        is False
    )


def test_extra_field_in_typeddict_strict() -> None:
    # --- setup ---
    schema = {"builds": list[MiniBuild]}
    cfg: dict[str, Any] = {
        "builds": [{"include": ["src"], "out": "dist", "weird": True}],
    }
    summary = make_summary()

    # --- execute and validate ---
    assert (
        amod_schema.check_schema_conformance(
            cfg,
            schema,
            "root",
            strict_config=True,
            summary=summary,
        )
        is False
    )
