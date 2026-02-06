#!/usr/bin/env python3
"""
Historical Learner for Predictive Routing
Learns from past task completions to improve routing accuracy.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .similarity_engine import SimilarityEngine


class HistoricalLearner:
    """Learns from historical task data to improve routing."""
    
    def __init__(
        self,
        queue_dir: str = ".federation/queue",
        predictor_data_dir: str = ".federation/predictor/data"
    ):
        self.queue_dir = Path(queue_dir)
        self.data_dir = Path(predictor_data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.engine = SimilarityEngine(str(predictor_data_dir))
        self.learning_log: List[Dict] = []
        self._load_learning_log()
    
    def _load_learning_log(self) -> None:
        """Load learning log from disk."""
        log_file = self.data_dir / "learning_log.json"
        if log_file.exists():
            with open(log_file) as f:
                self.learning_log = json.load(f)
    
    def _save_learning_log(self) -> None:
        """Save learning log to disk."""
        log_file = self.data_dir / "learning_log.json"
        with open(log_file, "w") as f:
            json.dump(self.learning_log, f, indent=2)
    
    def scan_completed_tasks(self) -> List[Dict]:
        """Scan completed tasks from queue directory."""
        completed_dir = self.queue_dir / "completed"
        if not completed_dir.exists():
            return []
        
        tasks = []
        for task_file in completed_dir.glob("*.json"):
            try:
                with open(task_file) as f:
                    task = json.load(f)
                    task["_source_file"] = str(task_file)
                    tasks.append(task)
            except (json.JSONDecodeError, IOError):
                continue
        
        return tasks
    
    def extract_learning_data(self, task: Dict) -> Optional[Dict]:
        """Extract learning data from a completed task."""
        # Skip tasks without completion data
        if task.get("status") != "completed":
            return None
        
        assigned_to = task.get("assigned_to", "")
        completed_by = task.get("completed_by", assigned_to)
        
        if not completed_by:
            return None
        
        # Calculate duration if timestamps available
        duration = self._calculate_duration(task)
        
        # Determine success (assume success if completed)
        # In future, could use explicit success/failure flag
        success = True
        
        return {
            "task_id": task.get("id", "unknown"),
            "description": task.get("description", ""),
            "completed_by": completed_by,
            "success": success,
            "duration_minutes": duration,
            "timestamp": task.get("completed_at", datetime.now().isoformat()),
            "task_type": task.get("type", "general"),
            "priority": task.get("priority", "normal")
        }
    
    def _calculate_duration(self, task: Dict) -> float:
        """Calculate task duration in minutes."""
        created = task.get("created_at", "")
        completed = task.get("completed_at", "")
        started = task.get("started_at", "")
        
        if not completed:
            return 30.0  # Default duration
        
        try:
            # Use started time if available, otherwise created
            start_time = started or created
            if not start_time:
                return 30.0
            
            start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            end = datetime.fromisoformat(completed.replace("Z", "+00:00"))
            
            duration = (end - start).total_seconds() / 60.0
            return max(duration, 1.0)  # Minimum 1 minute
        except (ValueError, TypeError):
            return 30.0  # Default on error
    
    def learn_from_task(self, learning_data: Dict) -> bool:
        """Learn from a single task completion."""
        agent_id = learning_data["completed_by"]
        description = learning_data["description"]
        success = learning_data["success"]
        duration = learning_data["duration_minutes"]
        
        # Update agent profile
        self.engine.update_profile_from_completion(
            agent_id, description, success, duration
        )
        
        # Log learning event
        learning_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": learning_data["task_id"],
            "agent_id": agent_id,
            "success": success,
            "duration": duration,
            "learned": True
        }
        self.learning_log.append(learning_entry)
        
        return True
    
    def learn_from_all_completed(self) -> Dict:
        """Learn from all completed tasks."""
        tasks = self.scan_completed_tasks()
        
        learned_count = 0
        skipped_count = 0
        errors = []
        
        for task in tasks:
            # Check if already learned
            task_id = task.get("id", "")
            if any(log.get("task_id") == task_id for log in self.learning_log):
                skipped_count += 1
                continue
            
            learning_data = self.extract_learning_data(task)
            if not learning_data:
                skipped_count += 1
                continue
            
            try:
                if self.learn_from_task(learning_data):
                    learned_count += 1
            except Exception as e:
                errors.append(f"{task_id}: {str(e)}")
        
        self._save_learning_log()
        
        return {
            "total_tasks": len(tasks),
            "learned": learned_count,
            "skipped": skipped_count,
            "errors": errors,
            "total_learning_events": len(self.learning_log)
        }
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about learning progress."""
        if not self.learning_log:
            return {"status": "no_data"}
        
        # Calculate success rate trend
        recent_events = self.learning_log[-50:]  # Last 50 events
        success_rate = sum(1 for e in recent_events if e.get("success")) / len(recent_events)
        
        # Calculate average duration
        durations = [e.get("duration", 0) for e in self.learning_log if e.get("duration")]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Count by agent
        agent_counts = {}
        for event in self.learning_log:
            agent = event.get("agent_id", "unknown")
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
        
        return {
            "status": "active",
            "total_learning_events": len(self.learning_log),
            "recent_success_rate": round(success_rate, 2),
            "avg_task_duration": round(avg_duration, 1),
            "learning_by_agent": agent_counts,
            "first_learning": self.learning_log[0].get("timestamp") if self.learning_log else None,
            "last_learning": self.learning_log[-1].get("timestamp") if self.learning_log else None
        }
    
    def predict_success_probability(
        self,
        agent_id: str,
        task_description: str
    ) -> float:
        """Predict probability of success for agent-task pair."""
        profile = self.engine.get_profile(agent_id)
        if not profile:
            return 0.5  # Unknown agent
        
        # Get base success rate
        base_rate = profile.success_rate
        
        # Check for similar past tasks
        similar_tasks = self._find_similar_past_tasks(agent_id, task_description)
        
        if similar_tasks:
            # Weight recent similar tasks more heavily
            recent_success = sum(1 for t in similar_tasks if t.get("success")) / len(similar_tasks)
            # Blend base rate with recent similar task success
            return 0.6 * base_rate + 0.4 * recent_success
        
        return base_rate
    
    def _find_similar_past_tasks(
        self,
        agent_id: str,
        task_description: str,
        n: int = 5
    ) -> List[Dict]:
        """Find similar past tasks completed by agent."""
        agent_events = [
            e for e in self.learning_log
            if e.get("agent_id") == agent_id
        ]
        
        # Get corresponding task data
        tasks = []
        for event in agent_events:
            task_data = self._get_task_data(event.get("task_id", ""))
            if task_data:
                tasks.append({**event, **task_data})
        
        # Sort by recency (most recent first)
        tasks.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return tasks[:n]
    
    def _get_task_data(self, task_id: str) -> Optional[Dict]:
        """Get task data from queue."""
        for status in ["completed", "in-progress", "pending"]:
            task_file = self.queue_dir / status / f"{task_id}.json"
            if task_file.exists():
                try:
                    with open(task_file) as f:
                        return json.load(f)
                except (json.JSONDecodeError, IOError):
                    continue
        return None
    
    def reset_learning(self) -> None:
        """Reset all learning data (use with caution)."""
        self.learning_log = []
        self._save_learning_log()
        
        # Reset profiles to defaults
        self.engine = SimilarityEngine(str(self.data_dir))
        
        print("Learning data reset. Profiles reinitialized.")


# Simple test
if __name__ == "__main__":
    learner = HistoricalLearner()
    
    # Learn from completed tasks
    result = learner.learn_from_all_completed()
    print(f"Learning result: {result}")
    
    # Get stats
    stats = learner.get_learning_stats()
    print(f"\nLearning stats: {stats}")
