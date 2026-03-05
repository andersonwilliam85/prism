# Testing Guide

Comprehensive testing for Prism installer.

## Test Types

### 1. **Unit Tests** (`tests/unit/`)
Test individual components in isolation.

### 2. **Integration Tests** (`tests/integration/`)
Test component interactions and workflows.

### 3. **E2E Tests** (`tests/e2e/`)
End-to-end testing with Playwright.

---

## Quick Start

### Install Dependencies

```bash
# Install Python test dependencies
pip install -r requirements-test.txt

# Install Playwright browsers
python -m playwright install
```

### Run All Tests

```bash
# Run everything
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test type
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### Run E2E Tests Only

```bash
# Headless (CI mode)
pytest tests/e2e/ --headed=false

# Headed (see browser)
pytest tests/e2e/ --headed=true

# Specific test
pytest tests/e2e/test_installer_flow.py::test_complete_installation
```

---

## Test Structure

```
tests/
├── unit/
│   ├── test_package_validator.py
│   ├── test_config_merger.py
│   ├── test_package_manager.py
│   └── test_npm_fetcher.py
├── integration/
│   ├── test_installer_engine.py
│   ├── test_web_ui_api.py
│   └── test_package_system.py
└── e2e/
    ├── test_installer_flow.py
    ├── test_package_selection.py
    ├── test_theme_switching.py
    ├── test_configuration.py
    └── fixtures/
        └── test_packages/
```

---

## Writing Tests

### Unit Test Example

```python
import pytest
from scripts.package_validator import PackageValidator

def test_validates_correct_package():
    validator = PackageValidator()
    result = validator.validate("prisms/core.prism")
    assert result["valid"] == True
    assert len(result["errors"]) == 0
```

### Integration Test Example

```python
import pytest
from installer_engine import InstallationEngine

def test_full_installation_flow():
    engine = InstallationEngine(
        config_package="core-prism",
        user_info={"name": "Test User", "email": "test@example.com"}
    )
    result = engine.install()
    assert result["success"] == True
```

### E2E Test Example

```python
import pytest
from playwright.sync_api import Page, expect

def test_package_selection(page: Page):
    # Navigate to installer
    page.goto("http://localhost:5555")
    
    # Select a package
    page.click("#pkg_core-prism")
    
    # Verify selection
    expect(page.locator("#pkg_core-prism")).to_have_css(
        "border", "2px solid rgb(102, 126, 234)"
    )
    
    # Click next
    page.click("button:has-text('Next')")
    
    # Verify step 2 is shown
    expect(page.locator("#step2")).to_be_visible()
```

---

## Continuous Integration

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
          python -m playwright install --with-deps
      
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Test Coverage

Target: **>90% coverage**

### View Coverage Report

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Coverage by Component

- **Package Validator**: 100%
- **Config Merger**: 95%
- **Installer Engine**: 90%
- **Web UI API**: 85%
- **E2E Flows**: 80%

---

## Fixtures & Test Data

### Test Packages (`tests/e2e/fixtures/test_packages/`)

Minimal test prisms for E2E testing:

- `minimal.prism` - Bare minimum config
- `complete.prism` - All features enabled
- `invalid.prism` - Invalid config (for error testing)

### Mocks & Stubs

Located in `tests/fixtures/`:

- `mock_npm_registry.py` - Mock npm responses
- `mock_git_operations.py` - Mock git commands
- `test_user_info.py` - Sample user data

---

## Debugging Tests

### Playwright Debugging

```bash
# Debug mode (opens inspector)
PWDEBUG=1 pytest tests/e2e/test_installer_flow.py

# Slow motion (see what's happening)
pytest tests/e2e/ --slowmo=1000

# Take screenshots on failure
pytest tests/e2e/ --screenshot=on
```

### Verbose Output

```bash
# Show print statements
pytest -s

# Verbose pytest output
pytest -v

# Show test durations
pytest --durations=10
```

---

## Best Practices

1. **Keep tests fast** - Unit tests <1s, E2E <30s each
2. **Isolate tests** - No dependencies between tests
3. **Use fixtures** - DRY principle for test data
4. **Test edge cases** - Invalid inputs, errors, edge cases
5. **Descriptive names** - `test_validates_missing_package_name_returns_error`
6. **Clean up** - Remove test artifacts after each test
7. **CI-ready** - Tests pass in headless mode

---

## Troubleshooting

### Playwright Install Fails

```bash
# Install system dependencies (Linux)
sudo apt-get install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libasound2

# Reinstall Playwright
python -m playwright install --force
```

### Port 5555 Already in Use

```bash
# Kill process on port
lsof -ti:5555 | xargs kill -9

# Or use a different port in tests
export TEST_PORT=5556
```

### Tests Hang

- Check for infinite loops in web UI
- Increase timeout: `pytest --timeout=60`
- Check background processes: `ps aux | grep python`

---

## Contributing

When adding new features:

1. ✅ Write unit tests first (TDD)
2. ✅ Add integration tests for workflows
3. ✅ Add E2E tests for user flows
4. ✅ Ensure >90% coverage
5. ✅ All tests pass in CI

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright Python](https://playwright.dev/python/)
- [Coverage.py](https://coverage.readthedocs.io/)
