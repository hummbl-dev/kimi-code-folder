#!/usr/bin/env python3
"""
Resumable Ollama Embedding Cache Builder

Builds embedding cache incrementally, saving progress every N samples.
Safe to interrupt and resume — won't re-process already cached samples.
"""

import json
import urllib.request
from pathlib import Path
from datetime import datetime

TRAINING_PATH = Path(__file__).parent.parent / ".federation" / "training_data.json"
CACHE_PATH = Path(__file__).parent.parent / ".federation" / "embeddings" / "ollama_index.json"
PROGRESS_PATH = Path(__file__).parent.parent / ".federation" / "embeddings" / "build_progress.json"

OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL = "mistral:latest"
BATCH_SAVE_INTERVAL = 5  # Save progress every N samples


def get_ollama_embedding(text: str, timeout: int = 30) -> list[float] | None:
    """Get embedding from Ollama API."""
    try:
        req = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps({"model": MODEL, "prompt": text}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode())
            return result.get("embedding")
    except Exception as e:
        print(f"    Error: {e}")
        return None


def load_training_data() -> list[dict]:
    """Load training data."""
    if not TRAINING_PATH.exists():
        raise FileNotFoundError(f"Training data not found: {TRAINING_PATH}")
    return json.loads(TRAINING_PATH.read_text())


def load_existing_cache() -> dict:
    """Load existing cache or return empty structure."""
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except Exception:
            pass
    return {"embeddings": []}


def load_progress() -> dict:
    """Load build progress."""
    if PROGRESS_PATH.exists():
        try:
            return json.loads(PROGRESS_PATH.read_text())
        except Exception:
            pass
    return {"completed": [], "failed": [], "last_run": None}


def save_cache(cache: dict):
    """Save cache to disk."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2))


def save_progress(progress: dict):
    """Save progress to disk."""
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_PATH.write_text(json.dumps(progress, indent=2))


def build_cache(resume: bool = True, max_samples: int = None):
    """
    Build Ollama embedding cache with resumable progress.
    
    Args:
        resume: If True, skip already processed samples
        max_samples: Limit processing to N samples (for testing)
    """
    # Load data
    training_data = load_training_data()
    cache = load_existing_cache() if resume else {"embeddings": []}
    progress = load_progress() if resume else {"completed": [], "failed": [], "last_run": None}
    
    # Track completed tasks
    completed_tasks = {item["task"] for item in cache["embeddings"]}
    completed_tasks.update(progress.get("completed", []))
    
    # Filter to unprocessed samples
    to_process = [item for item in training_data if item["task"] not in completed_tasks]
    
    if max_samples:
        to_process = to_process[:max_samples]
    
    print(f"Ollama Embedding Cache Builder")
    print(f"=" * 50)
    print(f"Training samples: {len(training_data)}")
    print(f"Already cached: {len(completed_tasks)}")
    print(f"To process: {len(to_process)}")
    print(f"Model: {MODEL}")
    print(f"Estimated time: ~{len(to_process) * 15 // 60}m {len(to_process) * 15 % 60}s")
    print(f"=" * 50)
    
    if not to_process:
        print("\n✅ All samples already cached!")
        return
    
    # Process samples
    processed_count = 0
    new_embeddings = []
    
    for i, item in enumerate(to_process, 1):
        print(f"\n[{i}/{len(to_process)}] Processing: {item['task'][:50]}...")
        
        embedding = get_ollama_embedding(item["task"])
        
        if embedding:
            new_embeddings.append({
                "task": item["task"],
                "agent": item["agent"],
                "embedding": embedding
            })
            completed_tasks.add(item["task"])
            progress["completed"].append(item["task"])
            print(f"    ✓ Success ({len(embedding)} dims)")
        else:
            progress["failed"].append({
                "task": item["task"],
                "timestamp": datetime.utcnow().isoformat()
            })
            print(f"    ✗ Failed")
        
        processed_count += 1
        
        # Save progress periodically
        if processed_count % BATCH_SAVE_INTERVAL == 0:
            cache["embeddings"].extend(new_embeddings)
            save_cache(cache)
            save_progress(progress)
            new_embeddings = []
            print(f"    💾 Progress saved ({len(cache['embeddings'])} total cached)")
    
    # Final save
    if new_embeddings:
        cache["embeddings"].extend(new_embeddings)
    
    progress["last_run"] = datetime.utcnow().isoformat()
    save_cache(cache)
    save_progress(progress)
    
    print(f"\n{'=' * 50}")
    print(f"✅ Build complete!")
    print(f"Total cached: {len(cache['embeddings'])}")
    print(f"Failed: {len(progress['failed'])}")
    print(f"Cache file: {CACHE_PATH}")


def status():
    """Show cache status."""
    training_data = load_training_data()
    cache = load_existing_cache()
    progress = load_progress()
    
    completed = {item["task"] for item in cache["embeddings"]}
    failed = {f["task"] for f in progress.get("failed", [])}
    pending = [item for item in training_data if item["task"] not in completed and item["task"] not in failed]
    
    print(f"Cache Status")
    print(f"=" * 50)
    print(f"Training samples: {len(training_data)}")
    print(f"Cached: {len(completed)}")
    print(f"Failed: {len(failed)}")
    print(f"Pending: {len(pending)}")
    
    # Per-agent breakdown
    agent_counts = {}
    for item in cache["embeddings"]:
        agent = item["agent"]
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
    
    print(f"\nCached by agent:")
    for agent in sorted(agent_counts.keys()):
        print(f"  {agent}: {agent_counts[agent]}")
    
    if progress.get("last_run"):
        print(f"\nLast build: {progress['last_run']}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build Ollama embedding cache")
    parser.add_argument("--resume", action="store_true", default=True, help="Resume from previous progress (default)")
    parser.add_argument("--restart", action="store_true", help="Start fresh, ignore existing cache")
    parser.add_argument("--max-samples", type=int, help="Process only N samples (for testing)")
    parser.add_argument("--status", action="store_true", help="Show cache status")
    args = parser.parse_args()
    
    if args.status:
        status()
        return
    
    resume = not args.restart
    build_cache(resume=resume, max_samples=args.max_samples)


if __name__ == "__main__":
    main()
