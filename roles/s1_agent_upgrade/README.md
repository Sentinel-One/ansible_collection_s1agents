# S1 Agent Upgrade

[![GitHub license](https://badgen.net/github/license/Sentinel-One/ansible_collection_s1agents)](https://github.com/Sentinel-One/ansible_collection_s1agents/blob/main/LICENSE)
[![Molecule CI](https://github.com/Sentinel-One/ansible_collection_s1agents/actions/workflows/s1_agent_upgrade.yml/badge.svg)](https://github.com/Sentinel-One/ansible_collection_s1agents/actions/workflows/s1_agent_upgrade.yml)

The `s1_agent_upgrade` role upgrades an existing SentinelOne Agent installed on Linux endpoints.

## Requirements

A valid SentinelOne license, access to the SentinelOne Management Console and access to the SentinelOne installation packages are required.

Inventory hosts on which the agent is being installed must be running on a supported Operating System and meet its [minimum system requirements](https://community.sentinelone.com/s/topic/0TO69000000as1iGAA/system-requirements).

### Permissions required to upgrade Windows Agents

In order to successfully set `Confirm Local Upgrade` via the API, the user account associated with the API token, `s1_api_token`, must be granted the permissions:

* Endpoints > View
* Endpoints > Update Software
* Endpoints > Uninstall
* Accounts > View
* Groups > View
* Local Upgrade Authorization > Edit
* Local Upgrade Authorization > View
* Roles > View
* Sites > View

Best practice is to create a new "Confirm Local Upgrade via API" role with these permissions. Then create a **Service User** and add them to the role.

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
s1_agent_site_token:
```

The Site or Group token for existing Windows agent, used by the SentinelOneInstaller package in cases where the installer fix a corrupted install prior to completing the upgrade.

### Configuring package variants

```yaml
s1_install_gpg_signed_rpm: false
```

When set to true download GPG signed rpm packages from the Management console, otherwise the standard RPM package will be downloaded. You may need to open a ticket with Support and request that signed Linux RPM installers be uploaded to your console.

```yaml
s1_install_msi: false
```

Download an MSI package instead of a SentinelOneInstaller package (the default).

### Windows: SentinelOneInstaller specific options

```yaml
s1_no_config_failures:
```

Set the SentinelOneInstaller package `--dont_fail_on_config_preserving_failures` flag for the upgrade.

```yaml
s1_no_preserve_uid:
```

Set the SentinelOneInstaller package `--dont_preserve_agent_uid` flag for the upgrade.

```yaml
s1_no_preserve_proxy:
```

Set the SentinelOneInstaller package `--dont_preserve_proxy` flag for the upgrade.

```yaml
s1_no_preserve_config:
```

Set the SentinelOneInstaller package `--dont_preserve_config_dir` flag for the upgrade.

### Variables from dependencies

No additional variables must be defined. However, the [s1_agent_common](../s1_agent_common/) role defines common variables including working directories and the [s1_agent_download](../s1_agent_download/) role determines which agent versions are downloaded.

#### s1_agent_common

```yaml
s1_download_path: /tmp/s1_agent_cache
s1_tmp_linux: /tmp/s1_install
s1_tmp_windows: "{{ ansible_env.TEMP}}\\s1_install"
s1_validate_certs: true
s1_product_id:
  v22_3_1_185_64_bit: '{547BC474-095C-4BFF-9D4E-7B6D2805C890}'
  v22_3_1_185_32_bit: '{5548CA13-E999-4066-8F6E-D31776C2143C}'
  v22_2_4_558_64_bit: '{5A990909-DD22-48FA-BD8B-F564AFC81C4B}'
  v22_2_4_558_32_bit: '{009923EA-54DD-4CF5-BF76-BE5C7EA048EE}'
```

#### s1_agent_download

```yaml
s1_agent_version:
s1_release_n_minus: 1
s1_package_availability:
    - Ga
```

## Dependencies

* [s1_agent_info](../s1_agent_info/) role: Gathers basic information about the SentinelOne agent.
* [s1_agent_download](../s1_agent_download/) role: automatically downloads the SentinelOne agent if `s1_agent_src` variable is undefined. Requires that the `s1_management_console` and `s1_api_token` variables are defined.
* [s1_mgmt_get_passphrase](../s1_mgmt_get_passphrase/) role: retrieves the agent's unique passphrase from the management console. Requires that `s1_management_console` and `s1_api_token` are defined.
* [s1_import_gpg_key](../s1_import_gpg_key/) role: only executed on the Red Hat family of operating systems.
* [s1_agent_common](../s1_agent_common/) role: configures common variables for all roles in the collection
* [ansible.windows](https://docs.ansible.com/ansible/latest/collections/ansible/windows/index.html)

## Example Playbooks

### Upgrade SentinelOne from a package that was previously downloaded

Upgrade the SentinelOne Agent from a package that has already been downloaded and staged on the Ansible Controller host. Note when the `s1_agent_src` var is set at the play level the play can only run against inventory hosts that support that package. For example a .deb package can not be installed on Red Hat endpoints. To target a mixed group of endpoints assign the `s1_agent_src` variable at the group_vars or host_vars.

```yaml
---
- name: Upgrade the SentinelOne Agent
  hosts: RedHat_Servers
  vars:
    s1_management_console: https://<management fqdn>
    s1_agent_src: /software/sentinelone/SentinelAgent_linux_v22_1_2_7.rpm
    s1_agent_version: 22.1.2.7
  tasks:
    - name: Include s1_agent_upgrade
      ansible.builtin.include_role:
        name: s1_agent_upgrade
```

### Download and upgrade to the latest SentinelOne agent

Automatically download the most recent Generally Available SentinelOne package and upgrade to it. Note, unlike the previous example, this playbook can target a mixed group containing hosts of different platforms and package managers.

```yaml
---
- name: Download and upgrade to the latest SentinelOne Agent
  hosts: all
  vars:
    s1_management_console: https://<management fqdn>
    s1_api_token: REDACTED
  tasks:
    - name: Include s1_agent_install
      ansible.builtin.include_role:
        name: s1_agent_install
```

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
