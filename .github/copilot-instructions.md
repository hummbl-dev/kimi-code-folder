# Kimi Code CLI - GitHub Copilot Integration Guide

> **Context**: This repository uses Kimi Code CLI, an autonomous AI coding agent. This guide helps GitHub Copilot collaborate effectively with Kimi Code.

## 🤝 When to Use Kimi Code vs. GitHub Copilot

| Task Type | Best Tool | Reason |
|-----------|-----------|--------|
| **Code completion/snippets** | GitHub Copilot | Real-time, inline suggestions |
| **Single file edits** | GitHub Copilot | Fast, context-aware |
| **Multi-file refactoring** | Kimi Code | Parallel subagent execution |
| **Autonomous debugging** | Kimi Code | Can run tests, search logs, iterate |
| **Deployment/Infrastructure** | Kimi Code | Has deployment skills (Vercel, etc.) |
| **Exploratory codebase analysis** | Kimi Code | Parallel search across modules |
| **Documentation generation** | Either | Both capable |
| **Quick explanations** | GitHub Copilot | Faster response |
| **Complex multi-step tasks** | Kimi Code | Maintains todo lists, orchestrates |

## 🎯 Decision Matrix

### Use GitHub Copilot When:
- ✅ User is actively typing/editing
- ✅ Need immediate inline suggestions
- ✅ Single function/class scope
- ✅ Answering conceptual questions
- ✅ Quick code review/explanations

### Delegate to Kimi Code When:
- 🚀 Task spans 3+ files
- 🚀 Requires running shell commands
- 🚀 Needs web search/external data
- 🚀 Deployment or infrastructure work
- 🚀 Autonomous task execution needed
- 🚀 User explicitly mentions "kimi" or autonomous work

### Collaborate When:
- 🤝 Copilot suggests approach, user delegates implementation to Kimi Code
- 🤝 Kimi Code reports results, Copilot helps user interpret/refine
- 🤝 Large refactoring: Copilot plans, Kimi Code executes

## ⚡ Kimi Code Quick Reference

### Core Tools (10)
| Tool | Purpose | Example |
|------|---------|---------|
| `ReadFile` | Read file content (supports line ranges) | Read `src/auth.ts` lines 50-100 |
| `WriteFile` | Create/overwrite files | Create new test file |
| `StrReplaceFile` | Exact string replacement | Update function signature |
| `Grep` | Search file contents | Find all TODO comments |
| `Glob` | Pattern-based file search | Find all `*.test.ts` files |
| `Shell` | Execute shell commands | Run `npm test` |
| `SearchWeb` | Query search engines | Latest Next.js docs |
| `FetchURL` | Retrieve web content | Fetch API reference |
| `ReadMediaFile` | Process images/audio/video | Extract text from screenshot |
| `Task` | Spawn parallel subagent | Delegate independent sub-task |

### Key Skills (33 total - most common)
| Skill | Trigger Keywords | Capability |
|-------|------------------|------------|
| `vercel-deploy` | "deploy", "vercel" | Deploy to Vercel platform |
| `pdf` | "pdf", "extract text" | PDF processing |
| `speech` | "transcribe", "audio" | Speech-to-text |
| `web-screenshot` | "screenshot website" | Capture webpage images |
| `image-generation` | "generate image", "create picture" | DALL-E integration |
| `context-fetcher` | "fetch context", "get docs" | Smart documentation retrieval |

*Full list: See [SKILLS.md](../SKILLS.md)*

## 📋 Request Pattern Templates

### ✅ Good Patterns (Kimi Code)
```
"Fix the authentication bug in auth.ts, update tests, and add error handling"
→ Specific outcome, lets Kimi choose approach

"Refactor the API routes to use TypeScript strict mode across all files"
→ Multi-file scope, clear goal

"Deploy the staging branch to Vercel and verify the deployment"
→ Uses deployment skill + verification
```

### ❌ Anti-Patterns
```
"Change line 45 in server.js to use const instead of let"
→ Too prescriptive, better for Copilot inline edit

"Fix it" (without context)
→ Too vague, Kimi needs to understand the problem first

"Make it better"
→ No clear success criteria
```

## 🔧 Kimi Code Operational Model

### Parallel Execution
- Kimi can spawn **multiple subagents** simultaneously
- Each subagent has **isolated context**
- Parent agent **orchestrates and synthesizes** results

**Example Flow:**
```
User: "Fix bugs in auth.ts, payments.ts, and update docs"
Kimi: 
  → Spawns 3 subagents in parallel
  → Subagent 1: Fixes auth.ts
  → Subagent 2: Fixes payments.ts  
  → Subagent 3: Updates docs
  → Synthesizes results into coherent summary
```

### Error Recovery (3-Tier)
1. **Transient errors** (network, file lock) → Auto-retry
2. **Logic errors** (wrong file, bad match) → Adjust approach and retry
3. **Fundamental blockers** (missing deps, unclear requirements) → Report with diagnostic info

### File Modifications
- **Always reads file first** to ensure exact match
- **StrReplaceFile uses literal matching** (no fuzzy matching)
- **Includes whitespace** in replacement strings
- **Verifies before replacing** to prevent mismatches

## 🚨 Common Pitfalls for Users

| Pitfall | Why It Fails | Better Approach |
|---------|--------------|-----------------|
| "Use X library at line Y" | Over-constrains Kimi's approach | "Add feature X using best practices" |
| Vague requests like "improve code" | No success criteria | "Improve performance by reducing API calls" |
| Not specifying file paths | Kimi must search first | "Fix bug in src/components/Button.tsx" |
| Asking for impossible tasks | Wastes time on blockers | Verify requirements are achievable |

## 💡 GitHub Copilot Best Practices

### When User Asks About Kimi Code:
1. **Explain capabilities** using this guide
2. **Suggest appropriate use cases** based on task type
3. **Show example request patterns** from templates above
4. **Don't over-promise** - be clear about Kimi's boundaries

### When Recommending Kimi Code:
```
"This task involves multiple files and requires running tests. 
Kimi Code would be well-suited for this - you can ask it to:

'Refactor the authentication system to use JWT tokens, 
update all affected routes, and verify tests pass'

Kimi will parallelize the work across files and validate the changes."
```

### When Copilot Handles It:
```
"I can help with this directly since it's a single-file change. 
Here's the updated code..."
```

## 📚 Additional Resources

- **Full Documentation**: See `README.md` for overview
- **Architecture Details**: `ARCHITECTURE.md` explains internal model
- **User Guide**: `USER-GUIDE.md` for effective request framing
- **Complete Tool Reference**: `TOOLS.md` (all 10 tools)
- **Skills Catalog**: `SKILLS.md` (all 33 skills)
- **Best Practices**: `BEST-PRACTICES.md` (patterns and anti-patterns)
- **Examples**: `EXAMPLES.md` (21 scenario-based examples)

## 🔑 Key Takeaway

**GitHub Copilot** = Real-time coding assistant (inline, fast, contextual)  
**Kimi Code** = Autonomous coding agent (multi-file, exploratory, task-oriented)

Use both strategically based on the task at hand. When in doubt, suggest the simpler tool first (Copilot for quick edits, Kimi for complex tasks).
