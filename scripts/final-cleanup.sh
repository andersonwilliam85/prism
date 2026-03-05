#!/bin/bash
# Final commit cleanup script
# Fixes: author names, timestamps, and ensures consistency

set -e

echo "🧹 Final Commit Cleanup"
echo "======================"
echo ""

# Step 1: Fix author name inconsistencies
echo "📝 Step 1: Standardizing author name..."
echo "   Will Anderson → William Anderson"
echo ""

FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --env-filter '
if [ "$GIT_AUTHOR_NAME" = "Will Anderson" ]; then
    export GIT_AUTHOR_NAME="William Anderson"
fi
if [ "$GIT_COMMITTER_NAME" = "Will Anderson" ]; then
    export GIT_COMMITTER_NAME="William Anderson"
fi
' --tag-name-filter cat -- --all

echo "✅ Author names standardized"
echo ""

# Step 2: Clean up filter-branch artifacts
echo "🗑️  Step 2: Cleaning up artifacts..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive
echo "✅ Cleanup complete"
echo ""

# Step 3: Rewrite all timestamps
echo "⏰ Step 3: Rewriting timestamps to late-night session..."
echo "   March 4th 10:00pm → March 5th 3:00am CST"
echo ""
python3 scripts/rewrite-all-commits.py

echo ""
echo "✅ ALL CLEANUP COMPLETE!"
echo "======================="
echo ""
echo "📊 Final verification:"
git log --format="%ai | %an | %s" -10
