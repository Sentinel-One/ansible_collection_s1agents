#!/usr/bin/env python
"""Thin orchestrator over molecule — the single test entry point.

Run on the project's existing pyenv (no uv):

    PYENV_VERSION=ansible-2.16 python scripts/molecule.py <action> <scenario> [--platform P]
    PYENV_VERSION=ansible-2.16 python scripts/molecule.py gate

Actions: test | converge | verify | destroy | create | login | gate
Platforms: linux (rocky8, default) | ubuntu2204 | opensuse15 | windows | <raw distro>
           (comma-separated to run several, e.g. --platform linux,windows)

Config precedence (low -> high): env-file (molecule.env) < process env < --platform preset.
Secrets are never committed; with secrets in the environment (CI) no env-file is needed.

Output is streamed to .molecule-logs/<scenario>-<platform>.log (gitignored); a compact
summary is printed to stdout. Exit 0 = pass, molecule's code = real failure, 75 = transient
infrastructure (proxy TLS reset / SSH connection reset) — re-authenticate the proxy and retry.

See docs/adr/0005-molecule-test-harness.md.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXTENSIONS_DIR = REPO_ROOT / "extensions"
LOG_DIR = REPO_ROOT / ".molecule-logs"
GATE_FILE = REPO_ROOT / "scripts" / "gate.yml"
DEFAULT_ENV_FILE = REPO_ROOT / "molecule.env"
PYENV = "ansible-2.16"

EXIT_TRANSIENT = 75  # EX_TEMPFAIL — transient infra, safe to retry

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

# Signatures that mean "environment hiccup", not a real test failure.
TRANSIENT_SIGNATURES = (
    "UNEXPECTED_EOF_WHILE_READING",  # proxy reset the inspected TLS connection
    "kex_exchange_identification",   # SSH handshake reset during VM boot
    "Connection reset by",
    "Connection closed by",
)

# Platform presets -> the S1_VAGRANT_* (and extra) env the molecule.yml consumes.
PRESETS: dict[str, dict[str, str]] = {
    "linux": {"S1_VAGRANT_DISTRO": "rocky8", "S1_VAGRANT_REPO": "roboxes", "S1_VAGRANT_GROUP": "Linux"},
    "rocky8": {"S1_VAGRANT_DISTRO": "rocky8", "S1_VAGRANT_REPO": "roboxes", "S1_VAGRANT_GROUP": "Linux"},
    "ubuntu2204": {"S1_VAGRANT_DISTRO": "ubuntu2204", "S1_VAGRANT_REPO": "roboxes", "S1_VAGRANT_GROUP": "Linux"},
    "opensuse15": {"S1_VAGRANT_DISTRO": "opensuse15", "S1_VAGRANT_REPO": "roboxes", "S1_VAGRANT_GROUP": "Linux"},
    "windows": {
        "S1_VAGRANT_DISTRO": "windows-server-2022-standard",
        "S1_VAGRANT_REPO": "gusztavvargadr",
        "S1_VAGRANT_GROUP": "Windows",
        "OBJC_DISABLE_INITIALIZE_FORK_SAFETY": "YES",
    },
}


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a shell-style env file (`export KEY=VALUE`); ignore comments/blanks."""
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        values[key.strip()] = val.strip().strip('"').strip("'")
    return values


def preset_for(platform: str) -> dict[str, str]:
    """Resolve a platform name to its env preset, or pass a raw distro through."""
    if platform in PRESETS:
        return dict(PRESETS[platform])
    # Raw distro pass-through: assume a Linux box on the default repo.
    return {"S1_VAGRANT_DISTRO": platform, "S1_VAGRANT_REPO": "roboxes", "S1_VAGRANT_GROUP": "Linux"}


def build_env(platform: str, env_file: Path) -> dict[str, str]:
    """Layer: env-file (base) < process env < platform preset."""
    env = dict(parse_env_file(env_file))      # lowest precedence
    env.update(os.environ)                    # process env / CI secrets win
    env.update(preset_for(platform))          # explicit platform wins for VM cfg
    env["PYENV_VERSION"] = PYENV
    # Disable ANSI color so the streamed .log is clean (matches ANSIBLE_LOG_PATH).
    env["ANSIBLE_NOCOLOR"] = "1"
    env["PY_COLORS"] = "0"
    return env


def classify(rc: int, log_text: str) -> str:
    """Return 'pass', 'transient', or 'fail'."""
    if rc == 0:
        return "pass"
    if any(sig in log_text for sig in TRANSIENT_SIGNATURES):
        return "transient"
    return "fail"


def recap_lines(log_text: str) -> list[str]:
    out = []
    keep = False
    for line in log_text.splitlines():
        clean = ANSI_RE.sub("", line)
        if "PLAY RECAP" in clean:
            keep = True
            continue
        if keep and clean.strip():
            out.append(clean.strip())
        elif keep and not clean.strip():
            keep = False
    return out


def run_one(action: str, scenario: str, platform: str, env_file: Path) -> tuple[str, int, Path]:
    """Run a single molecule action for one platform; return (result, rc, logpath)."""
    LOG_DIR.mkdir(exist_ok=True)
    logpath = LOG_DIR / f"{scenario}-{platform}.log"
    ansible_log = LOG_DIR / f"{scenario}-{platform}.ansible.log"
    env = build_env(platform, env_file)
    env["ANSIBLE_LOG_PATH"] = str(ansible_log)
    if ansible_log.exists():
        ansible_log.unlink()

    cmd = ["molecule", action, "--scenario-name", scenario]
    header = f"$ {action} {scenario} --platform {platform}  (distro={env.get('S1_VAGRANT_DISTRO')})"
    print(header, flush=True)

    with logpath.open("w") as lf:
        lf.write(header + "\n")
        lf.flush()
        proc = subprocess.Popen(
            cmd, cwd=EXTENSIONS_DIR, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            lf.write(line)
            lf.flush()
        proc.wait()
    rc = proc.returncode

    log_text = logpath.read_text(errors="replace")
    result = classify(rc, log_text)
    label = f"[{scenario}/{platform}]"
    if result == "pass":
        print(f"{label} PASS  ({'; '.join(recap_lines(log_text)) or 'ok'})")
    elif result == "transient":
        print(f"{label} TRANSIENT-INFRA (rc={rc})")
        print("  ⚠ proxy auth likely expired (TLS UNEXPECTED_EOF) or SSH reset during boot.")
        print("    Re-authenticate the proxy and re-run; this is not a code/test failure.")
    else:
        print(f"{label} FAIL (rc={rc})  {'; '.join(recap_lines(log_text)) or ''}")
    print(f"  log: {logpath.relative_to(REPO_ROOT)}")
    return result, rc, logpath


def load_gate() -> list[dict]:
    import yaml  # ships with ansible in the ansible-2.16 pyenv
    data = yaml.safe_load(GATE_FILE.read_text())
    return data if isinstance(data, list) else data.get("gate", [])


def aggregate_exit(results: list[str], rcs: list[int]) -> int:
    if all(r == "pass" for r in results):
        return 0
    if any(r == "fail" for r in results):
        return next((rc for r, rc in zip(results, rcs) if r == "fail" and rc), 1)
    return EXIT_TRANSIENT  # only transient failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Molecule test harness (see docs/adr/0005).")
    parser.add_argument("action", choices=["test", "converge", "verify", "destroy", "create", "login", "gate"])
    parser.add_argument("scenario", nargs="?", help="molecule scenario (omit for 'gate')")
    parser.add_argument("--platform", default="linux", help="preset(s) or raw distro, comma-separated")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE), type=Path)
    args = parser.parse_args()

    if args.action == "gate":
        results, rcs = [], []
        for entry in load_gate():
            scenario = entry["scenario"]
            for platform in entry.get("platforms", ["linux"]):
                result, rc, _ = run_one("test", scenario, platform, args.env_file)
                results.append(result)
                rcs.append(rc)
        print(f"\n=== gate: {results.count('pass')}/{len(results)} passed ===")
        return aggregate_exit(results, rcs)

    if not args.scenario:
        parser.error(f"action '{args.action}' requires a scenario")

    results, rcs = [], []
    for platform in [p.strip() for p in args.platform.split(",") if p.strip()]:
        result, rc, _ = run_one(args.action, args.scenario, platform, args.env_file)
        results.append(result)
        rcs.append(rc)
    return aggregate_exit(results, rcs)


if __name__ == "__main__":
    sys.exit(main())
