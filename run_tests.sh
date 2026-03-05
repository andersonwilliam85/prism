#!/bin/bash
# Run all tests with coverage

set -e

echo "🧪 Running Prism Test Suite"
echo "============================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if test dependencies are installed
if ! python3 -m pytest --version > /dev/null 2>&1; then
    echo -e "${RED}❌ pytest not found${NC}"
    echo "Installing test dependencies..."
    pip install -r requirements-test.txt
fi

if ! python3 -m playwright --version > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Playwright not found${NC}"
    echo "Installing Playwright..."
    python3 -m playwright install
fi

echo -e "${GREEN}✅ Test dependencies ready${NC}"
echo ""

# Run different test types
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Running Unit Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pytest tests/unit/ -v --cov=scripts --cov-report=term-missing

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 Running Integration Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pytest tests/integration/ -v

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Running E2E Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pytest tests/e2e/ -v --headed=false --slowmo=0

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Generating Coverage Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pytest --cov=. --cov-report=html --cov-report=term-missing

echo ""
echo -e "${GREEN}✅ All tests completed!${NC}"
echo ""
echo "📈 Coverage report: htmlcov/index.html"
echo ""

# Check if we can open the coverage report
if command -v open &> /dev/null; then
    echo "Opening coverage report..."
    open htmlcov/index.html
elif command -v xdg-open &> /dev/null; then
    echo "Opening coverage report..."
    xdg-open htmlcov/index.html
fi
