
test: rhel-test rhel6-test ubuntu-test suse-test windows-test
.PHONY: test

clean: rhel-destroy rhel6-destroy ubuntu-destroy suse-destroy windows-destroy
.PHONY: clean

# Red Hat
rhel-test: rhel-default-test rhel-forced-remove-test
.PHONY: rhel-test

rhel-create: rhel-default-create rhel-forced-remove-create
.PHONY: rhel-create

rhel-prepare: rhel-default-prepare rhel-forced-remove-prepare
.PHONY: rhel-prepare

rhel-converge: rhel-default-converge rhel-forced-remove-converge
.PHONY: rhel-converge

rhel-verify: rhel-default-verify rhel-forced-remove-verify
.PHONY: rhel-verify

rhel-destroy: rhel-default-destroy rhel-forced-remove-destroy
.PHONY: rhel-destroy

rhel-default-test:
	S1_VAGRANT_DISTRO=rocky8 molecule test --scenario-name default

rhel-default-create:
	S1_VAGRANT_DISTRO=rocky8 molecule create --scenario-name default

rhel-default-prepare:
	S1_VAGRANT_DISTRO=rocky8 molecule prepare --scenario-name default

rhel-default-converge:
	S1_VAGRANT_DISTRO=rocky8 molecule converge --scenario-name default

rhel-default-verify:
	S1_VAGRANT_DISTRO=rocky8 molecule verify --scenario-name default

rhel-default-destroy:
	S1_VAGRANT_DISTRO=rocky8 molecule destroy --scenario-name default

rhel-forced-remove-test:
	S1_VAGRANT_DISTRO=rocky8 molecule test --scenario-name forced_remove

rhel-forced-remove-create:
	S1_VAGRANT_DISTRO=rocky8 molecule create --scenario-name forced_remove

rhel-forced-remove-prepare:
	S1_VAGRANT_DISTRO=rocky8 molecule prepare --force --scenario-name forced_remove

rhel-forced-remove-converge:
	S1_VAGRANT_DISTRO=rocky8 molecule converge --scenario-name forced_remove

rhel-forced-remove-verify:
	S1_VAGRANT_DISTRO=rocky8 molecule verify --scenario-name forced_remove

rhel-forced-remove-destroy:
	S1_VAGRANT_DISTRO=rocky8 molecule destroy --scenario-name forced_remove

# Legacy Red Hat
rhel6-test: rhel6-default-test rhel6-forced-remove-test
.PHONY: rhel6-test

rhel6-create: rhel6-default-create rhel6-forced-remove-create
.PHONY: rhel6-create

rhel6-prepare: rhel6-default-prepare rhel6-forced-remove-prepare
.PHONY: rhel6-prepare

rhel6-converge: rhel6-default-converge rhel6-forced-remove-converge
.PHONY: rhel6-converge

rhel6-verify: rhel6-default-verify rhel6-forced-remove-verify
.PHONY: rhel6-verify

rhel6-destroy: rhel6-default-destroy rhel6-forced-remove-destroy
.PHONY: rhel6-destroy

rhel6-default-test:
	S1_VAGRANT_DISTRO=centos6 molecule test --scenario-name default

rhel6-default-create:
	S1_VAGRANT_DISTRO=centos6 molecule create --scenario-name default

rhel6-default-prepare:
	S1_VAGRANT_DISTRO=centos6 molecule prepare --scenario-name default

rhel6-default-converge:
	S1_VAGRANT_DISTRO=centos6 molecule converge --scenario-name default

rhel6-default-verify:
	S1_VAGRANT_DISTRO=centos6 molecule verify --scenario-name default

rhel6-default-destroy:
	S1_VAGRANT_DISTRO=centos6 molecule destroy --scenario-name default

rhel6-forced-remove-test:
	S1_VAGRANT_DISTRO=centos6 molecule test --scenario-name forced_remove

rhel6-forced-remove-create:
	S1_VAGRANT_DISTRO=centos6 molecule create --scenario-name forced_remove

rhel6-forced-remove-prepare:
	S1_VAGRANT_DISTRO=centos6 molecule prepare --force --scenario-name forced_remove

rhel6-forced-remove-converge:
	S1_VAGRANT_DISTRO=centos6 molecule converge --scenario-name forced_remove

rhel6-forced-remove-verify:
	S1_VAGRANT_DISTRO=centos6 molecule verify --scenario-name forced_remove

rhel6-forced-remove-destroy:
	S1_VAGRANT_DISTRO=centos6 molecule destroy --scenario-name forced_remove

# Ubuntu 22.04 LTS
ubuntu-test: ubuntu-default-test ubuntu-forced-remove-test
.PHONY: ubuntu-test

ubuntu-create: ubuntu-default-create ubuntu-forced-remove-create
.PHONY: ubuntu-create

ubuntu-prepare: ubuntu-default-prepare ubuntu-forced-remove-prepare
.PHONY: ubuntu-prepare

ubuntu-converge: ubuntu-default-converge ubuntu-forced-remove-converge
.PHONY: ubuntu-converge

ubuntu-verify: ubuntu-default-verify ubuntu-forced-remove-verify
.PHONY: ubuntu-verify

ubuntu-destroy: ubuntu-default-destroy ubuntu-forced-remove-destroy
.PHONY: ubuntu-destroy

ubuntu-default-test:
	S1_VAGRANT_DISTRO=ubuntu2204 molecule test --scenario-name default

ubuntu-default-create:
	S1_VAGRANT_DISTRO=ubuntu2204 molecule create --scenario-name default

ubuntu-default-prepare:
	S1_VAGRANT_DISTRO=ubuntu2204 molecule prepare --scenario-name default

ubuntu-default-converge:
	S1_VAGRANT_DISTRO=ubuntu2204 molecule converge --scenario-name default

ubuntu-default-verify:
	S1_VAGRANT_DISTRO=ubuntu2204 molecule verify --scenario-name default

ubuntu-default-destroy:
	S1_VAGRANT_DISTRO=ubuntu2204 molecule destroy --scenario-name default

ubuntu-forced-remove-test:
	S1_VAGRANT_DISTRO=ubuntu2204 molecule test --scenario-name forced_remove

ubuntu-forced-remove-create:
	S1_VAGRANT_DISTRO=ubuntu2204 molecule create --scenario-name forced_remove

ubuntu-forced-remove-prepare:
	S1_VAGRANT_DISTRO=ubuntu2204 molecule prepare --force --scenario-name forced_remove

ubuntu-forced-remove-converge:
	S1_VAGRANT_DISTRO=ubuntu2204 molecule converge --scenario-name forced_remove

ubuntu-forced-remove-verify:
	S1_VAGRANT_DISTRO=ubuntu2204 molecule verify --scenario-name forced_remove

ubuntu-forced-remove-destroy:
	S1_VAGRANT_DISTRO=ubuntu2204 molecule destroy --scenario-name forced_remove

# Open SUSE 15
suse-test: suse-default-test suse-forced-remove-test
.PHONY: suse-test

suse-create: suse-default-create suse-forced-remove-create
.PHONY: suse-create

suse-prepare: suse-default-prepare suse-forced-remove-prepare
.PHONY: suse-prepare

suse-converge: suse-default-converge suse-forced-remove-converge
.PHONY: suse-converge

suse-verify: suse-default-verify suse-forced-remove-verify
.PHONY: suse-verify

suse-destroy: suse-default-destroy suse-forced-remove-destroy
.PHONY: suse-destroy

suse-default-test:
	S1_VAGRANT_DISTRO=opensuse15 molecule test --scenario-name default

suse-default-create:
	S1_VAGRANT_DISTRO=opensuse15 molecule create --scenario-name default

suse-default-prepare:
	S1_VAGRANT_DISTRO=opensuse15 molecule prepare --scenario-name default

suse-default-converge:
	S1_VAGRANT_DISTRO=opensuse15 molecule converge --scenario-name default

suse-default-verify:
	S1_VAGRANT_DISTRO=opensuse15 molecule verify --scenario-name default

suse-default-destroy:
	S1_VAGRANT_DISTRO=opensuse15 molecule destroy --scenario-name default

suse-forced-remove-test:
	S1_VAGRANT_DISTRO=opensuse15 molecule test --scenario-name forced_remove

suse-forced-remove-create:
	S1_VAGRANT_DISTRO=opensuse15 molecule create --scenario-name forced_remove

suse-forced-remove-prepare:
	S1_VAGRANT_DISTRO=opensuse15 molecule prepare --force --scenario-name forced_remove

suse-forced-remove-converge:
	S1_VAGRANT_DISTRO=opensuse15 molecule converge --scenario-name forced_remove

suse-forced-remove-verify:
	S1_VAGRANT_DISTRO=opensuse15 molecule verify --scenario-name forced_remove

suse-forced-remove-destroy:
	S1_VAGRANT_DISTRO=opensuse15 molecule destroy --scenario-name forced_remove

# Windows Server 2022
srv2022-test: srv2022-default-test srv2022-forced-remove-test
.PHONY: srv2022-test

srv2022-create: srv2022-default-create srv2022-forced-remove-create
.PHONY: srv2022-create

srv2022-prepare: srv2022-default-prepare srv2022-forced-remove-prepare
.PHONY: srv2022-prepare

srv2022-converge: srv2022-default-converge srv2022-forced-remove-converge
.PHONY: srv2022-converge

srv2022-verify: srv2022-default-verify srv2022-forced-remove-verify
.PHONY: srv2022-verify

srv2022-destroy: srv2022-default-destroy srv2022-forced-remove-destroy
.PHONY: srv2022-destroy

srv2022-default-test:
	S1_VAGRANT_DISTRO=windows-server-2022-standard S1_VAGRANT_REPO=gusztavvargadr S1_VAGRANT_GROUP=Windows OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule test --scenario-name winrm_default

srv2022-default-create:
	S1_VAGRANT_DISTRO=windows-server-2022-standard S1_VAGRANT_REPO=gusztavvargadr S1_VAGRANT_GROUP=Windows OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule create --scenario-name winrm_default

srv2022-default-prepare:
	S1_VAGRANT_DISTRO=windows-server-2022-standard S1_VAGRANT_REPO=gusztavvargadr S1_VAGRANT_GROUP=Windows OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule prepare --scenario-name winrm_default

srv2022-default-converge:
	S1_VAGRANT_DISTRO=windows-server-2022-standard S1_VAGRANT_REPO=gusztavvargadr S1_VAGRANT_GROUP=Windows OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule converge --scenario-name winrm_default

srv2022-default-verify:
	S1_VAGRANT_DISTRO=windows-server-2022-standard S1_VAGRANT_REPO=gusztavvargadr S1_VAGRANT_GROUP=Windows OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule verify --scenario-name winrm_default

srv2022-default-destroy:
	S1_VAGRANT_DISTRO=windows-server-2022-standard S1_VAGRANT_REPO=gusztavvargadr S1_VAGRANT_GROUP=Windows OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule destroy --scenario-name winrm_default

srv2022-forced-remove-test:
	S1_VAGRANT_DISTRO=windows-server-2022-standard S1_VAGRANT_REPO=gusztavvargadr S1_VAGRANT_GROUP=Windows OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule test --scenario-name winrm_forced_remove

srv2022-forced-remove-create:
	S1_VAGRANT_DISTRO=windows-server-2022-standard S1_VAGRANT_REPO=gusztavvargadr S1_VAGRANT_GROUP=Windows OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule create --scenario-name winrm_forced_remove

srv2022-forced-remove-prepare:
	S1_VAGRANT_DISTRO=windows-server-2022-standard S1_VAGRANT_REPO=gusztavvargadr S1_VAGRANT_GROUP=Windows OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule prepare --scenario-name winrm_forced_remove

srv2022-forced-remove-converge:
	S1_VAGRANT_DISTRO=windows-server-2022-standard S1_VAGRANT_REPO=gusztavvargadr S1_VAGRANT_GROUP=Windows OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule converge --scenario-name winrm_forced_remove

srv2022-forced-remove-verify:
	S1_VAGRANT_DISTRO=windows-server-2022-standard S1_VAGRANT_REPO=gusztavvargadr S1_VAGRANT_GROUP=Windows OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule verify --scenario-name winrm_forced_remove

srv2022-forced-remove-destroy:
	S1_VAGRANT_DISTRO=windows-server-2022-standard S1_VAGRANT_REPO=gusztavvargadr S1_VAGRANT_GROUP=Windows OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule destroy --scenario-name winrm_forced_remove

# Windows Server 2012r2
srv2012r2-test: srv2012r2-default-test srv2012r2-forced-remove-test
.PHONY: srv2012r2-test

srv2012r2-create: srv2012r2-default-create srv2012r2-forced-remove-create
.PHONY: srv2012r2-create

srv2012r2-prepare: srv2012r2-default-prepare srv2012r2-forced-remove-prepare
.PHONY: srv2012r2-prepare

srv2012r2-converge: srv2012r2-default-converge srv2012r2-forced-remove-converge
.PHONY: srv2012r2-converge

srv2012r2-verify: srv2012r2-default-verify srv2012r2-forced-remove-verify
.PHONY: srv2012r2-verify

srv2012r2-destroy: srv2012r2-default-destroy srv2012r2-forced-remove-destroy
.PHONY: srv2012r2-destroy

srv2012r2-default-test:
	S1_VAGRANT_DISTRO=WindowsServer2012R2 S1_VAGRANT_REPO=jborean93 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule test --scenario-name winrm_default

srv2012r2-default-create:
	S1_VAGRANT_DISTRO=WindowsServer2012R2 S1_VAGRANT_REPO=jborean93 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule create --scenario-name winrm_default

srv2012r2-default-prepare:
	S1_VAGRANT_DISTRO=WindowsServer2012R2 S1_VAGRANT_REPO=jborean93 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule prepare --scenario-name winrm_default

srv2012r2-default-converge:
	S1_VAGRANT_DISTRO=WindowsServer2012R2 S1_VAGRANT_REPO=jborean93 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule converge --scenario-name winrm_default

srv2012r2-default-verify:
	S1_VAGRANT_DISTRO=WindowsServer2012R2 S1_VAGRANT_REPO=jborean93 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule verify --scenario-name winrm_default

srv2012r2-default-destroy:
	S1_VAGRANT_DISTRO=WindowsServer2012R2 S1_VAGRANT_REPO=jborean93 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule destroy --scenario-name winrm_default

srv2012r2-forced-remove-test:
	S1_VAGRANT_DISTRO=WindowsServer2012R2 S1_VAGRANT_REPO=jborean93 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule test --scenario-name winrm_forced_remove

srv2012r2-forced-remove-create:
	S1_VAGRANT_DISTRO=WindowsServer2012R2 S1_VAGRANT_REPO=jborean93 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule create --scenario-name winrm_forced_remove

srv2012r2-forced-remove-prepare:
	S1_VAGRANT_DISTRO=WindowsServer2012R2 S1_VAGRANT_REPO=jborean93 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule prepare --scenario-name winrm_forced_remove

srv2012r2-forced-remove-converge:
	S1_VAGRANT_DISTRO=WindowsServer2012R2 S1_VAGRANT_REPO=jborean93 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule converge --scenario-name winrm_forced_remove

srv2012r2-forced-remove-verify:
	S1_VAGRANT_DISTRO=WindowsServer2012R2 S1_VAGRANT_REPO=jborean93 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule verify --scenario-name winrm_forced_remove

srv2012r2-forced-remove-destroy:
	S1_VAGRANT_DISTRO=WindowsServer2012R2 S1_VAGRANT_REPO=jborean93 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES molecule destroy --scenario-name winrm_forced_remove