# Unpredictable root-owned tempfile work directories

The agent package was staged in a fixed, world-known path (`s1_tmp_linux`
default `/tmp/s1_install`) created `mode 0755` with no `follow: no`. A local
unprivileged user could pre-create the directory or plant symlinks before the
root-run copy/install, redirecting writes or swapping the package — a local→root
TOCTOU. We replace the fixed path with `ansible.builtin.tempfile state=directory`
(run as root), giving an unpredictable, `0700`, root-owned directory per run,
with `follow: no` on create and cleanup. `s1_tmp_linux` / `s1_tmp_windows` are
kept as an optional, documented **override**, not removed.

## Considered options

- **Harden the fixed path in place** (root-owned `0700`, `follow: no`, assert not
  a symlink). Rejected as the primary fix: the path stays predictable, so it only
  raises the bar rather than eliminating pre-creation.
- **Remove `s1_tmp_*` from the public contract.** Rejected: needless breaking
  change for operators who set it.

## Consequences

- The dynamic path is threaded into the included `s1_import_gpg_key` role so it
  does not recreate a predictable `0755` directory.
- Applied to install, upgrade, the gpg-key role, the Windows `%TEMP%` work dir,
  and the controller-local download cache.
