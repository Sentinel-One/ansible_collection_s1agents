# S1 Agent Install

[![GitHub license](https://badgen.net/github/license/s1-nathangerhart/ansible-collection-s1singularity)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/blob/main/LICENSE)
[![Molecule CI](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_install.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_install.yml)

Installs the SentinelOne Agent on Linux endpoints.

## Requirements

A valid SentinelOne license, access to the SentinelOne Management Console and access to the SentinelOne installation packages are required.

Inventory hosts on which the agent is being installed must be running on a supported Operating System and meet its [minimum system requirements](https://support.sentinelone.com/hc/en-us/articles/360004196614-System-Requirements).

## Role Variables

| Variable | Description | Required |
|----------|-------------|----------|
| s1_management_console | URL to the SentinelOne management console. | &check; |
| s1_api_token | API token with permissions download agent packages. | &check; |
| s1_agent_site_token | Site or Group token for binding the agent to the management console. | &check; |
| s1_agent_src | Path to a previously downloaded SentinelOne package to be used for upgrade. | [^1] |
| s1_install_unsigned_rpm | Download and install unsigned RPM packages, signed packages are used by default |  |
| s1_agent_auto_start | Controls if the agent auto-starts during install. Default: true |  |
| s1_agent_customer_id | Set a customer specific identifier for the host, AKA Customer ID / External ID |  |
| s1_agent_create_user | Controls if the sentinelone user is created during instal.If true (default), the agent creates the sentinelone user and group when it is installed. If false, the sentinelone user and group must be created manually, see the Knowledge Base for specifics. |  |
| s1_agent_custom_install_path | Change the default install location for the agent |  |
| s1_agent_device_type | Set the device type to `server` or `desktop`. Only applies to Linux endpoints |  |
| s1_agent_management_proxy | If a proxy is required for agent traffic to egress set it here |  |
| s1_agent_dv_proxy | If a proxy is required for agent traffic to egress set it here |  |

[^1]: When `s1_agent_src` is defined, then the `s1_agent_download` role will be skipped.

## Dependencies

* [s1_agent_download](../s1_agent_download/README.md) role: automatically downloads the SentinelOne agent if `s1_agent_src` is unset. Requires that the `s1_management_console` and `s1_api_token` variables are defined.
* [s1_import_rpm_key](../s1_import_rpm_key/README.md) role: only executed on the Red Hat family of operating systems.

## Example Playbooks

### Install SentinelOne from a package that was previously downloaded

Install the SentinelOne Agent from a package that has already been downloaded and staged on the Ansible Controller host. Note when the `s1_agent_src` var is set at the play level the play can only run against inventory hosts that support that package. For example a .deb package can not be installed on Red Hat endpoints. To target a mixed group of endpoints assign the `s1_agent_src` variable at the group_vars or host_vars.

```yaml
---
- name: Install the SentinelOne Agent
  hosts: RedHat_Servers
  vars:
    s1_management_console: https://usea1-support3.sentinelone.net
    s1_agent_site_token: REDACTED
    s1_agent_src: /software/sentinelone/SentinelAgent_linux_v22_1_2_7.rpm
  tasks:
    - name: Include s1_agent_install
      include_role:
        name: s1_agent_install
```

### Download and install the latest SentinelOne agent

Automatically download the most recent Generally Available SentinelOne package and install. Note, unlike the previous example, this playbook can target a mixed group containing hosts of different platforms and package managers.

```yaml
---
- name: Download and install the latest SentinelOne Agent
  hosts: all
  vars:
    s1_management_console: https://usea1-support3.sentinelone.net
    s1_agent_site_token: REDACTED
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
