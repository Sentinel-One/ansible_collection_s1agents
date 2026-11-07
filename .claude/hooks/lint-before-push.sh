#!/usr/bin/env bash
# PreToolUse push gate — runs ansible-lint (what CI's required Lint job runs)
# and the trufflehog secret scan before any `git push` leaves the machine. The
# edit hook (lint-after-edit.sh) only sees Write/Edit, so files rewritten from
# Bash would otherwise reach CI unlinted. Prettier is left out: it rewrites
# files rather than checking them. See docs/adr/0006-linting-toolchain.md.
#
# The trufflehog scan covers the commits being pushed (everything since the
# upstream, or since origin/main when the branch has none). It is deliberately
# separate from the pre-commit hook, which scans only the staged changes about
# to be committed: `--since-commit HEAD` finds nothing once work is committed.
# This catches commits that skipped any commit-time scan (--no-verify, another
# machine). Keep the flags aligned with .pre-commit-config.yaml.

cmd=$(/usr/bin/python3 -c 'import sys, json; print(json.load(sys.stdin).get("tool_input", {}).get("command", ""))' 2>/dev/null)

# Only gate commands that actually invoke `git push`.
printf '%s' "$cmd" | grep -Eq '(^|[^[:alnum:]_./-])git([[:space:]]+-C[[:space:]]+[^[:space:]]+)?[[:space:]]+push([^[:alnum:]_-]|$)' || exit 0

cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}" 2>/dev/null || exit 0

failed=0
if ! lint_out=$(.venv/bin/ansible-lint 2>&1); then
  printf 'ansible-lint failed; fix before pushing:\n%s\n\n' "$(printf '%s\n' "$lint_out" | tail -40)" >&2
  failed=1
fi
# Scan base: the merge-base with the upstream, else with origin/main or
# origin/master. With no remote ref at all, scan the full history (fail closed).
base=""
for ref in '@{u}' origin/main origin/master; do
  if git rev-parse --verify -q "$ref" >/dev/null 2>&1; then
    base=$(git merge-base HEAD "$ref" 2>/dev/null) && break
  fi
done
th_args=(git file://. --no-update --only-verified --fail)
[ -n "$base" ] && th_args+=(--since-commit "$base")
if ! th_out=$(trufflehog "${th_args[@]}" 2>&1); then
  printf 'trufflehog found a possible secret; do not push:\n%s\n' "$(printf '%s\n' "$th_out" | tail -40)" >&2
  failed=1
fi

[ "$failed" -eq 0 ] || exit 2
exit 0
