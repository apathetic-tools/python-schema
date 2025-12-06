# tests/0_independant/test_warn_keys_once.py
"""Tests for warn_keys_once function."""

from __future__ import annotations

from typing import cast

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


def test_warn_keys_once_with_aggregator_non_strict() -> None:
    """When agg is provided and strict=False, should aggregate warnings."""
    # --- setup ---
    summary = make_summary(strict=False)
    agg: amod_schema.ApatheticSchema_SchemaErrorAggregator = {}
    cfg = {"dry_run": True, "valid": "value"}
    bad_keys = {"dry_run"}

    # --- execute ---
    valid, found = apathetic_schema.warn_keys_once(
        tag="dry-run",
        bad_keys=bad_keys,
        cfg=cfg,
        context="in top-level configuration",
        msg="The 'dry-run' key is deprecated {ctx}",
        strict_config=False,
        summary=summary,
        agg=agg,
    )

    # --- verify ---
    assert valid is True  # non-strict mode
    assert found == {"dry_run"}
    assert "warnings" in agg
    assert "dry-run" in agg["warnings"]
    entry = cast(
        "amod_schema.ApatheticSchema_SchErrAggEntry",
        agg["warnings"]["dry-run"],
    )
    expected_msg = "The 'dry-run' key is deprecated {ctx}"
    assert entry["msg"] == expected_msg
    assert "in top-level configuration" in entry["contexts"]
    # Summary should not be modified when using aggregator
    assert not summary.warnings
    assert not summary.strict_warnings


def test_warn_keys_once_with_aggregator_strict() -> None:
    """When agg is provided and strict=True, should aggregate strict warnings."""
    # --- setup ---
    summary = make_summary(strict=True)
    agg: amod_schema.ApatheticSchema_SchemaErrorAggregator = {}
    cfg = {"dry_run": True}
    bad_keys = {"dry_run"}

    # --- execute ---
    valid, found = apathetic_schema.warn_keys_once(
        tag="dry-run",
        bad_keys=bad_keys,
        cfg=cfg,
        context="in config",
        msg="Deprecated key {keys} {ctx}",
        strict_config=True,
        summary=summary,
        agg=agg,
    )

    # --- verify ---
    assert valid is False  # strict mode makes it invalid
    assert found == {"dry_run"}
    assert "strict_warnings" in agg
    assert "dry-run" in agg["strict_warnings"]
    entry = cast(
        "amod_schema.ApatheticSchema_SchErrAggEntry",
        agg["strict_warnings"]["dry-run"],
    )
    expected_msg = "Deprecated key {keys} {ctx}"
    assert entry["msg"] == expected_msg
    assert "in config" in entry["contexts"]


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


def test_warn_keys_once_without_aggregator_non_strict() -> None:
    """When agg is None and strict=False, should add to warnings immediately."""
    # --- setup ---
    summary = make_summary(strict=False)
    cfg = {"dry_run": True, "other": "value"}
    bad_keys = {"dry_run"}

    # --- execute ---
    valid, found = apathetic_schema.warn_keys_once(
        tag="dry-run",
        bad_keys=bad_keys,
        cfg=cfg,
        context="in config",
        msg="Deprecated key {keys} found {ctx}",
        strict_config=False,
        summary=summary,
        agg=None,
    )

    # --- verify ---
    assert valid is True
    assert found == {"dry_run"}
    assert len(summary.warnings) == 1
    assert "dry_run" in summary.warnings[0]
    assert "in config" in summary.warnings[0]
    assert not summary.strict_warnings
    assert not summary.errors


def test_warn_keys_once_without_aggregator_strict() -> None:
    """When agg is None and strict=True, should add to strict_warnings immediately."""
    # --- setup ---
    summary = make_summary(strict=True)
    cfg = {"dry_run": True}
    bad_keys = {"dry_run"}

    # --- execute ---
    valid, found = apathetic_schema.warn_keys_once(
        tag="dry-run",
        bad_keys=bad_keys,
        cfg=cfg,
        context="in config",
        msg="Deprecated {keys} {ctx}",
        strict_config=True,
        summary=summary,
        agg=None,
    )

    # --- verify ---
    assert valid is False  # strict mode
    assert found == {"dry_run"}
    assert len(summary.strict_warnings) == 1
    assert "dry_run" in summary.strict_warnings[0]
    assert "in config" in summary.strict_warnings[0]
    assert not summary.warnings
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
