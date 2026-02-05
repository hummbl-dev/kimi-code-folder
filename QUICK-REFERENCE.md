# Kimi Code CLI - Quick Reference Card

> **One-page cheat sheet** for common patterns and quick lookups

## 🚀 Getting Started

```bash
# Install Kimi Code CLI
npm install -g @moonshot-ai/kimi-cli

# Start interactive session
kimi

# Run one-off task
kimi "fix the bug in auth.ts"

# Use in VS Code
Install "Kimi Code" extension from marketplace
```

## 🛠️ Tool Cheatsheet

| Tool | Syntax | Use When |
|------|--------|----------|
| **ReadFile** | Read specific lines or entire file | Need to see code |
| **WriteFile** | Create or overwrite file | New file or complete rewrite |
| **StrReplaceFile** | Exact string → new string | Surgical edits (requires exact match) |
| **Grep** | Search pattern in files | Find specific code/text |
| **Glob** | Pattern match files | Find files by name/extension |
| **Shell** | Execute terminal command | Run tests, install deps, build |
| **SearchWeb** | Query search engines | Latest docs, error solutions |
| **FetchURL** | Get webpage content | Read documentation |
| **ReadMediaFile** | Process images/audio/video | Extract text from screenshot |
| **Task** | Spawn subagent | Delegate independent work |

## 💬 Request Templates

### Bug Fixes
```
✅ "Fix the null pointer exception in UserService.java and add tests"
✅ "Debug why login fails when email contains '+' character"
✅ "Resolve TypeScript errors in src/components/"
```

### Feature Development
```
✅ "Add JWT authentication to the API with refresh tokens"
✅ "Implement dark mode toggle with localStorage persistence"
✅ "Create a user dashboard with profile and settings tabs"
```

### Refactoring
```
✅ "Refactor all API routes to use async/await instead of promises"
✅ "Convert class components to functional components with hooks"
✅ "Extract shared logic from auth components into custom hook"
```

### Testing
```
✅ "Write unit tests for PaymentService with 80% coverage"
✅ "Add integration tests for the checkout flow"
✅ "Fix failing tests in test/auth.test.ts"
```

### Documentation
```
✅ "Generate API documentation from JSDoc comments"
✅ "Add README with setup instructions and examples"
✅ "Document the database schema with ER diagram description"
```

### Deployment
```
✅ "Deploy the main branch to Vercel production"
✅ "Set up CI/CD pipeline with GitHub Actions"
✅ "Configure environment variables for staging"
```

### Code Review
```
✅ "Review auth.ts for security vulnerabilities"
✅ "Check all API routes for proper error handling"
✅ "Analyze bundle size and suggest optimizations"
```

## 🎯 Best Practices

### DO ✅
- **Be specific** about the outcome you want
- **Mention file paths** when known (faster execution)
- **State constraints** (don't modify tests, keep API compatible)
- **Request verification** (run tests, check build)
- **Use parallel tasks** (fix bugs in auth.ts, payments.ts, and update docs)

### DON'T ❌
- **Over-specify implementation** ("use X library at line Y")
- **Be vague** ("fix it", "make it better")
- **Expect mind-reading** (provide context for bugs)
- **Chain too many steps** without checkpoints
- **Ignore errors** (if Kimi reports blockers, address them)

## 🧠 Mental Models

### When to Use Subagents
```
Independent tasks → Spawn subagents in parallel
├─ "Fix 5 unrelated bugs across different files" ✅
├─ "Update docs for each of 10 API endpoints" ✅
└─ "Implement 3 independent features" ✅

Sequential tasks → Do it directly
├─ "Create database schema, then seed data" 🔄
├─ "Refactor function, then update all callers" 🔄
└─ "Fix bug, then write test for it" 🔄
```

### Parallel vs Sequential
```
Parallel (faster):
"Fix auth.ts, update tests, add docs" → 3 subagents

Sequential (better context):
"Refactor auth flow, then update tests to match" → 1 agent, 2 steps
```

## 🔥 Common Patterns

### Exploratory Debugging
```
1. "Search the codebase for all usages of deprecated function X"
2. "Show me the call chain from API endpoint to database"
3. "Find all files importing UserService"
```

### Bulk Operations
```
1. "Add error handling to all API routes"
2. "Update all console.log to use winston logger"
3. "Convert all var declarations to const/let"
```

### Verification Workflow
```
1. "Implement feature X"
2. "Run tests to verify the changes"
3. "If tests fail, debug and fix"
```

## ⚡ Skill Shortcuts

| Say This | Activates | Result |
|----------|-----------|--------|
| "deploy to vercel" | `vercel-deploy` | Deploys to Vercel |
| "extract PDF text" | `pdf` | Processes PDF |
| "transcribe audio" | `speech` | Speech-to-text |
| "screenshot this site" | `web-screenshot` | Captures webpage |
| "generate an image of X" | `image-generation` | Creates image |

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| **StrReplaceFile fails** | Kimi reads file first - ensure exact match including whitespace |
| **Subagent gets stuck** | Kimi retries automatically; if blocked, reports diagnostic info |
| **Skill not working** | Check if auth token needed (e.g., `OPENAI_API_KEY`) |
| **Context too large** | Use line ranges in ReadFile, or spawn subagents |
| **Unclear requirements** | Kimi will ask clarifying questions - provide more context |

## 📏 Size Guidelines

| Task Scope | Approach | Example |
|------------|----------|---------|
| **1 file, 1 function** | Direct edit | "Fix bug in getUserById()" |
| **1 file, multiple changes** | Direct edit | "Refactor UserService class" |
| **2-5 files, related** | Direct edit or 1 subagent | "Update auth flow across files" |
| **5+ files, independent** | Multiple subagents | "Fix bugs in 10 components" |
| **Entire module** | Multiple subagents | "Refactor authentication system" |

## 🎓 Learning Path

1. **Start simple**: "Fix the bug in file.ts"
2. **Add verification**: "Fix the bug and run tests"
3. **Go parallel**: "Fix bugs in auth.ts and payments.ts"
4. **Use skills**: "Fix bugs and deploy to vercel"
5. **Complex workflows**: "Refactor auth, update tests, update docs, deploy staging"

## 📖 Full Documentation

- **README.md** - Project overview and getting started
- **ARCHITECTURE.md** - How Kimi works internally
- **USER-GUIDE.md** - Detailed guide on effective usage
- **TOOLS.md** - Complete reference for all 10 tools
- **SKILLS.md** - Catalog of all 33 skills
- **BEST-PRACTICES.md** - Patterns and anti-patterns
- **EXAMPLES.md** - 21 scenario-based examples
- **.github/copilot-instructions.md** - Guide for GitHub Copilot integration
- **COPILOT-CONTEXT.md** - Condensed reference for AI assistants

---

**Pro Tip**: Frame requests as outcomes ("add authentication"), not methods ("use passport.js at line 45"). Kimi chooses the best approach based on your codebase.
