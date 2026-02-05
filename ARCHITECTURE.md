# Kimi Code Architecture

> Understanding how Kimi Code works internally — from tool execution to subagent orchestration.

---

## Overview

Kimi Code CLI is built on a **tool-use architecture** where the AI agent:
1. Receives a user request
2. Plans an approach using available tools
3. Executes tools (often in parallel)
4. Analyzes results and iterates
5. Returns the final output

The system is designed for **efficiency**, **context isolation**, and **parallel execution**.

---

## Core Components

### 1. Tool System

Kimi Code has direct access to 10 built-in tools:

```
┌─────────────────────────────────────────────────────────┐
│                    TOOL LAYER                           │
├──────────────┬──────────────┬──────────────┬────────────┤
│   File Ops   │  Code Search │    Shell     │    Web     │
├──────────────┼──────────────┼──────────────┼────────────┤
│ • ReadFile   │ • Grep       │ • Shell      │ • SearchWeb│
│ • WriteFile  │ • Glob       │              │ • FetchURL │
│ • StrReplace │              │              │            │
└──────────────┴──────────────┴──────────────┴────────────┘
┌─────────────────────────────────────────────────────────┐
│              MEDIA & SUBAGENTS                          │
├──────────────────────┬──────────────────────────────────┤
│ • ReadMediaFile      │ • Task (spawn subagents)         │
└──────────────────────┴──────────────────────────────────┘
```

**Key Design Principles:**
- **Exact matching**: `StrReplaceFile` uses literal string matching
- **Partial reads**: `ReadFile` supports `line_offset` and `n_lines`
- **Parallel execution**: Multiple tool calls can be made in one response

---

### 2. Subagent Model

The `Task` tool spawns **isolated subagents** that:
- Run in fresh contexts (no memory of parent conversation)
- Execute specific delegated tasks
- Return results to the parent
- Cannot communicate with each other

```
┌─────────────────────────────────────────────────────────┐
│                   PARENT AGENT                          │
│              (You — Kimi Code CLI)                      │
└──────────────────┬──────────────────────────────────────┘
                   │ spawns
        ┌──────────┼──────────┐
        ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │Task #1 │ │Task #2 │ │Task #3 │     ← Parallel subagents
   │Subagent│ │Subagent│ │Subagent│        (isolated contexts)
   └───┬────┘ └───┬────┘ └───┬────┘
       │          │          │
       └──────────┼──────────┘
                  ▼
         Returns results to parent
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              PARENT SYNTHESIZES RESULTS                 │
└─────────────────────────────────────────────────────────┘
```

**When to Use Subagents:**

| Scenario | Use Subagent? | Reason |
|----------|---------------|--------|
| Fix 3 unrelated bugs | ✅ Yes | Parallel execution, independent contexts |
| Debug a failed attempt | ✅ Yes | Fresh context, no pollution |
| Research multiple topics | ✅ Yes | Parallel information gathering |
| Analyze large codebase | ✅ Yes | Split across modules |
| Simple file edit | ❌ No | Direct execution is faster |
| Sequential dependent tasks | ❌ No | Parent maintains context |

---

### 3. Skills System

Skills are **modular extensions** stored at `~/.codex/skills/*/SKILL.md`:

```
skills/
├── vercel-deploy/SKILL.md
├── imagegen/SKILL.md
├── pdf/SKILL.md
├── playwright/SKILL.md
└── ... (33 total skills)
```

**How Skills Work:**
1. Kimi Code detects context (e.g., "deploy to Vercel")
2. Reads the relevant SKILL.md file
3. Follows the documented workflow
4. Uses any bundled scripts or tools

**Skill Categories:**

| Category | Skills |
|----------|--------|
| **Deployment** | vercel-deploy, netlify-deploy, cloudflare-deploy, render-deploy |
| **Media** | imagegen, speech, sora, transcribe, pdf, screenshot |
| **DevTools** | playwright, jupyter-notebook, spreadsheet |
| **GitHub** | gh-fix-ci, gh-address-comments, yeet |
| **Notion** | notion-knowledge-capture, notion-meeting-intelligence, notion-research-documentation, notion-spec-to-implementation |
| **Security** | security-best-practices, security-ownership-map, security-threat-model |
| **Game Dev** | develop-web-game |
| **Integrations** | linear, figma, figma-implement-design, sentry, openai-docs |

---

### 4. MCP Integration

Kimi Code supports **Model Context Protocol (MCP)** servers for external integrations:

**How MCP Works:**
- MCP servers are pre-configured in the environment
- They appear as additional tools Kimi Code can invoke
- Some require authentication tokens
- Kimi Code doesn't configure them mid-session

**Example MCP Servers:**
- Figma (design-to-code)
- Linear (issue tracking)
- Sentry (error monitoring)

**When MCP Fails:**
If an MCP tool fails due to missing auth, Kimi Code will report:
```
The Linear MCP server returned an error: Authentication required.
Please set the LINEAR_API_TOKEN environment variable.
```

---

### 5. Execution Flow

A typical task flows through these stages:

```
┌──────────────────────────────────────────────────────────────┐
│ 1. UNDERSTAND                                                │
│    • Parse user request                                      │
│    • Identify goals and constraints                          │
│    • Ask clarifying questions if needed                      │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. EXPLORE (if needed)                                       │
│    • Glob/Grep to understand codebase structure              │
│    • ReadFile to examine relevant files                      │
│    • FetchURL for external documentation                     │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. PLAN                                                      │
│    • Break into subtasks if multi-part                       │
│    • Set up todo list for tracking                           │
│    • Identify relevant skills                                │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. EXECUTE                                                   │
│    • Parallel tool calls where independent                   │
│    • Sequential calls where dependent                        │
│    • Spawn subagents for complex parallel work               │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. VERIFY                                                    │
│    • Run tests if available                                  │
│    • Check results against requirements                      │
│    • Report success or issues                                │
└──────────────────────────────────────────────────────────────┘
```

---

### 6. Context Management

Kimi Code manages context carefully:

**Strengths:**
- Large context window for complex tasks
- Partial file reads to avoid loading unnecessary content
- Subagent isolation prevents context pollution

**Limitations:**
- Each subagent starts fresh (no shared memory)
- Very large codebases may need splitting
- Previous conversation history is maintained but tools re-read files

**Best Practices:**
- Use `line_offset` and `n_lines` for large files
- Delegate exploration to subagents for huge codebases
- Re-read files if they've been modified

---

### 7. Error Handling

Kimi Code follows a three-tier error recovery strategy:

| Tier | Pattern | Example |
|------|---------|---------|
| **Retry** | Same approach, transient issue | Network timeout → retry request |
| **Adapt** | Different approach, same goal | Wrong file path → search for correct one |
| **Escalate** | Report to user with diagnostics | Missing dependency → explain what's needed |

**Never:**
- Silently fail
- Make up information
- Guess with file modifications

**Always:**
- Report blockers clearly
- Provide diagnostic information
- Suggest next steps

---

## Design Philosophy

1. **Minimal Changes**: Make only the changes necessary to achieve the goal
2. **Verify Before Acting**: Read files before modifying them
3. **Parallel by Default**: Execute independent operations simultaneously
4. **Clear Communication**: Explain reasoning and report issues transparently
5. **User Control**: Let users guide outcomes, Kimi Code handles implementation
