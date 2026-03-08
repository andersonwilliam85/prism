# CI/CD Setup Complete

## What's Included

This repository now has a **comprehensive CI/CD pipeline** with:

### Development Tools

#### **Makefile** - 40+ Commands
```bash
make help              # See all available commands
make dev               # Quick start: install + run
make test              # Fast tests (unit + CLI)
make test-all          # All tests
make lint              # Run linters
make format            # Auto-format code
make check             # Full CI checks
make pre-commit        # Pre-commit checks
```

### GitHub Actions Workflows

#### **1. Pull Request Checks** (`.github/workflows/ci.yml`)
Runs on PRs to dev, stage, or main:
- ✅ Linting (black, flake8, mypy)
- ✅ Unit tests
- ✅ CLI tests
- ✅ E2E tests (Playwright)
- ✅ Code coverage
- ✅ Security scanning (bandit, safety)

#### **2. Dev Deployment** (`.github/workflows/deploy-dev.yml`)
Runs on push to `dev`:
- Quick tests (lint + unit)
- Build dev snapshot
- Deploy to dev environment
- 7-day artifact retention

#### **3. Stage Deployment** (`.github/workflows/deploy-stage.yml`)
Runs on push to `stage`:
- Comprehensive tests + coverage
- Build release candidate
- Deploy to staging
- Smoke tests
- 30-day artifact retention

#### **4. Production Deployment** (`.github/workflows/deploy-main.yml`)
Runs on push to `main`:
- Full test suite
- Build distribution packages
- Generate checksums (SHA256)
- Create GitHub Release (for tags)
- Deploy to production
- **90-day artifact retention**

### Branch Protection

#### **Main Branch** (Production)
- ✅ 2 required approvals
- ✅ All CI checks must pass
- ✅ Conversation resolution required
- ✅ Signed commits required
- ✅ Linear history enforced
- ✅ Admins cannot bypass

#### **Stage Branch** (Pre-Production)
- ✅ 1 required approval
- ✅ All CI checks must pass
- ✅ Linear history enforced

#### **Dev Branch** (Development)
- ✅ 1 required approval
- ✅ Basic CI checks (lint, unit, CLI)

### Templates & Guidelines

- **Pull Request Template** - Comprehensive PR checklist
- **CODEOWNERS** - Automatic reviewer assignment
- **Branch Protection Guide** - Setup instructions
- **CI/CD Documentation** - Complete workflow guide

---

## Quick Start

### 1. Install Dependencies
```bash
make install-dev
```

### 2. Run Tests
```bash
make test           # Fast tests
make test-all       # All tests
make test-coverage  # With coverage
```

### 3. Format & Lint
```bash
make format  # Auto-format code
make lint    # Check code quality
```

### 4. Run Server
```bash
make run     # Foreground
make run-bg  # Background
make stop    # Stop background server
```

---

## Workflow

### Feature Development
```bash
# 1. Create feature branch from dev
git checkout dev
git pull origin dev
git checkout -b feature/my-feature

# 2. Make changes
# ... write code ...

# 3. Test and format
make pre-commit

# 4. Commit and push
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature

# 5. Create PR to dev
# Fill out PR template
# Wait for CI checks
# Get 1 approval
# Merge!
```

### Release Process
```
feature/xyz  →  dev  →  stage  →  main
   (PR)        (PR)    (PR)
   1 approval  1 approval  2 approvals
   Basic CI    Full CI     Full CI + Release
   Dev deploy  Stage deploy Production deploy
   7-day artifacts  30-day artifacts  90-day artifacts
```

---

## Setup CI/CD

### Option 1: Automated (GitHub CLI)
```bash
# Requires: gh CLI (https://cli.github.com/)
cd .github
./setup-cicd.sh
```

### Option 2: Manual
1. Go to **Repository Settings** → **Branches**
2. Add protection rules for `main`, `stage`, `dev`
3. Follow guide: `.github/BRANCH_PROTECTION.md`

### Configure Secrets (Optional)
```bash
gh secret set SLACK_WEBHOOK_URL      # Slack notifications
gh secret set TEAMS_WEBHOOK_URL      # Teams notifications
gh secret set DEPLOY_SSH_KEY         # Deployment SSH key
```

---

## Monitoring

### View Workflow Runs
```bash
gh run list                 # List all runs
gh run view <run-id>        # View specific run
gh run watch                # Watch current run
```

### Download Artifacts
```bash
gh run download <run-id> -n prism-release-v1.0.0
```

### View Test Reports
1. Go to **Actions** tab
2. Click on workflow run
3. Scroll to **Artifacts**
4. Download `test-results` or `coverage-report`
5. Open `playwright-report/report.html`

---

## Documentation

| Document | Purpose |
|----------|--------|
| `Makefile` | Development commands |
| `.github/CI_CD.md` | Complete CI/CD guide |
| `.github/BRANCH_PROTECTION.md` | Branch protection setup |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR template |
| `.github/CODEOWNERS` | Code ownership |
| `DASHBOARD_COMMANDS.md` | Test dashboard commands |
| `docs/PLAYWRIGHT_DASHBOARDS.md` | Playwright guides |

---

## Checklist

### For Developers:
- [ ] Install dev dependencies: `make install-dev`
- [ ] Run pre-commit before pushing: `make pre-commit`
- [ ] Fill out PR template completely
- [ ] Ensure CI checks pass
- [ ] Get required approvals

### For Maintainers:
- [ ] Run setup script: `.github/setup-cicd.sh`
- [ ] Update CODEOWNERS with team names
- [ ] Configure GitHub secrets (if needed)
- [ ] Test workflows on dev branch first
- [ ] Document deployment steps

### For Production:
- [ ] All tests passing: `make test-all`
- [ ] Code formatted: `make format-check`
- [ ] Linting clean: `make lint`
- [ ] Coverage adequate: `make test-coverage`
- [ ] Documentation updated
- [ ] CHANGELOG updated (if applicable)

---

## Troubleshooting

### Tests Failing?
```bash
# Run what CI runs
make ci

# Debug specific test
pytest tests/path/to/test.py -v --pdb

# View trace for E2E tests
make test-trace
make show-trace
```

### Format Issues?
```bash
# Auto-fix
make format

# Check only
make format-check
```

### Can't Merge?
Check:
1. All CI checks passing?
2. Required approvals received?
3. Conversations resolved?
4. Branch up to date?

---

## You're All Set!

Your repository now has:
- ✅ Professional CI/CD pipeline
- ✅ Automated testing
- ✅ Code quality checks
- ✅ Security scanning
- ✅ Branch protection
- ✅ Artifact management
- ✅ Comprehensive documentation

**Start developing with confidence!** 🚀

```bash
make dev  # Let's go!
```
