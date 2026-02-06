# ADR-001: No Root-Level Identity Symlinks in Agent Workspaces

## Status
**Accepted** — 2026-02-06

## Context
During Day 2 federation ops, Kimi created symlinks at the kimi-code-folder root
pointing to `../shared-hummbl-space/` (IDENTITY.md, AGENT.md, SOUL.md, USER.md,
avatars, scripts). Claude subsequently deleted them as stale Codex artifacts.

This created a coordination conflict: two agents made opposing decisions on the
same files without a handoff or vote.

## Decision
Agent workspace roots **do not** contain symlinks to shared-hummbl-space.

### Rationale
1. **Name collisions** — `scripts/` exists as a real directory containing
   federation Python code. A symlink would shadow it.
2. **Identity authority** — Each agent's identity lives in `agents/<name>/`.
   Root-level identity files create ambiguity about which is canonical.
3. **Portability** — Symlinks to `../shared-hummbl-space/` break when the repo
   is cloned to a different machine or path.
4. **Security** — Parent-traversing symlinks risk accidental exposure (ref:
   Day 2 security incident with `/Users/others` push).

## Consequences
- `agents/kimi/` is the **single source of truth** for Kimi's identity
- Shared federation config (if needed) should be copied or submoduled, not symlinked
- The `~/` root may retain its symlinks for the user's convenience, but
  individual workspace repos must be self-contained

## Alternatives Considered
- **Symlinks with guards** — .gitignore the symlinks, add pre-commit check.
  Rejected: doesn't solve the name collision or portability issues.
- **Git submodule** — Mount shared-hummbl-space as a submodule. Viable future
  option but adds complexity.
