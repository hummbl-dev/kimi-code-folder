# Kimi Code CLI Documentation

> Comprehensive documentation for working with Kimi Code CLI — an AI-powered coding agent by MoonshotAI.

## Quick Start

```
New to Kimi Code? → Read the [User Guide](./USER-GUIDE.md)
Want the details? → Check [Architecture](./ARCHITECTURE.md)
Need a reference? → See [Tools](./TOOLS.md) or [Skills](./SKILLS.md)
Looking for patterns? → Browse [Examples](./EXAMPLES.md)
```

## What is Kimi Code CLI?

Kimi Code CLI is an autonomous AI coding assistant that operates in your terminal and IDE. It can:

- **Read and edit code files** — partial or full file operations with precision
- **Execute shell commands** — run scripts, install dependencies, deploy applications
- **Search and analyze codebases** — find patterns across entire projects
- **Fetch web resources** — research APIs, documentation, latest information
- **Spawn parallel subagents** — delegate complex multi-part tasks efficiently
- **Access specialized skills** — deploy to Vercel/Netlify, generate images, process PDFs, and more

---

## Documentation Structure

| Document | Purpose |
|----------|---------|
| **[README.md](./README.md)** | This file — your entry point |
| **[AGENT_FIRST_MANIFESTO.md](./AGENT_FIRST_MANIFESTO.md)** | **Core philosophy** — Agent First principles, agency covenant, case studies |
| **[AGENTS.md](./AGENTS.md)** | **Federation guide** — Multi-agent coordination, routing, handoffs |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | How Kimi Code works internally — tools, subagents, skills system |
| **[USER-GUIDE.md](./USER-GUIDE.md)** | How to frame requests and get the best results |
| **[TOOLS.md](./TOOLS.md)** | Complete reference for all built-in tools |
| **[SKILLS.md](./SKILLS.md)** | Catalog of 33+ specialized skills and when to use them |
| **[BEST-PRACTICES.md](./BEST-PRACTICES.md)** | Patterns for effective collaboration |
| **[EXAMPLES.md](./EXAMPLES.md)** | Good vs. bad request patterns with explanations |
| **[FEDERATION_LOG.md](./FEDERATION_LOG.md)** | Cross-agent work tracking and handoff history |

---

## 🤖 Agent Federation

This workspace is part of a **multi-agent federation** — coordinated AI agents working together:

| Agent | Role | Best For |
|-------|------|----------|
| **Copilot** 💭 | Thinking & Review | Quick questions, IDE work, planning |
| **Kimi** 🔧 | Execution | Implementation, multi-file changes, deployment |
| **Claude** 📚 | Research & Docs | Architecture, analysis, documentation |
| **Ollama** 🏠 | Local Drafting | Fast iteration, prototyping, offline work |

### Quick Federation Commands

```bash
# Route a task to best agent
python3 scripts/route_task_v2.py "Research authentication patterns"

# Check task queue
python3 scripts/fed-queue.py list

# View federation dashboard
python3 scripts/fed-analytics.py dashboard
```

📖 **[Full federation guide → AGENTS.md](./AGENTS.md)**

---

## Key Principles

### 1. Parallel Execution
Kimi Code can make multiple independent tool calls simultaneously. Structure requests to leverage this:

```
❌ "First read file A, then read file B, then fix both"
✅ "Fix auth.ts, update tests in auth.test.ts, and update README"
```

### 2. Outcome Over Implementation
Describe **what** you want, not **how** to do it:

```
❌ "Use axios.get on line 45 and add error handling with try-catch"
✅ "Fetch user data from the API and handle network errors gracefully"
```

### 3. Subagent Isolation
Subagents work in isolation and report back. Use them for:
- Independent tasks that can run in parallel
- Context isolation (debugging, research, exploration)
- Large codebase analysis (split across modules)

### 4. Skill Auto-Detection
Kimi Code automatically identifies relevant skills based on context. You can also request specific ones:

```
"Deploy this to Vercel" → Auto-uses vercel-deploy skill
"Use the vercel-deploy skill to set up preview deployments" → Explicit
```

---

## Quick Reference

### Available Tools

| Tool | Purpose |
|------|---------|
| `ReadFile` | Read file contents (full or partial) |
| `WriteFile` | Create new files |
| `StrReplaceFile` | Replace exact strings in files |
| `Grep` | Search code with regex |
| `Glob` | Find files by pattern |
| `Shell` | Execute shell commands |
| `SearchWeb` | Search the internet |
| `FetchURL` | Fetch web page content |
| `ReadMediaFile` | Read images and videos |
| `Task` | Spawn parallel subagents |

### Popular Skills

| Skill | Use Case |
|-------|----------|
| `vercel-deploy` | Deploy to Vercel |
| `netlify-deploy` | Deploy to Netlify |
| `cloudflare-deploy` | Deploy Workers/Pages |
| `imagegen` | Generate images with DALL-E |
| `speech` | Text-to-speech conversion |
| `pdf` | PDF generation and processing |
| `playwright` | Browser automation |
| `sora` | AI video generation |
| `transcribe` | Audio transcription |

See [SKILLS.md](./SKILLS.md) for the complete list.

---

## Getting Help

- **Official Repo**: [github.com/MoonshotAI/kimi-cli](https://github.com/MoonshotAI/kimi-cli)
- **Documentation**: [moonshotai.github.io/kimi-cli](https://moonshotai.github.io/kimi-cli)
- **Homepage**: [kimi.com/code](https://kimi.com/code)

---

## License

Apache 2.0 — see the [official repository](https://github.com/MoonshotAI/kimi-cli) for details.
