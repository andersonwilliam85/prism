#!/bin/bash
# Run Playwright tests with UI mode (interactive dashboard)

set -e

echo "🎭 Playwright Interactive Dashboard"
echo "===================================="
echo ""
echo "This will open the Playwright UI where you can:"
echo "  • See all tests in a visual interface"
echo "  • Run tests with live browser preview"
echo "  • Debug tests step-by-step"
echo "  • View traces and screenshots"
echo "  • Watch tests in real-time"
echo ""
echo "Starting Playwright UI..."
echo ""

# Check if playwright is installed
if ! python3 -m playwright --version > /dev/null 2>&1; then
    echo "❌ Playwright not installed"
    echo "Installing..."
    pip install -r requirements-test.txt
    python3 -m playwright install
fi

# Run Playwright in UI mode
pytest tests/e2e/ --headed --slowmo=500 --ui
