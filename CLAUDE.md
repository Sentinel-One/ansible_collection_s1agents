# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Collection Overview

This is the `sentinelone.s1agents` Ansible collection (`galaxy.yml`) that
manages the full lifecycle of the SentinelOne agent on Linux and Windows
endpoints. It interacts with both target endpoints (via Ansible modules) and the
SentinelOne Management Console (via REST API using `s1_api_token`).

## Roles

| Role                     | Purpose                                                                                          |
| ------------------------ | ------------------------------------------------------------------------------------------------ |
| `s1_agent_common`        | Loads OS-specific vars (distro package names, product IDs); must run before all other roles      |
| `s1_agent_info`          | Gathers installed agent status without making changes                                            |
| `s1_agent_download`      | Downloads agent packages from the Management Console API to `s1_download_path` on the controller |
| `s1_agent_install`       | Installs the agent package on endpoints                                                          |
| `s1_agent_upgrade`       | Upgrades an existing agent; handles the 2-step upgrade path required for Linux ≥25.1.3           |
| `s1_agent_uninstall`     | Removes the agent; requires passphrase retrieval on newer agents                                 |
| `s1_agent_uuid`          | Reports agent UUIDs from the management console                                                  |
| `s1_import_gpg_key`      | Imports the SentinelOne GPG key on RPM-based systems                                             |
| `s1_mgmt_get_passphrase` | Fetches per-endpoint uninstall/upgrade passphrase from the Management Console API                |

`s1_agent_common` loads vars from `roles/s1_agent_common/vars/<os_family>.yml`
(e.g. `redhat.yml`, `debian.yml`, `windows.yml`, `suse.yml`). The `windows.yml`
file contains the `s1_product_id` map (version→GUID) that drives Windows
idempotence — this needs periodic updates as new agent versions release.

## Key Variables

- `s1_management_console` — URL of the SentinelOne console
- `s1_api_token` — API token (never commit; pass via vault or env)
- `s1_agent_site_token` — Site token for registering new agents
- `s1_download_path` — Controller-local cache dir (default
  `/tmp/s1_agent_cache`)
- `s1_agent_version` — Specific agent version to install/upgrade to
- `s1_validate_certs` — Set `false` for on-prem consoles with self-signed certs

## Linting

Linting is split by domain — see `docs/adr/0006-linting-toolchain.md`. Run both
before committing.

**pre-commit** drives prettier (Markdown + JSON formatting) and trufflehog
(committed-secret scanning). The git hooks are intentionally **not** installed;
run on demand. pre-commit provisions its own Node runtime for prettier, so no
system Node is required. trufflehog must be installed locally.

```bash
pre-commit run --all-files   # prettier (md/json) + trufflehog secret scan
```

Prettier formats Markdown and JSON only; all YAML is excluded (`.prettierignore`)
and owned by ansible-lint.

**ansible-lint** checks Ansible correctness (FQCN, task naming, idempotence,
`production` profile) and bundles yamllint for YAML style. Runs from the
project `.venv` (see below):

```bash
.venv/bin/ansible-lint
```

## Python Environment

The dev/test toolchain (ansible-core, ansible-lint, yamllint, molecule,
pre-commit, etc.) is declared in `requirements-dev.txt` at the repo root and
installed into a single repo-local `.venv` with **uv** (used as a fast,
pip-compatible installer — not uv project mode). See
`docs/adr/0007-uv-managed-venv-toolchain.md` for the rationale.

Bootstrap a fresh clone:

```bash
# prerequisites (once per machine): uv + trufflehog
#   uv:         curl -LsSf https://astral.sh/uv/install.sh | sh
#   trufflehog: brew install trufflehog   (or per-OS install)

uv venv --python 3.12
uv pip install -r requirements-dev.txt
.venv/bin/ansible-galaxy collection install -r requirements.yml
.venv/bin/pre-commit install-hooks    # provisions prettier's Node runtime
```

Every tool then runs as `.venv/bin/<tool>` (`.venv/bin/ansible-lint`,
`.venv/bin/yamllint`, `.venv/bin/molecule`, `.venv/bin/pre-commit`) — no
activation needed. `.venv/` is gitignored; never commit it.

To confirm the manifest still installs cleanly and every tool resolves, without
spinning up any molecule VMs:

```bash
uv run scripts/smoke_check.py
```

This builds a throwaway venv, checks each pinned tool reports a version, and
deletes the throwaway venv when done — it never touches your working `.venv`.

## Testing with Molecule

Molecule scenarios live in `extensions/molecule/<scenario>/`. All scenarios use
the **Vagrant driver** (VirtualBox or libvirt) and require a live SentinelOne
Management Console.

### Required Environment Variables

```bash
export S1_MANAGEMENT_CONSOLE=https://your-console.sentinelone.net
export S1_AGENT_SITE_TOKEN=<site-token>
export S1_API_TOKEN=<api-token>
export S1_DOWNLOAD_PATH=/tmp/s1_agent_cache   # optional, has default

# VM configuration (all have defaults)
export S1_VAGRANT_DISTRO=rocky8               # Vagrant box suffix
export S1_VAGRANT_REPO=roboxes               # Vagrant box namespace
export S1_VAGRANT_GROUP=Linux                # Ansible group: Linux or Windows
export S1_MOLECULE_HOSTNAME=blue-firefly     # VM hostname prefix
export VAGRANT_DEFAULT_PROVIDER=virtualbox   # or libvirt
```

### Running Tests

All tests run through `scripts/molecule.py`. Run from the repo root through the
project `.venv` (see [Python Environment](#python-environment)).

```bash
# Run all gate scenarios (same as CI)
.venv/bin/python scripts/molecule.py gate

# Run a single scenario against one platform preset
.venv/bin/python scripts/molecule.py test <scenario> --platform <preset>

# Run a single scenario against all its gate platforms
.venv/bin/python scripts/molecule.py test <scenario>
```

**Platform presets:**

| Preset       | Distro              | Notes                                |
| ------------ | ------------------- | ------------------------------------ |
| `rocky8`     | Rocky Linux 8       | Default Linux (roboxes)              |
| `ubuntu2204` | Ubuntu 22.04        | (roboxes)                            |
| `opensuse15` | OpenSUSE Leap 15    | (roboxes)                            |
| `windows`    | Windows Server 2022 | gusztavvargadr box; sets WinRM group |

**Logs** are written to `.molecule-logs/<scenario>-<platform>.log`. Exit code 75
means transient infra (proxy auth expired or VM SSH reset) — re-authenticate and
retry rather than treating it as a test failure.

**macOS note:** Windows tests set `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`
automatically.

To run raw molecule steps for development (from `extensions/`, with the `.venv`
activated so bare `molecule` resolves — `source ../.venv/bin/activate`):

```bash
cd extensions
S1_VAGRANT_DISTRO=rocky8 molecule converge -s default
S1_VAGRANT_DISTRO=ubuntu2204 molecule verify -s upgrade
```

### Molecule Scenarios

All scenarios live in `extensions/molecule/<scenario>/`. The gate matrix is in
`scripts/gate.yml`.

| Scenario         | Platforms       | Tests                                 |
| ---------------- | --------------- | ------------------------------------- |
| `common`         | Linux + Windows | `s1_agent_common` var loading         |
| `default`        | Linux + Windows | Full install → verify                 |
| `download`       | Linux + Windows | Package download from console         |
| `gpgkey`         | Linux (RPM)     | GPG key import                        |
| `info-installed` | Linux + Windows | `s1_agent_info` with agent present    |
| `info-missing`   | Linux + Windows | `s1_agent_info` without agent present |
| `passphrase`     | Linux + Windows | Passphrase retrieval from console     |
| `uninstall`      | Linux + Windows | Agent removal with passphrase         |
| `upgrade`        | Linux + Windows | Agent upgrade flow                    |
| `uuid`           | Linux + Windows | UUID report from console              |

`extensions/molecule/common/` also provides shared Jinja2 templates
(`templates/prepare-basic.yml`, `templates/cleanup-basic.yml`) used by other
scenarios.

## Building the Collection

```bash
ansible-galaxy collection build          # creates sentinelone-s1agents-<version>.tar.gz
ansible-galaxy collection install sentinelone-s1agents-*.tar.gz --force
```

## Installing Dependencies

```bash
ansible-galaxy collection install -r requirements.yml
```

## Windows Idempotence Note

When adding support for new Windows agent versions, update the `s1_product_id`
map in `roles/s1_agent_common/vars/windows.yml` with the new version's GUID.
Without this, molecule idempotence tests will falsely fail on the install task.

## Linux 2-Step Upgrade

Agents 22.2 and older cannot be upgraded directly to newer versions. See
`playbooks/example_upgrade_linux_with_gpg_signed_package.yml` for the 2-step
upgrade pattern.

## Agent skills

### Issue tracker

Issues and PRDs live as local markdown under `.scratch/<feature>/` (no external
PR triage surface). See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical states with default strings (needs-triage, needs-info,
ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at the repo root. See
`docs/agents/domain.md`.
