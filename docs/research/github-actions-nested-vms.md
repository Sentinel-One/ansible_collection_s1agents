# Nested VMs on GitHub-hosted Actions runners (public repo)

Research question: Can we run Molecule with the Vagrant driver (VirtualBox or
libvirt/KVM) inside a **GitHub-hosted** runner (not self-hosted) for a **public**
repository?

- **Scope:** `sentinelone.s1agents` Ansible collection; Molecule + Vagrant driver
  against Linux (Rocky, Ubuntu, openSUSE) and Windows guest VMs.
- **Research date:** 2026-07-24. Everything below is version/date-sensitive —
  runner-image and GitHub-platform behaviour changes frequently. Source dates are
  called out inline.

---

## Bottom line / recommendation

- **Yes, it is technically possible on GitHub-hosted Linux runners — but use
  KVM/libvirt, not VirtualBox.** GitHub-hosted Ubuntu runners now expose
  hardware-accelerated nested virtualization via `/dev/kvm`, including on the
  **standard free 4-vCPU runners** used for public repos. This is confirmed by
  GitHub's own Android-emulator changelog (2 April 2024), which documents the
  exact `udev` rule to unlock `/dev/kvm` on 2-vCPU runners.
- **VirtualBox is the wrong horse.** It is **not** pre-installed on current
  Ubuntu 22.04/24.04 runner images, and GitHub's own image-build pipeline for
  VirtualBox has been broken on the hosted fleet since ~18 Sept 2024 (VMs land in
  a "gurumeditation" fault state), which the maintainers attribute to a
  kernel/hypervisor change on the runner. VirtualBox needs its own VT-x access and
  historically ran degraded/software-only on these runners.
- **KVM/libvirt is the supported, hardware-accelerated path.** Install
  `qemu-kvm libvirt-daemon-system`, apply the `kvm` `udev` rule, and use the
  Vagrant **`vagrant-libvirt`** provider instead of VirtualBox. None of this
  tooling is pre-installed — you install it in the job.
- **Cost is a non-issue for a public repo.** Standard GitHub-hosted runners are
  **free and unlimited** on public repositories (no minute cap). Nested virt works
  on the free standard 4-vCPU/16 GB runner, so you do **not** need paid larger
  runners. Note the standard runner has only ~14 GB SSD — disk, not CPU, is the
  likely constraint when spinning up multiple guest VMs.
- **Licensing is clear for KVM/Vagrant, murky-but-fine for VirtualBox base.**
  KVM/QEMU/libvirt are GPL — no concern. Vagrant is BSL 1.1; internal CI/testing
  use is explicitly permitted (only reselling a competing hosted/embedded Vagrant
  offering is barred). VirtualBox's *base* package is GPLv3 (fine); only the
  proprietary **Extension Pack (PUEL)** is a commercial-licensing trap — another
  reason to avoid VirtualBox entirely.
- **One caveat:** GitHub does **not** contractually "support" nested
  virtualization on standard Linux runners as a documented product feature — it
  works in practice and is exercised by GitHub's own Android tooling, but is not a
  guaranteed SLA. A closed 2025 documentation request (#12933) asked GitHub to
  document this and it remains undocumented in the formal runner reference.

---

## 1. Nested virtualization support on GitHub-hosted runners

### Standard Linux runners now expose `/dev/kvm` with hardware acceleration

The clearest primary evidence is GitHub's own changelog for the Android emulator,
which relies on KVM acceleration:

> "GitHub Actions users of 2 vCPU GitHub-hosted Linux runners can now make use of
> hardware acceleration ... Previously, this feature was only available on runners
> with 4 or more vCPUs."
> — GitHub Changelog, **2 April 2024**
> (https://github.blog/changelog/2024-04-02-github-actions-hardware-accelerated-android-virtualization-now-available/)

That same changelog gives the exact step required to access `/dev/kvm`:

```bash
echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' \
  | sudo tee /etc/udev/rules.d/99-kvm4all.rules
sudo udevadm control --reload-rules
sudo udevadm trigger --name-match=kvm
```

Source: same changelog URL above.

The earlier February 2023 changelog shows hardware-accelerated Android
virtualization first arriving on **larger** Linux/Windows runners, before the 2024
extension to the standard 2-vCPU size:
https://github.blog/changelog/2023-02-23-hardware-accelerated-android-virtualization-on-actions-windows-and-linux-larger-hosted-runners/

Community confirmation (secondary, but consistent with the changelog) in GitHub's
own community discussion "Revisiting KVM support for Hosted GitHub Actions" notes
that as of an **October 2025** comment, "KVM virtualization seems to work just
adding the udev rule now," i.e. `/dev/kvm` is present on standard Linux runners:
https://github.com/orgs/community/discussions/8305

### Which OS images / where does it work?

- **Ubuntu Linux (ubuntu-latest / ubuntu-22.04 / ubuntu-24.04):** `/dev/kvm`
  available; hardware-accelerated nested virt works after applying the `udev`
  rule. This is the recommended target. (Changelog above; discussion #8305.)
- **Windows runners:** Larger Windows runners received hardware-accelerated
  Android virtualization (Feb 2023 changelog), but for full nested VMs Linux/KVM
  is the mainstream path; Windows nested virt is not the practical route for
  Vagrant/Molecule here.
- **macOS runners:** Hardware-accelerated virtualization works on Intel/standard
  macOS runners, but the official runner reference states nested virtualization is
  **not** supported on Apple-silicon (arm64) macOS "due to the limitation of
  Apple's Virtualization Framework."
  (https://docs.github.com/en/actions/reference/runners/github-hosted-runners)

### The `kvm` group / permissions caveat

By default the `runner` user is **not** a member of the `kvm` group on the hosted
images, so direct `/dev/kvm` access needs either the `udev` rule above (sets the
device world-accessible) or `sudo`. This was raised in runner-images issue #8542
("runner user is not in the kvm group"), which covers Ubuntu 20.04/22.04 (issue
now closed): https://github.com/actions/runner-images/issues/8542

The community feature request to pre-install `qemu-kvm` (issue #7541, opened
5 May 2023) shows the tooling is expected to be installed per-job, not baked into
the image: https://github.com/actions/runner-images/issues/7541

### VirtualBox specifically — avoid

- **Not pre-installed.** VirtualBox does **not** appear in the pre-installed
  software lists for the current Ubuntu 24.04 or Ubuntu 22.04 runner images (nor
  do Vagrant, QEMU, KVM, or libvirt):
  - https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md
  - https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2204-Readme.md
  (Historically older images shipped VirtualBox + Vagrant for GitHub's own image
  builds; current images do not list them.)
- **GitHub's own VirtualBox builds are broken on the hosted fleet.**
  runner-images issue #10678 ("Virtualbox builds failing on latest update")
  reports that from ~**18 September 2024**, VirtualBox VMs across Ubuntu
  20.04/22.04/24.04 (and macOS/Windows) enter an invalid "gurumeditation" state on
  boot, which the reporter attributes to "the kernel and/or hypervisor
  configuration in the GitHub Actions runner itself." This affects VirtualBox +
  Vagrant + Packer flows: https://github.com/actions/runner-images/issues/10678
- **Why:** VirtualBox uses its own hypervisor and needs VT-x exposed to the
  runner's guest; on the hosted runners it has historically been unreliable or
  software-emulated (slow). The nested-virt capability GitHub actually exposes and
  exercises is **KVM**, not VirtualBox's hypervisor.

### KVM/libvirt — supported and preferred

KVM is the acceleration path GitHub itself uses (Android emulator) and the one the
community reports working on standard runners after the `udev` rule. It is the
recommended backend. Pair it with the Vagrant `libvirt` provider.

---

## 2. Install process (KVM/libvirt + Vagrant) in a workflow

Nothing in this stack is pre-installed on the runner, so the job installs it.
Concrete, primary-source-derived snippet for an Ubuntu runner:

```yaml
jobs:
  molecule:
    runs-on: ubuntu-24.04      # standard, free for public repos
    steps:
      - uses: actions/checkout@v4

      # 1. Unlock /dev/kvm (from GitHub's own Android changelog, 2024-04-02)
      - name: Enable KVM access
        run: |
          echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' \
            | sudo tee /etc/udev/rules.d/99-kvm4all.rules
          sudo udevadm control --reload-rules
          sudo udevadm trigger --name-match=kvm

      # 2. Install KVM/libvirt + Vagrant + the libvirt provider
      - name: Install virtualization stack
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            qemu-kvm libvirt-daemon-system libvirt-dev \
            ebtables dnsmasq-base vagrant
          sudo usermod -aG kvm,libvirt "$USER"
          vagrant plugin install vagrant-libvirt

      - name: Verify KVM
        run: |
          ls -l /dev/kvm
          kvm-ok || true      # from cpu-checker; expects hardware acceleration

      # 3. Run Molecule with the Vagrant (libvirt) driver
      - name: Molecule test
        run: .venv/bin/python scripts/molecule.py gate
```

Notes / sources:
- The `udev` rule is verbatim from GitHub's changelog
  (https://github.blog/changelog/2024-04-02-github-actions-hardware-accelerated-android-virtualization-now-available/).
- `qemu-kvm`/`libvirt` are the packages requested in runner-images issue #7541
  (https://github.com/actions/runner-images/issues/7541); they are not
  pre-installed per the Ubuntu readmes cited in §1.
- The `kvm`-group workaround corresponds to runner-images issue #8542
  (https://github.com/actions/runner-images/issues/8542).
- **This project uses Vagrant boxes that are VirtualBox-format
  (`roboxes`, `gusztavvargadr`).** Moving to GitHub-hosted runners means switching
  to `vagrant-libvirt` and using **libvirt-format boxes** for each platform, or
  converting boxes — a real migration cost, not a drop-in. Molecule's own driver
  config (`extensions/molecule/*/molecule.yml`) and the Vagrantfile provider block
  would need a libvirt path.
- The `ubuntu-slim` runner variant runs Docker-in-unprivileged-container mode and
  explicitly does **not** support "mounting file systems ... or accessing
  low-level kernel features" — do not target `ubuntu-slim` for KVM; use the full
  `ubuntu-24.04`/`ubuntu-22.04` image
  (https://docs.github.com/en/actions/reference/runners/github-hosted-runners).

---

## 3. Runner sizes

Standard GitHub-hosted runner specs (from the official runner reference,
https://docs.github.com/en/actions/reference/runners/github-hosted-runners):

| Runner | Public repo | Private repo | Disk |
| --- | --- | --- | --- |
| ubuntu-latest / 22.04 / 24.04 (x64) | 4 vCPU / 16 GB | 2 vCPU / 8 GB | 14 GB SSD |
| windows-latest / 2022 / 2025 (x64) | 4 vCPU / 16 GB | 2 vCPU / 8 GB | 14 GB SSD |
| macOS (Intel) | 4 vCPU / 14 GB | same | 14 GB SSD |
| macOS (arm64/M1) | 3 vCPU / 7 GB | same | 14 GB SSD |

The public-repo doubling to 4 vCPU / 16 GB was announced in "GitHub-hosted
runners: Double the power for open source" (**17 Jan 2024**, rollout from
1 Dec 2023):
https://github.blog/news-insights/product-news/github-hosted-runners-double-the-power-for-open-source/

**Does nested virt need a larger runner?** No. Hardware-accelerated KVM was
extended to the standard 2-vCPU runners in April 2024 (changelog in §1), and the
public standard runner is 4 vCPU — so nested virt works on the **free standard
runner**. Larger runners (up to 64+ vCPU, listed at
https://docs.github.com/en/actions/reference/runners/larger-runners) give more
CPU/RAM/disk headroom but are **not required** for KVM to function.

**The real constraint is disk, not CPU/nested-virt capability.** The standard
runner offers only ~14 GB of SSD. Downloading agent packages plus booting one or
more full guest VMs (Rocky/Ubuntu/openSUSE/Windows) can exhaust that quickly;
Windows guests especially are large. Larger runners primarily help here by
offering more disk/RAM.

---

## 4. Costs & licensing

### Cost — public repository

- **Standard GitHub-hosted runners are free and unlimited on public repos.** The
  runner reference states plainly: "Use of the standard GitHub-hosted runners is
  free and unlimited on public repositories."
  (https://docs.github.com/en/actions/reference/runners/github-hosted-runners).
  The billing docs confirm standard runners incur no charge for public repos
  (https://docs.github.com/en/billing/concepts/product-billing/github-actions).
- **Larger runners are NOT free for public repos** — they are billed per-minute
  and require a Team/Enterprise plan
  (https://docs.github.com/en/actions/reference/runners/larger-runners,
  https://docs.github.com/en/billing/reference/actions-runner-pricing). Since the
  free standard runner supports KVM, there is no need to pay for larger runners
  unless disk/RAM forces it.
- Concurrency: public-repo jobs still run under GitHub's standard concurrency
  limits for the account tier, but there is no minute-consumption cost.

### Licensing

- **KVM / QEMU / libvirt — GPL, no concern.** Standard open-source Linux
  virtualization stack; free for any use including CI.
- **Vagrant — BSL 1.1, CI use permitted.** HashiCorp relicensed Vagrant from
  MPL 2.0 to the Business Source License 1.1 in Aug 2023
  (https://www.hashicorp.com/en/blog/hashicorp-adopts-business-source-license,
  https://github.com/hashicorp/vagrant/blob/main/LICENSE). The BSL restricts only
  offering a **competitive** hosted/embedded Vagrant product to third parties;
  internal use, testing, and CI/CD provisioning are allowed
  (https://www.hashicorp.com/en/license-faq, https://www.hashicorp.com/en/bsl).
  Running Vagrant in this project's Molecule CI is squarely permitted.
- **VirtualBox — split license (another reason to avoid it):**
  - The **base package** is **GPLv3** — free, no concern
    (https://www.virtualbox.org/wiki/Licensing_FAQ).
  - The **Extension Pack** is under the proprietary **PUEL**: free only for
    personal/educational use; commercial use requires a paid Oracle license, and
    the former 30-day trial has been discontinued
    (https://www.virtualbox.org/wiki/VirtualBox_PUEL,
    https://www.virtualbox.org/wiki/Licensing_FAQ). CI for a corporate-owned
    public repo would be "commercial" use. The Extension Pack provides features
    like USB 2.0/3.0, RDP, disk encryption; plain VirtualBox VMs generally don't
    need it, but this is a licensing minefield best sidestepped by using KVM.

---

## Sources (primary)

- GitHub Docs — GitHub-hosted runners reference (specs, free-for-public,
  macOS nested-virt limitation, ubuntu-slim limits):
  https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- GitHub Docs — Larger runners reference:
  https://docs.github.com/en/actions/reference/runners/larger-runners
- GitHub Docs — Actions runner pricing / billing:
  https://docs.github.com/en/billing/reference/actions-runner-pricing ,
  https://docs.github.com/en/billing/concepts/product-billing/github-actions
- GitHub Changelog — Hardware-accelerated Android virtualization on 2-vCPU
  runners (2024-04-02, the `udev`/`/dev/kvm` rule):
  https://github.blog/changelog/2024-04-02-github-actions-hardware-accelerated-android-virtualization-now-available/
- GitHub Changelog — Hardware-accelerated Android virtualization on larger
  runners (2023-02-23):
  https://github.blog/changelog/2023-02-23-hardware-accelerated-android-virtualization-on-actions-windows-and-linux-larger-hosted-runners/
- GitHub Blog — "Double the power for open source" (free 4-vCPU public runners,
  2024-01-17):
  https://github.blog/news-insights/product-news/github-hosted-runners-double-the-power-for-open-source/
- actions/runner-images #7541 — Add qemu-kvm to Ubuntu runners:
  https://github.com/actions/runner-images/issues/7541
- actions/runner-images #8542 — runner user not in kvm group:
  https://github.com/actions/runner-images/issues/8542
- actions/runner-images #10678 — VirtualBox builds failing (gurumeditation):
  https://github.com/actions/runner-images/issues/10678
- actions/runner-images #12933 — Documentation request: nested virt (closed,
  undocumented): https://github.com/actions/runner-images/issues/12933
- Ubuntu 24.04 / 22.04 pre-installed software (no VirtualBox/Vagrant/KVM):
  https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md ,
  https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2204-Readme.md
- community/discussions #8305 — Revisiting KVM support (Oct 2025 "udev rule works"
  report): https://github.com/orgs/community/discussions/8305
- HashiCorp — BSL adoption blog, license FAQ, BSL text; Vagrant LICENSE:
  https://www.hashicorp.com/en/blog/hashicorp-adopts-business-source-license ,
  https://www.hashicorp.com/en/license-faq , https://www.hashicorp.com/en/bsl ,
  https://github.com/hashicorp/vagrant/blob/main/LICENSE
- Oracle VirtualBox — Licensing FAQ, PUEL:
  https://www.virtualbox.org/wiki/Licensing_FAQ ,
  https://www.virtualbox.org/wiki/VirtualBox_PUEL
