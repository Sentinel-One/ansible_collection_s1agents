#!/usr/bin/env python
"""Thin orchestrator over molecule — the single test entry point.

Run on the project's uv-managed .venv (see requirements-dev.txt):

    .venv/bin/python scripts/molecule.py <action> <scenario> [--platform P]
    .venv/bin/python scripts/molecule.py gate

Actions: test | converge | verify | destroy | create | login | gate
Platforms: linux (rocky8, default) | ubuntu2204 | opensuse15 | windows | windowslegacyplus | none | <raw distro>
           (comma-separated to run several, e.g. --platform linux,windows)
           Scenarios with a single valid platform (PINNED_PLATFORMS, e.g.
           windows-legacy-plus) default to it and reject any other.
           "none" is for VM-less scenarios (e.g. windows-tier-matrix) that declare
           no Vagrant platform at all.

Secrets (molecule.env, gitignored) are injected by wrapping the invocation in `op run`,
never read or parsed by this script:

    op run --env-file="molecule.env" -- .venv/bin/python scripts/molecule.py test default

Config precedence (low -> high): process env (op run's injected secrets included) <
--platform preset.

Output is streamed to .molecule-logs/<scenario>-<platform>.log (gitignored); a compact
summary is printed to stdout. Exit 0 = pass, molecule's code = real failure, 75 = transient
infrastructure (proxy TLS reset / SSH connection reset) — re-authenticate the proxy and retry.
A known controller-setup problem (HOST_SIGNATURES) is labelled HOST-SETUP with a fix hint
and exits non-zero, since retrying won't clear it.

Unit tests for the pure logic here: uv run scripts/test_molecule.py

See docs/adr/0005-molecule-test-harness.md.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def _running_molecule_pids() -> list[int]:
    """Return PIDs of molecule subprocesses that are not the current process."""
    our_pid = os.getpid()
    # Match 'molecule <action>' invocations; avoids matching 'scripts/molecule.py' itself.
    pattern = r"molecule\s+(test|gate|converge|verify|destroy|create|login)"
    try:
        r = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True)
        return [int(p) for p in r.stdout.strip().splitlines() if p.strip() and int(p.strip()) != our_pid]
    except (FileNotFoundError, ValueError):
        return []


def _running_vms() -> list[str]:
    """Return display names of currently running VirtualBox VMs, or [] if unavailable."""
    for cmd in (["VBoxManage", "list", "runningvms"], ["vboxmanage", "list", "runningvms"]):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if r.returncode != 0:
                return []
            return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return []


def preflight_check(force: bool = False) -> None:
    """Warn or abort if another molecule session is running or stale VMs are found.

    Concurrent molecule runs share /tmp/s1_fact_cache and Vagrant VM names, which
    produces corrupt fact caches and SSH collisions.  Pass force=True (--force) to
    demote the abort to a warning when you know it is safe to proceed.
    """
    issues: list[str] = []

    pids = _running_molecule_pids()
    if pids:
        pid_str = ", ".join(str(p) for p in pids)
        issues.append(
            f"molecule is already running (PID {pid_str}).\n"
            f"    Concurrent runs corrupt the shared fact cache and VM names.\n"
            f"    Stop them first:  kill {pid_str}"
        )

    vms = _running_vms()
    if vms:
        vm_list = "\n".join(f"    {vm}" for vm in vms)
        issues.append(
            f"{len(vms)} VirtualBox VM(s) are already running and may block creation:\n"
            f"{vm_list}\n"
            f"    Destroy strays:  VBoxManage controlvm <uuid> poweroff"
        )

    if not issues:
        return

    sep = "-" * 64
    header = f"\n{sep}\n  PRE-FLIGHT CHECK FAILED\n{sep}"
    body = "\n".join(f"\n  ! {issue}" for issue in issues)
    if force:
        footer = f"\n  --force passed: proceeding anyway.\n{sep}"
        print(header + body + footer, file=sys.stderr)
    else:
        footer = f"\n  Rerun with --force to bypass these checks.\n{sep}"
        print(header + body + footer, file=sys.stderr)
        sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
EXTENSIONS_DIR = REPO_ROOT / "extensions"
LOG_DIR = SCRIPTS_DIR / "logs" / "molecule"
GATE_FILE = SCRIPTS_DIR / "gate.yml"

EXIT_TRANSIENT = 75  # EX_TEMPFAIL — transient infra, safe to retry

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

# Signatures that mean "environment hiccup", not a real test failure.
TRANSIENT_SIGNATURES = (
    "UNEXPECTED_EOF_WHILE_READING",  # proxy reset the inspected TLS connection
    "kex_exchange_identification",   # SSH handshake reset during VM boot
    "Connection reset by",
    "Connection closed by",
)

# Signatures that mean "this controller's setup is broken" — a retry won't help,
# but it isn't a code/test failure either. Each maps to the hint printed for it.
HOST_SIGNATURES: dict[str, str] = {
    "Vagrant found a port collision": (
        "Vagrant's forwarded-port check false-positives on macOS 26, so Windows boxes\n"
        "    can't place WinRM/RDP. See docs/vagrant-port-collision.md for the fix."
    ),
}

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
    # Real-install fixture (extensions/molecule/windows-legacy-plus) — proves
    # the Legacy Plus tier's frozen upgrade flow and default-version pin
    # against a real host, not fact-mocked. In the gate (scripts/gate.yml),
    # and this local run is the authoritative gate for that tier: it cannot
    # pass on hosted CI runners. See ADR 0008 and ADR 0011.
    "windowslegacyplus": {
        "S1_VAGRANT_DISTRO": "WindowsServer2012",
        "S1_VAGRANT_REPO": "jborean93",
        "S1_VAGRANT_GROUP": "Windows",
        "OBJC_DISABLE_INITIALIZE_FORK_SAFETY": "YES",
    },
    # VM-less scenario (extensions/molecule/windows-tier-matrix) — no box, so
    # no S1_VAGRANT_* env is needed; an empty preset keeps raw distro
    # pass-through (below) from misinterpreting "none" as a Linux box name.
    "none": {},
}


# Scenarios that can only ever run on one platform. Omitting --platform picks it;
# passing any other platform is an error rather than a silently meaningless run.
PINNED_PLATFORMS: dict[str, str] = {
    "windows-legacy-plus": "windowslegacyplus",
    "windows-tier-matrix": "none",
    "input-validation": "none",
}


def resolve_platforms(scenario: str, platform_arg: str | None) -> list[str]:
    """Platforms to run: the explicit --platform list, the scenario's pin, or linux."""
    pinned = PINNED_PLATFORMS.get(scenario)
    if platform_arg is None:
        return [pinned or "linux"]
    platforms = [p.strip() for p in platform_arg.split(",") if p.strip()]
    if pinned and any(p != pinned for p in platforms):
        raise ValueError(f"scenario '{scenario}' only runs on --platform {pinned} (got: {platform_arg})")
    return platforms


def preset_for(platform: str) -> dict[str, str]:
    """Resolve a platform name to its env preset, or pass a raw distro through."""
    if platform in PRESETS:
        return dict(PRESETS[platform])
    # Raw distro pass-through: assume a Linux box on the default repo.
    return {"S1_VAGRANT_DISTRO": platform, "S1_VAGRANT_REPO": "roboxes", "S1_VAGRANT_GROUP": "Linux"}


def build_env(platform: str) -> dict[str, str]:
    """Layer: process env (secrets, injected by `op run` if used) < platform preset."""
    env = dict(os.environ)
    env.update(preset_for(platform))          # explicit platform wins for VM cfg
    # molecule (provisioner.name: ansible) resolves ansible-playbook/ansible by
    # bare name via PATH — there's no ansible.cfg or pinned interpreter anywhere
    # in the repo — so .venv/bin must lead PATH for both molecule and its
    # ansible children to resolve to the pinned toolchain.
    venv_bin = Path(sys.executable).parent
    env["PATH"] = f"{venv_bin}{os.pathsep}{env.get('PATH', '')}"
    # Disable ANSI color so the streamed .log is clean (matches ANSIBLE_LOG_PATH).
    env["ANSIBLE_NOCOLOR"] = "1"
    env["PY_COLORS"] = "0"
    return env


def _unignored_fatals(log_text: str) -> list[str]:
    """Return fatal/failed-item results Ansible did NOT recover from, one string per result.

    A result is a single line, or a multi-line JSON body ending at a bare '}'.
    Ansible prints '...ignoring' right after a result whose task carries
    ignore_errors/ignore_unreachable — e.g. a pre-VM connectivity probe that's
    expected to fail before the box exists. Those results must not count as
    evidence of what actually broke the run.
    """
    lines = [ANSI_RE.sub("", ln) for ln in log_text.splitlines()]
    out = []
    for i, line in enumerate(lines):
        head = line.lstrip()
        if not (head.startswith("fatal:") or head.startswith("failed: [")):
            continue
        end = i
        if line.rstrip().endswith("{"):
            while end + 1 < len(lines) and lines[end].rstrip() != "}":
                end += 1
        if any("...ignoring" in nxt for nxt in lines[end + 1 : end + 3]):
            continue
        out.append("\n".join(lines[i : end + 1]))
    return out


def host_problem(log_text: str) -> str | None:
    """Return the HOST_SIGNATURES key found in the log, if any."""
    return next((sig for sig in HOST_SIGNATURES if sig in log_text), None)


def failure_reason(log_text: str) -> str:
    """One line naming what broke the run: the last unignored failure's msg, else a CRITICAL line.

    The last, not the first: a run stops at its final failure, while earlier
    ones may have been rescued (block/rescue prints no '...ignoring').
    """
    fatals = _unignored_fatals(log_text)
    if fatals:
        block = fatals[-1]
        m = re.search(r'"msg": "((?:[^"\\]|\\.)*)"', block)
        item = re.search(r"\(item=([^)]*)\)", block.splitlines()[0])
        text = m.group(1) if m else block.splitlines()[0].strip()
        return (f"{item.group(1)}: {text}" if item else text)[:240]
    for line in log_text.splitlines():
        clean = ANSI_RE.sub("", line).strip()
        if "CRITICAL" in clean:
            return clean[:240]
    return ""


def classify(rc: int, log_text: str) -> str:
    """Return 'pass', 'host', 'transient', or 'fail'.

    Transient signatures are matched only against unignored fatal/unreachable
    lines (falling back to the full log if none are found — e.g. a molecule-
    level abort with no leading 'fatal:' line) so an early, recovered blip
    (an ignored SSH reset during a pre-VM connectivity check, say) can't mask
    a real failure that happened later in the same run.
    """
    if rc == 0:
        return "pass"
    fatals = _unignored_fatals(log_text)
    haystack = "\n".join(fatals) if fatals else log_text
    if host_problem(haystack):
        return "host"
    if any(sig in haystack for sig in TRANSIENT_SIGNATURES):
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


def run_one(action: str, scenario: str, platform: str) -> tuple[str, int, Path]:
    """Run a single molecule action for one platform; return (result, rc, logpath)."""
    LOG_DIR.mkdir(exist_ok=True)
    logpath = LOG_DIR / f"{scenario}-{platform}.log"
    ansible_log = LOG_DIR / f"{scenario}-{platform}.ansible.log"
    env = build_env(platform)
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
    elif result == "host":
        print(f"{label} HOST-SETUP (rc={rc})")
        print(f"  ⚠ {host_problem(log_text)}: a controller problem, not a code/test failure.")
        print(f"    {HOST_SIGNATURES[host_problem(log_text)]}")
    elif result == "transient":
        print(f"{label} TRANSIENT-INFRA (rc={rc})")
        print("  ⚠ proxy auth likely expired (TLS UNEXPECTED_EOF) or SSH reset during boot.")
        print("    Re-authenticate the proxy and re-run; this is not a code/test failure.")
    else:
        print(f"{label} FAIL (rc={rc})  {'; '.join(recap_lines(log_text)) or ''}")
        if err := failure_reason(log_text):
            print(f"  error: {err}")
    print(f"  log: {logpath.relative_to(REPO_ROOT)}")
    return result, rc, logpath


def rotate_logs() -> None:
    """Rotate scripts/logs/molecule → molecule.1 → molecule.2; keep at most 3 runs."""
    base = LOG_DIR.parent  # scripts/logs/
    slot2 = base / "molecule.2"
    slot1 = base / "molecule.1"
    if slot2.exists():
        shutil.rmtree(slot2)
    if slot1.exists():
        slot1.rename(slot2)
    if LOG_DIR.exists():
        LOG_DIR.rename(slot1)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_gate() -> list[dict]:
    import yaml  # ansible-core dependency, resolves in the .venv
    data = yaml.safe_load(GATE_FILE.read_text())
    return data if isinstance(data, list) else data.get("gate", [])


def aggregate_exit(results: list[str], rcs: list[int]) -> int:
    if all(r == "pass" for r in results):
        return 0
    # A host-setup problem won't clear on retry, so it isn't reported as transient.
    if any(r in ("fail", "host") for r in results):
        return next((rc for r, rc in zip(results, rcs) if r in ("fail", "host") and rc), 1)
    return EXIT_TRANSIENT  # only transient failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Molecule test harness (see docs/adr/0005).")
    parser.add_argument("action", choices=["test", "converge", "verify", "destroy", "create", "login", "gate"])
    parser.add_argument("scenario", nargs="?", help="molecule scenario (omit for 'gate')")
    parser.add_argument(
        "--platform",
        help="preset(s) or raw distro, comma-separated (default: the scenario's pinned platform, else linux)",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="bypass pre-flight checks (running molecule/VMs); results may be unreliable",
    )
    args = parser.parse_args()

    if args.action != "gate":
        if not args.scenario:
            parser.error(f"action '{args.action}' requires a scenario")
        try:
            platforms = resolve_platforms(args.scenario, args.platform)
        except ValueError as e:
            parser.error(str(e))

    # Run pre-flight for actions that provision VMs and share the fact cache.
    if args.action in ("gate", "test"):
        preflight_check(force=args.force)

    if args.action == "gate":
        rotate_logs()
        results, rcs, misses = [], [], []
        for entry in load_gate():
            scenario = entry["scenario"]
            for platform in entry.get("platforms", ["linux"]):
                result, rc, logpath = run_one("test", scenario, platform)
                results.append(result)
                rcs.append(rc)
                if result != "pass":
                    log_text = logpath.read_text(errors="replace")
                    why = host_problem(log_text) if result == "host" else failure_reason(log_text)
                    misses.append(f"  {result.upper():<9} {scenario}/{platform}  {why}")
        print(f"\n=== gate: {results.count('pass')}/{len(results)} passed ===")
        if misses:
            print("\n".join(misses))
        return aggregate_exit(results, rcs)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    results, rcs = [], []
    for platform in platforms:
        result, rc, _ = run_one(args.action, args.scenario, platform)
        results.append(result)
        rcs.append(rc)
    return aggregate_exit(results, rcs)


if __name__ == "__main__":
    sys.exit(main())
