# INC-002: Agent Coordination Contradiction — Symlink Creation/Deletion

## Date
2026-02-06

## Severity
Medium — No data loss, but demonstrates a systemic coordination gap.

## Timeline
| Time | Agent | Action |
|------|-------|--------|
| T+0 | Kimi 🔧 | Identified missing symlinks to shared-hummbl-space |
| T+1 | Kimi 🔧 | Created 6 symlinks at kimi-code-folder root (IDENTITY.md, AGENT.md, SOUL.md, USER.md, avatars, scripts) |
| T+2 | User | Approved Kimi's action ("proceed") |
| T+3 | Claude 📚 (VS Code) | Identified root-level AGENT.md, IDENTITY.md, SOUL.md, USER.md as "old Codex identity files" |
| T+4 | Claude 📚 | Deleted them (`rm AGENT.md IDENTITY.md SOUL.md USER.md`) |
| T+5 | Claude 📚 | Committed clean state, pushed to origin |
| T+6 | Kimi 🔧 | Reviewed Claude's work, confirmed "repo is clean" |

## Root Cause
1. **No handoff protocol** — Claude was not informed that Kimi had just created those files
2. **No file provenance check** — Claude ran `head -3` and saw Codex content (from shared-hummbl-space), assumed they were stale leftovers rather than fresh symlinks
3. **Session context isolation** — Kimi (in terminal) and Claude (in VS Code) had separate conversation contexts with no shared state

## Impact
- Symlinks created by Kimi were deleted by Claude within the same session
- User received contradictory "done" signals from both agents
- No data was lost (symlink targets still exist in shared-hummbl-space)

## Resolution
- ADR-001 resolves the architectural question (no root symlinks)
- Protocol changes below prevent recurrence

## Recommended Protocol Changes

### 1. Pre-Modification Check
Before deleting or modifying files at the workspace root, agents MUST:
1. Run: `git log --oneline -3` (check recent commits)
2. Run: `ls -la <file>` (check if symlink vs real file)
3. If file was created/modified in last 2 hours → PAUSE and ask user

### 2. Federation Lock File
```bash
# Before making structural changes:
echo "$(date -u +%FT%TZ) <agent> modifying-root-files" >> .federation/LOCK
# After completion:
sed -i '' '/<agent> modifying-root-files/d' .federation/LOCK
```

### 3. Cross-Agent Visibility
After completing structural changes, agents should append to FEDERATION_LOG.md:
```markdown
## [TIMESTAMP] Agent: Structural Change
- **What:** [description]
- **Why:** [rationale or ADR reference]
- **Files affected:** [list]
```

This ensures the next agent to read the log understands what changed and why.
