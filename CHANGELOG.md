# Changelog

## Version 0.3.0 - 2023-03-06

### Added

- Support for managing the agent on Windows
- s1_agent_info role
- s1_agent_common role

### Changed

- To reduce duplication most variables used by the roles are now defined in the `s1_agent_common` role
- All roles now depend on the `s1_agent_common` role to set up common variables, tasks and handlers
- The `setup` module is called by default to gather the minimum viable set of facts for the collection to run successfully
- Streamlined workflows

### Deprecated

- Using the `s1_agent_uuid` role solely for looking up the agent's UUID is now deprecated, as this functionality has been moved to the `s1_agent_info` role. Going forward, the `s1_agent_uuid` role will be maintained solely for the purpose of generating a CSV report of agent UUIDs.

## Version 0.2.0 - 2022-07-22

### Added

- GitHub Action Workflows for all roles

### Changed

- Broke existing roles out. Each role has one job to do, there are now roles for:
  - installing S1 agent
  - updating S1 agent
  - uninstalling S1 agent
  - downloading S1 agent
  - retrieving the S1 agent's UUID
  - retrieving the S1 agents passphrase from the management console

## 2022-05-10

added the s1_agent_install role to the collection
switched s1_agent_download to use dynamic includes for getting the agent URI
re-worked molecule config
