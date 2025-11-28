---
layout: base
title: Quick Start
permalink: /quickstart/
---

# Quick Start Guide

Get up and running with Apathetic Python Schema in minutes.

## Basic Usage

The simplest way to use Apathetic Schema is to validate a dict against a TypedDict schema:

```python
from apathetic_schema import apathetic_schema, ApatheticSchema_ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

# Define your config schema using TypedDict
class AppConfig(TypedDict):
    name: str
    version: str
    port: int
    debug: bool

# Your config data (usually loaded from JSONC/JSON/TOML)
config = {
    "name": "MyApp",
    "version": "1.0.0",
    "port": 8080,
    "debug": True
}

# Validate against TypedDict schema
summary = ApatheticSchema_ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(AppConfig)

is_valid = apathetic_schema.check_schema_conformance(
    config,
    schema,
    "in configuration file",
    strict_config=False,
    summary=summary,
)

if summary.valid:
    print("Config is valid!")
else:
    print("Validation errors:", summary.errors)
    print("Warnings:", summary.warnings)
```

## Loading Config Files

### Loading JSONC Files

JSONC (JSON with Comments) files are commonly used for configuration:

```python
from apathetic_schema import apathetic_schema, ApatheticSchema_ValidationSummary
from apathetic_utils import schema_from_typeddict, load_jsonc
from typing import TypedDict
from pathlib import Path

class Config(TypedDict):
    name: str
    port: int

# Load a JSONC file
config = load_jsonc(Path("config.jsonc"))

# Validate it
summary = ApatheticSchema_ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(Config)

apathetic_schema.check_schema_conformance(
    config,
    schema,
    "in config.jsonc",
    strict_config=False,
    summary=summary,
)
```

### Loading JSON Files

```python
import json
from pathlib import Path
from apathetic_schema import apathetic_schema, ApatheticSchema_ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class Config(TypedDict):
    name: str
    port: int

# Load a JSON file
with Path("config.json").open() as f:
    config = json.load(f)

# Validate it
summary = ApatheticSchema_ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(Config)

apathetic_schema.check_schema_conformance(
    config,
    schema,
    "in config.json",
    strict_config=False,
    summary=summary,
)
```

## Nested TypedDicts

Apathetic Schema supports nested TypedDicts for complex configurations:

```python
from apathetic_schema import apathetic_schema, ApatheticSchema_ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class DatabaseConfig(TypedDict):
    host: str
    port: int
    database: str

class AppConfig(TypedDict):
    name: str
    database: DatabaseConfig

config = {
    "name": "MyApp",
    "database": {
        "host": "localhost",
        "port": 5432,
        "database": "mydb"
    }
}

summary = ApatheticSchema_ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(AppConfig)

apathetic_schema.check_schema_conformance(
    config,
    schema,
    "in configuration",
    strict_config=False,
    summary=summary,
)
```

## List Types

Validate lists of items:

```python
from apathetic_schema import apathetic_schema, ApatheticSchema_ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class AppConfig(TypedDict):
    name: str
    tags: list[str]
    ports: list[int]

config = {
    "name": "MyApp",
    "tags": ["web", "api"],
    "ports": [8080, 8081]
}

summary = ApatheticSchema_ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(AppConfig)

apathetic_schema.check_schema_conformance(
    config,
    schema,
    "in configuration",
    strict_config=False,
    summary=summary,
)
```

## Lists of TypedDicts

Validate lists of nested objects:

```python
from apathetic_schema import apathetic_schema, ApatheticSchema_ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class ServerConfig(TypedDict):
    host: str
    port: int

class AppConfig(TypedDict):
    name: str
    servers: list[ServerConfig]

config = {
    "name": "MyApp",
    "servers": [
        {"host": "localhost", "port": 8080},
        {"host": "example.com", "port": 8081}
    ]
}

summary = ApatheticSchema_ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(AppConfig)

apathetic_schema.check_schema_conformance(
    config,
    schema,
    "in configuration",
    strict_config=False,
    summary=summary,
)
```

## Strict Mode

Enable strict mode to treat warnings as errors:

```python
from apathetic_schema import apathetic_schema, ApatheticSchema_ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class Config(TypedDict):
    name: str
    port: int

config = {
    "name": "MyApp",
    "port": 8080,
    "unknown_key": "value"  # This will be an error in strict mode
}

summary = ApatheticSchema_ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(Config)

# strict_config=True treats unknown keys as errors
apathetic_schema.check_schema_conformance(
    config,
    schema,
    "in configuration",
    strict_config=True,  # Enable strict mode
    summary=summary,
)
```

## Error Aggregation

Use `SchemaErrorAggregator` to collect and organize validation errors:

```python
from apathetic_schema import (
    apathetic_schema,
    ApatheticSchema_ValidationSummary,
    ApatheticSchema_SchemaErrorAggregator,
)
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class Config(TypedDict):
    name: str
    port: int

config = {
    "name": "MyApp",
    "port": "invalid"  # Wrong type
}

summary = ApatheticSchema_ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
agg: ApatheticSchema_SchemaErrorAggregator = {}
schema = schema_from_typeddict(Config)

apathetic_schema.check_schema_conformance(
    config,
    schema,
    "in configuration",
    strict_config=False,
    summary=summary,
)

# Flush aggregated errors
apathetic_schema.flush_schema_aggregators(summary=summary, agg=agg)

if not summary.valid:
    print("Errors:", summary.errors)
    print("Warnings:", summary.warnings)
```

## Ignoring Keys

Sometimes you want to validate only part of a config:

```python
from apathetic_schema import apathetic_schema, ApatheticSchema_ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class Config(TypedDict):
    name: str
    port: int
    # We'll ignore 'metadata' key

config = {
    "name": "MyApp",
    "port": 8080,
    "metadata": {"extra": "data"}  # This will be ignored
}

summary = ApatheticSchema_ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(Config)

apathetic_schema.check_schema_conformance(
    config,
    schema,
    "in configuration",
    strict_config=False,
    summary=summary,
    ignore_keys={"metadata"},  # Ignore this key during validation
)
```

## Next Steps

- Read the [API Reference]({{ '/api' | relative_url }}) for complete documentation
- Check out [Examples]({{ '/examples' | relative_url }}) for more advanced patterns
- See [Contributing]({{ '/contributing' | relative_url }}) if you want to help improve the project
