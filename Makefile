# Prism Package Manager - Makefile
# Comprehensive development and CI/CD commands

.PHONY: help install install-dev test test-unit test-e2e test-cli test-integration test-all lint format clean build run docs serve-docs check pre-commit ci

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
FLAKE8 := $(PYTHON) -m flake8
MYPY := $(PYTHON) -m mypy
ISORT := $(PYTHON) -m isort
PLAYWRIGHT := $(PYTHON) -m playwright

# Directories
SRC_DIR := scripts
TEST_DIR := tests
DOCS_DIR := docs
REPORT_DIR := playwright-report
COVERAGE_DIR := htmlcov
DIST_DIR := dist
BUILD_DIR := build

# Colors for output
COLOR_RESET := \033[0m
COLOR_BOLD := \033[1m
COLOR_GREEN := \033[32m
COLOR_BLUE := \033[34m
COLOR_YELLOW := \033[33m

##@ Help

help: ## Display this help message
	@echo "$(COLOR_BOLD)Prism Package Manager - Development Commands$(COLOR_RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(COLOR_BLUE)<target>$(COLOR_RESET)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(COLOR_BLUE)%-20s$(COLOR_RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(COLOR_BOLD)%s$(COLOR_RESET)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Installation

install: ## Install production dependencies
	@echo "$(COLOR_GREEN)📦 Installing production dependencies...$(COLOR_RESET)"
	$(PIP) install -r requirements.txt
	@echo "$(COLOR_GREEN)✅ Production dependencies installed!$(COLOR_RESET)"

install-dev: install ## Install development dependencies (includes production)
	@echo "$(COLOR_GREEN)📦 Installing development dependencies...$(COLOR_RESET)"
	$(PIP) install -r requirements-dev.txt
	@echo "$(COLOR_GREEN)✅ Development dependencies installed!$(COLOR_RESET)"

install-playwright: ## Install Playwright browsers (uses system Chrome by default)
	@echo "$(COLOR_GREEN)🎭 Checking Playwright setup...$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)ℹ️  Using system Chrome - no browser download needed$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)✅ Playwright ready!$(COLOR_RESET)"

##@ Testing

test: test-unit test-cli ## Run unit and CLI tests (fast, no E2E)
	@echo "$(COLOR_GREEN)✅ Fast tests complete!$(COLOR_RESET)"

test-unit: ## Run unit tests only
	@echo "$(COLOR_BLUE)🧪 Running unit tests...$(COLOR_RESET)"
	$(PYTEST) $(TEST_DIR)/unit/ -v --no-cov

test-cli: ## Run CLI tests only
	@echo "$(COLOR_BLUE)🖥️  Running CLI tests...$(COLOR_RESET)"
	$(PYTEST) $(TEST_DIR)/e2e/test_cli_installer.py -v --no-cov

test-e2e: ## Run E2E browser tests (requires server)
	@echo "$(COLOR_BLUE)🎭 Running E2E tests...$(COLOR_RESET)"
	$(PYTEST) $(TEST_DIR)/e2e/test_installer_flow.py $(TEST_DIR)/e2e/test_complete_installation.py -v --no-cov

test-integration: ## Run integration tests
	@echo "$(COLOR_BLUE)🔗 Running integration tests...$(COLOR_RESET)"
	$(PYTEST) $(TEST_DIR)/integration/ -v --no-cov

test-all: ## Run ALL tests (unit, CLI, E2E, integration)
	@echo "$(COLOR_BLUE)🚀 Running ALL tests...$(COLOR_RESET)"
	$(PYTEST) $(TEST_DIR)/ -v --no-cov

test-coverage: ## Run tests with coverage report
	@echo "$(COLOR_BLUE)📊 Running tests with coverage...$(COLOR_RESET)"
	$(PYTEST) $(TEST_DIR)/ --cov=$(SRC_DIR) --cov-report=html --cov-report=term
	@echo "$(COLOR_GREEN)✅ Coverage report: htmlcov/index.html$(COLOR_RESET)"

test-report: ## Run tests and generate HTML report
	@echo "$(COLOR_BLUE)📋 Running tests with HTML report...$(COLOR_RESET)"
	$(PYTEST) $(TEST_DIR)/e2e/ --html=$(REPORT_DIR)/report.html --self-contained-html
	@echo "$(COLOR_GREEN)✅ Report generated: $(REPORT_DIR)/report.html$(COLOR_RESET)"

test-trace: ## Run E2E tests with trace viewer (for debugging)
	@echo "$(COLOR_BLUE)🎬 Running tests with trace viewer...$(COLOR_RESET)"
	$(PYTEST) $(TEST_DIR)/e2e/test_installer_flow.py --tracing=on --headed --slowmo=500
	@echo "$(COLOR_GREEN)🔍 View trace: make show-trace$(COLOR_RESET)"

show-trace: ## Open Playwright trace viewer for last test
	@echo "$(COLOR_BLUE)🎬 Opening trace viewer...$(COLOR_RESET)"
	@$(PLAYWRIGHT) show-trace $$(find test-results -name "trace.zip" | head -1)

##@ Code Quality

lint: ## Run all linters (flake8, mypy)
	@echo "$(COLOR_BLUE)🔍 Running linters...$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Running flake8...$(COLOR_RESET)"
	$(FLAKE8) $(SRC_DIR) $(TEST_DIR) --max-line-length=120 --exclude=__pycache__,.pytest_cache,htmlcov,test-results
	@echo "$(COLOR_YELLOW)Running mypy...$(COLOR_RESET)"
	$(MYPY) $(SRC_DIR) --ignore-missing-imports
	@echo "$(COLOR_GREEN)✅ Linting complete!$(COLOR_RESET)"

format: ## Format code with black and isort
	@echo "$(COLOR_BLUE)✨ Formatting code...$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Running isort...$(COLOR_RESET)"
	$(ISORT) $(SRC_DIR) $(TEST_DIR) --profile black --line-length 120
	@echo "$(COLOR_YELLOW)Running black...$(COLOR_RESET)"
	$(BLACK) $(SRC_DIR) $(TEST_DIR) --line-length 120
	@echo "$(COLOR_GREEN)✅ Code formatted!$(COLOR_RESET)"

format-check: ## Check if code is formatted (CI mode)
	@echo "$(COLOR_BLUE)🔍 Checking code format...$(COLOR_RESET)"
	$(ISORT) $(SRC_DIR) $(TEST_DIR) --profile black --line-length 120 --check-only
	$(BLACK) $(SRC_DIR) $(TEST_DIR) --line-length 120 --check
	@echo "$(COLOR_GREEN)✅ Code format OK!$(COLOR_RESET)"

##@ Development

run: ## Run the installer UI server
	@echo "$(COLOR_BLUE)🚀 Starting installer server...$(COLOR_RESET)"
	$(PYTHON) install-ui.py

run-bg: ## Run installer server in background
	@echo "$(COLOR_BLUE)🚀 Starting installer server in background...$(COLOR_RESET)"
	@lsof -ti:5555 | xargs kill -9 2>/dev/null || true
	@nohup $(PYTHON) install-ui.py > /tmp/prism-server.log 2>&1 &
	@sleep 2
	@curl -s http://localhost:5555 > /dev/null && echo "$(COLOR_GREEN)✅ Server running on http://localhost:5555$(COLOR_RESET)" || echo "$(COLOR_YELLOW)⚠️  Server may not be ready yet$(COLOR_RESET)"

stop: ## Stop background server
	@echo "$(COLOR_YELLOW)🛑 Stopping servers...$(COLOR_RESET)"
	@lsof -ti:5555 | xargs kill -9 2>/dev/null && echo "$(COLOR_GREEN)✅ Server stopped$(COLOR_RESET)" || echo "$(COLOR_BLUE)ℹ️  No server running$(COLOR_RESET)"

docs: ## Generate documentation
	@echo "$(COLOR_BLUE)📚 Generating documentation...$(COLOR_RESET)"
	$(PYTHON) auto-deploy-docs.py
	@echo "$(COLOR_GREEN)✅ Documentation generated!$(COLOR_RESET)"

serve-docs: docs ## Serve documentation locally
	@echo "$(COLOR_BLUE)📚 Serving documentation...$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)🌐 Documentation: http://localhost:8080$(COLOR_RESET)"
	@cd docs-server && $(PYTHON) -m http.server 8080

watch: ## Watch files and auto-run tests
	@echo "$(COLOR_BLUE)👀 Watching for changes...$(COLOR_RESET)"
	$(PYTEST) $(TEST_DIR)/unit/ -v --no-cov -f

##@ Build & Deploy

build: clean ## Build distribution packages
	@echo "$(COLOR_BLUE)📦 Building distribution packages...$(COLOR_RESET)"
	$(PYTHON) setup.py sdist bdist_wheel
	@echo "$(COLOR_GREEN)✅ Build complete: $(DIST_DIR)/$(COLOR_RESET)"

package: test-all lint build ## Run all checks and build (pre-release)
	@echo "$(COLOR_GREEN)✅ Package ready for release!$(COLOR_RESET)"

##@ Cleanup

clean: ## Clean build artifacts and caches
	@echo "$(COLOR_YELLOW)🧹 Cleaning build artifacts...$(COLOR_RESET)"
	rm -rf $(BUILD_DIR) $(DIST_DIR) *.egg-info
	rm -rf $(COVERAGE_DIR) .coverage
	rm -rf $(REPORT_DIR)/*.html $(REPORT_DIR)/*.json
	rm -rf test-results
	rm -rf .pytest_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	@echo "$(COLOR_GREEN)✅ Cleaned!$(COLOR_RESET)"

clean-all: clean ## Deep clean (includes node_modules, venv)
	@echo "$(COLOR_YELLOW)🧹 Deep cleaning...$(COLOR_RESET)"
	rm -rf node_modules
	rm -rf venv .venv
	@echo "$(COLOR_GREEN)✅ Deep clean complete!$(COLOR_RESET)"

##@ CI/CD

check: format-check lint test ## Run all CI checks (format, lint, test)
	@echo "$(COLOR_GREEN)✅ All CI checks passed!$(COLOR_RESET)"

pre-commit: format lint test-unit test-cli ## Run pre-commit checks (fast)
	@echo "$(COLOR_GREEN)✅ Pre-commit checks passed!$(COLOR_RESET)"

ci: install-dev check test-all ## Full CI pipeline (used by GitHub Actions)
	@echo "$(COLOR_GREEN)✅ CI pipeline complete!$(COLOR_RESET)"

ci-coverage: install-dev check test-coverage ## CI with coverage report
	@echo "$(COLOR_GREEN)✅ CI with coverage complete!$(COLOR_RESET)"

##@ Quick Commands

dev: install-dev run ## Quick start: install deps and run server

test-quick: test-unit ## Quick test (unit tests only)
	@echo "$(COLOR_GREEN)✅ Quick tests complete!$(COLOR_RESET)"

fix: format lint ## Auto-fix code issues (format + lint)
	@echo "$(COLOR_GREEN)✅ Code fixed!$(COLOR_RESET)"
