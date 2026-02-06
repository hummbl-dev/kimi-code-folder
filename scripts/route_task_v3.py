#!/usr/bin/env python3
"""
Neural Router v3 — Hybrid Tier 1+2 with Configurable Blending

Strategy:
  1. Hybrid (default): Blend Ollama embeddings + keyword + TF-IDF
  2. Tier 1 only: Ollama embeddings (when available)
  3. Tier 2 only: TF-IDF + keyword ensemble
  4. Tier 3 fallback: Keyword-only (when no index)

Default blend: 0.5×embedding + 0.3×keyword + 0.2×tfidf
Fallback (Ollama down): Pure keyword (proven 80% accuracy)
"""

import json
import math
import re
import urllib.request
from collections import Counter
from pathlib import Path

TRAINING_PATH = Path(__file__).parent.parent / ".federation" / "training_data.json"
INDEX_PATH = Path(__file__).parent.parent / ".federation" / "tfidf_index.json"
EMBEDDING_CACHE = Path(__file__).parent.parent / ".federation" / "embeddings" / "ollama_index.json"

# --- Agent Configuration ---

# Minimum confidence thresholds per agent (tuned from confusion analysis)
AGENT_THRESHOLDS = {
    "kimi": 0.35,      # Lower threshold - kimi is the "doer", more permissive
    "claude": 0.45,    # Higher threshold - avoid claude→kimi confusion
    "copilot": 0.30,   # Lowest - copilot tasks are clear
    "codex": 0.40,     # Medium - codex has clear patterns
    "ollama": 0.50     # Highest - ollama most often confused with kimi
}

# Uncertainty routing: if confidence < threshold, route to fallback
FALLBACK_AGENT = "kimi"  # Default fallback for uncertain tasks

# Context window: remember last N routing decisions for consistency
CONTEXT_WINDOW_SIZE = 3

# --- Agent Taxonomy (5 agents) ---

AGENT_TAXONOMY = {
    "kimi": {
        "keywords": [
            "implement", "build", "deploy", "fix", "refactor", "test",
            "create", "install", "migrate", "debug", "execute", "run",
            "scaffold", "configure", "setup", "ci", "cd", "pipeline",
            "docker", "kubernetes", "infrastructure", "devops", "shell",
            "script", "automate", "endpoint", "api", "crud", "database",
            "parallel", "multiple files", "batch"
        ],
        "phrase_patterns": [
            "across multiple", "across all", "across three", "then implement",
            "then build", "integrate", "set up", "batch process", "then deploy"
        ],
        "negative_keywords": [
            "from scratch", "single module", "focused", "draft", "sketch",
            "brainstorm", "research", "analyze", "document", "compare",
            "evaluate trade", "deep dive", "summarize", "quick fix",
            "inline", "hint", "rename", "small change", "snippet"
        ],
        "weight": 1.0,
        "complexity_bias": "high"
    },
    "claude": {
        "keywords": [
            "research", "analyze", "document", "architecture", "design",
            "compare", "evaluate", "review", "deep dive", "explain",
            "summarize", "assess", "strategy", "plan", "rfc", "adr",
            "trade-off", "pros cons", "long-term", "security audit",
            "threat model", "literature", "specification", "whitepaper",
            "decision record", "technical debt"
        ],
        "phrase_patterns": [
            "evaluate trade", "pros and cons", "deep dive into", "compare vs",
            "assess the", "create a plan", "strategy for", "research into",
            "analyze the", "document the", "architecture decision",
            "comprehensive architecture", "assess technical", "debt and create"
        ],
        "negative_keywords": [
            "implement", "build", "deploy", "fix", "create", "migrate",
            "quick", "snippet", "inline", "draft", "sketch", "mock"
        ],
        "weight": 1.0,
        "complexity_bias": "high"
    },
    "copilot": {
        "keywords": [
            "review", "quick", "snippet", "complete", "suggest",
            "inline", "hint", "type", "rename", "extract", "refactor",
            "single file", "function", "class", "method", "variable",
            "format", "lint", "clean", "tidy", "small change"
        ],
        "phrase_patterns": [
            "quick fix", "small change", "rename the", "inline hint",
            "extract this", "complete this", "type definition", "format this",
            "clean up", "suggest improvement"
        ],
        "negative_keywords": [
            "across", "multiple", "all files", "entire", "architecture",
            "research", "analyze", "document", "deploy", "infrastructure",
            "design pattern", "strategy"
        ],
        "weight": 1.0,
        "complexity_bias": "low"
    },
    "codex": {
        "keywords": [
            "build", "implement", "feature", "module", "service", "endpoint",
            "autonomous", "end to end", "from scratch", "single module", "focused",
            "api", "crud", "websocket", "oauth", "payment", "migration",
            "middleware", "caching", "redis", "upload", "validation"
        ],
        "phrase_patterns": [
            "from scratch", "end to end", "single module", "focused module",
            "build the", "implement the", "create the", "module for",
            "service for", "autonomous implementation"
        ],
        "negative_keywords": [
            "across", "multiple", "then implement", "then build", "integrate",
            "research", "analyze", "quick fix", "inline", "draft", "sketch"
        ],
        "weight": 1.0,
        "complexity_bias": "medium"
    },
    "ollama": {
        "keywords": [
            "draft", "sketch", "prototype", "brainstorm", "iterate",
            "offline", "local", "fast", "quick draft", "rough",
            "experiment", "try", "mock", "stub", "placeholder",
            "template", "boilerplate", "generate ideas"
        ],
        "phrase_patterns": [
            "draft the", "sketch out", "brainstorm", "prototype of",
            "rough draft", "quick draft", "template for", "boilerplate",
            "mock the", "stub for", "placeholder for",
            "stub out", "generate ideas", "experiment with"
        ],
        "negative_keywords": [
            "implement", "build", "deploy", "fix", "migrate", "debug",
            "architecture", "research", "analyze", "end to end", "from scratch"
        ],
        "weight": 1.0,
        "complexity_bias": "low"
    }
}

# --- Stopwords ---

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "can", "shall",
    "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "and",
    "but", "or", "nor", "not", "so", "yet", "both", "either",
    "neither", "each", "every", "all", "any", "few", "more",
    "most", "other", "some", "such", "no", "only", "own", "same",
    "than", "too", "very", "just", "because", "if", "when", "it",
    "this", "that", "these", "those", "i", "me", "my", "we", "us"
}

# --- Ollama Embeddings (Tier 1) ---

def get_ollama_embedding(text: str, model: str = "mistral:latest") -> list[float] | None:
    """Get embedding from Ollama API. Returns None if unavailable."""
    try:
        req = urllib.request.Request(
            "http://localhost:11434/api/embeddings",
            data=json.dumps({"model": model, "prompt": text}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            return result.get("embedding")
    except Exception as e:
        return None


def get_ollama_similarities(task: str) -> dict[str, float] | None:
    """
    Get similarity scores from Ollama embeddings.
    Returns dict of agent -> similarity, or None if unavailable.
    """
    if not EMBEDDING_CACHE.exists():
        return None
    
    ollama_embedding = get_ollama_embedding(task)
    if not ollama_embedding:
        return None
    
    try:
        cache = json.loads(EMBEDDING_CACHE.read_text())
        similarities = []
        for item in cache.get("embeddings", []):
            sim = cosine_similarity_vectors(ollama_embedding, item["embedding"])
            similarities.append({"agent": item["agent"], "similarity": sim})
        
        if not similarities:
            return None
        
        # Aggregate by agent (average of top 3 per agent)
        agent_sims = {}
        for agent in AGENT_TAXONOMY:
            agent_scores = [s["similarity"] for s in similarities if s["agent"] == agent]
            if agent_scores:
                agent_scores.sort(reverse=True)
                agent_sims[agent] = sum(agent_scores[:3]) / min(3, len(agent_scores))
        
        # Normalize to 0-1
        max_sim = max(agent_sims.values()) if agent_sims else 1.0
        if max_sim > 0:
            agent_sims = {a: s / max_sim for a, s in agent_sims.items()}
        
        return agent_sims
    except Exception:
        return None


def cosine_similarity_vectors(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two dense vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# --- TF-IDF Engine (Tier 2) ---

def tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alpha, remove stopwords."""
    tokens = re.findall(r'[a-z]+', text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def build_tfidf_index(training_data: list[dict]) -> dict:
    """Build TF-IDF index from training data. Pure Python."""
    documents = []
    for item in training_data:
        tokens = tokenize(item["task"])
        documents.append({
            "task": item["task"],
            "agent": item["agent"],
            "tokens": tokens,
            "tf": Counter(tokens)
        })

    # Document frequency
    df = Counter()
    for doc in documents:
        for token in set(doc["tokens"]):
            df[token] += 1

    n_docs = len(documents)

    # IDF
    idf = {}
    for token, freq in df.items():
        idf[token] = math.log((n_docs + 1) / (freq + 1)) + 1

    # TF-IDF vectors
    for doc in documents:
        tfidf = {}
        max_tf = max(doc["tf"].values()) if doc["tf"] else 1
        for token, freq in doc["tf"].items():
            tf_norm = freq / max_tf
            tfidf[token] = tf_norm * idf.get(token, 1.0)
        doc["tfidf"] = tfidf

    index = {
        "idf": idf,
        "documents": [
            {"task": d["task"], "agent": d["agent"], "tfidf": d["tfidf"]}
            for d in documents
        ]
    }

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(index, indent=2))
    return index


def cosine_similarity_tfidf(vec_a: dict, vec_b: dict) -> float:
    """Cosine similarity between two sparse TF-IDF vectors."""
    common = set(vec_a.keys()) & set(vec_b.keys())
    if not common:
        return 0.0
    dot = sum(vec_a[k] * vec_b[k] for k in common)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def get_tfidf_scores(task: str, index: dict, top_k: int = 3) -> dict[str, float]:
    """Get TF-IDF similarity scores for each agent."""
    task_tokens = tokenize(task)
    task_tf = Counter(task_tokens)
    max_tf = max(task_tf.values()) if task_tf else 1
    task_tfidf = {
        t: (f / max_tf) * index["idf"].get(t, 1.0)
        for t, f in task_tf.items()
    }

    # Find top-k similar training samples
    similarities = []
    for doc in index["documents"]:
        sim = cosine_similarity_tfidf(task_tfidf, doc["tfidf"])
        similarities.append({"agent": doc["agent"], "similarity": sim})
    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    top_matches = similarities[:top_k]

    # Aggregate by agent
    tfidf_scores = Counter()
    for match in top_matches:
        tfidf_scores[match["agent"]] += match["similarity"]
    
    # Normalize
    total = sum(tfidf_scores.values()) or 1.0
    return {a: tfidf_scores.get(a, 0.0) / total for a in AGENT_TAXONOMY}


# --- Keyword & Complexity Scorers ---

def keyword_score(task: str, agent: str) -> float:
    """
    Score task against agent's keyword taxonomy.
    Includes phrase patterns (positive) and negative keywords (penalty).
    """
    task_lower = task.lower()
    taxonomy = AGENT_TAXONOMY.get(agent, {})
    keywords = taxonomy.get("keywords", [])
    phrases = taxonomy.get("phrase_patterns", [])
    negatives = taxonomy.get("negative_keywords", [])
    weight = taxonomy.get("weight", 1.0)

    # Base keyword hits
    hits = sum(1 for kw in keywords if kw in task_lower)
    
    # Phrase pattern bonus (stronger signal)
    phrase_hits = sum(2 for phrase in phrases if phrase in task_lower)
    
    # Negative keyword penalty
    penalty = sum(0.5 for neg in negatives if neg in task_lower)
    
    max_possible = max(len(keywords), 1)
    score = ((hits + phrase_hits) / max_possible) * weight - penalty
    return max(score, 0.0)  # Floor at 0


def get_keyword_scores(task: str) -> dict[str, float]:
    """Get normalized keyword scores for all agents."""
    scores = {a: keyword_score(task, a) for a in AGENT_TAXONOMY}
    total = sum(scores.values()) or 1.0
    return {a: s / total for a, s in scores.items()}


def complexity_score(task: str) -> str:
    """Estimate task complexity: low, medium, high."""
    indicators_high = [
        "across", "multiple", "all files", "refactor", "migrate",
        "architecture", "system", "infrastructure", "deploy",
        "research", "analyze", "deep dive", "comprehensive"
    ]
    indicators_low = [
        "quick", "simple", "single", "small", "rename", "typo",
        "format", "lint", "draft", "sketch", "snippet"
    ]

    task_lower = task.lower()
    high_hits = sum(1 for i in indicators_high if i in task_lower)
    low_hits = sum(1 for i in indicators_low if i in task_lower)
    word_count = len(task.split())

    if high_hits >= 2 or word_count > 20:
        return "high"
    elif low_hits >= 2 or word_count < 8:
        return "low"
    return "medium"


def complexity_match(task: str, agent: str) -> float:
    """Score how well task complexity matches agent's bias."""
    task_complexity = complexity_score(task)
    agent_bias = AGENT_TAXONOMY.get(agent, {}).get("complexity_bias", "medium")

    if task_complexity == agent_bias:
        return 0.2
    elif (task_complexity == "high" and agent_bias == "low") or \
         (task_complexity == "low" and agent_bias == "high"):
        return -0.1
    return 0.0


def get_complexity_scores(task: str) -> dict[str, float]:
    """Get complexity match scores for all agents."""
    return {a: complexity_match(task, a) for a in AGENT_TAXONOMY}


# --- Ensemble Router ---

def route(task: str, index: dict = None, top_k: int = 3, explain: bool = False,
          weights: tuple = None, use_ollama: bool = False, tier: str = "hybrid") -> dict:
    """
    Route a task to the best agent using hybrid Tier 1+2 scoring.
    
    Args:
        task: The task description to route
        index: Pre-built TF-IDF index (optional)
        top_k: Number of similar docs to consider for TF-IDF
        explain: Include detailed scoring breakdown
        weights: Custom blend weights (embedding, keyword, tfidf, complexity)
        use_ollama: Whether to query Ollama live (slow)
        tier: "hybrid" (default), "tier1", "tier2", or "tier3"
    
    Returns:
        dict with recommended_agent, confidence, method, tier, scores
    """
    # Default weights: hybrid blend
    if weights is None:
        if tier == "tier1":
            weights = (1.0, 0.0, 0.0, 0.0)  # Pure embedding
        elif tier == "tier2":
            weights = (0.0, 0.5, 0.3, 0.2)  # No embedding
        elif tier == "tier3":
            weights = (0.0, 1.0, 0.0, 0.0)  # Pure keyword
        else:  # hybrid
            # Phase 2: Reduced embedding influence for better disambiguation
            weights = (0.35, 0.45, 0.2, 0.0)  # 35% embed, 45% keyword, 20% tfidf
    
    w_embed, w_kw, w_tfidf, w_cx = weights
    
    # Load index if needed
    if index is None and w_tfidf > 0:
        if INDEX_PATH.exists():
            index = json.loads(INDEX_PATH.read_text())
        elif w_kw == 0 and w_embed == 0:
            # Fallback to tier 3 if no index and no other signals
            tier = "tier3"
            w_kw = 1.0
            w_tfidf = 0.0
    
    # Get all signal scores
    embed_scores = get_ollama_similarities(task) if w_embed > 0 else None
    kw_scores = get_keyword_scores(task) if w_kw > 0 else None
    tfidf_scores = get_tfidf_scores(task, index, top_k) if w_tfidf > 0 and index else None
    cx_scores = get_complexity_scores(task) if w_cx > 0 else None
    
    # Fallback: if Ollama fails but we wanted it, use pure keyword
    if w_embed > 0 and embed_scores is None:
        if w_kw > 0:
            # Demote to keyword-heavy blend
            w_embed = 0.0
            w_kw = 0.8
            w_tfidf = 0.2
            tier = "tier2-keyword-fallback"
        else:
            # Can't do anything without Ollama or keywords
            return {
                "recommended_agent": "kimi",
                "confidence": 0.0,
                "method": "fallback-error",
                "tier": "error",
                "error": "Ollama unavailable and no keyword signal"
            }
    
    # Blend scores
    final_scores = {}
    for agent in AGENT_TAXONOMY:
        score = 0.0
        if embed_scores:
            score += w_embed * embed_scores.get(agent, 0.0)
        if kw_scores:
            score += w_kw * kw_scores.get(agent, 0.0)
        if tfidf_scores:
            score += w_tfidf * tfidf_scores.get(agent, 0.0)
        if cx_scores:
            score += w_cx * cx_scores.get(agent, 0.0)
        final_scores[agent] = score
    
    winner = max(final_scores, key=final_scores.get)
    confidence = final_scores[winner]
    method_suffix = ""  # Default: no suffix
    
    # Apply agent-specific threshold
    threshold = AGENT_THRESHOLDS.get(winner, 0.4)
    
    # Check for uncertainty - if below threshold, use fallback
    if confidence < threshold:
        # Try second-best
        sorted_scores = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_scores) >= 2:
            second_agent, second_score = sorted_scores[1]
            # Use second if it meets its threshold and is close
            second_threshold = AGENT_THRESHOLDS.get(second_agent, 0.4)
            if second_score >= second_threshold and (confidence - second_score) < 0.1:
                winner = second_agent
                confidence = second_score
                method_suffix = "-threshold-adjusted"
            else:
                # Fall back to default
                winner = FALLBACK_AGENT
                confidence = final_scores.get(FALLBACK_AGENT, 0.3)
                method_suffix = "-fallback"
        else:
            winner = FALLBACK_AGENT
            confidence = final_scores.get(FALLBACK_AGENT, 0.3)
            method_suffix = "-fallback"
    
    result = {
        "recommended_agent": winner,
        "confidence": round(confidence, 4),
        "method": f"{tier}-ensemble{method_suffix}",
        "tier": tier,
        "weights": {
            "embedding": w_embed,
            "keyword": w_kw,
            "tfidf": w_tfidf,
            "complexity": w_cx
        },
        "scores": {a: round(s, 4) for a, s in sorted(
            final_scores.items(), key=lambda x: x[1], reverse=True
        )}
    }
    
    if explain:
        result["signals"] = {}
        if embed_scores:
            result["signals"]["embedding"] = {a: round(s, 4) for a, s in embed_scores.items()}
        if kw_scores:
            result["signals"]["keyword"] = {a: round(s, 4) for a, s in kw_scores.items()}
        if tfidf_scores:
            result["signals"]["tfidf"] = {a: round(s, 4) for a, s in tfidf_scores.items()}
        if cx_scores:
            result["signals"]["complexity"] = cx_scores
    
    return result


def route_all_tiers(task: str, index: dict = None) -> dict:
    """
    Route using all tiers and return comparison.
    Useful for debugging and tier comparison.
    """
    return {
        "task": task,
        "tier1": route(task, index=index, tier="tier1"),
        "tier2": route(task, index=index, tier="tier2"),
        "tier3": route(task, index=index, tier="tier3"),
        "hybrid": route(task, index=index, tier="hybrid")
    }


def build_embedding_cache():
    """Build Ollama embedding cache from training data."""
    if not TRAINING_PATH.exists():
        print(f"No training data at {TRAINING_PATH}")
        return False
    
    data = json.loads(TRAINING_PATH.read_text())
    cache = {"embeddings": []}
    
    print(f"Building embedding cache for {len(data)} samples...")
    for i, item in enumerate(data):
        emb = get_ollama_embedding(item["task"])
        if emb:
            cache["embeddings"].append({
                "task": item["task"],
                "agent": item["agent"],
                "embedding": emb
            })
            print(f"  [{i+1}/{len(data)}] ✓ {item['task'][:50]}...")
        else:
            print(f"  [{i+1}/{len(data)}] ✗ Ollama not available, skipping")
            return False
    
    EMBEDDING_CACHE.parent.mkdir(parents=True, exist_ok=True)
    EMBEDDING_CACHE.write_text(json.dumps(cache, indent=2))
    print(f"Cached {len(cache['embeddings'])} embeddings to {EMBEDDING_CACHE}")
    return True


# --- CLI ---

def main():
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Neural Router v3 — Hybrid Tier 1+2")
    parser.add_argument("task", nargs="?", help="Task description to route")
    parser.add_argument("--explain", action="store_true", help="Show detailed scoring")
    parser.add_argument("--build-index", action="store_true", help="Build TF-IDF index")
    parser.add_argument("--build-embeddings", action="store_true", help="Build Ollama cache")
    parser.add_argument("--compare-tiers", action="store_true", help="Compare all tiers side-by-side")
    parser.add_argument("--tier", choices=["tier1", "tier2", "tier3", "hybrid"], 
                       default="hybrid", help="Routing tier to use")
    parser.add_argument("--weights", type=str, help="Custom weights 'embed,kw,tfidf,cx' (e.g., '0.5,0.3,0.2,0')")
    
    args = parser.parse_args()

    if args.build_index:
        if not TRAINING_PATH.exists():
            print(f"No training data at {TRAINING_PATH}")
            sys.exit(1)
        data = json.loads(TRAINING_PATH.read_text())
        index = build_tfidf_index(data)
        print(f"Built TF-IDF index from {len(data)} samples → {INDEX_PATH}")
        return

    if args.build_embeddings:
        success = build_embedding_cache()
        sys.exit(0 if success else 1)

    if args.compare_tiers:
        if not args.task:
            print("Usage: python3 route_task_v3.py <task> --compare-tiers")
            sys.exit(1)
        
        # Load index for comparison
        index = None
        if INDEX_PATH.exists():
            index = json.loads(INDEX_PATH.read_text())
        
        results = route_all_tiers(args.task, index=index)
        
        print(f"\nTask: {results['task']}\n")
        print(f"{'Tier':<12} {'Agent':<10} {'Confidence':<12} {'Method'}")
        print("-" * 60)
        for tier_name in ["tier1", "tier2", "tier3", "hybrid"]:
            r = results[tier_name]
            print(f"{tier_name:<12} {r['recommended_agent']:<10} {r['confidence']:<12.4f} {r['method']}")
        
        # Show agreement
        agents = [results[t]["recommended_agent"] for t in ["tier1", "tier2", "tier3", "hybrid"]]
        if len(set(agents)) == 1:
            print(f"\n✅ All tiers agree: {agents[0]}")
        else:
            print(f"\n⚠️  Tiers disagree: {dict(zip(['tier1', 'tier2', 'tier3', 'hybrid'], agents))}")
        
        if args.explain:
            print("\n" + "=" * 60)
            print("HYBRID DETAILED BREAKDOWN")
            print("=" * 60)
            hybrid = results["hybrid"]
            if "signals" in hybrid:
                for signal, scores in hybrid["signals"].items():
                    print(f"\n{signal.upper()} signal:")
                    for agent, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
                        print(f"  {agent}: {score:.4f}")
        
        return

    if not args.task:
        parser.print_help()
        sys.exit(1)
    
    # Parse custom weights
    weights = None
    if args.weights:
        parts = [float(x) for x in args.weights.split(",")]
        if len(parts) == 4:
            weights = tuple(parts)
    
    # Load index if available
    index = None
    if INDEX_PATH.exists():
        index = json.loads(INDEX_PATH.read_text())
    
    result = route(args.task, index=index, explain=args.explain, 
                   weights=weights, tier=args.tier)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
