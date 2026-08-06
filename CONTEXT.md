# sentinelone.s1agents

Ansible collection that manages the full lifecycle of the SentinelOne agent on
Linux and Windows endpoints, interacting with both the endpoints and the
SentinelOne Management Console API.

## Language

### Agent lifecycle

**End of Support (EOS)**: Lifecycle phase 9–15 months after an agent version's
release, during which the version still receives limited support. Per the
SentinelOne agent lifecycle (GA 0–9 months, EOS 9–15 months, EOL 15+ months).

**End of Life (EOL)**: Lifecycle phase 15+ months after release. The collection
no longer supports _installing_ versions that have been EOL for more than a
year, though _upgrading from_ an EOL version remains supported. _Avoid_:
deprecated, unsupported (too vague — name the phase).

**EOL accommodation**: A code path whose only reason to exist is to make an EOL
agent version work (e.g. `--nodigest`, which exists solely for pre-23.3 unsigned
RPMs that carry no header digest). The collection removes such accommodations
rather than adding gates that block EOL versions — see
[ADR 0002](./docs/adr/0002-remove-eol-accommodations-not-gate.md).

### Windows support tiers

**Windows support tier** (`s1_windows_tier`): The single classification fact —
`legacy` | `legacy_plus` | `modern` — computed once per Windows host in
`s1_agent_common` and used to route install/upgrade. Precedence is encoded in
its resolution order: the Legacy floor is decided first, then Legacy Plus, then
Modern. See [ADR 0008](./docs/adr/0008-windows-support-tier-routing.md).

**Legacy Plus**: The SentinelOne category of older Windows OSes on which Agent
23.4 remains the last supported version even though 23.4 is End of Life on every
other Windows platform — Windows 10 32-bit, Windows 8.1 32-bit, Windows 8,
Windows 7 SP1, POSReady 7, Server / Storage Server 2012 (non-R2), and Server
2008 R2 SP1. The set is not a version range (it spans NT 6.1 / 6.2 / 6.3 / 10.0
with the 64-bit 6.3/10.0 siblings excluded), so it is matched by OS bitness +
`ansible_distribution` (Caption) substrings, not a numeric key. Routed to a
role-local, intentionally-duplicated `windows_legacy_plus.yml` that freezes the
23.4 install flow and asserts `s1_agent_version < 24.1`. When no
`s1_agent_version` is requested, `s1_agent_common` pins one to a
manually-maintained constant (`s1_legacy_plus_default_version`,
`vars/windows.yml`) before `s1_agent_download` runs, so the download fallback
never fetches a too-new GA release that would fail the ceiling assert. _Avoid_:
letting `s1_agent_download`'s `release_n_minus` fallback run unpinned on a
Legacy Plus host.

One real-fact molecule fixture exists alongside the fact-mocked
`windows-tier-matrix` cases, gated to its own `paths:`-filtered CI workflow
rather than the default `scripts/gate.yml`: `extensions/molecule/windows-legacy-plus`
(a real `s1_agent_upgrade` run against genuinely-Legacy-Plus
`jborean93/WindowsServer2012` — proves the frozen flow and the default-version
pin end-to-end, not fact-mocked). The `not_match: "2012 R2"` exclusion was
previously proven by a real-guest classifier-only fixture; that guest is
retired and the exclusion is now a captured-fact case in `windows-tier-matrix`
instead.

**Legacy**: The older tier below Legacy Plus — Windows XP, Vista, POSReady 2009,
Server 2003, Server 2008 non-R2 (NT `< 6.1`) — which requires a separate
SentinelOne installer this collection does not manage. Install/upgrade route
these to `unsupported.yml` (fail-loud). _Avoid_: conflating with Legacy Plus
(different installer, no accommodation).

**Modern**: 64-bit Windows that is neither Legacy nor Legacy Plus. Reached via
the normal `with_first_found` dispatch (candidate `windows_<bitness>.yml`) and
carries **no agent-version assertion** — per [ADR
0002](./docs/adr/0002-remove-eol-accommodations-not-gate.md), EOL versions
(e.g. 23.1–23.4.x) still install/upgrade here exactly as they do today; only
Legacy Plus's ceiling is a genuine technical constraint worth gating.

**Normalized OS bitness** (`s1_os_bitness`): A collection-owned `64-bit` /
`32-bit` token derived in `s1_agent_common` from
`[Environment]::Is64BitOperatingSystem`. Used instead of `ansible_architecture`
because the latter maps to `Win32_OperatingSystem.OSArchitecture`, which is
_localized_ (`64 bits` on French, `64-Bit` on German) and so unsafe as a
filename or comparison key. _Avoid_: `ansible_architecture` for Windows routing.

### Install paths (Linux)

**Unsigned RPM branch**: The default Linux RPM install path (`rpm` command,
`s1_install_gpg_signed_rpm: false`). Integrity rests on TLS-from-console +
download checksum + the rpm header/payload digest.

**GPG-signed branch**: The opt-in Linux RPM install path (`yum`,
`s1_install_gpg_signed_rpm: true`) with full GPG signature verification. The
recommended path for versions that ship signed RPMs.

### Secrets & tokens

**Site token** (`s1_agent_site_token`): Base64 registration token (decodes to
`site_key` + `url`) used to associate a newly installed agent with the
Management Console. _Avoid_: API token (different thing), license key.

**API token** (`s1_api_token`): Console REST API credential, sent as the
`Authorization: ApiToken …` header. Used to download packages and fetch
passphrases. Never placed on argv.

**Passphrase** (`s1_agent_passphrase`): Per-endpoint, console-issued secret
required to uninstall or upgrade a newer agent. Treated as a local secret that
must never reach a process command line — see
[ADR 0003](./docs/adr/0003-passphrase-off-argv.md).

### Deployment / trust contexts

**Trusted-CLI model**: The default Ansible deployment, where whoever sets a
variable (inventory, `group_vars`, `-e`) is the play author. Operator variables
are part of the trusted control plane, so "inject via host_var" crosses no
privilege boundary.

**AWX/survey model**: Deployment under AWX/AAP where lower-privileged users
supply variables via job-template surveys. Here the variable-setter is _not_ the
play author, so unvalidated operator inputs become a real hardening obligation
for this collection as a vendor — see
[ADR 0001](./docs/adr/0001-trust-model.md).

**Endpoint local-user boundary**: The one privilege boundary that is real
regardless of trust model: the play runs as `root`/`SYSTEM`, so secrets on argv
and predictable-path races cross a genuine boundary against an unprivileged
local user on the managed endpoint.

### Version selection

**Named release**: Install/upgrade to an explicit `s1_agent_version`.

**n-minus release** (`s1_release_n_minus`): Selection of "latest minus N" from
the console's GA package list when no version is named. Always resolves to
recent (non-EOL) packages.

**2-step upgrade**: A Linux upgrade from Agent version 22.2 or below requires
two upgrades — an intermediate hop (e.g. to 22.3) before the target version
(e.g. 21.7 → 22.3 → 23.3).

### Testing & environment

**Test harness**: `scripts/molecule.py` — the thin Python orchestrator over
molecule (run on the uv-managed `.venv`, see
[ADR 0007](./docs/adr/0007-uv-managed-venv-toolchain.md)) that provides one
stable, allowlistable command, file-based logs under `.molecule-logs/`, and a
compact summary. The single entry point for the agent, end users, and CI. See
[ADR 0005](./docs/adr/0005-molecule-test-harness.md).

**Proxy**: The corporate TLS-inspecting egress proxy between the controller and
the Management Console. When its auth token expires it resets inspected TLS
connections, surfacing as `SSL: UNEXPECTED_EOF` on console API calls — a
_transient infrastructure_ error, not a playbook failure. _Avoid_: naming the
specific vendor product in committed artifacts.

**Transient infrastructure error**: A non-deterministic environmental failure
(proxy TLS reset, SSH `Connection reset` during VM boot) distinct from a real
test failure. The test harness signals it with exit code `75`.
