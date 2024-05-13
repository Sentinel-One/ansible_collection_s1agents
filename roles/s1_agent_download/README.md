# S1 Agent Download

[![GitHub license](https://badgen.net/github/license/Sentinel-One/ansible_collection_s1agents)](https://github.com/Sentinel-One/ansible_collection_s1agents/blob/main/LICENSE)
[![Molecule CI](https://github.com/Sentinel-One/ansible_collection_s1agents/actions/workflows/s1_agent_download.yml/badge.svg)](https://github.com/Sentinel-One/ansible_collection_s1agents/actions/workflows/s1_agent_download.yml)

The `s1_agent_download` role downloads the SentinelOne Agents from the management console.
This role is called automatically by the [s1_agent_install](../s1_agent_install/) and [s1_agent_upgrade](../s1_agent_upgrade/) roles if the `s1_agent_src` variable is unset.

## Requirements


A valid SentinelOne license, access to the SentinelOne Management Console and an account with permission to download packages and an API Token are required to use this role.

### Permissions required to download packages via the API

In order to successfully query and download packages via the API, the account associated with the API token, `s1_api_token`, must be granted the permissions:

* Accounts View
* Groups View
* Packages
* Roles View
* Sites View

Best practice is to create a new "Download packages via API" role with these permissions. Then create a **Service User** and add them to the role.

## Role Variables

```yaml
s1_management_console: https://<management fqdn>
```

This is mandatory and is the URL to your SentinelOne management console.

```yaml
s1_api_token:
```

This is mandatory and is the API token[^1] associated with the user which will running the role.

[^1]: See the SentinelOne KnowledgeBase article [Generating API Tokens](https://support.sentinelone.com/hc/en-us/articles/360004195934).

### Configuring the version of the agent

```yaml
s1_agent_version:
```

The version of the agent package to be downloaded. This can be found by referencing the `Build Number` on Sentinels > Packages page for the Package you want to download.
As agent versions vary by platform it should be set at the host or group level. When both `s1_agent_version` and `s1_release_n_minus` are unset, the latest release will be downloaded.

```yaml
s1_release_n_minus: 0
```

Download an agent package this many releases behind the latest release. A value of `0` indicates that the latest package should be downloaded.
If `s1_package_availability` includes Beta or Ea packages, then these versions will be included when counting backwards and may be deployed to the endpoint.
When both `s1_agent_version` and `s1_release_n_minus` are unset, the latest release will be downloaded.

### Configuring package variants

```yaml
s1_install_gpg_signed_rpm: false
```

When set to true download GPG signed rpm packages from the Management console, otherwise the standard RPM package will be downloaded. You may need to open a ticket with Support and request that signed Linux RPM installers be uploaded to your console.

```yaml
s1_install_msi: false
```

Download an MSI package instead of a SentinelOneInstaller package (the default).

### API parameters

```yaml
s1_api_limit: 100
```

The number of results to return with each call to the packages API endpoint.

```yaml
s1_platform_type:
  - Linux
  - Windows
```

Limits the results returned by the packages API to only packages applicable to Windows and Linux.

```yaml
s1_package_availability:
    - Beta
    - Ea
    - Ga
    - other
```

Determines the availability of the package to download. This further limits `s1_agent_version` and `s1_release_n_minus`. Acceptable values are `Beta`, `Ea`, `Ga` and `other`. All available options are shown here, but by default, only `Ga` releases are downloaded.

### Variables from dependencies

#### s1_agent_common

```yaml
s1_download_path: /tmp/s1_agent_cache
s1_validate_certs: true
```

## Dependencies

* [s1_agent_common](../s1_agent_common/) role: configures common variables for all roles in the collection
* [ansible.windows](https://docs.ansible.com/ansible/latest/collections/ansible/windows/index.html)

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
      ansible.builtin.include_role:
        name: s1_agent_download

    - name: Show path to downloaded agent
      ansible.builtin.debug:
        var: s1_agent_src
```

### Download a prior release

Instead of downloading the latest release, this will download the release immediately prior to it. By default only releases that meet Ga status will be considered. This

```yaml
---
- name: Download SentinelOne Agent from the Management Console
  hosts: all
  vars:
    s1_management_console: <Management Console URL>
    s1_api_token: <API Token>
    s1_release_n_minus: 1
  tasks:
    - name: Include s1_agent_download
      ansible.builtin.include_role:
        name: s1_agent_download

    - name: Show path to downloaded agent
      ansible.builtin.debug:
        var: s1_agent_src
```

### Download an agent by version number

Because package version numbers are platform specific, when downloading a named release it must be scoped to that platform (Windows or Linux) or group of like machines.

#### Linux

Download version 21.7.3.6 SentinelOne Linux Agent. Agent versions are platform specific. To avoid failed hosts on playbook run, the playbook's `hosts` parameter must be scoped to only include Linux endpoints.

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
      ansible.builtin.include_role:
        name: s1_agent_download

    - name: Show path to downloaded agent
      ansible.builtin.debug:
        var: s1_agent_src
```

#### Windows

Download version 22.1.4.10010 SentinelOneInstaller Agent for Windows. Agent versions are platform specific. To avoid failed hosts on playbook run, the playbook's `hosts` parameter must be scoped to only include Windows endpoints.

```yaml
---
- name: Download a Specific SentinelOne Agent from the Management Console
  hosts: Windows_Endpoints
  vars:
    s1_management_console: <Management Console URL>
    s1_api_token: <API Token>
    s1_agent_version: 22.1.4.10010
  tasks:
    - name: Include s1_agent_download
      ansible.builtin.include_role:
        name: s1_agent_download

    - name: Show path to downloaded agent
      ansible.builtin.debug:
        var: s1_agent_src
```

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
