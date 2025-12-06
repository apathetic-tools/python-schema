# tests/0_independant/test_collect_msg.py

from __future__ import annotations

import apathetic_schema as amod_schema
from tests.utils import make_summary


def test_collect_msg_appends_to_errors_when_is_error_true() -> None:
    # --- setup ---
    summary = make_summary(strict=False)

    # --- execute ---
    amod_schema.collect_msg(
        strict=False,
        msg="bad thing",
        summary=summary,
        is_error=True,
    )

    # --- verify ---
    assert summary.errors == ["bad thing"]  # type: ignore[attr-defined]
    assert summary.warnings == []  # type: ignore[attr-defined]
    assert summary.strict_warnings == []  # type: ignore[attr-defined]


def test_collect_msg_appends_to_strict_warnings_when_strict() -> None:
    # --- setup ---
    summary = make_summary(strict=True)

    # --- execute ---
    amod_schema.collect_msg(
        strict=True,
        msg="be careful",
        summary=summary,
    )

    # --- verify ---
    assert summary.strict_warnings == ["be careful"]  # type: ignore[attr-defined]
    assert summary.errors == []  # type: ignore[attr-defined]
    assert summary.warnings == []  # type: ignore[attr-defined]


def test_collect_msg_appends_to_warnings_when_not_strict() -> None:
    # --- setup ---
    summary = make_summary(strict=False)

    # --- execute ---
    amod_schema.collect_msg(
        strict=False,
        msg="heads up",
        summary=summary,
    )

    # --- verify ---
    assert summary.warnings == ["heads up"]  # type: ignore[attr-defined]
    assert summary.errors == []  # type: ignore[attr-defined]
    assert summary.strict_warnings == []  # type: ignore[attr-defined]


def test_collect_msg_error_always_overrides_strict_mode() -> None:
    # --- setup ---
    summary = make_summary(strict=True)

    # --- execute ---
    amod_schema.collect_msg(
        strict=True,
        msg="kaboom",
        summary=summary,
        is_error=True,
    )

    # --- verify ---
    assert summary.errors == ["kaboom"]  # type: ignore[attr-defined]
    assert summary.strict_warnings == []  # type: ignore[attr-defined]
    assert summary.warnings == []  # type: ignore[attr-defined]
