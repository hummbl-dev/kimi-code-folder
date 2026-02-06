# Workspace Architecture — Federation Standard

## Overview
Each agent in the federation operates from a dedicated workspace directory
under `/Users/others/`. Workspaces are self-contained git repositories.

## Directory Layout

```
/Users/others/                          # User home
├── kimi-code-folder/                   # 🔧 Kimi's workspace (git repo)
│   ├── agents/kimi/                    # Identity stack (AUTHORITATIVE)
│   │   ├── IDENTITY.md
│   │   ├── AGENT.md
│   │   ├── SOUL.md
│   │   ├── USER.md
│   │   ├── MEMORY.md
│   │   └── memory/
│   ├── scripts/                        # Federation tooling (real files)
│   ├── docs/                           # Architecture, planning, incidents
│   ├── .federation/                    # Task queue, votes, metrics
│   ├── .github/                        # CI, Copilot instructions
│   ├── AGENTS.md                       # Federation roster & routing
│   ├── FEDERATION_LOG.md               # Cross-agent activity log
│   ├── KIMI_IDENTITY_MANIFEST.md       # Identity invariant declaration
│   ├── README.md                       # Kimi CLI tool documentation
│   └── [other tool docs]
│
├── claude-code-folder/                 # 📚 Claude's workspace
│   ├── CLAUDE.md                       # Claude Code bootstrap file
│   └── [future: agents/claude/]
│
├── codex-code-folder/                  # 🧭 Codex workspace
│   ├── AGENTS.md                       # Codex identity & federation info
│   └── README.md
│
├── ollama-code-folder/                 # 🏠 Ollama workspace
│   ├── AGENTS.md                       # Ollama identity & federation info
│   └── README.md
│
├── shared-hummbl-space/                # Shared resources (NOT symlinked into repos)
│   ├── agents/                         # 58 agent identity stacks (registry)
│   ├── avatars/                        # PNG assets
│   ├── scripts/                        # Shared scripts
│   └── memory/                         # Shared memory
│
└── bin/                                # Entry scripts
    ├── kimi-entry.sh                   # cd ~/kimi-code-folder && exec kimi-cli
    ├── claude-entry.sh                 # cd ~/claude-code-folder && exec claude
    └── codex-entry.sh                  # cd ~/codex-code-folder && exec codex
```

## Invariants

| Rule | Rationale |
|------|-----------|
| Agent workspaces are self-contained git repos | Portability, clean history |
| No symlinks traversing `../` in tracked repos | Security, portability (ADR-001) |
| Identity authority = `agents/<name>/` | Single source of truth |
| `shared-hummbl-space/` is reference, not dependency | Repos must work without it |
| Entry scripts set `cd` before `exec` | Agents start in their own workspace |
| `.federation/` is the coordination layer | Tasks, votes, metrics live here |
| `FEDERATION_LOG.md` is the cross-agent journal | Every structural change gets logged |

## Identity Resolution Order
When an agent needs to determine "who am I":
1. `agents/<name>/IDENTITY.md` — **authoritative**
2. `KIMI_IDENTITY_MANIFEST.md` — invariant declaration (Kimi-specific)
3. `IDENTITY_CLARIFICATION.md` — disambiguation guide
4. ~~Root-level IDENTITY.md~~ — **does not exist** (per ADR-001)
5. ~~shared-hummbl-space/IDENTITY.md~~ — **not referenced** from within repos

## Relationship: Workspaces vs shared-hummbl-space

```
shared-hummbl-space/     →  Source of SHARED templates and assets
                             NOT a dependency of any workspace repo
                             May be referenced from ~/  (user convenience)
                             MUST NOT be symlinked into git-tracked repos

kimi-code-folder/        →  Self-contained. Has its own agents/kimi/ identity.
                             Does not depend on shared-hummbl-space at runtime.
```

## Agent Launch Flow

```
User types "kimi"
  → ~/bin/kimi-entry.sh
    → export AGENT_NAME="kimi"
    → export FEDERATION_HOME="$HOME/kimi-code-folder/.federation"
    → cd ~/kimi-code-folder
    → exec kimi-cli "$@"
      → kimi-cli reads agents/kimi/IDENTITY.md from cwd
      → Kimi is Kimi
```
