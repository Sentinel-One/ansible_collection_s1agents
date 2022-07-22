# Ansible Collection - s1community.singularity

[![s1_agent_download](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_download.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_download.yml)
[![s1_agent_install](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_install.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_install.yml)
[![s1_agent_uninstall](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_uninstall.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_uninstall.yml)
[![s1_agent_upgrade](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_upgrade.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_upgrade.yml)
[![s1_agent_uuid](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_uuid.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_agent_uuid.yml)
[![s1_import_rpm_key](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_import_rpm_key.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_import_rpm_key.yml)
[![s1_mgmt_get_passphrase](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_mgmt_get_passphrase.yml/badge.svg)](https://github.com/s1-nathangerhart/ansible-collection-s1singularity/actions/workflows/s1_mgmt_get_passphrase.yml)

The s1community.singularity Ansible Collection is a collection of roles for working with the SentinelOne Singularity platform.

## Included Roles

* [s1_agent_download](roles/s1_agent_download/README.md) assists with downloading agent installation packages from the Management Console.
* [s1_agent_install](roles/s1_agent_install/README.md) installs agent packages on endpoints.
* [s1_agent_uninstall](roles/s1_agent_uninstall/README.md) removes the agent from endpoints.
* [s1_agent_upgrade](roles/s1_agent_upgrade/README.md) upgrades an existing agent installed on an endpoint.
* [s1_agent_uuid](roles/s1_agent_uuid/README.md) is used by the other roles to get an agents UUID, but it can also be used independently to generate a report of agent UUIDs.
* [s1_import_rpm_key](roles/s1_import_rpm_key/README.md) is used by the install and upgrade roles to ensure that the SentinelOne PRM key is present on Red Hat systems.
* [s1_mgmt_get_passphrase](roles/s1_mgmt_get_passphrase/README.md) is used by other roles to query the management console and return the unique passphrase for each agent in the play. It can anslo be used independent of other roles to return the passphrase for use by tasks that call `sentinelctl` or generate a report of passphrases.

## Required Permissions

### Management Console

The various roles in this collection access the SentinelOne Management Console via API and an API token[^1] is needed. It should be passed to the ansible role/playbook via the `s1_api_token` variable.

Create a `Ansible Service Accounts` role in the SentinelOne Management console and grant it the permissions:[^2]

* Accounts View
* Endpoints Show Passphrase
* Endpoints View
* Groups View
* Packages
* Roles View
* Sites View

[^1]: See the SentinelOne KnowledgeBase article [Generating API Tokens](https://support.sentinelone.com/hc/en-us/articles/360004195934).
[^2]: This is a cumulative list of permissions required by the collection as a whole. If you wish to use a separate Service Account for each Ansible Role, see that roles README for a list of its required permissions.

Then add your service account(s) to the `Ansible Service Accounts` role and scope it to the appropriate Site/Account/Group.

### Privileges on Endpoints

The Service Account used by Ansible to connect to each host in the inventory must have elevated rights, sudo or su on Linux and Administrator on Windows, in order to successfully install and manage the agent. Ensure that your Ansible Service account is correctly configured.
