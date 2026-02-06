#!/usr/bin/env bash
#
# route-task.sh - Route a task to the best federation agent
#
# Usage:
#   route-task.sh "task description"
#   route-task.sh --json "task description"
#   route-task.sh --explain "task description"
#
# Examples:
#   route-task.sh "Research the Temporal Workflows library"
#   # → 📚 claude (0.95)
#
#   route-task.sh "Implement the auth middleware from Claude's design"
#   # → 🔧 kimi (0.95)
#
#   route-task.sh --explain "Pass this to kimi"
#   # → Detailed routing breakdown
#
# Configuration:
#   configs/federation-routing.yaml
#
# Dependencies:
#   - Python 3.8+
#   - PyYAML (pip install pyyaml)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/route_task.py"

# Check dependencies
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found" >&2
    exit 1
fi

if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "Error: route_task.py not found at $PYTHON_SCRIPT" >&2
    exit 1
fi

# Pass all arguments to Python script
python3 "$PYTHON_SCRIPT" "$@"
