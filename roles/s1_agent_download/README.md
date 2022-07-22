# S1 Agent Download

[![GitHub license](https://badgen.net/github/license/s1-nathangerhart/ansible-collection-s1singularity)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/blob/main/LICENSE)
[![Molecule CI](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_download.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_download.yml)

Downloads SentinelOne Agents from the management console.
This role is called automatically by the [s1_agent_install](../s1_agent_install/) and [s1_agent_upgrade](../s1_agent_upgrade/) roles if the `s1_agent_src` fact is unset.

## Requirements

A valid SentinelOne license, access to the SentinelOne Management Console and an account with permission to download packages and an API Token are required to use this role.

### Permissions required to download packages via the API

In order to successfully query and download packages via the API, the user account associated with the API token, `s1_api_token`, must be granted permissions:

* Accounts View
* Groups View
* Packages
* Roles View
* Sites View

Best practice is to create a new "Download packages via API" role with these permissions.

## Role Variables

| Variable | Description | Required |
|----------|-------------|----------|
| s1_management_console | URL to the SentinelOne management console. | &check; |
| s1_api_token | API token[^1] with permissions download agent packages. | &check; |
| s1_agent_version | Version of the agent package to download. As agent versions very by platform it should be set at the host or group level. This is the `Build Number` on Sentinels > Packages pages. If omitted the latest agent version will be downloaded. |  |
| s1_release_n_minus | Download an agent package this many releases behind the latest release. When both s1_agent_version and s1_release_n_minus are unset, the latest release will be downloaded. |  |
| s1_package_availability | Package availability to download. This further limits `s1_agent_version` and `s1_release_n_minus`. Acceptable values are `Beta`, `Ea`, `Ga` and `other`. Only `Ga` releases are downloaded by default. |  |
| s1_platform_type | Provide a list of platforms to download the agent packages for. Acceptable values are `Linux`, `Linux_k8s`, `Macos`, `Sdk`, `Windows` and `Windows_legacy`, but only `Linux` and `Windows` have been implemented. |  |

[^1]: See the SentinelOne KnowledgeBase article [Generating API Tokens](https://support.sentinelone.com/hc/en-us/articles/360004195934).

## Dependencies

None

## Example Playbooks

### Download the latest release

Download the latest SentinelOne Agent. Only the `s1_management_console` and `s1_api_token` variables are required.

```yaml
---
- name: Download the Latest SentinelOne Agent from the Management Console
  hosts: all
  vars:
    s1_management_console: <Management Console URL>
    s1_api_token: <API Token>
  tasks:
    - name: Include s1_agent_download
      include_role:
        name: s1_agent_download

    - name: Show path to downloaded agent
      ansible.builtin.debug:
        var: s1_agent_src
```

### Download a specific release

Download version 21.7.3.6 SentinelOne Linux Agent. Agent versions are platform specific so the playbook's `hosts` parameter must be scoped to a specific platform or group of machines.

```yaml
---
- name: Download a Specific SentinelOne Agent from the Management Console
  hosts: Linux_Endpoints
  vars:
    s1_management_console: <Management Console URL>
    s1_api_token: <API Token>
    s1_agent_version: 21.7.3.6
  tasks:
    - name: Include s1_agent_download
      include_role:
        name: s1_agent_download

    - name: Show path to downloaded agent
      ansible.builtin.debug:
        var: s1_agent_src
```

### Download a prior release

Instead of downloading the latest release, this will download the release immediately prior to it. By default only releases that meet Ga status will be considered.

```yaml
---
- name: Download SentinelOne Agent from the Management Console
  hosts: Linux_Endpoints
  vars:
    s1_management_console: <Management Console URL>
    s1_api_token: <API Token>
    s1_release_n_minus: 1
  tasks:
    - name: Include s1_agent_download
      include_role:
        name: s1_agent_download

    - name: Show path to downloaded agent
      ansible.builtin.debug:
        var: s1_agent_src
```

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
