# tests/0_independant/test_collect_msg.py

from __future__ import annotations

import pytest

import apathetic_schema as amod_schema
from tests.utils import make_summary


@pytest.mark.parametrize(
    (
        "strict",
        "is_error",
        "msg",
        "expected_errors",
        "expected_warnings",
        "expected_strict_warnings",
    ),
    [
        (False, True, "bad thing", ["bad thing"], [], []),
        (True, False, "be careful", [], [], ["be careful"]),
        (False, False, "heads up", [], ["heads up"], []),
        (True, True, "kaboom", ["kaboom"], [], []),
    ],
)
def test_collect_msg_routes_to_correct_bucket(
    strict: bool,  # noqa: FBT001
    is_error: bool,  # noqa: FBT001
    msg: str,
    expected_errors: list[str],
    expected_warnings: list[str],
    expected_strict_warnings: list[str],
) -> None:
    """Test collect_msg routes messages to correct bucket based on strict mode."""
    # --- setup ---
    summary = make_summary(strict=strict)

    # --- execute ---
    amod_schema.collect_msg(
        strict=strict,
        msg=msg,
        summary=summary,
        is_error=is_error,
    )

    # --- verify ---
    assert summary.errors == expected_errors
    assert summary.warnings == expected_warnings
    assert summary.strict_warnings == expected_strict_warnings
