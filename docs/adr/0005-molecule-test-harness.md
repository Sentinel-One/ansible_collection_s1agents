# Molecule test harness: a thin Python orchestrator run on the existing pyenv

**Status update:** the harness _design_ below (thin orchestrator, gate matrix,
exit-75 transient signalling) still stands. The **Python-environment** choice —
"run on the existing `ansible-2.16` pyenv, deliberately not uv" — is
**superseded by [ADR 0007](./0007-uv-managed-venv-toolchain.md)**: the toolchain
is now declared in `requirements-dev.txt` and installed with uv into one
repo-local `.venv`, and `scripts/molecule.py` sets `PATH` (not `PYENV_VERSION`).

The **config precedence** decision below is also superseded: the script no
longer parses an env-file itself. Secrets live in a gitignored `molecule.env`
of `KEY=op://vault/item/field` references at the repo root, and the invocation
is wrapped in 1Password's `op run --env-file="molecule.env" -- ...`, which
resolves the references into real environment variables before Python starts.
`scripts/molecule.py` never reads or parses that file — it only ever sees
`os.environ`. Precedence is now just: process env (`op run`'s injected secrets
included) < `--platform` preset.

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

- **Config precedence:** ~~optional env-file (`molecule.env`, dev/agent) < process
  environment (CI secrets win) < `--platform` preset (overrides `S1_VAGRANT_*`).~~
  Superseded — see status update above.
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
