#!/usr/bin/env python3
"""
Similarity Engine for Predictive Routing
Matches tasks to agents using cosine similarity and capability profiles.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from .feature_extractor import FeatureExtractor


@dataclass
class AgentProfile:
    """Profile of an agent's capabilities and history."""
    agent_id: str
    emoji: str
    specialty: str
    capability_vector: Dict[str, float]
    success_rate: float
    avg_task_duration: float
    task_count: int
    domains: List[str]
    keywords: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AgentProfile":
        return cls(**data)


@dataclass
class MatchResult:
    """Result of matching a task to an agent."""
    agent_id: str
    emoji: str
    similarity_score: float
    confidence: float
    domain_match: float
    keyword_match: float
    historical_bias: float
    explanation: str


class SimilarityEngine:
    """Engine for computing agent-task similarity."""
    
    # Agent definitions with base capabilities
    AGENT_DEFINITIONS = {
        "claude": {
            "emoji": "🔮",
            "specialty": "Research & Analysis",
            "keywords": [
                "research", "analyze", "architecture", "design", "document",
                "investigate", "explore", "study", "review", "assess",
                "evaluate", "recommend", "strategy", "planning", "structure"
            ],
            "domains": ["research", "design", "documentation", "architecture"],
            "base_success_rate": 0.92,
            "cost_tier": "medium"
        },
        "kimi": {
            "emoji": "🔧",
            "specialty": "Execution",
            "keywords": [
                "implement", "code", "build", "develop", "create", "write",
                "fix", "debug", "test", "deploy", "script", "configure",
                "setup", "install", "run", "execute", "automate"
            ],
            "domains": ["implementation", "testing", "deployment"],
            "base_success_rate": 0.94,
            "cost_tier": "low"
        },
        "copilot": {
            "emoji": "💭",
            "specialty": "Thinking & Planning",
            "keywords": [
                "plan", "think", "structure", "organize", "review",
                "check", "validate", "verify", "improve", "refactor",
                "suggest", "advise", "coordinate", "facilitate"
            ],
            "domains": ["planning", "review"],
            "base_success_rate": 0.88,
            "cost_tier": "free"
        },
        "ollama": {
            "emoji": "🏠",
            "specialty": "Local Drafting",
            "keywords": [
                "draft", "prototype", "experiment", "try", "sketch",
                "outline", "mockup", "template", "sample", "example"
            ],
            "domains": ["drafting", "prototyping"],
            "base_success_rate": 0.75,
            "cost_tier": "free"
        }
    }
    
    def __init__(self, data_dir: str = ".federation/predictor/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.extractor = FeatureExtractor(data_dir)
        self.profiles: Dict[str, AgentProfile] = {}
        self._load_profiles()
    
    def _load_profiles(self) -> None:
        """Load or initialize agent profiles."""
        profiles_file = self.data_dir / "agent_profiles.json"
        
        if profiles_file.exists():
            with open(profiles_file) as f:
                data = json.load(f)
                for agent_id, profile_data in data.items():
                    self.profiles[agent_id] = AgentProfile.from_dict(profile_data)
        else:
            # Initialize with base definitions
            for agent_id, defn in self.AGENT_DEFINITIONS.items():
                self.profiles[agent_id] = AgentProfile(
                    agent_id=agent_id,
                    emoji=defn["emoji"],
                    specialty=defn["specialty"],
                    capability_vector=self._build_capability_vector(defn),
                    success_rate=defn["base_success_rate"],
                    avg_task_duration=30.0,
                    task_count=0,
                    domains=defn["domains"],
                    keywords=defn["keywords"]
                )
            self._save_profiles()
    
    def _save_profiles(self) -> None:
        """Save agent profiles to disk."""
        profiles_file = self.data_dir / "agent_profiles.json"
        with open(profiles_file, "w") as f:
            json.dump(
                {k: v.to_dict() for k, v in self.profiles.items()},
                f, indent=2
            )
    
    def _build_capability_vector(self, definition: Dict) -> Dict[str, float]:
        """Build initial capability vector from definition."""
        vector = {}
        
        # Add keywords with high weight
        for kw in definition["keywords"]:
            vector[kw] = 1.0
        
        # Add domain terms
        for domain in definition["domains"]:
            vector[domain] = 0.8
        
        # Add specialty terms
        for term in definition["specialty"].lower().split():
            if term not in ["&"]:
                vector[term] = 0.9
        
        return vector
    
    def compute_task_agent_similarity(
        self,
        task_vector: Dict[str, float],
        task_domains: List[str],
        agent_id: str
    ) -> Tuple[float, float, float, str]:
        """
        Compute similarity between task and agent.
        Returns: (similarity, domain_match, keyword_match, explanation)
        """
        if agent_id not in self.profiles:
            return 0.0, 0.0, 0.0, "Unknown agent"
        
        profile = self.profiles[agent_id]
        
        # Compute cosine similarity
        similarity = self.extractor.cosine_similarity(
            task_vector,
            profile.capability_vector
        )
        
        # Compute domain match
        if task_domains:
            matching_domains = set(task_domains) & set(profile.domains)
            domain_match = len(matching_domains) / max(len(task_domains), len(profile.domains))
        else:
            domain_match = 0.5  # Neutral if no domains
        
        # Compute keyword match
        task_terms = set(task_vector.keys())
        agent_terms = set(profile.capability_vector.keys())
        if task_terms:
            matching_terms = task_terms & agent_terms
            keyword_match = len(matching_terms) / len(task_terms)
        else:
            keyword_match = 0.0
        
        # Build explanation
        explanation = self._build_explanation(
            agent_id, similarity, domain_match, keyword_match,
            task_domains, profile
        )
        
        return similarity, domain_match, keyword_match, explanation
    
    def _build_explanation(
        self,
        agent_id: str,
        similarity: float,
        domain_match: float,
        keyword_match: float,
        task_domains: List[str],
        profile: AgentProfile
    ) -> str:
        """Build human-readable explanation for match."""
        parts = []
        
        parts.append(f"Agent: {profile.emoji} {agent_id.title()} ({profile.specialty})")
        
        if similarity > 0.7:
            parts.append(f"Strong semantic similarity ({similarity:.0%})")
        elif similarity > 0.4:
            parts.append(f"Moderate semantic similarity ({similarity:.0%})")
        else:
            parts.append(f"Low semantic similarity ({similarity:.0%})")
        
        if domain_match > 0.5:
            matching = set(task_domains) & set(profile.domains)
            parts.append(f"Domain match: {', '.join(matching)}")
        
        parts.append(f"Historical success rate: {profile.success_rate:.0%}")
        parts.append(f"Tasks completed: {profile.task_count}")
        
        return "; ".join(parts)
    
    def find_best_matches(
        self,
        task_description: str,
        task_type: str = "",
        top_k: int = 4
    ) -> List[MatchResult]:
        """Find top-k matching agents for a task."""
        # Vectorize task
        features = self.extractor.vectorize_task(task_description, task_type)
        task_vector = features["tfidf_vector"]
        task_domains = features["domains"]
        
        matches = []
        
        for agent_id, profile in self.profiles.items():
            similarity, domain_match, keyword_match, explanation = \
                self.compute_task_agent_similarity(
                    task_vector, task_domains, agent_id
                )
            
            # Compute confidence using weighted combination
            historical_bias = profile.success_rate
            confidence = (
                similarity * 0.4 +
                domain_match * 0.3 +
                keyword_match * 0.2 +
                historical_bias * 0.1
            )
            
            matches.append(MatchResult(
                agent_id=agent_id,
                emoji=profile.emoji,
                similarity_score=round(similarity, 3),
                confidence=round(confidence, 3),
                domain_match=round(domain_match, 3),
                keyword_match=round(keyword_match, 3),
                historical_bias=round(historical_bias, 3),
                explanation=explanation
            ))
        
        # Sort by confidence
        matches.sort(key=lambda x: x.confidence, reverse=True)
        
        return matches[:top_k]
    
    def update_profile_from_completion(
        self,
        agent_id: str,
        task_description: str,
        success: bool,
        duration_minutes: float
    ) -> None:
        """Update agent profile based on task completion."""
        if agent_id not in self.profiles:
            return
        
        profile = self.profiles[agent_id]
        
        # Update task count
        profile.task_count += 1
        
        # Update success rate with exponential moving average
        alpha = 0.1  # Learning rate
        success_val = 1.0 if success else 0.0
        profile.success_rate = (1 - alpha) * profile.success_rate + alpha * success_val
        
        # Update average duration
        if profile.task_count == 1:
            profile.avg_task_duration = duration_minutes
        else:
            profile.avg_task_duration = (
                (profile.avg_task_duration * (profile.task_count - 1) + duration_minutes)
                / profile.task_count
            )
        
        # Update capability vector with task terms
        features = self.extractor.vectorize_task(task_description)
        task_vector = features["tfidf_vector"]
        
        for term, weight in task_vector.items():
            if term in profile.capability_vector:
                # Reinforce existing capability
                profile.capability_vector[term] = min(
                    1.0,
                    profile.capability_vector[term] + 0.01 * weight
                )
            else:
                # Add new capability with small weight
                profile.capability_vector[term] = 0.1 * weight
        
        self._save_profiles()
    
    def get_profile(self, agent_id: str) -> Optional[AgentProfile]:
        """Get profile for a specific agent."""
        return self.profiles.get(agent_id)
    
    def get_all_profiles(self) -> Dict[str, AgentProfile]:
        """Get all agent profiles."""
        return self.profiles.copy()


# Simple test
if __name__ == "__main__":
    engine = SimilarityEngine()
    
    # Test matching
    task = "Implement a REST API for user management with authentication"
    matches = engine.find_best_matches(task, "implementation")
    
    print(f"Task: {task}")
    print("\nTop matches:")
    for i, match in enumerate(matches, 1):
        print(f"\n{i}. {match.emoji} {match.agent_id.title()}")
        print(f"   Confidence: {match.confidence:.0%}")
        print(f"   Similarity: {match.similarity_score:.0%}")
        print(f"   Explanation: {match.explanation}")
