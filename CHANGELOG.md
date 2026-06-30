# Changelog

## [Unreleased]

### Breaking changes

- **Fresh installs of pre-23.3 unsigned RPMs are no longer supported.**
  The `rpm -i --nodigest` flag that allowed unsigned packages lacking a header
  digest to install has been removed (see [ADR 0002](./docs/adr/0002-remove-eol-accommodations-not-gate.md)).
  **Upgrades from old agent versions are unaffected** — upgrades run through
  `sentinelctl control upgrade`, not `rpm -i`, and the documented two-step
  upgrade path additionally uses the GPG-signed branch. A signed pre-23.3
  package can still be fresh-installed via the GPG-signed branch.

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
