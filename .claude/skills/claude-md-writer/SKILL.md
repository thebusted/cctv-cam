---
name: claude-md-writer
description: Creates effective CLAUDE.md files for Claude Code projects. Use when setting up hierarchical memory for new projects, refactoring existing CLAUDE.md files, or establishing consistent documentation patterns across teams. Generates project-specific context files that transform Claude Code from a general assistant into a specialized team member who understands your codebase, architecture, standards, and workflow.
---

# CLAUDE.md Writer

## Overview

This skill helps create effective CLAUDE.md files - the critical hierarchical memory system that transforms Claude Code from a general assistant into a productive team member who understands your specific project. Based on production experience, proper CLAUDE.md setup is the difference between frustration and 2-10x productivity gains.

## Workflow Decision Tree

When asked to create or update a CLAUDE.md file:

1. **Identify the level needed:**
   - User preferences across all projects? → Create `~/.claude/CLAUDE.md`
   - Project-wide architecture and standards? → Create `./CLAUDE.md`
   - Module-specific context? → Create `src/[module]/CLAUDE.md`

2. **Gather project information:**
   - Ask about tech stack, architecture patterns, and team conventions
   - Check for existing project documentation
   - Identify project-specific gotchas and requirements

3. **Generate appropriate CLAUDE.md:**
   - Use templates from `references/templates.md`
   - Customize for the specific project needs
   - Include all essential sections
   - Validate completeness with `references/validation.md`

4. **Test and refine:**
   - Have user test with actual Claude Code tasks
   - Refine based on what Claude misunderstands
   - Update when architecture changes

## Creating Project-Level CLAUDE.md

The project-level CLAUDE.md is the most critical. It should take 20-30 minutes to create properly and dramatically improves Claude's effectiveness.

### Essential Structure

```markdown
# Project: [Name] - [One-line purpose]

## Architecture
- State management: [Specific tool/pattern, e.g., "Redux Toolkit with RTK Query"]
- API layer: [Framework and patterns, e.g., "Express.js with middleware chains"]
- Database: [Type and ORM, e.g., "PostgreSQL with Prisma ORM"]
- Testing: [Framework and approach, e.g., "Jest + React Testing Library, TDD"]

## Development Commands
- `npm run dev`: Start development server (port 3000)
- `npm run test`: Run test suite (always run before commits)
- `npm run test:watch`: Run tests in watch mode during development
- `npm run lint`: Check code style
- `npm run build`: Production build
- `npm run migrate`: Run database migrations

## Code Style Guidelines
- Use TypeScript for all new files
- Functional components with hooks (no class components)
- Async/await over Promise.then() chains
- Destructure imports: `import { useState, useEffect } from 'react'`
- Co-locate tests with source files as *.test.ts

## Testing Conventions
- Unit tests: *.test.ts files co-located with source
- Integration tests: tests/integration/
- E2E tests: tests/e2e/ using Playwright
- Run specific test files during iteration, not full suite
- Write test first, verify it fails, then implement (TDD)

## Workflow Rules
- Branch naming: feature/*, fix/*, hotfix/*
- Commit format: "type: description" (feat/fix/chore/docs)
- PR requires: passing tests, type checking, lint, 1 approval
- Never commit directly to main
- Always run `npm test` before pushing
```

### Project-Specific Sections

Add these sections based on project needs:

```markdown
## API Patterns
- All endpoints return { data, error } structure
- Use middleware for auth: requireAuth()
- Pagination: ?page=1&limit=20
- Error codes follow RFC 7807

## Security Requirements
- All user input must be validated with Zod schemas
- Use parameterized queries only (no string concatenation)
- Authentication: JWT in httpOnly cookies
- Rate limiting: 100 requests/minute per IP

## Performance Targets
- Bundle size: <200KB gzipped
- LCP: <2.5s, FID: <100ms, CLS: <0.1
- API response time: p95 <500ms
- Use React.lazy() for route splitting

## Known Gotchas
- After TypeScript changes, ALWAYS run `npm run build` before `npm test`
- PostgreSQL requires explicit timezone handling
- Our auth service has 30-second cache, wait before testing permission changes
- webpack-dev-server sometimes needs restart after adding new dependencies
```

## Creating Module-Level CLAUDE.md

Keep module-level files concise and specific:

```markdown
# Module: User Authentication

## Purpose
Handles user registration, login, JWT management, and permission checks.

## Key Components
- AuthProvider: React context for auth state
- useAuth: Hook for accessing current user
- requireAuth: HOC for protected routes
- authService: API communication layer

## Internal APIs
- authService.login(email, password): Returns user + token
- authService.refresh(): Refreshes JWT using refresh token
- authService.logout(): Clears tokens and user state

## Module-Specific Rules
- Never store tokens in localStorage (use httpOnly cookies)
- All auth endpoints must use HTTPS in production
- Refresh tokens rotate on each use
- Session timeout: 24 hours
```

## Best Practices

### DO:
- **Be specific**: "Use Redux Toolkit" not "use state management"
- **Include commands**: Exact commands to run, not general advice
- **Document quirks**: The non-obvious things that waste time
- **Add examples**: Show actual code patterns for complex rules
- **Update regularly**: When architecture changes, update immediately
- **Test with Claude**: Verify Claude understands by running actual tasks

### DON'T:
- **Over-document basics**: Claude knows language syntax
- **Include everything**: Focus on project-specific knowledge
- **Copy documentation**: Link to docs instead of reproducing them
- **Forget compilation**: Critical for TypeScript/compiled languages
- **Skip validation**: Always test your CLAUDE.md works

## Special Cases

### For Mixed-Language Projects
```markdown
## Critical Build Order
TypeScript files must be compiled before running:
1. Make changes to .ts/.tsx files
2. Run `npm run build` to compile
3. Then run `npm test` to verify
Never run tests without compiling TypeScript first!
```

### For Security-Critical Applications
```markdown
## Security Checklist (Every PR)
- [ ] No hardcoded secrets or API keys
- [ ] All user inputs validated with Zod schemas
- [ ] SQL queries use parameterization
- [ ] Authentication checks on all protected routes
- [ ] Rate limiting applied to public endpoints
- [ ] Security headers configured (CSP, HSTS, etc.)
```

### For Data Science Projects
```markdown
## Data Pipeline
1. Raw data: s3://bucket/raw/ (never modify)
2. Processed: s3://bucket/processed/
3. Models: s3://bucket/models/v{version}/
4. Always version datasets with DVC
5. Reproduce results: `dvc repro pipeline.yaml`

## Model Development
- Notebooks: experiments/ (not in git)
- Production code: src/ (must have tests)
- Use MLflow for experiment tracking
- Tag experiments: mlflow.set_tag("purpose", "description")
```

## Resources

### scripts/
- `analyze_project.py`: Analyzes a codebase to suggest CLAUDE.md content
- `validate_claude_md.py`: Validates CLAUDE.md files for completeness

### references/
- `templates.md`: Ready-to-use CLAUDE.md templates for different project types
- `examples.md`: Real-world CLAUDE.md examples from production projects
- `validation.md`: Comprehensive checklist for CLAUDE.md completeness
- `antipatterns.md`: Common mistakes and how to avoid them

### assets/
- `starter-templates/`: Complete CLAUDE.md files for common stacks
