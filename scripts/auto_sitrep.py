#!/usr/bin/env python3
"""
Auto SITREP Generator — Daily Federation Status Report

Reads federation log, session status, git log, and generates
a daily SITREP markdown file.
"""

import json
import subprocess
import os
from pathlib import Path
from datetime import datetime, timezone

FEDERATION_DIR = Path.home() / ".federation"
SESSION_PATH = FEDERATION_DIR / "sessions" / "active-session.json"
REPO_ROOT = Path(__file__).parent.parent


def get_git_log(since: str = "24 hours ago") -> list[dict]:
    """Get git commits since specified time."""
    try:
        result = subprocess.run(
            ["git", "log", f"--since={since}", "--pretty=format:%H|%s|%ci|%an"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        
        commits = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                hash_, subject, date, author = line.split("|", 3)
                commits.append({
                    "hash": hash_[:8],
                    "subject": subject,
                    "date": date,
                    "author": author
                })
        return commits
    except Exception as e:
        return [{"error": str(e)}]


def get_session_status() -> dict:
    """Read federation session status."""
    if not SESSION_PATH.exists():
        return {"status": "no_active_session"}
    
    try:
        return json.loads(SESSION_PATH.read_text())
    except Exception as e:
        return {"status": "error", "error": str(e)}


def count_tasks_by_status(session: dict) -> dict:
    """Count tasks by status."""
    counts = {"pending": 0, "in_progress": 0, "completed": 0, "blocked": 0}
    
    for task in session.get("tasks", []):
        status = task.get("status", "pending")
        if status in counts:
            counts[status] += 1
        else:
            counts["pending"] += 1
    
    return counts


def get_active_agents(session: dict) -> list[str]:
    """Get list of active agents."""
    active = []
    for agent, info in session.get("agents", {}).items():
        if info.get("status") == "active":
            active.append(agent)
    return active


def get_router_metrics(session: dict) -> dict:
    """Get router accuracy metrics from session."""
    router = session.get("router", {})
    return {
        "version": router.get("version", "unknown"),
        "tier": router.get("tier", "unknown"),
        "accuracy": router.get("accuracy")
    }


def generate_sitrep() -> str:
    """Generate SITREP markdown."""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M UTC")
    
    # Gather data
    session = get_session_status()
    commits = get_git_log()
    
    # Format SITREP
    lines = []
    lines.append(f"# SITREP — {date_str}")
    lines.append(f"**Generated:** {time_str}  ")
    lines.append(f"**Sprint:** {session.get('sprint', 'N/A')}  ")
    lines.append(f"**Session:** {session.get('session_id', 'N/A')}")
    lines.append("")
    
    # Agent Status
    lines.append("## Agent Status")
    lines.append("")
    
    if "agents" in session:
        for agent, info in session["agents"].items():
            status = info.get("status", "unknown")
            task = info.get("current_task") or "No active task"
            
            # Emoji indicator
            emoji = {
                "active": "🔥",
                "idle": "💤",
                "standby": "⏸️",
                "error": "❌"
            }.get(status, "❓")
            
            lines.append(f"- {emoji} **{agent.capitalize()}:** {status.upper()} — {task[:50]}")
    else:
        lines.append("_No session data available_")
    
    lines.append("")
    
    # Task Summary
    lines.append("## Task Summary")
    lines.append("")
    
    if "tasks" in session:
        task_counts = count_tasks_by_status(session)
        total = sum(task_counts.values())
        
        lines.append(f"- **Total:** {total}")
        lines.append(f"- ⏳ Pending: {task_counts['pending']}")
        lines.append(f"- 🔄 In Progress: {task_counts['in_progress']}")
        lines.append(f"- ✅ Completed: {task_counts['completed']}")
        lines.append(f"- 🚫 Blocked: {task_counts['blocked']}")
        
        # List pending/high priority tasks
        pending = [t for t in session.get("tasks", []) if t.get("status") == "pending"]
        if pending:
            lines.append("")
            lines.append("### Pending Tasks")
            for task in pending[:5]:  # Top 5
                prio = task.get("priority", "medium")
                desc = task.get("description", "No description")
                lines.append(f"- [{prio.upper()}] {desc[:60]}")
    else:
        lines.append("_No task data available_")
    
    lines.append("")
    
    # Router Metrics
    lines.append("## Router Metrics")
    lines.append("")
    
    metrics = get_router_metrics(session)
    lines.append(f"- **Version:** {metrics['version']}")
    lines.append(f"- **Active Tier:** {metrics['tier']}")
    if metrics['accuracy']:
        lines.append(f"- **Accuracy:** {metrics['accuracy']*100:.1f}%")
    else:
        lines.append("- **Accuracy:** Not evaluated today")
    
    lines.append("")
    
    # Git Activity
    lines.append("## Git Activity (Last 24h)")
    lines.append("")
    
    if commits:
        lines.append(f"**{len(commits)} commits**")
        lines.append("")
        
        for commit in commits[:10]:  # Show last 10
            if "error" in commit:
                lines.append(f"_Error reading git log: {commit['error']}_")
                break
            lines.append(f"- `{commit['hash']}` {commit['subject'][:50]} — _{commit['author']}_")
        
        if len(commits) > 10:
            lines.append(f"- _... and {len(commits) - 10} more_")
    else:
        lines.append("_No commits in last 24 hours_")
    
    lines.append("")
    
    # Blockers
    lines.append("## Blockers")
    lines.append("")
    
    blocked = [t for t in session.get("tasks", []) if t.get("status") == "blocked"]
    if blocked:
        for task in blocked:
            lines.append(f"- 🚫 {task.get('description', 'Unknown')[:60]}")
    else:
        lines.append("_No blockers reported_")
    
    lines.append("")
    
    # Next Day Plan
    lines.append("## Next Day Plan")
    lines.append("")
    
    # Auto-generate based on pending tasks
    if pending:
        lines.append("Top priorities:")
        for i, task in enumerate(pending[:3], 1):
            agent = task.get("assigned_to", "kimi")
            lines.append(f"{i}. **{agent.capitalize()}:** {task.get('description', 'Task')[:50]}")
    else:
        lines.append("_No pending tasks — sprint may be complete_")
    
    lines.append("")
    
    # Footer
    lines.append("---")
    lines.append(f"*Auto-generated by federation-sync v1.0*")
    
    return "\n".join(lines)


def save_sitrep(content: str, output_dir: Path = None) -> Path:
    """Save SITREP to file."""
    if output_dir is None:
        output_dir = REPO_ROOT / "docs" / "sitreps"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"SITREP-{date_str}.md"
    filepath = output_dir / filename
    
    filepath.write_text(content)
    return filepath


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-generate daily SITREP")
    parser.add_argument("--print", action="store_true", help="Print to stdout only")
    parser.add_argument("--output", type=Path, help="Output directory")
    
    args = parser.parse_args()
    
    sitrep = generate_sitrep()
    
    if args.print:
        print(sitrep)
    else:
        filepath = save_sitrep(sitrep, args.output)
        print(f"SITREP saved to: {filepath}")


if __name__ == "__main__":
    main()
