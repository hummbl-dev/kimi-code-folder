#!/usr/bin/env bash
#
# vote.sh - Federation Voting CLI
# Cast, tally, and manage federation votes.
#
# Usage:
#   vote.sh create <title> --proposer <agent> --type <standard|super|emergency|advisory>
#   vote.sh cast <proposal-id> --agent <name> --vote <yes|no|abstain> --confidence <0-1> --reason "..."
#   vote.sh status <proposal-id>
#   vote.sh list [--status <status>]
#   vote.sh tally <proposal-id>
#   vote.sh close <proposal-id>  # Admin only
#   vote.sh veto <proposal-id> --reason "..."  # Reuben only
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VOTING_DIR="${SCRIPT_DIR}"
PROPOSALS_DIR="${VOTING_DIR}/proposals"
COMPLETED_DIR="${VOTING_DIR}/completed"
ARCHIVE_DIR="${VOTING_DIR}/archive"

# Active agents in federation
ACTIVE_AGENTS=("claude" "kimi" "copilot")
REQUIRED_QUORUM=2  # Majority of 3

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────

log_info() {
    echo -e "${BLUE}ℹ️  ${1}${NC}"
}

log_success() {
    echo -e "${GREEN}✅ ${1}${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  ${1}${NC}"
}

log_error() {
    echo -e "${RED}❌ ${1}${NC}" >&2
}

get_next_proposal_id() {
    local date_str
    date_str=$(date +%Y-%m-%d)
    local count=1
    
    while [[ -f "${PROPOSALS_DIR}/FED-${date_str}-$(printf "%03d" $count).md" ]]; do
        ((count++))
    done
    
    echo "FED-${date_str}-$(printf "%03d" $count)"
}

validate_agent() {
    local agent="$1"
    for valid_agent in "${ACTIVE_AGENTS[@]}"; do
        if [[ "$agent" == "$valid_agent" ]]; then
            return 0
        fi
    done
    return 1
}

validate_vote() {
    local vote="$1"
    [[ "$vote" == "yes" || "$vote" == "no" || "$vote" == "abstain" ]]
}

get_proposal_path() {
    local proposal_id="$1"
    
    # Check proposals/
    if [[ -f "${PROPOSALS_DIR}/${proposal_id}.md" ]]; then
        echo "${PROPOSALS_DIR}/${proposal_id}.md"
        return 0
    fi
    
    # Check completed/
    if [[ -f "${COMPLETED_DIR}/${proposal_id}.md" ]]; then
        echo "${COMPLETED_DIR}/${proposal_id}.md"
        return 0
    fi
    
    # Check archive/
    if [[ -f "${ARCHIVE_DIR}/${proposal_id}.md" ]]; then
        echo "${ARCHIVE_DIR}/${proposal_id}.md"
        return 0
    fi
    
    return 1
}

extract_yaml_frontmatter() {
    local file="$1"
    local key="$2"
    grep "^${key}:" "$file" | head -1 | cut -d':' -f2- | sed 's/^ *//'
}

# ─────────────────────────────────────────────────────────────
# Command: create
# ─────────────────────────────────────────────────────────────

cmd_create() {
    local title=""
    local proposer=""
    local type="standard"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --proposer)
                proposer="$2"
                shift 2
                ;;
            --type)
                type="$2"
                shift 2
                ;;
            *)
                if [[ -z "$title" ]]; then
                    title="$1"
                fi
                shift
                ;;
        esac
    done
    
    # Validate
    if [[ -z "$title" ]]; then
        log_error "Title required"
        exit 1
    fi
    
    if [[ -z "$proposer" ]]; then
        log_error "Proposer required (--proposer <agent>)"
        exit 1
    fi
    
    if ! validate_agent "$proposer"; then
        log_error "Invalid agent: $proposer"
        exit 1
    fi
    
    if [[ ! "$type" =~ ^(standard|super|emergency|advisory)$ ]]; then
        log_error "Invalid type: $type (use: standard, super, emergency, advisory)"
        exit 1
    fi
    
    # Generate proposal ID
    local proposal_id
    proposal_id=$(get_next_proposal_id)
    
    # Calculate deadlines
    local created
    local review_deadline
    local vote_deadline
    created=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    review_deadline=$(date -u -v+24H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '+24 hours' +%Y-%m-%dT%H:%M:%SZ)
    
    case $type in
        standard)
            vote_deadline=$(date -u -v+48H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '+48 hours' +%Y-%m-%dT%H:%M:%SZ)
            ;;
        super)
            vote_deadline=$(date -u -v+72H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '+72 hours' +%Y-%m-%dT%H:%M:%SZ)
            ;;
        emergency)
            vote_deadline=$(date -u -v+4H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '+4 hours' +%Y-%m-%dT%H:%M:%SZ)
            ;;
        advisory)
            vote_deadline=$(date -u -v+96H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '+96 hours' +%Y-%m-%dT%H:%M:%SZ)
            ;;
    esac
    
    # Create proposal file
    local proposal_file="${PROPOSALS_DIR}/${proposal_id}.md"
    cp "${PROPOSALS_DIR}/TEMPLATE.md" "$proposal_file"
    
    # Update frontmatter
    sed -i.bak "s/proposal_id:.*/proposal_id: ${proposal_id}/" "$proposal_file"
    sed -i.bak "s/proposer:.*/proposer: ${proposer}/" "$proposal_file"
    sed -i.bak "s/type:.*/type: ${type}/" "$proposal_file"
    sed -i.bak "s/created:.*/created: ${created}/" "$proposal_file"
    sed -i.bak "s/review_deadline:.*/review_deadline: ${review_deadline}/" "$proposal_file"
    sed -i.bak "s/vote_deadline:.*/vote_deadline: ${vote_deadline}/" "$proposal_file"
    
    # Update title
    sed -i.bak "s/# Proposal: \[Title Here\]/# Proposal: ${title}/" "$proposal_file"
    
    rm -f "${proposal_file}.bak"
    
    log_success "Created proposal: ${proposal_id}"
    log_info "Title: ${title}"
    log_info "Proposer: ${proposer}"
    log_info "Type: ${type}"
    log_info "Review deadline: ${review_deadline}"
    log_info "Vote deadline: ${vote_deadline}"
    log_info "File: ${proposal_file}"
}

# ─────────────────────────────────────────────────────────────
# Command: cast
# ─────────────────────────────────────────────────────────────

cmd_cast() {
    local proposal_id="$1"
    shift
    
    local agent=""
    local vote=""
    local confidence=""
    local reason=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --agent)
                agent="$2"
                shift 2
                ;;
            --vote)
                vote="$2"
                shift 2
                ;;
            --confidence)
                confidence="$2"
                shift 2
                ;;
            --reason)
                reason="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    # Validate
    if ! validate_agent "$agent"; then
        log_error "Invalid agent: $agent"
        exit 1
    fi
    
    if ! validate_vote "$vote"; then
        log_error "Invalid vote: $vote (use: yes, no, abstain)"
        exit 1
    fi
    
    local proposal_file
    proposal_file=$(get_proposal_path "$proposal_id") || {
        log_error "Proposal not found: $proposal_id"
        exit 1
    }
    
    # Update proposal file with vote
    # This is a simple implementation - in production, use proper YAML parsing
    local vote_line="| ${agent} | ${vote} | ${confidence} | ${reason} |"
    
    # Add vote to table (replace empty row)
    sed -i.bak "/^|.*|.*|.*|.*|$/{
        s/^|.*|.*|.*|.*|$/|       |      |            |           |/
        n
        s/^|.*|.*|.*|.*|$/${vote_line}/
    }" "$proposal_file" 2>/dev/null || true
    
    rm -f "${proposal_file}.bak"
    
    log_success "Vote recorded: ${agent} voted ${vote} on ${proposal_id}"
    [[ -n "$reason" ]] && log_info "Reason: ${reason}"
}

# ─────────────────────────────────────────────────────────────
# Command: status
# ─────────────────────────────────────────────────────────────

cmd_status() {
    local proposal_id="$1"
    
    local proposal_file
    proposal_file=$(get_proposal_path "$proposal_id") || {
        log_error "Proposal not found: $proposal_id"
        exit 1
    }
    
    local status
    local proposer
    local type
    status=$(extract_yaml_frontmatter "$proposal_file" "status")
    proposer=$(extract_yaml_frontmatter "$proposal_file" "proposer")
    type=$(extract_yaml_frontmatter "$proposal_file" "type")
    
    echo "📋 Proposal: ${proposal_id}"
    echo "────────────────────────────────────"
    echo "Status: ${status}"
    echo "Proposer: ${proposer}"
    echo "Type: ${type}"
    echo ""
    
    # Count votes
    local yes_votes=0
    local no_votes=0
    local abstain_votes=0
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^\|.*\|.*yes.*\|.*\|.*\|$ ]]; then
            ((yes_votes++))
        elif [[ "$line" =~ ^\|.*\|.*no.*\|.*\|.*\|$ ]]; then
            ((no_votes++))
        elif [[ "$line" =~ ^\|.*\|.*abstain.*\|.*\|.*\|$ ]]; then
            ((abstain_votes++))
        fi
    done < <(grep "^|" "$proposal_file")
    
    local total=$((yes_votes + no_votes + abstain_votes))
    
    echo "Votes:"
    echo "  YES: ${yes_votes}"
    echo "  NO: ${no_votes}"
    echo "  ABSTAIN: ${abstain_votes}"
    echo "  TOTAL: ${total}/${REQUIRED_QUORUM} (quorum)"
    echo ""
    
    if [[ $total -ge $REQUIRED_QUORUM ]]; then
        if [[ $yes_votes -gt $no_votes ]]; then
            log_success "Current outcome: LIKELY PASS"
        elif [[ $yes_votes -lt $no_votes ]]; then
            log_warning "Current outcome: LIKELY REJECT"
        else
            log_warning "Current outcome: TIE"
        fi
    else
        log_warning "Quorum not yet met (${total}/${REQUIRED_QUORUM})"
    fi
}

# ─────────────────────────────────────────────────────────────
# Command: list
# ─────────────────────────────────────────────────────────────

cmd_list() {
    local filter_status=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --status)
                filter_status="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    echo "📋 Federation Proposals"
    echo "────────────────────────────────────"
    
    local found=0
    
    # List from proposals/
    if [[ -d "$PROPOSALS_DIR" ]]; then
        for file in "${PROPOSALS_DIR}"/*.md; do
            [[ -f "$file" ]] || continue
            [[ "$(basename "$file")" == "TEMPLATE.md" ]] && continue
            
            local proposal_id
            local status
            local title
            proposal_id=$(basename "$file" .md)
            status=$(extract_yaml_frontmatter "$file" "status")
            title=$(grep "^# Proposal:" "$file" | head -1 | sed 's/# Proposal: //')
            
            if [[ -z "$filter_status" || "$status" == "$filter_status" ]]; then
                echo ""
                echo "📝 ${proposal_id}"
                echo "   Status: ${status}"
                echo "   Title: ${title}"
                ((found++))
            fi
        done
    fi
    
    if [[ $found -eq 0 ]]; then
        log_info "No proposals found"
    else
        echo ""
        log_info "Total: ${found} proposal(s)"
    fi
}

# ─────────────────────────────────────────────────────────────
# Command: tally
# ─────────────────────────────────────────────────────────────

cmd_tally() {
    local proposal_id="$1"
    cmd_status "$proposal_id"
}

# ─────────────────────────────────────────────────────────────
# Command: close
# ─────────────────────────────────────────────────────────────

cmd_close() {
    local proposal_id="$1"
    
    local proposal_file
    proposal_file=$(get_proposal_path "$proposal_id") || {
        log_error "Proposal not found: $proposal_id"
        exit 1
    }
    
    # Determine outcome
    local yes_votes=0
    local no_votes=0
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^\|.*\|.*yes.*\|.*\|.*\|$ ]]; then
            ((yes_votes++))
        elif [[ "$line" =~ ^\|.*\|.*no.*\|.*\|.*\|$ ]]; then
            ((no_votes++))
        fi
    done < <(grep "^|" "$proposal_file")
    
    local new_status
    if [[ $yes_votes -gt $no_votes ]]; then
        new_status="passed"
        log_success "Proposal PASSED: ${proposal_id}"
    else
        new_status="rejected"
        log_warning "Proposal REJECTED: ${proposal_id}"
    fi
    
    # Update status
    sed -i.bak "s/status:.*/status: ${new_status}/" "$proposal_file"
    rm -f "${proposal_file}.bak"
    
    # Move to completed/
    mv "$proposal_file" "${COMPLETED_DIR}/"
    log_info "Moved to completed/${proposal_id}.md"
}

# ─────────────────────────────────────────────────────────────
# Command: veto (Reuben only)
# ─────────────────────────────────────────────────────────────

cmd_veto() {
    local proposal_id="$1"
    shift
    
    local reason=""
    while [[ $# -gt 0 ]]; do
        case $1 in
            --reason)
                reason="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    local proposal_file
    proposal_file=$(get_proposal_path "$proposal_id") || {
        log_error "Proposal not found: $proposal_id"
        exit 1
    }
    
    log_warning "VETO EXECUTED: ${proposal_id}"
    log_warning "By: Reuben (Human Authority)"
    [[ -n "$reason" ]] && log_warning "Reason: ${reason}"
    
    # Update status
    sed -i.bak "s/status:.*/status: vetoed/" "$proposal_file"
    
    # Add veto note to resolution section
    cat >> "$proposal_file" << EOF

## VETO NOTE

**Vetoed by:** Reuben
**Date:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Reason:** ${reason}

EOF
    
    rm -f "${proposal_file}.bak"
    
    # Move to completed/
    mv "$proposal_file" "${COMPLETED_DIR}/"
    log_info "Moved to completed/${proposal_id}.md"
}

# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

main() {
    if [[ $# -lt 1 ]]; then
        echo "Usage: vote.sh <command> [options]"
        echo ""
        echo "Commands:"
        echo "  create <title> --proposer <agent> [--type <type>]"
        echo "  cast <proposal-id> --agent <name> --vote <yes|no|abstain> [--confidence <0-1>] [--reason <text>]"
        echo "  status <proposal-id>"
        echo "  list [--status <status>]"
        echo "  tally <proposal-id>"
        echo "  close <proposal-id>  # Admin only"
        echo "  veto <proposal-id> --reason <text>  # Reuben only"
        echo ""
        exit 1
    fi
    
    local command="$1"
    shift
    
    case $command in
        create)
            cmd_create "$@"
            ;;
        cast)
            cmd_cast "$@"
            ;;
        status)
            cmd_status "$@"
            ;;
        list)
            cmd_list "$@"
            ;;
        tally)
            cmd_tally "$@"
            ;;
        close)
            cmd_close "$@"
            ;;
        veto)
            cmd_veto "$@"
            ;;
        *)
            log_error "Unknown command: $command"
            exit 1
            ;;
    esac
}

main "$@"
