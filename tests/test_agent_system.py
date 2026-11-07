#!/usr/bin/env python3
"""
Automated Test Suite for Agent Hub Directives & Zero-Execution Enforcement.
Verifies that Master Agent rules, M2M protocols, sharding, and anti-polling guards
are 100% compliant.
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path

# Set UTF-8 encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class TestAgentSystemRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hub_dir = Path(__file__).resolve().parent.parent
        cls.gemini_md = cls.hub_dir / "GEMINI.md"
        cls.master_skill = cls.hub_dir / "common" / "skills" / "master-agent" / "SKILL.md"
        cls.m2m_rule = cls.hub_dir / "rules" / "m2m-protocol.md"
        cls.m2m_detail = cls.hub_dir / "rules" / "m2m-protocol-detail.md"
        cls.m2m_dispatch = cls.hub_dir / "common" / "skills" / "master-agent" / "references" / "m2m-dispatch.md"
        cls.sharder = cls.hub_dir / "common" / "scripts" / "context_sharder.py"
        cls.validator = cls.hub_dir / "common" / "scripts" / "validate_system.py"

    def test_01_gemini_directives_integrity(self):
        """Test GEMINI.md has strict Vietnamese directive, Rule 16, 18, and Rule 19 Zero-Execution."""
        self.assertTrue(self.gemini_md.exists(), "GEMINI.md must exist in root.")
        content = self.gemini_md.read_text(encoding="utf-8")
        
        self.assertIn("TIẾNG VIỆT", content, "Must enforce Vietnamese.")
        self.assertIn("Rule 16", content, "Must include Rule 16 (Maximal API offloading).")
        self.assertIn("Rule 18", content, "Must include Rule 18 (Dynamic Context Sharding).")
        self.assertIn("Rule 19", content, "Must include Rule 19 (Zero-Execution).")
        
        # Test specific prohibitions to prevent recurrence of 12% token drain
        self.assertIn("read_file", content, "Must explicitly prohibit read_file on project code in Main Chat.")
        self.assertIn("schedule", content.lower(), "Must explicitly prohibit polling via schedule.")
        self.assertIn("invoke_subagent", content, "Must mandate invoke_subagent for project tasks.")

    def test_02_master_agent_skill_sop(self):
        """Test master-agent/SKILL.md defines standard 4-step SOP and 5 Deadly Sins table."""
        self.assertTrue(self.master_skill.exists(), "master-agent/SKILL.md must exist.")
        content = self.master_skill.read_text(encoding="utf-8")
        
        self.assertIn("dental-pm-orchestrator", content, "Routing matrix must include dental-pm-orchestrator.")
        self.assertIn("vj-pm-orchestrator", content, "Routing matrix must include vj-pm-orchestrator.")
        self.assertIn("ĐIỀU CẤM KỴ", content, "Must contain 5 Deadly Sins table.")
        self.assertIn("Reactive Wakeup", content, "Must mandate Reactive Wakeup instead of polling.")

    def test_03_m2m_protocols_rule19(self):
        """Test m2m-protocol.md and m2m-protocol-detail.md include Rule 19."""
        self.assertTrue(self.m2m_rule.exists())
        self.assertTrue(self.m2m_detail.exists())
        
        c1 = self.m2m_rule.read_text(encoding="utf-8")
        c2 = self.m2m_detail.read_text(encoding="utf-8")
        
        self.assertIn("19.", c1, "Rule 19 must be in m2m-protocol.md")
        self.assertIn("Zero-Execution", c1, "Zero-Execution must be defined in m2m-protocol.md")
        self.assertIn("19.", c2, "Rule 19 must be in m2m-protocol-detail.md")
        self.assertIn("Reactive Wakeup", c2, "Reactive Wakeup must be detailed in m2m-protocol-detail.md")

    def test_04_system_validator_script(self):
        """Run validate_system.py and assert exit code 0 with 0 errors."""
        res = subprocess.run(
            [sys.executable, str(self.validator)],
            capture_output=True, encoding="utf-8", errors="replace", cwd=str(self.hub_dir)
        )
        self.assertEqual(res.returncode, 0, f"validate_system.py failed: {res.stderr}\n{res.stdout}")
        self.assertIn("0 Lỗi", res.stdout, "System validator must report 0 Lỗi.")

    def test_05_context_sharder_cycle(self):
        """Test context_sharder.py switches to dental shard and safely resets to core."""
        # 1. Shard to dental
        p1 = subprocess.run(
            [sys.executable, str(self.sharder), "--hub", str(self.hub_dir), "--set", "dental"],
            capture_output=True, encoding="utf-8", errors="replace", cwd=str(self.hub_dir)
        )
        self.assertEqual(p1.returncode, 0, f"Failed to set dental shard: {p1.stderr}")
        
        # 2. Reset shard to core
        p2 = subprocess.run(
            [sys.executable, str(self.sharder), "--hub", str(self.hub_dir), "--reset"],
            capture_output=True, encoding="utf-8", errors="replace", cwd=str(self.hub_dir)
        )
        self.assertEqual(p2.returncode, 0, f"Failed to reset shard: {p2.stderr}")
        self.assertIn("core", p2.stdout.lower(), "Must reset to core shard.")

if __name__ == "__main__":
    unittest.main()
