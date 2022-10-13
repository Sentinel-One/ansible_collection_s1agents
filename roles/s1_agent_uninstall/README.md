# S1 Agent Uninstall

[![GitHub license](https://badgen.net/github/license/s1-nathangerhart/ansible_collection_s1agent)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/blob/main/LICENSE)
[![Molecule CI](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_uninstall.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_uninstall.yml)

Uninstalls the SentinelOne agent.

## Requirements

None

## Role Variables

| Variable | Description | Required |
|----------|-------------|----------|
| s1_management_console | URL to the SentinelOne management console. | &check;[^1] |
| s1_api_token | API token with permissions lookup up agent passphrases. | &check;[^1] |
| s1_forced_remove | Remove the SentinelOne agent using Linux OS commands instead of sentinelctl. Consult with support before setting this to `true`. |  |

[^1]: When `s1_force_remove` is `true` then neither `s1_management_console` nor `s1_api_token` are required.

## Dependencies

* [s1_mgmt_get_passphrase](../s1_mgmt_get_passphrase/README.md) role: retrieves the agent's unique passphrase from the management console. Requires that `s1_management_console` and `s1_api_token` are defined. Note: this dependency does not exist when `s1_forced_remove` is `true`.

## Example Playbooks

### Uninstall the SentinelOne agent using sentinelctl commands

```yaml
---
- name: Uninstall the SentinelOne agent
  hosts: all
  vars:
    s1_management_console: https://usea1-support3.sentinelone.net
    s1_api_token: REDACTED
  tasks:
    - name: Include s1_agent_uninstall
      include_role:
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
      include_role:
        name: s1_agent_uninstall
```

This is mostly useful when cleaning up a corrupted install.

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
