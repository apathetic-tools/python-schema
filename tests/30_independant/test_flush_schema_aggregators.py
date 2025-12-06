# tests/0_independant/test_flush_schema_aggregators.py

from __future__ import annotations

from typing import cast

import apathetic_schema as amod_schema
from tests.utils import make_summary


def test_flush_schema_aggregators_flushes_strict_bucket() -> None:
    # --- setup ---
    summary = make_summary(strict=True)
    agg: amod_schema.SchemaErrorAggregator = cast(
        "amod_schema.SchemaErrorAggregator",
        {
            amod_schema.AGG_STRICT_WARN: {
                "dry-run": {
                    "msg": "Ignored config key(s) {keys} {ctx}",
                    "contexts": ["in build #1", "on build #2"],
                },
            },
        },
    )

    # --- execute ---
    amod_schema.flush_schema_aggregators(
        summary=summary,
        agg=agg,
    )

    # --- verify ---
    # bucket should be cleared
    assert not agg[amod_schema.AGG_STRICT_WARN]
    assert summary.valid is False  # type: ignore[attr-defined]
    assert len(summary.strict_warnings) == 1  # type: ignore[attr-defined]
    msg = summary.strict_warnings[0]  # type: ignore[attr-defined]
    assert "dry-run" in msg
    assert "build #1" in msg
    assert "build #2" in msg
    assert "Ignored config key(s)" in msg


def test_flush_schema_aggregators_flushes_warning_bucket() -> None:
    # --- setup ---
    summary = make_summary(strict=False)
    agg: amod_schema.SchemaErrorAggregator = cast(
        "amod_schema.SchemaErrorAggregator",
        {
            amod_schema.AGG_WARN: {
                "root-only": {
                    "msg": "Ignored {keys} {ctx}",
                    "contexts": ["in top-level configuration"],
                },
            },
        },
    )

    # --- execute ---
    amod_schema.flush_schema_aggregators(
        summary=summary,
        agg=agg,
    )

    # --- verify ---
    assert not agg[amod_schema.AGG_WARN]
    assert summary.valid is True  # type: ignore[attr-defined]
    assert summary.warnings == ["Ignored root-only in top-level configuration"]  # type: ignore[attr-defined]
    assert summary.strict_warnings == []  # type: ignore[attr-defined]
    assert summary.errors == []  # type: ignore[attr-defined]


def test_flush_schema_aggregators_cleans_context_prefixes() -> None:
    # --- setup ---
    summary = make_summary(strict=True)
    agg: amod_schema.SchemaErrorAggregator = cast(
        "amod_schema.SchemaErrorAggregator",
        {
            amod_schema.AGG_STRICT_WARN: {
                "noop": {
                    "msg": "Ignored {keys} {ctx}",
                    "contexts": ["in build #3", "on build #4", "build #5"],
                },
            },
        },
    )

    # --- execute ---
    amod_schema.flush_schema_aggregators(
        summary=summary,
        agg=agg,
    )

    # --- verify ---
    assert not agg[amod_schema.AGG_STRICT_WARN]
    msg = summary.strict_warnings[0]  # type: ignore[attr-defined]
    # Context prefixes 'in' and 'on' should not be duplicated
    assert msg == "Ignored noop in build #3, build #4, build #5"
