# S1 Agent UUID

[![GitHub license](https://badgen.net/github/license/s1-nathangerhart/ansible_collection_s1agent)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/blob/main/LICENSE)
[![Molecule CI](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_uuid.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_uuid.yml)

The `s1_agent_uuid` role retrieves the SentinelOne agent's UUID from each host in the play and stores it the `s1_agent_uuid` fact for use by later tasks in the play.

## Requirements

An endpoint with the SentinelOne agent installed and operational.

## Role Variables

```yaml
s1_agent_uuid_report: /home/jdoe/uuid.csv
```

When defined with a valid path, a CSV file containing UUIDs for the endpoints in the play will be saved to this location on the Ansible controller.

## Dependencies

* [s1_agent_info](../s1_agent_info/) role: Gathers basic information about the SentinelOne agent.
* [ansible.windows](https://docs.ansible.com/ansible/latest/collections/ansible/windows/index.html)

## Example Playbooks

### Get each endpoints UUID

Retrieve agent UUIDs for all endpoints. The UUID will be saved to the `s1_agent_uuid` fact on each endpoint and can be used by subsequent tasks in the same play.

```yaml
---
- name: Get the SentinelOne Agent's UUID
  hosts: all

  tasks:
    - name: Include the s1_agent_uuid role
      ansible.builtin.include_role:
        name: s1_agent_uuid

    - name: Show s1_agent_uuid
      ansible.builtin.debug:
        var: s1_agent_uuid
```

### Generate a CSV report containing the UUID for all hosts in the play

Retrieve agent UUIDs for all endpoints and generate a CSV report of UUIDs. The report will be saved to ~/S1Reports/agent_uuid.csv.

```yaml
---
- name: Generate a report of SentinelOne Agent UUIDs
  hosts:
  vars:
    s1_agent_uuid_report: ~/S1Reports/agent_uuid.csv

  tasks:
    - name: Include s1_agent_uuid
      ansible.builtin.include_role:
        name: s1_agent_uuid
```

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
