# S1 Agent UUID

[![GitHub license](https://badgen.net/github/license/s1-nathangerhart/ansible-collection-s1singularity)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/blob/main/LICENSE)
[![Molecule CI](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_uuid.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_uuid.yml)

Retrieves the SentinelOne agent's UUID from each host in the play and stores it the `s1_agent_uuid` fact for use by later tasks in the play.

## Requirements

An endpoint with the SentinelOne agent installed and operational.

## Role Variables

| Variable | Description | Required |
|----------|-------------|----------|
| s1_agent_uuid_report | If a path is provided a CSV containing UUIDs for the endpoints in the play will be saved to the path on the Ansible controller. |  |

## Dependencies

None

## Example Playbooks

### Get each endpoints UUID

Retrieve agent UUIDs for all endpoints. The UUID will be saved to the `s1_agent_uuid` fact on each endpoint and can be used by subsequent tasks in the same play.

```yaml
---
- name: Get the SentinelOne Agent's UUID
  hosts: all

  tasks:
    - name: Include the s1_agent_uuid role
      include_role:
        name: s1_agent_uuid

    - name: Show s1_agent_uuid
      debug:
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
      include_role:
        name: s1_agent_uuid
```

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
