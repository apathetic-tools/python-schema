---
layout: base
title: Examples
permalink: /examples/
---

# Usage Examples

Advanced usage patterns and examples for Apathetic Python Schema.

## Basic Schema Validation

### Simple Configuration Validation

```python
from apathetic_schema import check_schema_conformance, ValidationSummary
from apathetic_utils import schema_from_typeddict, load_jsonc
from typing import TypedDict
from pathlib import Path

class AppConfig(TypedDict):
    name: str
    version: str
    port: int
    debug: bool

# Load configuration from JSONC
config = load_jsonc(Path("config.jsonc"))

# Validate against schema
summary = ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(AppConfig)

is_valid = check_schema_conformance(
    config,
    schema,
    "in config.jsonc",
    strict_config=False,
    summary=summary,
)

if summary.valid:
    print("Configuration is valid!")
else:
    for error in summary.errors:
        print(f"Error: {error}")
    for warning in summary.warnings:
        print(f"Warning: {warning}")
```

## Nested TypedDicts

### Complex Nested Configuration

```python
from apathetic_schema import check_schema_conformance, ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class DatabaseConfig(TypedDict):
    host: str
    port: int
    database: str
    user: str
    password: str

class LoggingConfig(TypedDict):
    level: str
    file: str

class AppConfig(TypedDict):
    name: str
    database: DatabaseConfig
    logging: LoggingConfig

config = {
    "name": "MyApp",
    "database": {
        "host": "localhost",
        "port": 5432,
        "database": "mydb",
        "user": "admin",
        "password": "secret"
    },
    "logging": {
        "level": "INFO",
        "file": "/var/log/app.log"
    }
}

summary = ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(AppConfig)

check_schema_conformance(
    config,
    schema,
    "in configuration",
    strict_config=False,
    summary=summary,
)
```

## Lists and Collections

### Lists of Primitives

```python
from apathetic_schema import check_schema_conformance, ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class ServerConfig(TypedDict):
    name: str
    ports: list[int]
    tags: list[str]

config = {
    "name": "web-server",
    "ports": [8080, 8081, 8082],
    "tags": ["web", "production", "load-balanced"]
}

summary = ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(ServerConfig)

check_schema_conformance(
    config,
    schema,
    "in configuration",
    strict_config=False,
    summary=summary,
)
```

### Lists of TypedDicts

```python
from apathetic_schema import check_schema_conformance, ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class EndpointConfig(TypedDict):
    path: str
    method: str
    handler: str

class APIConfig(TypedDict):
    base_url: str
    endpoints: list[EndpointConfig]

config = {
    "base_url": "https://api.example.com",
    "endpoints": [
        {"path": "/users", "method": "GET", "handler": "get_users"},
        {"path": "/users", "method": "POST", "handler": "create_user"},
        {"path": "/users/{id}", "method": "GET", "handler": "get_user"}
    ]
}

summary = ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(APIConfig)

check_schema_conformance(
    config,
    schema,
    "in configuration",
    strict_config=False,
    summary=summary,
)
```

## Strict Mode

### Enforcing Strict Validation

```python
from apathetic_schema import check_schema_conformance, ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class Config(TypedDict):
    name: str
    port: int

# Config with unknown keys
config = {
    "name": "MyApp",
    "port": 8080,
    "unknown_key": "value",  # This will be an error in strict mode
    "another_unknown": 123
}

summary = ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(Config)

# Strict mode treats warnings as errors
check_schema_conformance(
    config,
    schema,
    "in configuration",
    strict_config=True,  # Enable strict mode
    summary=summary,
)

if not summary.valid:
    print("Validation failed!")
    print("Errors:", summary.errors)
    print("Strict warnings:", summary.strict_warnings)
```

## Ignoring Keys

### Partial Validation

```python
from apathetic_schema import check_schema_conformance, ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class Config(TypedDict):
    name: str
    port: int
    # We'll ignore 'metadata' and 'internal' keys

config = {
    "name": "MyApp",
    "port": 8080,
    "metadata": {"created": "2024-01-01", "author": "admin"},
    "internal": {"debug": True, "trace": False}
}

summary = ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(Config)

# Ignore specific keys during validation
check_schema_conformance(
    config,
    schema,
    "in configuration",
    strict_config=False,
    summary=summary,
    ignore_keys={"metadata", "internal"},
)
```

## Error Aggregation

### Using SchemaErrorAggregator

```python
from apathetic_schema import (
    check_schema_conformance,
    ValidationSummary,
    SchemaErrorAggregator,
    warn_keys_once,
    flush_schema_aggregators,
)
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class Config(TypedDict):
    name: str
    port: int

config = {
    "name": "MyApp",
    "port": "invalid",  # Wrong type
    "dry_run": True,    # Deprecated key
}

summary = ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
agg: SchemaErrorAggregator = {}
schema = schema_from_typeddict(Config)

# Warn about deprecated keys
deprecated_keys = {"dry_run"}
warn_keys_once(
    "deprecated",
    deprecated_keys,
    config,
    "in configuration",
    "The '{key}' key is deprecated",
    strict_config=False,
    summary=summary,
    agg=agg,
)

# Validate schema
check_schema_conformance(
    config,
    schema,
    "in configuration",
    strict_config=False,
    summary=summary,
)

# Flush aggregated errors
flush_schema_aggregators(summary=summary, agg=agg)

if not summary.valid:
    print("Validation Summary:")
    if summary.errors:
        print("Errors:")
        for error in summary.errors:
            print(f"  - {error}")
    if summary.warnings:
        print("Warnings:")
        for warning in summary.warnings:
            print(f"  - {warning}")
```

## Field Examples

### Providing Field Examples for Better Errors

```python
from apathetic_schema import check_schema_conformance, ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class Config(TypedDict):
    name: str
    port: int
    mode: str

config = {
    "name": "MyApp",
    "port": "invalid",  # Should be int
    "mode": "invalid_mode"
}

# Provide examples for better error messages
field_examples = {
    "port": "8080",
    "mode": "development, production, or testing"
}

summary = ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(Config)

check_schema_conformance(
    config,
    schema,
    "in configuration",
    strict_config=False,
    summary=summary,
    field_examples=field_examples,
)

# Error messages will include examples:
# "in configuration: key `port` expected int (e.g. 8080), got str"
```

## Real-World Application

### Complete Application Configuration

```python
from apathetic_schema import check_schema_conformance, ValidationSummary
from apathetic_utils import schema_from_typeddict, load_jsonc
from typing import TypedDict, NotRequired
from pathlib import Path

class DatabaseConfig(TypedDict):
    host: str
    port: int
    database: str
    user: str
    password: str
    pool_size: NotRequired[int]

class RedisConfig(TypedDict):
    host: str
    port: int
    db: NotRequired[int]

class AppConfig(TypedDict):
    name: str
    version: str
    debug: bool
    database: DatabaseConfig
    redis: NotRequired[RedisConfig]
    workers: int
    timeout: NotRequired[int]

def load_and_validate_config(config_path: Path) -> tuple[dict, bool]:
    """Load and validate configuration file."""
    # Load config
    config = load_jsonc(config_path)
    if config is None:
        raise ValueError(f"Failed to load configuration from {config_path}")

    # Validate
    summary = ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
    schema = schema_from_typeddict(AppConfig)

    is_valid = check_schema_conformance(
        config,
        schema,
        f"in {config_path}",
        strict_config=False,
        summary=summary,
    )

    # Report results
    if not summary.valid:
        print("Configuration validation failed:")
        for error in summary.errors:
            print(f"  ERROR: {error}")
        for warning in summary.warnings:
            print(f"  WARNING: {warning}")
        return config, False

    if summary.warnings:
        print("Configuration validated with warnings:")
        for warning in summary.warnings:
            print(f"  WARNING: {warning}")

    return config, True

# Usage
config, is_valid = load_and_validate_config(Path("app.jsonc"))
if is_valid:
    print(f"Loaded configuration for {config['name']} v{config['version']}")
```

## Next Steps

- Read the [API Reference]({{ '/api' | relative_url }}) for complete documentation
- Check out the [Quick Start Guide]({{ '/quickstart' | relative_url }}) for getting started
- See [Contributing]({{ '/contributing' | relative_url }}) if you want to help improve the project
