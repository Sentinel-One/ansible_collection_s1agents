# Declare the dev/test Python toolchain in `requirements-dev.txt`, install with uv into one `.venv`

**Status:** accepted — supersedes the Python-environment portion of
[ADR 0005](./0005-molecule-test-harness.md) (the molecule-harness _design_ in 0005
still stands; only "run on the existing `ansible-2.16` pyenv" is replaced).

Onboarding required two **undeclared, machine-specific** pyenv environments
(`ansible-2.16`, `sentinelone`), and scripts, hooks, and docs hardcoded those
personal names via `PYENV_VERSION=…`. No fresh machine could reproduce the
toolchain without manual pyenv setup. We now declare the toolchain in a single
`requirements-dev.txt` at the repo root and install it with **uv** (`uv venv
--python 3.12` + `uv pip install -r requirements-dev.txt`) into one repo-local
`.venv`. Tools run as `.venv/bin/<tool>`. This makes the toolchain reproducible
on any machine and removes every hardcoded personal env name.

## Considered options

- **Reuse the existing pyenv (0005's choice).** Rejected: the env names are
  personal and undeclared; nothing in the repo lets a teammate recreate them.
  0005 chose it to avoid "a second Python toolchain," but the real problem was
  that the _first_ toolchain was never declared — declaring it is what fixes
  onboarding.
- **uv _project mode_ (`pyproject.toml` + `uv.lock`).** Rejected: foreign to
  Ansible collections and would create a second Python manifest alongside the
  ecosystem-native `requirements.txt` flow that CI, ansible-builder, and
  ansible-dev-tools all speak — the "two dependency systems" trap. uv is used
  purely as a fast, pip-compatible **installer**, not a project manager. So the
  invocation is `.venv/bin/<tool>`, **not** `uv run` (which needs project mode).
- **`ansible-dev-tools` umbrella pin.** Rejected in favor of explicit per-tool
  pins: ADT tends to pull a recent ansible-core, and we must hold **2.16**.

## Consequences

- The toolchain is version-pinned in `requirements-dev.txt` (ansible-core 2.16.19,
  ansible-lint, yamllint, molecule `<25.2.0`, molecule-plugins, python-vagrant,
  pywinrm). `pre-commit` is the sole deliberate version change (`>=3.5,<4`, off
  the abandoned 2.19.0).
- `pre-commit` remains the orthogonal hook runner (Node/prettier + trufflehog per
  [ADR 0006](./0006-linting-toolchain.md)) but is installed **into the same
  `.venv`**, so there is one PATH for every tool.
- Two prerequisites live outside pip and must be installed per machine: **uv**
  (the installer) and **trufflehog** (the secret-scan binary; prettier's Node is
  provisioned by pre-commit itself).
- `scripts/molecule.py` no longer sets `PYENV_VERSION`; it prepends `.venv/bin` to
  `PATH` so molecule and the `ansible-playbook`/`ansible` it spawns all resolve to
  the `.venv` (resolution is PATH-based — there is no `ansible.cfg` or pinned
  interpreter in the repo).
- CI's `ci-setup` composite action (`.github/actions/ci-setup/action.yml`) now
  bootstraps the same `requirements-dev.txt`-declared toolchain via uv, so CI and
  local dev share one `.venv` build instead of CI's own inline-pip install. This
  landed as part of the GitHub-hosted KVM/libvirt cloud-runner migration (see
  `.scratch/github-hosted-runners/PRD.md`), not as part of this ADR's original
  scope.
