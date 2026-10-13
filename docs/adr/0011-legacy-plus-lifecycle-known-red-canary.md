# Prove the Legacy Plus lifecycle locally; keep its cloud job as a known-red canary

`extensions/molecule/windows-legacy-plus` proves the Legacy Plus tier end-to-end on a real guest (see [ADR 0008](./0008-windows-support-tier-routing.md)). It passes in full locally under VirtualBox and has never passed on a GitHub-hosted runner, for reasons outside this collection's control. So the local run is the authoritative gate, and the cloud job is kept only as a non-blocking canary.

## The external limitation

On hosted `ubuntu-24.04` under libvirt, the frozen `SentinelOneInstaller_windows_64bit_v23_4_5_337.exe` exits `rc: -1073741819` (`STATUS_ACCESS_VIOLATION` — a crash, not a clean error) with `stderr: Failed to access Sentinel Agent registry key`. An immediate retry reproduced the identical `rc` and `stderr`, so it is deterministic, not flaky.

Two comparisons bound it. The same box and binary pass locally, so the package is not broken. And the Windows leg of `s1_agent_install.yml` passes on the same hosted infrastructure with every variable this repo controls identical — memory, vCPUs, `ci-setup` call, runner image, provider, role-invocation shape. So the failure needs both this vintage guest and GitHub's nested KVM/libvirt stack: environmental, not a bad package. Nor is it starvation — the box pulls, boot takes ~8 minutes against an 1800s timeout, auth works, no disk pressure.

Two accommodations are load-bearing, not cleanup targets: the scenario's `requirements.yml` pins `ansible.windows<2.8.0` (2.8.0+ made `win_package`'s `Get-FileHash` checksum unconditional, and that cmdlet predates PowerShell 4) plus `community.windows<3.0.0` (its 3.x line would drag that pin back up), and it sets `ANSIBLE_SKIP_TAGS` to bypass the roles' PowerShell 4+ assert, since this box ships PowerShell 3.0 with no working upgrade path.

## Decisions

- **The local sweep is authoritative.** `scripts/gate.yml` includes the scenario; a green local run is what establishes the frozen flow works. Cloud CI cannot be that proof.
- **The cloud release job is a deliberate known-red canary.** It runs in its own `ci-release.yml` job, outside `release`'s `needs:`, so it reports independently but can never fail a release. Red is the expected state — an _external limitation_, not a transient error to retry and not a defect to fix. It is kept only because it going green would mean the upstream cause changed.
- **A separate job, because `continue-on-error` cannot express this.** Jobs calling a reusable workflow via `uses:` support only a restricted key set (`name`, `uses`, `with`, `secrets`, `needs`, `if`, `permissions`, `strategy`, `concurrency`); adding `continue-on-error` makes GitHub reject the whole file rather than ignore the key.
- **`windows_legacy_plus.yml` is dispatch-only.** No `push`, no `pull_request` — an automatic trigger on a known-red job is noise, and having no `pull_request` trigger means it can never appear as a PR check at all.
- **The roles assert PowerShell 4+ instead of failing opaquely,** tagged so it can be bypassed, so a real host below PowerShell 4 gets an actionable message rather than the native crash that took a full investigation to explain.

## Considered options

- **Hard-block releases on it.** Rejected: every release would depend on a decade-EOL guest whose failure is external and permanent.
- **Delete the cloud job.** Rejected: it costs nothing to ignore and is the only automatic notice if the upstream situation changes.
- **Keep chasing the crash.** Rejected on evidence: roles proven by local passes, hosted runners proven by the Modern-tier job, all controllable variables already identical. What is left is GitHub's runner environment, which this repo cannot change or usefully instrument.
- **Trigger the workflow automatically on Legacy Plus changes.** Rejected: guaranteed-red runs train maintainers to ignore CI.

## Consequences

- A red `windows-legacy-plus` job at release is expected and is not a blocker or a regression. Validate Legacy Plus changes with a local run.
- The dependency pins and the assert bypass must survive dependency housekeeping; removing any one breaks the local run this tier's proof rests on.
- If the canary ever goes green, the cloud path is viable again and this decision can be revisited.
