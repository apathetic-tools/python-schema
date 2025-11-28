# tests/0_independant/test_validate_typed_dict.py
"""Tests for validate_typed_dict function."""

from typing import Any, TypedDict

from apathetic_schema.types import ApatheticSchema_ValidationSummary
from apathetic_schema.validate_typed_dict import (
    ApatheticSchema_Internal_ValidateTypedDict,
)
from tests.utils import make_summary


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# --- Fixtures / Sample TypedDicts -------------------------------------------


class MiniBuild(TypedDict):
    include: list[str]
    out: str


def test_validate_typed_dict_accepts_dict() -> None:
    # --- execute ---
    result = ApatheticSchema_Internal_ValidateTypedDict.validate_typed_dict(
        context="root",
        val={"include": ["src"], "out": "dist"},
        typedict_cls=MiniBuild,
        strict=True,
        summary=make_summary(),
        prewarn=set(),
        field_path="root",
    )

    # --- verify ---
    assert isinstance(result, bool)


def test_validate_typed_dict_rejects_non_dict() -> None:
    # --- setup ---
    summary = make_summary()

    # --- patch and execute ---
    ok = ApatheticSchema_Internal_ValidateTypedDict.validate_typed_dict(
        "root",
        "notadict",
        MiniBuild,
        strict=True,
        summary=summary,
        prewarn=set(),
        field_path="root",
    )

    # --- verify ---
    assert ok is False
    assert any("expected an object" in m for m in summary.errors)


def test_validate_typed_dict_detects_unknown_keys() -> None:
    # --- setup ---
    summary = make_summary()

    # --- patch and execute ---
    ok = ApatheticSchema_Internal_ValidateTypedDict.validate_typed_dict(
        "root",
        {"include": ["x"], "out": "y", "weird": 1},
        MiniBuild,
        strict=True,
        summary=summary,
        prewarn=set(),
        field_path="root",
    )

    # --- verify ---
    assert ok is False
    # unknown keys appear as warnings (or strict_warnings if strict=True)
    pool = summary.warnings + summary.strict_warnings + summary.errors
    assert any("unknown key" in m.lower() for m in pool)


def test_validate_typed_dict_allows_missing_field() -> None:
    """Missing field should not cause failure."""
    # --- setup ---
    val = {"out": "dist"}  # 'include' missing

    # --- execute ---
    ok = ApatheticSchema_Internal_ValidateTypedDict.validate_typed_dict(
        "ctx",
        val,
        MiniBuild,
        strict=True,
        summary=make_summary(),
        prewarn=set(),
        field_path="root",
    )

    # --- verify ---
    assert ok is True


def test_validate_typed_dict_nested_recursion() -> None:
    """Nested TypedDict structures should validate recursively."""

    # --- setup ---
    class Outer(TypedDict):
        inner: MiniBuild

    good: Outer = {"inner": {"include": ["src"], "out": "dist"}}
    bad: Outer = {"inner": {"include": [123], "out": "dist"}}  # type: ignore[list-item]

    # --- patch, execute and verify ---
    summary1 = ApatheticSchema_ValidationSummary(True, [], [], [], True)
    assert ApatheticSchema_Internal_ValidateTypedDict.validate_typed_dict(
        "root",
        good,
        Outer,
        strict=True,
        summary=summary1,
        prewarn=set(),
        field_path="root",
    )

    summary2 = ApatheticSchema_ValidationSummary(True, [], [], [], True)
    assert not ApatheticSchema_Internal_ValidateTypedDict.validate_typed_dict(
        "root",
        bad,
        Outer,
        strict=True,
        summary=summary2,
        prewarn=set(),
        field_path="root",
    )
    assert summary2.errors  # collected from inner validation


def test_validate_typed_dict_respects_prewarn() -> None:
    """Keys in prewarn set should be skipped and not trigger unknown-key messages."""
    # --- setup ---
    cfg: dict[str, Any] = {"include": ["src"], "out": "dist", "dry_run": True}
    prewarn = {"dry_run"}
    summary = make_summary()

    # --- execute ---
    ok = ApatheticSchema_Internal_ValidateTypedDict.validate_typed_dict(
        "ctx",
        cfg,
        MiniBuild,
        strict=True,
        summary=summary,
        prewarn=prewarn,
        field_path="root",
    )

    # --- verify ---
    assert ok is True
    pool = summary.errors + summary.strict_warnings + summary.warnings
    assert not any("dry_run" in m and "unknown key" in m for m in pool)
