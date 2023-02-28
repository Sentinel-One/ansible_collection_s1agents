# S1 Agent Install

[![GitHub license](https://badgen.net/github/license/s1-nathangerhart/ansible_collection_s1agent)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/blob/main/LICENSE)
[![Molecule CI](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_install.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_install.yml)

The `s1_agent_install` role installs the SentinelOne Agent on endpoints.

## Requirements

A valid SentinelOne license, access to the SentinelOne Management Console and access to the SentinelOne installation packages are required.

Inventory hosts on which the agent is being installed must be running on a supported Operating System and meet its [minimum system requirements](https://support.sentinelone.com/hc/en-us/articles/360004196614-System-Requirements).

## Role Variables

```yaml
s1_management_console: https://usea1-support3.sentinelone.net
```

This is mandatory and is the URL to your SentinelOne management console.

```yaml
s1_api_token:
```

This is mandatory and is the API token[^1] associated with the user which will running the role.

[^1]: See the SentinelOne KnowledgeBase article [Generating API Tokens](https://support.sentinelone.com/hc/en-us/articles/360004195934).

```yaml
s1_agent_site_token:
```

This is mandatory and is the Site or Group token for binding the agent to the management console.

```yaml
s1_agent_src:
```

The path to a previously downloaded SentinelOne package to be used for the upgrade. As agent packages vary by platform it should be set at the host or group level. The path should be relative to and accessible from the Ansible Controller. The Ansible Controller will transfer it to each endpoint. If `s1_agent_src` is undefined then the s1_agent_download role will be called.

### Configuring package variants

```yaml
s1_install_gpg_signed_rpm: false
```

When set to true download GPG signed rpm packages from the Management console, otherwise the standard RPM package will be downloaded. You may need to open a ticket with Support and request that signed Linux RPM installers be uploaded to your console.

```yaml
s1_install_msi: false
```

Download an MSI package instead of a SentinelOneInstaller package (the default).

### Advanced options

```yaml
s1_agent_customer_id: My Custom Sting
```

Set a customer specific identifier for the host, depending on the platform this is either a Customer ID or an External ID in the documentation.

```yaml
s1_agent_custom_install_path: /some/alternate/install/location
```

Install the SentinelOne Agent to a custom location. Review the Knowledge Base for known limitations before setting this variable.

```yaml
s1_agent_management_proxy: http://proxy.local:8080
```

If a proxy is required for agent egress traffic to reach the management console, set it here, otherwise leave it undefined.

```yaml
s1_agent_dv_proxy: http://proxy.local:8080
```

If a proxy is required for agent deep visibility egrees traffic to reach the management console, set it here, otherwise leave it undefined.

### Linux only options

```yaml
s1_agent_device_type: server
```

Set the device type to `server` or `desktop`

```yaml
s1_agent_auto_start: true
```

Determines if the agent will be auto-started during deployment. The default is true

```yaml
s1_agent_create_user: true
```

Controls if the sentinelone user is created during instal. If true (default), the agent creates the sentinelone user and group when it is installed. If false, the sentinelone user and group must be created manually, see the Knowledge Base for specifics.

### Windows only options

```yaml
s1_enable_vdi: false
```

```yaml
s1_no_config_failures: false
```

Set the SentinelOneInstaller package `--dont_fail_on_config_preserving_failures` flag for the upgrade.

When set to true set the installer packages VDI flag to true and install the SentinelOne agent for a "cold clone".
Note: See [https://support.sentinelone.com/hc/en-us/articles/360035087333](https://support.sentinelone.com/hc/en-us/articles/360035087333.).

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

* [s1_agent_download](../s1_agent_download/) role: automatically downloads the SentinelOne agent if `s1_agent_src` is unset. Requires that the `s1_management_console` and `s1_api_token` variables are defined.
* [s1_import_gpg_key](../s1_import_gpg_key/) role: only executed on the Red Hat family of operating systems.
* [s1_agent_common](../s1_agent_common/) role: configures common variables for all roles in the collection
* [ansible.windows](https://docs.ansible.com/ansible/latest/collections/ansible/windows/index.html)
* [community.windows](https://docs.ansible.com/ansible/latest/collections/community/windows/index.html)

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
      ansible.builtin.include_role:
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
      ansible.builtin.include_role:
        name: s1_agent_install
```

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
