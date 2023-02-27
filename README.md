# Ansible Collection - Sentinel-One.s1agents

[![s1_agent_common](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_common.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_common.yml)
[![s1_agent_info](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_info.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_info.yml)
[![s1_agent_download](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_download.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_download.yml)
[![s1_agent_install](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_install.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_install.yml)
[![s1_agent_uninstall](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_uninstall.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_uninstall.yml)
[![s1_agent_upgrade](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_upgrade.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_upgrade.yml)
[![s1_agent_uuid](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_uuid.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_agent_uuid.yml)
[![s1_import_gpg_key](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_import_gpg_key.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_import_gpg_key.yml)
[![s1_mgmt_get_passphrase](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_mgmt_get_passphrase.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible_collection_s1agent/actions/workflows/s1_mgmt_get_passphrase.yml)

The Sentinel-One.s1agents Ansible Collection is a collection of roles for managing the lifecycle of the SentinelOne Agent.

## Included Roles

* [s1_agent_common](roles/s1_agent_common/README.md) loads common variables and configs used by all other roles.
* [s1_agent_info](roles/s1_agent_info/README.md) gathers basic info about the agent and can be used to determine if the agent is installed and operational.
* [s1_agent_download](roles/s1_agent_download/README.md) assists with downloading agent installation packages from the Management Console.
* [s1_agent_install](roles/s1_agent_install/README.md) installs agent packages on endpoints.
* [s1_agent_uninstall](roles/s1_agent_uninstall/README.md) removes the agent from endpoints.
* [s1_agent_upgrade](roles/s1_agent_upgrade/README.md) upgrades an existing agent installed on an endpoint.
* [s1_agent_uuid](roles/s1_agent_uuid/README.md) is used to generate a report of agent UUIDs.
* [s1_import_gpg_key](roles/s1_import_gpg_key/README.md) ensures the SentinelOne GPG key is present on RPM based systems.
* [s1_mgmt_get_passphrase](roles/s1_mgmt_get_passphrase/README.md) is used by other roles to retrieve the unique passphrase for each agent in the play, from the management console.

## Dependencies

The Sentinel-One.s1agents collection has dependencies upon the following collections.

* [ansible.windows](https://docs.ansible.com/ansible/latest/collections/ansible/windows/index.html)
* [ansible.posix](https://docs.ansible.com/ansible/latest/collections/ansible/posix/index.html)
* [community.windows](https://docs.ansible.com/ansible/latest/collections/community/windows/index.html)

The dependencies can be installed by using the ansible-galaxy command `ansible-galaxy install -r requirements.yml` and the requirements file found at the root of the project.

## Required Permissions

### Management Console

The various roles in this collection access the SentinelOne Management Console via API and an API token[^1] is required. It should be passed to the ansible role/playbook via the `s1_api_token` variable.

Create a `Ansible Service Accounts` role in the SentinelOne Management console and grant it the permissions:[^2]

* Accounts View
* Endpoints Show Passphrase
* Endpoints Uninstall
* Endpoints Update Software
* Endpoints View
* Groups View
* Local Upgrade Authorization Edit
* Local Upgrade Authorization View
* Packages
* Roles View
* Sites View

[^1]: See the SentinelOne KnowledgeBase article [Generating API Tokens](https://support.sentinelone.com/hc/en-us/articles/360004195934).
[^2]: This is a cumulative list of permissions required by the collection as a whole. If you wish to use a separate Service Account for each Ansible Role, see that role's README for a list of required permissions.

Then add your Service Users to the `Ansible Service Accounts` role and scope it to the appropriate Site/Account/Group.

### Privileges on Endpoints

In order to successfully install and manage the agent, the Service Account used by Ansible to connect to each host must have elevated rights, sudo or su on Linux and Administrator on Windows. Ensure that your Ansible Service account is correctly configured on each endpoint.

## Known Limitations

### Using the `s1_agent_version` variable with mixed deployments

When deploying a specific version of the agent to an inventory that contains a mix of Linux and Windows endpoints, it is necessary to define the `s1_agent_version` variable so that it applies only to Linux or Windows hosts. This means the inventory must be structured so that Widows and Linux hosts are in separate groups. Alternatively, the `set_fact` module can be used to define `s1_agent_version` in the playbook with a conditional for the `ansible_system`.

### Downgrading agent versions

This collection does not directly support downgrading agent versions. However, it can be used to achieve the same end result by building a playbook that first calls the `s1_agent_uninstall` role to uninstall the agent and then calls the `s1_agent_install` role to install the lower version. The endpoint will be assigned a new UUID and will appear as a new endpoint in the management console.

### Fact Gathering

The collection uses the setup module to gather a minimum set of facts that is required for it a successful run. This behavior can be disabled by passing `--skip-tags "s1_gather_facts"` to the ansible-playbook command. If you do this, ensure that your playbook contains either `gather_facts: yes` or that the `setup` module is called prior to any Sentinel-One roles.

### Linux Operating Systems

#### Upgrading older Linux Agents beyond version 22.2.2.2 when `s1_install_gpg_signed_rpm` is `true`

When upgrading to a Linux agent version that is newer than 22.2.2.2, using the GPG Signed packages, from an agent that is older than 22.2.2.2, you must first upgrade the agent to version 22.2.2.2. Once the agent has been upgraded to 22.2.2.2, you can upgrade to the desired version.

### Windows Operating Systems

#### Idempotence on Windows

To ensure idempotence, the `s1_product_id` variable must be defined with the Product ID (GUID) for the SentinelOne agent version being deployed. If the Product ID is not set, then the task will attempt to reinstall the same version. This variable is defined in the [s1_agent_common](roles/s1_agent_common/vars/windows.yml) role and will be updated periodically, but it is not guaranteed to have mappings for all releases. Steps for configuring `s1_product_id` specific to your deployment are provided in the [s1_agent_common role](roles/s1_agent_common/README.md) role.

Additionally, this can occasionally cause testing these roles with molecule (`molecule test`) to fail on the idempotence step. If you see:

```bash
CRITICAL Idempotence test failed because of the following tasks:
*  => s1_agent_install : Install SentinelOne | Windows
*  => Flush handlers
WARNING  An error occurred during the test sequence action: 'idempotence'. Cleaning up.
```

This can indicate that the `s1_product_id` variable needs to updated with the latest agent versions.

#### Installing/Upgrading Windows Agents

If you attempt to install an agent version that is the same or lower than the currently installed Windows agent, the installer will do nothing and exit. Ansible will see this and consider the task `OK` and `Unchanged`. This is by design so that idempotence can be maintained when re-running a playbook with the same input parameters.

### MacOS Operating Systems

#### MacOS is Unsupported

Managing the agent on MacOS is currently unsupported by this collection. This is due to security designs by Apple which limit authorizing the Full Disk Access and Network Extensions to an actual person or an authorized MDM solution. As Ansible and its service account is neither, it is impossible for Ansible to deploy a fully operational SentinelOne agent.
