# Keep the uninstall/upgrade passphrase off the process command line

The uninstall and upgrade tasks pass `--passphrase "{{ s1_agent_passphrase }}"`
to a `root`-run `sentinelctl`, which lands the console-issued passphrase on the
process command line. On Linux `/proc/<pid>/cmdline` is world-readable by
default, so any local unprivileged user can read it during the command window.
We feed the passphrase via the `command` module's `stdin:` parameter (omitting
the flag, which makes `sentinelctl` prompt) so it never reaches argv.

There is an empirical unknown: if `sentinelctl` reads the prompt from `/dev/tty`
rather than stdin, a piped value won't reach it under Ansible's non-TTY
execution. **Fallback:** switch that task to `ansible.builtin.expect` (allocates
a pty), accepting the `pexpect` dependency on the endpoint, rather than reverting
to argv. This is validated by the `uninstall` and `upgrade` molecule scenarios
before merge.

## Consequences

- The producer/consumer tasks that handle the passphrase and API token carry
  **unconditional `no_log: true`** (replacing the `no_log: "{{ ansible_verbosity
< 3 }}"` anti-pattern, which disabled redaction at the routine `-vvv`). Debug
  `Show …` tasks are changed to print structure/status, never the raw secret.
- Windows places the value in `Win32_Process.CommandLine`, which is not
  world-exposed the way `/proc` is; right-sized to Low and handled with
  `no_log: true` (the MSI `MsiHiddenProperties` route belongs to the vendor
  package, not this collection).
