# 🎨 Playwright Dashboard Quick Reference

## 📊 HTML Reports (Static Analysis)

```bash
# Generate HTML report for all tests
python3 -m pytest tests/e2e/ --html=playwright-report/report.html --self-contained-html

# Generate report for specific test file
python3 -m pytest tests/e2e/test_installer_flow.py --html=playwright-report/installer.html --self-contained-html

# Open the latest report
open playwright-report/report.html
```

**What you get:**
- ✅ Color-coded pass/fail results
- 📊 Test duration statistics
- 📝 Detailed error messages with stack traces
- 🎨 Beautiful HTML formatting
- 📤 Shareable standalone file

---

## 🎬 Trace Viewer (Time-Travel Debugging)

```bash
# Run tests with tracing enabled
python3 -m pytest tests/e2e/ --tracing=on --output=test-results

# View a specific trace
python3 -m playwright show-trace test-results/path-to-test/trace.zip

# Or view the most recent trace
python3 -m playwright show-trace $(find test-results -name "trace.zip" | head -1)
```

**What you get:**
- 📸 Screenshot at each test action
- 🌐 Network requests timeline
- 📝 Console logs and errors
- ⚡ DOM snapshots (time-travel through the page state)
- 🔍 Source code highlighting
- ⏱️ Performance metrics
- 🎯 Click on timeline to see exact state

---

## 📸 Screenshots & Videos

```bash
# Run with screenshots on failure (default)
python3 -m pytest tests/e2e/

# Run with video recording (configure in pytest.ini)
python3 -m pytest tests/e2e/ --video=on

# Screenshots saved to:
ls test-results/*/test-failed-*.png

# Videos saved to:
ls test-results/*/video.webm
```

---

## 🚀 Quick Commands

```bash
# Run all E2E tests with full dashboards
python3 -m pytest tests/e2e/ \
  --html=playwright-report/full.html \
  --self-contained-html \
  --tracing=on \
  --screenshot=on \
  --video=retain-on-failure

# Run single test with trace viewer (for debugging)
python3 -m pytest tests/e2e/test_installer_flow.py::TestInstallerFlow::test_page_loads \
  --tracing=on \
  --headed \
  --slowmo=500

# Then view the trace
python3 -m playwright show-trace test-results/*/trace.zip
```

---

## 📁 Dashboard Locations

| Dashboard Type | Location | Command |
|----------------|----------|---------|
| HTML Reports | `playwright-report/*.html` | `open playwright-report/report.html` |
| Trace Files | `test-results/*/trace.zip` | `playwright show-trace <file>` |
| Screenshots | `test-results/*/*.png` | `open test-results/` |
| Videos | `test-results/*/*.webm` | `open test-results/` |

---

## 🎯 Best Practices

1. **For CI/CD:** Use HTML reports (lightweight, shareable)
2. **For Debugging:** Use Trace Viewer (most detailed)
3. **For Quick Checks:** Run with `--headed` to watch live
4. **For Sharing:** HTML reports are self-contained

---

## 📚 More Info

See `docs/PLAYWRIGHT_DASHBOARDS.md` for detailed documentation.
