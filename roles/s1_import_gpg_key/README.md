# S1 Import GPG Key

[![GitHub license](https://badgen.net/github/license/Sentinel-One/ansible_collection_s1agents)](https://github.com/Sentinel-One/ansible_collection_s1agents/blob/main/LICENSE)
[![Molecule CI](https://github.com/Sentinel-One/ansible_collection_s1agents/actions/workflows/s1_import_gpg_key.yml/badge.svg)](https://github.com/Sentinel-One/ansible_collection_s1agents/actions/workflows/s1_import_gpg_key.yml)

The `s1_import_gpg_key` role imports the SentinelOne GPG Key into the host keyring, allowing packages signed by SentinelOne's GPG key to be installed.
This role is called, as needed, by the [s1_agent_install](../s1_agent_install/) and [s1_agent_upgrade](../s1_agent_upgrade/) roles to ensure the S1 GPG Key is available on each host in the play.

## Requirements

None

## Role Variables

```yaml
s1_import_gpg_key_state: present
```

Determines if the SentinelOne GPG key is added or removed from the host system. By default it is added.

### Variables from dependencies

No additional variables must be defined. However, the [s1_agent_common](../s1_agent_common/) role defines common variables including working directories

#### s1_agent_common

```yaml
s1_tmp_linux: /tmp/s1_install
```

## Dependencies

* [s1_agent_common](../s1_agent_common/) role: configures common variables for all roles in the collection

## Example Playbooks

### Install SentinelOne's GPG Key

```yaml
---
- name: Import the S1 GPG Key
  hosts: all
  tasks:
    - name: Include s1_import_gpg_key
      ansible.builtin.include_role:
        name: s1_import_gpg_key
```

### Remove SentinelOne's GPG Key

```yaml
---
- name: Import the S1 GPG Key
  hosts: all
  vars:
    s1_import_gpg_key_state: absent
  tasks:
    - name: Include s1_import_gpg_key
      ansible.builtin.include_role:
        name: s1_import_gpg_key
```

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
