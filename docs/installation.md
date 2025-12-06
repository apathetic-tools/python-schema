---
layout: base
title: Installation
permalink: /installation/
---

# Installation Guide

Apathetic Python Schema can be installed using several methods. Choose the one that best fits your project's needs.

## Primary Method: PyPI (Recommended)

The recommended way to install Apathetic Schema is via PyPI. We prefer `poetry` over `pip` for its `pyproject.toml` support, automatic venv management, and tool configuration without dotfiles.

### Using Poetry (Preferred)

```bash
poetry add apathetic-schema
```

### Using pip

```bash
pip install apathetic-schema
```

This installation method provides:
- Easy dependency management
- Version pinning
- Integration with your existing Python project structure

## Alternative: Stitched Distribution

For projects that prefer a stitched dependency, we also distribute a stitched `apathetic_schema.py` file that you can download directly from [releases](https://github.com/apathetic-tools/python-schema/releases).

### Download and Use

1. Download `apathetic_schema.py` from the [latest release](https://github.com/apathetic-tools/python-schema/releases)
2. Place it in your project directory
3. Import it directly:

```python
import apathetic_schema
```

This method is useful for:
- Projects that want to integrate dependencies directly into their codebase  
  *(avoiding package managers and external dependencies)*
- Embedded systems or restricted environments  
  *(including offline/air-gapped deployments)*

## Requirements

- **Python 3.10+**
- **apathetic-utils** (>=0.2.1,<2.0.0) - for `schema_from_typeddict`, `safe_isinstance`, and other utilities
- **apathetic-logging** (>=0.3.2,<2.0.0) - for logging functionality

Apathetic Python Schema has minimal runtime dependencies — it uses `apathetic-utils` for TypedDict schema extraction and type checking utilities.

## Verification

After installation, verify that it works:

```python
from apathetic_schema import apathetic_schema, ApatheticSchema_ValidationSummary
from apathetic_utils import schema_from_typeddict
from typing import TypedDict

class TestConfig(TypedDict):
    name: str

config = {"name": "test"}
summary = ApatheticSchema_ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(TestConfig)

apathetic_schema.check_schema_conformance(
    config,
    schema,
    "in test",
    strict_config=False,
    summary=summary,
)

print(f"Validation successful: {summary.valid}")
```

If the import succeeds and validation works, installation was successful!

## Next Steps

- Read the [Quick Start Guide]({{ '/quickstart' | relative_url }}) to get up and running
- Check out the [API Reference]({{ '/api' | relative_url }}) for detailed documentation
- See [Examples]({{ '/examples' | relative_url }}) for advanced usage patterns

