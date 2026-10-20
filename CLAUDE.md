# CLAUDE.md

## Build / Lint / Test

All tools run from the repo-local `.venv`. Do not activate it. uv is the installer only, not uv project mode (ADR 0007).

- Bootstrap: `uv venv --python 3.12 && uv pip install -r requirements-dev.txt`, then `.venv/bin/ansible-galaxy collection install -r requirements.yml` and `.venv/bin/pre-commit install-hooks`. Install `uv` and `trufflehog` once per machine.
- `uv run scripts/smoke_check.py` — checks that `requirements-dev.txt` installs and each tool runs. It uses a temporary venv and does not change `.venv`.
- `.venv/bin/ansible-lint` — Ansible rules (`production` profile) and yamllint. CI's required Lint job runs this.
- `.venv/bin/pre-commit run --all-files` — prettier (Markdown and JSON only) and the trufflehog secret scan. The git hooks are not installed. Run it on demand.
- `uv run scripts/test_molecule.py` — unit tests for `scripts/molecule.py`.
- `.venv/bin/python scripts/molecule.py gate` — runs every scenario in `scripts/gate.yml`.
- `.venv/bin/python scripts/molecule.py test <scenario> [--platform <preset>]` — runs one scenario. Presets are in `PRESETS` in `scripts/molecule.py`. Without `--platform`, the run uses the pin in `PINNED_PLATFORMS`, else `linux` (rocky8).
- `ansible-galaxy collection build` — builds `sentinelone-s1agents-<version>.tar.gz`.

Run ansible-lint and pre-commit before you commit (ADR 0006). A `PreToolUse` hook also runs ansible-lint and trufflehog before each `git push`.

### Molecule

- Scenarios are in `extensions/molecule/<scenario>/`. Shared templates are in `extensions/molecule/common/templates/`.
- Most scenarios use the Vagrant driver and a live Management Console. They need `S1_MANAGEMENT_CONSOLE`, `S1_AGENT_SITE_TOKEN` and `S1_API_TOKEN`. The `S1_VAGRANT_*`, `S1_MOLECULE_HOSTNAME` and `VAGRANT_DEFAULT_PROVIDER` variables have defaults.
- **The molecule VMs are AMD64.** On an ARM64 host (`uname -m` shows `arm64` or `aarch64`), do not run VM scenarios locally. Push the branch, then use the CI runs that the push starts as the test result. VM-less scenarios still run locally.
- `windows-tier-matrix` and `input-validation` are VM-less (preset `none`). They need no console and no `S1_*` variables.
- Logs go to `scripts/logs/molecule/<scenario>-<platform>.log`.
- Exit code 75 means a transient infrastructure failure (expired proxy auth or an SSH reset). Re-authenticate and run again. It is not a test failure.
- `HOST-SETUP` means a problem on this machine, not in the code. The output names the fix.
- `windows-legacy-plus`: the local run is the gate for the Legacy Plus tier. On hosted CI it always fails, and that failure is expected. Validate changes to Legacy Plus install or upgrade code locally, on an AMD64 host. This scenario needs `sshpass` on the controller. Its version pins and `ANSIBLE_SKIP_TAGS` are necessary (ADR 0011).

## Architecture

The `sentinelone.s1agents` collection manages the SentinelOne agent lifecycle on Linux and Windows endpoints. It calls the Management Console REST API with `s1_api_token`.

- `s1_agent_common` must run before the other roles. It loads `roles/s1_agent_common/vars/<os_family>.yml` and runs `tasks/validate_inputs.yml` (ADR 0001).
- The other roles: `s1_agent_info`, `s1_agent_download`, `s1_agent_install`, `s1_agent_upgrade`, `s1_agent_uninstall`, `s1_agent_uuid`, `s1_import_gpg_key`, `s1_mgmt_get_passphrase`. Each role has a `README.md`.
- Windows support tiers: ADR 0008.

## Conventions

- **Harness scripts go in `scripts/`.** Do you write a script to test or prove a change? Then save it in `scripts/` and commit it with the change. Do not leave it in the scratchpad. Give it a PEP 723 block and run it with `uv run`. Ansible test cases go in a molecule scenario instead.
- **Windows product IDs:** for each new Windows agent version, add its GUID to `s1_product_id` in `roles/s1_agent_common/vars/windows.yml`. If you do not, the idempotence check fails on the install task.
- **Linux 2-step upgrade:** an agent older than 22.2.2.2 cannot go directly to 22.3 or later. See `playbooks/example_upgrade_linux_with_gpg_signed_package.yml`.
- **Secrets:** do not commit `s1_api_token` or site tokens. Pass them through vault or the environment.
- **Markdown:** do not hard-wrap prose. Prettier does not format YAML. ansible-lint owns YAML.

## Agent docs

- Domain: `CONTEXT.md` and `docs/adr/`. See `docs/agents/domain.md`.
- Issues and PRDs: local Markdown in `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.
- Triage labels: `docs/agents/triage-labels.md`.
