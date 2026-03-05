#!/usr/bin/env python3
"""
Rewrite git commit timestamps to reflect a late-night coding session.
March 4th 2026, 10pm CST -> March 5th 2026, 3am CST
"""

import subprocess
import sys
from datetime import datetime, timedelta
import re

def get_commits(count=20):
    """Get the last N commits"""
    result = subprocess.run(
        ['git', 'log', f'-{count}', '--format=%H'],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip().split('\n')

def rewrite_commit_dates():
    """
    Rewrite commit dates to be between 10pm March 4th and 3am March 5th 2026 CST
    """
    # Get commits (oldest first)
    commits = get_commits(20)
    commits.reverse()  # Oldest first
    
    # Define time range
    start_time = datetime(2026, 3, 4, 22, 0, 0)  # 10pm March 4th
    end_time = datetime(2026, 3, 5, 3, 0, 0)     # 3am March 5th
    
    # Calculate time increment
    total_minutes = int((end_time - start_time).total_seconds() / 60)
    minutes_per_commit = total_minutes / len(commits)
    
    print(f"🔄 Rewriting {len(commits)} commits...")
    print(f"📅 Time range: {start_time} -> {end_time}")
    print(f"⏱️  ~{minutes_per_commit:.1f} minutes per commit\n")
    
    # Create filter-branch script
    filter_script = []
    
    for i, commit_hash in enumerate(commits):
        # Calculate timestamp for this commit
        commit_time = start_time + timedelta(minutes=minutes_per_commit * i)
        
        # Format as git expects: "YYYY-MM-DD HH:MM:SS -0600" (CST is UTC-6)
        date_str = commit_time.strftime("%Y-%m-%d %H:%M:%S -0600")
        
        # Get commit message
        msg_result = subprocess.run(
            ['git', 'log', '-1', '--format=%s', commit_hash],
            capture_output=True,
            text=True,
            check=True
        )
        commit_msg = msg_result.stdout.strip()
        
        print(f"  {i+1:2d}. {commit_time.strftime('%b %d %I:%M%p')} - {commit_msg[:60]}")
        
        filter_script.append(f"if [ $GIT_COMMIT = {commit_hash} ]; then export GIT_AUTHOR_DATE='{date_str}'; export GIT_COMMITTER_DATE='{date_str}'; fi")
    
    # Write filter script
    script_content = '\n'.join(filter_script)
    
    print("\n⚠️  This will rewrite git history. Make sure you have a backup!")
    response = input("Continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Aborted.")
        return
    
    # Use git filter-branch to rewrite history
    print("\n🚀 Rewriting history...\n")
    
    env_filter = '; '.join(filter_script)
    
    subprocess.run([
        'git', 'filter-branch', '-f', '--env-filter', env_filter,
        f'HEAD~{len(commits)}..HEAD'
    ], check=True)
    
    print("\n✅ Done! Commit times rewritten.")
    print("\n📊 New commit log:")
    subprocess.run(['git', 'log', '--oneline', '-20'])

if __name__ == '__main__':
    try:
        rewrite_commit_dates()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
