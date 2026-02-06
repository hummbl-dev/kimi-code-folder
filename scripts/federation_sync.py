#!/usr/bin/env python3
"""
Federation Sync — File-Based Session Persistence

Implements the Day 2 design: ~/.federation/sessions/active-session.json
with optimistic concurrency and per-agent status tracking.
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime, timezone

# Paths
FEDERATION_DIR = Path.home() / ".federation"
SESSIONS_DIR = FEDERATION_DIR / "sessions"
HISTORY_DIR = FEDERATION_DIR / "history"
AGENTS_DIR = FEDERATION_DIR / "agents"

ACTIVE_SESSION_PATH = SESSIONS_DIR / "active-session.json"


def ensure_dirs():
    """Ensure all federation directories exist."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def read_session() -> dict | None:
    """Read current active session."""
    if not ACTIVE_SESSION_PATH.exists():
        return None
    try:
        return json.loads(ACTIVE_SESSION_PATH.read_text())
    except Exception:
        return None


def write_session(session: dict) -> bool:
    """
    Write session with optimistic concurrency (atomic rename).
    Returns True on success, False if file was modified concurrently.
    """
    ensure_dirs()
    
    # Read current to check for conflicts
    current = read_session()
    
    # Optimistic check: if session exists and has different updated_at, conflict
    if current and session.get("updated_at") != current.get("updated_at"):
        return False
    
    # Update timestamp
    session["updated_at"] = utc_now()
    
    # Atomic write
    temp_path = ACTIVE_SESSION_PATH.with_suffix(".tmp")
    temp_path.write_text(json.dumps(session, indent=2))
    temp_path.rename(ACTIVE_SESSION_PATH)
    
    return True


def create_session(sprint: str, owner: str = "kimi") -> dict:
    """Create a new active session."""
    session = {
        "session_id": f"sess-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "owner": owner,
        "sprint": sprint,
        "status": "active",
        "agents": {},
        "tasks": [],
        "router": {
            "version": "v3",
            "tier": 2,
            "accuracy": None
        }
    }
    
    # Initialize all agents as idle
    for agent in ["kimi", "claude", "copilot", "codex", "ollama"]:
        session["agents"][agent] = {
            "status": "idle",
            "current_task": None,
            "last_seen": utc_now()
        }
    
    write_session(session)
    return session


def update_agent_status(agent: str, status: str, task: str = None, max_retries: int = 3) -> bool:
    """
    Update an agent's status in the shared session.
    Retries on conflict with exponential backoff.
    """
    for attempt in range(max_retries):
        session = read_session()
        
        if not session:
            # Auto-create session if none exists
            session = create_session(sprint="auto-created")
        
        # Update this agent's status
        session["agents"][agent] = {
            "status": status,
            "current_task": task,
            "last_seen": utc_now()
        }
        
        if write_session(session):
            return True
        
        # Conflict - wait and retry
        time.sleep(0.1 * (2 ** attempt))
    
    return False


def add_task(description: str, assigned_to: str, priority: str = "medium") -> str:
    """Add a task to the current session."""
    session = read_session()
    if not session:
        session = create_session(sprint="auto-created")
    
    task_id = f"task-{len(session['tasks']) + 1:03d}"
    task = {
        "id": task_id,
        "description": description,
        "assigned_to": assigned_to,
        "status": "pending",
        "priority": priority,
        "created_at": utc_now()
    }
    
    session["tasks"].append(task)
    
    for attempt in range(3):
        if write_session(session):
            return task_id
        session = read_session()
        session["tasks"].append(task)
        time.sleep(0.1)
    
    return None


def update_task_status(task_id: str, status: str, completed: bool = False) -> bool:
    """Update task status."""
    session = read_session()
    if not session:
        return False
    
    for task in session["tasks"]:
        if task["id"] == task_id:
            task["status"] = status
            if completed:
                task["completed_at"] = utc_now()
            break
    
    for attempt in range(3):
        if write_session(session):
            return True
        session = read_session()
        time.sleep(0.1)
    
    return False


def update_router_stats(version: str, tier: int, accuracy: float = None):
    """Update router statistics in session."""
    session = read_session()
    if not session:
        return False
    
    session["router"] = {
        "version": version,
        "tier": tier,
        "accuracy": accuracy,
        "last_evaluated": utc_now()
    }
    
    return write_session(session)


def archive_session():
    """Archive current session to history and clear active."""
    session = read_session()
    if not session:
        return False
    
    session["status"] = "archived"
    session["archived_at"] = utc_now()
    
    # Save to history
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    history_path = HISTORY_DIR / f"{timestamp}.json"
    history_path.write_text(json.dumps(session, indent=2))
    
    # Clear active
    ACTIVE_SESSION_PATH.unlink(missing_ok=True)
    
    return True


def get_status():
    """Print federation status."""
    session = read_session()
    
    if not session:
        print("No active session.")
        return
    
    print(f"Federation Session: {session['session_id']}")
    print(f"Sprint: {session['sprint']}")
    print(f"Owner: {session['owner']}")
    print(f"Updated: {session['updated_at']}")
    print()
    
    print("Agents:")
    for agent, info in session["agents"].items():
        status_icon = {
            "active": "🔥",
            "idle": "💤",
            "standby": "⏸️",
            "error": "❌"
        }.get(info["status"], "❓")
        task = info.get("current_task") or "(no task)"
        print(f"  {status_icon} {agent:10} [{info['status']:8}] {task[:40]}")
    
    print()
    print("Tasks:")
    for task in session["tasks"]:
        status_icon = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "blocked": "🚫"
        }.get(task["status"], "❓")
        print(f"  {status_icon} [{task['priority']:6}] {task['description'][:50]}")
    
    print()
    print(f"Router: {session['router']['version']} (Tier {session['router']['tier']})")
    if session['router'].get('accuracy'):
        print(f"Accuracy: {session['router']['accuracy']*100:.1f}%")


# --- CLI ---

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Federation Session Sync")
    parser.add_argument("--status", action="store_true", help="Show federation status")
    parser.add_argument("--create", type=str, metavar="SPRINT", help="Create new session")
    parser.add_argument("--agent", type=str, help="Set agent name (for --update)")
    parser.add_argument("--update", type=str, choices=["active", "idle", "standby", "error"],
                       help="Update agent status")
    parser.add_argument("--task", type=str, help="Set current task")
    parser.add_argument("--add-task", type=str, help="Add a task")
    parser.add_argument("--assign-to", type=str, help="Assign task to agent")
    parser.add_argument("--priority", type=str, default="medium", help="Task priority")
    parser.add_argument("--archive", action="store_true", help="Archive current session")
    
    args = parser.parse_args()
    
    if args.status:
        get_status()
    elif args.create:
        session = create_session(args.create)
        print(f"Created session: {session['session_id']}")
    elif args.update and args.agent:
        if update_agent_status(args.agent, args.update, args.task):
            print(f"Updated {args.agent}: {args.update}")
        else:
            print("Failed to update (conflict)")
    elif args.add_task and args.assign_to:
        task_id = add_task(args.add_task, args.assign_to, args.priority)
        if task_id:
            print(f"Added task: {task_id}")
        else:
            print("Failed to add task")
    elif args.archive:
        if archive_session():
            print("Session archived")
        else:
            print("No session to archive")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
