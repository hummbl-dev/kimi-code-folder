#!/usr/bin/env python3
"""
Unit tests for the Federation Task Router.

Usage:
    python3 test_route_task.py
    python3 test_route_task.py -v  # Verbose
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path to import route_task
sys.path.insert(0, str(Path(__file__).parent))
from route_task import TaskRouter

# Use the same config path as the router
SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR.parent / "configs" / "federation-routing.json"


class TestTaskRouter(unittest.TestCase):
    """Test cases for the federation task router."""

    @classmethod
    def setUpClass(cls):
        """Initialize router once for all tests."""
        cls.router = TaskRouter(CONFIG_PATH)

    # ─────────────────────────────────────────────────────────────
    # Explicit Assignment Tests
    # ─────────────────────────────────────────────────────────────

    def test_explicit_pass_to_kimi(self):
        """Test 'pass to kimi' pattern."""
        result = self.router.route("pass this to kimi for implementation")
        self.assertEqual(result["agent"], "kimi")
        self.assertEqual(result["confidence"], 1.0)
        self.assertEqual(result["source"], "explicit")

    def test_explicit_at_mention_claude(self):
        """Test '@claude' mention pattern."""
        result = self.router.route("@claude research this topic")
        self.assertEqual(result["agent"], "claude")
        self.assertEqual(result["confidence"], 1.0)

    def test_explicit_agent_prefix(self):
        """Test 'agent:' prefix pattern."""
        result = self.router.route("kimi: implement this feature")
        self.assertEqual(result["agent"], "kimi")
        self.assertEqual(result["confidence"], 1.0)

    # ─────────────────────────────────────────────────────────────
    # Claude Routing Tests (Research/Analysis)
    # ─────────────────────────────────────────────────────────────

    def test_claude_research_keyword(self):
        """Test primary keyword 'research' routes to Claude."""
        result = self.router.route("Research the best authentication library")
        self.assertEqual(result["agent"], "claude")
        self.assertGreaterEqual(result["confidence"], 0.90)

    def test_claude_analyze_keyword(self):
        """Test primary keyword 'analyze' routes to Claude."""
        result = self.router.route("Analyze the current architecture")
        self.assertEqual(result["agent"], "claude")

    def test_claude_sitrep_special_case(self):
        """Test SITREP special case routes to Claude."""
        result = self.router.route("Generate a SITREP for Phase 3")
        self.assertEqual(result["agent"], "claude")

    def test_claude_architecture_keyword(self):
        """Test architecture keyword routes to Claude."""
        result = self.router.route("Design the system architecture")
        self.assertEqual(result["agent"], "claude")

    # ─────────────────────────────────────────────────────────────
    # Kimi Routing Tests (Implementation/Execution)
    # ─────────────────────────────────────────────────────────────

    def test_kimi_implement_keyword(self):
        """Test primary keyword 'implement' routes to Kimi."""
        result = self.router.route("Implement the auth middleware")
        self.assertEqual(result["agent"], "kimi")
        self.assertGreaterEqual(result["confidence"], 0.90)

    def test_kimi_build_keyword(self):
        """Test primary keyword 'build' routes to Kimi."""
        result = self.router.route("Build the user dashboard")
        self.assertEqual(result["agent"], "kimi")

    def test_kimi_deploy_keyword(self):
        """Test deploy keyword routes to Kimi."""
        result = self.router.route("Deploy to production")
        self.assertEqual(result["agent"], "kimi")

    def test_kimi_multi_file_bonus(self):
        """Test multi-file keyword gives boost to Kimi."""
        result = self.router.route("Implement auth across 5 files")
        self.assertEqual(result["agent"], "kimi")

    # ─────────────────────────────────────────────────────────────
    # Copilot Routing Tests (Thinking/Review)
    # ─────────────────────────────────────────────────────────────

    def test_copilot_think_keyword(self):
        """Test primary keyword 'think' routes to Copilot."""
        result = self.router.route("Think about the best approach")
        self.assertEqual(result["agent"], "copilot")

    def test_copilot_plan_keyword(self):
        """Test primary keyword 'plan' routes to Copilot."""
        result = self.router.route("Plan the sprint tasks")
        self.assertEqual(result["agent"], "copilot")

    def test_copilot_review_keyword(self):
        """Test review keyword routes to Copilot."""
        result = self.router.route("Review this code")
        self.assertEqual(result["agent"], "copilot")

    def test_copilot_what_do_you_think(self):
        """Test 'what do you think' pattern."""
        result = self.router.route("What do you think about this design?")
        self.assertEqual(result["agent"], "copilot")

    # ─────────────────────────────────────────────────────────────
    # Ollama Routing Tests (Drafting/Prototyping)
    # ─────────────────────────────────────────────────────────────

    def test_ollama_draft_keyword(self):
        """Test primary keyword 'draft' routes to Ollama."""
        result = self.router.route("Draft a quick proposal")
        self.assertEqual(result["agent"], "ollama")

    def test_ollama_prototype_keyword(self):
        """Test primary keyword 'prototype' routes to Ollama."""
        result = self.router.route("Prototype the new feature")
        self.assertEqual(result["agent"], "ollama")

    def test_ollama_offline_keyword(self):
        """Test offline keyword routes to Ollama."""
        result = self.router.route("Work on this offline")
        self.assertEqual(result["agent"], "ollama")

    # ─────────────────────────────────────────────────────────────
    # Confidence & Threshold Tests
    # ─────────────────────────────────────────────────────────────

    def test_high_confidence_auto_assignable(self):
        """Test high confidence tasks are auto-assignable."""
        result = self.router.route("implement auth system")
        self.assertTrue(result["auto_assignable"])
        self.assertGreaterEqual(result["confidence"], 0.70)

    def test_low_confidence_needs_clarification(self):
        """Test ambiguous tasks need clarification."""
        result = self.router.route("do the thing")
        self.assertTrue(result["needs_clarification"])
        self.assertLess(result["confidence"], 0.60)

    def test_alternatives_provided(self):
        """Test alternatives are provided for routing."""
        result = self.router.route("implement auth")
        self.assertIn("alternatives", result)
        self.assertIsInstance(result["alternatives"], list)

    # ─────────────────────────────────────────────────────────────
    # Negative Pattern Tests
    # ─────────────────────────────────────────────────────────────

    def test_research_negative_for_kimi(self):
        """Test 'research' in task penalizes Kimi score."""
        result = self.router.route("research implementation options")
        # Should go to Claude despite 'implementation' keyword
        self.assertEqual(result["agent"], "claude")

    # ─────────────────────────────────────────────────────────────
    # Edge Cases
    # ─────────────────────────────────────────────────────────────

    def test_empty_task(self):
        """Test empty task handling."""
        result = self.router.route("")
        self.assertIn("agent", result)
        self.assertIn("confidence", result)

    def test_very_long_task(self):
        """Test very long task gets length bonus."""
        long_task = "implement " * 100
        result = self.router.route(long_task)
        self.assertEqual(result["agent"], "kimi")

    def test_case_insensitivity(self):
        """Test routing is case insensitive."""
        result1 = self.router.route("IMPLEMENT AUTH")
        result2 = self.router.route("implement auth")
        self.assertEqual(result1["agent"], result2["agent"])


class TestRouterCLI(unittest.TestCase):
    """Test CLI interface (if needed)."""
    pass


if __name__ == "__main__":
    # Check if config exists
    if not CONFIG_PATH.exists():
        print(f"Error: Config not found at {CONFIG_PATH}")
        print("Make sure you're running from the scripts/ directory")
        sys.exit(1)

    # Run tests
    unittest.main(verbosity=2)
