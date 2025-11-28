<!-- DECISIONS.md -->
# DECISIONS.md

A record of major design and implementation choices in **serger** — what was considered, what was chosen, and why.

Each decision:

- Is **atomic** — focused on one clear choice.  
- Is **rationale-driven** — the “why” matters more than the “what.”  
- Should be written as if explaining it to your future self — concise, readable, and honest.  
- Includes **Context**, **Options Considered**, **Decision**, and **Consequences**.  

For formatting guidelines, see the [DECISIONS.md Style Guide](./DECISIONS_STYLE_GUIDE.md).

---


## 🚀 Adopt `python-semantic-release` for PyPI and GitHub Releases
<a id="dec16"></a>*DEC 16 — 2025-11-24*

### Context

Managing releases involves coordinating multiple steps: version bumping, changelog generation, PyPI publishing, and GitHub release creation.  
Manual release workflows are error-prone and time-consuming — especially when maintaining consistency across version numbers, release notes, and distribution artifacts.  
The project needed an **automated, convention-driven approach** that reduces manual steps while ensuring reliable, reproducible releases.

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **`python-semantic-release`** | ✅ Automated versioning from conventional commits<br>✅ Generates changelogs automatically<br>✅ Handles PyPI and GitHub releases in one workflow<br>✅ Integrates with CI/CD pipelines<br>✅ Reduces human error in version management | ⚠️ Requires adopting conventional commit format<br>⚠️ Less control over exact release timing |
| **Manual versioning + `twine`** | ✅ Full control over version and release timing<br>✅ Simple and transparent | ❌ Error-prone manual coordination<br>❌ Time-consuming for each release<br>❌ Risk of version mismatches between files |
| **`bump2version` + manual releases** | ✅ Automated version bumping<br>✅ Works with existing workflows | ❌ Still requires manual changelog and release creation<br>❌ Doesn't integrate PyPI and GitHub releases |
| **GitHub Actions only** | ✅ Native GitHub integration | ❌ Requires custom scripting for versioning and changelogs<br>❌ More maintenance overhead |

### Decision

Adopt **`python-semantic-release`** to streamline the release process.  
It automates version management, changelog generation, PyPI publishing, and GitHub release creation from a single workflow — reducing manual coordination and the risk of version mismatches.  
By using [Conventional Commits](https://www.conventionalcommits.org/), the tool determines version bumps automatically and generates consistent release notes, making the release process predictable and maintainable.

This aligns with the project's principle of *automation over manual steps* while maintaining transparency through conventional commit messages that document changes clearly.


<br/><br/>

---

---

<br/><br/>

## 🔧 Adopt `mise` for Environment Management
<a id="dec15"></a>*DEC 15 — 2025-11-24*

### Context

The project requires **multiple runtime environments** — Python 3.10+ for the main codebase and Ruby 3.3 for Jekyll documentation.  
As the Apathetic Tools ecosystem expands, developers need a **unified tool** that can manage both Python and Ruby versions consistently across projects, including Node.js projects.  
Traditional version managers (e.g., `pyenv`, `rbenv`, `nvm`) require separate installations and configurations, creating friction when working across different language ecosystems.

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **`mise`** | ✅ Single tool for Python, Ruby, and Node.js<br>✅ Automatic version activation via `.tool-versions`<br>✅ Fast and lightweight<br>✅ Works across all Apathetic Tools projects<br>✅ Simple fallback to system tools | ⚠️ Additional tool to install<br>⚠️ Less familiar than language-specific managers |
| **`pyenv` + `rbenv` + `nvm`** | ✅ Language-specific, mature tools<br>✅ Widely known and documented | ❌ Three separate tools to install and configure<br>❌ Inconsistent interfaces and workflows<br>❌ No unified project-level configuration |
| **System package managers only** | ✅ No additional tools required<br>✅ Works out of the box | ❌ Limited version flexibility<br>❌ Inconsistent across platforms<br>❌ Difficult to test multiple versions |
| **Docker containers** | ✅ Complete isolation<br>✅ Reproducible environments | ❌ Heavyweight for local development<br>❌ Slower iteration cycles<br>❌ More complex setup |

### Decision

Adopt **`mise`** for environment management across the project and Apathetic Tools ecosystem.  
It provides a **single, consistent interface** for managing Python, Ruby, and Node.js versions — reducing setup complexity and enabling seamless collaboration across projects.  
The `.tool-versions` file automatically activates the correct versions when entering the project directory, while the tool gracefully falls back to system-installed versions when available.

This choice supports the project's goal of **minimizing friction** for contributors while maintaining flexibility for developers who prefer system tools or other version managers.


<br/><br/>

---

---

<br/><br/>

## 📦 Enable PyPI Releases for Package Distribution
<a id="dec14"></a>*DEC 14 — 2025-11-24*

### Context

Users need a **simple, standard way** to install and manage the library across different environments.  
While single-file scripts and zipapps provide portability, they don't integrate with Python's standard dependency management ecosystem.  
The project needed a **canonical distribution format** that works seamlessly with `pip`, `poetry`, and other package managers — making it easy for users to specify version constraints, track updates, and manage dependencies.

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **PyPI releases** | ✅ Standard Python package distribution<br>✅ Works with `pip`, `poetry`, `pipenv`<br>✅ Easy version management for users<br>✅ Integrates with dependency resolvers<br>✅ Familiar workflow for Python developers | ⚠️ Requires PyPI account and publishing setup<br>⚠️ Users need internet connection to install |
| **GitHub Releases only** | ✅ Simple distribution via GitHub<br>✅ No external service dependencies | ❌ Doesn't integrate with package managers<br>❌ Manual installation steps required<br>❌ No automatic dependency resolution |
| **Git submodules or direct Git installs** | ✅ Version control integration<br>✅ Easy to track source | ❌ Not standard for Python packages<br>❌ Complex dependency management<br>❌ Poor user experience |
| **No formal distribution** | ✅ No publishing overhead | ❌ Difficult for users to install and update<br>❌ No version management<br>❌ Poor discoverability |

### Decision

Enable **PyPI releases** as the primary distribution method for the package.  
This provides a **standard, familiar installation path** that integrates with Python's ecosystem — allowing users to install via `pip install apathetic-schema` or add it as a dependency in `pyproject.toml` with version constraints.  
PyPI releases complement the single-file and zipapp distributions by offering the canonical importable package format that works seamlessly with dependency management tools.

This decision prioritizes **user convenience and ecosystem integration** while maintaining the project's other distribution formats for specialized use cases.


<br/><br/>

---

---

<br/><br/>

## 📦 Choose `shiv` for Zipapp Support
<a id="dec13"></a>*DEC 13 — 2025-11-24*

### Context

As part of the three-tier distribution strategy *(see [DEC 10](#dec10))*, the project needed a tool to create **portable zipapp (`.pyz`) distributions** that bundle dependencies and maintain import semantics.  
Python's standard library `zipapp` module provides basic functionality but requires manual dependency management and doesn't handle entry points or dependency resolution automatically.  
The project needed a tool that **automatically bundles dependencies** while producing a single, executable archive file.

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **`shiv`** | ✅ Automatic dependency resolution and bundling<br>✅ Handles entry points and console scripts<br>✅ Produces executable `.pyz` files<br>✅ Integrates with `pyproject.toml`<br>✅ Active maintenance and Python 3.10+ support | ⚠️ Additional dependency for build process |
| **Standard library `zipapp`** | ✅ No external dependencies<br>✅ Built into Python | ❌ Manual dependency management required<br>❌ No automatic entry point handling<br>❌ More complex build scripts needed |
| **`pex`** | ✅ Similar functionality to shiv<br>✅ Mature tool with good documentation | ⚠️ Slightly more complex configuration<br>⚠️ Less Python-native feel |
| **Custom build script** | ✅ Full control over bundling process | ❌ Significant development and maintenance overhead<br>❌ Risk of missing edge cases in dependency resolution |

### Decision

Choose **`shiv`** for zipapp creation.  
It provides **automatic dependency resolution and bundling** — reading dependencies from `pyproject.toml` and creating a self-contained `.pyz` file that includes all required packages.  
Shiv's integration with Python packaging standards and its straightforward CLI make it ideal for the project's goal of **minimizing build complexity** while maintaining portability.

This choice supports the three-tier distribution model by providing a reliable, automated way to produce zipapp distributions without manual dependency management or complex build scripts.


<br/><br/>

---

---

<br/><br/>

## 📚 Use Jekyll with Minima Theme for Documentation
<a id="dec12"></a>*DEC 12 — 2025-11-13*

### Context

The project needed a **documentation site** that could be hosted on GitHub Pages with minimal configuration and maintenance overhead.  
GitHub Pages provides built-in support for Jekyll, making it the most straightforward option for hosting documentation without additional CI/CD setup or external hosting services.  
The documentation should be **easy to maintain, visually consistent, and automatically deployed** when changes are pushed to the repository.

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Jekyll with Minima theme** | ✅ Native GitHub Pages support<br>✅ Automatic deployment on push<br>✅ Minimal configuration required<br>✅ Large ecosystem of plugins<br>✅ Markdown-based content | ⚠️ Requires Ruby for local development<br>⚠️ Less flexible than custom static site generators |
| **MkDocs** | ✅ Python-based (matches project language)<br>✅ Good documentation tools<br>✅ Easy theme customization | ❌ Requires GitHub Actions for deployment<br>❌ Additional CI/CD configuration |
| **Sphinx** | ✅ Powerful documentation generation<br>✅ Excellent for API documentation | ❌ More complex setup<br>❌ Requires build step for GitHub Pages<br>❌ Heavier configuration |
| **Astro** | ✅ Modern, fast static site generator<br>✅ Component-based architecture<br>✅ Good performance and SEO<br>✅ Markdown support<br>✅ Flexible and modern tooling | ❌ Requires GitHub Actions for deployment<br>❌ Requires Node.js for local development<br>❌ Less mature ecosystem than Jekyll<br>❌ Additional CI/CD configuration |
| **Custom static site** | ✅ Full control over design and features | ❌ Significant development overhead<br>❌ Requires custom build and deployment setup |
| **GitHub Wiki** | ✅ Built into GitHub<br>✅ No setup required | ❌ Limited formatting options<br>❌ No custom domain or branding<br>❌ Less professional appearance |

### Decision

Use **Jekyll with the Minima theme** (configured with the solarized skin) for the documentation site.  
GitHub Pages' **native Jekyll support** enables automatic deployment without additional CI/CD configuration — documentation updates are published automatically when changes are pushed to the repository.  
The Minima theme provides a clean, professional appearance with minimal configuration, while Jekyll's plugin ecosystem offers flexibility for future enhancements.

This choice prioritizes **simplicity and zero-maintenance deployment** while providing a solid foundation for documentation that can evolve as the project grows.


<br/><br/>

---

---

<br/><br/>

## 🪵 Adopt Standard Library `logging`
<a id="dec11"></a>*DEC 11 — 2025-10-15 → revised 2025-10-31*  

### Context  

Early in development, the project required a **consistent and colorized logging system** that worked seamlessly in both modular and single-file builds.  
At the time, the built-in Python `logging` module seemed overkill for such a small utility — especially since the tool needed lightweight log-level control and minimal setup.  
We initially built a **custom logger** to provide:  

- Compact, dependency-free logging.  
- Inline color formatting for terminals.  
- Simpler test injection and patching for trace output.  

This approach fit the project's early ethos of *“small, inspectable, and standalone.”*  

### Options Considered  

| Option | Pros | Cons |
|--------|------|------|
| **Custom lightweight logger** | ✅ Fully under our control<br>✅ Compact and easily embedded<br>✅ Works identically in single-file builds | ⚠️ Duplicates standard functionality<br>⚠️ Harder to test and mock<br>⚠️ Configuration drift between modules |
| **Standard Library `logging`** | ✅ Mature and battle-tested<br>✅ Configurable handlers, filters, and levels<br>✅ Works natively with external libraries<br>✅ Simple integration with pytest and CLI flags | ⚠️ Significantly more verbose setup for color and formatting |
| **Third-party libraries (e.g. `loguru`, `rich.logging`)** | ✅ Rich formatting and features out-of-the-box | ❌ Adds runtime dependencies<br>❌ Conflicts with minimalism goal |

### Decision — *2025-10-15*  

Implement a **custom, lightweight logger** tailored for the project.  
It would provide clear output, colorized levels, and simple hooks for tracing (`TRACE`) without bringing in external dependencies or complex handler hierarchies.  
This custom module fit our goals of **portability** and **transparency**, keeping the tool’s behavior explicit and easy to inspect.  

### Follow-up and Evolution (*2025-10-31*)

As the codebase grew, the in-house logger **expanded significantly** — gaining configuration flags, test-time injection, and shims for different runtime modes.  
It became increasingly **difficult to test, maintain, and integrate** with third-party tooling.  

We also realized (belatedly) that the **standard `logging` module already supports** most of what we built manually — including level control, handler injection, and structured message formatting — all without external dependencies.  

The custom logger was therefore deprecated and removed. The project now **builds on Python's standard library `logging`** as its foundation, enhanced through the `apathetic-logging` wrapper library that provides colorized output, simplified configuration, and streamlined integration patterns while maintaining compatibility with the standard library's logging ecosystem.  



<br/><br/>

---
---

<br/><br/>

## ⚙️ Adopt a Three-Tier Distribution Strategy
<a id="dec10"></a>*DEC 10 — 2025-10-11*  

### Context 

As the early ad-hoc merger script evolved into a tested module, we want to ensure the project remains easy to distribute in forms that best suits different users.  

### Options Considered

| Option | Pros | Cons | Tools
|--------|------|------|------|
| **PyPI module (default)** | ✅ Easy to maintain and install<br>✅ Supports imports and APIs | ❌ Requires installation and internet | [`poetry`](https://python-poetry.org/), [`pip`](https://pypi.org/project/pip/) |
| **Single-file script** | ✅ No install step<br>✅ Human-readable source<br>✅ Ideal for quick CLI use | ❌ Not importable<br>❌ Harder to maintain merger logic | [`serger`](https://github.com/apathetic-tools/serger) |
| **Zipped module (`.pyz`)** | ✅ Bundled, portable archive<br>✅ Maintains import semantics | ⚠️ Requires unzip for source<br>⚠️ Slight startup overhead | [`zipapp`](https://docs.python.org/3/library/zipapp.html), [`shiv`](https://pypi.org/project/shiv/), [`pex`](https://pypi.org/project/pex/) |
| **Executable bundlers** | ✅ Fully portable binaries<br>✅ No Python install required | ❌ Platform-specific<br>❌ Not source-transparent  | [`PyInstaller`](https://pyinstaller.org/en/stable/), [`shiv`](https://pypi.org/project/shiv/), [`pex`](https://pypi.org/project/pex/) |


---

### Decision

Adopt a **three-tier distribution model**:  

1. **PyPI package** — the canonical importable module with semantic versioning guarantees.  
2. **Single-file script** — a CLI build based on `ast` import parsing.  
3. **Zipped module (`.pyz`)** — optional for future releases and easy to produce.  

Each tier serves different users while sharing the same tested, modular codebase.  

This does not rule out an executable bundle in the future.


<br/><br/>

---
---

<br/><br/>


## 🧪 Adopt `Pytest` for Testing  
<a id="dec09"></a>*DEC 09 — 2025-10-10*  

### Context

The project required a lightweight, expressive testing framework compatible with modern Python and CI environments.  
Testing should be easy to write, discover, and extend — without verbose boilerplate or heavy configuration.  
The priority was to keep tests readable while supporting fixtures, parametrization, and integration with tools like coverage and tox.

### Options Considered

| Tool | Pros | Cons |
|------|------|------|
| **[`Pytest`](https://docs.pytest.org/)** | ✅ Simple test discovery (`test_*.py`)<br>✅ Rich fixtures and parametrization<br>✅ Integrates with CI and coverage tools<br>✅ Large ecosystem and community | ⚠️ Implicit magic can obscure behavior for beginners |
| **`unittest` (stdlib)** | ✅ Built into Python<br>✅ Familiar xUnit style | ❌ Verbose boilerplate<br>❌ Weak fixture system<br>❌ Slower iteration and less readable output |


### Decision

Adopt **Pytest** as the primary testing framework.  
It provides clean syntax, automatic discovery, and a thriving ecosystem — making it ideal for both quick unit tests and full integration suites.  
Pytest’s concise, declarative style aligns with the project’s principle of *clarity over ceremony*, enabling contributors to write and run tests effortlessly across all supported Python versions.


<br/><br/>

---
---

<br/><br/>


## 🔍 Adopt `Pylance` and `MyPy` for Type Checking  
<a id="dec08"></a>*DEC 08 — 2025-10-10*  

### Context

Static typing improves maintainability and clarity across the codebase, but Python’s ecosystem offers multiple overlapping tools.  
The goal was to balance **developer ergonomics** in VS Code with **strict, automated checks** in CI.  
We wanted instant feedback during development and deeper, slower analysis during builds — without fragmenting the configuration.

### Options Considered

| Tool | Pros | Cons |
|------|------|------|
| **[`Pylance`](https://github.com/microsoft/pylance-release)** | ✅ Deep integration with VS Code<br>✅ Fast, incremental type checking<br>✅ Excellent in-editor inference and documentation<br>✅ Minimal configuration (uses `pyrightconfig.json` or `pyproject.toml`) | ❌ IDE-only — cannot run in CI<br>❌ Limited control over advanced typing rules |
| **[`Pyright`](https://github.com/microsoft/pyright)** | ✅ CLI equivalent of Pylance<br>✅ Fast and scriptable for CI | ⚠️ Less flexible than MyPy for complex type logic |
| **[`MyPy`](https://github.com/python/mypy)** | ✅ Mature, standards-based type checker<br>✅ Detects deeper type inconsistencies<br>✅ Integrates easily into CI workflows | ⚠️ Slower than Pyright<br>⚠️ Sometimes stricter or inconsistent with Pylance behavior |
| **No static checking** | ✅ Simplifies setup | ❌ No type enforcement; increased maintenance burden |

### Decision

Adopt **Pylance** as the default IDE type checker for developers using VS Code, and **MyPy** as the canonical CI type checker.  
Pylance offers immediate, contextual feedback during development through its deep VS Code integration, while MyPy provides comprehensive type analysis in automated checks.  

This dual setup ensures fast iteration locally and rigorous verification in CI — complementing Ruff’s linting and formatting without overlapping responsibilities.

### Future Consideration

Future builds may experiment with **`pyright` CLI** to align IDE and CI checks under a single configuration, but for now, **Pylance in the editor** and **MyPy in CI** provide the best balance of speed, coverage, and reliability.


<br/><br/>

---
---

<br/><br/>


## 🪶 Adopt `editorconfig` and `Ruff` for Linting and Formatting  
<a id="dec07"></a>*DEC 07 — 2025-10-10 → revised 2025-10-30*  

### Context

The project needed a **consistent, automated style and linting toolchain** to enforce quality without slowing down iteration.  
Python’s ecosystem offers several specialized tools (`black`, `isort`, `flake8`, `mypy`, etc.), but managing them separately increases setup friction and configuration sprawl.  
The goal was to find a **fast, unified tool** that covers linting, formatting, and import management from a single configuration.


### Options Considered

| Tool | Pros | Cons |
|------|------|------|
| **[`Ruff`](https://github.com/astral-sh/ruff)** | ✅ Extremely fast (Rust-based)<br>✅ Replaces multiple tools (lint, format, import sort)<br>✅ Single configuration in `pyproject.toml`<br>✅ Compatible with Black-style formatting | ⚠️ Still evolving rapidly |
| **[`Black`](https://github.com/psf/black)** | ✅ Widely adopted<br>✅ Consistent formatting standard | ❌ Format-only — requires separate tools for linting and imports |
| **[`isort`](https://pycqa.github.io/isort/)** | ✅ Excellent import sorter<br>✅ Highly configurable | ❌ Separate config and step<br>❌ Slower and redundant when used with Ruff |
| **[`.editorconfig`](https://editorconfig.org/)** | ✅ Supported by most editors<br>✅ Defines consistent indentation, EOLs, and encoding<br>✅ Works across languages | ❌ Limited to basic formatting rules |

### Decision

Adopt **Ruff** as the unified linting and formatting tool, complemented by **EditorConfig** for cross-editor baseline consistency.
Ruff’s **speed**, **all-in-one scope**, and **`pyproject.toml` integration** reduce the need for multiple Python-specific tools, while EditorConfig ensures **consistent indentation, encoding, and newline behavior** in any environment.  

Together, they provide a lightweight, editor-agnostic foundation that enforces uniform style without excess configuration — aligning with the project’s “minimal moving parts” principle.

### Follow-up and Evolution (2025-10-11 → 2025-10-30)

For a brief period, **isort** was integrated alongside Ruff to handle complex import merging, as the team was unaware that Ruff’s configuration already supported equivalent sorting behavior.  
After confirming Ruff’s import management features, **isort was removed**, consolidating all style and linting functions under Ruff alone.



<br/><br/>

---
---

<br/><br/>


## 📦 Choose `Poetry` for Dependency and Environment Management  
<a id="dec06"></a>*DEC 06 — 2025-10-10*  

### Context

The project needs a **single-source, reproducible setup** covering dependency management, packaging, and development workflows.  
The goal is to reduce moving parts — **one configuration, one lockfile, one entrypoint.**

### Options Considered

| Tool | Pros | Cons |
|------|------|------|
| **[`Poetry`](https://python-poetry.org/)** | ✅ Unified `pyproject.toml` for dependencies and metadata<br>✅ Built-in lockfile for reproducible builds<br>✅ Manages virtual environments automatically<br>✅ Extensible with plugins (e.g. [`poethepoet`](https://github.com/nat-n/poethepoet)) for task automation | ⚠️ Slightly heavier CLI<br>⚠️ Requires learning its workflow |
| **`pip` + `requirements.txt`** | ✅ Ubiquitous and simple<br>✅ Works with system Python or virtualenv | ❌ No lockfile by default<br>❌ Fragmented setup (requires separate tools for packaging and scripts)<br>❌ Harder to track metadata and extras |
| **`pip-tools`** | ✅ Adds lockfile support to `pip` | ⚠️ Partial overlap; still requires setup scripts |
| **Manual `venv` + Makefile** | ✅ Transparent and minimal | ❌ Scattered configuration<br>❌ Manual sync and version drift |

### Decision

Adopt **Poetry** as the project’s canonical environment and dependency manager.  
It provides a **batteries-included workflow** — unified configuration (`pyproject.toml`), reproducible installs (`poetry.lock`), isolated environments, and task automation via the `poethepoet` plugin instead of maintaining Makefiles.  

This mirrors the **familiar ergonomics of `package.json` + `pnpm`** for developers coming from JavaScript ecosystems while preserving full Python portability.


<br/><br/>

---
---

<br/><br/>


## 🤝 Adopt `Contributor Covenant 3.0` as Code of Conduct  
<a id="dec05"></a>*DEC 05 — 2025-10-10*  

### Context

The project needed a **clear, inclusive standard of behavior** for contributors and maintainers.  
As the Apathetic Tools ecosystem grows, shared norms for collaboration, respect, and conflict resolution become essential — especially for open projects that welcome community participation.  
Rather than inventing custom language, the team wanted a **widely recognized, well-maintained template** that could be easily understood, translated, and enforced.

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Contributor Covenant 3.0** | ✅ Industry-standard and widely adopted<br>✅ Legally sound and CC BY-SA 4.0 licensed<br>✅ Clearly defines expectations, reporting, and enforcement<br>✅ Includes inclusive language and repair-focused approach | ⚠️ Template language can feel formal or corporate |
| **Custom in-house code** | ✅ Tailored tone and structure | ❌ Risk of omissions or unclear enforcement<br>❌ Higher maintenance burden |
| **No formal code** | ✅ Less administrative work | ❌ Unclear expectations<br>❌ Difficult to moderate conflicts fairly |

### Decision

Adopt the **Contributor Covenant 3.0** as the foundation for the project’s `CODE_OF_CONDUCT.md`, adapted for the Apathetic Tools community.  
This provides a **consistent, transparent behavioral framework** while avoiding the overhead of authoring and maintaining a custom code.  
It defines reporting, enforcement, and repair processes clearly, reinforcing the community’s emphasis on accountability and respect.  

This version is lightly customized with local contact details and references to community moderation procedures, maintaining alignment with upstream guidance.


<br/><br/>

---
---

<br/><br/>


## 🧭 Target `Python` Version `3.10`
<a id="dec04"></a>*DEC 04 — 2025-10-10*  


### Context

Following the choice of Python *(see [DEC 03](#dec03))*, this project must define a minimum supported version balancing modern features, CI stability, and broad usability.  
The goal is to stay current without excluding common environments.

### Options Considered

The latest Python version is *3.14*.

| Version | Pros | Cons |
|---------|------|------|
| **3.8+** | ✅ Works on older systems | ❌ Lacks modern typing (`\|`, `match`, `typing.Self`) and adds maintenance overhead |
| **3.10+**  | ✅ Matches Ubuntu 22.04 LTS (baseline CI)<br>✅ Includes modern syntax and typing features | ⚠️ Slightly narrower audience but covers all active LTS platforms
| **3.12+** | ✅ Latest stdlib and type system | ❌ Too new; excludes many CI and production environments |

### Platform Baselines
Windows WSL typically runs Ubuntu 22.04 or 24.04 LTS.

| Platform | Default Python | Notes |
|-----------|----------------|-------|
| Ubuntu 22.04 LTS | 3.10 | Minimum baseline |
| Ubuntu 24.04 LTS | 3.12 | Current CI default |
| macOS / Windows | 3.12 | User-installed or Store LTS |
| GitHub Actions `ubuntu-latest` | 3.10 → 3.12 | Transition period coverage |

### Python Versions

| Version | Status | Released | EOL |
|---------|--------|----------|-----|
| 3.14 | bugfix | 2025-10 | 2030-10 |
| 3.13 | bugfix | 2024-10 | 2029-10 |
| 3.12 | security | 2023-10 | 2028-10 |
| 3.11 | security | 2022-10 | 2027-10 |
| **3.10** | security | 2021-10 | 2026-10 |
| 3.9 | security | 2020-10 | 2025-10 |
| 3.8 | end of life | 2019-10-14 | 2024-10-07 |

### Decision

Target **Python 3.10 and newer** as the supported baseline.  
This version provides modern typing and syntax while staying compatible with Ubuntu 22.04 LTS — the lowest common denominator across CI and production systems.


<br/><br/>

---
---

<br/><br/>


## 🧭 Choose `Python` as the Implementation Language  
<a id="dec03"></a>*DEC 03 — 2025-10-09*  


### Context

The project aims to be a **lightweight, dependency-free build tool** that runs anywhere — Linux, macOS, Windows, or CI — without setup or compilation.  
Compiled languages (e.g. Go, Rust) would require distributing multiple binaries and would prevent in-place auditing and modification.
Python 3, by contrast, is preinstalled or easily available on all major platforms, balancing universality and maintainability.

---

### Options Considered

| Language | Pros | Cons |
|-----------|------|------|
| **Python** | ✅ Widely available<br>✅ No compile step<br>✅ Readable and introspectable  | ⚠️ Slower execution<br>⚠️ Limited single-file packaging |
| **JavaScript / Node.js** | ✅ Familiar to web developers | ❌ Not standard on all OSes<br>❌ Frequent version churn |
| **Bash** | ✅ Ubiquitous | ❌ Fragile for complex logic

### Decision

Implement the project in **Python 3**, targeting **Python 3.10+** *(see [DEC 04](#dec04))*.  
Python provides **zero-dependency execution**, **cross-platform reach**, and **transparent, editable source code**, aligning with the project’s principle of *clarity over complexity*.  
 It allows users to run the tool immediately and understand it fully.

The performance trade-off compared to compiled binaries is acceptable for small workloads.  
Future distributions may include `.pyz` or bundled binary releases as the project evolves.


<br/><br/>

---
---

<br/><br/>


## ⚖️ Choose `MIT-a-NOAI` License
<a id="dec02"></a>*DEC 02 — 2025-10-09*  

### Context

This project is meant to be open, modifiable, and educational — a tool for human developers.  
The ethics and legality of AI dataset collection are still evolving, and no reliable system for consent or attribution yet exists.

The project uses AI tools but distinguishes between **using AI** and **being used by AI** without consent.

### Options Considered

- **MIT License (standard)** — simple and permissive, but allows unrestricted AI scraping.
- **MIT + “No-AI Use” rider (MIT-a-NOAI)** — preserves openness while prohibiting dataset inclusion or model training; untested legally and not OSI-certified.

### Decision

Adopt the **MIT-a-NOAI license** — the standard MIT license plus an explicit clause banning AI/ML training or dataset inclusion.
This keeps the project open for human collaboration while defining clear ethical boundaries.

While this may deter adopters requiring OSI-certified licenses, it can later be dual-licensed if consent-based frameworks emerge.

### Ethical Consideration

AI helped create this project but does not own it.  
The license asserts consent as a prerequisite for training use — a small boundary while the wider ecosystem matures.


<br/><br/>

---
---

<br/><br/>



## 🤖 Use `AI Assistance` for Documentation and Development  
<a id="dec01"></a>*DEC 01 — 2025-10-09*


### Context

This project started as a small internal tool. Expanding it for public release required more documentation, CLI scaffolding, and testing than available time allowed.

AI tools (notably ChatGPT) offered a practical way to draft and refine code and documentation quickly, allowing maintainers to focus on design and correctness instead of boilerplate.

### Options Considered

- **Manual authoring** — complete control but slow and repetitive.
- **Static generators (pdoc, Sphinx)** — good for APIs, poor for narrative docs.
- **AI-assisted drafting** — fast, flexible, and guided by human review.

### Decision

Use **AI-assisted authoring** (e.g. ChatGPT) for documentation and boilerplate generation, with final edits and review by maintainers.  
This balances speed and quality with limited human resources. Effort can shift from writing boilerplate to improving design and clarity.  

AI use is disclosed in headers and footers as appropriate.

### Ethical Note

AI acts as a **paid assistant**, not a data harvester.  
Its role is pragmatic and transparent — used within clear limits while the ecosystem matures.


<br/><br/>

---
---

<br/><br/>

_Written following the [Apathetic Decisions Style v1](https://apathetic-recipes.github.io/decisions-md/v1) and [ADR](https://adr.github.io/), optimized for small, evolving projects._  
_This document records **why** we build things the way we do — not just **what** we built._

> ✨ *AI was used to help draft language, formatting, and code — plus we just love em dashes.*

<p align="center">
  <sub>😐 <a href="https://apathetic-tools.github.io/">Apathetic Tools</a> © <a href="./LICENSE">MIT-a-NOAI</a></sub>
</p>
