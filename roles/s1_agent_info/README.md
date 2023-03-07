# S1 Agent Info

[![GitHub license](https://badgen.net/github/license/Sentinel-One/ansible_collection_s1agents)](https://github.com/Sentinel-One/ansible_collection_s1agents/blob/main/LICENSE)
[![Molecule CI](https://github.com/Sentinel-One/ansible_collection_s1agents/actions/workflows/s1_agent_info.yml/badge.svg)](https://github.com/Sentinel-One/ansible_collection_s1agents/actions/workflows/s1_agent_info.yml)

Retrieves the SentinelOne agent's status from each host in the play and stores it the `s1_agent_info` fact for use by later tasks in the play. Information collected includes if the agent is installed, state of the service, uuid and if a reboot is required.

## Requirements

An endpoint with the SentinelOne agent installed and operational.

## Role Variables

None

## Dependencies

* [s1_agent_common](../s1_agent_common/) role: configures common variables for all roles in the collection
* [ansible.windows](https://docs.ansible.com/ansible/latest/collections/ansible/windows/index.html)

## Example Playbooks

### Get agent info for each endpoint

Retrieve information about the agent for all endpoints. The agent's state will be saved to the `s1_agent_info` fact on each endpoint and can be used by subsequent tasks in the same play.

```yaml
---
- name: Get the SentinelOne Agent's Status
  hosts: all

  tasks:
    - name: Include the s1_agent_info role
      ansible.builtin.include_role:
        name: s1_agent_info

    - name: Show SentinelOne Agent status
      ansible.builtin.debug:
        var: s1_agent_info
```

#### Sample output for a Linux endpoint with the agent installed

```bash
[Linux] => {
    "s1_agent_info": {
        "agent_enabled": true,
        "anti_tamper_enabled": true,
        "installed": true,
        "mgmt_url": "https://<management fqdn>",
        "product_id": "",
        "reboot_required": false,
        "service_status": "running",
        "uuid": "23a908c8-f348-526b-ab16-1a4f5de40d82",
        "version": "22.1.2.7"
    }
}
```

#### Sample output for a Windows endpoint with the agent installed

```bash
[Windows] => {
    "s1_agent_info": {
        "agent_enabled": true,
        "anti_tamper_enabled": true,
        "installed": true,
        "mgmt_url": "https://<management fqdn>",
        "product_id": "{5A990909-DD22-48FA-BD8B-F564AFC81C4B}",
        "reboot_required": false,
        "service_status": "started",
        "uuid": "f68fa59f4194463dbf6d2b9de3b6830b",
        "version": "22.2.558"
    }
}
```

#### Sample output for a Linux endpoint without the agent installed

```bash
[Linux] => {
    "s1_agent_info": {
        "agent_enabled": "",
        "anti_tamper_enabled": "",
        "installed": false,
        "mgmt_url": "",
        "product_id": "",
        "reboot_required": "",
        "service_status": "",
        "uuid": "",
        "version": ""
    }
}
```

#### Sample output for a Windows endpoint without the agent installed

```bash
[Windows] => {
    "s1_agent_info": {
        "agent_enabled": "",
        "anti_tamper_enabled": "",
        "installed": false,
        "mgmt_url": "",
        "product_id": "",
        "reboot_required": "",
        "service_status": "",
        "uuid": "",
        "version": ""
    }
}
```

## License

GPL-3.0-or-later

## Author Information

Nathan Gerhart / SentinelOne
