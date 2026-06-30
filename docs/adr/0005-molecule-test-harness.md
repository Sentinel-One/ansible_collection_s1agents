# Molecule test harness: a thin Python orchestrator run on the existing pyenv

Testing is driven through molecule, but invoking it ad hoc produces a different
shell command every time (scenario, env vars, `cd`, `source`, output piping),
which can't be permission-allowlisted, floods stdout, and drifts between the
agent, end users, and CI. We add `scripts/molecule.py`: a thin orchestrator that
sets the environment, runs the `molecule` subprocess, streams output to a
per-target log file under `.molecule-logs/` (gitignored), and prints a compact
PASS/FAIL summary. One stable invocation serves all three consumers and is
allowlistable.

The script is **Python run on the existing `ansible-2.16` pyenv** — invoked as
`PYENV_VERSION=ansible-2.16 python scripts/molecule.py …` — deliberately **not**
`uv`. Python is the right language (layered config precedence, the gate matrix,
log parsing, transient-error detection are awkward in bash/make), but `uv` would
add a second Python toolchain alongside the pyenv that molecule already requires,
purely to run a script that orchestrates that pyenv tool. Reusing the pyenv adds
zero new dependency and keeps `gate.yml` in YAML (PyYAML ships with ansible).

## Decisions

- **Config precedence:** optional env-file (`molecule.env`, dev/agent) < process
  environment (CI secrets win) < `--platform` preset (overrides `S1_VAGRANT_*`).
  No secrets are committed; the same command works for agent, end users, and CI.
- **Platform presets** live in the script (rocky8/linux, ubuntu2204, opensuse15,
  windows); raw distro names pass through. The `gate` matrix (scenarios ×
  platforms) is read from committed `scripts/gate.yml` so it evolves without code
  edits.
- **Exit codes:** `0` pass; molecule's non-zero is propagated for real failures;
  `75` signals **transient infrastructure** (a TLS-inspecting **proxy** resetting
  the connection — `SSL: UNEXPECTED_EOF` — or an SSH `Connection reset` during
  boot) with a re-authenticate-and-retry hint, so CI can auto-retry and a reader
  doesn't chase it as a code defect.

## Consequences

- Committed artifacts use the generic term **proxy** (never a vendor name) to
  avoid leaking environmental details.
- A project permission allowlist entry
  (`Bash(PYENV_VERSION=ansible-2.16 python scripts/molecule.py:*)`) stops the
  per-run prompts.
