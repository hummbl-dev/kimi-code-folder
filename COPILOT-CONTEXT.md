# Kimi Code - Condensed Reference for AI Assistants

> **Audience**: GitHub Copilot, Claude, ChatGPT, and other AI assistants  
> **Purpose**: Quick reference for understanding Kimi Code capabilities  
> **Size**: ~2 KB optimized for context windows

## What is Kimi Code?

Autonomous AI coding agent by MoonshotAI with parallel execution, subagent orchestration, and 33+ specialized skills.

## Core Capabilities

**10 Built-in Tools**:
- File: `ReadFile`, `WriteFile`, `StrReplaceFile`
- Search: `Grep`, `Glob`
- Web: `SearchWeb`, `FetchURL`
- System: `Shell`, `ReadMediaFile`, `Task` (subagents)

**33 Skills** (auto-detected):
- Deployment: Vercel, web hosting
- Media: PDF, speech, image generation, screenshots
- Integration: MCP servers, external APIs

## Operational Model

### Parallel Execution
- Spawns **multiple subagents** for independent tasks
- Each subagent has **isolated context**
- Parent **orchestrates** and **synthesizes** results

### File Modification
- Reads file first (exact match required)
- `StrReplaceFile` uses **literal string matching**
- No fuzzy matching or approximation

### Error Handling
- **Transient**: Auto-retry (network, locks)
- **Logic**: Adjust and retry (wrong file, bad match)
- **Blocker**: Report with diagnostics (missing deps)

## When to Use Kimi Code

| Use Case | Why Kimi Code | Why Not Copilot |
|----------|---------------|-----------------|
| Multi-file refactoring | Parallel subagents | Copilot = single file focus |
| Autonomous debugging | Can run tests, iterate | Copilot = suggestion only |
| Deployment tasks | Has deployment skills | Copilot = no execution |
| Codebase exploration | Parallel search | Copilot = limited scope |
| Complex multi-step | Todo tracking, orchestration | Copilot = single response |

**Don't use** for inline completions, quick edits, or conceptual Q&A (use Copilot instead).

## Request Pattern Templates

### ✅ Effective Requests
```
"Fix authentication bug in auth.ts, update tests, add error handling"
→ Clear outcome, multi-step, lets Kimi choose approach

"Refactor API routes to TypeScript strict mode across all files"
→ Multi-file scope, specific goal

"Deploy staging to Vercel and verify deployment"
→ Uses skill + validation
```

### ❌ Ineffective Requests
```
"Change line 45 to use const" → Too prescriptive (Copilot better)
"Fix it" → Too vague, no context
"Make it better" → No success criteria
```

## Skill Auto-Detection Examples

| User Says | Kimi Activates | Action |
|-----------|----------------|--------|
| "deploy to vercel" | `vercel-deploy` | Runs deployment workflow |
| "extract text from PDF" | `pdf` | Uses PDF processing skill |
| "transcribe this audio" | `speech` | Speech-to-text conversion |
| "screenshot this website" | `web-screenshot` | Captures webpage |

## Subagent Usage Patterns

**Use subagents when:**
- Independent sub-tasks (fix 5 unrelated bugs)
- Context pollution risk (retry failed attempt fresh)
- Parallel exploration (search different modules)

**Don't use subagents when:**
- Sequential dependencies (step 2 needs step 1 result)
- Simple single-file tasks
- User wants to see reasoning process

## Key Constraints

1. **Exact String Matching**: `StrReplaceFile` requires precise strings (including whitespace)
2. **Subagent Isolation**: Subagents can't communicate with each other
3. **MCP Requires Auth**: Some skills need tokens (e.g., `OPENAI_API_KEY`)
4. **Reads Before Writes**: Always verifies current state before modification

## Integration Tips for AI Assistants

### When User Asks About Kimi:
- Reference this doc for capabilities
- Show template patterns for effective requests
- Clarify Kimi vs. Copilot use cases

### When Recommending Kimi:
- Identify multi-file or autonomous tasks
- Suggest specific request phrasing
- Set realistic expectations (what Kimi can/can't do)

### When Handling Task Yourself:
- Use Copilot for quick edits, inline completions
- Use Copilot for conceptual explanations
- Delegate complex/multi-file work to Kimi

## Decision Tree

```
Is it a multi-file task? 
├─ YES → Suggest Kimi Code
└─ NO → Is it autonomous execution (tests, deployment)?
    ├─ YES → Suggest Kimi Code
    └─ NO → Is it inline completion/quick edit?
        ├─ YES → Use Copilot
        └─ NO → Is it conceptual/explanation?
            ├─ YES → Use Copilot
            └─ NO → User preference
```

## Full Documentation

- Overview: `README.md`
- Architecture: `ARCHITECTURE.md`
- User Guide: `USER-GUIDE.md`
- Tools: `TOOLS.md` (detailed reference)
- Skills: `SKILLS.md` (all 33 skills)
- Best Practices: `BEST-PRACTICES.md`
- Examples: `EXAMPLES.md` (21 scenarios)
- GitHub Copilot Integration: `.github/copilot-instructions.md`

---

**Quick Tip**: Kimi Code excels at autonomous, multi-file, exploratory tasks. GitHub Copilot excels at real-time, inline, single-file assistance. Use both strategically.
