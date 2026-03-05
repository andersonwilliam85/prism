# CI/CD Pipeline Documentation

Comprehensive CI/CD setup for Prism Package Manager using GitHub Actions.

---

## 🎯 Overview

### Branch Strategy

```
main (production)    ← PR from stage (2 approvals required)
  ↑
stage (pre-prod)     ← PR from dev (1 approval required)
  ↑
dev (development)    ← PR from feature/* (1 approval required)
  ↑
feature/xyz (work)
```

### Workflow Summary

| Workflow | Trigger | Purpose | Artifacts |
|----------|---------|---------|----------|
| `ci.yml` | PR to dev/stage/main | Run tests, lint, security | Test reports, coverage |
| `deploy-dev.yml` | Push to dev | Deploy to dev env | Dev snapshot (7 days) |
| `deploy-stage.yml` | Push to stage | Deploy to stage env | RC build (30 days) |
| `deploy-main.yml` | Push to main | Deploy to production | Release artifacts (90 days) |

---

## 🛠️ Makefile Commands

### Quick Reference

```bash
# Development
make help              # Show all commands
make install-dev       # Install dev dependencies
make run               # Start installer server
make dev               # Install + run (quick start)

# Testing
make test              # Fast tests (unit + CLI)
make test-all          # All tests (unit + CLI + E2E + integration)
make test-coverage     # Tests with coverage report
make test-report       # Generate HTML test report
make test-trace        # E2E tests with trace viewer

# Code Quality
make lint              # Run linters (flake8, mypy)
make format            # Auto-format code (black, isort)
make format-check      # Check format (CI mode)

# CI/CD
make check             # All CI checks (format + lint + test)
make pre-commit        # Quick pre-commit checks
make ci                # Full CI pipeline

# Cleanup
make clean             # Remove build artifacts
make clean-all         # Deep clean (includes venv)
```

---

## 🔄 CI Workflow (`ci.yml`)

### Triggered On:
- Pull requests to `dev`, `stage`, or `main`

### Jobs:

#### 1️⃣ Lint Job
```yaml
Steps:
- Checkout code
- Setup Python 3.9
- Install dependencies (cached)
- Run black format check
- Run flake8 linter
- Run mypy type checker
```

#### 2️⃣ Unit Tests
```yaml
Steps:
- Checkout code
- Setup Python 3.9
- Install dependencies
- Run unit tests (pytest)
- Upload test results
```

#### 3️⃣ CLI Tests
```yaml
Steps:
- Checkout code
- Setup Python 3.9
- Install dependencies
- Run CLI tests
```

#### 4️⃣ E2E Tests
```yaml
Steps:
- Checkout code
- Setup Python 3.9
- Install dependencies
- Install Playwright browsers
- Run E2E tests
- Upload test reports
- Upload traces (on failure)
```

#### 5️⃣ Coverage
```yaml
Steps:
- Checkout code
- Setup Python 3.9
- Install dependencies
- Run tests with coverage
- Upload coverage report
- Comment coverage on PR
```

#### 6️⃣ Security Scan
```yaml
Steps:
- Run safety check (dependencies)
- Run bandit (code security)
- Upload security reports
```

#### 7️⃣ PR Summary
```yaml
Dependencies: All above jobs
Purpose: Final gate - fail if any check fails
```

---

## 🔵 Dev Deployment (`deploy-dev.yml`)

### Triggered On:
- Push to `dev` branch

### Jobs:

1. **Quick Tests** - Lint + unit tests (fast feedback)
2. **Build Dev Snapshot** - Create `dev-{sha}.tar.gz`
3. **Deploy to Dev** - Deploy to dev environment
4. **Notify Team** - Send notifications

### Artifacts:
- Retention: **7 days**
- Naming: `prism-dev-{sha}`

---

## 🟡 Stage Deployment (`deploy-stage.yml`)

### Triggered On:
- Push to `stage` branch

### Jobs:

1. **Comprehensive Tests** - All tests + coverage
2. **Build RC Package** - Create release candidate
3. **Deploy to Stage** - Deploy to staging environment
4. **Smoke Tests** - Run smoke tests against stage
5. **Notify Team** - Send notifications

### Artifacts:
- Retention: **30 days**
- Naming: `prism-stage-{sha}`
- Includes: Distribution packages + checksums

---

## 🔴 Main Deployment (`deploy-main.yml`)

### Triggered On:
- Push to `main` branch
- Git tags (for releases)

### Jobs:

1. **Full Test Suite** - All tests with reports
2. **Build Distribution**
   - Build wheel and source dist
   - Generate checksums (SHA256)
   - Create release archive
   - Version from git tag or SHA
3. **Publish Artifacts**
   - Upload to GitHub Artifacts (90 days)
   - Create GitHub Release (for tagged commits)
4. **Deploy to Production**
   - Deploy to production environment
5. **Notify Team** - Send deployment notifications

### Artifacts:
- Retention: **90 days**
- Naming: `prism-release-{version}`
- Includes:
  - Python wheel (`.whl`)
  - Source distribution (`.tar.gz`)
  - Release archive (complete source)
  - SHA256 checksums

### GitHub Release:
Created automatically for tagged commits:
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

---

## 🔒 Branch Protection Rules

See `.github/BRANCH_PROTECTION.md` for detailed configuration.

### Main Branch:
- ✅ 2 required approvals
- ✅ All CI checks must pass
- ✅ Conversation resolution required
- ✅ Signed commits required
- ✅ Linear history enforced
- ✅ Admins cannot bypass

### Stage Branch:
- ✅ 1 required approval
- ✅ All CI checks must pass
- ✅ Conversation resolution required
- ✅ Linear history enforced

### Dev Branch:
- ✅ 1 required approval
- ✅ Basic CI checks (lint, unit, CLI tests)
- ✅ Conversation resolution required

---

## 📝 Pull Request Process

### 1. Create Feature Branch
```bash
git checkout dev
git pull origin dev
git checkout -b feature/my-awesome-feature
```

### 2. Make Changes
```bash
# Write code
vim scripts/my_feature.py

# Format and lint
make format
make lint

# Test
make test

# Commit
git add .
git commit -m "feat: add awesome feature"
```

### 3. Push and Create PR
```bash
git push origin feature/my-awesome-feature

# Then create PR on GitHub
# Fill out the PR template
```

### 4. CI Runs Automatically
- Linting
- Unit tests
- CLI tests
- E2E tests
- Coverage
- Security scan

### 5. Code Review
- Request reviews from CODEOWNERS
- Address feedback
- Resolve conversations

### 6. Merge
- All checks green ✅
- Required approvals received
- Squash and merge to dev

---

## 🚀 Release Process

### Standard Release (dev → stage → main)

```bash
# 1. Merge feature to dev
feature/xyz → dev (PR)
  ↓
  CI runs (fast tests)
  Deploy to dev environment

# 2. Promote dev to stage
dev → stage (PR)
  ↓
  CI runs (full tests + coverage)
  Build RC package
  Deploy to stage environment
  Smoke tests

# 3. Promote stage to main
stage → main (PR)
  ↓
  CI runs (full test suite)
  Build production artifacts
  Create GitHub Release (if tagged)
  Deploy to production
  90-day artifact retention
```

### Hotfix Release (emergency)

```bash
# 1. Branch from main
git checkout main
git checkout -b hotfix/critical-bug

# 2. Fix and test
make test-all

# 3. PR directly to main (with justification)
hotfix/critical-bug → main (PR)
  ↓
  Requires 2 approvals + CI green

# 4. Backport to stage and dev
git checkout stage
git cherry-pick <commit-sha>
git push origin stage

git checkout dev
git cherry-pick <commit-sha>
git push origin dev
```

---

## 📊 Monitoring & Artifacts

### View Workflow Runs
```bash
gh run list
gh run view <run-id>
gh run watch  # Watch current run
```

### Download Artifacts
```bash
# List artifacts
gh run list --workflow=deploy-main.yml

# Download specific artifact
gh run download <run-id> -n prism-release-v1.0.0
```

### View Test Reports
1. Go to Actions tab
2. Click on workflow run
3. Scroll to Artifacts section
4. Download test reports
5. Open `playwright-report/report.html`

---

## 🔧 Troubleshooting

### CI Failing?

```bash
# Run locally what CI runs
make ci

# Or step by step
make format-check  # Check formatting
make lint          # Check linting
make test-all      # Run all tests
```

### Playwright Tests Failing?

```bash
# Run with trace viewer
make test-trace

# Then view trace
make show-trace

# Or run headed (see browser)
pytest tests/e2e/ --headed --slowmo=500
```

### Merge Conflicts?

```bash
# Update your branch
git fetch origin
git rebase origin/dev  # or stage/main

# Resolve conflicts
git add .
git rebase --continue

# Force push (only to feature branches!)
git push --force-with-lease
```

### Can't Merge PR?

Check:
1. Are all CI checks passing? ✅
2. Do you have required approvals?
3. Are all conversations resolved?
4. Is branch up to date with base?
5. Are you merging to the right branch?

---

## 🔐 Secrets Management

### Required Secrets (set in GitHub repo settings):

```bash
# GitHub Actions secrets
GITHUB_TOKEN          # Auto-provided by GitHub

# Optional (for notifications)
SLACK_WEBHOOK_URL     # For Slack notifications
TEAMS_WEBHOOK_URL     # For Teams notifications

# Optional (for deployments)
DEPLOY_SSH_KEY        # For SSH deployments
DEPLOY_API_TOKEN      # For API-based deployments
```

### Set secrets:
```bash
gh secret set SLACK_WEBHOOK_URL
gh secret set DEPLOY_SSH_KEY < ~/.ssh/deploy_key
```

---

## 📚 Additional Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Makefile Docs](https://www.gnu.org/software/make/manual/)
- [Branch Protection Guide](.github/BRANCH_PROTECTION.md)
- [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md)
- [Code Owners](.github/CODEOWNERS)

---

## ✅ Quick Checklist

### For Developers:
- [ ] Run `make pre-commit` before pushing
- [ ] Fill out PR template completely
- [ ] Request reviews from CODEOWNERS
- [ ] Respond to review feedback
- [ ] Ensure all CI checks pass

### For Maintainers:
- [ ] Configure branch protection rules
- [ ] Set up GitHub secrets
- [ ] Update CODEOWNERS with team names
- [ ] Test CI workflows on dev branch first
- [ ] Document any custom deployment steps

### For CI/CD:
- [ ] All workflows in `.github/workflows/`
- [ ] Branch protection rules configured
- [ ] Secrets configured
- [ ] Artifacts retention set appropriately
- [ ] Notifications configured
