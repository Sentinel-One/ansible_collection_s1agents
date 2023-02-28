# S1 Agent Common

[![GitHub license](https://badgen.net/github/license/s1-nathangerhart/ansible_collection_s1agent)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/blob/main/LICENSE)
[![Molecule CI](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_common.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_common.yml)

The `s1_agent_common` role is a dependency of all other roles in the `s1agent` Ansible Collection and is responsible for loading common variables, handlers and other configuration used by the other roles in the collection.

## Requirements

Access to the SentinelOne Management console.
A valid SentinelOne license and access to the SentinelOne Management Console are required to use this roles in this collection.

## Role Variables

### Defaults

Defaults (`defaults/main.yml`) are listed below. These can safely be customized to fit your deployment scenario.

```yaml
s1_download_path: /tmp/s1_agent_cache
s1_tmp_linux: /tmp/s1_install
s1_tmp_windows: "{{ ansible_env.TEMP}}\\s1_install"
s1_validate_certs: true
```

The Ansible controller will download and cache agent packages to the `s1_download_path` directory. To prevent unnecessary load on the management console, this directory is not removed at the end of the play.

Linux and Windows hosts targeted by the play wil use `s1_tmp_linux` and `s1_tmp_windows` as their local working directory for the duration of the play. This directory is removed at the end of a successful play.

When working with an on-premisses management console using self-signed certificates, it may be necessary to disable SSL Certificate Verification `s1_validate_certs: false`.

### Vars

Vars (`vars/*.yml`) are listed below. Their values depend on a combination of the System, Platform, Distribution and Version. See the corresponding file in vars for the default value. These values typically only need to be altered when adding support for an operating system and care should be taken before overriding them.

```yaml
s1_package_name
s1_service_name
s1_service_handler_name
s1_reboot_handler_name
s1_product_id:
  v22_3_1_185_64_bit: '{547BC474-095C-4BFF-9D4E-7B6D2805C890}'
  v22_3_1_185_32_bit: '{5548CA13-E999-4066-8F6E-D31776C2143C}'
  v22_2_4_558_64_bit: '{5A990909-DD22-48FA-BD8B-F564AFC81C4B}'
  v22_2_4_558_32_bit: '{009923EA-54DD-4CF5-BF76-BE5C7EA048EE}'
```

`s1_package_name` defines the distribution specific name of the SentinelOne software in the local package manager, while `s1_service_name` defines the name of the distribution specific SentinelOne service.

`s1_service_handler_name` is the name of the Ansible Handler used to start the SentinelOne service on Linux.

`s1_reboot_handler_name` is the name of the Ansible Handler used to reboot Windows Hosts.

`s1_product_id` is specific to Windows and is the Product ID or GUID of the installed SentinelOne agent. When defined, this can speed up Ansible's ability to determine if the correct version of the agent is installed. It is recommended to include this variable in the group_vars for your environment and to update it with the versions of the agent being deployed locally. This variable will be updated periodically, but it is not guaranteed to have mappings for all releases.

Note: after an agent has been installed on one endpoint, the [s1_agent_info](../s1_agent_info/) role can be used to retrieve the Product ID for that particular package. The Product ID will be identical for both the SentinelOneInstaller package and the MSI of any given version.

## Dependencies

* [ansible.windows](https://docs.ansible.com/ansible/latest/collections/ansible/windows/index.html)

## Example Playbook

None. This role is called by other roles as needed. It does not make any changes to the host. There is no reason to run it manually.

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
