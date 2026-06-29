# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Collection Overview

This is the `sentinelone.s1agents` Ansible collection (`galaxy.yml`) that manages the full lifecycle of the SentinelOne agent on Linux and Windows endpoints. It interacts with both target endpoints (via Ansible modules) and the SentinelOne Management Console (via REST API using `s1_api_token`).

## Roles

| Role | Purpose |
|------|---------|
| `s1_agent_common` | Loads OS-specific vars (distro package names, product IDs); must run before all other roles |
| `s1_agent_info` | Gathers installed agent status without making changes |
| `s1_agent_download` | Downloads agent packages from the Management Console API to `s1_download_path` on the controller |
| `s1_agent_install` | Installs the agent package on endpoints |
| `s1_agent_upgrade` | Upgrades an existing agent; handles the 2-step upgrade path required for Linux ≥25.1.3 |
| `s1_agent_uninstall` | Removes the agent; requires passphrase retrieval on newer agents |
| `s1_agent_uuid` | Reports agent UUIDs from the management console |
| `s1_import_gpg_key` | Imports the SentinelOne GPG key on RPM-based systems |
| `s1_mgmt_get_passphrase` | Fetches per-endpoint uninstall/upgrade passphrase from the Management Console API |

`s1_agent_common` loads vars from `roles/s1_agent_common/vars/<os_family>.yml` (e.g. `redhat.yml`, `debian.yml`, `windows.yml`, `suse.yml`). The `windows.yml` file contains the `s1_product_id` map (version→GUID) that drives Windows idempotence — this needs periodic updates as new agent versions release.

## Key Variables

- `s1_management_console` — URL of the SentinelOne console
- `s1_api_token` — API token (never commit; pass via vault or env)
- `s1_agent_site_token` — Site token for registering new agents
- `s1_download_path` — Controller-local cache dir (default `/tmp/s1_agent_cache`)
- `s1_agent_version` — Specific agent version to install/upgrade to
- `s1_validate_certs` — Set `false` for on-prem consoles with self-signed certs

## Linting

The project uses [Trunk](https://docs.trunk.io) to manage linters.

```bash
trunk check          # lint all changed files
trunk check --all    # lint entire repo
trunk fmt            # auto-format
```

Active linters: `yamllint`, `markdownlint`, `prettier`, `ansible-lint` (via checkov), `actionlint`, `trufflehog`.

## Testing with Molecule

Molecule scenarios live in `extensions/molecule/<scenario>/`. All scenarios use the **Vagrant driver** (VirtualBox or libvirt) and require a live SentinelOne Management Console.

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

Each role has a `makefile` with platform-specific targets. Run from within the role directory:

```bash
cd roles/s1_agent_install

make test           # all platforms (RHEL, RHEL6, Ubuntu, SUSE, Windows 2022, Windows 2012R2)
make rhel-test      # Rocky 8 only
make ubuntu-test    # Ubuntu 22.04 only
make suse-test      # OpenSUSE 15 only
make srv2022-test   # Windows Server 2022 (uses winrm_default scenario)
make srv2012r2-test # Windows Server 2012 R2
make clean          # destroy all VMs
```

To run individual molecule steps directly:

```bash
# Linux — uses the scenario matching the role (e.g. "default", "upgrade", "uninstall")
cd extensions
S1_VAGRANT_DISTRO=rocky8 molecule test -s default
S1_VAGRANT_DISTRO=ubuntu2204 molecule converge -s upgrade
S1_VAGRANT_DISTRO=opensuse15 molecule verify -s default

# Windows — uses the "winrm_default" scenario, not "default"
cd extensions
S1_VAGRANT_DISTRO=windows-server-2022-standard S1_VAGRANT_REPO=gusztavvargadr \
  S1_VAGRANT_GROUP=Windows OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES \
  molecule test -s winrm_default
```

> **macOS note:** Windows tests require `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` to avoid a fork-safety crash in the WinRM connection plugin.

### Molecule Scenarios

| Scenario | Tests |
|----------|-------|
| `common` | `s1_agent_common` var loading |
| `default` | Full install → verify |
| `info-installed` / `info-missing` | `s1_agent_info` with/without agent present |
| `download` | Package download from console |
| `upgrade` | Agent upgrade flow |
| `uninstall` | Agent removal with passphrase |
| `uuid` | UUID report generation |
| `gpgkey` | GPG key import on RPM systems |
| `passphrase` | Passphrase retrieval from console |

The `common` scenario (`extensions/molecule/common/`) contains shared Jinja2 templates used by other scenarios (`templates/prepare-basic.yml`, `templates/cleanup-basic.yml`).

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

When adding support for new Windows agent versions, update the `s1_product_id` map in `roles/s1_agent_common/vars/windows.yml` with the new version's GUID. Without this, molecule idempotence tests will falsely fail on the install task.

## Linux 2-Step Upgrade

Agents older than 22.2.2.2 cannot be upgraded directly to versions newer than 22.2.2.2 when using GPG-signed RPMs. The `upgrade` role handles the ≥25.1.3 passphrase requirement. See `playbooks/example_upgrade_linux_with_gpg_signed_package.yml` for the 2-step upgrade pattern.
