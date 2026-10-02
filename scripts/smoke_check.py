# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bootstrap smoke check for the uv-managed dev toolchain.

Builds a throwaway venv from requirements-dev.txt, confirms every pinned
tool resolves to its expected version, then deletes the throwaway venv.
Never touches the working .venv. Run on demand:

    uv run scripts/smoke_check.py
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS = REPO_ROOT / "requirements-dev.txt"
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")

# tool -> (version command, regex to extract the version)
CHECKS = {
    "ansible-lint": (["ansible-lint", "--version"], r"ansible-lint\s+([0-9.]+)"),
    "yamllint": (["yamllint", "--version"], r"yamllint\s+([0-9.]+)"),
    "molecule": (["molecule", "--version"], r"molecule\s+([0-9.]+)"),
    "pre-commit": (["pre-commit", "--version"], r"pre-commit\s+([0-9.]+)"),
    "ansible": (["ansible", "--version"], r"ansible\s+\[core\s+([0-9.]+)\]"),
}


def pinned_version(package: str) -> str | None:
    text = REQUIREMENTS.read_text()
    match = re.search(rf"^{re.escape(package)}==([0-9.]+)", text, re.MULTILINE)
    return match.group(1) if match else None


def main() -> int:
    tmp_dir = Path(tempfile.mkdtemp(prefix="s1agents-smoke-"))
    venv_dir = tmp_dir / ".venv"
    try:
        subprocess.run(
            ["uv", "venv", "--python", "3.12", str(venv_dir)], check=True
        )
        subprocess.run(
            [
                "uv",
                "pip",
                "install",
                "--python",
                str(venv_dir / "bin" / "python"),
                "-r",
                str(REQUIREMENTS),
            ],
            check=True,
        )

        env = {**os.environ, "PATH": f"{venv_dir / 'bin'}:{os.environ.get('PATH', '')}"}

        failures = []
        for tool, (cmd, pattern) in CHECKS.items():
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            output = ANSI_ESCAPE.sub("", result.stdout + result.stderr)
            match = re.search(pattern, output)
            if result.returncode != 0 or not match:
                failures.append(f"{tool}: did not resolve to a version (exit {result.returncode})")
                continue

            resolved = match.group(1)
            pin = pinned_version(tool)
            if pin and resolved != pin:
                failures.append(f"{tool}: resolved {resolved}, expected pinned {pin}")
            else:
                print(f"OK  {tool} {resolved}")

        if failures:
            for failure in failures:
                print(f"FAIL {failure}", file=sys.stderr)
            return 1

        print("Bootstrap smoke check passed.")
        return 0
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
