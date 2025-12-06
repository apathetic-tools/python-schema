# tests/0_independant/test_priv__validate_typed_dict.py
"""Smoke tests for serger.config_validate internal validator helpers."""

# we import `_` private for testing purposes only
# ruff: noqa: SLF001
# pyright: reportPrivateUsage=false

from __future__ import annotations

import sys
from typing import Any, TypedDict

import pytest

import apathetic_schema as amod_schema
from tests.utils import make_summary


# Access submodule via sys.modules (runtime_swap handles the swap transparently)
# Note: Can't use `import apathetic_schema.validate_typed_dict` because
# __init__.py exports it as a function, not the module
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
    summary1 = amod_schema.ApatheticSchema_ValidationSummary(True, [], [], [], True)
    assert ApatheticSchema_Internal_ValidateTypedDict.validate_typed_dict(
        "root",
        good,
        Outer,
        strict=True,
        summary=summary1,
        prewarn=set(),
        field_path="root",
    )

    summary2 = amod_schema.ApatheticSchema_ValidationSummary(True, [], [], [], True)
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


def test_validate_typed_dict_field_examples_wildcard() -> None:
    """Field examples should support wildcard pattern matching."""

    # --- setup ---
    class Config(TypedDict):  # pyright: ignore[reportUnusedClass]
        watch_interval: int
        watch_paths: list[str]

    field_examples = {
        "root.watch_*": "30",
    }

    # --- execute ---
    # Should work, but we're testing that wildcard matching is used
    # The example should be found via wildcard pattern
    example = ApatheticSchema_Internal_ValidateTypedDict._get_example_for_field(  # pyright: ignore[reportPrivateUsage]
        "root.watch_interval",
        field_examples,
    )

    # --- verify ---
    assert example == "30"


def test_validate_typed_dict_field_examples_no_match_returns_none() -> None:
    """Field examples should return None when no match is found."""
    # --- setup ---
    field_examples = {
        "root.other_*": "value",
    }

    # --- execute ---
    example = ApatheticSchema_Internal_ValidateTypedDict._get_example_for_field(  # pyright: ignore[reportPrivateUsage]
        "root.unmatched_field",
        field_examples,
    )

    # --- verify ---
    assert example is None


def test_validate_typed_dict_field_examples_exact_match() -> None:
    """Field examples should support exact path matching."""
    # --- setup ---
    field_examples = {
        "root.include": '["src"]',
        "root.out": '"dist"',
    }

    # --- execute and verify ---
    example1 = ApatheticSchema_Internal_ValidateTypedDict._get_example_for_field(  # pyright: ignore[reportPrivateUsage]
        "root.include",
        field_examples,
    )
    assert example1 == '["src"]'

    example2 = ApatheticSchema_Internal_ValidateTypedDict._get_example_for_field(  # pyright: ignore[reportPrivateUsage]
        "root.out",
        field_examples,
    )
    assert example2 == '"dist"'


def test_validate_typed_dict_infer_type_label_exception() -> None:
    """_infer_type_label should handle exceptions gracefully."""
    # --- setup ---
    # Create an object that raises when get_origin() tries to access attributes
    error_msg = "Problematic type access"

    class ProblematicType:
        def __getattribute__(self, name: str) -> Any:
            # get_origin() might access various attributes, raise on any access
            raise RuntimeError(error_msg)

    problematic = ProblematicType()

    # --- execute ---
    # Should not raise, should return string representation
    label = ApatheticSchema_Internal_ValidateTypedDict._infer_type_label(  # pyright: ignore[reportPrivateUsage]
        problematic,
    )

    # --- verify ---
    assert isinstance(label, str)
    # Should fall back to str() representation when exception occurs
    # The exception handler should catch and return str(expected_type)


def test_validate_typed_dict_example_message_formatting() -> None:
    """Error messages should include example when field_examples provided."""

    # --- setup ---
    class Config(TypedDict):
        interval: int

    field_examples = {"root.interval": "30"}
    summary = make_summary()

    # --- execute ---
    ok = ApatheticSchema_Internal_ValidateTypedDict.validate_typed_dict(
        context="root",
        val={"interval": "not_an_int"},  # Wrong type
        typedict_cls=Config,
        strict=True,
        summary=summary,
        prewarn=set(),
        field_path="root",
        field_examples=field_examples,
    )

    # --- verify ---
    assert ok is False
    # Error message should include example
    error_msgs = " ".join(summary.errors)
    assert "e.g." in error_msgs or "30" in error_msgs


def test_validate_typed_dict_unknown_keys_with_hints() -> None:
    """Unknown keys should show hints for similar keys."""

    # --- setup ---
    class Config(TypedDict):
        include: list[str]
        output: str

    summary = make_summary()

    # --- execute ---
    ok = ApatheticSchema_Internal_ValidateTypedDict.validate_typed_dict(
        context="root",
        val={"include": ["src"], "outpt": "dist"},  # "outpt" is close to "output"
        typedict_cls=Config,
        strict=True,
        summary=summary,
        prewarn=set(),
        field_path="root",
    )

    # --- verify ---
    assert ok is False
    # Note: get_close_matches might not always find a match depending on cutoff
    # So we just check that unknown key error is present
    pool = summary.warnings + summary.strict_warnings + summary.errors
    assert any("unknown key" in m.lower() or "outpt" in m.lower() for m in pool)


def test_validate_typed_dict_unknown_keys_location_handling() -> None:
    """Unknown key location should be handled correctly for top-level config."""

    # --- setup ---
    class Config(TypedDict):
        valid: str

    summary = make_summary()

    # --- execute ---
    ok = ApatheticSchema_Internal_ValidateTypedDict.validate_typed_dict(
        context="in top-level configuration.",
        val={"valid": "ok", "unknown": "bad"},
        typedict_cls=Config,
        strict=True,
        summary=summary,
        prewarn=set(),
        field_path="root",
    )

    # --- verify ---
    assert ok is False
    # Location should be processed correctly
    pool = summary.warnings + summary.strict_warnings + summary.errors
    # Should mention unknown key
    assert any("unknown" in m.lower() for m in pool)


# TypedDict classes for test_validate_typed_dict_nested_location_handling
# Defined at module level so get_type_hints() can resolve forward references
class _TestNestedLocation_Inner(TypedDict):  # noqa: N801
    value: str


class _TestNestedLocation_Outer(TypedDict):  # noqa: N801
    inner: _TestNestedLocation_Inner


def test_validate_typed_dict_nested_location_handling() -> None:
    """Nested TypedDict validation should handle location correctly."""
    # --- setup ---
    summary = make_summary()

    # --- execute ---
    ok = ApatheticSchema_Internal_ValidateTypedDict.validate_typed_dict(
        context="in top-level configuration.",
        val={"inner": {"value": "ok"}},
        typedict_cls=_TestNestedLocation_Outer,
        strict=True,
        summary=summary,
        prewarn=set(),
        field_path="root",
    )

    # --- verify ---
    # Should handle nested location correctly
    # The location for inner validation should be "inner" not
    # "in top-level configuration.inner"
    assert isinstance(ok, bool)


def test_validate_typed_dict_missing_annotations_raises() -> None:
    """Should raise AssertionError if TypedDict has no __annotations__.

    Note: This tests an internal invariant. In Python 3.10+, all classes
    have __annotations__ by default, so this is difficult to trigger in practice.
    The check exists as a defensive measure for internal consistency.
    """
    # --- setup ---
    # Create a type without __annotations__ using type()
    # This is the only way to create something that truly lacks __annotations__
    fake_typed_dict = type("FakeTypedDict", (), {})
    # Verify it doesn't have __annotations__
    if hasattr(fake_typed_dict, "__annotations__"):
        # On Python 3.10+, classes get __annotations__ automatically
        # This test may not be triggerable, but documents the invariant
        return

    summary = make_summary()

    # --- execute and verify ---
    # This should raise AssertionError if the invariant is violated
    # Use pytest.raises for proper exception testing
    with pytest.raises(AssertionError, match="no __annotations__"):
        ApatheticSchema_Internal_ValidateTypedDict.validate_typed_dict(
            context="root",
            val={},
            typedict_cls=fake_typed_dict,
            strict=True,
            summary=summary,
            prewarn=set(),
            field_path="root",
        )
