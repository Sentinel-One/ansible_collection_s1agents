# Split linting by domain: prettier for prose, ansible-lint for playbooks

The collection needs consistent formatting for its docs and JSON, correctness
checks for its Ansible content, and a guard against committed secrets — without
depending on a licensed meta-linter to bundle those tools together. We assign
each concern to the narrowest tool that owns it and orchestrate them with the
`pre-commit` framework, which provisions its own runtimes (including the Node
that prettier needs on machines that have none).

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
