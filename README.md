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

- **Complex hierarchies** — Fortune 500 companies with 5+ organizational levels
- **Conflicting requirements** — Different teams need different tools, configs, and access
- **Configuration drift** — No single source of truth across thousands of employees
- **Onboarding friction** — New hires waste days configuring their environment

### The Solution

Prism provides:

- **Configuration inheritance** — Define once at company level, override per team
- **Multi-level hierarchies** — Support structures from flat (startups) to 5+ levels (enterprise)
- **Web UI** — Visual prism selection and installation wizard with themes, cascading dropdowns, and real-time progress
- **CLI tools** — Scriptable, automatable, CI/CD friendly
- **NPM distribution** — Packages published to npm, no custom infrastructure needed
- **Validation** — Catch errors before deployment
- **Smart merging** — Deep-merge with configurable strategies (union, override, append)
- **Installation rollback** — Every action tracked, automatic LIFO undo on failure
- **Privilege separation** — Two-phase install with sudo session management

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/andersonwilliam85/prism.git
cd prism

# Install dependencies
make install-dev

# Run tests
make test

# Start the web UI installer
make run
# Opens at http://localhost:5555
```

See [Getting Started](https://andersonwilliam85.github.io/prism/getting-started/quickstart) for the full guide.

---

## Features

### Web UI Installer

- Prism gallery with visual cards for all configurations
- Step-by-step wizard with progress tracking
- **Theme system** — 5 built-in themes + custom themes with 5 gradient color slots
- **Cascading dropdowns** — Dynamic field dependencies (e.g., division filters available teams)
- **Settings panel** — Runtime registry, CDN, and language overrides
- Responsive design with smart validation

### Configuration Inheritance

Multi-level hierarchy with configurable merge strategies:

```
Company (base)
  └── Business Unit
      └── Department
          └── Team
              └── Individual
```

Configurations merge intelligently — base layer defines company standards, each level can override or extend using union, deep_merge, override, or append strategies.

### Built-in Prisms

| Prism | Use Case | Hierarchy | Scale |
|-------|----------|-----------|-------|
| `prism` | Default (ships as core) | Flat | Any |
| `personal-dev` | Solo developers | 3 environment tiers | 1 |
| `startup` | Seed/Series A startups | 1 level | 10–50 |
| `acme-corp` | Template for companies | 2 levels | 100–1K |
| `consulting-firm` | Multi-client work | By client | Variable |
| `fortune500` | Enterprise | 5 levels | 50K+ |
| `university` | Academic institutions | Dept to Lab | Variable |
| `opensource` | Community projects | Flat | Community |

Each prism includes custom themes, cascading user fields, and rollback configuration.

### Installation Safety

- **Rollback** — Every file copy, directory creation, command execution, and config change is tracked. On failure, changes unwind in LIFO order.
- **Privilege separation** — Normal operations run first. Privileged steps (apt-get, global npm) require explicit sudo approval in a separate phase.
- **Sudo sessions** — Cryptographic tokens with 15-minute TTL and 3-attempt lockout.

### NPM Distribution

```bash
# Packages auto-fetch from npm via unpkg CDN
python3 install.py --prism personal-dev

# Use custom registry (corporate/air-gapped)
python3 install.py --npm-registry https://npm.mycompany.com
```

### Local Docs Server

Post-install, browse your workspace configuration:

```bash
python3 -m prism.tools.docs_server --workspace ~/dev
```

---

## Architecture

Prism follows a **VBD-inspired** (Volatility-Based Decomposition) layered architecture with dependency injection.

| Layer | Role | Components |
|-------|------|------------|
| **Managers** | Orchestration — *the "what"* | `installation_manager`, `package_manager` |
| **Engines** | Business logic — *the "how"* | `config_engine` (schema evolution), `installation_engine` (installation surface) |
| **Accessors** | I/O boundary — *thin adapters* | `file`, `command`, `registry`, `system`, `rollback`, `sudo` |
| **Utilities** | Cross-cutting services | `event_bus` (pub/sub progress) |
| **Models** | Plain dataclasses | Installation, config, rollback DTOs |
| **UI** | Flask web app | REST API + static frontend |

All layers are wired through a composition root (`container.py`) with constructor injection — no global state, fully testable.

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
make test-all       # All tests including E2E
make run            # Start dev server
make lint           # Run linters (flake8 + mypy)
make format         # Format code (black + isort)
make check          # All CI checks
```

### Testing

```bash
make test              # Unit + CLI tests
make test-all          # All tests including E2E
make test-coverage     # With coverage report
make test-trace        # E2E with Playwright traces
```

GitHub Actions runs lint, test, coverage, and security scans on every PR.

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

See [Contributing Guide](https://andersonwilliam85.github.io/prism/contributor-guide/contributing).

---

## License

MIT License — See [LICENSE](LICENSE)

Copyright (c) 2025 William Anderson

---

<p align="center">
  <strong>Prism — Refract complexity into clarity</strong><br>
  Made by <a href="https://github.com/andersonwilliam85">William Anderson</a>
</p>
