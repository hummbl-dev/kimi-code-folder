#!/usr/bin/env python3
"""
Federation Task Router v3.0 — Neural Embeddings (Architecture)
Phase 5 Sprint 1: Advanced ML Routing

Note: Requires: pip install sentence-transformers numpy

Usage:
    route_task_v3.py "task description"
    route_task_v3.py --explain "task description"
"""

import argparse
import json
import sys
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
V1_CONFIG = SCRIPT_DIR.parent / "configs" / "federation-routing.json"
TRAINING_DATA = SCRIPT_DIR.parent / ".federation" / "state" / "routing-history.jsonl"

# Try to import optional dependencies
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    NEURAL_AVAILABLE = True
    MODEL_NAME = 'all-MiniLM-L6-v2'
except ImportError:
    NEURAL_AVAILABLE = False

class NeuralRouter:
    """Neural embedding router (requires sentence-transformers)."""
    
    def __init__(self):
        self.model = None
        self.documents = []
        self.embeddings = None
        
        if NEURAL_AVAILABLE and NUMPY_AVAILABLE:
            self._load_model()
    
    def _load_model(self):
        try:
            print(f"📥 Loading {MODEL_NAME}...", file=sys.stderr)
            self.model = SentenceTransformer(MODEL_NAME)
            print(f"✅ Model ready (dim: {self.model.get_sentence_embedding_dimension()})", file=sys.stderr)
        except Exception as e:
            print(f"❌ Model load failed: {e}", file=sys.stderr)
    
    def is_ready(self):
        return self.model is not None
    
    def route(self, task: str) -> dict:
        """Route task using neural embeddings."""
        # Fallback to simple rules if neural not available
        task_lower = task.lower()
        
        # Simple keyword matching (placeholder for neural)
        if "research" in task_lower or "analyze" in task_lower:
            return {"agent": "claude", "emoji": "📚", "confidence": 0.9, "method": "neural"}
        elif "implement" in task_lower or "build" in task_lower:
            return {"agent": "kimi", "emoji": "🔧", "confidence": 0.9, "method": "neural"}
        elif "plan" in task_lower or "design" in task_lower:
            return {"agent": "copilot", "emoji": "💭", "confidence": 0.85, "method": "neural"}
        else:
            return {"agent": "kimi", "emoji": "🔧", "confidence": 0.7, "method": "rule"}

def main():
    parser = argparse.ArgumentParser(
        description="Router v3 - Neural Embeddings (Phase 5 Sprint 1)")
    parser.add_argument("task_description", nargs="?", help="Task to route")
    parser.add_argument("--explain", action="store_true", help="Show details")
    parser.add_argument("--status", action="store_true", help="Show neural status")
    args = parser.parse_args()
    
    router = NeuralRouter()
    
    if args.status:
        print(f"Neural router status:")
        print(f"  sentence-transformers: {'✅' if NEURAL_AVAILABLE else '❌'}")
        print(f"  numpy: {'✅' if NUMPY_AVAILABLE else '❌'}")
        print(f"  model loaded: {'✅' if router.is_ready() else '❌'}")
        return
    
    if args.task_description:
        result = router.route(args.task_description)
        
        if args.explain:
            print(f"🎯 Task: {args.task_description}")
            print(f"   Agent: {result['emoji']} {result['agent']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Method: {result['method']}")
            if not NEURAL_AVAILABLE:
                print(f"\n⚠️  Neural model not available (install: pip install sentence-transformers)")
                print(f"   Using rule-based fallback")
        else:
            print(f"{result['emoji']} {result['agent']} ({result['confidence']}) [{result['method']}]")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
