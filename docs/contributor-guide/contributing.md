---
layout: default
title: Contributing
---

# Contributing to Prism

## Table of Contents

- [Branch Strategy](#branch-strategy)
- [Development Setup](#development-setup)
- [Workflow](#workflow)
- [Pre-Commit Hooks](#pre-commit-hooks)
- [Testing](#testing)
- [Coding Standards](#coding-standards)
- [Adding a New Prism](#adding-a-new-prism)

---

## Branch Strategy

Prism uses **gitflow**. All three long-lived branches are protected — no direct pushes.

```
main        production — tagged releases only
 ^
stage       release candidate — full test suite + smoke tests
 ^
dev         integration — features land here first
 ^
feature/*   your work branches from dev
```

### Normal development

1. Branch from `dev`
2. PR back to `dev`
3. When `dev` is stable, PR `dev` -> `stage`
4. When `stage` passes, PR `stage` -> `main`

### Hotfixes

1. Branch `hotfix/*` from `main`
2. PR directly to `main`
3. Cherry-pick the fix to `dev`
4. Normal flow: `dev` -> `stage` -> `main`

---

## Development Setup

### Prerequisites

- Python 3.9+
- Git

### Setup

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/prism.git
cd prism
git remote add upstream https://github.com/andersonwilliam85/prism.git

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
make install-dev

# Verify
make test
```

---

## Workflow

### 1. Create a branch from dev

```bash
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name
```

### 2. Make changes

- Write code
- Add tests (>90% coverage)
- Update documentation if needed

### 3. Test locally

```bash
make test          # Unit + CLI tests
make lint          # flake8 + mypy
make format-check  # black + isort
```

### 4. Commit

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: Add new theme system
fix: Fix package validation error
docs: Update testing guide
refactor: Simplify config merger
test: Add E2E tests for installer
```

Pre-commit hooks will run automatically on commit (see below).

### 5. Push and open PR to dev

```bash
git push origin feature/your-feature-name
```

Open a PR targeting `dev`. CI runs automatically. Once approved, it merges to `dev`.

---

## Pre-Commit Hooks

Prism uses pre-commit hooks that run automatically on every commit. All hooks must pass before the commit is accepted.

The hooks run in order:

1. **isort** — sort imports (profile: black, line length: 120)
2. **black** — format code (line length: 120)
3. **flake8** — lint (max line length: 120, ignores: E203, W503)
4. **pytest** — run unit tests (`tests/unit -x -q`)

With 590+ tests in the suite, the pytest hook runs the unit test subset to keep commits fast while still catching regressions.

To run the hooks manually:

```bash
make pre-commit
```

To install the hooks in a fresh clone:

```bash
pre-commit install
```

---

## Testing

See [Testing](https://andersonwilliam85.github.io/prism/contributor-guide/testing) for the comprehensive guide.

### Quick reference

```bash
make test              # Unit + CLI
make test-all          # All tests including E2E
make test-coverage     # With coverage report
make lint              # Linters
make format            # Auto-format
make check             # All CI checks
```

### Test types

- **Unit** — individual functions/classes (590+ test functions)
- **CLI** — command-line interface
- **Web** — Flask API endpoints
- **Integration** — component interactions
- **E2E** — full user workflows with Playwright

Coverage requirement: >90%

---

## Coding Standards

### Style

- **PEP 8** with 120-character line length
- **black** for formatting
- **isort** for imports
- Type hints where appropriate

### Format code

```bash
make format   # black + isort
make lint     # flake8 + mypy
```

---

## Adding a New Prism

See [Package System](https://andersonwilliam85.github.io/prism/reference/package-system) for the full guide.

1. Create `prisms/your-prism.prism/`
2. Add `package.yaml`
3. Add `base/tool-registry.yaml` (or inherit from the default prism's registry)
4. Add `README.md`
5. Add tests
6. Submit PR to `dev`

---

## Questions?

[Open an issue](https://github.com/andersonwilliam85/prism/issues)

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
