---
layout: base
title: Home
permalink: /
---

# Apathetic Python Schema 🧩

**Lightweight validation for dict-based configs.**  
*Types can be schema too.*

*Apathetic Python Schema* validates dict-based data structures (configs, usually from JSONC/JSON/TOML) using Python TypedDicts used for mypy/pyright. No need for separate schema definitions — your type annotations are your schema.

## Features
- 🧩 **TypedDict validation** — Validate dict-based configs using Python TypedDicts
- 📋 **Recursive validation** — Supports nested TypedDicts and list types
- ⚠️ **Error aggregation** — Collect and report validation errors and warnings
- 🎯 **Strict mode** — Optional strict validation that treats warnings as errors
- 🔧 **Type-aware** — Works with mypy/pyright type annotations
- 🪶 **Minimal dependencies** — Only requires `apathetic-utils`
- 📝 **Helpful errors** — Provides context and suggestions for validation failures

## Quick Example

```python
from apathetic_schema import check_schema_conformance, ValidationSummary
from apathetic_utils import schema_from_typeddict, load_jsonc
from typing import TypedDict
from pathlib import Path

# Define your config schema using TypedDict
class AppConfig(TypedDict):
    name: str
    version: str
    port: int
    debug: bool

# Load config from JSONC
config = load_jsonc(Path("config.jsonc"))

# Validate against TypedDict schema
summary = ValidationSummary(valid=True, errors=[], strict_warnings=[], warnings=[], strict=False)
schema = schema_from_typeddict(AppConfig)

is_valid = check_schema_conformance(
    config,
    schema,
    "in configuration file",
    strict_config=False,
    summary=summary,
)

if not summary.valid:
    print("Validation errors:", summary.errors)
    print("Warnings:", summary.warnings)
```

## Requirements

- **Python 3.10+**
- **apathetic-utils** (>=0.2.1,<2.0.0) - for `schema_from_typeddict`, `safe_isinstance`, and other utilities

## Installation

Install via **poetry** or **pip**:

```bash
# Using poetry
poetry add apathetic-schema

# Using pip
pip install apathetic-schema
```

For alternative installation methods, see the [Installation Guide]({{ '/installation' | relative_url }}).

## Documentation

- **[Installation Guide]({{ '/installation' | relative_url }})** — How to install and set up
- **[Quick Start]({{ '/quickstart' | relative_url }})** — Get up and running in minutes
- **[API Reference]({{ '/api' | relative_url }})** — Complete API documentation
- **[Examples]({{ '/examples' | relative_url }})** — Advanced usage examples
- **[Contributing]({{ '/contributing' | relative_url }})** — How to contribute

## License

[MIT-a-NOAI License](https://github.com/apathetic-tools/python-schema/blob/main/LICENSE)

You're free to use, copy, and modify the library under the standard MIT terms.  
The additional rider simply requests that this project not be used to train or fine-tune AI/ML systems until the author deems fair compensation frameworks exist.  
Normal use, packaging, and redistribution for human developers are unaffected.

## Resources

- 📘 [Roadmap](https://github.com/apathetic-tools/python-schema/blob/main/ROADMAP.md)
- 📝 [Release Notes](https://github.com/apathetic-tools/python-schema/releases)
- 🐛 [Issue Tracker](https://github.com/apathetic-tools/python-schema/issues)
- 💬 [Discord](https://discord.gg/PW6GahZ7)

