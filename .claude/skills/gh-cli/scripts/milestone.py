#!/usr/bin/env python3
"""
Manage GitHub milestones using the gh CLI API.
Supports creating, listing, updating, and closing milestones.
"""
import subprocess
import sys
import json
from datetime import datetime

def gh_api(endpoint, method="GET", fields=None, repo=None):
    """
    Call GitHub API using gh CLI.
    
    Args:
        endpoint: API endpoint (e.g., "repos/:owner/:repo/milestones")
        method: HTTP method (GET, POST, PATCH, DELETE)
        fields: Dictionary of fields to send
        repo: Repository in owner/repo format (optional)
    """
    cmd = ["gh", "api", endpoint, "--method", method]
    
    if repo:
        # Replace :owner/:repo in endpoint
        owner, repo_name = repo.split('/')
        endpoint = endpoint.replace(":owner", owner).replace(":repo", repo_name)
        cmd = ["gh", "api", endpoint, "--method", method]
    
    if fields:
        for key, value in fields.items():
            if value is not None:
                cmd.extend(["-f", f"{key}={value}"])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout) if result.stdout else None
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def create_milestone(title, repo=None, description=None, due_date=None, state="open"):
    """
    Create a new milestone.
    
    Args:
        title: Milestone title (required)
        repo: Repository in owner/repo format (optional, uses current if not specified)
        description: Milestone description (optional)
        due_date: Due date in ISO 8601 format YYYY-MM-DDTHH:MM:SSZ (optional)
        state: "open" or "closed" (default: "open")
    """
    if repo:
        endpoint = f"repos/{repo}/milestones"
    else:
        # Get current repo
        result = subprocess.run(["gh", "repo", "view", "--json", "nameWithOwner"], 
                              capture_output=True, text=True, check=True)
        repo_info = json.loads(result.stdout)
        repo = repo_info['nameWithOwner']
        endpoint = f"repos/{repo}/milestones"
    
    fields = {
        "title": title,
        "state": state
    }
    
    if description:
        fields["description"] = description
    
    if due_date:
        # Ensure proper ISO 8601 format
        fields["due_on"] = due_date
    
    print(f"Creating milestone '{title}' in {repo}...")
    result = gh_api(endpoint, method="POST", fields=fields)
    
    print(f"✅ Milestone created successfully!")
    print(f"   Number: {result['number']}")
    print(f"   Title: {result['title']}")
    print(f"   URL: {result['html_url']}")
    return result

def list_milestones(repo=None, state="open", sort="due_on", direction="asc"):
    """
    List milestones.
    
    Args:
        repo: Repository in owner/repo format (optional)
        state: "open", "closed", or "all" (default: "open")
        sort: "due_on" or "completeness" (default: "due_on")
        direction: "asc" or "desc" (default: "asc")
    """
    if repo:
        endpoint = f"repos/{repo}/milestones?state={state}&sort={sort}&direction={direction}"
    else:
        result = subprocess.run(["gh", "repo", "view", "--json", "nameWithOwner"], 
                              capture_output=True, text=True, check=True)
        repo_info = json.loads(result.stdout)
        repo = repo_info['nameWithOwner']
        endpoint = f"repos/{repo}/milestones?state={state}&sort={sort}&direction={direction}"
    
    result = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True, check=True)
    milestones = json.loads(result.stdout)
    
    if not milestones:
        print(f"No {state} milestones found.")
        return []
    
    print(f"\n{'#':<6} {'Title':<30} {'Progress':<20} {'Due Date':<12} {'State':<8}")
    print("-" * 90)
    
    for m in milestones:
        number = m['number']
        title = m['title'][:28] + '..' if len(m['title']) > 30 else m['title']
        
        # Calculate progress
        total = m['open_issues'] + m['closed_issues']
        if total > 0:
            percent = (m['closed_issues'] / total) * 100
            progress = f"{m['closed_issues']}/{total} ({percent:.0f}%)"
        else:
            progress = "0/0"
        
        # Format due date
        due_date = "None"
        if m.get('due_on'):
            due_dt = datetime.fromisoformat(m['due_on'].replace('Z', '+00:00'))
            due_date = due_dt.strftime('%Y-%m-%d')
        
        state = m['state']
        
        print(f"{number:<6} {title:<30} {progress:<20} {due_date:<12} {state:<8}")
    
    return milestones

def update_milestone(number, repo=None, title=None, description=None, due_date=None, state=None):
    """
    Update an existing milestone.
    
    Args:
        number: Milestone number (required)
        repo: Repository in owner/repo format (optional)
        title: New title (optional)
        description: New description (optional)
        due_date: New due date in ISO 8601 format (optional)
        state: "open" or "closed" (optional)
    """
    if repo:
        endpoint = f"repos/{repo}/milestones/{number}"
    else:
        result = subprocess.run(["gh", "repo", "view", "--json", "nameWithOwner"], 
                              capture_output=True, text=True, check=True)
        repo_info = json.loads(result.stdout)
        repo = repo_info['nameWithOwner']
        endpoint = f"repos/{repo}/milestones/{number}"
    
    fields = {}
    if title:
        fields["title"] = title
    if description:
        fields["description"] = description
    if due_date:
        fields["due_on"] = due_date
    if state:
        fields["state"] = state
    
    if not fields:
        print("❌ Error: No fields to update specified", file=sys.stderr)
        sys.exit(1)
    
    print(f"Updating milestone #{number}...")
    result = gh_api(endpoint, method="PATCH", fields=fields)
    
    print(f"✅ Milestone updated successfully!")
    print(f"   Title: {result['title']}")
    print(f"   State: {result['state']}")
    return result

def close_milestone(number, repo=None):
    """Close a milestone."""
    return update_milestone(number, repo=repo, state="closed")

def reopen_milestone(number, repo=None):
    """Reopen a milestone."""
    return update_milestone(number, repo=repo, state="open")

def get_milestone(number, repo=None):
    """
    Get details of a specific milestone.
    
    Args:
        number: Milestone number
        repo: Repository in owner/repo format (optional)
    """
    if repo:
        endpoint = f"repos/{repo}/milestones/{number}"
    else:
        result = subprocess.run(["gh", "repo", "view", "--json", "nameWithOwner"], 
                              capture_output=True, text=True, check=True)
        repo_info = json.loads(result.stdout)
        repo = repo_info['nameWithOwner']
        endpoint = f"repos/{repo}/milestones/{number}"
    
    result = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True, check=True)
    milestone = json.loads(result.stdout)
    
    print(f"\nMilestone #{milestone['number']}: {milestone['title']}")
    print(f"{'='*60}")
    print(f"State: {milestone['state']}")
    print(f"Description: {milestone.get('description', 'None')}")
    
    if milestone.get('due_on'):
        due_dt = datetime.fromisoformat(milestone['due_on'].replace('Z', '+00:00'))
        print(f"Due Date: {due_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    total = milestone['open_issues'] + milestone['closed_issues']
    if total > 0:
        percent = (milestone['closed_issues'] / total) * 100
        print(f"Progress: {milestone['closed_issues']}/{total} ({percent:.0f}%)")
    else:
        print(f"Progress: 0/0")
    
    print(f"URL: {milestone['html_url']}")
    
    return milestone

def delete_milestone(number, repo=None):
    """
    Delete a milestone.
    
    Args:
        number: Milestone number
        repo: Repository in owner/repo format (optional)
    """
    if repo:
        endpoint = f"repos/{repo}/milestones/{number}"
    else:
        result = subprocess.run(["gh", "repo", "view", "--json", "nameWithOwner"], 
                              capture_output=True, text=True, check=True)
        repo_info = json.loads(result.stdout)
        repo = repo_info['nameWithOwner']
        endpoint = f"repos/{repo}/milestones/{number}"
    
    result = subprocess.run(["gh", "api", endpoint, "--method", "DELETE"], 
                          capture_output=True, text=True, check=True)
    
    print(f"✅ Milestone #{number} deleted successfully!")

def main():
    if len(sys.argv) < 2:
        print("""
GitHub Milestone Manager

Usage: python milestone.py <command> [options]

Commands:
    create <title> [--repo OWNER/REPO] [--description TEXT] [--due-date YYYY-MM-DD] [--state open|closed]
        Create a new milestone
        
    list [--repo OWNER/REPO] [--state open|closed|all] [--sort due_on|completeness]
        List milestones
        
    get <number> [--repo OWNER/REPO]
        Get milestone details
        
    update <number> [--repo OWNER/REPO] [--title TEXT] [--description TEXT] [--due-date YYYY-MM-DD] [--state open|closed]
        Update a milestone
        
    close <number> [--repo OWNER/REPO]
        Close a milestone
        
    reopen <number> [--repo OWNER/REPO]
        Reopen a milestone
        
    delete <number> [--repo OWNER/REPO]
        Delete a milestone

Examples:
    python milestone.py create "v1.0 Release" --due-date 2025-12-31
    python milestone.py list --state all
    python milestone.py update 1 --title "v1.0.1 Release" --state closed
    python milestone.py close 2
    python milestone.py get 1
""")
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    # Parse common options
    repo = None
    if "--repo" in args:
        idx = args.index("--repo")
        repo = args[idx + 1]
        args = args[:idx] + args[idx+2:]
    
    if command == "create":
        if not args:
            print("❌ Error: Title required", file=sys.stderr)
            sys.exit(1)
        
        title = args[0]
        description = None
        due_date = None
        state = "open"
        
        if "--description" in args:
            idx = args.index("--description")
            description = args[idx + 1]
        
        if "--due-date" in args:
            idx = args.index("--due-date")
            due_date = args[idx + 1] + "T00:00:00Z"
        
        if "--state" in args:
            idx = args.index("--state")
            state = args[idx + 1]
        
        create_milestone(title, repo, description, due_date, state)
    
    elif command == "list":
        state = "open"
        sort = "due_on"
        
        if "--state" in args:
            idx = args.index("--state")
            state = args[idx + 1]
        
        if "--sort" in args:
            idx = args.index("--sort")
            sort = args[idx + 1]
        
        list_milestones(repo, state, sort)
    
    elif command == "get":
        if not args:
            print("❌ Error: Milestone number required", file=sys.stderr)
            sys.exit(1)
        number = args[0]
        get_milestone(number, repo)
    
    elif command == "update":
        if not args:
            print("❌ Error: Milestone number required", file=sys.stderr)
            sys.exit(1)
        
        number = args[0]
        title = None
        description = None
        due_date = None
        state = None
        
        if "--title" in args:
            idx = args.index("--title")
            title = args[idx + 1]
        
        if "--description" in args:
            idx = args.index("--description")
            description = args[idx + 1]
        
        if "--due-date" in args:
            idx = args.index("--due-date")
            due_date = args[idx + 1] + "T00:00:00Z"
        
        if "--state" in args:
            idx = args.index("--state")
            state = args[idx + 1]
        
        update_milestone(number, repo, title, description, due_date, state)
    
    elif command == "close":
        if not args:
            print("❌ Error: Milestone number required", file=sys.stderr)
            sys.exit(1)
        number = args[0]
        close_milestone(number, repo)
    
    elif command == "reopen":
        if not args:
            print("❌ Error: Milestone number required", file=sys.stderr)
            sys.exit(1)
        number = args[0]
        reopen_milestone(number, repo)
    
    elif command == "delete":
        if not args:
            print("❌ Error: Milestone number required", file=sys.stderr)
            sys.exit(1)
        number = args[0]
        delete_milestone(number, repo)
    
    else:
        print(f"❌ Unknown command: {command}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
