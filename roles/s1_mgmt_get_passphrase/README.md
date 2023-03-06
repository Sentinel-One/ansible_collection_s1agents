# S1 MGMT Get Passphrase

[![GitHub license](https://badgen.net/github/license/Sentinel-One/ansible_collection_s1agents)](https://github.com/Sentinel-One/ansible_collection_s1agents/blob/main/LICENSE)
[![Molecule CI](https://github.com/Sentinel-One/ansible_collection_s1agents/actions/workflows/s1_mgmt_get_passphrase.yml/badge.svg)](https://github.com/Sentinel-One/ansible_collection_s1agents/actions/workflows/s1_mgmt_get_passphrase.yml)

The `s1_mgmt_get_passphrase` role retrieves the passphrase for an endpoint from the SentinelOne management console, using the agents UUID, and saves it to the `s1_agent_passphrase` fact.

## Requirements

An endpoint with the SentinelOne agent installed and operational. A valid SentinelOne license, access to the SentinelOne Management Console and an API key are required.

### Permissions required to get agent passphrases via the API

In order to successfully query agent passphrases via the API, the user account associated with the API token, `s1_api_token`, must be granted the permissions:

* Accounts View
* Endpoints View
* Endpoints Show Passphrase
* Groups View
* Roles View
* Sites View

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

```yaml
s1_api_limit: 100
```

The number of results to return with each call to the packages API endpoint.

```yaml
s1_agent_passphrase_report: /home/jdoe/passphrase.csv
```

When defined with a valid path, a CSV file containing passphrases  for the endpoints in the play will be saved to this location on the Ansible controller. **This report contains sensitive information.**

## Dependencies

* [s1_agent_info](../s1_agent_info/) role: Gathers basic information about the SentinelOne agent.
* [s1_agent_common](../s1_agent_common/) role: configures common variables for all roles in the collection
* [ansible.windows](https://docs.ansible.com/ansible/latest/collections/ansible/windows/index.html)

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
      ansible.builtin.include_role:
        name: s1_mgmt_get_passphrase

    - name: Show s1_agent_passphrase
      ansible.builtin.debug:
        var: s1_agent_passphrase
```

### Generate a report of agent passphrases

Retrieve agent passphrases for all endpoints and generate a CSV report of passphrases. The report will be saved to /tmp/s1_agent_cache/agent_passphrase.csv.

```yaml
---
- name: Generate a report of endpoint passphrases
  hosts:
  vars:
    s1_agent_uuid_report: /tmp/s1_agent_cache/agent_passphrase.csv

  tasks:
    - name: Include the s1_mgmt_get_passphrase role
      ansible.builtin.include_role:
        name: s1_mgmt_get_passphrase
```

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
