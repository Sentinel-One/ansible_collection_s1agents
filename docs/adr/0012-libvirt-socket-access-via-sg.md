# Reach the libvirt socket through `sg`, not a world-writable socket

Hosted-runner molecule jobs (see [ADR 0010](./0010-github-hosted-kvm-cloud-runners.md)) drive Vagrant, which drives libvirt over `qemu:///system` at `/var/run/libvirt/libvirt-sock`. `ci-setup` installs libvirt and adds the `runner` user to the `libvirt` group, but the job's login session predates that change, so the new membership is invisible to every later step.

## Decision

- **Keep Ubuntu's socket ACL.** The socket stays `root:libvirt 0660`; `ci-setup` no longer runs `chmod 666` on it.
- **Wrap every libvirt-touching command in `sg libvirt -c '...'`.** `sg` starts the command with `libvirt` as its group, which the user genuinely holds, so it needs no password and no fresh login. Today that is exactly one step: `Molecule test` in `run-molecule.yml`. Molecule launches Vagrant, Vagrant creates the guest through libvirt, so any molecule invocation against a Vagrant scenario must be wrapped.
- **Keep the `/dev/kvm` udev rule.** It is GitHub's documented recipe for nested virtualization and is left as-is; the runner therefore needs no `kvm` group membership.

## Why not `chmod 666`

- **It is root-equivalent for every local UID.** Ubuntu sets `auth_unix_rw = "none"` and relies on the socket's group to gate access. A world-writable RW socket hands full libvirt control — and so root — to any process on the host, including the unprivileged service accounts that run guests and `dnsmasq`.
- **It does not persist.** systemd owns the socket via `libvirtd.socket`; any socket re-creation restores `0660` and silently breaks later steps.
- **It made the `usermod` dead code.**

## Considered options

- **`setfacl -m u:runner:rw` on the socket.** Scoped to one user, but just as non-persistent as `chmod`.
- **A polkit rule for `org.libvirt.unix.manage` with `auth_unix_rw = "polkit"`.** Needs no wrapping, but reconfigures libvirtd and may pull in `polkitd`; too many moving parts for an ephemeral runner.
- **Run molecule under `sudo`.** Grants root to the whole Ansible/Vagrant stack; strictly worse.

## Consequences

- Any new workflow step that runs `molecule` against a Vagrant scenario, `vagrant`, or `virsh` must use `sg libvirt -c '...'`, or it fails with a libvirt permission-denied error.
- Commands inside `sg -c` run under `/bin/sh` (dash), not bash; keep them to a single simple command and single-quote them so the step's environment is expanded by the inner shell.
- VM-less scenarios (e.g. `windows-tier-matrix`, `enable_kvm: "false"`) are not wrapped: they never touch libvirt, and the `libvirt` group does not exist on those runners.
