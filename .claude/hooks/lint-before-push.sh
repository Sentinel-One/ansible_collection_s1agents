#!/usr/bin/env bash
# PreToolUse push gate — runs ansible-lint (what CI's required Lint job runs)
# and the trufflehog secret scan before any `git push` leaves the machine. The
# edit hook (lint-after-edit.sh) only sees Write/Edit, so files rewritten from
# Bash would otherwise reach CI unlinted. Prettier is left out: it rewrites
# files rather than checking them. See docs/adr/0006-linting-toolchain.md.

cmd=$(/usr/bin/python3 -c 'import sys, json; print(json.load(sys.stdin).get("tool_input", {}).get("command", ""))' 2>/dev/null)

# Only gate commands that actually invoke `git push`.
printf '%s' "$cmd" | grep -Eq '(^|[^[:alnum:]_./-])git([[:space:]]+-C[[:space:]]+[^[:space:]]+)?[[:space:]]+push([^[:alnum:]_-]|$)' || exit 0

cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}" 2>/dev/null || exit 0

failed=0
if ! lint_out=$(.venv/bin/ansible-lint 2>&1); then
  printf 'ansible-lint failed; fix before pushing:\n%s\n\n' "$(printf '%s\n' "$lint_out" | tail -40)" >&2
  failed=1
fi
if ! th_out=$(.venv/bin/pre-commit run trufflehog --all-files 2>&1); then
  printf 'trufflehog found a possible secret; do not push:\n%s\n' "$(printf '%s\n' "$th_out" | tail -40)" >&2
  failed=1
fi

[ "$failed" -eq 0 ] || exit 2
exit 0
