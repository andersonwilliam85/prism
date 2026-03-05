# Playwright Dashboards & Reports

Playwright provides multiple ways to view, debug, and analyze your test runs.

---

## 🎭 Option 1: Playwright UI Mode (Interactive Dashboard)

**The most powerful option** - Live interactive test runner with browser preview.

### Features:
- ✅ Visual test explorer
- ✅ Live browser preview as tests run
- ✅ Step-by-step debugging
- ✅ Watch mode (auto-rerun on changes)
- ✅ Time travel debugging
- ✅ Network inspection
- ✅ Console logs

### Run UI Mode:

```bash
# Quick start
./run_playwright_ui.sh

# Or manually
pytest tests/e2e/ --headed --ui
```

This opens an **interactive GUI** where you can:
1. See all tests in a tree view
2. Click to run individual tests
3. Watch the browser in real-time
4. Pause and step through tests
5. Inspect DOM at any point
6. View network requests
7. See console output

**Screenshot of UI Mode:**
```
┌─────────────────────────────────────────────────┐
│  Playwright Test Runner                        │
├─────────────────────────────────────────────────┤
│  tests/                                         │
│  ├─ e2e/                                        │
│  │  ├─ ✓ test_installer_flow.py        (5/5)   │
│  │  ├─ ▶ test_complete_installation.py (0/8)   │
│  │  └─ ⏸ test_validation_and_ux.py     (3/12)  │
├─────────────────────────────────────────────────┤
│  [Browser Preview]                              │
│  [Live view of test execution]                  │
└─────────────────────────────────────────────────┘
```

---

## 📊 Option 2: HTML Test Report

**Best for sharing results** - Beautiful standalone HTML report.

### Features:
- ✅ Overview of all test results
- ✅ Pass/fail statistics
- ✅ Screenshots on failure
- ✅ Test duration analytics
- ✅ Shareable (single HTML file)
- ✅ Filterable results

### Generate Report:

```bash
# Quick start
./run_playwright_report.sh

# Or manually
pytest tests/e2e/ \
    --html=playwright-report/report.html \
    --self-contained-html

# Open report
open playwright-report/report.html
```

**Report includes:**
- Total tests run
- Pass/fail/skip counts
- Execution time per test
- Error messages and stack traces
- Screenshots of failures
- Test metadata

---

## 🔍 Option 3: Playwright Trace Viewer

**Best for debugging failures** - Deep dive into what happened during test execution.

### Features:
- ✅ Time-travel debugging
- ✅ Full DOM snapshots
- ✅ Network activity
- ✅ Console logs
- ✅ Screenshots at each step
- ✅ Action timeline
- ✅ Source code view

### Generate & View Traces:

```bash
# Run tests with tracing enabled
pytest tests/e2e/ \
    --tracing=on \
    --headed=false

# View a specific trace
playwright show-trace test-results/<test-name>/trace.zip

# Example:
playwright show-trace test-results/test_installer_flow/trace.zip
```

**Trace Viewer shows:**
- Timeline of all actions
- DOM state at each step
- Network requests/responses
- Console output
- Screenshots
- Source code with highlights

**Screenshot of Trace Viewer:**
```
┌─────────────────────────────────────────────────┐
│  Actions │ Network │ Console │ Source │ Metadata│
├──────────┴──────────┴─────────┴────────┴─────────┤
│  Timeline:                                       │
│  00:00 - page.goto('http://localhost:5555')     │
│  00:12 - click('.package-card')                  │
│  00:15 - click('button:has-text("Next")')       │
│  00:18 - fill('input[name="email"]', ...)      │
├─────────────────────────────────────────────────┤
│  [DOM Snapshot at 00:15]                         │
│  [Screenshot]                                    │
└─────────────────────────────────────────────────┘
```

---

## 📹 Option 4: Video Recording

**Best for visual verification** - Watch test execution as a video.

### Enable Video Recording:

```bash
pytest tests/e2e/ \
    --video=on \
    --headed=false

# Or only on failures
pytest tests/e2e/ \
    --video=retain-on-failure
```

**Videos saved to:** `test-results/<test-name>/video.webm`

---

## 📸 Option 5: Screenshots

**Best for quick debugging** - Capture screenshots at specific points or on failure.

### Enable Screenshots:

```bash
# Screenshot only on failures
pytest tests/e2e/ \
    --screenshot=only-on-failure

# Screenshot on all tests
pytest tests/e2e/ \
    --screenshot=on
```

**Screenshots saved to:** `test-results/<test-name>/screenshot.png`

---

## 🚀 Quick Command Reference

### Interactive Dashboard (Recommended for Development)
```bash
./run_playwright_ui.sh
```

### Generate HTML Report (Recommended for CI/CD)
```bash
./run_playwright_report.sh
```

### Run with Everything (Traces + Videos + Screenshots)
```bash
pytest tests/e2e/ \
    --headed=false \
    --tracing=on \
    --video=retain-on-failure \
    --screenshot=only-on-failure \
    --html=playwright-report/report.html
```

### Debug a Single Test in UI Mode
```bash
pytest tests/e2e/test_installer_flow.py::test_package_selection \
    --headed \
    --ui
```

### View Trace from Failed Test
```bash
# Find the trace file
ls test-results/

# Open trace viewer
playwright show-trace test-results/<test-name>/trace.zip
```

---

## 🎯 Which Dashboard Should You Use?

| Use Case | Tool | Command |
|----------|------|----------|
| **Writing tests** | UI Mode | `./run_playwright_ui.sh` |
| **Debugging failures** | Trace Viewer | `playwright show-trace <trace.zip>` |
| **Sharing results** | HTML Report | `./run_playwright_report.sh` |
| **CI/CD** | HTML Report + Traces | See `.github/workflows/playwright.yml` |
| **Quick validation** | Terminal output | `pytest tests/e2e/ -v` |

---

## 📁 Output Directory Structure

After running tests, you'll have:

```
prism/
├── playwright-report/
│   └── report.html          # Main HTML report
├── test-results/
│   ├── test_name_1/
│   │   ├── trace.zip        # Trace file
│   │   ├── video.webm       # Video recording
│   │   └── screenshot.png   # Screenshots
│   └── test_name_2/
│       └── ...
└── htmlcov/                 # Code coverage report
    └── index.html
```

---

## 🔧 Configuration

Playwright options are configured in:
- `pytest.ini` - Default pytest options
- `conftest.py` - Playwright browser settings
- Command line - Override defaults

### Example: Change Browser

```bash
# Use Firefox
pytest tests/e2e/ --browser firefox

# Use multiple browsers
pytest tests/e2e/ --browser chromium --browser firefox
```

### Example: Slow Down Execution

```bash
# Add 500ms delay between actions (easier to watch)
pytest tests/e2e/ --headed --slowmo=500
```

---

## 📚 Learn More

- [Playwright Python Docs](https://playwright.dev/python/)
- [Playwright Trace Viewer](https://playwright.dev/python/docs/trace-viewer)
- [Playwright UI Mode](https://playwright.dev/python/docs/test-ui-mode)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)

---

## 💡 Pro Tips

1. **Use UI Mode during development** - It's the fastest way to write and debug tests
2. **Enable traces on CI** - They're invaluable for debugging failures you can't reproduce locally
3. **Use `--headed --slowmo=500`** - Makes it easy to see what's happening
4. **Filter tests with `-k`** - `pytest tests/e2e/ -k "theme"` runs only theme-related tests
5. **Use `--pdb` for Python debugging** - `pytest tests/e2e/ --pdb` drops into debugger on failure

---

**Happy Testing!** 🎭✨
