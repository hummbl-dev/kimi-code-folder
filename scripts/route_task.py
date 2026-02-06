#!/usr/bin/env python3
"""
Federation Task Router
Routes tasks to agents based on keyword taxonomy and confidence scoring.

Usage:
    python route_task.py "task description"
    python route_task.py --json "task description"
    python route_task.py --explain "task description"
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR.parent / "configs" / "federation-routing.json"

# ─────────────────────────────────────────────────────────────
# Core Router
# ─────────────────────────────────────────────────────────────

class TaskRouter:
    def __init__(self, config_path: Path = CONFIG_PATH):
        with open(config_path) as f:
            self.config = json.load(f)
        self.agents = self.config.get("agents", {})
        self.scoring = self.config.get("scoring", {})
        self.explicit_patterns = self.config.get("explicit_patterns", [])
        self.special_cases = self.config.get("special_cases", [])

    def route(self, task: str) -> dict:
        """Route a task to the best agent with confidence scoring."""
        task_lower = task.lower()
        scores = {}
        match_details = {}

        # 1. Check explicit agent mentions first
        explicit_result = self._check_explicit_mentions(task_lower)
        if explicit_result:
            return explicit_result

        # 2. Score each agent
        for agent_name, agent_config in self.agents.items():
            score, details = self._score_agent(task_lower, agent_name, agent_config)
            scores[agent_name] = score
            match_details[agent_name] = details

        # 3. Apply special case rules
        for case in self.special_cases:
            if self._matches_condition(task_lower, case.get("condition", "")):
                agent = case.get("agent")
                if agent:
                    if "confidence" in case:
                        scores[agent] = max(scores.get(agent, 0), case["confidence"])
                    elif "confidence_boost" in case:
                        scores[agent] = scores.get(agent, 0) + case["confidence_boost"]
                    match_details[agent]["special_case"] = case.get("reason", "special case")

        # 4. Determine winner
        sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_agent, best_score = sorted_agents[0]
        alternatives = sorted_agents[1:3]

        # 5. Build result
        source = match_details.get(best_agent, {}).get("source", "fallback")
        matched = match_details.get(best_agent, {}).get("matched", [])

        result = {
            "agent": best_agent,
            "emoji": self.agents.get(best_agent, {}).get("emoji", ""),
            "confidence": round(best_score, 2),
            "source": source,
            "matched_pattern": matched[:3] if matched else None,
            "alternatives": [
                {"agent": a, "confidence": round(s, 2)}
                for a, s in alternatives
            ],
            "reasoning": self._build_reasoning(best_agent, best_score, source, matched),
            "needs_clarification": best_score < self.scoring.get("clarification_threshold", 0.60),
            "auto_assignable": best_score >= self.scoring.get("auto_assign_threshold", 0.70),
        }

        return result

    def _check_explicit_mentions(self, task: str) -> Optional[dict]:
        """Check for explicit agent mentions like 'pass to kimi' or '@claude'."""
        for pattern_config in self.explicit_patterns:
            pattern = pattern_config.get("pattern", "")
            match = re.search(pattern, task, re.IGNORECASE)
            if match and pattern_config.get("extract_agent"):
                agent = match.group("agent").lower()
                return {
                    "agent": agent,
                    "emoji": self.agents.get(agent, {}).get("emoji", ""),
                    "confidence": 1.0,
                    "source": "explicit",
                    "matched_pattern": [match.group(0)],
                    "alternatives": [],
                    "reasoning": f"Explicit mention: '{match.group(0)}'",
                    "needs_clarification": False,
                    "auto_assignable": True,
                }
        return None

    def _score_agent(self, task: str, agent_name: str, config: dict) -> tuple[float, dict]:
        """Score how well a task matches an agent."""
        score = 0.0
        matched = []
        source = "fallback"

        # Primary keywords (0.95)
        primary_conf = self.scoring.get("primary_keyword", 0.95)
        for kw in config.get("primary_keywords", []):
            if kw.lower() in task:
                if score < primary_conf:
                    score = primary_conf
                    source = "primary"
                matched.append(f"primary:{kw}")

        # Secondary keywords (0.85)
        secondary_conf = self.scoring.get("secondary_keyword", 0.85)
        for kw in config.get("secondary_keywords", []):
            if kw.lower() in task:
                if score < secondary_conf:
                    score = secondary_conf
                    source = "secondary"
                matched.append(f"secondary:{kw}")

        # Contextual patterns (0.75)
        contextual_conf = self.scoring.get("contextual_pattern", 0.75)
        for pattern in config.get("contextual_patterns", []):
            if re.search(pattern, task, re.IGNORECASE):
                if score < contextual_conf:
                    score = contextual_conf
                    source = "contextual"
                matched.append(f"pattern:{pattern[:30]}...")

        # Negative patterns (penalty)
        penalty = self.scoring.get("negative_pattern_penalty", -0.20)
        for pattern in config.get("negative_patterns", []):
            if pattern.lower() in task:
                score += penalty
                matched.append(f"negative:{pattern}")

        # Multiple keyword bonus
        if len(matched) > 1:
            bonus = self.scoring.get("multiple_keyword_bonus", 0.05)
            max_bonus = 0.10
            score += min(bonus * (len(matched) - 1), max_bonus)

        # Task length bonus
        length_config = self.scoring.get("task_length_bonus", {})
        if len(task) > length_config.get("threshold", 50):
            score += length_config.get("bonus", 0.02)

        # Clamp to [0, 1]
        score = max(0.0, min(1.0, score))

        return score, {"source": source, "matched": matched}

    def _matches_condition(self, task: str, condition: str) -> bool:
        """Evaluate a special case condition."""
        if "contains" in condition:
            # Extract quoted strings
            matches = re.findall(r"'([^']+)'", condition)
            if " or " in condition:
                return any(m.lower() in task for m in matches)
            elif " and " in condition:
                return all(m.lower() in task for m in matches)
            else:
                return any(m.lower() in task for m in matches)
        elif "starts with" in condition:
            matches = re.findall(r"'([^']+)'", condition)
            return any(task.startswith(m.lower()) for m in matches)
        return False

    def _build_reasoning(self, agent: str, score: float, source: str, matched: list) -> str:
        """Build human-readable reasoning for the routing decision."""
        specialty = self.agents.get(agent, {}).get("specialty", "unknown")

        if source == "explicit":
            return f"Explicitly assigned to {agent}"
        elif source == "primary":
            keywords = [m.split(":")[1] for m in matched if m.startswith("primary:")]
            return f"Strong signal from keywords: {', '.join(keywords[:3])}. {agent.capitalize()} specializes in {specialty}."
        elif source == "secondary":
            keywords = [m.split(":")[1] for m in matched if m.startswith("secondary:")]
            return f"Good signal from keywords: {', '.join(keywords[:3])}. {agent.capitalize()} handles {specialty}."
        elif source == "contextual":
            return f"Pattern match suggests {agent}. Specialty: {specialty}."
        else:
            return f"Fallback to {agent} (default for ambiguous tasks)."


# ─────────────────────────────────────────────────────────────
# CLI Interface
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Route a task to the best federation agent.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  route_task.py "Research the Temporal Workflows library"
  route_task.py --json "Implement the auth middleware"
  route_task.py --explain "Pass this to kimi for deployment"
        """
    )
    parser.add_argument("task", help="Task description to route")
    parser.add_argument("--json", action="store_true", help="Output full JSON result")
    parser.add_argument("--explain", action="store_true", help="Show detailed reasoning")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH, help="Path to routing config")

    args = parser.parse_args()

    try:
        router = TaskRouter(args.config)
        result = router.route(args.task)

        if args.json:
            print(json.dumps(result, indent=2))
        elif args.explain:
            print(f"Agent:      {result['emoji']} {result['agent']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Source:     {result['source']}")
            print(f"Reasoning:  {result['reasoning']}")
            if result['matched_pattern']:
                print(f"Matched:    {', '.join(result['matched_pattern'])}")
            if result['alternatives']:
                alts = ", ".join(f"{a['agent']}({a['confidence']})" for a in result['alternatives'])
                print(f"Alternatives: {alts}")
            if result['needs_clarification']:
                print("\n⚠️  Low confidence. Consider clarifying or specifying agent explicitly.")
        else:
            # Simple output for scripting
            emoji = result['emoji']
            agent = result['agent']
            conf = result['confidence']
            if result['needs_clarification']:
                print(f"? ({conf}) Ambiguous. Clarify or use: @{agent}")
            elif result['auto_assignable']:
                print(f"{emoji} {agent} ({conf})")
            else:
                print(f"{emoji} {agent} ({conf}) [review suggested]")

    except FileNotFoundError:
        print(f"Error: Config not found at {args.config}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
