# Migrate CI from self-hosted VirtualBox runners to GitHub-hosted KVM/libvirt runners

CI ran on self-hosted VirtualBox runners because, when this test harness was
built ([ADR 0005](./0005-molecule-test-harness.md)), GitHub-hosted Actions
runners did not support nested virtualization — Molecule's Vagrant-driven guest
VMs had nowhere to run except a machine we owned and maintained. That
constraint no longer holds: GitHub-hosted Ubuntu runners now expose
hardware-accelerated nested virtualization, including on the free standard
runner tier. Paying the ongoing cost of a bespoke self-hosted host to work
around a limitation GitHub has since removed stopped making sense, so CI moves
onto GitHub-hosted runners, using **KVM/libvirt** (not VirtualBox, which is
unsupported and unreliable on the hosted fleet) as the Vagrant provider.

## Decisions

- **Provider-pluggable, static scenarios.** Each Molecule scenario keeps one
  `molecule.yml`, shared byte-for-byte between local dev and CI. The Vagrant
  provider is the single pluggable knob (an environment variable, defaulting to
  the local provider; CI overrides it), so local and CI can never drift on
  _what_ is tested — only _where the guest runs_. Provider-specific options
  with no cross-provider equivalent are removed rather than conditionally
  included, since the scenario format supports only shell-style
  default-value interpolation, not conditional blocks.
- **Forks never receive secrets automatically.** Test jobs need a real,
  credential-bearing console token, and a public repository makes fork pull
  requests an untrusted-input surface. Lint runs for every contributor,
  forks included, and is the only required check. Secret-backed test jobs run
  automatically only for same-repo branches, which already carry write access;
  a fork pull request never receives secrets by any automatic path. A
  maintainer who wants to test a fork's contribution pulls its branch into the
  repository first, so it runs as a trusted same-repo branch. Because test
  jobs are advisory rather than required, a fork's skipped run never blocks a
  required check.
- **Thin per-role callers over one reusable workflow.** Per-role workflows
  keep native path-based triggering (no third-party filtering dependency, no
  token) and delegate the actual run to one reusable workflow, parameterized by
  scenario and platform, so the run logic lives in a single place instead of
  many near-duplicate files.

## Considered options

- **Keep the self-hosted VirtualBox fleet.** Rejected: it is a standing
  maintenance and availability burden that existed solely to work around a
  limitation GitHub has since removed.
- **Larger, paid GitHub-hosted runners.** Rejected as unnecessary: nested
  virtualization works on the free standard runner tier.
- **VirtualBox on GitHub-hosted runners.** Rejected: unreliable and largely
  unsupported on the hosted fleet, unlike KVM, which is the acceleration path
  GitHub's own tooling actually exercises.
- **Grant fork pull requests secrets directly (e.g. via a `pull_request_target`
  trigger).** Rejected on security grounds: a malicious fork contribution could
  exfiltrate the console token.
- **A third-party path-filter action for per-role selectivity.** Rejected:
  adds supply-chain surface for savings that are negligible on free runners, in
  favor of each workflow's own native path filtering.

## Consequences

- The self-hosted VirtualBox fleet is retired.
- Local and CI runs share one scenario definition per role; the Vagrant
  provider is the only intentional difference between them.
- External contributors get lint feedback automatically but never see a
  secret; maintainers stay in the loop for any change that needs a full test
  run.
- Every GitHub Action used in these workflows is official or vendor-owned and
  pinned to a full commit SHA, keeping the supply-chain surface auditable and
  minimal.
