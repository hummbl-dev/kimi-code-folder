#!/usr/bin/env bash
#
# fed-stats.sh - Federation Health & Metrics Dashboard
#
# Usage:
#   fed-stats.sh              # Quick status summary
#   fed-stats.sh --report     # Full dashboard report
#   fed-stats.sh --json       # Raw JSON metrics
#   fed-stats.sh --watch      # Live refresh every 30s
#   fed-stats.sh --indicator FHI-001  # Single indicator detail
#
# Outputs:
#   Console dashboard with health indicators, thresholds, and trends

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FED_DIR="${SCRIPT_DIR}/../.federation"
METRICS_DIR="${FED_DIR}/analytics/metrics"
STATE_FILE="${FED_DIR}/state/federation-state.json"
HEALTH_FILE="${METRICS_DIR}/health-indicators.json"
QUEUE_DIR="${FED_DIR}/queue"

# Colors
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────

print_header() {
    echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${BLUE}   FEDERATION HEALTH DASHBOARD${NC}"
    echo -e "${BOLD}${BLUE}   $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo
}

print_section() {
    echo -e "${BOLD}${CYAN}─── $1 ───${NC}"
}

get_queue_stats() {
    local pending=0
    local in_progress=0
    local completed=0

    if [[ -d "${QUEUE_DIR}/pending" ]]; then
        pending=$(find "${QUEUE_DIR}/pending" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
    fi
    if [[ -d "${QUEUE_DIR}/in_progress" ]]; then
        in_progress=$(find "${QUEUE_DIR}/in_progress" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
    fi
    if [[ -d "${QUEUE_DIR}/completed" ]]; then
        completed=$(find "${QUEUE_DIR}/completed" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
    fi

    echo "${pending}|${in_progress}|${completed}"
}

get_agent_status() {
    local agent="$1"
    if [[ -f "$STATE_FILE" ]]; then
        python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
    agents = state.get('agents', {})
    a = agents.get('$agent', {})
    status = a.get('status', 'unknown')
    emoji = {'active': '🟢', 'standby': '🟡', 'rate_limited': '🔴', 'unknown': '⚪'}.get(status, '⚪')
    print(f'{emoji} {status}')
" 2>/dev/null || echo "⚪ unknown"
    else
        echo "⚪ unknown"
    fi
}

calculate_health_score() {
    # Placeholder - returns mock score until real data exists
    # In production, this would read from metrics files
    local routing_acc="${1:-85}"
    local handoff_eff="${2:-90}"
    local throughput="${3:-75}"
    local cost_eff="${4:-70}"
    local balance="${5:-65}"

    # Weighted average
    local score=$(python3 -c "
score = ($routing_acc * 0.25) + ($handoff_eff * 0.25) + ($throughput * 0.20) + ($cost_eff * 0.15) + ($balance * 0.15)
print(f'{score:.1f}')
")
    echo "$score"
}

get_health_emoji() {
    local score="$1"
    if (( $(echo "$score >= 80" | bc -l) )); then
        echo "🟢"
    elif (( $(echo "$score >= 60" | bc -l) )); then
        echo "🟡"
    else
        echo "🔴"
    fi
}

format_indicator() {
    local name="$1"
    local value="$2"
    local threshold_min="$3"
    local threshold_warn="$4"
    local unit="${5:-%}"

    local color=""
    local emoji=""

    if (( $(echo "$value >= $threshold_min" | bc -l) )); then
        color="${GREEN}"
        emoji="🟢"
    elif (( $(echo "$value >= $threshold_warn" | bc -l) )); then
        color="${YELLOW}"
        emoji="🟡"
    else
        color="${RED}"
        emoji="🔴"
    fi

    # Use echo -e for proper color rendering
    local formatted_value
    formatted_value=$(printf "%6.1f" "$value")
    echo -e "  ${emoji} $(printf '%-22s' "$name") ${color}${formatted_value}${unit}${NC}"
}

# ─────────────────────────────────────────────────────────────
# Quick Status (default)
# ─────────────────────────────────────────────────────────────

quick_status() {
    echo -e "${BOLD}Federation Status${NC} | $(date '+%H:%M')"
    echo

    # Queue stats
    IFS='|' read -r pending in_progress completed <<< "$(get_queue_stats)"
    echo -e "Queue: ${YELLOW}${pending}${NC} pending | ${BLUE}${in_progress}${NC} active | ${GREEN}${completed}${NC} done"

    # Agent status (compact)
    echo -n "Agents: "
    for agent in copilot kimi claude ollama; do
        status=$(get_agent_status "$agent")
        emoji="${status%% *}"
        echo -n "${emoji} "
    done
    echo

    # Health score
    score=$(calculate_health_score)
    emoji=$(get_health_emoji "$score")
    echo -e "Health: ${emoji} ${score}%"
}

# ─────────────────────────────────────────────────────────────
# Full Report (--report)
# ─────────────────────────────────────────────────────────────

full_report() {
    print_header

    # ─── Overall Health Score ───
    print_section "FEDERATION HEALTH SCORE"
    echo

    local score=$(calculate_health_score)
    local emoji=$(get_health_emoji "$score")

    echo -e "  ${BOLD}${emoji} Overall Health: ${score}%${NC}"
    echo

    # Visual bar
    local bar_filled=$(python3 -c "print('█' * int($score / 5))")
    local bar_empty=$(python3 -c "print('░' * (20 - int($score / 5)))")
    echo -e "  [${GREEN}${bar_filled}${DIM}${bar_empty}${NC}] ${score}%"
    echo

    # ─── Health Indicators ───
    print_section "HEALTH INDICATORS"
    echo

    # Header
    printf "  %-26s %8s   %-12s\n" "Indicator" "Value" "Status"
    printf "  %-26s %8s   %-12s\n" "─────────────────────────" "────────" "──────"

    # Indicators (using placeholder values until real data)
    format_indicator "Routing Accuracy" "85.0" "85" "70" "%"
    format_indicator "Handoff Efficiency" "92.0" "90" "75" "%"
    format_indicator "Queue Throughput" "2.3" "2.0" "1.0" " t/h"
    format_indicator "Cost Efficiency" "68.0" "70" "50" "%"
    format_indicator "Agent Balance" "62.0" "60" "40" "%"
    echo

    # ─── Agent Status ───
    print_section "AGENT STATUS"
    echo
    printf "  %-12s %-15s %-20s\n" "Agent" "Status" "Location"
    printf "  %-12s %-15s %-20s\n" "──────" "──────" "────────"

    if [[ -f "$STATE_FILE" ]]; then
        python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
    agents = state.get('agents', {})
    for name, info in agents.items():
        status = info.get('status', 'unknown')
        location = info.get('location', 'unknown')
        emoji = {'active': '🟢', 'standby': '🟡', 'rate_limited': '🔴'}.get(status, '⚪')
        print(f'  {name:<12} {emoji} {status:<12} {location}')
" 2>/dev/null || echo "  (state file not found)"
    fi
    echo

    # ─── Queue Summary ───
    print_section "QUEUE SUMMARY"
    echo

    IFS='|' read -r pending in_progress completed <<< "$(get_queue_stats)"
    local total=$((pending + in_progress + completed))

    printf "  %-20s %5s\n" "Pending" "$pending"
    printf "  %-20s %5s\n" "In Progress" "$in_progress"
    printf "  %-20s %5s\n" "Completed (today)" "$completed"
    printf "  %-20s %5s\n" "──────────────────" "─────"
    printf "  ${BOLD}%-20s %5s${NC}\n" "Total" "$total"
    echo

    # ─── Cost Tracking ───
    print_section "COST TRACKING (Estimated)"
    echo
    printf "  %-12s %10s\n" "Agent" "Cost"
    printf "  %-12s %10s\n" "──────" "────────"
    printf "  %-12s %10s\n" "Copilot" "\$0.00"
    printf "  %-12s %10s\n" "Kimi" "\$0.15"
    printf "  %-12s %10s\n" "Claude" "\$0.50"
    printf "  %-12s %10s\n" "Ollama" "\$0.00"
    printf "  %-12s %10s\n" "──────" "────────"
    printf "  ${BOLD}%-12s %10s${NC}\n" "Total" "\$0.65"
    echo

    # ─── Threshold Reference ───
    print_section "THRESHOLD REFERENCE"
    echo
    echo -e "  ${GREEN}🟢 Healthy${NC}    Routing ≥85% | Handoff ≥90% | Throughput ≥2.0"
    echo -e "  ${YELLOW}🟡 Warning${NC}    Routing 70-84% | Handoff 75-89% | Throughput 1.0-1.9"
    echo -e "  ${RED}🔴 Critical${NC}   Routing <70% | Handoff <75% | Throughput <1.0"
    echo

    # ─── Recommendations ───
    print_section "RECOMMENDATIONS"
    echo

    # Check for issues and provide recommendations
    local issues=0

    # Cost efficiency warning (placeholder check)
    if (( $(echo "68.0 < 70" | bc -l) )); then
        echo -e "  ${YELLOW}⚠${NC}  Cost efficiency below target (68% < 70%)"
        echo -e "      → Consider using Ollama for draft tasks"
        ((issues++))
    fi

    # Agent balance warning (placeholder check)
    if (( $(echo "62.0 < 65" | bc -l) )); then
        echo -e "  ${YELLOW}⚠${NC}  Agent workload slightly imbalanced (62%)"
        echo -e "      → Kimi handling disproportionate share"
        ((issues++))
    fi

    if [[ $issues -eq 0 ]]; then
        echo -e "  ${GREEN}✓${NC}  No critical issues detected"
    fi
    echo

    # Footer
    echo -e "${DIM}───────────────────────────────────────────────────────────${NC}"
    echo -e "${DIM}  Generated by fed-stats.sh | Data: .federation/analytics/${NC}"
    echo -e "${DIM}  Run 'fed-stats.sh --json' for raw metrics${NC}"
}

# ─────────────────────────────────────────────────────────────
# JSON Output (--json)
# ─────────────────────────────────────────────────────────────

json_output() {
    IFS='|' read -r pending in_progress completed <<< "$(get_queue_stats)"

    cat <<EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "health_score": $(calculate_health_score),
  "indicators": {
    "routing_accuracy": {"value": 85.0, "status": "healthy", "threshold": 85},
    "handoff_efficiency": {"value": 92.0, "status": "healthy", "threshold": 90},
    "queue_throughput": {"value": 2.3, "status": "healthy", "threshold": 2.0},
    "cost_efficiency": {"value": 68.0, "status": "warning", "threshold": 70},
    "agent_balance": {"value": 62.0, "status": "healthy", "threshold": 60}
  },
  "queue": {
    "pending": $pending,
    "in_progress": $in_progress,
    "completed": $completed
  },
  "cost": {
    "total": 0.65,
    "by_agent": {"copilot": 0, "kimi": 0.15, "claude": 0.50, "ollama": 0}
  }
}
EOF
}

# ─────────────────────────────────────────────────────────────
# Watch Mode (--watch)
# ─────────────────────────────────────────────────────────────

watch_mode() {
    while true; do
        clear
        full_report
        echo -e "${DIM}  Refreshing in 30s... (Ctrl+C to exit)${NC}"
        sleep 30
    done
}

# ─────────────────────────────────────────────────────────────
# Single Indicator (--indicator)
# ─────────────────────────────────────────────────────────────

show_indicator() {
    local indicator_id="$1"

    if [[ ! -f "$HEALTH_FILE" ]]; then
        echo "Error: Health indicators file not found" >&2
        exit 1
    fi

    python3 -c "
import json
with open('$HEALTH_FILE') as f:
    data = json.load(f)

# Find indicator by ID or name
for key, ind in data.get('indicators', {}).items():
    if ind.get('id') == '$indicator_id' or key == '$indicator_id'.lower().replace('-', '_'):
        print(f\"Indicator: {ind['name']} ({ind['id']})\")
        print(f\"Description: {ind['description']}\")
        print(f\"Formula: {ind['formula']}\")
        print(f\"Unit: {ind['unit']}\")
        print()
        print('Thresholds:')
        for level, thresh in ind['thresholds'].items():
            label = thresh.get('label', level)
            if 'min' in thresh and 'max' in thresh:
                print(f\"  {label}: {thresh['min']} - {thresh['max']}\")
            elif 'min' in thresh:
                print(f\"  {label}: ≥ {thresh['min']}\")
            elif 'max' in thresh:
                print(f\"  {label}: < {thresh['max']}\")
            action = thresh.get('action', 'none')
            if action != 'none':
                print(f\"    Action: {action}\")
        exit(0)

print('Indicator not found: $indicator_id')
print('Available: FHI-001 (routing), FHI-002 (handoff), FHI-003 (throughput), FHI-004 (cost), FHI-005 (balance)')
exit(1)
"
}

# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

case "${1:-}" in
    --report)
        full_report
        ;;
    --json)
        json_output
        ;;
    --watch)
        watch_mode
        ;;
    --indicator)
        if [[ -z "${2:-}" ]]; then
            echo "Usage: fed-stats.sh --indicator FHI-001" >&2
            exit 1
        fi
        show_indicator "$2"
        ;;
    --help|-h)
        echo "Usage: fed-stats.sh [OPTIONS]"
        echo
        echo "Options:"
        echo "  (none)              Quick status summary"
        echo "  --report            Full dashboard report"
        echo "  --json              Raw JSON metrics"
        echo "  --watch             Live refresh every 30s"
        echo "  --indicator ID      Show single indicator (FHI-001 to FHI-005)"
        echo "  --help              This help message"
        echo
        echo "Health Indicators:"
        echo "  FHI-001  Routing Accuracy     (target: ≥85%)"
        echo "  FHI-002  Handoff Efficiency   (target: ≥90%)"
        echo "  FHI-003  Queue Throughput     (target: ≥2.0 tasks/hr)"
        echo "  FHI-004  Cost Efficiency      (target: ≥70%)"
        echo "  FHI-005  Agent Balance        (target: ≥60%)"
        ;;
    "")
        quick_status
        ;;
    *)
        echo "Unknown option: $1" >&2
        echo "Run 'fed-stats.sh --help' for usage" >&2
        exit 1
        ;;
esac
