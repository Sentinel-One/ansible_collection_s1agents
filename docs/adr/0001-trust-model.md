# Trust model: trusted-CLI by default, AWX/survey as the hardening driver

Ansible treats operator-supplied variables as part of the trusted control plane,
so in the default CLI deployment "inject via host*var" crosses no privilege
boundary (anyone who can set a variable can already run arbitrary modules). We
nonetheless validate and quote operator inputs because this is a \_published
collection consumed downstream*, sometimes under AWX/AAP where lower-privileged
users supply variables via job-template surveys — there the variable-setter is
not the play author. We therefore right-size the "variable injection" findings
(MSI properties, rpm basename, custom-install-path delete) out of Critical/High
to Low/Medium **vendor hardening** obligations, and fix them by validating +
quoting rather than treating them as standing RCEs.

## Consequences

- Input-validation asserts live **centrally in `s1_agent_common`**,
  which every role declares as a meta dependency, so it runs first for all roles.
  Asserts are conditional (`defined and not none → must match`) so info/uuid-only
  runs are unaffected.
- The genuinely real boundary — an unprivileged local user on the `root`/`SYSTEM`
  endpoint — is treated as a hard boundary regardless of how variables are
  supplied. Those findings (the `/tmp` race, passphrase on argv) are fixed
  unconditionally, not right-sized. See [ADR 0003](./0003-passphrase-off-argv.md)
  and [ADR 0004](./0004-tempfile-work-dirs.md).
