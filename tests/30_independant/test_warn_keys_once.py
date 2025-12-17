# tests/0_independant/test_warn_keys_once.py
"""Tests for warn_keys_once function."""

from __future__ import annotations

from typing import Any, cast

import pytest

import apathetic_schema as amod_schema
from tests.utils import make_summary


# Get the namespace class
apathetic_schema = amod_schema.apathetic_schema


def test_warn_keys_once_no_bad_keys() -> None:
    """When no bad keys are found, should return valid=True and empty set."""
    # --- setup ---
    summary = make_summary()
    cfg = {"valid_key": "value", "another": 123}
    bad_keys = {"bad_key", "deprecated"}

    # --- execute ---
    valid, found = apathetic_schema.warn_keys_once(
        tag="test",
        bad_keys=bad_keys,
        cfg=cfg,
        context="test context",
        msg="Bad key {keys} found {ctx}",
        strict_config=False,
        summary=summary,
        agg=None,
    )

    # --- verify ---
    assert valid is True
    assert found == set()
    assert not summary.warnings
    assert not summary.strict_warnings
    assert not summary.errors


@pytest.mark.parametrize(
    (
        "strict_config",
        "summary_strict",
        "expected_valid",
        "expected_agg_key",
        "expected_summary_warnings",
        "expected_summary_strict_warnings",
    ),
    [
        (False, False, True, "warnings", [], []),
        (True, True, False, "strict_warnings", [], []),
    ],
)
def test_warn_keys_once_with_aggregator(
    strict_config: bool,  # noqa: FBT001
    summary_strict: bool,  # noqa: FBT001
    expected_valid: bool,  # noqa: FBT001
    expected_agg_key: str,
    expected_summary_warnings: list[str],
    expected_summary_strict_warnings: list[str],
) -> None:
    """When agg is provided, should aggregate warnings/strict_warnings."""
    # --- setup ---
    summary = make_summary(strict=summary_strict)
    agg: amod_schema.ApatheticSchema_SchemaErrorAggregator = {}
    cfg = {"dry_run": True, "valid": "value"}
    bad_keys = {"dry_run"}
    context = "in top-level configuration" if not strict_config else "in config"
    msg = (
        "The 'dry-run' key is deprecated {ctx}"
        if not strict_config
        else "Deprecated key {keys} {ctx}"
    )

    # --- execute ---
    valid, found = apathetic_schema.warn_keys_once(
        tag="dry-run",
        bad_keys=bad_keys,
        cfg=cfg,
        context=context,
        msg=msg,
        strict_config=strict_config,
        summary=summary,
        agg=agg,
    )

    # --- verify ---
    assert valid is expected_valid
    assert found == {"dry_run"}
    assert expected_agg_key in agg
    assert "dry-run" in agg[expected_agg_key]
    entry = cast(
        "amod_schema.ApatheticSchema_SchErrAggEntry",
        agg[expected_agg_key]["dry-run"],
    )
    assert entry["msg"] == msg
    assert context in entry["contexts"]
    # Summary should not be modified when using aggregator
    assert summary.warnings == expected_summary_warnings
    assert summary.strict_warnings == expected_summary_strict_warnings


def test_warn_keys_once_with_aggregator_multiple_contexts() -> None:
    """Aggregator should collect multiple contexts for the same tag."""
    # --- setup ---
    summary = make_summary()
    agg: amod_schema.ApatheticSchema_SchemaErrorAggregator = {}
    bad_keys = {"dry_run"}

    # --- execute ---
    # First call
    apathetic_schema.warn_keys_once(
        tag="dry-run",
        bad_keys=bad_keys,
        cfg={"dry_run": True},
        context="context1",
        msg="Message {ctx}",
        strict_config=False,
        summary=summary,
        agg=agg,
    )

    # Second call with same tag
    apathetic_schema.warn_keys_once(
        tag="dry-run",
        bad_keys=bad_keys,
        cfg={"dry_run": False},
        context="context2",
        msg="Message {ctx}",
        strict_config=False,
        summary=summary,
        agg=agg,
    )

    # --- verify ---
    entry = cast(
        "amod_schema.ApatheticSchema_SchErrAggEntry",
        agg["warnings"]["dry-run"],
    )
    expected_context_count = 2
    assert len(entry["contexts"]) == expected_context_count
    assert "context1" in entry["contexts"]
    assert "context2" in entry["contexts"]


@pytest.mark.parametrize(
    (
        "strict_config",
        "summary_strict",
        "expected_valid",
        "expected_warnings_count",
        "expected_strict_warnings_count",
    ),
    [
        (False, False, True, 1, 0),
        (True, True, False, 0, 1),
    ],
)
def test_warn_keys_once_without_aggregator(
    strict_config: bool,  # noqa: FBT001
    summary_strict: bool,  # noqa: FBT001
    expected_valid: bool,  # noqa: FBT001
    expected_warnings_count: int,
    expected_strict_warnings_count: int,
) -> None:
    """When agg is None, should add to warnings/strict_warnings immediately."""
    # --- setup ---
    summary = make_summary(strict=summary_strict)
    cfg: dict[str, Any] = {"dry_run": True, "other": "value"}
    bad_keys = {"dry_run"}
    msg = (
        "Deprecated key {keys} found {ctx}"
        if not strict_config
        else "Deprecated {keys} {ctx}"
    )

    # --- execute ---
    valid, found = apathetic_schema.warn_keys_once(
        tag="dry-run",
        bad_keys=bad_keys,
        cfg=cfg,
        context="in config",
        msg=msg,
        strict_config=strict_config,
        summary=summary,
        agg=None,
    )

    # --- verify ---
    assert valid is expected_valid
    assert found == {"dry_run"}
    assert len(summary.warnings) == expected_warnings_count
    assert len(summary.strict_warnings) == expected_strict_warnings_count
    if expected_warnings_count > 0:
        assert "dry_run" in summary.warnings[0]
        assert "in config" in summary.warnings[0]
    if expected_strict_warnings_count > 0:
        assert "dry_run" in summary.strict_warnings[0]
        assert "in config" in summary.strict_warnings[0]
    assert not summary.errors


def test_warn_keys_once_case_insensitive_matching() -> None:
    """Should match keys case-insensitively but preserve original case."""
    # --- setup ---
    summary = make_summary()
    # Test that lowercase bad_key matches uppercase cfg key
    cfg = {"DRY_RUN": True, "valid": "value"}
    bad_keys = {"dry_run"}  # Lowercase

    # --- execute ---
    _valid, found = apathetic_schema.warn_keys_once(
        tag="test",
        bad_keys=bad_keys,
        cfg=cfg,
        context="test",
        msg="Found {keys} {ctx}",
        strict_config=False,
        summary=summary,
        agg=None,
    )

    # --- verify ---
    # Should find match case-insensitively and preserve original case from cfg
    assert found == {"DRY_RUN"}  # Original case from cfg preserved
    assert len(summary.warnings) == 1
    msg = summary.warnings[0]
    assert "DRY_RUN" in msg  # Original case should appear in message


def test_warn_keys_once_multiple_bad_keys() -> None:
    """Should find and report multiple bad keys."""
    # --- setup ---
    summary = make_summary()
    cfg = {"dry_run": True, "deprecated": "value", "valid": "ok"}
    bad_keys = {"dry_run", "deprecated"}

    # --- execute ---
    _valid, found = apathetic_schema.warn_keys_once(
        tag="test",
        bad_keys=bad_keys,
        cfg=cfg,
        context="test",
        msg="Found {keys} {ctx}",
        strict_config=False,
        summary=summary,
        agg=None,
    )

    # --- verify ---
    assert found == {"dry_run", "deprecated"}
    assert len(summary.warnings) == 1
    msg = summary.warnings[0]
    # Keys should be sorted in message
    assert "dry_run" in msg or "deprecated" in msg


def test_warn_keys_once_message_formatting() -> None:
    """Message should be formatted with keys and context placeholders."""
    # --- setup ---
    summary = make_summary()
    cfg = {"bad": True}
    bad_keys = {"bad"}

    # --- execute ---
    apathetic_schema.warn_keys_once(
        tag="test",
        bad_keys=bad_keys,
        cfg=cfg,
        context="in my config",
        msg="Key {keys} found {ctx}",
        strict_config=False,
        summary=summary,
        agg=None,
    )

    # --- verify ---
    assert len(summary.warnings) == 1
    msg = summary.warnings[0]
    assert "bad" in msg
    assert "in my config" in msg
    # Should be formatted, not contain literal {keys} or {ctx}
    assert "{keys}" not in msg
    assert "{ctx}" not in msg
