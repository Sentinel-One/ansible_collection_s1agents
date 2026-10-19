# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Unit tests for scripts/molecule.py's pure logic (no molecule, no VMs).

    uv run scripts/test_molecule.py
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("molecule_harness", Path(__file__).with_name("molecule.py"))
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

PORT_COLLISION_LOG = """\
TASK [Create molecule instance(s)] *****
fatal: [localhost]: FAILED! => {"changed": false, "msg": "Failed to start the VM", "stderr_lines": ["Vagrant found a port collision for the specified port and virtual machine.", "While this port was marked to be auto-corrected, the ports in the", "auto-correction range are all also used."]}
"""

TLS_RESET_LOG = """\
fatal: [rocky8]: FAILED! => {"msg": "Status code was -1: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING]>"}
"""

REAL_FAIL_LOG = """\
fatal: [rocky8]: FAILED! => {"msg": "Probe expected to fail"}
...ignoring
fatal: [rocky8]: FAILED! => {"changed": false, "msg": "SentinelOne agent version mismatch: \\"26.1\\" != \\"25.2\\""}
"""

# Pretty-printed results: '...ignoring' follows the closing brace, not the fatal line.
IGNORED_MULTILINE_TRANSIENT_LOG = """\
fatal: [win]: FAILED! => {
    "changed": false,
    "msg": "kex_exchange_identification: read: Connection reset by peer"
}
...ignoring
fatal: [win]: FAILED! => {
    "changed": false,
    "msg": "Agent service is not running"
}
"""

# An earlier rescued failure, then the looped assert that actually ended the run.
RESCUED_THEN_ITEM_FAIL_LOG = """\
fatal: [host]: FAILED! => {
    "assertion": "x",
    "msg": "expected rejection, rescued"
}
failed: [host] (item=linux_path_dot) => {"ansible_loop_var": "c", "msg": "linux_path_dot: expected reject, got accept"}
"""

CRITICAL_ONLY_LOG = """\
INFO     Running default > create
CRITICAL Ansible return code was 2, command was: ansible-playbook create.yml
"""


class ResolvePlatforms(unittest.TestCase):
    def test_pinned_scenario_defaults_to_its_platform(self):
        self.assertEqual(m.resolve_platforms("windows-legacy-plus", None), ["windowslegacyplus"])
        self.assertEqual(m.resolve_platforms("windows-tier-matrix", None), ["none"])

    def test_pinned_scenario_accepts_its_platform(self):
        self.assertEqual(m.resolve_platforms("windows-legacy-plus", "windowslegacyplus"), ["windowslegacyplus"])

    def test_pinned_scenario_rejects_other_platforms(self):
        for arg in ("linux", "windowslegacyplus,windows"):
            with self.subTest(arg=arg), self.assertRaises(ValueError):
                m.resolve_platforms("windows-legacy-plus", arg)

    def test_unpinned_scenario_defaults_to_linux(self):
        self.assertEqual(m.resolve_platforms("upgrade", None), ["linux"])

    def test_explicit_list_is_split_and_trimmed(self):
        self.assertEqual(m.resolve_platforms("upgrade", "rocky8, windows"), ["rocky8", "windows"])


class Classify(unittest.TestCase):
    def test_zero_rc_passes(self):
        self.assertEqual(m.classify(0, PORT_COLLISION_LOG), "pass")

    def test_port_collision_is_host_setup(self):
        self.assertEqual(m.classify(2, PORT_COLLISION_LOG), "host")

    def test_tls_reset_is_transient(self):
        self.assertEqual(m.classify(2, TLS_RESET_LOG), "transient")

    def test_other_failure_is_fail(self):
        self.assertEqual(m.classify(2, REAL_FAIL_LOG), "fail")

    def test_ignored_multiline_transient_does_not_mask_real_failure(self):
        self.assertEqual(m.classify(2, IGNORED_MULTILINE_TRANSIENT_LOG), "fail")


class FailureReason(unittest.TestCase):
    def test_skips_ignored_fatals_and_returns_msg(self):
        self.assertEqual(m.failure_reason(REAL_FAIL_LOG), 'SentinelOne agent version mismatch: \\"26.1\\" != \\"25.2\\"')

    def test_reads_msg_from_multiline_result(self):
        self.assertEqual(m.failure_reason(IGNORED_MULTILINE_TRANSIENT_LOG), "Agent service is not running")

    def test_reports_last_failure_with_its_loop_item(self):
        self.assertEqual(
            m.failure_reason(RESCUED_THEN_ITEM_FAIL_LOG),
            "linux_path_dot: linux_path_dot: expected reject, got accept",
        )

    def test_falls_back_to_critical_line(self):
        self.assertTrue(m.failure_reason(CRITICAL_ONLY_LOG).startswith("CRITICAL Ansible return code was 2"))

    def test_empty_when_nothing_found(self):
        self.assertEqual(m.failure_reason("PLAY RECAP\n"), "")


class AggregateExit(unittest.TestCase):
    def test_all_pass(self):
        self.assertEqual(m.aggregate_exit(["pass", "pass"], [0, 0]), 0)

    def test_only_transient_is_75(self):
        self.assertEqual(m.aggregate_exit(["pass", "transient"], [0, 2]), m.EXIT_TRANSIENT)

    def test_host_setup_is_not_reported_as_transient(self):
        self.assertEqual(m.aggregate_exit(["host", "transient"], [2, 2]), 2)

    def test_real_failure_wins(self):
        self.assertEqual(m.aggregate_exit(["transient", "fail"], [2, 1]), 1)


if __name__ == "__main__":
    sys.exit(0 if unittest.main(exit=False, verbosity=1).result.wasSuccessful() else 1)
