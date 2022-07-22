# S1 Import RPM Key

[![GitHub license](https://badgen.net/github/license/s1-nathangerhart/ansible-collection-s1singularity)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/blob/main/LICENSE)
[![Molecule CI](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_import_rpm_key.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_import_rpm_key.yml)

Imports the SentinelOne GPG Key in the RPM database, allowing packages signed by SentinelOne to be installed.
This role is called automatically by the [s1_agent_install](../s1_agent_install/) and [s1_agent_upgrade](../s1_agent_upgrade/) roles to ensure the S1 RPM Key is available on each host in the play.

## Requirements

None

## Role Variables

| Variable | Description | Required |
|----------|-------------|----------|
| s1_import_rpm_key_state | Choose `present` to import the RPM key or `absent` to remove it. Default is `present`. |  |

## Dependencies

None

## Example Playbooks

### Install SentinelOne's RPM Key

```yaml
---
- name: Import the S1 RPM Key
  hosts: all
  vars:
    s1_import_rpm_key_state: present
  tasks:
    - name: Include s1_import_rpm_key
      include_role:
        name: s1_import_rpm_key
```

### Remove SentinelOne's RPM Key

```yaml
---
- name: Import the S1 RPM Key
  hosts: all
  vars:
    s1_import_rpm_key_state: absent
  tasks:
    - name: Include s1_import_rpm_key
      include_role:
        name: s1_import_rpm_key
```

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
