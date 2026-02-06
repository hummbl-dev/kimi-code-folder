#!/usr/bin/env python3
"""
Federation Auto-Scheduling System
Enables agents to automatically queue follow-up tasks for other agents.

Usage:
    fed-auto-schedule.py enable          # Enable auto-scheduling
    fed-auto-schedule.py disable         # Disable auto-scheduling
    fed-auto-schedule.py status          # Check auto-scheduling status
    fed-auto-schedule.py on-complete     # Triggered on task completion
    fed-auto-schedule.py check-startup   # Check for queued tasks on agent startup
    fed-auto-schedule.py trigger-rules   # List all auto-schedule rules

This is Phase 4 Sprint 2: Autonomous Task Scheduling
"""

import argparse
import json
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

FEDERATION_DIR = Path(__file__).parent.parent / ".federation"
STATE_FILE = FEDERATION_DIR / "state" / "federation-state.json"
RULES_FILE = FEDERATION_DIR / "state" / "auto-schedule-rules.json"
QUEUE_SCRIPT = Path(__file__).parent / "fed-queue.py"

# ─────────────────────────────────────────────────────────────
# Auto-Schedule Rules
# ─────────────────────────────────────────────────────────────

DEFAULT_RULES = {
    "version": "1.0",
    "enabled": False,
    "rules": [
        {
            "id": "research-to-implementation",
            "name": "Research → Implementation",
            "trigger": {
                "from_agent": "claude",
                "task_patterns": ["research", "analyze", "architecture", "design"],
                "output_artifact": True
            },
            "action": {
                "queue_for": "kimi",
                "task_template": "Implement {previous_task} from {artifact_path}",
                "priority": "high",
                "auto_start": False
            },
            "enabled": True
        },
        {
            "id": "implementation-to-testing",
            "name": "Implementation → Testing",
            "trigger": {
                "from_agent": "kimi",
                "task_patterns": ["implement", "build", "create", "refactor"],
                "output_artifact": True
            },
            "action": {
                "queue_for": "copilot",
                "task_template": "Review and test {previous_task}",
                "priority": "normal",
                "auto_start": False
            },
            "enabled": True
        },
        {
            "id": "design-to-execution",
            "name": "Design → Execution",
            "trigger": {
                "from_agent": "copilot",
                "task_patterns": ["design", "plan", "structure"],
                "output_artifact": True
            },
            "action": {
                "queue_for": "claude",
                "task_template": "Research and document approach for {previous_task}",
                "priority": "normal",
                "auto_start": False
            },
            "enabled": True
        },
        {
            "id": "draft-to-polish",
            "name": "Draft → Polish",
            "trigger": {
                "from_agent": "ollama",
                "task_patterns": ["draft", "sketch", "prototype"],
                "output_artifact": True
            },
            "action": {
                "queue_for": "kimi",
                "task_template": "Polish and productionize {previous_task}",
                "priority": "low",
                "auto_start": False
            },
            "enabled": False  # Disabled by default - Ollama tasks may stay draft
        }
    ],
    "global_settings": {
        "require_confirmation": True,  # If True, queue but don't auto-start
        "log_to_federation": True,
        "max_auto_queue_depth": 5,  # Prevent infinite loops
        "notification_on_queue": True
    }
}

# ─────────────────────────────────────────────────────────────
# Core Auto-Scheduler
# ─────────────────────────────────────────────────────────────

class AutoScheduler:
    """Manages automatic task scheduling between federation agents."""
    
    def __init__(self):
        self.rules_file = RULES_FILE
        self.state_file = STATE_FILE
        self._ensure_rules_exist()
    
    def _ensure_rules_exist(self):
        """Initialize rules file if it doesn't exist."""
        if not self.rules_file.exists():
            self.rules_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.rules_file, 'w') as f:
                json.dump(DEFAULT_RULES, f, indent=2)
    
    def _load_rules(self) -> Dict:
        """Load auto-schedule rules."""
        with open(self.rules_file) as f:
            return json.load(f)
    
    def _save_rules(self, rules: Dict):
        """Save auto-schedule rules."""
        with open(self.rules_file, 'w') as f:
            json.dump(rules, f, indent=2)
    
    def is_enabled(self) -> bool:
        """Check if auto-scheduling is enabled."""
        rules = self._load_rules()
        return rules.get("enabled", False)
    
    def enable(self):
        """Enable auto-scheduling."""
        rules = self._load_rules()
        rules["enabled"] = True
        self._save_rules(rules)
        print("✅ Auto-scheduling enabled")
        print("   Rules active: {}".format(sum(1 for r in rules["rules"] if r.get("enabled"))))
    
    def disable(self):
        """Disable auto-scheduling."""
        rules = self._load_rules()
        rules["enabled"] = False
        self._save_rules(rules)
        print("🚫 Auto-scheduling disabled")
    
    def status(self):
        """Show auto-scheduling status."""
        rules = self._load_rules()
        
        print("📊 Auto-Scheduling Status")
        print(f"   Enabled: {'✅ Yes' if rules.get('enabled') else '🚫 No'}")
        print(f"   Version: {rules.get('version', 'unknown')}")
        print(f"   Active rules: {sum(1 for r in rules['rules'] if r.get('enabled'))}/{len(rules['rules'])}")
        print(f"   Settings:")
        settings = rules.get('global_settings', {})
        for key, value in settings.items():
            print(f"      {key}: {value}")
    
    def list_rules(self):
        """List all auto-schedule rules."""
        rules = self._load_rules()
        
        print("📋 Auto-Schedule Rules")
        print("-" * 80)
        for rule in rules["rules"]:
            status = "✅" if rule.get("enabled") else "🚫"
            print(f"{status} {rule['id']}")
            print(f"   Name: {rule['name']}")
            print(f"   Trigger: {rule['trigger']['from_agent']} completes [{', '.join(rule['trigger']['task_patterns'])}]")
            print(f"   Action: Queue for {rule['action']['queue_for']}")
            print(f"   Template: {rule['action']['task_template']}")
            print()
    
    def check_startup(self, agent: str) -> List[Dict]:
        """Check for tasks queued for this agent on startup."""
        # Query queue for pending tasks for this agent
        result = subprocess.run(
            ["python3", str(QUEUE_SCRIPT), "list", "--status", "pending", "--agent", agent],
            capture_output=True,
            text=True,
            cwd=QUEUE_SCRIPT.parent.parent
        )
        
        if result.returncode != 0:
            print(f"Warning: Could not check queue: {result.stderr}", file=sys.stderr)
            return []
        
        # Parse output (simple text parsing)
        tasks = []
        for line in result.stdout.strip().split('\n')[2:]:  # Skip header lines
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
    
    def on_complete(self, task_id: str, completed_by: str, artifact_path: Optional[str] = None) -> Optional[str]:
        """
        Triggered when a task is completed. Checks if auto-scheduling should queue a follow-up.
        
        Returns:
            New task ID if auto-queued, None otherwise
        """
        rules = self._load_rules()
        
        if not rules.get("enabled", False):
            return None
        
        # Get completed task details
        task = self._get_task_details(task_id)
        if not task:
            print(f"Warning: Could not find task {task_id}", file=sys.stderr)
            return None
        
        # Check rules for matches
        for rule in rules["rules"]:
            if not rule.get("enabled", False):
                continue
            
            if self._rule_matches(rule, task, completed_by):
                new_task_id = self._execute_rule(rule, task, artifact_path)
                if new_task_id:
                    self._log_auto_schedule(task, rule, new_task_id)
                    return new_task_id
        
        return None
    
    def _get_task_details(self, task_id: str) -> Optional[Dict]:
        """Get task details from queue files."""
        for status in ["completed", "in-progress", "pending"]:
            task_file = FEDERATION_DIR / "queue" / status / f"{task_id}.json"
            if task_file.exists():
                with open(task_file) as f:
                    return json.load(f)
        return None
    
    def _rule_matches(self, rule: Dict, task: Dict, completed_by: str) -> bool:
        """Check if a rule matches the completed task."""
        trigger = rule["trigger"]
        
        # Check from_agent matches
        if trigger.get("from_agent") != completed_by:
            return False
        
        # Check task pattern matches
        task_desc = task.get("description", "").lower()
        patterns = trigger.get("task_patterns", [])
        if not any(pattern.lower() in task_desc for pattern in patterns):
            return False
        
        # Check output artifact requirement
        if trigger.get("output_artifact", False):
            # Task should have a result or artifact path
            if not task.get("result") and not task.get("artifact_path"):
                return False
        
        return True
    
    def _execute_rule(self, rule: Dict, completed_task: Dict, artifact_path: Optional[str]) -> Optional[str]:
        """Execute an auto-schedule rule."""
        action = rule["action"]
        
        # Build task description from template
        template = action["task_template"]
        previous_task = completed_task.get("description", "previous work")
        artifact = artifact_path or completed_task.get("result", "")
        
        task_desc = template.format(
            previous_task=previous_task,
            artifact_path=artifact
        )
        
        # Queue the new task
        result = subprocess.run(
            [
                "python3", str(QUEUE_SCRIPT), "add",
                "--from", completed_task.get("to_agent", "unknown"),  # The agent that completed
                "--to", action["queue_for"],
                "--task", task_desc,
                "--priority", action.get("priority", "normal"),
                "--deps", completed_task["task_id"]  # Depend on completed task
            ],
            capture_output=True,
            text=True,
            cwd=QUEUE_SCRIPT.parent.parent
        )
        
        if result.returncode == 0:
            # Parse task ID from output
            output = result.stdout.strip()
            if "Created task:" in output:
                task_id = output.split(": ")[-1]
                print(f"🔄 Auto-scheduled: {task_id}")
                print(f"   For: {action['queue_for']}")
                print(f"   Task: {task_desc[:60]}...")
                return task_id
        else:
            print(f"Error auto-scheduling: {result.stderr}", file=sys.stderr)
        
        return None
    
    def _log_auto_schedule(self, completed_task: Dict, rule: Dict, new_task_id: str):
        """Log auto-scheduling event to FEDERATION_LOG.md."""
        # This is a simplified version - full implementation would append to log
        print(f"   Rule: {rule['id']}")
        print(f"   Dependency: {completed_task['task_id']} → {new_task_id}")
        
        # TODO: Append to FEDERATION_LOG.md with proper formatting
        # For now, we print to stdout for visibility


# ─────────────────────────────────────────────────────────────
# CLI Interface
# ─────────────────────────────────────────────────────────────

def main():
    scheduler = AutoScheduler()
    
    parser = argparse.ArgumentParser(
        description="Federation Auto-Scheduling System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fed-auto-schedule.py enable
  fed-auto-schedule.py status
  fed-auto-schedule.py check-startup --agent kimi
  fed-auto-schedule.py on-complete task-20260205-0001 --by claude --artifact docs/design.md
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Enable
    subparsers.add_parser("enable", help="Enable auto-scheduling")
    
    # Disable
    subparsers.add_parser("disable", help="Disable auto-scheduling")
    
    # Status
    subparsers.add_parser("status", help="Show auto-scheduling status")
    
    # List rules
    subparsers.add_parser("trigger-rules", help="List auto-schedule rules")
    
    # Check startup
    startup_parser = subparsers.add_parser("check-startup", help="Check for queued tasks on startup")
    startup_parser.add_argument("--agent", "-a", required=True, help="Agent to check for")
    
    # On complete
    complete_parser = subparsers.add_parser("on-complete", help="Trigger auto-schedule on task completion")
    complete_parser.add_argument("task_id", help="Completed task ID")
    complete_parser.add_argument("--by", "-b", required=True, help="Agent that completed the task")
    complete_parser.add_argument("--artifact", help="Path to output artifact")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == "enable":
        scheduler.enable()
    
    elif args.command == "disable":
        scheduler.disable()
    
    elif args.command == "status":
        scheduler.status()
    
    elif args.command == "trigger-rules":
        scheduler.list_rules()
    
    elif args.command == "check-startup":
        tasks = scheduler.check_startup(args.agent)
        if tasks:
            print(f"📥 {len(tasks)} task(s) queued for {args.agent}:")
            for task in tasks:
                print(f"   - {task['task_id']}: {task['description'][:50]}...")
        else:
            print(f"No pending tasks for {args.agent}")
    
    elif args.command == "on-complete":
        new_task = scheduler.on_complete(args.task_id, args.by, args.artifact)
        if new_task:
            print(f"✅ Auto-scheduled follow-up: {new_task}")
        else:
            print("ℹ️  No auto-schedule rule matched")


if __name__ == "__main__":
    main()
