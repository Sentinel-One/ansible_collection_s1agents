# Drop EOL support by removing accommodations, not by gating versions

The `rpm -i --nodigest` flag (install/linux.yml) disables digest verification.
It exists _only_ to let pre-23.3 unsigned RPMs — which carry no header digest —
install at all; modern/supported packages have digests. Rather than add a
minimum-version assertion that actively blocks End-of-Life installs, we **remove
the accommodation**: drop `--nodigest` so rpm's own digest verification is
restored. Supported versions install unchanged; a pre-23.3 unsigned RPM now
fails on rpm's own `does not verify: no digest` check — i.e. it stops working
because we stopped bending around it, not because we block it.

This is the project's general stance on EOL: stop carrying version-specific
accommodations, stop testing those paths, and stop accepting issues for them —
do **not** add forced version gates.

## Considered options

- **Keep `--nodigest`** as a vendor constraint for ≤23.2 (the conservative
  option, since those unsigned RPMs carry no digest). Rejected: the maintainer
  chose to drop pre-23.3 unsigned support, which removes the constraint.
- **Add a minimum-version assertion** that blocks EOL installs. Rejected: forced
  gating is not the chosen model; removing the accommodation achieves the goal
  without a gate and without date-tracking.

## Consequences

- An inline comment + docs note records _why_ `--nodigest` was removed, so it is
  not "helpfully" re-added later for old agents.
- This change is Linux-RPM-only; `--nodigest` exists in exactly one task — the
  fresh `rpm -i` install path.
- **Breaking change, narrowly scoped.** The only thing that stops working is a
  _fresh install_ of a pre-23.3 _unsigned_ RPM. Upgrades _from_ old versions are
  unaffected: they run through `sentinelctl control upgrade` (not `rpm -i`), and
  the documented two-step upgrade additionally uses the GPG-signed branch — so
  the intermediate hop never relied on `--nodigest`. A signed pre-23.3 package
  can still be fresh-installed via the GPG-signed branch.
- Full End-of-Life compliance (Windows EOL, the 23.4 "Legacy Plus" exception,
  RHEL6 path pruning, precise "EOL > 1 year" date logic) is separate, lower-
  priority work and is **not** part of this security pass.
