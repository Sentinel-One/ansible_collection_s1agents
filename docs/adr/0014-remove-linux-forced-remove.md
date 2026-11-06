# Remove forced remove on Linux

`s1_agent_uninstall` used to rescue any failure of the Linux graceful uninstall (`sentinelctl control uninstall`) by deleting the agent's files, service and package records as root, and `s1_forced_remove: true` ran that delete on request. A wrong or stale passphrase was enough to trigger the rescue, and the delete followed `s1_agent_custom_install_path`, which made it a route to TSS-25. Starting with agent 25.1 the agent can also be protected by the kernel (BPF with LSM), so the delete no longer works on a healthy agent: stopping and disabling the service fails with `Access denied`. Fixing that means disabling BPF with LSM and restarting the host, which a playbook should not do. We **remove forced remove on Linux**. The only Linux removal is the agent's own graceful uninstall, and a failure fails the host with a pointer to the [Knowledge Base article](https://community.sentinelone.com/s/article/000005374).

## Considered options

- **Keep the automatic escalation.** Rejected: an unrequested root delete, and it hid the real failure (usually the passphrase).
- **Keep forced remove behind `s1_forced_remove`, with a symlink-derived target.** Rejected: it cannot run against a healthy agent on 25.1 or newer, so it would work only for older agents and broken installs, and it is destructive code that can no longer be tested against a real agent.
- **Remove it on Linux (chosen).** The destructive path goes away, so TSS-25 is closed by deleting the code, not by guarding it.

## Consequences

- Breaking for anyone who relied on the escalation or on `s1_forced_remove: true` to clean up broken or pre-25.1 agents. Central validation fails the host before any change when `s1_forced_remove` is set to `true`, naming the removal and the KB article, because Ansible cannot deprecate a variable and the option would otherwise be ignored silently.
- Windows keeps its second uninstall mechanism (the agent's own `uninstall.exe` with the passphrase), which is not destructive and is not affected by kernel protection. The variable is renamed `s1_windows_use_uninstall_exe`, and `s1_forced_remove` is rejected there too, with a message naming the new variable.
- A failed uninstall on either OS fails the host with a pointer to the KB article.
