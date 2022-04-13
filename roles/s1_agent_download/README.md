# S1 Agent Download

Downloads SentinelOne Agents from the management console.

## Requirements

A valid SentinelOne license, access to the SentinelOne Management Console and an account with permission to download packages and an API Token are required to use this role.

### Permissions required to download packages via the API

* Accounts View
* Groups View
* Packages
* Roles View
* Sites View

## Role Variables

* **s1_management_console**: URL for the Management Console.
* **s1_api_token**: Token used to access the API.
* **s1_agent_management_proxy**: Set if the endpoint needs a proxy to access the management console.
* **s1_agent_version**: Version of the agent to download. As agent versions very by platform it should be set at the host or group level. This can be found in the `Build Number` column on Sentinels > Packages pages. If omitted the latest agent version will be downloaded.
* **s1_package_status**: Package release status to download. Acceptable values are `Beta`, `Ea`, `Ga` and `other`.
* **s1_platform_type**: Provide a list of platforms to download the agent packages for. Acceptable values are `Linux`, `Linux_k8s`, `Macos`, `Sdk`, `Windows` and `Windows_legacy`, but only `Linux` and `Windows` are implemented.

## Dependencies

None

## Example Playbook

Download the SentinelOne Agent. Only the `s1_management_console` and `s1_api_token` variables are required.

```yaml
---
- name: Download SentinelOne Agent from the Management Console
  hosts: all
  vars:
    s1_management_console: https://usea1-support3.sentinelone.net
    s1_api_token:
    s1_platform_type: Linux
    s1_agent_version: 21.7.3.6
  tasks:
    - name: Include s1_agent_download
      include_role:
        name: s1_agent_download

    - name: Show path to downloaded agent
      debug:
        var: s1_agent_src
```

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
