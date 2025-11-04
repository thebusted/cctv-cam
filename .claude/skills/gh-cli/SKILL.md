---
name: gh-cli
description: Automate GitHub operations using the gh CLI tool. Use for creating issues and PRs, managing repositories, running workflows, and automating GitHub tasks. Ideal when users want to interact with GitHub programmatically or automate repetitive GitHub operations.
---

# GitHub CLI (gh) Automation

Automate GitHub operations using the `gh` CLI tool for issues, pull requests, repositories, and workflows.

## Prerequisites

Before using gh commands, verify:
```bash
# Check if gh is installed
gh --version

# Check authentication status
gh auth status
```

If not authenticated: `gh auth login`

## Quick Start Patterns

### Creating Issues

**Interactive creation:**
```bash
gh issue create
```

**With title and body:**
```bash
gh issue create --title "Bug: Login timeout" --body "Users experience timeout after 30s"
```

**From file (use with templates):**
```bash
gh issue create --title "Feature: Dark mode" --body-file feature_request.md --label "enhancement"
```

**With all options:**
```bash
gh issue create \
  --title "Bug: Database connection fails" \
  --body-file bug_report.md \
  --label "bug,urgent" \
  --assignee "@me" \
  --repo owner/repo
```

### Creating Pull Requests

**From current branch:**
```bash
gh pr create --title "Add login feature" --body "Implements user authentication"
```

**Draft PR:**
```bash
gh pr create --draft --title "WIP: New dashboard"
```

**With reviewers and labels:**
```bash
gh pr create \
  --title "Fix memory leak" \
  --body-file pr_description.md \
  --reviewer "@user1,@user2" \
  --label "bugfix,critical"
```

## Using the Helper Scripts

### create_issue.py

Python script for programmatic issue creation:

```bash
python scripts/create_issue.py "Bug: Login fails" bug_template.md "bug,urgent" "@me"
```

**Parameters:**
1. Title (required)
2. Body file path (required) 
3. Labels - comma-separated (optional)
4. Assignees - comma-separated (optional)
5. Repository - owner/repo format (optional)

### create_pr.py

Python script for pull request creation:

```bash
python scripts/create_pr.py "Add feature" pr_body.md --draft --reviewers "@user1,@user2"
```

**Options:**
- `--base BRANCH` - Base branch
- `--head BRANCH` - Head branch
- `--draft` - Create as draft
- `--repo OWNER/REPO` - Target repository
- `--labels` - Comma-separated labels
- `--assignees` - Comma-separated assignees
- `--reviewers` - Comma-separated reviewers

### gh_quick.sh

Bash wrapper for common operations:

```bash
# Quick bug report
./scripts/gh_quick.sh bug "Login timeout" "Users can't login after 30 seconds"

# Quick feature request
./scripts/gh_quick.sh feature "Dark mode" "Add theme toggle in settings"

# Create from template
./scripts/gh_quick.sh issue-from-template bug_template.md "Fix login bug" "bug,urgent"

# List your issues
./scripts/gh_quick.sh my-issues

# List PRs needing review
./scripts/gh_quick.sh my-reviews

# Quick PR
./scripts/gh_quick.sh pr "Add authentication" "Implements OAuth2 login"
```

## Integration with Issue Templates

Combine with the github-issue-templates skill:

1. Generate template content using github-issue-templates skill
2. Save to a file (e.g., `bug_report.md`)
3. Submit using gh:
   ```bash
   gh issue create --title "Bug title" --body-file bug_report.md --label "bug"
   ```

Or use the Python script:
```bash
python scripts/create_issue.py "Bug title" bug_report.md "bug,urgent" "@me"
```

## Common Workflows

### Issue Management Workflow
```bash
# List open issues assigned to you
gh issue list --assignee "@me" --state open

# View issue details
gh issue view 123

# Add comment
gh issue comment 123 --body "Working on this now"

# Close issue
gh issue close 123
```

### PR Review Workflow
```bash
# List PRs awaiting your review
gh pr list --search "is:open review-requested:@me"

# Checkout PR locally
gh pr checkout 456

# Review after testing
gh pr review 456 --approve --body "LGTM! ✅"

# Request changes
gh pr review 456 --request-changes --body "Please add tests"
```

### Repository Operations
```bash
# Clone repository
gh repo clone owner/repo

# Create new repository
gh repo create my-project --public --clone

# Fork repository
gh repo fork owner/repo --clone

# View repository info
gh repo view owner/repo
```

## Advanced Usage

### JSON Output with jq
```bash
# Get issue data as JSON
gh issue list --json number,title,labels,state | jq '.[] | select(.state=="OPEN")'

# Extract specific fields
gh pr view 123 --json title,author,reviews | jq '.reviews[].state'
```

### Custom Aliases
```bash
# Create shortcuts
gh alias set bugs 'issue list --label "bug" --state open'
gh alias set my-prs 'pr list --author "@me"'

# Use aliases
gh bugs
gh my-prs
```

### Environment Variables
```bash
# Set default repository
export GH_REPO="owner/repo"

# For GitHub Enterprise
export GH_HOST="github.company.com"
```

## Reference Documentation

For comprehensive command reference, see `references/commands.md`:
- Complete command syntax
- All available options
- More usage examples
- Advanced patterns

## Troubleshooting

**Authentication issues:**
```bash
gh auth status
gh auth login
```

**Check repository context:**
```bash
gh repo view  # Shows current repository
```

**Verbose output for debugging:**
```bash
gh issue create --title "Test" --body "Test" --verbose
```

## Milestone Management

Milestones help track progress on groups of issues or pull requests. Use for release planning, sprints, or feature grouping.

### Using gh API (Direct)

```bash
# Create milestone
gh api repos/:owner/:repo/milestones --method POST \
  -f title="v1.0 Release" \
  -f state="open" \
  -f description="First major release" \
  -f due_on="2025-12-31T00:00:00Z"

# List milestones
gh api repos/:owner/:repo/milestones

# Update milestone
gh api repos/:owner/:repo/milestones/1 --method PATCH -f state="closed"

# Delete milestone
gh api repos/:owner/:repo/milestones/1 --method DELETE
```

### Using milestone.py Script

```bash
# Create milestone
python scripts/milestone.py create "v1.0 Release" \
  --description "First release" \
  --due-date 2025-12-31

# List milestones
python scripts/milestone.py list --state all

# Get details
python scripts/milestone.py get 1

# Update
python scripts/milestone.py update 1 --title "v1.0.1" --state closed

# Close/reopen
python scripts/milestone.py close 1
python scripts/milestone.py reopen 1

# Delete
python scripts/milestone.py delete 1
```

### Assigning Issues to Milestones

```bash
# During issue creation
gh issue create --title "Bug fix" --body "..." --milestone 1

# Update existing issue
gh issue edit 123 --milestone 1

# Remove milestone
gh issue edit 123 --milestone ""

# Using API
gh api repos/:owner/:repo/issues/123 --method PATCH -f milestone=1
```

### Thai Language Support

Milestones support Unicode characters including Thai:
```bash
python scripts/milestone.py create "รอบที่ 1" --description "การพัฒนาเฟสแรก"
gh api repos/:owner/:repo/milestones --method POST -f title="เวอร์ชัน 1.0"
```

For comprehensive milestone documentation, see `references/milestones.md`.

## When to Use This Skill

Use gh-cli skill when:
- Creating issues/PRs programmatically
- Automating GitHub workflows
- Bulk operations on issues/PRs
- Managing milestones and releases
- Integrating GitHub with CI/CD
- Managing repositories from command line

Use GitHub web interface when:
- Complex formatting needed
- Adding images/attachments
- Using GitHub-specific features (Projects, Discussions)
- Collaborating with non-technical users
