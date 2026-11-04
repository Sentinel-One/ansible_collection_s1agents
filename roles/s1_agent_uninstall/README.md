# S1 Agent Uninstall

[![GitHub license](https://badgen.net/github/license/Sentinel-One/ansible_collection_s1agents)](https://github.com/Sentinel-One/ansible_collection_s1agents/blob/main/LICENSE)
[![Molecule CI](https://github.com/Sentinel-One/ansible_collection_s1agents/actions/workflows/s1_agent_uninstall.yml/badge.svg)](https://github.com/Sentinel-One/ansible_collection_s1agents/actions/workflows/s1_agent_uninstall.yml)

The `s1_agent_uninstall` role uninstalls the SentinelOne agent.

## Requirements

A valid SentinelOne license, access to the SentinelOne Management Console and access to the SentinelOne installation packages are required.

## Role Variables

```yaml
s1_management_console: https://<management fqdn>
```

This is mandatory and is the URL to your SentinelOne management console.

```yaml
s1_api_token:
```

This is mandatory and is the API token[^1] associated with the user which will running the role.

[^1]: See the SentinelOne KnowledgeBase article [Generating API Tokens](https://community.sentinelone.com/s/article/000005262).

```yaml
s1_windows_use_uninstall_exe: false
```

Windows only. By default the agent is uninstalled through its MSI package by product GUID, and if that fails the role retries with the agent's own `uninstall.exe` and the passphrase. Set this to `true` to skip the MSI uninstall and use `uninstall.exe` directly. It was called `s1_forced_remove` before; the old name is rejected with a message naming the new one.

On Linux the agent is removed with `sentinelctl control uninstall`, authorised by the endpoint's passphrase. There is no forced remove: agent 25.1 and newer can be protected by the kernel (BPF with LSM), which blocks deleting the agent, and `s1_forced_remove: true` is rejected ([ADR 0014](../../docs/adr/0014-remove-linux-forced-remove.md)). If the uninstall fails on either OS, the host fails; see the Knowledge Base article [uninstalling the agent when the normal uninstall fails](https://community.sentinelone.com/s/article/000005374).

### Variables from dependencies

No additional variables must be defined. However, the [s1_agent_common](../s1_agent_common/) role defines common variables including working directories.

#### s1_agent_common

```yaml
s1_tmp_linux: /tmp/s1_install
s1_tmp_windows: "{{ ansible_env.TEMP}}\\s1_install"
s1_validate_certs: true
```

## Dependencies

- [s1_agent_info](../s1_agent_info/) role: Gathers basic information about the SentinelOne agent.
- [s1_mgmt_get_passphrase](../s1_mgmt_get_passphrase/) role: retrieves the agent's unique passphrase from the management console.
- [s1_agent_common](../s1_agent_common/README.md) role: configures common variables for all roles in the collection
- [ansible.windows](https://docs.ansible.com/ansible/latest/collections/ansible/windows/index.html)
- [ansible.posix](https://docs.ansible.com/ansible/latest/collections/ansible/posix/index.html)

## Example Playbooks

### Uninstall the SentinelOne agent using sentinelctl commands

```yaml
---
- name: Uninstall the SentinelOne agent
  hosts: all
  vars:
    s1_management_console: https://<management fqdn>
    s1_api_token: REDACTED
  tasks:
    - name: Include s1_agent_uninstall
      ansible.builtin.include_role:
        name: s1_agent_uninstall
```

### Uninstall the SentinelOne agent on Windows with its own uninstall.exe

```yaml
---
- name: Uninstall the SentinelOne agent with uninstall.exe
  hosts: windows
  vars:
    s1_windows_use_uninstall_exe: true
  tasks:
    - name: Include s1_agent_uninstall
      ansible.builtin.include_role:
        name: s1_agent_uninstall
```

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
