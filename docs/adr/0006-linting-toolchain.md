# Split linting by domain: prettier for prose, ansible-lint for playbooks

The collection needs consistent formatting for its docs and JSON, correctness
checks for its Ansible content, and a guard against committed secrets — without
depending on a licensed meta-linter to bundle those tools together. We assign
each concern to the narrowest tool that owns it and orchestrate them with the
`pre-commit` framework. trufflehog runs as a locally installed binary
(`language: system`), installed once per machine; prettier is provisioned by
`pre-commit` (see the amendments below).

- **prettier** formats **Markdown and JSON only** (`proseWrap: always`). All
  YAML is excluded via `.prettierignore` so prettier never competes with
  ansible-lint over Ansible files (quote style, indentation, block scalars).
- **ansible-lint** (`production` profile) owns YAML and playbook correctness. It
  bundles yamllint, so YAML style is covered without a second YAML formatter.
- **trufflehog** scans for committed secrets.

`pre-commit` is configured but its git hooks are **not** auto-installed: the
tools run on demand (`pre-commit run --all-files`), matching how the toolchain
was used before. Editor integration lives in `.vscode/settings.json`
(prettier-vscode for Markdown, redhat.vscode-yaml for YAML).

## Consequences

- **Dedicated static-analysis scanners for IaC and CI workflows are out of
  scope.** Ansible-specific security posture is covered by ansible-lint's
  `production` profile and the ADRs in this directory; there is no separate IaC
  policy scanner. If workflow or IaC scanning is wanted later, add it as its own
  `pre-commit` hook rather than reviving a bundled meta-linter.
- Secret scanning is local-only. It depends on `trufflehog` being installed on
  the developer's machine; it does not gate CI (the GitHub Actions workflows are
  retained for historical context and are not part of the active gate).
- Markdown is prose-wrapped by prettier. Doc edits should be run through
  `pre-commit run --all-files` (or format-on-save) to avoid reflow churn in
  review.
- The toolchain (including `pre-commit` itself) is declared in
  `requirements-dev.txt` and installed via **uv** into a single repo-local
  `.venv` (see
  [ADR 0007](./0007-uv-managed-venv-toolchain.md)), so every tool here runs as
  `.venv/bin/<tool>` with no personal environment setup required.

## Amendment: prettier is a local install (superseded)

_Superseded by the next amendment; kept for the reasoning._ The prettier hook originally used `mirrors-prettier`, so `pre-commit` would
download Node and prettier itself. That download goes to the npm registry, and
behind a TLS-inspecting proxy it fails with `ECONNRESET` whenever proxy auth has
lapsed, which blocked `pre-commit run --all-files` entirely (including the
trufflehog hook). prettier is now a `repo: local` hook with `language: system`,
the same shape as trufflehog, running with the flags the mirror hook used
(`--write --list-different --ignore-unknown`). Considered and rejected:
`language: node` (still fetches from the npm registry on first use) and a
`package.json` with a repo-local `node_modules` (adds a second package manager
to a repo whose toolchain is otherwise uv-only, ADR 0007).

- Prerequisite: `brew install prettier`, once per machine. The hook is no longer
  pinned to a version, so a machine's prettier can drift from another's; an
  unexpected Markdown reflow after upgrading prettier is the sign. Formatting
  was verified against 3.9.10, which left every tracked Markdown and JSON file
  unchanged except two files that had never been formatted (the previously
  pinned 3.5.3 is not needed to reproduce the repo's formatting).
- The hook fails with ``Executable `prettier` not found`` if it is not
  installed.

## Amendment: prettier is back on mirrors-prettier

The local-install workaround is reverted. The proxy problem it addressed no
longer blocks `pre-commit` from downloading Node and prettier, so the hook is
again the `mirrors-prettier` hook, and there is no per-machine prettier
prerequisite. The mirror has no tag past `v3.1.0` (then `v4.0.0-alpha.*`), so
`rev` pins only the hook definition; the prettier that runs is pinned by
`additional_dependencies` (`prettier@3.5.3`). Keep the two in mind separately
when bumping. Pinning restores identical formatting across machines, which the
local install could not guarantee.

## Amendment: trufflehog scans staged changes at commit and the unpushed range at push

The two scans have different jobs, so they use different commands.

- **Commit time** (`.pre-commit-config.yaml`): `--since-commit HEAD
--no-update --only-verified --fail` scans the staged changes about to be
  committed. `--no-update` skips the self-update check, which fails behind a
  TLS-inspecting proxy. `--only-verified` drops unverified ("unknown") findings,
  so only live credentials fail the scan.
- **Push time** (`.claude/hooks/lint-before-push.sh`): the same flags, but with
  `--since-commit` set to the merge-base with the upstream (else `origin/main`),
  so it scans the commits being pushed. The commit-time command cannot do this:
  once work is committed, `--since-commit HEAD` has nothing to scan, so the push
  gate would pass even with a committed secret. With no remote ref, the hook
  scans the full history. Keep the shared flags aligned between the two.
