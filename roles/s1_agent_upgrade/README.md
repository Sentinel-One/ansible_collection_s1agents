# S1 Agent Upgrade

[![GitHub license](https://badgen.net/github/license/s1-nathangerhart/ansible-collection-s1singularity)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/blob/main/LICENSE)
[![Molecule CI](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_upgrade.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_upgrade.yml)

Upgrades an existing SentinelOne Agent installed on Linux endpoints.

## Requirements

A valid SentinelOne license, access to the SentinelOne Management Console and access to the SentinelOne installation packages are required.

Inventory hosts on which the agent is being installed must be running on a supported Operating System and meet its [minimum system requirements](https://support.sentinelone.com/hc/en-us/articles/360004196614-System-Requirements).

## Role Variables

| Variable | Description | Required |
|----------|-------------|----------|
| s1_management_console | URL to the SentinelOne management console. | &check; |
| s1_api_token | API token with permissions download agent packages and lookup up agent passphrases. | &check; |
| s1_agent_src | Path to a previously downloaded SentinelOne package to be used for upgrade. | [^1] |
| s1_agent_version | Version of the package specified by `s1_agent_src`. | [^1] |

[^1]: When `s1_agent_src` is defined, then the `s1_agent_download` role will be skipped. `s1_agent_version` must also be defined.

## Dependencies

* [s1_agent_download](../s1_agent_download/README.md) role: automatically downloads the SentinelOne agent if `s1_agent_src` is unset. Requires that the `s1_management_console` and `s1_api_token` variables are defined.
* [s1_import_rpm_key](../s1_import_rpm_key/README.md) role: only executed on the Red Hat family of operating systems.
* [s1_mgmt_get_passphrase](../s1_mgmt_get_passphrase/README.md) role: retrieves the agent's unique passphrase from the management console. Requires that `s1_management_console` and `s1_api_token` are defined. Note: this dependency does not exist when `s1_forced_remove` is `true`.

## Example Playbooks

### Upgrade SentinelOne from a package that was previously downloaded

Upgrade the SentinelOne Agent from a package that has already been downloaded and staged on the Ansible Controller host. Note when the `s1_agent_src` var is set at the play level the play can only run against inventory hosts that support that package. For example a .deb package can not be installed on Red Hat endpoints. To target a mixed group of endpoints assign the `s1_agent_src` variable at the group_vars or host_vars.

```yaml
---
- name: Upgrade the SentinelOne Agent
  hosts: RedHat_Servers
  vars:
    s1_management_console: https://usea1-support3.sentinelone.net
    s1_agent_src: /software/sentinelone/SentinelAgent_linux_v22_1_2_7.rpm
    s1_agent_version: 22.1.2.7
  tasks:
    - name: Include s1_agent_install
      include_role:
        name: s1_agent_install
```

### Download and upgrade to the latest SentinelOne agent

Automatically download the most recent Generally Available SentinelOne package and upgrade to it. Note, unlike the previous example, this playbook can target a mixed group containing hosts of different platforms and package managers.

```yaml
---
- name: Download and upgrade to the latest SentinelOne Agent
  hosts: all
  vars:
    s1_management_console: https://usea1-support3.sentinelone.net
    s1_api_token: REDACTED
  tasks:
    - name: Include s1_agent_install
      include_role:
        name: s1_agent_install
```

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
