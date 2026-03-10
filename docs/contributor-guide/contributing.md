---
layout: default
title: Contributing
---

# Contributing to Prism

Thank you for considering contributing to Prism! 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Testing](#testing)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)

---

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to make development better!

---

## Getting Started

### Prerequisites

- Python 3.9+
- Git
- pip or uv

### Fork & Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/prism.git
cd prism

# Add upstream remote
git remote add upstream https://github.com/original/prism.git
```

---

## Development Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### 3. Install Playwright

```bash
python -m playwright install
```

### 4. Run Tests

```bash
pytest
```

If all tests pass, you're ready to develop! ✅

---

## Testing

See [Testing](testing.md) for comprehensive testing guide.

### Quick Reference

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test type
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run in watch mode (install pytest-watch)
ptw
```

### Writing Tests

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **E2E tests**: Test full user workflows with Playwright

**Coverage requirement**: >90%

---

## Coding Standards

### Python Style

We follow **PEP 8** with some modifications:

- Line length: 100 characters (not 79)
- Use `black` for formatting
- Use `isort` for import sorting
- Use type hints where appropriate

### Format Code

```bash
# Auto-format with black
black .

# Sort imports
isort .

# Check with flake8
flake8 .
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: Add new theme system
fix: Fix package validation error
docs: Update testing guide
chore: Update dependencies
refactor: Simplify config merger
test: Add E2E tests for installer
```

**Format**: `<type>: <description>`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `chore`: Maintenance
- `refactor`: Code refactoring
- `test`: Add/update tests
- `perf`: Performance improvement

---

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write code
- Add tests (>90% coverage)
- Update documentation
- Format code (`black .` and `isort .`)

### 3. Test Locally

```bash
# Run all tests
pytest

# Check coverage
pytest --cov=. --cov-report=term-missing

# Lint
flake8 .
```

### 4. Commit

```bash
git add .
git commit -m "feat: Add awesome feature"
```

### 5. Push

```bash
git push origin feature/your-feature-name
```

### 6. Open Pull Request

- Go to GitHub
- Click "New Pull Request"
- Fill in the template:

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Coverage >90%

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### 7. Code Review

- Address feedback
- Make requested changes
- Push updates (they'll appear in PR automatically)

### 8. Merge

Once approved, maintainers will merge your PR. Thank you! 🎉

---

## Project Structure

```
prism/
├── install.py              # CLI installer
├── install-ui.py           # Web UI installer
├── installer_engine.py     # Core installation logic
├── requirements.txt        # Dependencies
├── requirements-test.txt   # Test dependencies
├── pytest.ini              # Pytest configuration
├── conftest.py             # Pytest fixtures
│
├── docs/                   # Documentation
│   ├── TESTING.md
│   ├── PACKAGE_SYSTEM.md
│   └── ...
│
├── prisms/                 # Prism packages
│   ├── core.prism/
│   ├── startup.prism/
│   └── ...
│
├── scripts/                # Utility scripts
│   ├── package_validator.py
│   ├── package_manager.py
│   └── ...
│
├── tests/                  # Test suite
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
│
└── .github/
    └── workflows/
        └── tests.yml       # CI/CD
```

---

## Adding a New Feature

### Example: Adding a New Theme

1. **Write tests first** (TDD):

```python
# tests/unit/test_themes.py
def test_new_theme_applies():
    # Test code
    pass
```

2. **Implement feature**:

```python
# Update theme system
# Add new theme CSS
```

3. **Update docs**:

```markdown
# README.md
- Added new "Sunset" theme
```

4. **Test locally**:

```bash
pytest
```

5. **Submit PR**!

---

## Adding a New Prism

See [Package System](../reference/package-system.md) for creating custom prisms.

**Quick steps**:

1. Create `prisms/your-prism/`
2. Add `package.yaml`
3. Add `README.md`
4. Add tests
5. Submit PR

---

## Questions?

- Open an issue: [GitHub Issues](https://github.com/prism/prism/issues)
- Start a discussion: [GitHub Discussions](https://github.com/prism/prism/discussions)

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🚀✨
