---
layout: base
title: API Reference
permalink: /api/
---

# API Reference

Complete API documentation for Apathetic Python Schema.

## Quick Reference

| Category | Functions & Classes |
|----------|-------------------|
| **Core Validation** | [`apathetic_schema.check_schema_conformance()`](#check_schema_conformance) |
| **Error Handling** | [`ApatheticSchema_ValidationSummary`](#validationsummary), [`ApatheticSchema_SchemaErrorAggregator`](#schemaerroraggregator), [`apathetic_schema.collect_msg()`](#collect_msg), [`apathetic_schema.flush_schema_aggregators()`](#flush_schema_aggregators) |
| **Key Warnings** | [`apathetic_schema.warn_keys_once()`](#warn_keys_once) |

## Core Validation

### check_schema_conformance

```python
apathetic_schema.check_schema_conformance(
    cfg: dict[str, Any],
    schema: dict[str, Any],
    context: str,
    *,
    strict_config: bool,
    summary: ApatheticSchema_ValidationSummary,
    prewarn: set[str] | None = None,
    ignore_keys: set[str] | None = None,
    base_path: str = "root",
    field_examples: dict[str, str] | None = None,
) -> bool
```

Validate a dict-based configuration against a TypedDict schema.

This is the main validation function that checks if a configuration dictionary conforms to a schema (typically extracted from a TypedDict using `apathetic_utils.schema_from_typeddict`).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cfg` | `dict[str, Any]` | The configuration dictionary to validate |
| `schema` | `dict[str, Any]` | The schema dictionary (from `schema_from_typeddict`) |
| `context` | `str` | Context string for error messages (e.g., "in configuration file") |
| `strict_config` | `bool` | If `True`, warnings are treated as errors |
| `summary` | `ApatheticSchema_ValidationSummary` | Validation summary object (modified in place) |
| `prewarn` | `set[str] \| None` | Set of keys to pre-warn about (default: `None`) |
| `ignore_keys` | `set[str] \| None` | Set of keys to ignore during validation (default: `None`) |
| `base_path` | `str` | Base path for field paths in error messages (default: `"root"`) |
| `field_examples` | `dict[str, str] \| None` | Examples for fields to include in error messages (default: `None`) |

**Returns:**
- `bool`: `True` if validation passed, `False` otherwise

**Example:**

```python
from apathetic_schema import apathetic_schema, ApatheticSchema_ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class AppConfig(TypedDict):
    name: str
    port: int
    debug: bool

config = {"name": "MyApp", "port": 8080, "debug": True}
summary = ApatheticSchema_ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(AppConfig)

is_valid = apathetic_schema.check_schema_conformance(
    config,
    schema,
    "in configuration file",
    strict_config=False,
    summary=summary,
)
```

## Error Handling

### ValidationSummary

```python
@dataclass
class ApatheticSchema_ValidationSummary:
    valid: bool
    errors: list[str]
    strict_warnings: list[str]
    warnings: list[str]
    strict: bool
```

A dataclass that holds the results of schema validation.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `valid` | `bool` | Whether validation passed (no errors or strict warnings) |
| `errors` | `list[str]` | List of error messages |
| `strict_warnings` | `list[str]` | List of strict warning messages (warnings in strict mode) |
| `warnings` | `list[str]` | List of warning messages |
| `strict` | `bool` | Whether strict mode was enabled |

**Example:**

```python
from apathetic_schema import ApatheticSchema_ValidationSummary

summary = ApatheticSchema_ValidationSummary(
    valid=True,
    errors=[],
    strict_warnings=[],
    warnings=[],
    strict=False
)

# After validation, check results
if not summary.valid:
    if summary.errors:
        print("Errors:", summary.errors)
    if summary.strict_warnings:
        print("Strict warnings:", summary.strict_warnings)
    if summary.warnings:
        print("Warnings:", summary.warnings)
```

### SchemaErrorAggregator

```python
ApatheticSchema_SchemaErrorAggregator = dict[str, dict[str, dict[str, _SchErrAggEntry]]]
```

A type alias for a nested dictionary structure that aggregates validation errors by severity and tag.

**Structure:**
```python
{
    "strict_warnings": {
        "tag": {
            "msg": "Error message",
            "contexts": ["context1", "context2"]
        }
    },
    "warnings": {
        ...
    }
}
```

**Example:**

```python
from apathetic_schema import ApatheticSchema_SchemaErrorAggregator

agg: ApatheticSchema_SchemaErrorAggregator = {}

# Used with warn_keys_once and flush_schema_aggregators
```

### collect_msg

```python
apathetic_schema.collect_msg(
    msg: str,
    *,
    strict: bool,
    summary: ApatheticSchema_ValidationSummary,
    is_error: bool = False,
) -> None
```

Route a validation message to the appropriate bucket in the summary.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `msg` | `str` | The message to collect |
| `strict` | `bool` | If `True`, warnings go to `strict_warnings` |
| `summary` | `ApatheticSchema_ValidationSummary` | The summary object (modified in place) |
| `is_error` | `bool` | If `True`, message is treated as an error (default: `False`) |

**Example:**

```python
from apathetic_schema import apathetic_schema, ApatheticSchema_ValidationSummary

summary = ApatheticSchema_ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)

apathetic_schema.collect_msg(
    "Unknown key 'extra' in configuration",
    strict=False,
    summary=summary,
    is_error=False
)
```

### flush_schema_aggregators

```python
apathetic_schema.flush_schema_aggregators(
    *,
    summary: ApatheticSchema_ValidationSummary,
    agg: ApatheticSchema_SchemaErrorAggregator,
) -> None
```

Flush aggregated errors from the aggregator into the summary.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `summary` | `ApatheticSchema_ValidationSummary` | The summary object (modified in place) |
| `agg` | `ApatheticSchema_SchemaErrorAggregator` | The error aggregator |

**Example:**

```python
from apathetic_schema import apathetic_schema, ApatheticSchema_ValidationSummary, ApatheticSchema_SchemaErrorAggregator

summary = ApatheticSchema_ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
agg: ApatheticSchema_SchemaErrorAggregator = {}

# ... populate agg with warn_keys_once ...

apathetic_schema.flush_schema_aggregators(summary=summary, agg=agg)
```

## Key Warnings

### warn_keys_once

```python
apathetic_schema.warn_keys_once(
    tag: str,
    bad_keys: set[str],
    cfg: dict[str, Any],
    context: str,
    msg: str,
    *,
    strict_config: bool,
    summary: ApatheticSchema_ValidationSummary,
    agg: ApatheticSchema_SchemaErrorAggregator | None,
) -> tuple[bool, set[str]]
```

Warn about specific keys once, aggregating warnings by tag.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `tag` | `str` | Tag to group warnings (e.g., "dry-run") |
| `bad_keys` | `set[str]` | Set of keys to warn about |
| `cfg` | `dict[str, Any]` | Configuration dictionary to check |
| `context` | `str` | Context string for error messages |
| `msg` | `str` | Warning message template |
| `strict_config` | `bool` | If `True`, warnings are treated as errors |
| `summary` | `ApatheticSchema_ValidationSummary` | The summary object (modified in place) |
| `agg` | `ApatheticSchema_SchemaErrorAggregator \| None` | Optional aggregator for warnings |

**Returns:**
- `tuple[bool, set[str]]`: A tuple of (is_valid, found_keys)

**Example:**

```python
from apathetic_schema import apathetic_schema, ApatheticSchema_ValidationSummary, ApatheticSchema_SchemaErrorAggregator

summary = ApatheticSchema_ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
agg: ApatheticSchema_SchemaErrorAggregator = {}

config = {"dry_run": True, "other": "value"}
bad_keys = {"dry_run"}

is_valid, found = apathetic_schema.warn_keys_once(
    "dry-run",
    bad_keys,
    config,
    "in configuration",
    "The 'dry-run' key is deprecated",
    strict_config=False,
    summary=summary,
    agg=agg,
)
```

## Integration with apathetic-utils

Apathetic Python Schema works seamlessly with `apathetic-utils` for schema extraction:

```python
from apathetic_schema import apathetic_schema, ApatheticSchema_ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class Config(TypedDict):
    name: str
    port: int

# Extract schema from TypedDict
schema = schema_from_typeddict(Config)

# Validate configuration
summary = ApatheticSchema_ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
apathetic_schema.check_schema_conformance(
    {"name": "MyApp", "port": 8080},
    schema,
    "in config",
    strict_config=False,
    summary=summary,
)
```

## Next Steps

- Read the [Quick Start Guide]({{ '/quickstart' | relative_url }}) for getting started
- Check out [Examples]({{ '/examples' | relative_url }}) for advanced usage patterns
- See [Contributing]({{ '/contributing' | relative_url }}) if you want to help improve the project
