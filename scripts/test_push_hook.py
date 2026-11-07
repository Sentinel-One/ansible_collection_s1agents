# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Tests the trufflehog scan range chosen by .claude/hooks/lint-before-push.sh.

Each case builds a throwaway git repo, puts a `trufflehog` shim on PATH that
records its arguments, runs the hook with a `git push` payload, and checks the
--since-commit base the hook passed. A fake secret cannot test detection here
(the hook uses --only-verified), so detection is out of scope: this checks that
the hook scans the commits being pushed rather than only the staged changes.

Run: uv run scripts/test_push_hook.py
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / ".claude" / "hooks" / "lint-before-push.sh"


def git(repo: Path, *args: str) -> str:
    env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
    out = subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=repo, env=env, check=True, capture_output=True, text=True,
    )
    return out.stdout.strip()


class PushHookRange(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        (self.repo / "a.txt").write_text("a\n")
        git(self.repo, "add", "a.txt")
        git(self.repo, "commit", "-qm", "base")
        self.base = git(self.repo, "rev-parse", "HEAD")

        # Stub ansible-lint so only the trufflehog half of the hook is exercised.
        lint = self.repo / ".venv" / "bin" / "ansible-lint"
        lint.parent.mkdir(parents=True)
        lint.write_text("#!/bin/sh\nexit 0\n")
        lint.chmod(0o755)

        # trufflehog shim: record argv, succeed.
        self.argfile = root / "args.txt"
        shim_dir = root / "shim"
        shim_dir.mkdir()
        shim = shim_dir / "trufflehog"
        shim.write_text(f'#!/bin/sh\nprintf "%s\\n" "$@" > "{self.argfile}"\nexit 0\n')
        shim.chmod(0o755)
        self.path = f"{shim_dir}:{os.environ['PATH']}"

    def commit_unpushed(self) -> str:
        (self.repo / "b.txt").write_text("b\n")
        git(self.repo, "add", "b.txt")
        git(self.repo, "commit", "-qm", "unpushed")
        return git(self.repo, "rev-parse", "HEAD")

    def run_hook(self) -> subprocess.CompletedProcess:
        payload = json.dumps({"tool_input": {"command": "git push"}})
        env = {**os.environ, "PATH": self.path, "CLAUDE_PROJECT_DIR": str(self.repo),
               "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
        return subprocess.run(["bash", str(HOOK)], input=payload, env=env,
                              capture_output=True, text=True)

    def args(self) -> list[str]:
        return self.argfile.read_text().split()

    def test_upstream_base(self) -> None:
        git(self.repo, "remote", "add", "origin", "/nonexistent")  # never contacted
        git(self.repo, "update-ref", "refs/remotes/origin/main", self.base)
        git(self.repo, "branch", "--set-upstream-to=origin/main")
        self.commit_unpushed()
        res = self.run_hook()
        self.assertEqual(res.returncode, 0, res.stderr)
        a = self.args()
        self.assertEqual(a[a.index("--since-commit") + 1], self.base)
        self.assertIn("--only-verified", a)

    def test_origin_main_fallback_without_upstream(self) -> None:
        git(self.repo, "update-ref", "refs/remotes/origin/main", self.base)
        self.commit_unpushed()
        res = self.run_hook()
        self.assertEqual(res.returncode, 0, res.stderr)
        a = self.args()
        self.assertEqual(a[a.index("--since-commit") + 1], self.base)

    def test_no_remote_ref_scans_full_history(self) -> None:
        self.commit_unpushed()
        res = self.run_hook()
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertNotIn("--since-commit", self.args())

    def test_trufflehog_failure_blocks_push(self) -> None:
        self.commit_unpushed()
        Path(self.path.split(":")[0], "trufflehog").write_text("#!/bin/sh\nexit 183\n")
        res = self.run_hook()
        self.assertEqual(res.returncode, 2)
        self.assertIn("trufflehog found a possible secret", res.stderr)


if __name__ == "__main__":
    sys.exit(unittest.main())
