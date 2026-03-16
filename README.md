<p align="center">
  <img src="assets/branding/prism_light_256.png" alt="Prism" width="128">
</p>

<h1 align="center">Prism</h1>
<p align="center"><strong>Refract complexity into clarity</strong></p>
<p align="center"><em>Configuration inheritance system for managing multi-level development environments</em></p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+"></a>
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey" alt="Platform">
  <a href="https://andersonwilliam85.github.io/prism/"><img src="https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg" alt="Documentation"></a>
</p>

---

## What is Prism?

Prism is a **configuration inheritance system** that manages complex, multi-level development environments through composable YAML configurations. Like a prism refracts white light into distinct colors, Prism takes organizational complexity and refracts it into clear, manageable configuration layers.

### The Problem

Large organizations face configuration chaos:

- **Complex hierarchies** -- Fortune 500 companies with 5+ organizational levels
- **Conflicting requirements** -- Different teams need different tools, configs, and access
- **Configuration drift** -- No single source of truth across thousands of employees
- **Onboarding friction** -- New hires waste days configuring their environment

### The Solution

Prism provides:

- **Centralized tool registry** -- Tools defined once in `tool-registry.yaml` with per-platform install/uninstall commands; child configs reference tools by name only
- **Configuration inheritance** -- Define once at company level, override per team
- **Multi-level hierarchies** -- Support structures from flat (startups) to 5+ levels (enterprise)
- **Web UI** -- Tool selection with categories (Core, Editor, Containers, Runtime, Cloud, Kubernetes, CLI), inline validation, hover tooltips, platform-aware filtering, cancel/retry flow
- **CLI tools** -- `prism install`, `prism rollback`, `prism history` -- scriptable, automatable, CI/CD friendly
- **NPM distribution** -- Packages published to npm, no custom infrastructure needed
- **Validation** -- Config engine validates tool registry (install + uninstall), tool references, and email patterns from YAML
- **Smart merging** -- Deep-merge with configurable strategies (union, override, append)
- **Installation rollback** -- `.prism_rollback.json` manifest persisted on install; `prism rollback <workspace>` reverses all actions
- **Privilege separation** -- Two-phase install with sudo session management
- **No generic fallbacks** -- Tools without explicit platform install commands are skipped

---

## Quick Start

### Install from PyPI

```bash
pip install prism-dx
prism ui            # Launch the web installer
prism install       # Or install directly from CLI
```

### Install from source

```bash
git clone https://github.com/andersonwilliam85/prism.git
cd prism
make install-dev
make run            # Opens at http://localhost:5555
```

See [Getting Started](https://andersonwilliam85.github.io/prism/getting-started/quickstart) for the full guide.

---

## Features

### Web UI Installer

- Tool selection page with categories (Core, Editor, Containers, Runtime, Cloud, Kubernetes, CLI)
- Hover tooltips for tool descriptions
- Platform-aware filtering (tools without install commands for your OS are hidden)
- Inline validation (no alerts)
- Step-by-step wizard with progress tracking
- **Theme system** -- 5 built-in themes + custom themes with 5 gradient color slots
- **Cascading dropdowns** -- Dynamic field dependencies (e.g., division filters available teams)
- **Settings panel** -- Runtime registry, CDN, and language overrides
- **Environment management** on landing page
- Cancel/retry flow
- Rollback button

### Tool Registry

Tools are defined once in a centralized `tool-registry.yaml`. Each tool specifies:
- **label**, **summary**, **description** -- for the UI
- **category** -- core, editor, containers, runtime, cloud, kubernetes, cli
- **platforms** -- per-OS install commands (mac, ubuntu, linux, windows)
- **uninstall** -- per-OS uninstall commands (used by rollback)

Child configs reference tools by string name only (e.g., `- git`). Tools without explicit install commands for the current platform are skipped -- no guessing.

### Starter Packages

8 starter packages ship in the `prisms/` directory:

| Prism | Use Case | Hierarchy | Scale |
|-------|----------|-----------|-------|
| `prism` | Default -- solo developers | Flat | Any |
| `startup` | Seed/Series A startups | 1 level | 10--50 |
| `acme-corp` | Template for companies | 2 levels | 100--1K |
| `consulting-firm` | Multi-client work | By client | Variable |
| `fortune500` | Enterprise | 5 levels | 50K+ |
| `university` | Academic institutions | Dept to Lab | Variable |
| `opensource` | Community projects | Flat | Community |
| `cli-test-prism` | CLI testing fixture | Flat | Testing |

### Installation Safety

- **Rollback** -- Every install persists a `.prism_rollback.json` manifest. `prism rollback <workspace>` reverses all actions. The UI also has a rollback button. Rollback engine at `prism/engines/rollback_engine.py`.
- **Privilege separation** -- Normal operations run first. Privileged steps (tool installs from the registry) require explicit sudo approval in a separate phase.
- **Sudo sessions** -- Cryptographic tokens with 15-minute TTL and 3-attempt lockout.

### Installation History

```bash
prism history
```

Scans for previous installations. Also available via the `/api/history` endpoint.

---

## Architecture

Prism follows a **VBD-inspired** (Volatility-Based Decomposition) layered architecture with dependency injection.

| Layer | Role | Components |
|-------|------|------------|
| **Managers** | Orchestration -- *the "what"* | `installation_manager`, `package_manager` |
| **Engines** | Business logic -- *the "how"* | `config_engine`, `installation_engine`, `rollback_engine` |
| **Accessors** | External boundaries -- *the "where"* | `file`, `command`, `registry`, `system`, `rollback`, `sudo` |
| **Utilities** | Cross-cutting services | `event_bus` (pub/sub progress) |
| **Models** | Plain dataclasses | Installation, config, rollback DTOs |
| **UI** | Flask web app | REST API + static frontend |
| **CLI** | Click commands | `install`, `rollback`, `history`, `packages`, `ui` |

All layers are wired through a composition root (`container.py`) with constructor injection -- no global state, fully testable.

See [Architecture Reference](https://andersonwilliam85.github.io/prism/reference/architecture) for the full breakdown.

---

## Development

### Prerequisites

- Python 3.9+
- Flask, PyYAML, Rich

### Setup

```bash
make install-dev    # Install dev dependencies
make test           # Run tests (unit + CLI)
make test-all       # All tests (590+ test functions)
make run            # Start dev server
make lint           # Run linters (flake8 + mypy)
make format         # Format code (black + isort)
make check          # All CI checks
```

### Testing

```bash
make test              # Unit + CLI tests
make test-all          # All tests (590+ test functions)
make test-coverage     # With coverage report
make test-trace        # E2E with Playwright traces
```

GitHub Actions runs lint, test, coverage, and security scans on every PR. Pre-commit hooks enforce isort, black, flake8, and pytest.

---

## Documentation

Full documentation at **[andersonwilliam85.github.io/prism](https://andersonwilliam85.github.io/prism/)**.

- [Getting Started](https://andersonwilliam85.github.io/prism/getting-started/quickstart)
- [Themes & Customization](https://andersonwilliam85.github.io/prism/user-guide/themes)
- [Cascading Dropdowns](https://andersonwilliam85.github.io/prism/user-guide/cascading-dropdowns)
- [Configuration Schema](https://andersonwilliam85.github.io/prism/reference/configuration-schema)
- [Architecture](https://andersonwilliam85.github.io/prism/reference/architecture)
- [Rollback System](https://andersonwilliam85.github.io/prism/reference/rollback-system)
- [Privilege Separation](https://andersonwilliam85.github.io/prism/reference/privilege-separation)
- [Contributing](https://andersonwilliam85.github.io/prism/contributor-guide/contributing)

---

## Supported Platforms

- **macOS** (Intel and Apple Silicon)
- **Windows** 10/11
- **Linux** (Ubuntu 20.04+, Debian, Fedora, RHEL)
- **WSL2**

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and test: `make test-all`
4. Format code: `make format`
5. Run CI checks: `make check`
6. Submit a Pull Request

Pre-commit hooks run isort, black, flake8, and pytest on every commit. All must pass.

See [Contributing Guide](https://andersonwilliam85.github.io/prism/contributor-guide/contributing).

---

## License

MIT License -- See [LICENSE](LICENSE)

Copyright (c) 2025 William Anderson

---

<p align="center">
  <strong>Prism -- Refract complexity into clarity</strong><br>
  Made by <a href="https://github.com/andersonwilliam85">William Anderson</a>
</p>
