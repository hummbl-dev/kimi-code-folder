#!/usr/bin/env python3
"""
Neural Router v3 — Enhanced Hybrid (Zero Cost, Zero External Deps)

Strategy:
  1. Ollama embeddings (Tier 1) — if available via localhost:11434
  2. TF-IDF similarity (Tier 2) — pure Python fallback
  3. Keyword taxonomy (Tier 3) — if no index exists

Ensemble: 40% TF-IDF + 40% keyword + 20% complexity
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
        "weight": 1.0,
        "complexity_bias": "high"
    },
    "claude": {
        "keywords": [
            "research", "analyze", "document", "architecture", "design",
            "compare", "evaluate", "review", "deep dive", "explain",
            "summarize", "assess", "strategy", "plan", "rfc", "adr",
            "trade-off", "pros cons", "long-term", "security audit",
            "threat model", "literature", "specification", "whitepaper"
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
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode())
            return result.get("embedding")
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

# --- Keyword & Complexity Scorers ---

def keyword_score(task: str, agent: str) -> float:
    """Score task against agent's keyword taxonomy."""
    task_lower = task.lower()
    taxonomy = AGENT_TAXONOMY.get(agent, {})
    keywords = taxonomy.get("keywords", [])
    weight = taxonomy.get("weight", 1.0)

    hits = sum(1 for kw in keywords if kw in task_lower)
    max_possible = max(len(keywords), 1)
    return (hits / max_possible) * weight

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

# --- Ensemble Router ---

def route(task: str, index: dict = None, top_k: int = 3, explain: bool = False) -> dict:
    """
    Route a task to the best agent using 3-signal ensemble.
    Tries Ollama embeddings first, falls back to TF-IDF, then keywords.
    """
    # Tier 1: Try Ollama embeddings
    ollama_embedding = get_ollama_embedding(task)
    if ollama_embedding and EMBEDDING_CACHE.exists():
        # Load cached embeddings and compare
        try:
            cache = json.loads(EMBEDDING_CACHE.read_text())
            similarities = []
            for item in cache.get("embeddings", []):
                sim = cosine_similarity_vectors(ollama_embedding, item["embedding"])
                similarities.append({"agent": item["agent"], "similarity": sim})
            
            if similarities:
                similarities.sort(key=lambda x: x["similarity"], reverse=True)
                top = similarities[0]
                return {
                    "recommended_agent": top["agent"],
                    "confidence": round(top["similarity"], 4),
                    "method": "ollama-embeddings-tier1",
                    "tier": 1
                }
        except Exception:
            pass  # Fall through to Tier 2

    # Tier 2: TF-IDF + ensemble
    if index is None:
        if INDEX_PATH.exists():
            index = json.loads(INDEX_PATH.read_text())
        else:
            # Tier 3: Keyword-only fallback
            scores = {}
            for agent in AGENT_TAXONOMY:
                kw = keyword_score(task, agent)
                cx = complexity_match(task, agent)
                scores[agent] = kw + cx
            winner = max(scores, key=scores.get)
            return {
                "recommended_agent": winner,
                "confidence": min(scores[winner], 1.0),
                "method": "keyword-only-tier3",
                "tier": 3,
                "scores": scores
            }

    # TF-IDF similarity
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
        similarities.append({"agent": doc["agent"], "task": doc["task"], "similarity": sim})
    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    top_matches = similarities[:top_k]

    # TF-IDF signal
    tfidf_scores = Counter()
    for match in top_matches:
        tfidf_scores[match["agent"]] += match["similarity"]
    total_sim = sum(tfidf_scores.values()) or 1.0
    tfidf_scores = {a: s / total_sim for a, s in tfidf_scores.items()}

    # Keyword signal
    kw_scores = {a: keyword_score(task, a) for a in AGENT_TAXONOMY}
    total_kw = sum(kw_scores.values()) or 1.0
    kw_scores = {a: s / total_kw for a, s in kw_scores.items()}

    # Complexity signal
    cx_scores = {a: complexity_match(task, a) for a in AGENT_TAXONOMY}

    # Ensemble: 40% TF-IDF + 40% keyword + 20% complexity
    final_scores = {}
    for agent in AGENT_TAXONOMY:
        tfidf = tfidf_scores.get(agent, 0.0)
        kw = kw_scores.get(agent, 0.0)
        cx = cx_scores.get(agent, 0.0)
        final_scores[agent] = (0.4 * tfidf) + (0.4 * kw) + (0.2 * cx)

    winner = max(final_scores, key=final_scores.get)
    confidence = final_scores[winner]

    result = {
        "recommended_agent": winner,
        "confidence": round(confidence, 4),
        "method": "ensemble-tfidf-tier2",
        "tier": 2,
        "scores": {a: round(s, 4) for a, s in sorted(
            final_scores.items(), key=lambda x: x[1], reverse=True
        )}
    }

    if explain:
        result["explanation"] = {
            "tfidf_signal": {a: round(s, 4) for a, s in tfidf_scores.items()},
            "keyword_signal": {a: round(s, 4) for a, s in kw_scores.items()},
            "complexity": complexity_score(task),
            "complexity_signal": cx_scores,
            "top_training_matches": top_matches[:3],
            "weights": "40% TF-IDF + 40% keyword + 20% complexity"
        }

    return result

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

    if len(sys.argv) < 2:
        print("Usage: python3 route_task_v3.py <task> [--explain] [--build-index] [--build-embeddings]")
        sys.exit(1)

    if "--build-index" in sys.argv:
        if not TRAINING_PATH.exists():
            print(f"No training data at {TRAINING_PATH}")
            sys.exit(1)
        data = json.loads(TRAINING_PATH.read_text())
        index = build_tfidf_index(data)
        print(f"Built TF-IDF index from {len(data)} samples → {INDEX_PATH}")
        return

    if "--build-embeddings" in sys.argv:
        success = build_embedding_cache()
        sys.exit(0 if success else 1)

    task = sys.argv[1]
    if task.startswith("--"):
        print("Usage: python3 route_task_v3.py <task> [--explain] [--build-index] [--build-embeddings]")
        sys.exit(1)
    
    explain = "--explain" in sys.argv

    result = route(task, explain=explain)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
