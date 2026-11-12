# Issue tracker: Beads

Issues and specs for this repo live in a [Beads](https://github.com/gastownhall/beads) database under `.beads/`. Use the `bd` CLI for all operations.

## Conventions

- **Create an issue**: `bd create "<title>" -d "..."`. Types via `-t` (`task` is the default; `bug`, `feature`, `chore`, `epic`, `decision`), priority via `-p` (0 to 4, 0 highest, default 2). Use `--body-file <file>` (or `--stdin`) for multi-line descriptions, and `--silent` to capture just the new id when scripting.
- **Read an issue**: `bd show <id> --json` for the full record (labels, body, status, dependencies), plus `bd comments <id> --json` for the discussion thread. Drop `--json` for human-readable output.
- **Make an issue a child of a parent**: `bd create "<title>" --parent <parent-id>`, which gives it a hierarchical id (`<parent-id>.1`, `<parent-id>.2`, ...). List a parent's children with `bd list --parent <parent-id>`. A child **inherits the parent's labels** unless you pass `--no-inherit-labels`. Always pass it when publishing a set of tickets and then label each child deliberately: a parent carrying `ready-for-agent` otherwise hands that label to every child, including the ones meant for a human. (`bd label propagate` is the deliberate opposite, for pushing a label down on purpose.)
- **Give a parent children, and it becomes an epic**: `bd update <parent-id> -t epic`. Only type `epic` is reported on by `bd epic status`, so an issue that has acquired children but kept its original type silently has no progress rollup. Retype it when the children are created, not later.
- **List issues**: `bd list` with `--status`, `--label`, `--type`, `--assignee`, and `--parent` filters. `bd ready` lists open issues with no open blockers; `bd blocked` lists the inverse, each with the blockers holding it.
- **Comment on an issue**: `bd comment <id> "..."`
- **Apply / remove labels**: `bd label add <id> <label>` / `bd label remove <id> <label>`
- **Close**: `bd close <id> --reason "..."`. Reopen with `bd reopen <id>`.
- **Blocking edges**: Beads's native dependencies, the canonical representation: `bd dep add <blocked-id> <blocker-id>` (the first argument depends on the second). `bd dep tree <id>` shows the graph. A dependency-blocked issue drops out of `bd ready` until every blocker is closed. Do not also write a `Blocked by` line in the issue body when the edge exists.

`bd` auto-discovers the workspace from the repo's `.beads/` directory; run it from anywhere inside the clone. Before the first write of a session, run `bd where` and confirm it names this repo's `.beads/` (a stale `BEADS_DIR` or a different clone would send issues to the wrong database). `BEADS_DIR`, if set, must point at the `.beads` directory itself, not the project root.

Issue data lives in a local Dolt database that git does not track (only `.beads/` config files are committed), so issues travel through Beads itself, not through commits: `bd dolt push` syncs the database to the repo's git remote (with no Dolt remote configured, bd adopts one derived from the git origin only with consent, so an agent should run `bd dolt push --yes` the first time, or `--no-adopt` to refuse; the data is stored under `refs/dolt/data`, separate from the code branches), `bd dolt pull` fetches it back, and `bd export` / `bd import` move JSONL snapshots where a remote is not an option. On a fresh clone, `bd bootstrap --yes` sets the database up non-destructively (`--yes` skips the confirmation prompt; it is also skipped automatically off a TTY or when `CI=true`).

## Triage state

Beads has statuses as well as labels, and `bd ready` treats any `open` issue with no open blockers as claimable work. Apply the triage-role labels from `triage-labels.md` verbatim with `bd label add`, and pair the two waiting roles with a status so untriaged work never looks claimable:

- `needs-triage` / `needs-info`: add the label, then `bd update <id> --status blocked` so the issue stays out of `bd ready` while a human decision is pending.
- `ready-for-agent`: add the label, then `bd update <id> --status open` to restore it to the frontier.
- `ready-for-human`: add the label, then `bd update <id> --status blocked`. Unlike `ready-for-agent`, it must stay out of `bd ready` so no agent can pick it up. The label, not the status, says why it is parked: `blocked` here means "reserved for a human", not "waiting on a dependency". A human finds these with `bd list --label ready-for-human` and takes one with `bd update <id> --status in_progress -a <name>`.
- `wontfix`: add the label, then `bd close <id> --reason "wontfix: <why>"`.

### Never hand a human ticket to an agent

Three layers keep `ready-for-human`, `needs-triage` and `needs-info` tickets away from agents. Do not rely on any one alone.

1. **Status hold-out**: those tickets sit at `blocked` (above), so `bd ready` never returns them.
2. **Label filter**: every frontier query excludes them explicitly, in case a status drifts back to `open`: `--exclude-label ready-for-human,needs-triage,needs-info`.
3. **Rule**: before claiming or implementing a ticket, read it with `bd show <id> --json`. If its labels include `ready-for-human`, `needs-triage` or `needs-info`, stop and tell the user, unless the user named that ticket explicitly. This applies even when a skill (for example `/implement-spec`) derives its frontier from the dependency graph instead of from `bd ready`.

## When a skill says "publish to the issue tracker"

Create a Beads issue with `bd create`. When publishing a set of tickets with blocking edges, create blockers first with `--silent` to capture their ids, then pass `--deps <blocker-id>` on each dependent ticket (comma-separate several). Pass `--no-inherit-labels` on every child so no ticket arrives pre-labelled from its parent, retype the parent `-t epic`, and afterwards verify the result rather than assuming it: the labels on each child, and that `bd ready --parent <parent-id>` returns only the tickets that genuinely have no blockers. The frontier is then `bd ready --exclude-label ready-for-human,needs-triage,needs-info` (scope it to a spec's epic with `--parent <epic-id>`); see **Never hand a human ticket to an agent**.

## When a skill says "fetch the relevant ticket"

Run `bd show <id> --json`, plus `bd comments <id> --json` when the discussion matters.

## Wayfinding operations

Used by `/wayfinder`. The **map** is an epic issue with **child** issues as tickets.

- **Map**: a single issue of type `epic` labelled `wayfinder:map`, holding the Notes / Decisions-so-far / Fog body: `bd create "<map title>" -t epic -l wayfinder:map -d "..."`. Update the body with `bd update <map> -d` (or `--body-file`).
- **Child ticket**: created with `--parent <map-id>`, which gives it a hierarchical id (`<map-id>.1`, `<map-id>.2`, ...). Labels: `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`).
- **Blocking**: Beads's native dependencies, the canonical representation: `bd dep add <child> <blocker>`. A ticket is unblocked when every blocker is closed; `bd dep tree <map-id>` shows the whole graph.
- **Frontier query**: `bd list --ready --parent <map-id> --no-assignee --exclude-label ready-for-human,needs-triage,needs-info`; first in map order wins.
- **Claim**: `bd update <n> --claim` (atomically assigns you and sets `in_progress`), the session's first write. A claim carries a lease that expires after a TTL (default 5 minutes): keep it alive with `bd heartbeat <n>` while the ticket is in progress, and hand it back with `bd unclaim <n>` if you stop. A stale claim is reverted to open by `bd reclaim --older-than <duration>`, which is meant to be run by a supervisor. To reassign a ticket only while its current owner still holds it, use `bd update <n> --if-assignee <owner> -a <new>` (exit code 13 means another actor won the race, so skip the ticket rather than retry).
- **Resolve**: `bd comment <n> "<answer>"`, then `bd close <n> --reason "<one-line answer>"`, then append a context pointer (gist + link) to the map's Decisions-so-far.
- **Progress**: `bd epic status <map-id>` reports how many children are closed.
