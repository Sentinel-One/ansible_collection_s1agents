# S1 MGMT Get Passphrase

[![GitHub license](https://badgen.net/github/license/s1-nathangerhart/ansible_collection_s1agent)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/blob/main/LICENSE)
[![Molecule CI](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_mgmt_get_passphrase.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_mgmt_get_passphrase.yml)

Retrieves the passphrase for an endpoint from the SentinelOne management console, using the agents UUID, and saves it to the `s1_agent_passphrase` fact.

## Requirements

An endpoint with the SentinelOne agent installed and operational. A valid SentinelOne license, access to the SentinelOne Management Console and an API key are required.

### Permissions required to get agent passphrases via the API

In order to successfully query agent passphrases via the API, the user account associated with the API token, `s1_api_token`, must be granted permissions:

* Accounts View
* Endpoints View
* Endpoints Show Passphrase
* Groups View
* Roles View
* Sites View

## Role Variables

| Variable | Description | Required |
|----------|-------------|----------|
| s1_management_console | URL to the SentinelOne management console. | &check; |
| s1_api_token | API token[^1] with permissions download agent packages and lookup up agent passphrases. | &check; |
| s1_agent_passphrase_report | If provided a CSV containing passphrases for endpoints in the play will be saved to the path specified on the Ansible controller. This report contains sensitive information. |  |

[^1]: See the SentinelOne KnowledgeBase article [Generating API Tokens](https://support.sentinelone.com/hc/en-us/articles/360004195934).

## Dependencies

* [s1_agent_uuid](../s1_agent_uuid/README.md): The s1_mgmt_get_passphrase role will automatically call the s1_agent_uuid role to retrieve UUIDs from each host in the Ansible inventory.

## Example Playbook

### Retrieve agent passphrases for use by other tasks in the play

Retrieve agent passphrases for all endpoints. The passphrase will be saved to the `s1_agent_passphrase` fact on each endpoint and can be used by subsequent tasks in the same play.

*Warning: this sample play is very insecure - it prints the agent's passphrase to stdout. It is provided as an example to show that the `s1_agent_passphrase` fact can be used by later tasks in the play.*

```yaml
---
- name: Get the endpoint's passphrase
  hosts: all

  tasks:
    - name: Include the s1_mgmt_get_passphrase role
      include_role:
        name: s1_mgmt_get_passphrase

    - name: Show s1_agent_passphrase
      debug:
        var: s1_agent_passphrase
```

### Generate a report of agent passphrases

Retrieve agent passphrases for all endpoints and generate a CSV report of passphrases. The report will be saved to /tmp/s1_workdir/agent_passphrase.csv.

```yaml
---
- name: Generate a report of endpoint passphrases
  hosts:
  vars:
    s1_agent_uuid_report: /tmp/s1_workdir/agent_passphrase.csv

  tasks:
    - name: Include the s1_mgmt_get_passphrase role
      include_role:
        name: s1_mgmt_get_passphrase
```

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
