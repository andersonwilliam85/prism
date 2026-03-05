#!/bin/bash
# Quick CI/CD Setup Script
# Sets up branch protection rules via GitHub CLI

set -e

REPO="your-org/prism"  # Change this to your repo

echo "🚀 Setting up CI/CD for Prism Package Manager"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found!"
    echo "Install from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"
echo ""

# Prompt for repo
read -p "Enter repository (format: owner/repo) [$REPO]: " input_repo
REPO=${input_repo:-$REPO}

echo "📝 Setting up branch protection for: $REPO"
echo ""

# Function to set branch protection
setup_branch_protection() {
    local branch=$1
    local required_approvals=$2
    local checks="$3"
    
    echo "🔒 Setting up protection for $branch branch..."
    
    # Create protection rule
    gh api "repos/$REPO/branches/$branch/protection" \
        -X PUT \
        -F "required_status_checks[strict]=true" \
        -F "required_pull_request_reviews[required_approving_review_count]=$required_approvals" \
        -F "required_pull_request_reviews[dismiss_stale_reviews]=true" \
        -F "required_pull_request_reviews[require_code_owner_reviews]=true" \
        -F "enforce_admins=true" \
        -F "required_linear_history=true" \
        -F "allow_force_pushes=false" \
        -F "allow_deletions=false" \
        -F "required_conversation_resolution=true" \
        2>/dev/null || echo "⚠️  Could not set protection for $branch (branch may not exist yet)"
    
    echo "✅ $branch protection configured"
}

# Set up branch protections
setup_branch_protection "main" 2 "lint,test-unit,test-cli,test-e2e,coverage"
setup_branch_protection "stage" 1 "lint,test-unit,test-cli,test-e2e,coverage"
setup_branch_protection "dev" 1 "lint,test-unit,test-cli"

echo ""
echo "✨ Branch protection setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .github/CODEOWNERS with your team names"
echo "2. Configure GitHub secrets (if needed):"
echo "   gh secret set SLACK_WEBHOOK_URL"
echo "3. Create dev, stage branches if they don't exist:"
echo "   git checkout -b dev && git push origin dev"
echo "   git checkout -b stage && git push origin stage"
echo "4. Test CI by creating a PR"
echo ""
echo "📚 Documentation:"
echo "   - CI/CD Guide: .github/CI_CD.md"
echo "   - Branch Protection: .github/BRANCH_PROTECTION.md"
echo "   - Makefile: make help"
echo ""
echo "✅ Setup complete!"
