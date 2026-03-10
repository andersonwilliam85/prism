---
layout: default
title: CI/CD Pipeline
---

# CI/CD Pipeline

Complete automation pipeline for Prism Package Manager.

---

## Overview

Prism uses **GitHub Actions** for continuous integration and deployment with a multi-stage workflow:

```
feature/* → dev → stage → main
    ↓       ↓      ↓       ↓
   PR(1)   PR(1)  PR(2)  Release
   Basic   Full   Full   GitHub
   CI      CI     CI     Release
```

**4 Workflows:**
1. **ci.yml** - PR checks (lint, test, coverage, security)
2. **deploy-dev.yml** - Dev deployment (7-day artifacts)
3. **deploy-stage.yml** - Stage deployment (30-day artifacts)
4. **deploy-main.yml** - Production deployment (90-day artifacts + releases)

---

## Makefile Commands

### Quick Reference

```bash
make help              # See all 40+ commands

# Development
make dev               # Quick start (install + run)
make run               # Start installer server

# Testing
make test              # Fast tests (unit + CLI)
make test-all          # All tests (72 tests)
make test-coverage     # With coverage report

# Code Quality
make format            # Auto-format (black + isort)
make lint              # Run linters (flake8 + mypy)
make format-check      # Check format (CI mode)

# CI/CD
make check             # All CI checks
make pre-commit        # Quick pre-commit checks
make ci                # Full CI pipeline
```

See all commands: `make help`

---

## Workflows

### 1. Pull Request Checks (`ci.yml`)

**Trigger:** PR to `dev`, `stage`, or `main`

**Jobs (run in parallel):**
- ✅ **Lint** → black, flake8, mypy
- ✅ **Unit Tests** → pytest tests/unit/
- ✅ **CLI Tests** → pytest tests/e2e/test_cli_installer.py
- ✅ **E2E Tests** → Playwright browser tests
- ✅ **Coverage** → Generate coverage report
- ✅ **Security** → bandit + safety scans
- ✅ **Summary** → Final gate (all must pass)

**Artifacts:**
- Test results (HTML reports)
- Coverage reports (HTML)
- Playwright traces (on failure)
- Security scan results

### 2. Dev Deployment (`deploy-dev.yml`)

**Trigger:** Push to `dev` branch

**Jobs:**
1. Quick Tests → lint + unit (fast feedback)
2. Build → Create `dev-{sha}.tar.gz`
3. Deploy → Deploy to dev environment
4. Notify → Send notifications

**Artifacts:**
- `prism-dev-{sha}.tar.gz`
- **Retention: 7 days**

### 3. Stage Deployment (`deploy-stage.yml`)

**Trigger:** Push to `stage` branch

**Jobs:**
1. Comprehensive Tests → All tests + coverage
2. Build RC → Release candidate package
3. Deploy → Deploy to stage
4. Smoke Tests → Verify deployment
5. Notify → Send notifications

**Artifacts:**
- `prism-stage-{sha}.tar.gz`
- Python wheel (.whl)
- Source dist (.tar.gz)
- SHA256 checksums
- **Retention: 30 days**

### 4. Production Deployment (`deploy-main.yml`)

**Trigger:** Push to `main` branch OR git tag

**Jobs:**
1. Full Test Suite → All 72 tests
2. Build Distribution → Wheel + source + archive
3. Publish Artifacts → Upload to GitHub
4. GitHub Release → Auto-create (if tagged)
5. Deploy Production → Deploy to prod
6. Notify → Send notifications

**Artifacts:**
- `prism-release-{version}.tar.gz` (complete source)
- Python wheel (.whl)
- Source distribution (.tar.gz)
- SHA256SUMS.txt
- **Retention: 90 days**

**GitHub Release (for tags):**
- Automatic release notes
- All artifacts attached
- Installation instructions

---

## Branch Protection

### Main Branch (Production)

- ✅ 2 required approvals
- ✅ All CI checks must pass
- ✅ Conversation resolution required
- ✅ Signed commits required
- ✅ Linear history enforced
- ✅ Admins cannot bypass
- ✅ CODEOWNERS review required

### Stage Branch (Pre-Production)

- ✅ 1 required approval
- ✅ All CI checks must pass
- ✅ Conversation resolution required
- ✅ Linear history enforced

### Dev Branch (Development)

- ✅ 1 required approval
- ✅ Basic CI checks (lint, unit, CLI)
- ✅ Conversation resolution required

---

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout dev
git pull origin dev
git checkout -b feature/my-feature
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
git commit -m "feat: add my feature"
```

### 3. Push and Create PR

```bash
git push origin feature/my-feature

# Create PR on GitHub
# Fill out PR template
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

## Release Process

### Standard Release (dev → stage → main)

```bash
# 1. Merge feature to dev
feature/xyz → dev (PR)
  ↓
  CI runs (fast tests)
  Deploy to dev environment
  7-day artifacts

# 2. Promote dev to stage
dev → stage (PR)
  ↓
  CI runs (full tests + coverage)
  Build RC package
  Deploy to stage environment
  Smoke tests
  30-day artifacts

# 3. Promote stage to main
stage → main (PR)
  ↓
  CI runs (full test suite)
  Build production artifacts
  Deploy to production
  90-day artifacts

# 4. Tag for GitHub Release (optional)
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
  ↓
  Create GitHub Release with artifacts
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

## Local CI Simulation

Run what CI runs locally:

```bash
# All checks
make ci

# Step by step
make format-check  # Check formatting
make lint          # Run linters
make test-all      # Run all tests

# Pre-commit checks (quick)
make pre-commit
```

---

## Setup CI/CD

### Option 1: Automated (GitHub CLI)

```bash
cd .github
./setup-cicd.sh

# Follow prompts:
# 1. Enter repo (owner/repo)
# 2. Script sets up branch protection
# 3. Update CODEOWNERS with team names
# 4. Done!
```

### Option 2: Manual

1. Go to **Settings** → **Branches**
2. Add protection rules for:
   - `main` (2 approvals, all checks)
   - `stage` (1 approval, all checks)
   - `dev` (1 approval, basic checks)
3. See `.github/BRANCH_PROTECTION.md` for details

---

## Monitoring

### View Workflow Runs

```bash
gh run list                    # All runs
gh run view <run-id>           # Specific run
gh run watch                   # Watch live
```

### Download Artifacts

```bash
gh run download <run-id> -n prism-release-v1.0.0
```

### View Test Reports

1. **Actions** tab → Click run
2. Scroll to **Artifacts**
3. Download `test-results`
4. Open `playwright-report/report.html`

---

## Troubleshooting

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

# View trace
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

## Secrets Management

### Required Secrets

Set in GitHub repo settings:

```bash
GITHUB_TOKEN          # Auto-provided by GitHub

# Optional (for notifications)
SLACK_WEBHOOK_URL     # Slack notifications
TEAMS_WEBHOOK_URL     # Teams notifications

# Optional (for deployments)
DEPLOY_SSH_KEY        # SSH deployments
DEPLOY_API_TOKEN      # API-based deployments
```

### Set Secrets

```bash
gh secret set SLACK_WEBHOOK_URL
gh secret set DEPLOY_SSH_KEY < ~/.ssh/deploy_key
```

---

## Status

| Component | Status |
|-----------|--------|
| Makefile | ✅ Complete (40+ commands) |
| PR Checks | ✅ Complete (7 jobs) |
| Dev Deploy | ✅ Complete |
| Stage Deploy | ✅ Complete |
| Prod Deploy | ✅ Complete |
| Branch Protection | ⚠️ Setup Required |
| Documentation | ✅ Complete |
| Tests | ✅ Working (72 tests) |

---

## Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Makefile Guide](../../Makefile)
- [Branch Protection](.github/BRANCH_PROTECTION.md)
- [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md)
- [CODEOWNERS](.github/CODEOWNERS)

---

**Questions?** [Open an issue](https://github.com/andersonwilliam85/prism/issues)
