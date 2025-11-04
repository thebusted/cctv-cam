#!/usr/bin/env python3
"""
Create a GitHub pull request using the gh CLI.
"""
import subprocess
import sys
import tempfile
import os

def create_pr(title, body=None, base=None, head=None, draft=False, repo=None, labels=None, assignees=None, reviewers=None):
    """
    Create a GitHub pull request using gh CLI.
    
    Args:
        title: PR title
        body: PR description (optional)
        base: Base branch (default: main/master)
        head: Head branch (default: current branch)
        draft: Create as draft PR
        repo: Repository in owner/repo format (optional)
        labels: Comma-separated labels
        assignees: Comma-separated assignees
        reviewers: Comma-separated reviewers
    """
    cmd = ["gh", "pr", "create", "--title", title]
    
    # Handle body
    if body:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(body)
            temp_file = f.name
        cmd.extend(["--body-file", temp_file])
    else:
        cmd.extend(["--body", ""])
    
    try:
        if base:
            cmd.extend(["--base", base])
        
        if head:
            cmd.extend(["--head", head])
        
        if draft:
            cmd.append("--draft")
        
        if repo:
            cmd.extend(["--repo", repo])
        
        if labels:
            cmd.extend(["--label", labels])
        
        if assignees:
            cmd.extend(["--assignee", assignees])
        
        if reviewers:
            cmd.extend(["--reviewer", reviewers])
        
        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Pull request created successfully!")
        print(result.stdout)
        return result.stdout
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating pull request:", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    finally:
        if body:
            os.unlink(temp_file)

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_pr.py <title> [body_file] [options]")
        print("\nOptions:")
        print("  --base BRANCH       Base branch (default: repo default)")
        print("  --head BRANCH       Head branch (default: current)")
        print("  --draft             Create as draft PR")
        print("  --repo OWNER/REPO   Target repository")
        print("  --labels LABELS     Comma-separated labels")
        print("  --assignees USERS   Comma-separated assignees")
        print("  --reviewers USERS   Comma-separated reviewers")
        print("\nExample:")
        print("  python create_pr.py 'Add login feature' pr_body.md --draft --reviewers '@user1,@user2'")
        sys.exit(1)
    
    title = sys.argv[1]
    body = None
    
    # Parse arguments
    args = sys.argv[2:]
    options = {
        'base': None,
        'head': None,
        'draft': False,
        'repo': None,
        'labels': None,
        'assignees': None,
        'reviewers': None
    }
    
    # Check if second arg is a file (body)
    if args and not args[0].startswith('--'):
        try:
            with open(args[0], 'r') as f:
                body = f.read()
            args = args[1:]
        except FileNotFoundError:
            pass
    
    # Parse options
    i = 0
    while i < len(args):
        if args[i] == '--draft':
            options['draft'] = True
            i += 1
        elif args[i] in ['--base', '--head', '--repo', '--labels', '--assignees', '--reviewers']:
            key = args[i][2:]  # Remove --
            if i + 1 < len(args):
                options[key] = args[i + 1]
                i += 2
            else:
                print(f"❌ Error: {args[i]} requires a value", file=sys.stderr)
                sys.exit(1)
        else:
            i += 1
    
    create_pr(title, body, **options)

if __name__ == "__main__":
    main()
