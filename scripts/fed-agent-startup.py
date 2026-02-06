#!/usr/bin/env python3
"""
Federation Agent Startup Script
Checks for queued tasks and auto-scheduled work on agent startup.

Usage:
    fed-agent-startup.py --agent <agent-name> [--auto-start]

Add to agent startup routine in AGENT.md or SOUL.md
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Configuration
QUEUE_SCRIPT = Path(__file__).parent / "fed-queue.py"
AUTO_SCHEDULE_SCRIPT = Path(__file__).parent / "fed-auto-schedule.py"


def check_queued_tasks(agent: str) -> list:
    """Check for pending tasks queued for this agent."""
    result = subprocess.run(
        ["python3", str(QUEUE_SCRIPT), "list", "--status", "pending", "--agent", agent],
        capture_output=True,
        text=True,
        cwd=QUEUE_SCRIPT.parent.parent
    )
    
    if result.returncode != 0:
        print(f"Warning: Could not check queue: {result.stderr}", file=sys.stderr)
        return []
    
    # Parse tasks from output
    tasks = []
    lines = result.stdout.strip().split('\n')
    
    # Skip header lines (first 2)
    for line in lines[2:]:
        if line.startswith('task-'):
            parts = line.split()
            if len(parts) >= 6:
                tasks.append({
                    "task_id": parts[0],
                    "status": parts[1],
                    "priority": parts[2],
                    "from_agent": parts[3],
                    "to_agent": parts[4],
                    "description": ' '.join(parts[5:])
                })
    
    return tasks


def get_next_ready_task(agent: str) -> dict:
    """Get the next task that's ready to start (dependencies met)."""
    result = subprocess.run(
        ["python3", str(QUEUE_SCRIPT), "next", "--agent", agent],
        capture_output=True,
        text=True,
        cwd=QUEUE_SCRIPT.parent.parent
    )
    
    if result.returncode != 0 or "No pending tasks" in result.stdout:
        return None
    
    # Parse output - it's a multi-line format
    lines = result.stdout.strip().split('\n')
    task = {}
    for line in lines:
        if line.startswith('   ID:'):
            task['task_id'] = line.split(':')[1].strip()
        elif line.startswith('   From:'):
            task['from_agent'] = line.split(':')[1].strip()
        elif line.startswith('   Priority:'):
            task['priority'] = line.split(':')[1].strip()
        elif line.startswith('   Description:'):
            task['description'] = line.split(':')[1].strip()
    
    return task if task.get('task_id') else None


def startup_sequence(agent: str, auto_start: bool = False):
    """Run full agent startup sequence."""
    
    print(f"🚀 Federation Agent Startup: {agent}")
    print("-" * 60)
    
    # 1. Check auto-scheduling status
    result = subprocess.run(
        ["python3", str(AUTO_SCHEDULE_SCRIPT), "status"],
        capture_output=True,
        text=True,
        cwd=QUEUE_SCRIPT.parent.parent
    )
    
    if "Enabled: ✅" in result.stdout:
        print("📋 Auto-scheduling: Enabled")
    else:
        print("📋 Auto-scheduling: Disabled")
    
    # 2. Check for queued tasks
    tasks = check_queued_tasks(agent)
    
    if not tasks:
        print(f"\n📭 No pending tasks for {agent}")
        print("   Ready for new assignments from Reuben.")
        return
    
    print(f"\n📥 {len(tasks)} task(s) in queue for {agent}:")
    print()
    
    for i, task in enumerate(tasks, 1):
        status_icon = "🔄" if task['status'] == 'pending' else "▶️"
        print(f"{i}. {status_icon} {task['task_id']}")
        print(f"   From: {task['from_agent']}")
        print(f"   Priority: {task['priority'].upper()}")
        print(f"   Description: {task['description'][:60]}...")
        print()
    
    # 3. Check for next ready task
    print("-" * 60)
    next_task = get_next_ready_task(agent)
    
    if next_task:
        print(f"⏭️  NEXT TASK (dependencies met):")
        print(f"   ID: {next_task['task_id']}")
        print(f"   From: {next_task['from_agent']}")
        print(f"   Description: {next_task['description'][:60]}...")
        
        if auto_start:
            print(f"\n🚀 Auto-starting task...")
            result = subprocess.run(
                ["python3", str(QUEUE_SCRIPT), "start", next_task['task_id']],
                capture_output=True,
                text=True,
                cwd=QUEUE_SCRIPT.parent.parent
            )
            if result.returncode == 0:
                print(f"✅ Task {next_task['task_id']} started!")
            else:
                print(f"❌ Error starting task: {result.stderr}", file=sys.stderr)
        else:
            print(f"\n💡 To start: fed-queue.py start {next_task['task_id']}")
    else:
        print("⏳ Tasks exist but have unmet dependencies.")
        print("   Waiting for prerequisite tasks to complete.")
    
    print("-" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Federation Agent Startup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fed-agent-startup.py --agent kimi
  fed-agent-startup.py --agent claude --auto-start
        """
    )
    
    parser.add_argument("--agent", "-a", required=True, help="Agent name (kimi, claude, copilot, ollama)")
    parser.add_argument("--auto-start", action="store_true", help="Auto-start next ready task")
    
    args = parser.parse_args()
    
    startup_sequence(args.agent, args.auto_start)


if __name__ == "__main__":
    main()
