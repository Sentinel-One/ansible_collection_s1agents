# The upgrade role takes no site token

The Windows upgrade argument templates (MSI and new-EXE) used to pass `s1_agent_site_token` to the installer (`SITE_TOKEN=` / `-t`), inserted raw with none of the structural checking the install role applies. That made it an unvalidated operator value on a `SYSTEM` command line — the MSI property-injection shape [ADR 0001](./0001-trust-model.md) treats as a hardening obligation for AWX/AAP consumers. We **remove the token from the upgrade role** instead of validating it: an upgrade targets an agent that is already registered to a site, so the installer does not need a registration token to upgrade it.

## Considered options

- **Validate the token in the upgrade role** (reuse the install role's `b64decode | from_json` check). Rejected: it keeps a secret the upgrade does not need on the upgrade command line, and keeps operators distributing a registration secret to jobs that only upgrade.

## Consequences

- The upgrade role ignores `s1_agent_site_token`; inventories that still set it globally keep working unchanged.
- The role README had said the token let the installer repair a corrupted install before upgrading. That repair-on-upgrade path is gone: a corrupted install is recovered by re-installing with the install role, which still requires and validates the token. Do not re-add the token to the upgrade role for this.
- Linux upgrades are unaffected; they run through `sentinelctl control upgrade` and never used the token.
