# tests/0_independant/test_flush_schema_aggregators.py

from typing import TYPE_CHECKING, cast

from apathetic_schema.constants import ApatheticSchema_Internal_Constants
from apathetic_schema.flush_schema_aggregators import (
    ApatheticSchema_Internal_FlushSchemaAggregators,
)
from tests.utils import make_summary


if TYPE_CHECKING:
    from apathetic_schema.warn_keys_once import ApatheticSchema_SchemaErrorAggregator


def test_flush_schema_aggregators_flushes_strict_bucket() -> None:
    # --- setup ---
    summary = make_summary(strict=True)
    agg: ApatheticSchema_SchemaErrorAggregator = cast(
        "ApatheticSchema_SchemaErrorAggregator",
        {
            ApatheticSchema_Internal_Constants.AGG_STRICT_WARN: {
                "dry-run": {
                    "msg": "Ignored config key(s) {keys} {ctx}",
                    "contexts": ["in build #1", "on build #2"],
                },
            },
        },
    )

    # --- execute ---
    ApatheticSchema_Internal_FlushSchemaAggregators.flush_schema_aggregators(
        summary=summary, agg=agg
    )

    # --- verify ---
    # bucket should be cleared
    assert not agg[ApatheticSchema_Internal_Constants.AGG_STRICT_WARN]
    assert summary.valid is False
    assert len(summary.strict_warnings) == 1
    msg = summary.strict_warnings[0]
    assert "dry-run" in msg
    assert "build #1" in msg
    assert "build #2" in msg
    assert "Ignored config key(s)" in msg


def test_flush_schema_aggregators_flushes_warning_bucket() -> None:
    # --- setup ---
    summary = make_summary(strict=False)
    agg: ApatheticSchema_SchemaErrorAggregator = cast(
        "ApatheticSchema_SchemaErrorAggregator",
        {
            ApatheticSchema_Internal_Constants.AGG_WARN: {
                "root-only": {
                    "msg": "Ignored {keys} {ctx}",
                    "contexts": ["in top-level configuration"],
                },
            },
        },
    )

    # --- execute ---
    ApatheticSchema_Internal_FlushSchemaAggregators.flush_schema_aggregators(
        summary=summary, agg=agg
    )

    # --- verify ---
    assert not agg[ApatheticSchema_Internal_Constants.AGG_WARN]
    assert summary.valid is True
    assert summary.warnings == ["Ignored root-only in top-level configuration"]
    assert summary.strict_warnings == []
    assert summary.errors == []


def test_flush_schema_aggregators_cleans_context_prefixes() -> None:
    # --- setup ---
    summary = make_summary(strict=True)
    agg: ApatheticSchema_SchemaErrorAggregator = cast(
        "ApatheticSchema_SchemaErrorAggregator",
        {
            ApatheticSchema_Internal_Constants.AGG_STRICT_WARN: {
                "noop": {
                    "msg": "Ignored {keys} {ctx}",
                    "contexts": ["in build #3", "on build #4", "build #5"],
                },
            },
        },
    )

    # --- execute ---
    ApatheticSchema_Internal_FlushSchemaAggregators.flush_schema_aggregators(
        summary=summary, agg=agg
    )

    # --- verify ---
    assert not agg[ApatheticSchema_Internal_Constants.AGG_STRICT_WARN]
    msg = summary.strict_warnings[0]
    # Context prefixes 'in' and 'on' should not be duplicated
    assert msg == "Ignored noop in build #3, build #4, build #5"
