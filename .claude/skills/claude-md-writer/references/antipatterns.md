# CLAUDE.md Anti-patterns

Common mistakes that reduce Claude Code's effectiveness and how to avoid them.

## Anti-pattern 1: The Novel
```markdown
❌ BAD:
The frontend of our application uses React, which is a JavaScript library for building user interfaces. React was created by Facebook and uses a virtual DOM to efficiently update the UI. We chose React because it has a large ecosystem and community support...
```

```markdown
✅ GOOD:
- Frontend: React 18 with TypeScript
- State: Redux Toolkit with RTK Query
```

**Why it's bad**: Claude already knows what React is. Focus on YOUR specific implementation.

## Anti-pattern 2: The Vague Directive
```markdown
❌ BAD:
- Use best practices for testing
- Follow standard conventions
- Optimize performance where needed
```

```markdown
✅ GOOD:
- Test files: *.test.ts co-located with source
- Commit format: "type(scope): message"
- Bundle size limit: 200KB gzipped
```

**Why it's bad**: "Best practices" means different things to different teams. Be specific.

## Anti-pattern 3: The Missing Compilation Step
```markdown
❌ BAD:
## Commands
- `npm test`: Run tests
```

```markdown
✅ GOOD:
## Commands (TypeScript Project)
- `npm run build`: Compile TypeScript
- `npm test`: Run tests
Note: ALWAYS build before testing after TS changes
```

**Why it's bad**: Claude forgets to compile, tests fail mysteriously, time wasted debugging.

## Anti-pattern 4: The Wishful Thinking
```markdown
❌ BAD:
- Always write secure code
- Never hardcode secrets
- Follow OWASP guidelines
```

```markdown
✅ GOOD:
## Security Checklist (Every PR)
- [ ] Validate inputs with Zod: `z.string().email()`
- [ ] Use parameterized queries: `db.query(sql, [param])`
- [ ] Check auth: `requireAuth()` middleware on all protected routes
```

**Why it's bad**: General security advice doesn't prevent specific vulnerabilities.

## Anti-pattern 5: The Documentation Dump
```markdown
❌ BAD:
## React Hooks Documentation
useState is a Hook that lets you add React state to function components...
[500 lines of React docs copied]
```

```markdown
✅ GOOD:
## Our Hook Patterns
- Custom hooks in src/hooks/
- Prefix with "use": useAuth, useApi
- See React docs: https://react.dev/reference/react
```

**Why it's bad**: Wastes context window on information Claude already has.

## Anti-pattern 6: The Outdated Commands
```markdown
❌ BAD:
- `npm run dev`: Start server (written 6 months ago)
[Project now uses yarn and different scripts]
```

```markdown
✅ GOOD:
## Commands (Updated: 2024-01-15)
- `yarn dev`: Start server (port 3000)
- `yarn test`: Run tests
```

**Why it's bad**: Claude follows outdated instructions, nothing works.

## Anti-pattern 7: The Everything File
```markdown
❌ BAD:
[1000+ lines covering every possible scenario]
```

```markdown
✅ GOOD:
# Project Root CLAUDE.md
[Core architecture and standards - 100 lines]

# src/frontend/CLAUDE.md
[Frontend-specific details - 50 lines]

# src/backend/CLAUDE.md
[Backend-specific details - 50 lines]
```

**Why it's bad**: Hierarchical organization provides relevant context without overload.

## Anti-pattern 8: The Assumption Trap
```markdown
❌ BAD:
- Use our standard error handling
- Follow the usual deployment process
- Apply company conventions
```

```markdown
✅ GOOD:
- Error handling: Throw AppError with code + message
- Deploy: Push to main → GitHub Actions → AWS ECS
- Naming: camelCase vars, PascalCase components
```

**Why it's bad**: Claude doesn't know your "standard" unless you define it.

## Anti-pattern 9: The Test Afterthought
```markdown
❌ BAD:
## Testing
- Write tests when possible
```

```markdown
✅ GOOD:
## Testing Requirements
- New features: Unit tests required
- Bug fixes: Add regression test
- API changes: Update integration tests
- Run before commit: `npm test -- --related`
```

**Why it's bad**: Vague testing guidance leads to untested code.

## Anti-pattern 10: The Solo Author
```markdown
❌ BAD:
[CLAUDE.md written by one person, never reviewed]
```

```markdown
✅ GOOD:
[CLAUDE.md reviewed by team, tested with actual Claude Code usage]

## Contributors
- Initial: @jane (2024-01-01)
- Security section: @security-team
- Last review: Team retrospective (2024-01-15)
```

**Why it's bad**: Single perspective misses important context others would catch.

## Red Flags in Your CLAUDE.md

If you see these, refactor immediately:

1. **"TODO" items older than a week** - Either do them or delete them
2. **Contradictions** - "Use TypeScript" vs "new files can be .js"
3. **Dead commands** - Scripts that no longer exist
4. **Generic examples** - "handleClick" instead of real function names
5. **No dates** - Can't tell if information is current
6. **No specifics** - "Modern React patterns" vs "Functional components with hooks"
7. **Copy-pasted content** - Identical sections across unrelated projects
8. **Missing gotchas** - Known issues team discusses but aren't documented
9. **Academic tone** - Explaining theory instead of practice
10. **No validation** - Never tested with actual Claude Code

## Quick Fixes

### From Vague to Specific
- ❌ "Good performance" → ✅ "LCP <2.5s, bundle <200KB"
- ❌ "Use TypeScript" → ✅ "TypeScript strict mode, no any types"
- ❌ "Test thoroughly" → ✅ "80% coverage, test edge cases"

### From Assumption to Explicit
- ❌ "Standard PR process" → ✅ "PR needs 2 approvals + passing CI"
- ❌ "Usual auth flow" → ✅ "JWT in cookies, refresh every 15min"
- ❌ "Company style" → ✅ "ESLint config: @company/eslint-config"

### From Passive to Active
- ❌ "Tests should pass" → ✅ "Run tests before every commit"
- ❌ "Consider security" → ✅ "Validate all inputs with Zod schemas"
- ❌ "Optimize when needed" → ✅ "Profile if response >500ms"

## The Golden Rule

If you wouldn't be able to onboard a new developer with just this CLAUDE.md, it's not complete enough for Claude Code.

## Testing Your CLAUDE.md

```bash
# The ultimate test
claude /clear
claude "I'm a new developer on this project. Can you explain the architecture and show me how to add a new feature?"

# If Claude struggles or asks clarifying questions about basics, your CLAUDE.md needs work
```
