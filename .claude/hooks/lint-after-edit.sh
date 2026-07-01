#!/usr/bin/env bash
# PostToolUse lint hook — routes a just-written/edited file to a fast linter by
# extension, so we lint immediately without paying for the wrong (slow) tool:
#   .md / .json   -> prettier, auto-format in place (silent; never blocks)
#   .yml / .yaml  -> yamllint, report-only (blocks with feedback on findings)
# ansible-lint is intentionally NOT run here (~15s/file); it stays a manual /
# pre-commit gate. See docs/adr/0006-linting-toolchain.md.

# Extract the edited file path from the PostToolUse JSON on stdin.
file=$(/usr/bin/python3 -c 'import sys, json; print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))' 2>/dev/null)

[ -n "$file" ] || exit 0
[ -f "$file" ] || exit 0

# pre-commit / yamllint config resolution needs the repo root as cwd.
cd "${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$file")" rev-parse --show-toplevel 2>/dev/null)}" 2>/dev/null || exit 0

case "$file" in
  *.md | *.json)
    # Auto-format in place; swallow output and always succeed.
    .venv/bin/pre-commit run prettier --files "$file" >/dev/null 2>&1
    exit 0
    ;;
  *.yml | *.yaml)
    if out=$(.venv/bin/yamllint "$file" 2>&1); then
      exit 0
    fi
    printf 'yamllint reported issues in %s:\n%s\n' "$file" "$out" >&2
    exit 2
    ;;
esac

exit 0
