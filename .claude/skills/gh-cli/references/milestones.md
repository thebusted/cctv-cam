# GitHub Milestones Reference

Comprehensive guide for managing GitHub milestones using `gh` CLI and API.

## What are Milestones?

Milestones are a way to track progress on groups of issues or pull requests in a repository. They're useful for:
- Release planning (e.g., "v1.0", "Q4 2025")
- Sprint/iteration tracking
- Feature grouping
- Progress monitoring

## Quick Start

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
gh api repos/:owner/:repo/milestones/1 --method PATCH \
  -f state="closed"

# Delete milestone
gh api repos/:owner/:repo/milestones/1 --method DELETE
```

### Using milestone.py Script

```bash
# Create milestone
python scripts/milestone.py create "v1.0 Release" \
  --description "First major release" \
  --due-date 2025-12-31

# List milestones
python scripts/milestone.py list --state all

# Update milestone
python scripts/milestone.py update 1 \
  --title "v1.0.1 Release" \
  --state closed

# Get milestone details
python scripts/milestone.py get 1

# Close milestone
python scripts/milestone.py close 1

# Delete milestone
python scripts/milestone.py delete 1
```

## Creating Milestones

### Basic Creation

```bash
# Minimal - just title
gh api repos/:owner/:repo/milestones --method POST \
  -f title="Sprint 1"

# With description
gh api repos/:owner/:repo/milestones --method POST \
  -f title="v2.0 Beta" \
  -f description="Beta release for v2.0"

# With due date (ISO 8601 format)
gh api repos/:owner/:repo/milestones --method POST \
  -f title="Q1 2025" \
  -f due_on="2025-03-31T23:59:59Z"

# Create closed milestone
gh api repos/:owner/:repo/milestones --method POST \
  -f title="Archived Sprint" \
  -f state="closed"
```

### Using Script

```bash
# Basic
python scripts/milestone.py create "Sprint 1"

# With all options
python scripts/milestone.py create "v2.0 Release" \
  --description "Major version 2 release" \
  --due-date 2025-12-31 \
  --state open \
  --repo owner/repo
```

### Thai Language Support

```bash
# Milestones support Unicode/Thai text
gh api repos/:owner/:repo/milestones --method POST \
  -f title="รอบที่ 1" \
  -f description="การพัฒนาเฟสแรก"

python scripts/milestone.py create "เวอร์ชัน 1.0" \
  --description "เปิดตัวครั้งแรก"
```

## Listing Milestones

### All Milestones

```bash
# All open milestones
gh api repos/:owner/:repo/milestones

# All milestones (open and closed)
gh api repos/:owner/:repo/milestones?state=all

# Only closed milestones
gh api repos/:owner/:repo/milestones?state=closed
```

### Sorting and Filtering

```bash
# Sort by due date (ascending)
gh api repos/:owner/:repo/milestones?sort=due_on&direction=asc

# Sort by due date (descending)
gh api repos/:owner/:repo/milestones?sort=due_on&direction=desc

# Sort by completeness
gh api repos/:owner/:repo/milestones?sort=completeness&direction=desc
```

### Using Script with Formatting

```bash
# List open milestones (default)
python scripts/milestone.py list

# List all milestones
python scripts/milestone.py list --state all

# List closed milestones
python scripts/milestone.py list --state closed

# Sort by completeness
python scripts/milestone.py list --sort completeness

# Specific repository
python scripts/milestone.py list --repo owner/repo --state all
```

### Output Format (Script)

```
#      Title                          Progress             Due Date     State   
----------------------------------------------------------------------------------
1      v1.0 Release                   5/10 (50%)          2025-12-31   open    
2      Sprint 1                       0/3 (0%)            2025-11-30   open    
3      Bug Fixes                      8/8 (100%)          None         closed  
```

## Viewing Milestone Details

```bash
# Get single milestone
gh api repos/:owner/:repo/milestones/1

# Using script with formatted output
python scripts/milestone.py get 1
```

### Output Format (Script)

```
Milestone #1: v1.0 Release
============================================================
State: open
Description: First major release with core features
Due Date: 2025-12-31 00:00:00 UTC
Progress: 5/10 (50%)
URL: https://github.com/owner/repo/milestone/1
```

## Updating Milestones

### Update Title

```bash
gh api repos/:owner/:repo/milestones/1 --method PATCH \
  -f title="v1.0.1 Release"

python scripts/milestone.py update 1 --title "v1.0.1 Release"
```

### Update Description

```bash
gh api repos/:owner/:repo/milestones/1 --method PATCH \
  -f description="Updated description with new scope"

python scripts/milestone.py update 1 \
  --description "Updated description"
```

### Update Due Date

```bash
gh api repos/:owner/:repo/milestones/1 --method PATCH \
  -f due_on="2025-12-31T23:59:59Z"

python scripts/milestone.py update 1 --due-date 2025-12-31
```

### Update Multiple Fields

```bash
gh api repos/:owner/:repo/milestones/1 --method PATCH \
  -f title="v1.1 Release" \
  -f description="Minor update" \
  -f due_on="2026-01-15T00:00:00Z"

python scripts/milestone.py update 1 \
  --title "v1.1 Release" \
  --description "Minor update" \
  --due-date 2026-01-15
```

## Closing and Reopening Milestones

### Close Milestone

```bash
# Direct API
gh api repos/:owner/:repo/milestones/1 --method PATCH \
  -f state="closed"

# Using script
python scripts/milestone.py close 1
```

### Reopen Milestone

```bash
# Direct API
gh api repos/:owner/:repo/milestones/1 --method PATCH \
  -f state="open"

# Using script
python scripts/milestone.py reopen 1
```

## Deleting Milestones

⚠️ **Warning:** Deleting a milestone removes it permanently but does NOT delete associated issues.

```bash
# Direct API
gh api repos/:owner/:repo/milestones/1 --method DELETE

# Using script
python scripts/milestone.py delete 1
```

## Assigning Issues to Milestones

### During Issue Creation

```bash
# Create issue with milestone
gh issue create \
  --title "Bug fix" \
  --body "Description" \
  --milestone 1
```

### Update Existing Issue

```bash
# Assign milestone to existing issue
gh issue edit 123 --milestone 1

# Remove milestone from issue
gh issue edit 123 --milestone ""
```

### Using gh API

```bash
# Assign milestone
gh api repos/:owner/:repo/issues/123 --method PATCH \
  -f milestone=1

# Remove milestone (set to null)
gh api repos/:owner/:repo/issues/123 --method PATCH \
  -F milestone=null
```

## Bulk Operations

### List All Issues in a Milestone

```bash
# Get issues for milestone #1
gh issue list --milestone 1

# With JSON output
gh issue list --milestone 1 --json number,title,state
```

### Close All Issues in Milestone

```bash
# Get all open issues in milestone and close them
gh issue list --milestone 1 --state open --json number \
  | jq -r '.[].number' \
  | xargs -I {} gh issue close {}
```

### Move Issues Between Milestones

```bash
# Move all issues from milestone 1 to milestone 2
gh issue list --milestone 1 --json number \
  | jq -r '.[].number' \
  | xargs -I {} gh issue edit {} --milestone 2
```

## Advanced Patterns

### Milestone Progress Report

```bash
# Get milestone with progress
gh api repos/:owner/:repo/milestones/1 \
  | jq '{
      title: .title,
      progress: "\(.closed_issues)/\(.open_issues + .closed_issues)",
      percent: ((.closed_issues / (.open_issues + .closed_issues)) * 100)
    }'
```

### Find Overdue Milestones

```bash
# List milestones with due dates in the past
gh api repos/:owner/:repo/milestones?state=open \
  | jq --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.[] | select(.due_on != null and .due_on < $now) | {title, due_on}'
```

### Create Milestones from Template

```bash
# Create quarterly milestones for 2025
for quarter in Q1 Q2 Q3 Q4; do
  python scripts/milestone.py create "$quarter 2025" \
    --description "Goals for $quarter"
done
```

## Integration with Issues

### Create Issue with Milestone

```bash
# Using gh issue create
gh issue create \
  --title "Implement feature X" \
  --body "Description" \
  --milestone 1 \
  --label "enhancement"

# Using Python script (milestone.py doesn't create issues, use create_issue.py)
# Create issue first, then assign milestone
gh issue create --title "Bug fix" --body "..." | grep -oP '#\d+' | xargs -I {} gh issue edit {} --milestone 1
```

## Best Practices

### Naming Conventions

```bash
# Version releases
"v1.0", "v1.1", "v2.0-beta"

# Time-based
"Q1 2025", "Sprint 23", "December 2025"

# Feature-based
"Authentication", "Dashboard Redesign", "API v2"

# Thai examples
"เวอร์ชัน 1.0", "ไตรมาส 1 2568", "การปรับปรุงหน้าแดชบอร์ด"
```

### Due Dates

```bash
# End of month
--due-date 2025-12-31

# Specific sprint end
--due-date 2025-11-15

# Quarter end
--due-date 2025-03-31  # Q1
--due-date 2025-06-30  # Q2
--due-date 2025-09-30  # Q3
--due-date 2025-12-31  # Q4
```

### Progress Tracking

1. **Create milestone at sprint/release start**
2. **Assign issues as planned**
3. **Monitor progress**: `python scripts/milestone.py get <number>`
4. **Close when complete**: `python scripts/milestone.py close <number>`

## Common Workflows

### Release Planning Workflow

```bash
# 1. Create milestone for release
python scripts/milestone.py create "v1.0 Release" \
  --description "First production release" \
  --due-date 2025-12-31

# 2. Create and assign issues
gh issue create --title "Feature X" --milestone 1
gh issue create --title "Bug Y" --milestone 1

# 3. Monitor progress
python scripts/milestone.py list

# 4. When complete, close milestone
python scripts/milestone.py close 1
```

### Sprint Planning Workflow

```bash
# 1. Create sprint milestone
python scripts/milestone.py create "Sprint 10" \
  --due-date 2025-11-15

# 2. Assign issues to sprint
gh issue edit 101 --milestone 1
gh issue edit 102 --milestone 1

# 3. Daily standup - check progress
python scripts/milestone.py get 1

# 4. End of sprint - close completed
python scripts/milestone.py close 1
```

## Troubleshooting

### Issue: "Not Found" Error

```bash
# Verify repository format is correct
gh api repos/owner/repo/milestones

# Check if milestone number exists
python scripts/milestone.py list
```

### Issue: Authentication Required

```bash
# Check auth status
gh auth status

# Login if needed
gh auth login
```

### Issue: Date Format Error

```bash
# Correct ISO 8601 format required
# ✅ Correct: 2025-12-31T00:00:00Z
# ❌ Wrong: 2025-12-31
# ❌ Wrong: 12/31/2025

# Script handles this automatically
python scripts/milestone.py create "Test" --due-date 2025-12-31
```

## Reference

### API Endpoints

```
GET    /repos/:owner/:repo/milestones              # List milestones
GET    /repos/:owner/:repo/milestones/:number      # Get milestone
POST   /repos/:owner/:repo/milestones              # Create milestone
PATCH  /repos/:owner/:repo/milestones/:number      # Update milestone
DELETE /repos/:owner/:repo/milestones/:number      # Delete milestone
```

### Fields

- `title` (string, required) - Milestone title
- `state` (string) - "open" or "closed"
- `description` (string) - Milestone description
- `due_on` (string) - ISO 8601 timestamp

### Response Fields

- `number` (integer) - Milestone number
- `open_issues` (integer) - Number of open issues
- `closed_issues` (integer) - Number of closed issues
- `html_url` (string) - Web URL to milestone
- `created_at` (string) - Creation timestamp
- `updated_at` (string) - Last update timestamp
