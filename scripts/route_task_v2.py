#!/usr/bin/env python3
"""
Federation Task Router v2.0 — Predictive Routing
Phase 4 Sprint 5: ML-Enhanced Task Routing

Hybrid approach: Rule-based + TF-IDF similarity

Usage:
    route_task_v2.py "task description"
    route_task_v2.py --explain "task description"
    route_task_v2.py --train --task "..." --agent "..." --success true
    route_task_v2.py --compare "task description"  # A/B test vs v1

Examples:
    route_task_v2.py "Research authentication patterns"
    route_task_v2.py --explain "Build the user dashboard"
    route_task_v2.py --train --task "Research auth" --agent claude --success true --duration 35
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import math

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
V1_CONFIG = SCRIPT_DIR.parent / "configs" / "federation-routing.json"
TRAINING_DATA = SCRIPT_DIR.parent / ".federation" / "state" / "routing-history.jsonl"
V2_CONFIG = SCRIPT_DIR.parent / ".federation" / "state" / "routing-v2-config.json"

# Algorithm weights (configurable)
RULE_WEIGHT = 0.6
ML_WEIGHT = 0.4
MIN_TRAINING_SAMPLES = 10

# ─────────────────────────────────────────────────────────────
# TF-IDF Implementation (Lightweight)
# ─────────────────────────────────────────────────────────────

class SimpleTFIDF:
    """Lightweight TF-IDF for task similarity matching."""
    
    def __init__(self):
        self.documents: List[Tuple[str, str]] = []  # (text, agent)
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.document_vectors: List[Dict[str, float]] = []
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        # Lowercase, remove special chars, split
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        tokens = text.split()
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 
                      'be', 'been', 'being', 'have', 'has', 'had',
                      'do', 'does', 'did', 'will', 'would', 'could',
                      'should', 'may', 'might', 'must', 'shall',
                      'can', 'need', 'dare', 'ought', 'used', 'to',
                      'of', 'in', 'for', 'on', 'with', 'at', 'by',
                      'from', 'as', 'into', 'through', 'during',
                      'before', 'after', 'above', 'below', 'between',
                      'under', 'and', 'but', 'or', 'yet', 'so',
                      'if', 'because', 'although', 'though', 'while',
                      'where', 'when', 'that', 'which', 'who', 'whom',
                      'whose', 'what', 'this', 'these', 'those',
                      'i', 'you', 'he', 'she', 'it', 'we', 'they',
                      'me', 'him', 'her', 'us', 'them', 'my', 'your',
                      'his', 'its', 'our', 'their', 'mine', 'yours',
                      'hers', 'ours', 'theirs', 'myself', 'yourself',
                      'himself', 'herself', 'itself', 'ourselves',
                      'yourselves', 'themselves', 'am', 'it', 's', 't'}
        return [t for t in tokens if t not in stop_words and len(t) > 2]
    
    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Compute term frequency."""
        tf = defaultdict(int)
        for token in tokens:
            tf[token] += 1
        # Normalize
        total = len(tokens)
        if total > 0:
            tf = {k: v/total for k, v in tf.items()}
        return dict(tf)
    
    def _compute_idf(self):
        """Compute inverse document frequency."""
        N = len(self.documents)
        if N == 0:
            return
        
        # Count document frequency for each term
        df = defaultdict(int)
        for text, _ in self.documents:
            tokens = set(self._tokenize(text))
            for token in tokens:
                df[token] += 1
        
        # IDF = log(N / df)
        self.idf = {term: math.log(N / (df[term] + 1)) + 1 
                    for term in df}
    
    def fit(self, documents: List[Tuple[str, str]]):
        """Fit TF-IDF on training documents."""
        self.documents = documents
        self._compute_idf()
        
        # Compute document vectors
        self.document_vectors = []
        for text, agent in documents:
            tokens = self._tokenize(text)
            tf = self._compute_tf(tokens)
            # TF-IDF vector
            vector = {term: tf.get(term, 0) * self.idf.get(term, 0) 
                     for term in self.idf.keys()}
            # Normalize vector
            magnitude = math.sqrt(sum(v**2 for v in vector.values()))
            if magnitude > 0:
                vector = {k: v/magnitude for k, v in vector.items()}
            self.document_vectors.append((vector, agent))
    
    def predict(self, text: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Predict best agent for text using cosine similarity."""
        if not self.document_vectors:
            return []
        
        # Compute query vector
        tokens = self._tokenize(text)
        tf = self._compute_tf(tokens)
        query_vector = {term: tf.get(term, 0) * self.idf.get(term, 0) 
                       for term in self.idf.keys()}
        
        # Normalize
        magnitude = math.sqrt(sum(v**2 for v in query_vector.values()))
        if magnitude > 0:
            query_vector = {k: v/magnitude for k, v in query_vector.items()}
        
        # Compute cosine similarity with all documents
        agent_scores = defaultdict(list)
        for doc_vector, agent in self.document_vectors:
            # Cosine similarity = dot product (both normalized)
            similarity = sum(query_vector.get(term, 0) * doc_vector.get(term, 0) 
                           for term in set(query_vector) & set(doc_vector))
            agent_scores[agent].append(similarity)
        
        # Average similarity per agent
        avg_scores = {agent: sum(scores)/len(scores) 
                     for agent, scores in agent_scores.items()}
        
        # Sort by score
        sorted_agents = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_agents[:top_k]


# ─────────────────────────────────────────────────────────────
# Rule-Based Router (v1 compatible)
# ─────────────────────────────────────────────────────────────

class RuleBasedRouter:
    """Original rule-based routing from v1."""
    
    def __init__(self, config_path: Path = V1_CONFIG):
        with open(config_path) as f:
            self.config = json.load(f)
        self.agents = self.config.get("agents", {})
        self.scoring = self.config.get("scoring", {})
        self.special_cases = self.config.get("special_cases", [])
    
    def route(self, task: str) -> Tuple[str, float, str]:
        """Route using rules. Returns (agent, score, method)."""
        task_lower = task.lower()
        scores = {}
        
        for agent_name, agent_config in self.agents.items():
            score = self._score_agent(task_lower, agent_name, agent_config)
            scores[agent_name] = score
        
        # Apply special cases
        for case in self.special_cases:
            if self._matches_condition(task_lower, case.get("condition", "")):
                agent = case.get("agent")
                if agent:
                    if "confidence" in case:
                        scores[agent] = max(scores.get(agent, 0), case["confidence"])
                    elif "confidence_boost" in case:
                        scores[agent] = scores.get(agent, 0) + case["confidence_boost"]
        
        best_agent = max(scores, key=scores.get)
        return best_agent, scores[best_agent], "rule"
    
    def _score_agent(self, task: str, agent_name: str, config: dict) -> float:
        """Score agent for task."""
        score = 0.0
        
        primary_conf = self.scoring.get("primary_keyword", 0.95)
        for kw in config.get("primary_keywords", []):
            if kw.lower() in task:
                score = max(score, primary_conf)
        
        secondary_conf = self.scoring.get("secondary_keyword", 0.85)
        for kw in config.get("secondary_keywords", []):
            if kw.lower() in task:
                score = max(score, secondary_conf)
        
        contextual_conf = self.scoring.get("contextual_pattern", 0.75)
        for pattern in config.get("contextual_patterns", []):
            if re.search(pattern, task, re.IGNORECASE):
                score = max(score, contextual_conf)
        
        penalty = self.scoring.get("negative_pattern_penalty", -0.20)
        for pattern in config.get("negative_patterns", []):
            if pattern.lower() in task:
                score += penalty
        
        return max(0.0, min(1.0, score))
    
    def _matches_condition(self, task: str, condition: str) -> bool:
        """Check special case condition."""
        if "contains" in condition:
            matches = re.findall(r"'([^']+)'", condition)
            if " or " in condition:
                return any(m.lower() in task for m in matches)
            return any(m.lower() in task for m in matches)
        elif "starts with" in condition:
            matches = re.findall(r"'([^']+)'", condition)
            return any(task.startswith(m.lower()) for m in matches)
        return False


# ─────────────────────────────────────────────────────────────
# Hybrid Router (v2)
# ─────────────────────────────────────────────────────────────

class HybridRouter:
    """Hybrid router combining rules and ML."""
    
    def __init__(self):
        self.rule_router = RuleBasedRouter()
        self.tfidf = SimpleTFIDF()
        self.training_samples = 0
        self._load_training_data()
    
    def _load_training_data(self):
        """Load training data from file."""
        if not TRAINING_DATA.exists():
            return
        
        documents = []
        with open(TRAINING_DATA) as f:
            for line in f:
                try:
                    record = json.loads(line)
                    documents.append((record["task"], record["agent"]))
                except (json.JSONDecodeError, KeyError):
                    continue
        
        if documents:
            self.tfidf.fit(documents)
            self.training_samples = len(documents)
    
    def route(self, task: str) -> Dict:
        """Route task using hybrid approach."""
        # Get rule-based score
        rule_agent, rule_score, _ = self.rule_router.route(task)
        
        # Get ML score if enough training data
        ml_scores = {}
        ml_confidence = 0.0
        
        if self.training_samples >= MIN_TRAINING_SAMPLES:
            ml_predictions = self.tfidf.predict(task)
            if ml_predictions:
                # Normalize ML scores to 0-1
                max_score = ml_predictions[0][1] if ml_predictions else 1
                if max_score > 0:
                    ml_scores = {agent: score/max_score 
                                for agent, score in ml_predictions}
                ml_confidence = min(1.0, self.training_samples / 100)  # Confidence grows with data
        
        # Combine scores
        combined_scores = {}
        for agent in self.rule_router.agents.keys():
            rule_component = RULE_WEIGHT * (1.0 if agent == rule_agent else rule_score * 0.5)
            ml_component = ML_WEIGHT * ml_scores.get(agent, 0) * ml_confidence
            combined_scores[agent] = rule_component + ml_component
        
        # Determine winner
        best_agent = max(combined_scores, key=combined_scores.get)
        best_score = combined_scores[best_agent]
        
        # Determine method
        if ml_confidence > 0.5:
            method = "hybrid"
        else:
            method = "rule"
        
        # Build alternatives
        sorted_agents = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        alternatives = [
            {"agent": a, "confidence": round(s, 2)}
            for a, s in sorted_agents[1:3]
        ]
        
        return {
            "agent": best_agent,
            "emoji": self.rule_router.agents.get(best_agent, {}).get("emoji", ""),
            "confidence": round(best_score, 2),
            "method": method,
            "rule_component": round(rule_score, 2),
            "ml_component": round(ml_scores.get(best_agent, 0), 2),
            "ml_confidence": round(ml_confidence, 2),
            "training_samples": self.training_samples,
            "alternatives": alternatives,
            "auto_assignable": best_score >= 0.70,
            "needs_clarification": best_score < 0.60
        }
    
    def record_training(self, task: str, agent: str, success: bool,
                        duration: Optional[int] = None, notes: Optional[str] = None):
        """Record training example."""
        TRAINING_DATA.parent.mkdir(parents=True, exist_ok=True)
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "agent": agent,
            "success": success,
            "duration": duration,
            "notes": notes
        }
        
        with open(TRAINING_DATA, 'a') as f:
            f.write(json.dumps(record) + '\n')
        
        self.training_samples += 1
        return record
    
    def compare_with_v1(self, task: str) -> Dict:
        """Compare v1 vs v2 routing."""
        v1_agent, v1_score, _ = self.rule_router.route(task)
        v2_result = self.route(task)
        
        return {
            "task": task,
            "v1": {
                "agent": v1_agent,
                "confidence": round(v1_score, 2)
            },
            "v2": {
                "agent": v2_result["agent"],
                "confidence": v2_result["confidence"],
                "method": v2_result["method"]
            },
            "match": v1_agent == v2_result["agent"],
            "improvement": round(v2_result["confidence"] - v1_score, 2)
        }


# ─────────────────────────────────────────────────────────────
# CLI Interface
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Federation Task Router v2.0 — Predictive Routing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  route_task_v2.py "Research authentication patterns"
  route_task_v2.py --explain "Build the user dashboard"
  route_task_v2.py --compare "Implement auth middleware"
  route_task_v2.py --train --task "Research auth" --agent claude --success true --duration 35
        """
    )
    
    parser.add_argument("task_description", nargs="?", help="Task description to route")
    parser.add_argument("--explain", action="store_true", 
                       help="Show detailed routing breakdown")
    parser.add_argument("--compare", action="store_true",
                       help="Compare v1 vs v2 routing")
    parser.add_argument("--train", action="store_true",
                       help="Record training example")
    parser.add_argument("--train-task", help="Task text (for --train)")
    parser.add_argument("--agent", help="Agent (for --train)")
    parser.add_argument("--success", choices=["true", "false"],
                       help="Task success (for --train)")
    parser.add_argument("--duration", type=int, help="Duration in minutes (for --train)")
    parser.add_argument("--notes", help="Notes (for --train)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    router = HybridRouter()
    
    if args.train:
        if not all([args.train_task, args.agent, args.success]):
            print("❌ Error: --train requires --train-task, --agent, and --success")
            sys.exit(1)
        
        record = router.record_training(
            args.train_task, args.agent, args.success == "true",
            args.duration, args.notes
        )
        print(f"✅ Recorded training example")
        print(f"   Task: {record['task'][:50]}...")
        print(f"   Agent: {record['agent']}")
        print(f"   Success: {record['success']}")
        print(f"   Total samples: {router.training_samples}")
    
    elif args.compare and args.task_description:
        result = router.compare_with_v1(args.task_description)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"📊 A/B Comparison: v1 vs v2")
            print(f"Task: {result['task']}")
            print(f"")
            print(f"v1 (Rules):     {result['v1']['agent']} ({result['v1']['confidence']})")
            print(f"v2 (Hybrid):    {result['v2']['agent']} ({result['v2']['confidence']})")
            print(f"Method:         {result['v2']['method']}")
            print(f"")
            if result['match']:
                print(f"✅ Both routers agree")
            else:
                print(f"⚠️  Routers disagree!")
            print(f"Confidence delta: {result['improvement']:+.2f}")
    
    elif args.task_description:
        result = router.route(args.task_description)
        
        if args.json:
            print(json.dumps(result, indent=2))
        elif args.explain:
            print(f"Task: {args.task_description}")
            print(f"")
            print(f"🎯 Routing Decision")
            print(f"   Agent:      {result['emoji']} {result['agent']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Method:     {result['method']}")
            print(f"")
            print(f"📊 Score Breakdown")
            print(f"   Rule component: {result['rule_component']}")
            print(f"   ML component:   {result['ml_component']}")
            print(f"   ML confidence:  {result['ml_confidence']} (samples: {result['training_samples']})")
            print(f"")
            if result['alternatives']:
                print(f"Alternatives:")
                for alt in result['alternatives']:
                    print(f"   • {alt['agent']}: {alt['confidence']}")
            if result['needs_clarification']:
                print(f"⚠️  Low confidence — consider clarification")
        else:
            # Simple output
            emoji = result['emoji']
            agent = result['agent']
            conf = result['confidence']
            method = result['method']
            
            if result['needs_clarification']:
                print(f"? ({conf}) Ambiguous — clarify or use @{agent}")
            else:
                print(f"{emoji} {agent} ({conf}) [{method}]")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
