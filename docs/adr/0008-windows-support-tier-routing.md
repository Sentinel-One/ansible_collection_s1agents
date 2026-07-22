# Route Windows hosts by support tier (Legacy / Legacy Plus / Modern)

SentinelOne Agent 23.4 is End of Life on Windows _except_ on a fixed list of
older OSes ("Legacy Plus") where 23.4 remains the last supported version. Agent
24.1+ installs only on 64-bit Windows. Below Legacy Plus sits an even older
"Legacy" group (Windows XP/Vista/2003/2008 non-R2, POSReady 2009) that needs a
different installer package this collection does not manage. This is the "23.4
Legacy Plus exception" that [ADR
0002](./0002-remove-eol-accommodations-not-gate.md) deferred as separate work.

Source data (SentinelOne EOL policy — Windows 23.3 and older are EOL; 23.4 is
EOL on every Windows platform _except_ the Legacy Plus list below; Linux 23.4
and older are EOL; agent lifecycle is GA 0–9 months / EOS 9–15 months / EOL 15+
months after release):

| Tier                                        | Windows OSes                                                                                                                                                                                     |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Legacy Plus** (23.4 last supported)       | Windows 10 32-bit; Windows 8.1 32-bit; Windows 8 32/64-bit; Windows 7 SP1 32/64-bit; POSReady 7; Server / Storage Server / Server Core 2012 (**not** R2) 32/64-bit; Server 2008 R2 SP1 32/64-bit |
| **Legacy** (different installer, unmanaged) | Windows XP; Windows Vista; POSReady 2009; Server 2003; Server 2008 non-R2                                                                                                                        |

We classify every Windows host into one of three tiers with a single fact,
`s1_windows_tier` (`legacy` | `legacy_plus` | `modern`), computed once in
`s1_agent_common`, and route on it:

- **`legacy`** — `ansible_distribution_version` (the NT version) `< 6.1`.
  `s1_agent_install`/`s1_agent_upgrade` route these to the existing
  `unsupported.yml` fail-loud task.
- **`legacy_plus`** — not `legacy`, and either 32-bit Windows _or_ a 64-bit
  edition whose `ansible_distribution` (WMI `Caption`) matches the
  `s1_legacy_plus_x64_editions` substring matrix. Routed to a per-role
  `windows_legacy_plus.yml`.
- **`modern`** — everything else. Reached via the existing `with_first_found`
  dispatch, whose Windows candidate is renamed to `windows_<bitness>.yml`.

Each tier is reached with `include_tasks` off `s1_windows_tier`, mirroring the
existing `s1_agent_info` RHEL-6 dispatch shape. Only `windows_legacy_plus.yml`
carries a version assertion — a ceiling, `s1_agent_version < 24.1` — since
those OSes genuinely cannot run newer versions. The Modern flow carries no
version assertion at all: 23.1–23.4.x are EOL there but still install/upgrade
today with no gate, and per [ADR
0002](./0002-remove-eol-accommodations-not-gate.md) that's a support-policy
question this collection deliberately doesn't gate, not a technical
incompatibility worth asserting on.

## Why the fact plumbing forces this shape

The `ansible.windows` `setup` module derives Windows facts as follows (verified
against `plugins/modules/setup.ps1` and the `Win32_OperatingSystem` docs):

- `ansible_distribution` = `Win32_OperatingSystem.Caption` — an edition-suffixed
  string (`Microsoft Windows Server 2012 R2 Standard`). Its **product-name
  portion is a brand string Microsoft does not translate** (backed by registry
  `ProductName`, kept consistent across MUI language packs), so substring matches
  on `Windows 7`, `Server 2012`, `2012 R2` are robust on French/German/Japanese
  hosts.
- `ansible_distribution_version` = `[Environment]::OSVersion.Version` — the NT
  version (`5.1`, `6.0`, `6.1`, `6.3`, `10.0`). Numeric, **not localized**. The
  Windows "version lie" only ever makes a _newer_ OS under-report (never below
  6.2), so the `< 6.1` Legacy floor is safe in both directions.
- `ansible_architecture` = `Win32_OperatingSystem.OSArchitecture` — the OS
  install bitness, but **localized** (`64 bits` on French, `64-Bit` on German).

Two consequences drive the design:

1. **Legacy Plus cannot be a version key.** It is a scattered set — NT 6.1, 6.2,
   6.3-32-bit, 10.0-32-bit — with the 64-bit 6.3/10.0 siblings (Windows 8.1
   64-bit, Server 2012 R2, modern Windows) _excluded_. No numeric threshold
   describes it; it needs OS identity (Caption) + bitness. By contrast the
   **Legacy tier is contiguous** (`NT < 6.1`), so it _is_ a clean version key.
2. **Bitness must be normalized before use.** Because `ansible_architecture` is
   localized, keying a filename or comparison off it breaks on non-English hosts.
   `s1_agent_common` computes `s1_os_bitness` (`64-bit`/`32-bit`) from
   `[Environment]::Is64BitOperatingSystem` (a locale-independent .NET boolean)
   and everything downstream keys off that collection-owned token.

## Considered options

- **`with_first_found` filename dispatch for Legacy Plus** (mirror RHEL 6's
  `redhat_6.yml`). Rejected: the Caption is edition-suffixed and formally
  localizable, so the rendered filename (`microsoft_windows_server_2012_standard.yml`)
  is neither stable nor buildable. `first_found` is kept for the _arch_-level
  split (`windows_64-bit.yml`), which is a controlled token.
- **A version/NT threshold for Legacy Plus** (e.g. "< 6.4 but not 2012 R2").
  Rejected: Windows 10 32-bit is NT 10.0 and must be _included_, so no threshold
  captures the set. Used only for the Legacy floor, where it fits.
- **Two booleans (`s1_is_legacy`, `s1_is_legacy_plus`)** vs. **a `s1_windows_tier`
  enum.** Chose the enum: it reads as a single classification, encodes precedence
  in one place, gives read-only roles something to report, and extends to a
  fourth group by adding one clause.
- **A thin guard in `windows_legacy_plus.yml`** (assert only, shared install
  after) vs. **intentionally duplicated install steps.** Chose duplication: it
  freezes the known-good 23.4 install flow so the Modern flow can evolve freely,
  accepting copy-paste as the cost of that decoupling.
- **A bespoke `assert` for the Legacy tier** vs. **routing to `unsupported.yml`.**
  Chose the `include_tasks: unsupported.yml` route: one fail-loud path, symmetric
  with the other two tier includes, at the cost of the generic "not supported"
  message (loses the "needs a different installer" nuance).
- **Gate the Modern flow on `s1_agent_version` (either narrowly, blocking only
  `23.4.x`, or broadly, requiring `>= 24.1`)** vs. **no version assertion at
  all.** Rejected both gated options: 23.4 (and 23.1–23.3) install/upgrade on
  Modern hosts today with no version check, and that's a plain EOL-support
  question, not a technical incompatibility — exactly what [ADR
  0002](./0002-remove-eol-accommodations-not-gate.md) says not to gate. The
  Legacy Plus ceiling assertion is kept because it's the opposite kind of
  constraint: those OSes cannot run newer versions at all, a real technical
  limit rather than a support-policy choice.
- **Legacy Plus default version.** When a Legacy Plus host has no explicit
  `s1_agent_version`, `s1_agent_download`'s existing fallback (`release_n_minus`)
  would silently fetch the latest GA release — which then fails the
  `windows_legacy_plus.yml` ceiling assert after an unnecessary download.
  Resolved by having `s1_agent_common` set `s1_agent_version` to a
  manually-maintained constant (`s1_legacy_plus_default_version`, alongside
  `s1_product_id` in `vars/windows.yml`) whenever `s1_windows_tier ==
legacy_plus` and no version was requested — for both `s1_agent_install` and
  `s1_agent_upgrade`, since both include `s1_agent_common` first. Chose a
  constant over querying the console for the newest `23.4.*` release:
  `s1_agent_download`'s version matching is exact-only (`selectattr('version',
'equalto', ...)`), so a constant needs no new download-role logic, and the
  pinned version changes infrequently, if ever.
- **Legacy Plus 2012R2-exclusion test fixture.** The retired
  `WindowsServer2012R2` Vagrant box is revived specifically to assert
  `s1_windows_tier == 'modern'` against real facts (proving the `not_match:
"2012 R2"` clause), but is NOT added to the default `scripts/gate.yml` matrix.
  Instead it's wired as its own `paths:`-filtered GitHub Actions workflow keyed
  to the Legacy Plus task/vars files (mirroring the existing per-role
  `paths:`-filtered workflows under `.github/workflows/`), so it only runs when
  the Legacy Plus flow itself changes.

## Consequences

- **New/changed layout.** `s1_agent_common` gains `s1_os_bitness` +
  `s1_windows_tier` (and the `s1_legacy_plus_x64_editions` matrix in
  `vars/windows.yml`). `s1_agent_install` and `s1_agent_upgrade` gain three
  `include_tasks` tier routes, rename `tasks/windows.yml` → `tasks/windows_64-bit.yml`
  (Modern flow, no version guard), and add `tasks/windows_legacy_plus.yml`
  (frozen 23.4 flow, `< 24.1` ceiling guard). The read-only roles are untouched
  so they do not hard-fail merely gathering against an old box.
- **32-bit is Legacy Plus by short-circuit.** Any supported 32-bit Windows (Win10
  32-bit, 8.1 32-bit, …) routes to the frozen flow with no Caption check; an
  unsupported old 32-bit box fails naturally at install rather than being blocked
  up front, consistent with ADR 0002's no-gate stance.
- **A 32-bit host that is `NT < 6.1` is Legacy, not Legacy Plus** — the tier
  ternary decides the floor before the bitness branch, so 32-bit XP routes to
  `unsupported.yml`.
- **POSReady 7 is not detected on 64-bit.** Its exact Caption could not be
  verified against a real host, so it is deliberately omitted from the matrix.
  32-bit POSReady 7 still routes correctly (bitness short-circuit); 64-bit
  POSReady 7 reads as Modern and fails naturally. Solve only if a customer
  reports it.
- **Testing needs fact-mocking, plus two real-fact fixtures.** The only Windows
  molecule preset is Server 2022 (Modern). Legacy Plus / Legacy paths are
  exercised by overriding `ansible_distribution` / `ansible_distribution_version`
  / `s1_os_bitness` via `set_fact`. The `not_match: "2012 R2"` exclusion clause
  is additionally verified against real facts by reviving the retired
  `jborean93/WindowsServer2012R2` Vagrant box as a classifier-only fixture
  (asserts `s1_windows_tier == 'modern'`, installs nothing) — gated to its own
  `paths:`-filtered CI workflow so it only runs when the Legacy Plus flow
  changes, not part of the default `scripts/gate.yml` matrix. Standing this box
  up is deferred to the `/tdd` build; if it proves impractical, it may need its
  own testing path rather than blocking the rest of the work.
- **A second real-fact fixture proves genuine Legacy Plus, not just its 2012
  R2 exclusion.** `jborean93/WindowsServer2012` (non-R2) genuinely qualifies
  for Legacy Plus, unlike the 2012 R2 box above. `extensions/molecule/windows-legacy-plus`
  installs an explicit, older 23.4.x release, then runs `s1_agent_upgrade`
  with **no** `s1_agent_version` requested — asserting both that the real
  host classifies as `legacy_plus` and that the issue 03 default-version pin
  resolves and completes the frozen upgrade flow end-to-end, against a real
  host rather than a fact-mocked one. Unlike the 2012 R2 fixture this one
  does install (a deliberate, maintainer-approved exception to that fixture's
  install-nothing precedent — the goal here is to vet the frozen flow itself,
  not just classification). Unlike the 2012 R2 fixture, this one **is** in
  `scripts/gate.yml` (maintainer call: it needs to be runnable as part of
  pre-release validation, not only on demand) on top of its own
  `paths:`-filtered CI workflow, which still runs it per-PR/per-push scoped
  to Legacy Plus file changes. This box ships Win32-OpenSSH pre-installed and
  auto-started (unlike 2012 R2's broken OpenSSH path), so it connects over
  `ssh` with password auth (requires `sshpass` on the controller) like the
  Server 2022 preset rather than forcing `winrm`.
