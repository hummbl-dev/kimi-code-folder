#!/usr/bin/env python3
"""
Federation Voting System
Phase 4 Sprint 3: Agent Voting on Decisions

Usage:
    fed-vote.py create "Question to vote on" --context <path> [--deadline <hours>]
    fed-vote.py vote <vote-id> --agent <name> --choice <option> --confidence <0-1> --reasoning "..."
    fed-vote.py status <vote-id>
    fed-vote.py resolve <vote-id>
    fed-vote.py list [--status active|resolved|escalated]
    fed-vote.py escalate <vote-id> --reason "..."

Examples:
    fed-vote.py create "Use Next.js App Router or Pages Router?" --context docs/decisions/routing.md
    fed-vote.py vote vote-20260205-001 --agent claude --choice "app-router" --confidence 0.85 --reasoning "Better SSR support"
    fed-vote.py resolve vote-20260205-001
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
FEDERATION_DIR = SCRIPT_DIR.parent / ".federation"
VOTES_DIR = FEDERATION_DIR / "votes"
ACTIVE_VOTES_DIR = VOTES_DIR / "active"
RESOLVED_VOTES_DIR = VOTES_DIR / "resolved"
ESCALATED_VOTES_DIR = VOTES_DIR / "escalated"
STATE_FILE = FEDERATION_DIR / "state" / "federation-state.json"

# Voting rules from Phase 4 spec
MIN_VOTERS = 2
CONFIDENCE_THRESHOLD = 0.70
DEFAULT_DEADLINE_HOURS = 24


# ─────────────────────────────────────────────────────────────
# Voting System
# ─────────────────────────────────────────────────────────────

class VotingSystem:
    """Manages agent voting on federation decisions."""
    
    def __init__(self):
        self._ensure_directories()
        self.agents = self._load_agents()
    
    def _ensure_directories(self):
        """Create vote directories if they don't exist."""
        for dir_path in [ACTIVE_VOTES_DIR, RESOLVED_VOTES_DIR, ESCALATED_VOTES_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _load_agents(self) -> Dict:
        """Load registered agents from federation state."""
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                state = json.load(f)
                return state.get("agents", {})
        return {}
    
    def _generate_vote_id(self) -> str:
        """Generate unique vote ID."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        # Count existing votes today for sequence
        today_prefix = datetime.now().strftime("vote-%Y%m%d-")
        existing = list(ACTIVE_VOTES_DIR.glob(f"{today_prefix}*.json"))
        seq = len(existing) + 1
        return f"vote-{timestamp}-{seq:04d}"
    
    def _load_vote(self, vote_id: str) -> Optional[Dict]:
        """Load vote from any status directory."""
        for dir_path in [ACTIVE_VOTES_DIR, RESOLVED_VOTES_DIR, ESCALATED_VOTES_DIR]:
            vote_file = dir_path / f"{vote_id}.json"
            if vote_file.exists():
                with open(vote_file) as f:
                    return json.load(f)
        return None
    
    def _save_vote(self, vote: Dict, directory: Path):
        """Save vote to specified directory."""
        vote_file = directory / f"{vote['vote_id']}.json"
        with open(vote_file, 'w') as f:
            json.dump(vote, f, indent=2)
    
    def create_vote(self, question: str, context_path: Optional[str] = None,
                    deadline_hours: int = DEFAULT_DEADLINE_HOURS) -> Dict:
        """Create a new vote."""
        vote_id = self._generate_vote_id()
        deadline = datetime.now() + timedelta(hours=deadline_hours)
        
        vote = {
            "vote_id": vote_id,
            "question": question,
            "context_path": context_path,
            "created_at": datetime.now().isoformat(),
            "deadline": deadline.isoformat(),
            "status": "active",
            "votes": {},
            "result": None,
            "escalation_reason": None,
            "metadata": {
                "min_voters": MIN_VOTERS,
                "confidence_threshold": CONFIDENCE_THRESHOLD,
                "created_by": "reuben",  # Default, could be agent
            }
        }
        
        self._save_vote(vote, ACTIVE_VOTES_DIR)
        return vote
    
    def cast_vote(self, vote_id: str, agent: str, choice: str, 
                  confidence: float, reasoning: str) -> Dict:
        """Cast a vote from an agent."""
        vote = self._load_vote(vote_id)
        if not vote:
            raise ValueError(f"Vote {vote_id} not found")
        
        if vote["status"] != "active":
            raise ValueError(f"Vote {vote_id} is not active (status: {vote['status']})")
        
        # Validate agent
        if agent not in self.agents:
            raise ValueError(f"Unknown agent: {agent}. Registered: {list(self.agents.keys())}")
        
        # Validate confidence
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {confidence}")
        
        # Check deadline
        deadline = datetime.fromisoformat(vote["deadline"])
        if datetime.now() > deadline:
            raise ValueError(f"Vote {vote_id} deadline has passed")
        
        vote["votes"][agent] = {
            "choice": choice,
            "confidence": confidence,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat()
        }
        
        self._save_vote(vote, ACTIVE_VOTES_DIR)
        return vote
    
    def resolve_vote(self, vote_id: str, force: bool = False) -> Dict:
        """Resolve a vote and determine the outcome."""
        vote = self._load_vote(vote_id)
        if not vote:
            raise ValueError(f"Vote {vote_id} not found")
        
        if vote["status"] != "active":
            raise ValueError(f"Vote {vote_id} already resolved")
        
        votes = vote["votes"]
        
        # Check minimum voters
        if len(votes) < MIN_VOTERS and not force:
            raise ValueError(
                f"Need at least {MIN_VOTERS} votes, have {len(votes)}. "
                f"Use --force to override."
            )
        
        # Count choices
        choices: Dict[str, List[Dict]] = {}
        for agent, vote_data in votes.items():
            choice = vote_data["choice"]
            if choice not in choices:
                choices[choice] = []
            choices[choice].append({"agent": agent, **vote_data})
        
        # Check for low confidence votes
        low_confidence = any(
            v["confidence"] < CONFIDENCE_THRESHOLD 
            for v in votes.values()
        )
        
        # Determine winner
        if len(choices) == 0:
            result = {"outcome": "escalate", "reason": "No votes cast"}
        elif len(choices) == 1 and not low_confidence:
            # Unanimous
            winner = list(choices.keys())[0]
            result = {
                "outcome": "decided",
                "winner": winner,
                "votes_for": len(choices[winner]),
                "method": "unanimous"
            }
        else:
            # WEIGHTED CONFIDENCE: Sum confidence scores per choice
            weighted_scores = {}
            for choice, voters in choices.items():
                weighted_scores[choice] = sum(v["confidence"] for v in voters)
            
            total_weight = sum(weighted_scores.values())
            max_weight = max(weighted_scores.values())
            winners = [c for c, w in weighted_scores.items() if w == max_weight]
            
            if len(winners) > 1:
                # Tie (even with weighted confidence)
                result = {
                    "outcome": "escalate",
                    "reason": f"Weighted tie between: {', '.join(winners)}",
                    "tie": winners,
                    "weighted_scores": {c: round(s, 2) for c, s in weighted_scores.items()}
                }
            elif low_confidence:
                # Winner but low confidence in some votes
                winner = winners[0]
                result = {
                    "outcome": "escalate",
                    "reason": "Low confidence vote(s) detected",
                    "winner": winner,
                    "weighted_score": round(max_weight, 2),
                    "weighted_scores": {c: round(s, 2) for c, s in weighted_scores.items()}
                }
            else:
                # Clear winner by weighted confidence
                winner = winners[0]
                winner_confidence = weighted_scores[winner] / total_weight if total_weight > 0 else 0
                result = {
                    "outcome": "decided",
                    "winner": winner,
                    "weighted_score": round(max_weight, 2),
                    "total_weight": round(total_weight, 2),
                    "confidence_percentage": round(winner_confidence * 100, 1),
                    "method": "weighted_confidence"
                }
        
        # Update vote
        vote["result"] = result
        vote["resolved_at"] = datetime.now().isoformat()
        
        if result["outcome"] == "escalate":
            vote["status"] = "escalated"
            self._save_vote(vote, ESCALATED_VOTES_DIR)
            # Remove from active
            (ACTIVE_VOTES_DIR / f"{vote_id}.json").unlink(missing_ok=True)
        else:
            vote["status"] = "resolved"
            self._save_vote(vote, RESOLVED_VOTES_DIR)
            # Remove from active
            (ACTIVE_VOTES_DIR / f"{vote_id}.json").unlink(missing_ok=True)
        
        return vote
    
    def escalate_vote(self, vote_id: str, reason: str) -> Dict:
        """Manually escalate a vote to Reuben."""
        vote = self._load_vote(vote_id)
        if not vote:
            raise ValueError(f"Vote {vote_id} not found")
        
        vote["status"] = "escalated"
        vote["escalation_reason"] = reason
        vote["escalated_at"] = datetime.now().isoformat()
        
        self._save_vote(vote, ESCALATED_VOTES_DIR)
        (ACTIVE_VOTES_DIR / f"{vote_id}.json").unlink(missing_ok=True)
        
        return vote
    
    def get_vote_status(self, vote_id: str) -> Dict:
        """Get detailed status of a vote."""
        vote = self._load_vote(vote_id)
        if not vote:
            raise ValueError(f"Vote {vote_id} not found")
        
        # Calculate time remaining
        deadline = datetime.fromisoformat(vote["deadline"])
        now = datetime.now()
        time_remaining = deadline - now
        
        status = {
            "vote_id": vote["vote_id"],
            "question": vote["question"],
            "status": vote["status"],
            "votes_cast": len(vote["votes"]),
            "min_required": MIN_VOTERS,
            "deadline": vote["deadline"],
            "time_remaining_hours": max(0, time_remaining.total_seconds() / 3600),
            "votes": vote["votes"],
            "result": vote.get("result")
        }
        
        return status
    
    def list_votes(self, status_filter: Optional[str] = None) -> List[Dict]:
        """List all votes with optional status filter."""
        votes = []
        
        directories = {
            "active": ACTIVE_VOTES_DIR,
            "resolved": RESOLVED_VOTES_DIR,
            "escalated": ESCALATED_VOTES_DIR
        }
        
        if status_filter:
            if status_filter not in directories:
                raise ValueError(f"Invalid status: {status_filter}")
            dirs_to_check = {status_filter: directories[status_filter]}
        else:
            dirs_to_check = directories
        
        for status, dir_path in dirs_to_check.items():
            for vote_file in dir_path.glob("vote-*.json"):
                with open(vote_file) as f:
                    vote = json.load(f)
                    votes.append({
                        "vote_id": vote["vote_id"],
                        "question": vote["question"][:50] + "..." if len(vote["question"]) > 50 else vote["question"],
                        "status": vote["status"],
                        "votes_cast": len(vote["votes"]),
                        "created_at": vote["created_at"],
                        "deadline": vote["deadline"]
                    })
        
        return sorted(votes, key=lambda x: x["created_at"], reverse=True)


# ─────────────────────────────────────────────────────────────
# CLI Interface
# ─────────────────────────────────────────────────────────────

def format_vote_status(status: Dict) -> str:
    """Format vote status for display."""
    lines = [
        f"Vote: {status['vote_id']}",
        f"Question: {status['question']}",
        f"Status: {status['status'].upper()}",
        f"Votes: {status['votes_cast']}/{status['min_required']} required",
        f"Time Remaining: {status['time_remaining_hours']:.1f} hours",
        ""
    ]
    
    if status['votes']:
        lines.append("Cast Votes:")
        for agent, vote in status['votes'].items():
            conf_emoji = "✅" if vote['confidence'] >= CONFIDENCE_THRESHOLD else "⚠️"
            lines.append(f"  {agent}: {vote['choice']} {conf_emoji} ({vote['confidence']:.0%})")
            lines.append(f"    \"{vote['reasoning'][:60]}...\"")
    
    if status['result']:
        lines.append("")
        lines.append(f"Result: {status['result']['outcome'].upper()}")
        if 'winner' in status['result']:
            lines.append(f"Winner: {status['result']['winner']}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Federation Voting System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fed-vote.py create "Use App Router or Pages Router?" --context docs/routing.md
  fed-vote.py vote vote-20260205-001 --agent claude --choice "app-router" --confidence 0.85 --reasoning "Better SSR"
  fed-vote.py status vote-20260205-001
  fed-vote.py resolve vote-20260205-001
  fed-vote.py list --status active
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Create
    create_parser = subparsers.add_parser('create', help='Create a new vote')
    create_parser.add_argument('question', help='Question to vote on')
    create_parser.add_argument('--context', help='Path to context document')
    create_parser.add_argument('--deadline', type=int, default=DEFAULT_DEADLINE_HOURS,
                               help=f'Deadline in hours (default: {DEFAULT_DEADLINE_HOURS})')
    
    # Vote
    vote_parser = subparsers.add_parser('vote', help='Cast a vote')
    vote_parser.add_argument('vote_id', help='Vote ID')
    vote_parser.add_argument('--agent', required=True, help='Agent name')
    vote_parser.add_argument('--choice', required=True, help='Choice/option')
    vote_parser.add_argument('--confidence', type=float, required=True, help='Confidence 0.0-1.0')
    vote_parser.add_argument('--reasoning', required=True, help='Reasoning for vote')
    
    # Status
    status_parser = subparsers.add_parser('status', help='Show vote status')
    status_parser.add_argument('vote_id', help='Vote ID')
    
    # Resolve
    resolve_parser = subparsers.add_parser('resolve', help='Resolve a vote')
    resolve_parser.add_argument('vote_id', help='Vote ID')
    resolve_parser.add_argument('--force', action='store_true', help='Force resolution despite min voters')
    
    # List
    list_parser = subparsers.add_parser('list', help='List votes')
    list_parser.add_argument('--status', choices=['active', 'resolved', 'escalated'],
                             help='Filter by status')
    
    # Escalate
    escalate_parser = subparsers.add_parser('escalate', help='Escalate vote to Reuben')
    escalate_parser.add_argument('vote_id', help='Vote ID')
    escalate_parser.add_argument('--reason', required=True, help='Escalation reason')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        voting = VotingSystem()
        
        if args.command == 'create':
            vote = voting.create_vote(args.question, args.context, args.deadline)
            print(f"✅ Vote created: {vote['vote_id']}")
            print(f"   Question: {vote['question']}")
            print(f"   Deadline: {vote['deadline']}")
            print(f"\n   Agents can vote with:")
            print(f"   fed-vote.py vote {vote['vote_id']} --agent <name> --choice <option> --confidence <0-1> --reasoning \"...\"")
        
        elif args.command == 'vote':
            vote = voting.cast_vote(args.vote_id, args.agent, args.choice, 
                                    args.confidence, args.reasoning)
            print(f"✅ {args.agent} voted for '{args.choice}' ({args.confidence:.0%} confidence)")
            print(f"   Total votes: {len(vote['votes'])}")
        
        elif args.command == 'status':
            status = voting.get_vote_status(args.vote_id)
            print(format_vote_status(status))
        
        elif args.command == 'resolve':
            vote = voting.resolve_vote(args.vote_id, args.force)
            result = vote['result']
            
            if result['outcome'] == 'decided':
                print(f"✅ Vote resolved: {result['winner']}")
                print(f"   Method: {result['method']}")
                print(f"   Votes: {result.get('votes_for', 'N/A')}")
            else:
                print(f"⚠️  Vote escalated to Reuben")
                print(f"   Reason: {result['reason']}")
        
        elif args.command == 'list':
            votes = voting.list_votes(args.status)
            if not votes:
                print("No votes found.")
            else:
                print(f"{'Vote ID':<25} {'Status':<12} {'Votes':<8} {'Question':<40}")
                print("-" * 90)
                for v in votes:
                    short_id = v['vote_id'][:24]
                    q = v['question'][:38] + "..." if len(v['question']) > 40 else v['question']
                    print(f"{short_id:<25} {v['status']:<12} {v['votes_cast']}/{v.get('min_required', MIN_VOTERS):<5} {q}")
        
        elif args.command == 'escalate':
            vote = voting.escalate_vote(args.vote_id, args.reason)
            print(f"⚠️  Vote {args.vote_id} escalated to Reuben")
            print(f"   Reason: {args.reason}")
    
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
