# Branch Protection Rules Configuration

This document describes the recommended branch protection rules for Prism.

## How to Configure

Go to: **Repository Settings** → **Branches** → **Add branch protection rule**

---

## 🔒 Main Branch Protection

**Branch name pattern:** `main`

### Required Settings:

- ☑️ **Require a pull request before merging**
  - ☑️ Require approvals: **2**
  - ☑️ Dismiss stale pull request approvals when new commits are pushed
  - ☑️ Require review from Code Owners

- ☑️ **Require status checks to pass before merging**
  - ☑️ Require branches to be up to date before merging
  - Required status checks:
    - `lint`
    - `test-unit`
    - `test-cli`
    - `test-e2e`
    - `coverage`

- ☑️ **Require conversation resolution before merging**

- ☑️ **Require signed commits**

- ☑️ **Require linear history**

- ☑️ **Include administrators** (enforce rules for admins too)

- ☑️ **Restrict who can push to matching branches**
  - Allow: **Maintainers only**

- ☑️ **Do not allow bypassing the above settings**

---

## 🟡 Stage Branch Protection

**Branch name pattern:** `stage`

### Required Settings:

- ☑️ **Require a pull request before merging**
  - ☑️ Require approvals: **1**
  - ☑️ Dismiss stale pull request approvals when new commits are pushed

- ☑️ **Require status checks to pass before merging**
  - ☑️ Require branches to be up to date before merging
  - Required status checks:
    - `lint`
    - `test-unit`
    - `test-cli`
    - `test-e2e`
    - `coverage`

- ☑️ **Require conversation resolution before merging**

- ☑️ **Require linear history**

- ☑️ **Restrict who can push to matching branches**
  - Allow: **Developers and Maintainers**

---

## 🟢 Dev Branch Protection

**Branch name pattern:** `dev`

### Required Settings:

- ☑️ **Require a pull request before merging**
  - ☑️ Require approvals: **1**

- ☑️ **Require status checks to pass before merging**
  - Required status checks:
    - `lint`
    - `test-unit`
    - `test-cli`

- ☑️ **Require conversation resolution before merging**

- ☐ **Require linear history** (optional for dev)

---

## 🔄 Merge Strategy

### Recommended Merge Flow:

```
feature/xyz  →  dev  →  stage  →  main
   (PR)        (PR)    (PR)
```

### Merge Methods:

- **main**: Squash and merge (clean history)
- **stage**: Squash and merge or Rebase
- **dev**: Merge commit allowed

---

## ⚙️ Additional Repository Settings

### General Settings:

- ☑️ **Automatically delete head branches** (after PR merge)
- ☑️ **Allow squash merging**
- ☑️ **Allow rebase merging**
- ☐ **Allow merge commits** (only for dev)

### Security:

- ☑️ **Enable Dependabot alerts**
- ☑️ **Enable Dependabot security updates**
- ☑️ **Enable secret scanning**

---

## 📝 Pull Request Template

Create `.github/PULL_REQUEST_TEMPLATE.md` (see separate file)

---

## 👥 Code Owners

Create `.github/CODEOWNERS` (see separate file)

---

## 🚀 Quick Setup Script

Use GitHub CLI to set up branch protection:

```bash
# Install GitHub CLI first: https://cli.github.com/

# Main branch
gh api repos/:owner/:repo/branches/main/protection \
  -X PUT \
  -F required_status_checks[strict]=true \
  -F required_status_checks[contexts][]=lint \
  -F required_status_checks[contexts][]=test-unit \
  -F required_status_checks[contexts][]=test-cli \
  -F required_status_checks[contexts][]=test-e2e \
  -F required_pull_request_reviews[required_approving_review_count]=2 \
  -F required_pull_request_reviews[dismiss_stale_reviews]=true \
  -F enforce_admins=true \
  -F required_linear_history=true

# Repeat for stage and dev with appropriate settings
```

---

## 📊 Monitoring

### Check Branch Protection Status:

```bash
gh api repos/:owner/:repo/branches/main/protection
gh api repos/:owner/:repo/branches/stage/protection
gh api repos/:owner/:repo/branches/dev/protection
```

---

## 🔧 Troubleshooting

### Common Issues:

1. **CI checks not showing up:**
   - Ensure workflows are in `.github/workflows/`
   - Check workflow syntax with `gh workflow list`
   - Verify status check names match exactly

2. **Can't merge despite passing tests:**
   - Check if branch is up to date with base
   - Verify all required reviewers approved
   - Check for unresolved conversations

3. **Admin bypassing rules:**
   - Ensure "Include administrators" is checked
   - Verify "Do not allow bypassing" is enabled

---

## 📚 Resources

- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [CODEOWNERS Syntax](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
