#!/bin/bash

# Prism GitHub Push Script
# This script pushes the repo and sets up GitHub metadata

echo "🚀 Prism GitHub Deployment Script"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Step 1: Create the GitHub repository
echo "🏗️  Step 1/4: Creating GitHub repository..."
GH_HOST=github.com gh repo create andersonwilliam85/prism \
  --public \
  --description "Prism - A flexible, beautiful development environment installer that scales from solo developers to Fortune 500 enterprises. Features multi-level config inheritance, 7 pre-built packages, beautiful web UI with 5 themes, and comprehensive CI/CD automation." \
  --homepage "https://andersonwilliam85.github.io/prism" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Repository created!"
else
    echo "⚠️  Repository might already exist, continuing..."
fi

echo ""

# Step 2: Push to GitHub
echo "📤 Step 2/4: Pushing code to GitHub..."
GIT_SSH_COMMAND='ssh -i ~/.ssh/id_rsa_github_prism -o IdentitiesOnly=yes' git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Code pushed successfully!"
else
    echo "❌ Push failed!"
    exit 1
fi

echo ""

# Step 3: Set repository description
echo "📝 Step 3/4: Setting repository description..."
GH_HOST=github.com gh repo edit andersonwilliam85/prism \
  --description "Prism - A flexible, beautiful development environment installer that scales from solo developers to Fortune 500 enterprises. Features multi-level config inheritance, 7 pre-built packages, beautiful web UI with 5 themes, and comprehensive CI/CD automation."

if [ $? -eq 0 ]; then
    echo "✅ Description set!"
else
    echo "⚠️  Description failed (you may need to set it manually)"
fi

echo ""

# Step 4: Add topics
echo "🏷️  Step 4/4: Adding repository topics..."
GH_HOST=github.com gh repo edit andersonwilliam85/prism \
  --add-topic python \
  --add-topic developer-tools \
  --add-topic onboarding \
  --add-topic devops \
  --add-topic automation \
  --add-topic config-management \
  --add-topic enterprise \
  --add-topic setup-wizard \
  --add-topic package-manager \
  --add-topic developer-experience

if [ $? -eq 0 ]; then
    echo "✅ Topics added!"
else
    echo "⚠️  Topics failed (you may need to add them manually)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🎉 DEPLOYMENT COMPLETE!"
echo ""
echo "🌐 View your repo: https://github.com/andersonwilliam85/prism"
echo "═══════════════════════════════════════════════════════════════"
