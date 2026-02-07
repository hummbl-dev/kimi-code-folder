#!/usr/bin/env python3
"""
Day 4 — Step 1: Restore Codex samples + merge new adversarial data.

1. Restore 34 codex samples from dirty backup (Kimi remapped them to kimi — wrong)
2. Remove the kimi-remapped duplicates from current data
3. Merge 50 new adversarial samples (all 5 agents)
4. Deduplicate by task text
5. Rebuild TF-IDF index
"""
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent.parent
FED = ROOT / ".federation"
TRAINING = FED / "training_data.json"
BACKUP = FED / "training_data_dirty_backup.json"
NEW_SAMPLES = FED / "training_samples_day4_adversarial.json"
OUTPUT = TRAINING  # Overwrite current

def main():
    # --- Load current and backup ---
    current = json.loads(TRAINING.read_text())
    backup = json.loads(BACKUP.read_text())

    print(f"Current training data: {len(current)} samples")
    print(f"Dirty backup: {len(backup)} samples")

    # --- Extract codex samples from backup ---
    codex_samples = [s for s in backup if s.get("agent") == "codex" or s.get("expected_agent") == "codex"]
    print(f"Codex samples in backup: {len(codex_samples)}")

    # --- Remove kimi-remapped duplicates from current ---
    # These are samples where original_agent == "codex" but agent was changed to "kimi"
    remapped = [s for s in current if s.get("original_agent") == "codex"]
    print(f"Remapped codex→kimi samples in current: {len(remapped)}")
    
    # Keep everything in current EXCEPT the remapped ones
    clean_current = [s for s in current if s.get("original_agent") != "codex"]
    print(f"After removing remapped: {len(clean_current)} samples")

    # --- Normalize codex samples to standard format ---
    normalized_codex = []
    for s in codex_samples:
        normalized_codex.append({
            "task": s["task"],
            "agent": "codex"
        })

    # --- Load new adversarial samples ---
    if NEW_SAMPLES.exists():
        new_data = json.loads(NEW_SAMPLES.read_text())
        print(f"New adversarial samples: {len(new_data)}")
    else:
        new_data = []
        print("No new adversarial samples file found (will be created next)")

    # --- Merge all ---
    merged = clean_current + normalized_codex + new_data

    # --- Deduplicate by task text ---
    seen = set()
    deduped = []
    for s in merged:
        task_key = s["task"].strip().lower()
        if task_key not in seen:
            seen.add(task_key)
            deduped.append({"task": s["task"], "agent": s.get("agent", s.get("expected_agent", "unknown"))})

    print(f"\nMerged total: {len(merged)} → Deduped: {len(deduped)}")

    # --- Distribution ---
    dist = Counter(s["agent"] for s in deduped)
    print("\nAgent distribution:")
    for agent, count in sorted(dist.items()):
        print(f"  {agent}: {count}")

    # --- Save ---
    TRAINING.write_text(json.dumps(deduped, indent=2))
    print(f"\n✅ Saved {len(deduped)} samples to {TRAINING}")

    # --- Rebuild TF-IDF index ---
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from route_task_v3 import build_tfidf_index
    index = build_tfidf_index(deduped)
    print(f"✅ Rebuilt TF-IDF index ({len(index['documents'])} docs)")

if __name__ == "__main__":
    main()
