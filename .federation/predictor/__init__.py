"""
Predictor package for ML-enhanced task routing.
"""

from .feature_extractor import FeatureExtractor
from .similarity_engine import SimilarityEngine, AgentProfile, MatchResult
from .historical_learner import HistoricalLearner

__all__ = [
    "FeatureExtractor",
    "SimilarityEngine",
    "AgentProfile",
    "MatchResult",
    "HistoricalLearner",
]

__version__ = "1.0.0"
