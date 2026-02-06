#!/usr/bin/env python3
"""
ML-Enhanced Task Router for Federation
Combines keyword-based routing with ML similarity matching.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    # Try relative imports first
    sys.path.insert(0, str(Path(__file__).parent.parent / '.federation'))
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from predictor.similarity_engine import SimilarityEngine, MatchResult
    from predictor.historical_learner import HistoricalLearner
    ML_AVAILABLE = True
except ImportError as e:
    # Fallback if predictor modules not available
    print(f"Debug: ML import error: {e}", file=sys.stderr)
    ML_AVAILABLE = False


class MLRouter:
    """ML-enhanced task router."""
    
    # Thresholds for auto-assignment
    AUTO_ASSIGN_THRESHOLD = 0.75
    CLARIFICATION_THRESHOLD = 0.60
    
    # Weight configuration
    KEYWORD_WEIGHT = 0.40
    SIMILARITY_WEIGHT = 0.40
    HISTORICAL_WEIGHT = 0.20
    
    def __init__(self, use_ml: bool = True):
        self.use_ml = use_ml and ML_AVAILABLE
        self.engine = None
        self.learner = None
        
        if self.use_ml:
            try:
                self.engine = SimilarityEngine()
                self.learner = HistoricalLearner()
            except Exception as e:
                print(f"Warning: ML components failed to load: {e}", file=sys.stderr)
                self.use_ml = False
    
    def route_task(
        self,
        description: str,
        task_type: str = "",
        required_agent: Optional[str] = None,
        explain: bool = False
    ) -> Dict:
        """
        Route a task to the best agent.
        
        Args:
            description: Task description
            task_type: Optional task type/category
            required_agent: If specified, route to this agent
            explain: Include detailed explanation in result
            
        Returns:
            Routing decision with confidence and explanation
        """
        # If specific agent required
        if required_agent:
            return self._create_fixed_assignment(required_agent, description, explain)
        
        # Get ML-based matches if available
        if self.use_ml and self.engine:
            ml_matches = self.engine.find_best_matches(description, task_type, top_k=4)
            return self._process_ml_matches(ml_matches, description, explain)
        else:
            # Fallback to keyword-based routing
            return self._fallback_keyword_routing(description, explain)
    
    def _create_fixed_assignment(
        self,
        agent_id: str,
        description: str,
        explain: bool
    ) -> Dict:
        """Create routing for fixed agent assignment."""
        result = {
            "recommended_agent": agent_id,
            "confidence": 1.0,
            "method": "explicit_assignment",
            "auto_assign": True,
            "explanation": f"Explicitly assigned to {agent_id}"
        }
        
        if explain:
            result["detailed_explanation"] = {
                "reason": "Agent specified in routing request",
                "override": True
            }
            result["alternatives"] = []
        
        return result
    
    def _process_ml_matches(
        self,
        matches: List[MatchResult],
        description: str,
        explain: bool
    ) -> Dict:
        """Process ML matches into routing decision."""
        if not matches:
            return self._fallback_keyword_routing(description, explain)
        
        best_match = matches[0]
        confidence = best_match.confidence
        
        # Determine routing decision
        if confidence >= self.AUTO_ASSIGN_THRESHOLD:
            decision = "auto_assign"
        elif confidence >= self.CLARIFICATION_THRESHOLD:
            decision = "suggest_clarification"
        else:
            decision = "manual_assignment"
        
        result = {
            "recommended_agent": best_match.agent_id,
            "confidence": confidence,
            "method": "ml_similarity",
            "auto_assign": decision == "auto_assign",
            "decision": decision,
            "explanation": best_match.explanation if explain else self._summarize_explanation(best_match)
        }
        
        if explain:
            result["detailed_explanation"] = {
                "similarity_score": best_match.similarity_score,
                "domain_match": best_match.domain_match,
                "keyword_match": best_match.keyword_match,
                "historical_bias": best_match.historical_bias,
                "reasoning": self._build_detailed_reasoning(best_match)
            }
            
            # Add alternatives
            result["alternatives"] = [
                {
                    "agent": m.agent_id,
                    "emoji": m.emoji,
                    "confidence": m.confidence,
                    "explanation": m.explanation[:100] + "..." if len(m.explanation) > 100 else m.explanation
                }
                for m in matches[1:3]  # Top 2 alternatives
            ]
            
            # Add learning info
            if self.learner:
                success_prob = self.learner.predict_success_probability(
                    best_match.agent_id, description
                )
                result["prediction"] = {
                    "success_probability": round(success_prob, 2),
                    "estimated_duration_minutes": self._get_estimated_duration(best_match.agent_id)
                }
        
        return result
    
    def _fallback_keyword_routing(self, description: str, explain: bool) -> Dict:
        """Fallback to simple keyword-based routing."""
        desc_lower = description.lower()
        
        # Simple keyword matching
        agent_keywords = {
            "claude": ["research", "analyze", "architecture", "design", "document"],
            "kimi": ["implement", "code", "build", "develop", "fix", "test"],
            "copilot": ["plan", "review", "structure", "organize", "coordinate"],
            "ollama": ["draft", "prototype", "experiment", "try"]
        }
        
        scores = {}
        for agent, keywords in agent_keywords.items():
            score = sum(1 for kw in keywords if kw in desc_lower)
            scores[agent] = score / len(keywords) if keywords else 0
        
        best_agent = max(scores, key=scores.get)
        confidence = scores[best_agent]
        
        # Normalize to reasonable range
        confidence = min(0.7, confidence * 2)  # Cap at 0.7 for keyword-only
        
        result = {
            "recommended_agent": best_agent,
            "confidence": round(confidence, 2),
            "method": "keyword_fallback",
            "auto_assign": confidence >= 0.5,
            "explanation": f"Keyword match: {best_agent} (fallback mode)"
        }
        
        if explain:
            result["detailed_explanation"] = {
                "keyword_scores": scores,
                "note": "ML components unavailable, using keyword fallback"
            }
        
        return result
    
    def _summarize_explanation(self, match: MatchResult) -> str:
        """Create brief explanation."""
        return f"{match.emoji} {match.agent_id.title()}: {match.confidence:.0%} confidence"
    
    def _build_detailed_reasoning(self, match: MatchResult) -> str:
        """Build detailed reasoning string."""
        parts = []
        
        if match.similarity_score > 0.7:
            parts.append(f"Strong semantic match ({match.similarity_score:.0%})")
        elif match.similarity_score > 0.4:
            parts.append(f"Moderate semantic match ({match.similarity_score:.0%})")
        
        if match.domain_match > 0.5:
            parts.append(f"Domain alignment ({match.domain_match:.0%})")
        
        if match.historical_bias > 0.9:
            parts.append(f"Excellent track record ({match.historical_bias:.0%})")
        elif match.historical_bias < 0.8:
            parts.append(f"Limited history ({match.historical_bias:.0%})")
        
        return "; ".join(parts) if parts else "Based on overall profile match"
    
    def _get_estimated_duration(self, agent_id: str) -> Optional[float]:
        """Get estimated task duration for agent."""
        if not self.engine:
            return None
        
        profile = self.engine.get_profile(agent_id)
        if profile:
            return round(profile.avg_task_duration, 1)
        return None
    
    def update_from_completion(
        self,
        agent_id: str,
        task_description: str,
        success: bool = True,
        duration_minutes: float = 30.0
    ) -> bool:
        """Update ML models from task completion."""
        if not self.use_ml or not self.learner:
            return False
        
        try:
            self.learner.learn_from_task({
                "task_id": f"feedback-{hash(task_description) % 10000}",
                "description": task_description,
                "completed_by": agent_id,
                "success": success,
                "duration_minutes": duration_minutes,
                "timestamp": "2026-02-06T01:00:00Z"
            })
            return True
        except Exception as e:
            print(f"Warning: Failed to update learning: {e}", file=sys.stderr)
            return False
    
    def get_stats(self) -> Dict:
        """Get router statistics."""
        stats = {
            "ml_available": self.use_ml,
            "auto_assign_threshold": self.AUTO_ASSIGN_THRESHOLD,
            "clarification_threshold": self.CLARIFICATION_THRESHOLD
        }
        
        if self.use_ml and self.learner:
            stats["learning"] = self.learner.get_learning_stats()
        
        if self.use_ml and self.engine:
            profiles = self.engine.get_all_profiles()
            stats["agents"] = {
                agent_id: {
                    "success_rate": p.success_rate,
                    "task_count": p.task_count,
                    "avg_duration": round(p.avg_task_duration, 1)
                }
                for agent_id, p in profiles.items()
            }
        
        return stats


def main():
    parser = argparse.ArgumentParser(
        description="ML-Enhanced Task Router for Federation"
    )
    parser.add_argument(
        "task",
        nargs="?",
        default="",
        help="Task description to route"
    )
    parser.add_argument(
        "--type", "-t",
        default="",
        help="Task type/category"
    )
    parser.add_argument(
        "--to", "-a",
        dest="agent",
        help="Require specific agent"
    )
    parser.add_argument(
        "--explain", "-e",
        action="store_true",
        help="Include detailed explanation"
    )
    parser.add_argument(
        "--no-ml",
        action="store_true",
        help="Disable ML, use keyword fallback only"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show router statistics"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    router = MLRouter(use_ml=not args.no_ml)
    
    if args.stats:
        stats = router.get_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("Router Statistics")
            print("=" * 50)
            print(f"ML Available: {stats['ml_available']}")
            print(f"Auto-assign Threshold: {stats['auto_assign_threshold']}")
            print(f"Clarification Threshold: {stats['clarification_threshold']}")
            
            if 'learning' in stats:
                learning = stats['learning']
                print(f"\nLearning Status: {learning.get('status', 'unknown')}")
                if 'total_learning_events' in learning:
                    print(f"Learning Events: {learning['total_learning_events']}")
            
            if 'agents' in stats:
                print("\nAgent Profiles:")
                for agent, profile in stats['agents'].items():
                    print(f"  {agent}: {profile['success_rate']:.0%} success, "
                          f"{profile['task_count']} tasks")
        return
    
    if not args.task:
        parser.print_help()
        sys.exit(1)
    
    # Route the task
    result = router.route_task(
        description=args.task,
        task_type=args.type,
        required_agent=args.agent,
        explain=args.explain
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Task: {args.task}")
        print(f"Recommended Agent: {result['recommended_agent']}")
        print(f"Confidence: {result['confidence']:.0%}")
        print(f"Method: {result['method']}")
        print(f"Auto-assign: {'Yes' if result['auto_assign'] else 'No'}")
        print(f"\nExplanation: {result['explanation']}")
        
        if 'detailed_explanation' in result:
            print("\nDetailed Explanation:")
            de = result['detailed_explanation']
            if 'similarity_score' in de:
                print(f"  Similarity: {de['similarity_score']:.0%}")
                print(f"  Domain Match: {de['domain_match']:.0%}")
                print(f"  Keyword Match: {de['keyword_match']:.0%}")
                print(f"  Historical: {de['historical_bias']:.0%}")
            if 'reasoning' in de:
                print(f"  Reasoning: {de['reasoning']}")
        
        if 'alternatives' in result:
            print("\nAlternatives:")
            for alt in result['alternatives']:
                print(f"  {alt['emoji']} {alt['agent']}: {alt['confidence']:.0%}")
        
        if 'prediction' in result:
            pred = result['prediction']
            print(f"\nPrediction:")
            print(f"  Success Probability: {pred['success_probability']:.0%}")
            if pred.get('estimated_duration_minutes'):
                print(f"  Est. Duration: {pred['estimated_duration_minutes']} min")


if __name__ == "__main__":
    main()
