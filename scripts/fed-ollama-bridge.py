#!/usr/bin/env python3
"""
Ollama Bridge for Federation
Enables local model inference for low-stakes tasks.

Usage:
    fed-ollama-bridge.py --task "quick draft"
    fed-ollama-bridge.py --prompt "Generate 3 function names for auth"
    fed-ollama-bridge.py --status

Requires:
    - Ollama running locally (ollama serve)
    - qwen2.5-coder:7b model pulled (ollama pull qwen2.5-coder:7b)
"""

import argparse
import json
import sys
import subprocess
import time
from pathlib import Path

# Configuration
OLLAMA_MODEL = "qwen2.5-coder:7b"
FEDERATION_DIR = Path(__file__).parent.parent / ".federation"


def check_ollama_status():
    """Check if Ollama is running and model is available."""
    try:
        # Check if ollama is running
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return {"running": False, "error": "Ollama not responding"}
        
        data = json.loads(result.stdout)
        models = [m["name"] for m in data.get("models", [])]
        
        return {
            "running": True,
            "models": models,
            "target_model": OLLAMA_MODEL,
            "target_available": OLLAMA_MODEL in models
        }
    
    except Exception as e:
        return {"running": False, "error": str(e)}


def query_ollama(prompt: str, timeout: int = 60) -> dict:
    """Query Ollama with a prompt."""
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        start_time = time.time()
        
        result = subprocess.run(
            ["curl", "-s", "-X", "POST",
             "http://localhost:11434/api/generate",
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"curl failed: {result.stderr}",
                "elapsed_seconds": elapsed
            }
        
        data = json.loads(result.stdout)
        
        return {
            "success": True,
            "response": data.get("response", ""),
            "elapsed_seconds": round(elapsed, 2),
            "model": OLLAMA_MODEL,
            "tokens": data.get("eval_count", 0)
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Timeout after {timeout}s",
            "elapsed_seconds": timeout
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "elapsed_seconds": None
        }


def route_via_ollama(task_description: str) -> dict:
    """Route a simple task to Ollama for quick processing."""
    
    # Check if task is suitable for Ollama
    suitable_keywords = ["draft", "sketch", "rough", "quick", "outline", "brainstorm"]
    is_suitable = any(kw in task_description.lower() for kw in suitable_keywords)
    
    if not is_suitable:
        return {
            "success": False,
            "routed": False,
            "reason": "Task not suitable for local model (no 'draft/quick/rough' keywords)",
            "recommendation": "Use Kimi or Claude for this task"
        }
    
    # Build prompt
    prompt = f"""You are a helpful coding assistant. The user asks:

"{task_description}"

Provide a quick, rough response. Don't worry about perfection.
"""
    
    result = query_ollama(prompt)
    result["routed"] = True
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Ollama Bridge for Federation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fed-ollama-bridge.py --status
  fed-ollama-bridge.py --prompt "List 3 pros of TypeScript"
  fed-ollama-bridge.py --task "Draft a README outline"
        """
    )
    
    parser.add_argument("--status", action="store_true", help="Check Ollama status")
    parser.add_argument("--prompt", help="Send a prompt to Ollama")
    parser.add_argument("--task", help="Route a task to Ollama")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds")
    
    args = parser.parse_args()
    
    if not any([args.status, args.prompt, args.task]):
        parser.print_help()
        sys.exit(1)
    
    # Status check
    if args.status:
        status = check_ollama_status()
        
        if status["running"]:
            print("🟢 Ollama is running")
            print(f"   Available models: {', '.join(status['models'])}")
            
            if status["target_available"]:
                print(f"   ✅ Target model '{OLLAMA_MODEL}' is available")
            else:
                print(f"   ⚠️  Target model '{OLLAMA_MODEL}' NOT found")
                print(f"   Run: ollama pull {OLLAMA_MODEL}")
        else:
            print("🔴 Ollama is not running")
            print(f"   Error: {status.get('error', 'Unknown')}")
            print("   Start with: ollama serve")
        
        return
    
    # Check Ollama is available first
    status = check_ollama_status()
    if not status["running"]:
        print("Error: Ollama is not running", file=sys.stderr)
        print("Start with: ollama serve", file=sys.stderr)
        sys.exit(1)
    
    if not status["target_available"]:
        print(f"Error: Model {OLLAMA_MODEL} not found", file=sys.stderr)
        print(f"Pull with: ollama pull {OLLAMA_MODEL}", file=sys.stderr)
        sys.exit(1)
    
    # Direct prompt
    if args.prompt:
        print(f"🔄 Querying {OLLAMA_MODEL}...")
        result = query_ollama(args.prompt, timeout=args.timeout)
        
        if result["success"]:
            print(f"✅ Response ({result['elapsed_seconds']}s, {result['tokens']} tokens):")
            print("-" * 60)
            print(result["response"])
            print("-" * 60)
        else:
            print(f"❌ Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
    
    # Task routing
    if args.task:
        print(f"🔄 Routing task to Ollama: {args.task[:50]}...")
        result = route_via_ollama(args.task)
        
        if not result.get("routed"):
            print(f"⚠️  {result['reason']}")
            print(f"   Recommendation: {result['recommendation']}")
            sys.exit(1)
        
        if result["success"]:
            print(f"✅ Task completed ({result['elapsed_seconds']}s, {result['tokens']} tokens)")
            print("-" * 60)
            print(result["response"])
            print("-" * 60)
            print("\n⚠️  This is a draft from local model. Consider review before use.")
        else:
            print(f"❌ Error: {result['error']}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
