# Installation

Complete guide to installing and setting up Prism Package Manager.

---

## Prerequisites

### Required

- **Python 3.9 or higher**
  ```bash
  python3 --version  # Should show 3.9+
  ```

- **Internet connection** (for fetching npm packages)

### Recommended

- **Git** (for cloning the repository)
- **Make** (for using Makefile commands)

---

## Installation Methods

### Method 1: Clone from GitHub (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/andersonwilliam85/prism.git
cd prism

# 2. Install dependencies
make install-dev

# 3. Verify installation
make test

# 4. Start the web UI
make run
# Opens automatically at http://localhost:5555
```

### Method 2: Download ZIP

```bash
# 1. Download from GitHub
curl -L https://github.com/andersonwilliam85/prism/archive/main.zip -o prism.zip

# 2. Extract
unzip prism.zip
cd prism-main

# 3. Install dependencies
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-dev.txt

# 4. Run the installer
python3 install-ui.py
```

### Method 3: Development Setup

For contributors and developers:

```bash
# 1. Fork the repo on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/prism.git
cd prism

# 3. Add upstream remote
git remote add upstream https://github.com/andersonwilliam85/prism.git

# 4. Install development dependencies
make install-dev

# 5. Install Playwright browsers (for E2E tests)
make install-playwright

# 6. Run all tests
make test-all

# 7. Start development server
make dev
```

---

## Platform-Specific Instructions

### macOS

**Python 3 is pre-installed** on macOS 10.15+:

```bash
# Verify Python version
python3 --version

# If Python < 3.9, install via Homebrew
brew install python@3.11

# Clone and install
git clone https://github.com/andersonwilliam85/prism.git
cd prism
make install-dev
make run
```

### Windows

**Install Python first** from [python.org](https://www.python.org/downloads/):

```powershell
# Verify Python installation
python --version

# Clone (requires Git for Windows)
git clone https://github.com/andersonwilliam85/prism.git
cd prism

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run the installer
python install-ui.py
```

**Note**: On Windows, use `python` instead of `python3`.

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python 3.9+ if not present
sudo apt install python3.11 python3-pip python3-venv

# Clone and install
git clone https://github.com/andersonwilliam85/prism.git
cd prism
make install-dev
make run
```

### Linux (Fedora/RHEL)

```bash
# Install Python 3.9+
sudo dnf install python3.11 python3-pip

# Clone and install
git clone https://github.com/andersonwilliam85/prism.git
cd prism
make install-dev
make run
```

---

## Dependency Installation

### Production Dependencies

```bash
# Install only what's needed to run Prism
make install
# or
pip install -r requirements.txt
```

**Includes:**
- Flask (web UI server)
- PyYAML (configuration parsing)
- Jinja2 (templating)
- Requests (HTTP client)

### Development Dependencies

```bash
# Install everything (production + testing + linting)
make install-dev
# or
pip install -r requirements-dev.txt
```

**Includes production dependencies plus:**
- pytest (testing framework)
- playwright (E2E testing)
- black (code formatting)
- flake8 (linting)
- mypy (type checking)
- coverage (test coverage)

### Playwright Browsers

For running E2E tests:

```bash
# Install Playwright browsers
make install-playwright
# or
python3 -m playwright install
```

---

## Verification

### Test Installation

```bash
# Run quick tests
make test

# Expected output:
# ===== test session starts =====
# tests/unit/... PASSED
# tests/e2e/... PASSED
# ===== X passed in Y.YYs =====
```

### Launch Web UI

```bash
# Start the installer
make run
# or
python3 install-ui.py

# Should open browser at:
# http://localhost:5555
```

### Verify CLI

```bash
# Run CLI installer
python3 install.py --help

# Should show usage information
```

---

## Troubleshooting

### Python Version Too Old

**Error**: `Python 3.9 or higher required`

**Solution**:
```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11

# Fedora/RHEL
sudo dnf install python3.11
```

### Flask Not Found

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
make install-dev
# or
pip install Flask
```

### Port 5555 Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Use a different port
python3 install-ui.py --port 8080

# Or kill the process using port 5555
lsof -ti:5555 | xargs kill -9
```

### Permission Errors

**Error**: `Permission denied`

**Solution**:
```bash
# Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Then install
make install-dev
```

### Git Not Installed

**Error**: `git: command not found`

**Solution**:
```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt install git

# Windows
# Download from https://git-scm.com/
```

---

## Custom Registry Setup

For corporate/air-gapped environments:

### Environment Variable

```bash
# Set npm registry URL
export PRISM_NPM_REGISTRY=https://npm.mycompany.com

# Install packages from custom registry
python3 install.py
```

### Command-Line Option

```bash
python3 install.py --npm-registry https://npm.mycompany.com
```

### Configuration File

```yaml
# ~/.prism/config.yaml
npm_registry: https://npm.mycompany.com
```

See [Custom Registries](../user-guide/custom-registries.md) for detailed setup.

---

## Uninstallation

### Remove Installation

```bash
# Navigate to prism directory
cd ~/path/to/prism

# Clean all artifacts
make clean-all

# Remove directory
cd ..
rm -rf prism
```

### Remove Dependencies

```bash
# If using virtual environment
deactivate
rm -rf venv

# Or uninstall packages
pip uninstall -r requirements.txt
pip uninstall -r requirements-dev.txt
```

---

## Next Steps

- ✅ **Installation complete!**
- 🚀 [Quickstart Guide](quickstart.md) - Get started in 5 minutes
- 🎭 [Create Your First Configuration](first-configuration.md) - Build a custom config
- 📖 [User Guide](../user-guide/choosing-a-package.md) - Choose the right package

---

**Need help?** [Open an issue](https://github.com/andersonwilliam85/prism/issues)
