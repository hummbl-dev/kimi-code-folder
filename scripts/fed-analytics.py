#!/usr/bin/env python3
"""
Federation Analytics & Optimization System
Phase 4 Sprint 4: Performance Tracking and Routing Optimization

Usage:
    fed-analytics.py dashboard              # Show federation dashboard
    fed-analytics.py agent <name>           # Show agent metrics
    fed-analytics.py task-type <type>       # Show task type performance
    fed-analytics.py optimize               # Apply routing optimizations
    fed-analytics.py record --agent <name> --task <type> --success <bool> --duration <min>
    fed-analytics.py export                 # Export metrics to JSON

Examples:
    fed-analytics.py dashboard
    fed-analytics.py agent kimi
    fed-analytics.py optimize --dry-run     # Preview changes
    fed-analytics.py record --agent kimi --task implementation --success true --duration 25
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
FEDERATION_DIR = SCRIPT_DIR.parent / ".federation"
METRICS_FILE = FEDERATION_DIR / "state" / "metrics.json"
ROUTING_CONFIG = SCRIPT_DIR.parent / "configs" / "federation-routing.json"

# Optimization thresholds
HIGH_PERFORMER_THRESHOLD = 0.90
LOW_PERFORMER_THRESHOLD = 0.50
MIN_SAMPLES = 5
BOOST_AMOUNT = 0.05
PENALTY_AMOUNT = -0.05


# ─────────────────────────────────────────────────────────────
# Analytics System
# ─────────────────────────────────────────────────────────────

class AnalyticsSystem:
    """Tracks and optimizes federation performance."""
    
    def __init__(self):
        self.metrics = self._load_metrics()
        self.routing_config = self._load_routing_config()
    
    def _load_metrics(self) -> Dict:
        """Load metrics from file or create default."""
        if METRICS_FILE.exists():
            with open(METRICS_FILE) as f:
                return json.load(f)
        return self._create_default_metrics()
    
    def _create_default_metrics(self) -> Dict:
        """Create default metrics structure."""
        return {
            "version": "1.0",
            "initialized": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "agents": {},
            "task_types": {},
            "routing_performance": {},
            "optimization_history": []
        }
    
    def _load_routing_config(self) -> Dict:
        """Load current routing configuration."""
        if ROUTING_CONFIG.exists():
            with open(ROUTING_CONFIG) as f:
                return json.load(f)
        return {}
    
    def _save_metrics(self):
        """Save metrics to file."""
        METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.metrics["last_updated"] = datetime.now().isoformat()
        with open(METRICS_FILE, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def record_task(self, agent: str, task_type: str, success: bool, 
                    duration_min: Optional[int] = None, 
                    rework_required: bool = False,
                    notes: Optional[str] = None):
        """Record a task completion for analytics."""
        timestamp = datetime.now().isoformat()
        
        # Initialize agent metrics if not exists
        if agent not in self.metrics["agents"]:
            self.metrics["agents"][agent] = {
                "total_tasks": 0,
                "successful_tasks": 0,
                "failed_tasks": 0,
                "total_duration_min": 0,
                "avg_duration_min": 0,
                "rework_count": 0,
                "success_rate": 0.0,
                "task_types": {}
            }
        
        agent_metrics = self.metrics["agents"][agent]
        agent_metrics["total_tasks"] += 1
        
        if success:
            agent_metrics["successful_tasks"] += 1
        else:
            agent_metrics["failed_tasks"] += 1
        
        if duration_min:
            agent_metrics["total_duration_min"] += duration_min
            agent_metrics["avg_duration_min"] = (
                agent_metrics["total_duration_min"] / agent_metrics["total_tasks"]
            )
        
        if rework_required:
            agent_metrics["rework_count"] += 1
        
        # Update success rate
        agent_metrics["success_rate"] = (
            agent_metrics["successful_tasks"] / agent_metrics["total_tasks"]
        )
        
        # Track by task type
        if task_type not in agent_metrics["task_types"]:
            agent_metrics["task_types"][task_type] = {
                "count": 0,
                "successes": 0,
                "failures": 0,
                "total_duration": 0,
                "success_rate": 0.0
            }
        
        task_metrics = agent_metrics["task_types"][task_type]
        task_metrics["count"] += 1
        if success:
            task_metrics["successes"] += 1
        else:
            task_metrics["failures"] += 1
        if duration_min:
            task_metrics["total_duration"] += duration_min
        task_metrics["success_rate"] = (
            task_metrics["successes"] / task_metrics["count"]
        )
        
        # Track task type globally
        if task_type not in self.metrics["task_types"]:
            self.metrics["task_types"][task_type] = {
                "total_count": 0,
                "agent_breakdown": {}
            }
        
        self.metrics["task_types"][task_type]["total_count"] += 1
        
        # Record individual task
        task_record = {
            "timestamp": timestamp,
            "agent": agent,
            "task_type": task_type,
            "success": success,
            "duration_min": duration_min,
            "rework_required": rework_required,
            "notes": notes
        }
        
        if "recent_tasks" not in self.metrics:
            self.metrics["recent_tasks"] = []
        
        self.metrics["recent_tasks"].insert(0, task_record)
        # Keep only last 100 tasks
        self.metrics["recent_tasks"] = self.metrics["recent_tasks"][:100]
        
        self._save_metrics()
        return task_record
    
    def get_dashboard(self) -> Dict:
        """Get federation-wide dashboard metrics."""
        total_tasks = sum(
            a["total_tasks"] for a in self.metrics["agents"].values()
        )
        
        if total_tasks == 0:
            return {
                "status": "no_data",
                "message": "No tasks recorded yet. Use 'record' command to log tasks."
            }
        
        total_success = sum(
            a["successful_tasks"] for a in self.metrics["agents"].values()
        )
        
        # Calculate overall success rate
        overall_success_rate = total_success / total_tasks if total_tasks > 0 else 0
        
        # Agent rankings
        agent_rankings = []
        for agent, data in self.metrics["agents"].items():
            if data["total_tasks"] >= MIN_SAMPLES:
                agent_rankings.append({
                    "agent": agent,
                    "success_rate": data["success_rate"],
                    "total_tasks": data["total_tasks"],
                    "avg_duration": data.get("avg_duration_min", 0),
                    "rework_rate": data["rework_count"] / data["total_tasks"]
                })
        
        agent_rankings.sort(key=lambda x: x["success_rate"], reverse=True)
        
        # Task type breakdown
        task_breakdown = []
        for task_type, data in self.metrics["task_types"].items():
            task_breakdown.append({
                "task_type": task_type,
                "total_count": data["total_count"]
            })
        
        task_breakdown.sort(key=lambda x: x["total_count"], reverse=True)
        
        return {
            "status": "ok",
            "summary": {
                "total_tasks": total_tasks,
                "total_success": total_success,
                "overall_success_rate": round(overall_success_rate, 2),
                "active_agents": len(self.metrics["agents"]),
                "task_types": len(self.metrics["task_types"])
            },
            "agent_rankings": agent_rankings[:5],
            "task_breakdown": task_breakdown[:5],
            "last_updated": self.metrics["last_updated"]
        }
    
    def get_agent_metrics(self, agent: str) -> Optional[Dict]:
        """Get detailed metrics for a specific agent."""
        if agent not in self.metrics["agents"]:
            return None
        
        data = self.metrics["agents"][agent]
        
        # Calculate task type performance
        task_performance = []
        for task_type, task_data in data.get("task_types", {}).items():
            if task_data["count"] >= 3:  # Need at least 3 samples
                task_performance.append({
                    "task_type": task_type,
                    "count": task_data["count"],
                    "success_rate": task_data["success_rate"],
                    "avg_duration": task_data["total_duration"] / task_data["count"]
                      if task_data["total_duration"] > 0 else 0
                })
        
        task_performance.sort(key=lambda x: x["success_rate"], reverse=True)
        
        return {
            "agent": agent,
            "summary": {
                "total_tasks": data["total_tasks"],
                "success_rate": data["success_rate"],
                "avg_duration_min": data.get("avg_duration_min", 0),
                "rework_rate": data["rework_count"] / data["total_tasks"]
                  if data["total_tasks"] > 0 else 0,
                "optimization_boost": data.get("routing_boost", 0.0)
            },
            "task_type_performance": task_performance
        }
    
    def get_task_type_metrics(self, task_type: str) -> Optional[Dict]:
        """Get metrics for a specific task type across all agents."""
        if task_type not in self.metrics["task_types"]:
            return None
        
        # Collect performance per agent for this task type
        agent_performance = []
        for agent, data in self.metrics["agents"].items():
            if task_type in data.get("task_types", {}):
                task_data = data["task_types"][task_type]
                agent_performance.append({
                    "agent": agent,
                    "count": task_data["count"],
                    "success_rate": task_data["success_rate"],
                    "recommendation": "high" if task_data["success_rate"] >= HIGH_PERFORMER_THRESHOLD else "low" if task_data["success_rate"] <= LOW_PERFORMER_THRESHOLD else "neutral"
                })
        
        agent_performance.sort(key=lambda x: x["success_rate"], reverse=True)
        
        return {
            "task_type": task_type,
            "total_count": self.metrics["task_types"][task_type]["total_count"],
            "agent_performance": agent_performance
        }
    
    def optimize_routing(self, dry_run: bool = False) -> Dict:
        """Analyze metrics and suggest routing optimizations."""
        optimizations = []
        
        for agent, data in self.metrics["agents"].items():
            if data["total_tasks"] < MIN_SAMPLES:
                continue
            
            current_boost = data.get("routing_boost", 0)
            success_rate = data["success_rate"]
            
            # Check for high performer
            if success_rate >= HIGH_PERFORMER_THRESHOLD and current_boost < BOOST_AMOUNT:
                opt = {
                    "agent": agent,
                    "action": "boost",
                    "current_rate": success_rate,
                    "current_boost": current_boost,
                    "new_boost": BOOST_AMOUNT,
                    "reason": f"High performer: {success_rate:.0%} success rate"
                }
                optimizations.append(opt)
                
                if not dry_run:
                    self.metrics["agents"][agent]["routing_boost"] = BOOST_AMOUNT
            
            # Check for low performer
            elif success_rate <= LOW_PERFORMER_THRESHOLD and current_boost > PENALTY_AMOUNT:
                opt = {
                    "agent": agent,
                    "action": "penalty",
                    "current_rate": success_rate,
                    "current_boost": current_boost,
                    "new_boost": PENALTY_AMOUNT,
                    "reason": f"Low performer: {success_rate:.0%} success rate"
                }
                optimizations.append(opt)
                
                if not dry_run:
                    self.metrics["agents"][agent]["routing_boost"] = PENALTY_AMOUNT
        
        # Task-type specific optimizations
        for agent, data in self.metrics["agents"].items():
            for task_type, task_data in data.get("task_types", {}).items():
                if task_data["count"] < MIN_SAMPLES:
                    continue
                
                success_rate = task_data["success_rate"]
                
                if success_rate >= HIGH_PERFORMER_THRESHOLD:
                    opt = {
                        "agent": agent,
                        "task_type": task_type,
                        "action": "task_boost",
                        "success_rate": success_rate,
                        "reason": f"Excellent at {task_type}: {success_rate:.0%}"
                    }
                    optimizations.append(opt)
        
        if not dry_run and optimizations:
            self.metrics["optimization_history"].append({
                "timestamp": datetime.now().isoformat(),
                "optimizations_applied": len(optimizations),
                "details": optimizations
            })
            self._save_metrics()
        
        return {
            "dry_run": dry_run,
            "optimizations_found": len(optimizations),
            "optimizations": optimizations
        }
    
    def export_metrics(self, output_path: Optional[str] = None) -> str:
        """Export metrics to JSON file."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_path = f".federation/exports/metrics-{timestamp}.json"
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        return str(output_file)


# ─────────────────────────────────────────────────────────────
# CLI Interface
# ─────────────────────────────────────────────────────────────

def format_dashboard(data: Dict) -> str:
    """Format dashboard for display."""
    if data.get("status") == "no_data":
        return f"⚠️  {data['message']}"
    
    summary = data["summary"]
    lines = [
        "╔══════════════════════════════════════════════════════════════╗",
        "║           FEDERATION ANALYTICS DASHBOARD                     ║",
        "╚══════════════════════════════════════════════════════════════╝",
        "",
        f"📊 Summary",
        f"   Total Tasks:      {summary['total_tasks']}",
        f"   Success Rate:     {summary['overall_success_rate']:.0%}",
        f"   Active Agents:    {summary['active_agents']}",
        f"   Task Types:       {summary['task_types']}",
        "",
        f"🏆 Top Performers",
    ]
    
    for i, agent in enumerate(data["agent_rankings"][:3], 1):
        medal = ["🥇", "🥈", "🥉"][i-1]
        lines.append(f"   {medal} {agent['agent']:<12} {agent['success_rate']:.0%} ({agent['total_tasks']} tasks)")
    
    lines.extend([
        "",
        f"📋 Task Distribution",
    ])
    
    for task in data["task_breakdown"][:3]:
        lines.append(f"   • {task['task_type']:<20} {task['total_count']} tasks")
    
    lines.extend([
        "",
        f"Last Updated: {data['last_updated'][:19]}"
    ])
    
    return "\n".join(lines)


def format_agent_metrics(data: Dict) -> str:
    """Format agent metrics for display."""
    lines = [
        f"📊 Agent: {data['agent']}",
        "",
        f"Summary:",
        f"   Total Tasks:      {data['summary']['total_tasks']}",
        f"   Success Rate:     {data['summary']['success_rate']:.0%}",
        f"   Avg Duration:     {data['summary']['avg_duration_min']:.0f} min",
        f"   Rework Rate:      {data['summary']['rework_rate']:.0%}",
        f"   Routing Boost:    {data['summary']['optimization_boost']:+.2f}",
        "",
        f"Task Type Performance:",
    ]
    
    for task in data['task_type_performance'][:5]:
        emoji = "✅" if task['success_rate'] >= 0.90 else "⚠️" if task['success_rate'] >= 0.70 else "❌"
        lines.append(f"   {emoji} {task['task_type']:<20} {task['success_rate']:.0%} ({task['count']} tasks)")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Federation Analytics & Optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fed-analytics.py dashboard
  fed-analytics.py agent kimi
  fed-analytics.py optimize --dry-run
  fed-analytics.py record --agent kimi --task implementation --success true --duration 25
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Dashboard
    subparsers.add_parser('dashboard', help='Show federation dashboard')
    
    # Agent metrics
    agent_parser = subparsers.add_parser('agent', help='Show agent metrics')
    agent_parser.add_argument('agent_name', help='Agent name')
    
    # Task type metrics
    task_parser = subparsers.add_parser('task-type', help='Show task type metrics')
    task_parser.add_argument('task_type', help='Task type (e.g., implementation, research)')
    
    # Optimize
    opt_parser = subparsers.add_parser('optimize', help='Apply routing optimizations')
    opt_parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    
    # Record
    record_parser = subparsers.add_parser('record', help='Record a task completion')
    record_parser.add_argument('--agent', required=True, help='Agent name')
    record_parser.add_argument('--task', required=True, help='Task type')
    record_parser.add_argument('--success', required=True, choices=['true', 'false'],
                               help='Task succeeded?')
    record_parser.add_argument('--duration', type=int, help='Duration in minutes')
    record_parser.add_argument('--rework', action='store_true', help='Required rework')
    record_parser.add_argument('--notes', help='Additional notes')
    
    # Export
    subparsers.add_parser('export', help='Export metrics to JSON')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        analytics = AnalyticsSystem()
        
        if args.command == 'dashboard':
            data = analytics.get_dashboard()
            print(format_dashboard(data))
        
        elif args.command == 'agent':
            data = analytics.get_agent_metrics(args.agent_name)
            if data:
                print(format_agent_metrics(data))
            else:
                print(f"No metrics found for agent: {args.agent_name}")
                print("Use 'record' command to log tasks.")
        
        elif args.command == 'task-type':
            data = analytics.get_task_type_metrics(args.task_type)
            if data:
                print(f"📋 Task Type: {data['task_type']}")
                print(f"Total Tasks: {data['total_count']}")
                print("\nAgent Performance:")
                for perf in data['agent_performance']:
                    emoji = "✅" if perf['recommendation'] == 'high' else "⚠️" if perf['recommendation'] == 'neutral' else "❌"
                    print(f"   {emoji} {perf['agent']:<12} {perf['success_rate']:.0%} ({perf['count']} tasks)")
            else:
                print(f"No metrics found for task type: {args.task_type}")
        
        elif args.command == 'optimize':
            result = analytics.optimize_routing(args.dry_run)
            
            mode = "(DRY RUN)" if args.dry_run else ""
            print(f"🔧 Optimization Analysis {mode}")
            print(f"Found {result['optimizations_found']} optimizations:\n")
            
            for opt in result['optimizations']:
                if opt['action'] == 'boost':
                    print(f"✅ BOOST {opt['agent']}: {opt['reason']}")
                    print(f"   Routing boost: {opt['current_boost']:+.2f} → {opt['new_boost']:+.2f}")
                elif opt['action'] == 'penalty':
                    print(f"⚠️  PENALTY {opt['agent']}: {opt['reason']}")
                    print(f"   Routing boost: {opt['current_boost']:+.2f} → {opt['new_boost']:+.2f}")
                elif opt['action'] == 'task_boost':
                    print(f"🎯 TASK BOOST: {opt['agent']} for {opt['task_type']}")
                    print(f"   {opt['reason']}")
                print()
            
            if not args.dry_run and result['optimizations_found'] > 0:
                print(f"✅ Applied {result['optimizations_found']} optimizations")
            elif args.dry_run:
                print("Run without --dry-run to apply these optimizations")
        
        elif args.command == 'record':
            record = analytics.record_task(
                agent=args.agent,
                task_type=args.task,
                success=args.success == 'true',
                duration_min=args.duration,
                rework_required=args.rework,
                notes=args.notes
            )
            status = "✅" if record['success'] else "❌"
            print(f"{status} Recorded: {record['agent']} completed '{record['task_type']}'")
            if record['duration_min']:
                print(f"   Duration: {record['duration_min']} min")
        
        elif args.command == 'export':
            path = analytics.export_metrics()
            print(f"✅ Exported metrics to: {path}")
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
