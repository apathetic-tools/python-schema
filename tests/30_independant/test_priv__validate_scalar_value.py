# tests/0_independant/test_priv__validate_scalar_value.py
"""Smoke tests for serger.config_validate internal validator helpers."""

# we import `_` private for testing purposes only
# ruff: noqa: SLF001
# pyright: reportPrivateUsage=false

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

import apathetic_utils as mod_utils

from tests.utils import PROGRAM_PACKAGE, make_summary
from tests.utils.constants import PATCH_STITCH_HINTS


if TYPE_CHECKING:
    import pytest

# Access submodule via sys.modules (runtime_swap handles the swap transparently)
ApatheticSchema_Internal_ValidateTypedDict = sys.modules[
    "apathetic_schema.validate_typed_dict"
].ApatheticSchema_Internal_ValidateTypedDict


def test_validate_scalar_value_returns_bool() -> None:
    # --- execute ---
    result = ApatheticSchema_Internal_ValidateTypedDict._validate_scalar_value(
        strict=True,
        context="ctx",
        key="x",
        val="abc",
        expected_type=str,
        summary=make_summary(),
        field_path="root.x",
    )

    # --- verify ---
    assert isinstance(result, bool)


def test_validate_scalar_value_accepts_correct_type() -> None:
    # --- setup ---
    summary = make_summary()

    # --- patch and execute ---
    ok = ApatheticSchema_Internal_ValidateTypedDict._validate_scalar_value(
        "ctx",
        "x",
        42,
        int,
        strict=True,
        summary=summary,
        field_path="root.x",
    )

    # --- verify ---
    assert ok is True
    assert not summary.errors
    assert not summary.warnings
    assert not summary.strict_warnings


def test_validate_scalar_value_rejects_wrong_type() -> None:
    # --- setup ---
    summary = make_summary()

    # --- patch and execute ---
    ok = ApatheticSchema_Internal_ValidateTypedDict._validate_scalar_value(
        "ctx",
        "x",
        "abc",
        int,
        strict=True,
        summary=summary,
        field_path="root.x",
    )

    # --- verify ---
    assert ok is False
    assert any("expected int" in m for m in summary.errors)


def test_validate_scalar_value_handles_fallback_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If safe_isinstance raises, fallback isinstance check still works."""

    # --- setup ---
    def _fake_safe_isinstance(_value: Any, _expected_type: Any) -> bool:
        xmsg = "simulated typing bug"
        raise TypeError(xmsg)

    # --- patch and execute ---
    mod_utils.patch_everywhere(
        monkeypatch,
        mod_utils,
        "safe_isinstance",
        _fake_safe_isinstance,
        package_prefix=PROGRAM_PACKAGE,
        stitch_hints=PATCH_STITCH_HINTS,
    )
    ok = ApatheticSchema_Internal_ValidateTypedDict._validate_scalar_value(
        "ctx",
        "x",
        5,
        int,
        strict=True,
        summary=make_summary(),
        field_path="root.x",
    )

    # --- verify ---
    assert ok is True  # fallback handled correctly
