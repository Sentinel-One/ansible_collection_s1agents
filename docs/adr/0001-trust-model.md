# Trust model: trusted-CLI by default, AWX/survey as the defense-in-depth driver

Ansible treats operator-supplied variables as part of the trusted control plane,
so in the default CLI deployment "inject via host*var" crosses no privilege
boundary (anyone who can set a variable can already run arbitrary modules). We
nonetheless validate and quote operator inputs because this is a \_published
collection consumed downstream*, sometimes under AWX/AAP where lower-privileged
users supply variables via job-template surveys — there the variable-setter is
not the play author. We therefore right-size the "variable injection" findings
(MSI properties, rpm basename, custom-install-path delete) out of Critical/High
to Low/Medium **defense-in-depth** findings, and fix them by validating +
quoting rather than treating them as standing RCEs.

## Consequences

- Input-validation asserts live **centrally in `s1_agent_common`**,
  which every role declares as a meta dependency, so it runs first for all roles.
  Asserts are conditional (`defined and not none → must match`) so info/uuid-only
  runs are unaffected.
- Validation runs right after `s1_agent_common`'s read-only fact gather, before any change to the endpoint, so OS-specific rules (e.g. the Linux vs. Windows `s1_agent_custom_install_path` shape) can key on `ansible_os_family`.
- Every accept/reject rule is pinned by a case in the VM-less `input-validation` molecule scenario (`extensions/molecule/input-validation/vars/cases.yml`). A newly found bypass gets a failing reject case there before its fix.
- The genuinely real boundary — an unprivileged local user on the `root`/`SYSTEM`
  endpoint — is treated as a hard boundary regardless of how variables are
  supplied. Those findings (the `/tmp` race, passphrase on argv) are fixed
  unconditionally, not right-sized. See [ADR 0003](./0003-passphrase-off-argv.md)
  and [ADR 0004](./0004-tempfile-work-dirs.md).
- Fields from Management Console API responses (package `fileName`, `link`, `sha1`) are still shape-checked and kept off command strings, but as hygiene, not as a boundary. Findings that assume a hostile console are right-sized the same way.
- We do not set the machine-wide `TransformsSecure` Installer policy, even though scanners recommend it against MSI `TRANSFORMS=` injection. It only controls where Windows Installer caches a transform; it does not stop msiexec loading one named on the command line. It would also change Installer behaviour for every other product on the endpoint and contend with customer Group Policy. The defence against injected MSI properties is strict validation of every value the collection puts on the installer command line.
