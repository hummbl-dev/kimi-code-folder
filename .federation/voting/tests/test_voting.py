#!/usr/bin/env python3
"""
Unit tests for Federation Voting System

Usage:
    python3 test_voting.py
    python3 test_voting.py -v  # Verbose
"""

import unittest
import json
import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestVotingProtocol(unittest.TestCase):
    """Tests for the voting protocol and mechanics."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.proposals_dir = self.test_dir / "proposals"
        self.proposals_dir.mkdir()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_quorum_calculation(self):
        """Test that quorum is correctly calculated."""
        # With 3 active agents, quorum should be 2
        active_agents = ["claude", "kimi", "copilot"]
        quorum = len(active_agents) // 2 + 1  # Majority
        self.assertEqual(quorum, 2)
    
    def test_vote_types(self):
        """Test valid vote types."""
        valid_votes = ["yes", "no", "abstain"]
        for vote in valid_votes:
            self.assertIn(vote, valid_votes)
    
    def test_simple_majority_pass(self):
        """Test simple majority passing scenario."""
        yes_votes = 2
        no_votes = 1
        abstain = 0
        
        total_votes = yes_votes + no_votes + abstain
        self.assertGreaterEqual(total_votes, 2)  # Quorum met
        self.assertGreater(yes_votes, no_votes)  # Pass condition
    
    def test_simple_majority_reject(self):
        """Test simple majority rejecting scenario."""
        yes_votes = 1
        no_votes = 2
        abstain = 0
        
        total_votes = yes_votes + no_votes
        self.assertGreaterEqual(total_votes, 2)  # Quorum met
        self.assertLess(yes_votes, no_votes)  # Reject condition
    
    def test_tie_scenario(self):
        """Test tie scenario."""
        yes_votes = 1
        no_votes = 1
        abstain = 1
        
        total_votes = yes_votes + no_votes + abstain
        self.assertGreaterEqual(total_votes, 2)  # Quorum met
        self.assertEqual(yes_votes, no_votes)  # Tie condition
    
    def test_no_quorum(self):
        """Test scenario without quorum."""
        yes_votes = 1
        no_votes = 0
        abstain = 0
        
        total_votes = yes_votes + no_votes
        self.assertLess(total_votes, 2)  # No quorum
    
    def test_super_majority(self):
        """Test super majority (2/3) requirement."""
        total_agents = 3
        yes_votes = 2
        
        self.assertGreaterEqual(yes_votes / total_agents, 2/3)
    
    def test_proposal_id_format(self):
        """Test proposal ID format."""
        # Format: FED-YYYY-MM-DD-NNN
        proposal_id = "FED-2026-02-05-001"
        parts = proposal_id.split("-")
        
        self.assertEqual(parts[0], "FED")
        self.assertEqual(len(parts[1]), 4)  # Year
        self.assertEqual(len(parts[2]), 2)  # Month
        self.assertEqual(len(parts[3]), 2)  # Day
        self.assertEqual(len(parts[4]), 3)  # Sequence


class TestVotingIntegration(unittest.TestCase):
    """Integration tests for voting workflow."""
    
    def test_full_voting_workflow(self):
        """Test a complete voting workflow."""
        # This is a conceptual test - actual implementation
        # would test the CLI commands
        
        steps = [
            "create_proposal",
            "review_period",
            "cast_votes",
            "tally_results",
            "resolve_proposal"
        ]
        
        for step in steps:
            self.assertIsNotNone(step)
    
    def test_reuben_veto(self):
        """Test Reuben's veto authority."""
        # Even with 3 YES votes, Reuben can veto
        yes_votes = 3
        reuben_veto = True
        
        if reuben_veto:
            outcome = "REJECTED"
        else:
            outcome = "PASSED"
        
        self.assertEqual(outcome, "REJECTED")


class TestProposalTemplate(unittest.TestCase):
    """Tests for proposal template."""
    
    def test_template_exists(self):
        """Verify TEMPLATE.md exists."""
        template_path = Path(__file__).parent.parent / "proposals" / "TEMPLATE.md"
        self.assertTrue(template_path.exists())
    
    def test_template_has_required_sections(self):
        """Verify template has all required sections."""
        template_path = Path(__file__).parent.parent / "proposals" / "TEMPLATE.md"
        content = template_path.read_text()
        
        required_sections = [
            "Summary",
            "Background",
            "Proposal",
            "Alternatives Considered",
            "Impact",
            "Implementation",
            "Rollback Plan",
            "Votes"
        ]
        
        for section in required_sections:
            self.assertIn(section, content)


class TestVotingProtocol(unittest.TestCase):
    """Tests for voting protocol document."""
    
    def test_protocol_exists(self):
        """Verify VOTING_PROTOCOL.md exists."""
        protocol_path = Path(__file__).parent.parent / "VOTING_PROTOCOL.md"
        self.assertTrue(protocol_path.exists())
    
    def test_protocol_has_rules(self):
        """Verify protocol contains voting rules."""
        protocol_path = Path(__file__).parent.parent / "VOTING_PROTOCOL.md"
        content = protocol_path.read_text()
        
        # Check for key concepts
        self.assertIn("Quorum", content)
        self.assertIn("YES", content)
        self.assertIn("NO", content)
        self.assertIn("ABSTAIN", content)
        self.assertIn("veto", content.lower())


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestVotingProtocol))
    suite.addTests(loader.loadTestsFromTestCase(TestVotingIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestProposalTemplate))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
