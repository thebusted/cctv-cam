# GitHub CLI (gh) Command Reference

Quick reference for common `gh` commands and patterns.

## Authentication

```bash
# Login to GitHub
gh auth login

# Check authentication status
gh auth status

# Logout
gh auth logout
```

## Issues

### Creating Issues
```bash
# Create issue interactively
gh issue create

# Create with title and body
gh issue create --title "Bug: Login fails" --body "Description here"

# Create from file
gh issue create --title "Feature request" --body-file feature.md

# Create with labels and assignees
gh issue create --title "Bug" --body "Fix this" --label "bug,urgent" --assignee "@me"

# Create in specific repo
gh issue create --repo owner/repo --title "Issue title" --body "Content"
```

### Listing & Searching Issues
```bash
# List open issues
gh issue list

# List with filters
gh issue list --label "bug" --state "open" --assignee "@me"

# Search issues
gh issue list --search "is:open label:bug"

# Limit results
gh issue list --limit 20
```

### Viewing & Managing Issues
```bash
# View issue details
gh issue view 123

# View in browser
gh issue view 123 --web

# Close an issue
gh issue close 123

# Reopen an issue
gh issue reopen 123

# Add comment
gh issue comment 123 --body "Thanks for reporting!"

# Edit issue
gh issue edit 123 --title "New title" --body "New description"
```

## Pull Requests

### Creating PRs
```bash
# Create PR interactively
gh pr create

# Create with title and body
gh pr create --title "Add feature" --body "Description"

# Create from file
gh pr create --title "Fix bug" --body-file pr_description.md

# Create draft PR
gh pr create --draft --title "WIP: New feature"

# Create with reviewers and labels
gh pr create --title "Fix" --reviewer "@user1,@user2" --label "bugfix"

# Specify base branch
gh pr create --base main --head feature-branch --title "Add feature"
```

### Listing & Searching PRs
```bash
# List PRs
gh pr list

# List with filters
gh pr list --state "open" --label "bugfix" --author "@me"

# List drafts
gh pr list --draft

# Search PRs
gh pr list --search "is:open review:required"
```

### Managing PRs
```bash
# View PR details
gh pr view 456

# View diff
gh pr diff 456

# Checkout PR locally
gh pr checkout 456

# Review PR
gh pr review 456 --approve
gh pr review 456 --request-changes --body "Please fix..."
gh pr review 456 --comment --body "Looks good overall"

# Merge PR
gh pr merge 456
gh pr merge 456 --squash
gh pr merge 456 --rebase
gh pr merge 456 --merge

# Close without merging
gh pr close 456

# Reopen PR
gh pr reopen 456

# Mark as ready (remove draft status)
gh pr ready 456
```

## Repository Operations

```bash
# Clone repository
gh repo clone owner/repo

# Create new repository
gh repo create my-new-repo --public
gh repo create my-new-repo --private

# Fork repository
gh repo fork owner/repo

# View repository
gh repo view owner/repo
gh repo view owner/repo --web

# List repositories
gh repo list
gh repo list owner

# Archive repository
gh repo archive owner/repo
```

## Workflow & Actions

```bash
# List workflows
gh workflow list

# Run a workflow
gh workflow run workflow.yml

# View workflow run
gh run view 123456

# List recent runs
gh run list

# Watch a workflow run
gh run watch

# Download artifacts
gh run download 123456
```

## Gists

```bash
# Create gist
gh gist create file.txt
gh gist create file.txt --public

# List gists
gh gist list

# View gist
gh gist view gist-id

# Edit gist
gh gist edit gist-id
```

## Milestones

### Creating Milestones
```bash
# Create milestone using gh API
gh api repos/:owner/:repo/milestones --method POST \
  -f title="v1.0 Release" \
  -f state="open"

# With description and due date
gh api repos/:owner/:repo/milestones --method POST \
  -f title="Sprint 1" \
  -f description="First development sprint" \
  -f due_on="2025-12-31T23:59:59Z"

# Thai language support
gh api repos/:owner/:repo/milestones --method POST \
  -f title="รอบที่ 1" \
  -f description="การพัฒนาเฟสแรก"
```

### Listing Milestones
```bash
# All open milestones
gh api repos/:owner/:repo/milestones

# All milestones (open and closed)
gh api repos/:owner/:repo/milestones?state=all

# Sort by due date
gh api repos/:owner/:repo/milestones?sort=due_on&direction=asc

# Sort by completeness
gh api repos/:owner/:repo/milestones?sort=completeness
```

### Viewing Milestone Details
```bash
# Get specific milestone
gh api repos/:owner/:repo/milestones/1

# Format with jq
gh api repos/:owner/:repo/milestones/1 | jq '{title, open_issues, closed_issues, due_on}'
```

### Updating Milestones
```bash
# Update title
gh api repos/:owner/:repo/milestones/1 --method PATCH \
  -f title="v1.0.1 Release"

# Update multiple fields
gh api repos/:owner/:repo/milestones/1 --method PATCH \
  -f title="v1.1" \
  -f description="Minor update" \
  -f due_on="2026-01-15T00:00:00Z"

# Close milestone
gh api repos/:owner/:repo/milestones/1 --method PATCH \
  -f state="closed"

# Reopen milestone
gh api repos/:owner/:repo/milestones/1 --method PATCH \
  -f state="open"
```

### Deleting Milestones
```bash
gh api repos/:owner/:repo/milestones/1 --method DELETE
```

### Assigning Issues to Milestones
```bash
# Create issue with milestone
gh issue create --title "Bug fix" --body "..." --milestone 1

# Assign milestone to existing issue
gh issue edit 123 --milestone 1

# Remove milestone from issue
gh issue edit 123 --milestone ""

# Using API
gh api repos/:owner/:repo/issues/123 --method PATCH -f milestone=1
```

### Milestone Progress Tracking
```bash
# Get milestone progress
gh api repos/:owner/:repo/milestones/1 \
  | jq '{
      title: .title,
      open: .open_issues,
      closed: .closed_issues,
      percent: ((.closed_issues / (.open_issues + .closed_issues)) * 100)
    }'

# List all issues in milestone
gh issue list --milestone 1

# Find overdue milestones
gh api repos/:owner/:repo/milestones?state=open \
  | jq --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.[] | select(.due_on != null and .due_on < $now) | {title, due_on}'
```

## Advanced Usage

### Using with JQ for JSON output
```bash
# Get issue data as JSON
gh issue view 123 --json title,body,labels

# List issues and extract specific fields
gh issue list --json number,title,state | jq '.[] | select(.state=="OPEN")'
```

### Aliases
```bash
# Create custom aliases
gh alias set bugs 'issue list --label "bug"'
gh alias set my-prs 'pr list --author "@me"'

# List aliases
gh alias list

# Use alias
gh bugs
```

### Environment Variables
```bash
# Set default repository
export GH_REPO="owner/repo"

# Set default host
export GH_HOST="github.company.com"  # For GitHub Enterprise

# Set editor
export EDITOR="code --wait"  # or vim, nano, etc.
```

## Quick Patterns

### Issue Workflow
```bash
# 1. List issues to find work
gh issue list --assignee "@me"

# 2. View issue details
gh issue view 123

# 3. Create branch for issue
git checkout -b fix-issue-123

# 4. Work on fix, commit changes
git commit -am "Fix issue #123"

# 5. Push and create PR
git push -u origin fix-issue-123
gh pr create --title "Fix: Issue #123" --body "Closes #123"

# 6. After PR is merged, close issue (if not auto-closed)
gh issue close 123
```

### PR Review Workflow
```bash
# 1. List PRs assigned for review
gh pr list --search "is:open review-requested:@me"

# 2. Checkout and test PR locally
gh pr checkout 456
# Run tests...

# 3. Review and approve/request changes
gh pr review 456 --approve --body "LGTM! ✅"
```

## Tips

1. **Interactive mode**: Most commands support interactive mode if you omit required arguments
2. **Web flag**: Use `--web` or `-w` to open items in browser
3. **JSON output**: Use `--json` for programmatic access
4. **Aliases**: Create shortcuts for frequently used commands
5. **Help**: Use `gh help` or `gh <command> --help` for detailed information
