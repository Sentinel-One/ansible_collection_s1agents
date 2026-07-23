# Unify the Linux upgrade command on the passphrase path

`s1_agent_upgrade`'s Linux path carried two forked upgrade commands — one that
supplied the console-issued passphrase via `stdin:` (ADR 0003), one that
didn't — split by which `s1_prior_version` band the endpoint fell into, with
the GPG-signed branch (`s1_install_gpg_signed_rpm: true`) excluded from the
passphrase-based task entirely and left on its own narrower path. We believed
every supported agent version actually accepts the passphrase-based command,
making the fork unnecessary complexity rather than a real behavioral
requirement.

We removed both forks and replaced them with a single upgrade task that
always supplies the passphrase, regardless of prior version or
`s1_install_gpg_signed_rpm`. The passphrase fetch (`include_role:
s1_mgmt_get_passphrase`) became unconditional too — dropping its version-range
condition and a vestigial `s1_forced_remove` check that belongs to
`s1_agent_uninstall`, not upgrade — keeping only the guard against re-fetching
a passphrase that's already defined. The existing two-step-upgrade assertion
(`s1_prior_version >= 22.2.2.2` required before jumping to `22.3` or newer)
lost its `s1_install_gpg_signed_rpm` condition and now applies to every
upgrade — it's a genuine `sentinelctl` version limitation, not something
specific to GPG-signed packages.

This closed a latent bug as a side effect: a GPG-signed upgrade with a prior
version in `[22.2.2.2, 22.3)` matched neither of the old tasks' `when`
conditions and silently did nothing. Under the unified command it correctly
triggers an upgrade.

## Cross-band validation

Because this changes behavior for the `22.3`–`25.1.3` band (which previously
upgraded _without_ a passphrase) and the existing `upgrade` molecule scenario
only exercised one hop back (`s1_release_n_minus: 1`, landing in that same
middle band), the scenario was temporarily parametrized to pin explicit
`s1_agent_version` starting points spanning all three legacy bands (`< 22.3`,
`22.3`–`25.1.3`, `>= 25.1.3`) before the old passphrase-less task was deleted:

- **`22.3`–`25.1.3`**: prior `24.3.3.6` → upgraded to `26.1.2.10`, plain RPM
  and GPG-signed. PASS (verify + idempotence green) both times.
- **`>= 25.1.3`**: prior `25.1.3.6` → upgraded to `26.1.2.10`, plain RPM and
  GPG-signed. PASS (verify + idempotence green) both times.
- **`< 22.3`**: no plain-RPM package this old remains available on the
  validating console (its retained GA catalog starts at `22.3.3.11`), and no
  GPG-signed package exists in `[22.2.2.2, 22.3)` at all — GPG signing was
  folded into the normal package from `23.3` onward, so no in-scope console
  ever carried a separate signed package that old. Live-validated instead via
  a maintainer-uploaded real `22.2.2.2` prior version on the plain-RPM path: a
  genuine fresh install of that version was confirmed to still fail rpm's
  digest check per ADR 0002 (proving that restriction is unbroken), then
  installed anyway via a test-only manual `--nodigest` rescue (not shipped),
  and the real, unmodified `s1_agent_upgrade` role upgraded it via a single
  hop to `22.4.2.4` — PASS (verify + idempotence green). The unified
  command's logic doesn't distinguish this band from the other two (the old
  fork's `< 22.3` condition was `or`'d with `>= 25.1.3` into the same
  "with-passphrase" task), so the two directly-validated bands plus this
  construction argument for the third were treated as sufficient grounds to
  proceed, per explicit maintainer decision.

## Considered options

- **Keep the version-banded fork, close only the GPG-signed gap** (add the
  missing `[22.2.2.2, 22.3)` case to the existing passphrase-based task's
  `when`). Rejected: still carries two upgrade commands and two fetch
  conditions to keep in sync going forward, for no behavioral benefit once
  every band is confirmed to accept the passphrase.
- **Gate the unification behind a new variable** (e.g.
  `s1_upgrade_use_passphrase`) so operators could opt out. Rejected: no
  evidence any supported version rejects the passphrase-based command: an
  opt-out would be speculative complexity carried indefinitely for a
  hypothetical.
- **Ship the unification on faith, skip the extended validation.** Rejected:
  the `22.3`–`25.1.3` band's behavior was changing (passphrase-less →
  passphrase-based) and the standing scenario only ever exercised that one
  band by coincidence of `s1_release_n_minus: 1` — validating all three bands
  before deleting the old path was the whole point of treating this as a
  behavior change, not a refactor.

## Consequences

- `s1_agent_upgrade`'s Linux upgrade task, the two-step-upgrade assertion, and
  the passphrase fetch are each single tasks with a single `when` (or none),
  replacing two of each split by prior-version band and
  `s1_install_gpg_signed_rpm`.
- The upgrade's success/failure debug output is a single registered result
  (`s1_upgrade_result`) instead of two differently-named results split by
  which branch ran.
- The `upgrade` molecule scenario's temporary per-band parametrization
  (`S1_UPGRADE_LEGACY_VERSION`, `S1_UPGRADE_LEGACY_NODIGEST`,
  `S1_UPGRADE_TARGET_VERSION`, `S1_UPGRADE_GPG_SIGNED`, and the `--nodigest`
  smoke-test block they gated) was removed once validation passed — it was
  scaffolding for this decision, not permanent regression coverage; a single
  unified code path doesn't need band-specific coverage going forward. The
  scenario is back to testing one `s1_release_n_minus: 1` hop.
- Every Linux upgrade now fetches a passphrase unconditionally (unless
  already supplied), including bands that previously didn't need one — this
  is the intended behavior change, not a regression.
