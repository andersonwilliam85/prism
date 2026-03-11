---
layout: default
title: About Prism
---

<p align="center">
  <img src="assets/prism-logo-light.png" alt="Prism" width="128">
</p>

<h1 align="center">Prism</h1>
<p align="center"><strong>Refract complexity into clarity</strong></p>
<p align="center"><em>Configuration inheritance system for managing multi-level development environments</em></p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+"></a>
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey" alt="Platform">
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
git clone https://github.com/andersonwilliam85/prism.git
cd prism
make install-dev
make run
# Opens at http://localhost:5555
```

---

## Built-in Prisms

| Prism | Use Case | Hierarchy | Scale |
|-------|----------|-----------|-------|
| `prism` | Default (ships as core) | Flat | Any |
| `prism` | Solo developers | 3 environment tiers | 1 |
| `startup` | Seed/Series A startups | 1 level | 10–50 |
| `acme-corp` | Template for companies | 2 levels | 100–1K |
| `consulting-firm` | Multi-client work | By client | Variable |
| `fortune500` | Enterprise | 5 levels | 50K+ |
| `university` | Academic institutions | Dept to Lab | Variable |
| `opensource` | Community projects | Flat | Community |

Each prism includes custom themes, cascading user fields, and rollback configuration.

---

## Architecture

Prism follows a **VBD-inspired** (Volatility-Based Decomposition) layered architecture:

- **Managers** — Orchestration — *the "what"*
- **Engines** — Business logic — *the "how"*
- **Accessors** — External boundaries — *the "where"*
- **Utilities** — Cross-cutting services
- **Models** — Plain dataclasses

All wiring via dependency injection in `container.py`. See [Architecture](reference/architecture.md).

---

## Key Features

- [Themes & Customization](user-guide/themes.md) — 5 built-in + custom themes
- [Cascading Dropdowns](user-guide/cascading-dropdowns.md) — Dynamic field dependencies
- [Rollback System](reference/rollback-system.md) — Installation safety
- [Privilege Separation](reference/privilege-separation.md) — Sudo session management
- [Config Inheritance](user-guide/config-inheritance.md) — Multi-level merge strategies
- [Local Docs Server](user-guide/local-docs-server.md) — Post-install workspace browser

---

## Supported Platforms

- **macOS** (Intel and Apple Silicon)
- **Windows** 10/11
- **Linux** (Ubuntu 20.04+, Debian, Fedora, RHEL)
- **WSL2**

---

## License

MIT License — Copyright (c) 2025 William Anderson

---

<p align="center">
  <strong>Prism — Refract complexity into clarity</strong><br>
  Made by <a href="https://github.com/andersonwilliam85">William Anderson</a>
</p>
