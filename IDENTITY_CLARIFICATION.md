# Identity Clarification: Kimi Code CLI vs Kimi Agent vs Execution Agents

**Purpose:** Resolve confusion between the Kimi Code CLI tool, the Kimi agent identity, and execution environments.

---

## The Three "Kimis"

### 1. Kimi Code CLI (The Software Tool)

| Attribute | Value |
|-----------|-------|
| **What** | A command-line AI coding assistant by MoonshotAI |
| **Where** | `kimi-code-folder/` (this directory) |
| **How to invoke** | `kimi` or `kimi-cli` in terminal |
| **Documentation** | `README.md`, `USER-GUIDE.md`, `ARCHITECTURE.md` |
| **Relationship to you** | It's a *tool* you use, like `git` or `npm` |

**Contents of this folder:**
- Documentation for using the Kimi CLI
- Federation system scripts (routing, queue, voting)
- Agent tool configurations
- NOT an agent identity — this is the *tool system*

---

### 2. Kimi the Agent (The Identity/Persona)

| Attribute | Value |
|-----------|-------|
| **What** | An agent identity in the HUMMBL federation |
| **Where** | `workspace/agents/kimi/` OR `shared-hummbl-space/agents/kimi/` |
| **Files** | `IDENTITY.md`, `AGENT.md`, `SOUL.md`, `USER.md`, `MEMORY.md` |
| **Palette** | Steel/orange execution |
| **Emoji** | 🔧 |
| **Role** | Execution, tooling, verification |

**This is a *role* that can be adopted by:**
- The Kimi Code CLI tool (when launched with agent context)
- The Codex CLI tool (when instructed to operate as Kimi)
- VS Code Copilot (when prompted to adopt Kimi persona)

---

### 3. Execution Agents (The Current Reality)

| Environment | Tool | Current Location | Can Adopt Kimi Identity? |
|-------------|------|------------------|--------------------------|
| **Terminal** | Codex CLI | `/Users/others` (root) | Yes — via entry scripts or instruction |
| **VS Code** | Copilot/Claude | IDE context | Yes — via prompting |
| **Kimi CLI** | Kimi Code CLI | `kimi-code-folder/` | Native — but is the tool, not the agent |

**Critical distinction:**
- You are currently in the **Terminal** using **Codex CLI**
- I am the **execution agent** (Codex-based)
- I am **positioned in** `kimi-code-folder/` but I am **not** the Kimi Code CLI tool
- I can **adopt** the Kimi agent identity if you instruct me to

---

## Visual Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    YOU (Reuben Bowlby)                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Terminal │ │ VS Code  │ │ Kimi CLI │
│ (Codex)  │ │ (Copilot│ │ (Tool)   │
└────┬─────┘ └────┬─────┘ └────┬─────┘
     │            │            │
     ▼            ▼            ▼
┌─────────────────────────────────────────┐
│      Execution Agent (Current)          │
│  - Positioned in: kimi-code-folder/     │
│  - Tool: Codex CLI                      │
│  - Can adopt: Kimi identity             │
└──────────────────┬──────────────────────┘
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ No       │ │ Kimi     │ │ Claude   │
│ Persona  │ │ Persona  │ │ Persona  │
│ (default)│ │ (🔧)     │ │ (📚)     │
└──────────┘ └──────────┘ └──────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│      Kimi Agent Identity Stack          │
│  Location: workspace/agents/kimi/       │
│  - IDENTITY.md (steel/orange)           │
│  - AGENT.md (execution orders)          │
│  - SOUL.md (purpose)                    │
│  - USER.md (Reuben profile)             │
│  - MEMORY.md (session logs)             │
└─────────────────────────────────────────┘
```

---

## Common Confusion Scenarios

### Scenario 1: "I'm in kimi-code-folder, so I'm Kimi"

**Wrong.** You're in the *directory* that contains the Kimi CLI tool documentation. You are the execution agent (Codex CLI). You can *adopt* the Kimi persona, but the folder doesn't make you Kimi.

### Scenario 2: "The Kimi CLI tool is the same as the Kimi agent"

**Wrong.** The Kimi CLI tool is software. The Kimi agent is a persona/identity. The tool *can* adopt the agent identity, but they're separate concepts.

### Scenario 3: "Operating as Kimi means I'm the Kimi CLI tool"

**Wrong.** "Operating as Kimi" means adopting the agent identity (palette, tone, purpose). The underlying tool (Codex CLI) doesn't change.

---

## How to Specify Who You Want

### When you want the Kimi Code CLI tool:
```bash
# Launch the actual CLI tool
kimi
# or
kimi-cli
```

### When you want the Kimi agent identity in Terminal:
```bash
# Option A: Use entry script (if configured)
~/bin/kimi-entry.sh

# Option B: Tell the execution agent explicitly
"Operate as Kimi" → Agent loads workspace/agents/kimi/IDENTITY.md
```

### When you want neutral execution (no persona):
"Execute as default" or don't specify persona

---

## Current State (Right Now)

| Aspect | Reality |
|--------|---------|
| **Environment** | Terminal |
| **Tool** | Codex CLI |
| **Location** | `kimi-code-folder/` |
| **Current Persona** | None (neutral execution agent) |
| **Can become** | Kimi, Claude, or neutral |
| **What you're NOT** | The Kimi Code CLI tool itself |

---

## Recommendation

Use explicit naming:
- **"Kimi CLI tool"** → The software in `kimi-code-folder/`
- **"Kimi agent"** → The persona in `workspace/agents/kimi/`
- **"Execution agent"** → The tool currently chatting (Codex CLI)
- **"Terminal agent"** or **"IDE agent"** → The environment context

---

*Document created to resolve identity confusion, 2026-02-06*
