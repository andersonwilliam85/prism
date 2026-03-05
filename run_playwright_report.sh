#!/bin/bash
# Run Playwright tests and generate interactive HTML report

set -e

echo "📊 Playwright Test Report Generator"
echo "===================================="
echo ""

# Check dependencies
if ! python3 -m pytest --version > /dev/null 2>&1; then
    echo "Installing test dependencies..."
    pip install -r requirements-test.txt
    python3 -m playwright install
fi

echo "🧪 Running E2E tests with report generation..."
echo ""

# Run tests with HTML report and trace generation
pytest tests/e2e/ \
    --headed=false \
    --html=playwright-report/report.html \
    --self-contained-html \
    --tracing=on \
    --screenshot=only-on-failure \
    --video=retain-on-failure \
    -v

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "⚠️  Some tests failed (exit code: $EXIT_CODE)"
fi

echo ""
echo "📊 Report generated:"
echo "   📄 HTML Report: playwright-report/report.html"

if [ -d "test-results" ]; then
    echo "   🎬 Traces: test-results/"
fi

echo ""
echo "🚀 Opening report..."

# Open the report
if [ -f "playwright-report/report.html" ]; then
    if command -v open &> /dev/null; then
        open playwright-report/report.html
    elif command -v xdg-open &> /dev/null; then
        xdg-open playwright-report/report.html
    else
        echo "   👉 Open manually: playwright-report/report.html"
    fi
fi

echo ""
echo "🔍 To view traces:"
echo "   playwright show-trace test-results/<test-name>/trace.zip"
echo ""

exit $EXIT_CODE
