# CLAUDE.md Validation Checklist

Use this checklist to ensure your CLAUDE.md file is complete and effective. A well-validated CLAUDE.md dramatically improves Claude Code's performance.

## Essential Requirements ✅

### Header and Overview
- [ ] Project name clearly stated
- [ ] One-line project purpose/description
- [ ] Clear indication of project type (web app, API, CLI, etc.)

### Architecture Section
- [ ] Primary programming language(s) specified
- [ ] Framework(s) and major libraries listed with versions
- [ ] Database type and ORM/driver specified
- [ ] State management approach documented
- [ ] Testing framework(s) identified

### Development Commands
- [ ] Start/run command documented
- [ ] Test command included
- [ ] Build command specified
- [ ] Lint/format command listed
- [ ] All commands actually work when run
- [ ] Port numbers specified for services

### Code Style Guidelines
- [ ] Language-specific conventions stated
- [ ] Import/export patterns clarified
- [ ] Async pattern preferences (promises vs async/await)
- [ ] Component/function patterns described
- [ ] File naming conventions specified

### Testing Conventions
- [ ] Test file location and naming pattern
- [ ] Types of tests (unit, integration, e2e)
- [ ] Test execution strategy
- [ ] Coverage expectations (if any)
- [ ] TDD approach documented (if used)

### Workflow Rules
- [ ] Branch naming convention
- [ ] Commit message format
- [ ] PR requirements and review process
- [ ] Merge strategy (squash, rebase, etc.)

## Important Additions 🎯

### For Web Applications
- [ ] API endpoint patterns documented
- [ ] Authentication method specified
- [ ] Frontend/backend separation explained
- [ ] Bundle size or performance targets
- [ ] Environment variable handling

### For APIs/Services
- [ ] Request/response format specified
- [ ] Error response structure documented
- [ ] Pagination approach described
- [ ] Rate limiting mentioned
- [ ] Authentication/authorization pattern

### For Compiled Languages
- [ ] **Build before test reminder** (CRITICAL for TypeScript)
- [ ] Compilation command specified
- [ ] Build output directory noted
- [ ] Watch mode command (if available)

### Security Considerations
- [ ] Input validation approach
- [ ] Authentication requirements
- [ ] Sensitive data handling
- [ ] Security checklist for PRs

## Quality Checks 🔍

### Clarity and Conciseness
- [ ] No unnecessary explanations of basic concepts
- [ ] Specific tool names, not generic descriptions
- [ ] Commands are exact, not approximate
- [ ] Examples provided for complex patterns
- [ ] Bullet points used effectively

### Accuracy
- [ ] All commands tested and working
- [ ] Version numbers are current
- [ ] File paths are correct
- [ ] Port numbers are accurate
- [ ] No conflicting information

### Completeness
- [ ] Covers all major development workflows
- [ ] Includes troubleshooting for known issues
- [ ] Documents project-specific quirks
- [ ] Has enough detail for new team member onboarding

### Maintenance
- [ ] Date of last update noted (optional)
- [ ] Version controlled with the project
- [ ] Team has agreed on the content
- [ ] Process exists for keeping it updated

## Testing Your CLAUDE.md 🧪

### Functional Test
1. Clear Claude Code's context: `/clear`
2. Ask Claude to explain the project architecture
3. Verify Claude understands correctly
4. Ask Claude to create a new feature
5. Check if Claude follows all conventions

### Completeness Test
1. Give CLAUDE.md to new team member
2. Can they understand the project?
3. Can they run all basic commands?
4. Do they know the workflow?

### Common Issues to Check
- [ ] No "after TS changes, build before test" = test failures
- [ ] Missing port numbers = connection confusion
- [ ] No branch convention = git chaos
- [ ] Vague descriptions = Claude makes assumptions
- [ ] Out-of-date commands = frustration

## Red Flags 🚩

These indicate your CLAUDE.md needs improvement:

1. **Claude asks about basic project structure** - Architecture section incomplete
2. **Tests fail mysteriously** - Missing compilation step documentation
3. **Wrong code style generated** - Guidelines not specific enough
4. **Claude uses wrong commands** - Commands section inaccurate
5. **Security vulnerabilities in generated code** - Security patterns not documented
6. **Claude doesn't understand workflow** - Workflow rules unclear

## Scoring Guide

Rate your CLAUDE.md:

- **Excellent (90-100%)**: All essential items ✓, most important additions ✓, passes all tests
- **Good (70-89%)**: All essential items ✓, some important additions, minor issues in testing
- **Needs Work (50-69%)**: Most essential items ✓, missing important context
- **Poor (Below 50%)**: Missing essential items, Claude struggles to understand project

## Quick Fixes for Common Problems

### Problem: Too Long
- Move detailed docs to links
- Use concise bullet points
- Remove obvious information
- Focus on project-specific knowledge

### Problem: Too Vague
- Add specific version numbers
- Include exact commands
- Provide concrete examples
- Specify file paths and ports

### Problem: Outdated
- Set calendar reminder for updates
- Update during architecture changes
- Review in sprint retrospectives
- Assign ownership to team member

### Problem: Ignored by Team
- Include in onboarding process
- Require updates in PR template
- Reference in code reviews
- Demonstrate value with examples

## Final Validation

Before considering your CLAUDE.md complete:

```bash
# 1. Test with fresh Claude Code session
claude /clear
claude "Explain our project architecture"

# 2. Test a common task
claude "Create a new API endpoint for user preferences"

# 3. Verify conventions followed
# Review generated code for style compliance

# 4. Check for security issues
claude "Review this for security vulnerabilities"
```

If Claude can correctly understand and work with your project after these tests, your CLAUDE.md is ready for production use!
