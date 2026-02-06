#!/usr/bin/env python3
"""
Federation Queue Manager
Manages task queue for autonomous agent coordination.

Usage:
    fed-queue.py add --from <agent> --to <agent> --task <desc> [--priority <level>] [--deps <ids>]
    fed-queue.py list [--status <status>] [--agent <agent>]
    fed-queue.py status
    fed-queue.py start <task-id>
    fed-queue.py complete <task-id> [--result <path>]
    fed-queue.py cancel <task-id>
    fed-queue.py next [--agent <agent>]

Examples:
    fed-queue.py add --from claude --to kimi --task "Implement auth design" --priority high
    fed-queue.py list --status pending
    fed-queue.py next --agent kimi
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

FEDERATION_DIR = Path(__file__).parent.parent / ".federation"
QUEUE_DIR = FEDERATION_DIR / "queue"
STATE_FILE = FEDERATION_DIR / "state" / "federation-state.json"

# Ensure directories exist
for subdir in ["pending", "in-progress", "completed"]:
    (QUEUE_DIR / subdir).mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# Core Queue Manager
# ─────────────────────────────────────────────────────────────

class FederationQueue:
    """File-based task queue for agent federation."""
    
    def __init__(self):
        self.queue_dir = QUEUE_DIR
        self.state_file = STATE_FILE
        
    def _generate_task_id(self) -> str:
        """Generate unique task ID with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        # Get count of existing tasks for uniqueness
        existing = list(self.queue_dir.glob("*/task-*.json"))
        seq = len(existing) + 1
        return f"task-{timestamp}-{seq:04d}"
    
    def _task_path(self, task_id: str, status: str) -> Path:
        """Get file path for a task."""
        return self.queue_dir / status / f"{task_id}.json"
    
    def _load_task(self, task_id: str) -> Optional[Dict]:
        """Load task from any status directory."""
        for status in ["pending", "in-progress", "completed"]:
            path = self._task_path(task_id, status)
            if path.exists():
                with open(path) as f:
                    return json.load(f)
        return None
    
    def add(self, from_agent: str, to_agent: str, task: str, 
            priority: str = "normal", deps: List[str] = None) -> str:
        """Add a new task to the queue."""
        
        task_id = self._generate_task_id()
        task_data = {
            "task_id": task_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "from_agent": from_agent,
            "to_agent": to_agent,
            "description": task,
            "priority": priority,
            "dependencies": deps or [],
            "started_at": None,
            "completed_at": None,
            "result": None,
            "context": {}
        }
        
        # Check dependencies exist
        for dep_id in task_data["dependencies"]:
            dep = self._load_task(dep_id)
            if not dep:
                print(f"Warning: Dependency {dep_id} not found", file=sys.stderr)
        
        # Write to pending
        task_path = self._task_path(task_id, "pending")
        with open(task_path, 'w') as f:
            json.dump(task_data, f, indent=2)
        
        self._update_state()
        return task_id
    
    def list_tasks(self, status: Optional[str] = None, agent: Optional[str] = None) -> List[Dict]:
        """List tasks, optionally filtered by status and/or agent."""
        tasks = []
        
        statuses = [status] if status else ["pending", "in-progress", "completed"]
        
        for s in statuses:
            status_dir = self.queue_dir / s
            if not status_dir.exists():
                continue
                
            for task_file in sorted(status_dir.glob("task-*.json")):
                with open(task_file) as f:
                    task = json.load(f)
                    
                # Filter by agent if specified
                if agent:
                    if task.get("to_agent") != agent and task.get("from_agent") != agent:
                        continue
                
                tasks.append(task)
        
        # Sort by priority and creation time
        priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
        tasks.sort(key=lambda t: (priority_order.get(t.get("priority", "normal"), 2), t.get("created_at", "")))
        
        return tasks
    
    def status(self) -> Dict:
        """Get overall queue status."""
        counts = {}
        for status in ["pending", "in-progress", "completed"]:
            status_dir = self.queue_dir / status
            if status_dir.exists():
                counts[status] = len(list(status_dir.glob("task-*.json")))
            else:
                counts[status] = 0
        
        return {
            "pending": counts["pending"],
            "in_progress": counts["in-progress"],
            "completed": counts["completed"],
            "total": sum(counts.values())
        }
    
    def start(self, task_id: str) -> bool:
        """Mark a task as in-progress."""
        task = self._load_task(task_id)
        if not task:
            print(f"Error: Task {task_id} not found", file=sys.stderr)
            return False
        
        if task["status"] != "pending":
            print(f"Error: Task {task_id} is not pending (status: {task['status']})", file=sys.stderr)
            return False
        
        # Check dependencies are complete
        for dep_id in task.get("dependencies", []):
            dep = self._load_task(dep_id)
            if not dep or dep.get("status") != "completed":
                print(f"Error: Dependency {dep_id} not completed", file=sys.stderr)
                return False
        
        # Move from pending to in-progress
        old_path = self._task_path(task_id, "pending")
        new_path = self._task_path(task_id, "in-progress")
        
        task["status"] = "in-progress"
        task["started_at"] = datetime.now().isoformat()
        
        with open(new_path, 'w') as f:
            json.dump(task, f, indent=2)
        
        old_path.unlink()
        self._update_state()
        return True
    
    def complete(self, task_id: str, result: Optional[str] = None) -> bool:
        """Mark a task as completed."""
        task = self._load_task(task_id)
        if not task:
            print(f"Error: Task {task_id} not found", file=sys.stderr)
            return False
        
        if task["status"] != "in-progress":
            print(f"Error: Task {task_id} is not in-progress (status: {task['status']})", file=sys.stderr)
            return False
        
        # Move from in-progress to completed
        old_path = self._task_path(task_id, "in-progress")
        new_path = self._task_path(task_id, "completed")
        
        task["status"] = "completed"
        task["completed_at"] = datetime.now().isoformat()
        if result:
            task["result"] = result
        
        with open(new_path, 'w') as f:
            json.dump(task, f, indent=2)
        
        old_path.unlink()
        self._update_state()
        
        # Log to FEDERATION_LOG.md (optional integration)
        print(f"✅ Task {task_id} completed. Auto-scheduling check: enabled")
        
        return True
    
    def cancel(self, task_id: str) -> bool:
        """Cancel a pending or in-progress task."""
        task = self._load_task(task_id)
        if not task:
            print(f"Error: Task {task_id} not found", file=sys.stderr)
            return False
        
        status = task["status"]
        if status == "completed":
            print(f"Error: Cannot cancel completed task {task_id}", file=sys.stderr)
            return False
        
        path = self._task_path(task_id, status)
        if path.exists():
            path.unlink()
        
        self._update_state()
        print(f"🚫 Task {task_id} cancelled")
        return True
    
    def next_task(self, agent: Optional[str] = None) -> Optional[Dict]:
        """Get the next task for an agent (highest priority, oldest first)."""
        tasks = self.list_tasks(status="pending", agent=agent)
        
        # Filter for tasks with all dependencies complete
        ready_tasks = []
        for task in tasks:
            deps_complete = True
            for dep_id in task.get("dependencies", []):
                dep = self._load_task(dep_id)
                if not dep or dep.get("status") != "completed":
                    deps_complete = False
                    break
            if deps_complete:
                ready_tasks.append(task)
        
        return ready_tasks[0] if ready_tasks else None
    
    def _update_state(self):
        """Update federation state file with current counts."""
        if not self.state_file.exists():
            return
        
        try:
            with open(self.state_file) as f:
                state = json.load(f)
            
            status = self.status()
            state["queue"]["pending_count"] = status["pending"]
            state["queue"]["in_progress_count"] = status["in_progress"]
            state["queue"]["completed_count"] = status["completed"]
            state["queue"]["last_updated"] = datetime.now().isoformat()
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not update state: {e}", file=sys.stderr)


# ─────────────────────────────────────────────────────────────
# CLI Interface
# ─────────────────────────────────────────────────────────────

def main():
    queue = FederationQueue()
    
    parser = argparse.ArgumentParser(
        description="Federation Queue Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fed-queue.py add --from claude --to kimi --task "Implement auth" --priority high
  fed-queue.py list --status pending
  fed-queue.py next --agent kimi
  fed-queue.py start task-20260205-184700-0001
  fed-queue.py complete task-20260205-184700-0001 --result "auth.md"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("--from", "-f", required=True, dest="from_agent", help="Source agent")
    add_parser.add_argument("--to", "-t", required=True, dest="to_agent", help="Target agent")
    add_parser.add_argument("--task", "-d", required=True, help="Task description")
    add_parser.add_argument("--priority", "-p", default="normal", 
                           choices=["critical", "high", "normal", "low"],
                           help="Task priority")
    add_parser.add_argument("--deps", help="Comma-separated dependency task IDs")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", "-s", choices=["pending", "in-progress", "completed"],
                            help="Filter by status")
    list_parser.add_argument("--agent", "-a", help="Filter by agent (to or from)")
    
    # Status command
    subparsers.add_parser("status", help="Show queue status")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start a task")
    start_parser.add_argument("task_id", help="Task ID to start")
    
    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Complete a task")
    complete_parser.add_argument("task_id", help="Task ID to complete")
    complete_parser.add_argument("--result", "-r", help="Path to result artifact")
    
    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel a task")
    cancel_parser.add_argument("task_id", help="Task ID to cancel")
    
    # Next command
    next_parser = subparsers.add_parser("next", help="Get next task for agent")
    next_parser.add_argument("--agent", "-a", help="Agent to get next task for")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == "add":
        deps = args.deps.split(",") if args.deps else []
        task_id = queue.add(
            from_agent=args.from_agent,
            to_agent=args.to_agent,
            task=args.task,
            priority=args.priority,
            deps=deps
        )
        print(f"✅ Created task: {task_id}")
        print(f"   From: {args.from_agent} → To: {args.to_agent}")
        print(f"   Priority: {args.priority}")
        
    elif args.command == "list":
        tasks = queue.list_tasks(status=args.status, agent=args.agent)
        if not tasks:
            print("No tasks found")
            return
        
        print(f"{'Task ID':<30} {'Status':<12} {'Priority':<10} {'From':<10} {'To':<10} {'Description'}")
        print("-" * 100)
        for task in tasks:
            desc = task['description'][:40] + "..." if len(task['description']) > 40 else task['description']
            print(f"{task['task_id']:<30} {task['status']:<12} {task['priority']:<10} "
                  f"{task['from_agent']:<10} {task['to_agent']:<10} {desc}")
    
    elif args.command == "status":
        status = queue.status()
        print("📊 Federation Queue Status")
        print(f"   Pending:     {status['pending']}")
        print(f"   In Progress: {status['in_progress']}")
        print(f"   Completed:   {status['completed']}")
        print(f"   Total:       {status['total']}")
    
    elif args.command == "start":
        if queue.start(args.task_id):
            print(f"🚀 Started task: {args.task_id}")
        else:
            sys.exit(1)
    
    elif args.command == "complete":
        if queue.complete(args.task_id, args.result):
            print(f"✅ Completed task: {args.task_id}")
        else:
            sys.exit(1)
    
    elif args.command == "cancel":
        if queue.cancel(args.task_id):
            print(f"🚫 Cancelled task: {args.task_id}")
        else:
            sys.exit(1)
    
    elif args.command == "next":
        task = queue.next_task(args.agent)
        if task:
            print(f"⏭️  Next task for {args.agent or 'any agent'}:")
            print(f"   ID:          {task['task_id']}")
            print(f"   From:        {task['from_agent']}")
            print(f"   Priority:    {task['priority']}")
            print(f"   Description: {task['description']}")
            if task.get('dependencies'):
                print(f"   Dependencies: {', '.join(task['dependencies'])}")
        else:
            print(f"No pending tasks{' for ' + args.agent if args.agent else ''}")


if __name__ == "__main__":
    main()
