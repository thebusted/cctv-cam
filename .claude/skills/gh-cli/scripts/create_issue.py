#!/usr/bin/env python3
"""
Create a GitHub issue using the gh CLI.
Supports creating issues from template content or direct input.
"""
import subprocess
import sys
import tempfile
import os
from pathlib import Path

def create_issue(title, body, labels=None, assignees=None, repo=None):
    """
    Create a GitHub issue using gh CLI.
    
    Args:
        title: Issue title
        body: Issue body (markdown content)
        labels: Comma-separated labels (e.g., "bug,urgent")
        assignees: Comma-separated assignees (e.g., "@me,user2")
        repo: Repository in owner/repo format (optional, uses current repo if not specified)
    """
    # Build the gh command
    cmd = ["gh", "issue", "create", "--title", title]
    
    # Use a temporary file for the body to handle multiline content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(body)
        temp_file = f.name
    
    try:
        cmd.extend(["--body-file", temp_file])
        
        if labels:
            cmd.extend(["--label", labels])
        
        if assignees:
            cmd.extend(["--assignee", assignees])
        
        if repo:
            cmd.extend(["--repo", repo])
        
        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Issue created successfully!")
        print(result.stdout)
        return result.stdout
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating issue:", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    finally:
        # Clean up temp file
        os.unlink(temp_file)

def main():
    if len(sys.argv) < 3:
        print("Usage: python create_issue.py <title> <body_file> [labels] [assignees] [repo]")
        print("\nExample:")
        print("  python create_issue.py 'Bug: Login fails' bug_report.md 'bug,urgent' '@me'")
        sys.exit(1)
    
    title = sys.argv[1]
    body_file = sys.argv[2]
    labels = sys.argv[3] if len(sys.argv) > 3 else None
    assignees = sys.argv[4] if len(sys.argv) > 4 else None
    repo = sys.argv[5] if len(sys.argv) > 5 else None
    
    # Read body from file
    try:
        with open(body_file, 'r') as f:
            body = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Body file '{body_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    create_issue(title, body, labels, assignees, repo)

if __name__ == "__main__":
    main()
