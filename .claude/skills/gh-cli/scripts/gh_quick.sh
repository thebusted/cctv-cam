#!/bin/bash
# Quick GitHub CLI operations wrapper

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function to check if gh is installed
check_gh() {
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}❌ Error: GitHub CLI (gh) is not installed${NC}"
        echo "Install from: https://cli.github.com/"
        exit 1
    fi
}

# Helper function to check auth
check_auth() {
    if ! gh auth status &> /dev/null; then
        echo -e "${RED}❌ Error: Not authenticated with GitHub${NC}"
        echo "Run: gh auth login"
        exit 1
    fi
}

# Create issue from template
create_issue_from_template() {
    local template_file="$1"
    local title="$2"
    local labels="${3:-}"
    local assignees="${4:-}"
    
    if [ ! -f "$template_file" ]; then
        echo -e "${RED}❌ Error: Template file not found: $template_file${NC}"
        exit 1
    fi
    
    local cmd="gh issue create --title \"$title\" --body-file \"$template_file\""
    
    [ -n "$labels" ] && cmd="$cmd --label \"$labels\""
    [ -n "$assignees" ] && cmd="$cmd --assignee \"$assignees\""
    
    echo -e "${YELLOW}Creating issue...${NC}"
    eval "$cmd"
    echo -e "${GREEN}✅ Issue created successfully!${NC}"
}

# Quick bug report
quick_bug() {
    local title="$1"
    local description="$2"
    local labels="${3:-bug}"
    
    gh issue create \
        --title "Bug: $title" \
        --body "$description" \
        --label "$labels"
    
    echo -e "${GREEN}✅ Bug report created!${NC}"
}

# Quick feature request
quick_feature() {
    local title="$1"
    local description="$2"
    local labels="${3:-enhancement}"
    
    gh issue create \
        --title "Feature: $title" \
        --body "$description" \
        --label "$labels"
    
    echo -e "${GREEN}✅ Feature request created!${NC}"
}

# List my open issues
my_issues() {
    echo -e "${YELLOW}Your open issues:${NC}"
    gh issue list --assignee "@me" --state open
}

# List PRs waiting for my review
my_reviews() {
    echo -e "${YELLOW}PRs waiting for your review:${NC}"
    gh pr list --search "is:open review-requested:@me"
}

# Quick PR creation from current branch
quick_pr() {
    local title="$1"
    local body="${2:-}"
    local draft="${3:-false}"
    
    local cmd="gh pr create --title \"$title\""
    
    if [ -n "$body" ]; then
        cmd="$cmd --body \"$body\""
    fi
    
    if [ "$draft" = "true" ]; then
        cmd="$cmd --draft"
    fi
    
    echo -e "${YELLOW}Creating pull request...${NC}"
    eval "$cmd"
    echo -e "${GREEN}✅ Pull request created!${NC}"
}

# Show usage
usage() {
    cat << EOF
GitHub CLI Quick Operations

Usage: gh_quick.sh <command> [arguments]

Commands:
    issue-from-template <template_file> <title> [labels] [assignees]
        Create an issue from a template file
        
    bug <title> <description> [labels]
        Quick bug report (default label: bug)
        
    feature <title> <description> [labels]
        Quick feature request (default label: enhancement)
        
    my-issues
        List your open issues
        
    my-reviews
        List PRs waiting for your review
        
    pr <title> [body] [draft:true|false]
        Quick PR from current branch

Examples:
    gh_quick.sh bug "Login fails" "Users can't login after update"
    gh_quick.sh feature "Dark mode" "Add dark theme support"
    gh_quick.sh my-issues
    gh_quick.sh pr "Add login feature" "Implements user authentication" false
    gh_quick.sh issue-from-template bug_template.md "Fix login bug" "bug,urgent" "@me"

EOF
}

# Main command dispatcher
main() {
    check_gh
    check_auth
    
    local command="${1:-}"
    
    case "$command" in
        issue-from-template)
            shift
            create_issue_from_template "$@"
            ;;
        bug)
            shift
            quick_bug "$@"
            ;;
        feature)
            shift
            quick_feature "$@"
            ;;
        my-issues)
            my_issues
            ;;
        my-reviews)
            my_reviews
            ;;
        pr)
            shift
            quick_pr "$@"
            ;;
        help|--help|-h|"")
            usage
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $command${NC}"
            usage
            exit 1
            ;;
    esac
}

main "$@"
