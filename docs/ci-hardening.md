# CI hardening notes

This document records unsafe patterns that existed in the GitHub Actions
workflows and the mitigations to apply in any future CI rebuild. These
patterns are **mitigated or moot in the current repository state** (no live
self-hosted runner, no `requirements.txt`) — they are documented here so they
are not accidentally re-introduced.

## Pattern 1 — Unquoted input interpolated into a `run:` shell step

**Risk.** Injecting `${{ github.event.* }}` or other external values directly
into a `run:` shell string allows an attacker to break out of the string with
shell metacharacters (e.g. `; malicious-command`).

**Fix.** Pass untrusted values through `env:` and reference them as shell
variables inside the `run:` block:

```yaml
# Bad — direct injection
run: echo ${{ github.event.pull_request.title }}

# Good — through env:
env:
  PR_TITLE: ${{ github.event.pull_request.title }}
run: echo "$PR_TITLE"
```

## Pattern 2 — Unconditional `requirements.txt` auto-install

**Risk.** Installing a floating `requirements.txt` in CI means any package
update (or a compromised package) is automatically pulled in without review.

**Fix.** Remove the auto-install step, or replace it with a committed,
hash-locked file and verify hashes before installing:

```bash
pip install --require-hashes -r requirements-locked.txt
```

## Pattern 3 — `pull_request` checkout of PR-head code on a self-hosted runner

**Risk.** A `pull_request` event from a fork checks out untrusted PR-head code
and runs it on the same runner that holds secrets. A malicious PR can exfiltrate
all secrets accessible to the runner.

**Fix.**

- Use **ephemeral runners** for untrusted code (each run gets a clean VM).
- Require maintainer approval before running CI on PRs from outside
  collaborators (`pull_request_target` with environment protection, or
  the "Require approval for first-time contributors" setting).
- Pin all third-party actions to a full commit SHA (not a mutable tag):
  ```yaml
  uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
  ```
