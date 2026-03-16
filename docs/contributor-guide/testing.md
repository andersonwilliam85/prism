---
layout: default
title: Testing
---

# Testing

Comprehensive testing guide for Prism.

---

## Overview

Prism uses a multi-layered testing strategy with 590+ test functions across 35 test files:

- **Unit Tests** — Core logic validation (config engine, installation engine, accessors, managers, utilities, CLI, UI, tools)
- **CLI Tests** — Command-line interface
- **Web Tests** — Flask API endpoints
- **Integration Tests** — Component interactions
- **E2E Tests** — Full user workflows (Playwright)

**Target Coverage: >90%**

---

## Quick Start

### Install Test Dependencies

```bash
# Install everything (development + testing)
make install-dev

# Install Playwright browsers
make install-playwright
```

### Run Tests

```bash
# Fast tests (unit + CLI)
make test

# All tests (includes E2E)
make test-all

# With coverage report
make test-coverage

# E2E tests with trace viewer (debugging)
make test-trace
```

---

## Test Types

### Unit Tests (`tests/unit/`)

Test individual components in isolation. This is the largest test category, covering:

- `engines/` — ConfigEngine, InstallationEngine
- `managers/` — InstallationManager, PackageManager
- `accessors/` — FileAccessor, CommandAccessor, SystemAccessor, RollbackAccessor, RegistryAccessor
- `utilities/` — EventBus, PlatformDetector, EnvSubstitutor, ProgressLogger
- `cli/` — CLI command tests
- `ui/` — API endpoint tests (packages, installation, validation, configuration)
- `tools/` — DocsServer, DocsDiscovery, DocsRenderer
- Top-level — ConfigMerger, PrismValidator, InstallerEngine, PackageManager, E2E install flows

**Run:**
```bash
make test-unit
# or
pytest tests/unit/ -v
```

### CLI Tests (`tests/e2e/test_cli_installer.py`)

Test command-line installer interface, including `prism install`, `prism rollback`, and `prism history`.

**Run:**
```bash
make test-cli
# or
pytest tests/e2e/test_cli_installer.py -v
```

### Web Tests (`tests/unit/ui/`)

Test Flask API endpoints including packages, installation, validation, and configuration APIs.

**Run:**
```bash
pytest tests/unit/ui/ -v
```

### E2E Tests (`tests/e2e/`)

End-to-end browser testing with Playwright.

**Files:**
- `test_installer_flow.py` — Core installation workflow
- `test_complete_installation.py` — Full user journey
- `test_validation_and_ux.py` — UX and validation (inline validation, no alerts)
- `test_full_install_flow.py` — Full install flow
- `test_hd_api_e2e.py` — HD API E2E tests
- `test_web_api.py` — Web API tests

**Run:**
```bash
make test-e2e
# or
pytest tests/e2e/ --headed
```

### Integration Tests (`tests/integration/`)

Test component interactions (installer engine, prism validation).

**Run:**
```bash
make test-integration
# or
pytest tests/integration/ -v
```

---

## Pre-Commit Hooks

Pre-commit hooks run automatically on every commit and must all pass:

1. **isort** — sort imports
2. **black** — format code
3. **flake8** — lint
4. **pytest** — run unit tests (`tests/unit -x -q`)

This ensures that all commits pass formatting, linting, and unit tests before they are accepted.

---

## Makefile Commands

```bash
# Testing
make test                # Fast tests (unit + CLI)
make test-unit           # Unit tests only
make test-cli            # CLI tests only
make test-e2e            # E2E browser tests
make test-integration    # Integration tests
make test-all            # All tests
make test-coverage       # Tests with coverage report
make test-report         # Generate HTML test report
make test-trace          # E2E with trace viewer
make show-trace          # Open trace viewer

# Quality
make lint                # Run linters
make format              # Auto-format code
make format-check        # Check formatting (CI mode)

# CI/CD
make check               # All CI checks
make pre-commit          # Pre-commit checks
make ci                  # Full CI pipeline
```

---

## Playwright Dashboards

### HTML Reports (Static Analysis)

Generate and view test reports:

```bash
# Generate HTML report
pytest tests/e2e/ --html=playwright-report/report.html --self-contained-html

# Open report
open playwright-report/report.html
# or
make test-report
```

### Trace Viewer (Time-Travel Debugging)

Debug tests with Playwright's trace viewer:

```bash
# Run tests with tracing
make test-trace

# View trace
make show-trace

# Or manually
python3 -m pytest tests/e2e/ --tracing=on
python3 -m playwright show-trace test-results/*/trace.zip
```

### Screenshots & Videos

```bash
# Screenshots on failure (default)
pytest tests/e2e/

# Video recording
pytest tests/e2e/ --video=on

# View screenshots
ls test-results/*/test-failed-*.png

# View videos
ls test-results/*/video.webm
```

### Quick Debug Commands

```bash
# Run single test with trace + headed mode
pytest tests/e2e/test_installer_flow.py::TestInstallerFlow::test_page_loads \
  --tracing=on \
  --headed \
  --slowmo=500

# Then view trace
playwright show-trace test-results/*/trace.zip

# Debug with Playwright inspector
PWDEBUG=1 pytest tests/e2e/test_installer_flow.py

# Slow motion (see what's happening)
pytest tests/e2e/ --headed --slowmo=1000
```

### Dashboard Locations

| Dashboard | Location | Command |
|-----------|----------|---------|
| HTML Reports | `playwright-report/*.html` | `open playwright-report/report.html` |
| Trace Files | `test-results/*/trace.zip` | `playwright show-trace <file>` |
| Screenshots | `test-results/*/*.png` | `open test-results/` |
| Videos | `test-results/*/*.webm` | `open test-results/` |

---

## Test Coverage

### View Coverage

```bash
# Generate coverage report
make test-coverage

# Open HTML report
open htmlcov/index.html
```

### Current Coverage

| Component | Coverage |
|-----------|----------|
| Package Validator | ~90% |
| Config Merger | ~85% |
| Installer Engine | ~80% |
| Web UI | ~75% |
| **Overall** | **>80%** |

**Target: >90%**

---

## Writing Tests

### Unit Test Template

```python
import pytest
from prism.engines.config_engine._merge import ConfigMerger

class TestConfigMerger:
    def test_merges_simple_configs(self):
        """Test basic config merging"""
        base = {"package": {"name": "test"}}
        override = {"package": {"version": "1.0"}}
        result = merge_configs(base, override)

        assert result["package"]["name"] == "test"
        assert result["package"]["version"] == "1.0"

    def test_handles_nested_configs(self):
        """Test deep merging"""
        base = {"package": {"settings": {"debug": False}}}
        override = {"package": {"settings": {"verbose": True}}}
        result = merge_configs(base, override)

        assert result["package"]["settings"]["debug"] == False
        assert result["package"]["settings"]["verbose"] == True
```

### E2E Test Template

```python
import pytest
from playwright.sync_api import Page, expect

class TestInstallerFlow:
    def test_complete_workflow(self, page: Page):
        """Test full installation workflow"""
        # 1. Start page
        page.goto("http://localhost:5555")
        expect(page.locator("h1")).to_contain_text("Prism Installer")

        # 2. Select package
        page.click("#pkg_prism")
        page.click("button:has-text('Next')")

        # 3. Enter user info
        page.fill("#name", "Test User")
        page.fill("#email", "test@example.com")
        page.click("button:has-text('Install')")

        # 4. Verify completion
        expect(page.locator(".success")).to_be_visible()
        expect(page.locator(".success")).to_contain_text("Installation complete")
```

### Fixtures

Create reusable test data:

```python
import pytest

@pytest.fixture
def sample_package():
    return {
        "package": {
            "name": "test-package",
            "version": "1.0.0",
            "description": "Test package"
        }
    }

@pytest.fixture
def sample_user_info():
    return {
        "name": "Test User",
        "email": "test@example.com"
    }

def test_with_fixtures(sample_package, sample_user_info):
    # Use fixtures
    assert sample_package["package"]["name"] == "test-package"
    assert sample_user_info["name"] == "Test User"
```

---

## Continuous Integration

Prism uses GitHub Actions for automated testing.

### Workflows

1. **ci.yml** - Runs on every PR
   - Lint (isort, black, flake8, mypy)
   - Unit tests
   - CLI tests
   - E2E tests
   - Coverage report
   - Security scan

2. **deploy-*.yml** - Deployment pipelines
   - Dev, Stage, Production
   - Full test suites before deploy

See [CI/CD Documentation](ci-cd.md) for details.

### Local CI Simulation

```bash
# Run what CI runs
make ci

# Step by step
make format-check  # Format check
make lint          # Linters
make test-all      # All tests
```

---

## Debugging

### Playwright Debugging

```bash
# Open Playwright Inspector
PWDEBUG=1 pytest tests/e2e/test_installer_flow.py

# Slow motion (500ms between actions)
pytest tests/e2e/ --headed --slowmo=500

# Take screenshots
pytest tests/e2e/ --screenshot=on

# Record video
pytest tests/e2e/ --video=on

# With trace viewer
make test-trace
make show-trace
```

### Verbose Output

```bash
# Show print statements
pytest -s

# Verbose pytest
pytest -v

# Show test durations
pytest --durations=10

# Stop on first failure
pytest -x
```

### Port Issues

**Error:** `Address already in use`

```bash
# Kill process on port 5555
lsof -ti:5555 | xargs kill -9

# Or use different port
export TEST_PORT=5556
pytest tests/e2e/
```

---

## Best Practices

### 1. Keep Tests Fast
- Unit tests: <1s each
- E2E tests: <30s each
- Use mocks for external services

### 2. Isolate Tests
- No dependencies between tests
- Clean up after each test
- Use fixtures for setup/teardown

### 3. Test Edge Cases
```python
def test_handles_invalid_input():
    with pytest.raises(ValueError):
        validate_package(None)

def test_handles_missing_fields():
    result = validate_package({"package": {}})
    assert result["valid"] == False
    assert "Missing required field: name" in result["errors"]
```

### 4. Descriptive Names
```python
# Good
def test_validates_missing_package_name_returns_error():
    pass

# Bad
def test_validation():
    pass
```

### 5. Use Fixtures
```python
@pytest.fixture
def mock_server():
    server = start_test_server()
    yield server
    server.stop()
```

### 6. Document Tests
```python
def test_complex_workflow():
    """
    Test the complete installation workflow including:
    1. Package selection
    2. User info entry
    3. Configuration
    4. Installation
    5. Completion
    """
    # Test implementation
```

---

## Contributing

When adding features:

1. Write unit tests first (TDD)
2. Add E2E tests for UI changes
3. Ensure >90% coverage
4. All tests pass locally
5. Pre-commit hooks pass (isort, black, flake8, pytest)
6. Tests pass in CI
7. Document test cases

### Test Checklist

- [ ] Unit tests for new functions
- [ ] E2E tests for UI changes
- [ ] Edge cases covered
- [ ] Fixtures for reusable data
- [ ] Descriptive test names
- [ ] Tests pass: `make test-all`
- [ ] Coverage maintained: `make test-coverage`
- [ ] CI passes: `make ci`

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright Python Docs](https://playwright.dev/python/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Questions?** [Open an issue](https://github.com/andersonwilliam85/prism/issues)
