# Changelog

## [Unreleased]

### Breaking changes

- **A Windows uninstall now fails when the agent's own `uninstall.exe` cannot be located.** After a failed MSI uninstall, or with `s1_windows_use_uninstall_exe: true`, a missing service registry key used to skip the retry and report success without removing anything.
- **Linux installs refuse an existing, non-empty `s1_agent_custom_install_path` that is not already an agent install.** The installer puts the agent directly in that directory, so a shared directory such as `/srv` would become the agent's install directory. `s1_agent_install` now fails the host before changing anything and asks for a dedicated directory. Reruns over an existing agent install are unaffected.
- **Forced remove is removed on Linux.** A failed `sentinelctl control uninstall` used to be followed by a root delete of the agent's files, and `s1_forced_remove: true` ran that delete on request. Agent 25.1 and newer is protected by the kernel (BPF with LSM), so the delete fails on a healthy agent, and it could delete `s1_agent_custom_install_path`. A failed uninstall now fails the host and points to [KB 000005374](https://community.sentinelone.com/s/article/000005374), as it does on Windows. `s1_forced_remove: true` now fails the host. On Windows the option is renamed `s1_windows_use_uninstall_exe`.
- **Windows installs and upgrades to Agent 26.2 or newer now fail on Windows
  8.1 64-bit, Server / Storage Server 2012 R2 64-bit, and Windows 10 1507 / 1511.** SentinelOne dropped these operating systems effective with Agent
  26.2, and the installer refuses to run on them. `s1_agent_install` and
  `s1_agent_upgrade` now fail the affected host before downloading anything,
  and a play that names no `s1_agent_version` is pinned to 26.1.2.177 on these
  hosts. Other hosts in the play are unaffected, and `s1_agent_info`,
  `s1_agent_uninstall` and `s1_agent_uuid` still work on them. See the
  Amendment in [ADR 0008](./docs/adr/0008-windows-support-tier-routing.md).
- **Fresh installs of pre-23.3 unsigned RPMs are no longer supported.**
  The `rpm -i --nodigest` flag that allowed unsigned packages lacking a header
  digest to install has been removed (see [ADR 0002](./docs/adr/0002-remove-eol-accommodations-not-gate.md)).
  **Upgrades from old agent versions are unaffected** — upgrades run through
  `sentinelctl control upgrade`, not `rpm -i`, and the documented two-step
  upgrade path additionally uses the GPG-signed branch. A signed pre-23.3
  package can still be fresh-installed via the GPG-signed branch.

### Added

- **Windows installation telemetry opt-out.** Set `s1_disable_install_telemetry: true` to pass `INSTALLATION_TELEMETRY=FALSE` to the installer on install and upgrade, for both `.exe` and MSI packages and on all Windows tiers. The default is unchanged. A non-boolean value fails input validation. Upgrading with the `.exe` package is unverified until a CI VM run shows the installer accepts the flag.

### Changed

- **Windows proxy and data path validation follows the installer KB.** On Windows, `s1_agent_management_proxy` and `s1_agent_dv_proxy` also accept `auto`, `system` and `user,<fallback>[:<port>]`, and `s1_agent_dv_proxy` accepts `single`. Linux proxy handling is unchanged, except that the shape check now matches the whole value, so a value such as `host,x` is rejected. A Windows `s1_agent_custom_install_path` over 150 characters or with non-ASCII characters is rejected. Install fails early when the data path drive is not the system drive and does not exist, is not NTFS, or has less than 4 GB free.

### Security

- **Tempfile work directories (issue 01).** Agent packages are now staged in an
  unpredictable, root/SYSTEM-owned, mode-`0700` per-run directory created via
  `ansible.builtin.tempfile` / `ansible.windows.win_tempfile`, closing the
  TOCTOU race on the managed endpoint. `s1_tmp_linux` / `s1_tmp_windows` are
  now optional operator overrides (undefined by default). The resolved path is
  exposed as the `s1_work_dir` fact. The controller-local download cache
  (`s1_download_path`) is hardened to mode `0700`.
  See [ADR 0004](./docs/adr/0004-tempfile-work-dirs.md).

- **Unconditional secret redaction (issue 02).** All verbosity-gated
  `no_log: "{{ ansible_verbosity < 3 }}"` replaced with unconditional
  `no_log: true` so routine `-vvv` debugging never leaks the API token or
  passphrase. Debug `Show` tasks now emit a status/count summary instead of
  the raw registered result.
  See [ADR 0003](./docs/adr/0003-passphrase-off-argv.md).

- **Passphrase off the command line (issue 03).** Linux `sentinelctl` upgrade
  and uninstall tasks no longer pass the passphrase on argv (readable via
  `/proc/<pid>/cmdline`). The passphrase is now delivered via the `command`
  module's `stdin:` parameter. The Linux uninstall command task and Windows
  `win_package` uninstall tasks carry `no_log: true`.
  See [ADR 0003](./docs/adr/0003-passphrase-off-argv.md).

- **RPM digest verification restored (issue 04).** `--nodigest` removed from
  the unsigned-branch `rpm -i` install; the invocation is now in `argv:` list
  form (no shell-parsing of the package path).
  See [ADR 0002](./docs/adr/0002-remove-eol-accommodations-not-gate.md).

- **Centralized input validation (issue 05).** `s1_agent_common` now validates
  operator-supplied inputs (`s1_agent_management_proxy`, `s1_agent_dv_proxy`,
  `s1_agent_customer_id`, `s1_agent_custom_install_path`, `s1_agent_src`)
  with conditional `assert` tasks. Runs without the variable set are
  unaffected. See [ADR 0001](./docs/adr/0001-trust-model.md).

- **Upgrade role no longer uses the site token.** The Windows upgrade MSI and new-EXE argument templates no longer pass `s1_agent_site_token` (`SITE_TOKEN=` / `-t`), removing an unvalidated value from the upgrade command line. The variable is now ignored by `s1_agent_upgrade`; existing inventories need no change. See [ADR 0013](./docs/adr/0013-upgrade-role-takes-no-site-token.md).

- **Input validation bypasses closed.** `s1_agent_custom_install_path` is now checked across its whole value (a trailing `" TRANSFORMS=...` could previously slip past), is refused under operating-system directories such as `/usr/lib` or `/etc/ssl` on Linux, and has a Windows rule that accepts drive-letter paths like `C:\S1Data` (previously every Windows value was rejected). The proxy variables additionally refuse `"` and `=`. Validation now runs immediately after the collection's read-only fact gather so the OS-specific rule can apply. See [ADR 0001](./docs/adr/0001-trust-model.md).

- **CI hardening documentation (issue 06).** Documented unsafe CI patterns
  (unquoted input injection, floating `requirements.txt`, PR-head code on
  self-hosted runners) and their fixes in `docs/ci-hardening.md` for future
  reference.

## Version 0.3.0 - 2023-03-06

### Added

- Support for managing the agent on Windows
- s1_agent_info role
- s1_agent_common role

### Changed

- To reduce duplication most variables used by the roles are now defined in the `s1_agent_common` role
- All roles now depend on the `s1_agent_common` role to set up common variables, tasks and handlers
- The `setup` module is called by default to gather the minimum viable set of facts for the collection to run successfully
- Streamlined workflows

### Deprecated

- Using the `s1_agent_uuid` role solely for looking up the agent's UUID is now deprecated, as this functionality has been moved to the `s1_agent_info` role. Going forward, the `s1_agent_uuid` role will be maintained solely for the purpose of generating a CSV report of agent UUIDs.

## Version 0.2.0 - 2022-07-22

### Added

- GitHub Action Workflows for all roles

### Changed

- Broke existing roles out. Each role has one job to do, there are now roles for:
  - installing S1 agent
  - updating S1 agent
  - uninstalling S1 agent
  - downloading S1 agent
  - retrieving the S1 agent's UUID
  - retrieving the S1 agents passphrase from the management console

## 2022-05-10

added the s1_agent_install role to the collection
switched s1_agent_download to use dynamic includes for getting the agent URI
re-worked molecule config
