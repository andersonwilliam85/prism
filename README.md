# 💎 Prism Package Manager

**Refract complexity into clarity**

*Configuration inheritance system for managing multi-level development environments*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey)](#supported-platforms)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#testing)

---

## 🎯 What is Prism?

Prism is a **configuration inheritance system** that manages complex, multi-level development environments through composable YAML configurations. Like a prism refracts white light into distinct colors, Prism takes organizational complexity and refracts it into clear, manageable configuration layers.

### The Problem

Large organizations face configuration chaos:

- 🏢 **Complex hierarchies**: Fortune 500 companies with 5+ organizational levels
- 🎯 **Conflicting requirements**: Different teams need different tools, configs, and access
- 🔄 **Configuration drift**: No single source of truth across 50,000+ employees
- ⚠️ **Onboarding nightmare**: New hires waste days configuring their environment
- 📊 **No standardization**: Every team reinvents the wheel

### The Solution

Prism provides:

✅ **Configuration inheritance** - Define once at company level, override per team  
✅ **Multi-level hierarchies** - Support structures from flat (startups) to 5+ levels (enterprise)  
✅ **Beautiful web UI** - Visual package selection and installation wizard  
✅ **CLI tools** - Scriptable, automatable, CI/CD friendly  
✅ **NPM distribution** - Packages published to npm, no custom infrastructure  
✅ **Validation system** - Catch errors before deployment  
✅ **Merge strategies** - Smart deep-merging with list handling  

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/prism.git
cd prism

# Install dependencies
make install-dev

# Run tests
make test

# Start the web UI installer
make run
# Opens at http://localhost:5555
```

### Create Your First Configuration

```bash
# Use a template as starting point
cp -r prisms/acme-corp prisms/my-company

# Edit the base configuration
vim prisms/my-company/base/my-company.yaml

# Create team-specific overrides
vim prisms/my-company/teams/platform-team.yaml

# Validate
python3 scripts/package_validator.py prisms/my-company

# Test the configuration
python3 scripts/config_merger.py \
  prisms/my-company/base/my-company.yaml \
  prisms/my-company/teams/platform-team.yaml
```

See [Creating Configurations](docs/user-guide/creating-configurations.md) for detailed guide.

---

## 📖 Features

### 🌐 Web UI Installer

- **Package gallery** with visual cards showing all configurations
- **Step-by-step wizard** with progress tracking
- **Live installation updates** via Server-Sent Events
- **Theme system** (5 beautiful themes with localStorage persistence)
- **Responsive design** works on any screen size
- **Smart validation** prevents configuration errors

```bash
python3 install-ui.py
# or
make run
```

### 🎭 Configuration Inheritance

**Multi-level hierarchy support:**

```
Company (base)
  └── Business Unit
      └── Department
          └── Team
              └── Individual
```

Configurations merge intelligently:
- Base layer defines company standards
- Each level can override or extend
- Smart deep-merge handles nested structures
- List concatenation or replacement strategies

See [Config Inheritance](docs/user-guide/config-inheritance.md).

### 📦 Package System

**Built-in configurations:**

| Package | Use Case | Hierarchy | Users |
|---------|----------|-----------|-------|
| `personal-dev` | Freelancers, indie devs | Flat | 1 |
| `startup` | Seed/Series A startups | 1 level | 10-50 |
| `acme-corp` | Template for companies | 2 levels | 100-1K |
| `consulting-firm` | Multi-client work | By client | Variable |
| `fortune500` | Enterprise | 5 levels | 50K+ |
| `university` | Academic institutions | Dept → Lab | Variable |
| `opensource` | Community projects | Flat | Community |

See [Choosing a Package](docs/user-guide/choosing-a-package.md).

### 🔧 NPM Distribution

Packages are published to npm under the `@prism` scope:

```bash
# Packages auto-fetch from npm via unpkg CDN
python3 install.py --package @prism/personal-dev-config

# Use custom registry (corporate/air-gapped)
python3 install.py --npm-registry https://npm.mycompany.com

# Or set environment variable
export PRISM_NPM_REGISTRY=https://npm.mycompany.com
```

See [NPM Packages](docs/reference/npm-packages.md) and [Custom Registries](docs/user-guide/custom-registries.md).

### ✅ Validation System

Comprehensive validation ensures:

- Required fields present (`name`, `version`, `description`)
- Valid YAML syntax
- Schema compliance
- Asset file existence
- User info field validation

```bash
# Validate single package
python3 scripts/package_validator.py prisms/my-company

# Validate all packages
python3 scripts/package_validator.py --all
```

### 🧪 Testing & CI/CD

**Professional testing stack:**

- **Unit tests** - Core functionality (pytest)
- **CLI tests** - Command-line interface
- **E2E tests** - Full user flows (Playwright)
- **Coverage reporting** - Track test coverage
- **GitHub Actions** - Automated CI/CD pipeline

```bash
make test              # Fast tests (unit + CLI)
make test-all          # All tests including E2E
make test-coverage     # With coverage report
make test-trace        # E2E with trace viewer
```

See [Testing](docs/development/testing.md) and [CI/CD](docs/development/ci-cd.md).

---

## 📚 Documentation

### Getting Started

- [Installation](docs/getting-started/installation.md) - Setup and dependencies
- [Quickstart](docs/getting-started/quickstart.md) - Your first Prism package
- [First Configuration](docs/getting-started/first-configuration.md) - Step-by-step guide

### User Guide

- [Choosing a Package](docs/user-guide/choosing-a-package.md) - Which config is right for you?
- [Creating Configurations](docs/user-guide/creating-configurations.md) - Build your own
- [Config Inheritance](docs/user-guide/config-inheritance.md) - How merging works
- [Custom Registries](docs/user-guide/custom-registries.md) - Corporate npm registries

### Development

- [Testing](docs/development/testing.md) - Running and writing tests
- [Contributing](docs/development/contributing.md) - Join the project
- [CI/CD](docs/development/ci-cd.md) - Automation pipeline

### Reference

- [Package System](docs/reference/package-system.md) - Technical architecture
- [NPM Packages](docs/reference/npm-packages.md) - Distribution system
- [Configuration Schema](docs/reference/configuration-schema.md) - YAML structure

---

## 🏗️ Architecture

### Core Components

```
prism/
├── install-ui.py          # Web UI server (Flask)
├── install.py             # CLI installer
├── installer_engine.py    # Core installation logic
├── scripts/
│   ├── config_merger.py   # Configuration inheritance engine
│   ├── config_validator.py # YAML validation
│   ├── package_validator.py # Package schema validation
│   ├── package_manager.py  # Package operations
│   └── npm_package_fetcher.py # NPM integration
├── prisms/                # Configuration packages
│   ├── personal-dev/
│   ├── startup/
│   ├── acme-corp/
│   ├── consulting-firm/
│   ├── fortune500/
│   ├── university/
│   └── opensource/
└── tests/                 # Comprehensive test suite
    ├── unit/
    ├── e2e/
    └── integration/
```

### Configuration Merge Flow

```python
# 1. Load base configuration
base = load_yaml("prisms/company/base/company.yaml")

# 2. Load team override
team = load_yaml("prisms/company/teams/platform.yaml")

# 3. Deep merge
result = merge_configs(base, team)

# 4. Result contains:
# - All base settings
# - Team overrides applied
# - Lists concatenated or replaced
# - Nested dicts merged
```

See [Package System](docs/reference/package-system.md) for technical details.

---

## 💻 Supported Platforms

- ✅ **macOS** (Intel & Apple Silicon)
- ✅ **Windows** 10/11
- ✅ **Linux** (Ubuntu 20.04+, Debian, Fedora, RHEL)

---

## 🛠️ Development

### Prerequisites

- Python 3.9+
- Flask (for web UI)
- Playwright (for E2E tests)

### Setup

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Start development server
make run

# Run linters
make lint

# Format code
make format
```

### Makefile Commands

```bash
make help              # See all 40+ commands
make dev               # Quick start: install + run
make test              # Fast tests (unit + CLI)
make test-all          # All tests
make check             # All CI checks
make pre-commit        # Pre-commit checks
make ci                # Full CI pipeline
```

See [Contributing](docs/development/contributing.md) for development workflow.

---

## 🧪 Testing

### Test Coverage

- **72 total tests**
  - 15 unit tests (config merger, package validator)
  - 3 CLI tests (installer interface)
  - 54 E2E tests (full user flows)

### Running Tests

```bash
# Fast tests (unit + CLI)
make test

# All tests including E2E
make test-all

# With coverage report
make test-coverage

# E2E with trace viewer (debugging)
make test-trace
make show-trace
```

### Continuous Integration

GitHub Actions workflows:

1. **PR Checks** - Lint, test, coverage on every PR
2. **Dev Deploy** - Auto-deploy to dev on merge
3. **Stage Deploy** - Release candidates with smoke tests
4. **Production Deploy** - Tagged releases with artifacts

See [CI/CD Documentation](docs/development/ci-cd.md).

---

## 📝 Examples

### Simple Personal Configuration

```yaml
# prisms/my-setup/package.yaml
package:
  name: "my-dev-setup"
  version: "1.0.0"
  description: "My personal development environment"
  
  tools:
    - git
    - docker
    - python
    - nodejs
    
  repositories:
    - url: "git@github.com:me/project.git"
      path: "~/Development/projects/project"
```

### Enterprise Multi-Level Configuration

```yaml
# Base company config
# prisms/company/base/company.yaml
package:
  name: "acme-corp"
  tools:
    - git
    - docker
  security:
    sso: true
    vpn_required: true

---
# Team override
# prisms/company/teams/platform.yaml
package:
  name: "platform-team"
  tools:
    - kubernetes
    - terraform
  security:
    vault_access: true

# Merged result:
# - All company tools + team tools
# - Company security + team security
# - Team-specific additions
```

See [Configuration Examples](docs/user-guide/creating-configurations.md#examples).

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Make changes and test**: `make test-all`
4. **Format code**: `make format`
5. **Run CI checks**: `make check`
6. **Commit**: `git commit -m "feat: add my feature"`
7. **Push**: `git push origin feature/my-feature`
8. **Create Pull Request**

See [Contributing Guide](docs/development/contributing.md) for detailed workflow.

### Ways to Contribute

- ⭐ **Star the repo** - Show your support
- 🐛 **Report bugs** - Help us improve
- 💡 **Suggest features** - Share your ideas
- 📝 **Improve docs** - Make it clearer
- 🎭 **Create packages** - Share your configs
- 🔧 **Submit PRs** - Fix bugs or add features

---

## 📜 License

**MIT License** - See [LICENSE](LICENSE)

Copyright (c) 2025 William Anderson

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

---

## 👨‍💻 Author

**Created by [William Anderson](https://github.com/andersonwilliam85)**

Prism was built to solve the configuration chaos problem at scale - from solo developers to Fortune 500 enterprises. What started as a weekend project to automate dev environment setup evolved into a comprehensive configuration inheritance system.

### The Story

Every new job, new machine, new teammate - I'd spend hours:

1. Installing forgotten tools
2. Configuring git (again)
3. Generating SSH keys (again)
4. Creating folder structures
5. Cloning repositories

It was tedious, error-prone, and didn't scale. After experiencing this pain at startups and enterprise companies, I built Prism to:

- **Standardize** - Everyone gets the same great setup
- **Scale** - Works for 1 person or 50,000
- **Simplify** - Complex hierarchies become manageable
- **Share** - Open source for everyone to benefit

### Philosophy

💎 **Refract Complexity Into Clarity** - Like a prism turns white light into a spectrum, Prism turns organizational chaos into clear structure.

🌈 **Beauty Through Organization** - Your dev environment should be as elegant as the code you write.

💡 **Illuminate, Don't Dictate** - Provide structure but stay flexible. Use what you need.

✨ **Open & Extensible** - Built on open principles. Fork it, extend it, make it yours.

---

## 🙏 Acknowledgments

- Built with assistance from **Claude** (Anthropic)
- Inspired by the frustration of manual environment setup
- Influenced by npm's package ecosystem
- Motivated by the need for better configuration management at scale
- Made with ♥️ for developers everywhere

---

## 🔗 Links

- **GitHub**: [github.com/andersonwilliam85/prism](https://github.com/andersonwilliam85/prism)
- **Issues**: [github.com/andersonwilliam85/prism/issues](https://github.com/andersonwilliam85/prism/issues)
- **Documentation**: [docs/](docs/)
- **NPM Packages**: [@prism scope](https://www.npmjs.com/search?q=%40prism)

---

## 📞 Support

Need help? Found a bug?

1. **Check documentation**: [docs/](docs/)
2. **Search issues**: [GitHub Issues](https://github.com/andersonwilliam85/prism/issues)
3. **Create new issue**: [New Issue](https://github.com/andersonwilliam85/prism/issues/new)

Pull requests are always welcome! 🚀

---

<p align="center">
  <strong>💎 Prism - Refract complexity into clarity</strong><br>
  Made with ♥️ by <a href="https://github.com/andersonwilliam85">William Anderson</a>
</p>
