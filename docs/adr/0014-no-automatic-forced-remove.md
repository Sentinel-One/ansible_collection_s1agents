# A failed graceful uninstall does not escalate to forced remove

On Linux, `s1_agent_uninstall` used to rescue any failure of the graceful uninstall (`sentinelctl control uninstall`) by running forced remove, which deletes the agent's files, service and package records as root. A wrong or stale passphrase was enough to trigger it, so a typo became an unrequested wipe, and it was a second route to the custom-install-path delete in TSS-25. We now **fail the host when the graceful uninstall fails** and run forced remove only when the operator sets `s1_forced_remove: true`.

## Considered options

- **Keep the automatic escalation.** Rejected: destructive root deletes should be an explicit operator choice, and the escalation hid the real failure (usually the passphrase).
- **Escalate only on specific failure modes** (e.g. `sentinelctl` missing). Rejected: it means classifying `sentinelctl` output, which is brittle across agent versions, for little gain over an explicit flag.

## Consequences

- Breaking for anyone who relied on the escalation to clean up broken agents. They now rerun with `s1_forced_remove: true`, and the failure message says so.
- Windows is unaffected. Its rescue retries with the agent's own `uninstall.exe` and the passphrase, which is not destructive.
