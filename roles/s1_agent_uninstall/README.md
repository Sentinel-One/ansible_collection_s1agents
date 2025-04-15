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
s1_forced_remove: false
```

### Variables from dependencies

No additional variables must be defined. However, the [s1_agent_common](../s1_agent_common/) role defines common variables including working directories.

#### s1_agent_common

```yaml
s1_tmp_linux: /tmp/s1_install
s1_tmp_windows: "{{ ansible_env.TEMP}}\\s1_install"
s1_validate_certs: true
```

## Dependencies

* [s1_agent_info](../s1_agent_info/) role: Gathers basic information about the SentinelOne agent.
* [s1_mgmt_get_passphrase](../s1_mgmt_get_passphrase/) role: retrieves the agent's unique passphrase from the management console. Note: this dependency does not exist for Linux agents when `s1_forced_remove` is `true`.
* [s1_agent_common](../s1_agent_common/README.md) role: configures common variables for all roles in the collection
* [ansible.windows](https://docs.ansible.com/ansible/latest/collections/ansible/windows/index.html)
* [ansible.posix](https://docs.ansible.com/ansible/latest/collections/ansible/posix/index.html)

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

### Uninstall the SentinelOne agent using Linux OS commands

```yaml
---
- name: Uninstall the SentinelOne agent
  hosts: all
  vars:
    s1_forced_remove: true
  tasks:
    - name: Include s1_agent_uninstall
      ansible.builtin.include_role:
        name: s1_agent_uninstall
```

This is mostly useful when cleaning up a corrupted install.

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
