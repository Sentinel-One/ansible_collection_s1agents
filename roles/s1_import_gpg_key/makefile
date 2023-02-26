
test: rhel-test rhel6-test suse-test
.PHONY: test

clean: rhel-destroy rhel6-destroy suse-destroy
.PHONY: clean

# Red Hat
rhel-test: rhel-default-test
.PHONY: rhel-test

rhel-create: rhel-default-create
.PHONY: rhel-create

rhel-prepare: rhel-default-prepare
.PHONY: rhel-prepare

rhel-converge: rhel-default-converge
.PHONY: rhel-converge

rhel-verify: rhel-default-verify
.PHONY: rhel-verify

rhel-destroy: rhel-default-destroy
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

# Legacy Red Hat
rhel6-test: rhel6-default-test
.PHONY: rhel6-test

rhel6-create: rhel6-default-create
.PHONY: rhel6-create

rhel6-prepare: rhel6-default-prepare
.PHONY: rhel6-prepare

rhel6-converge: rhel6-default-converge
.PHONY: rhel6-converge

rhel6-verify: rhel6-default-verify
.PHONY: rhel6-verify

rhel6-destroy: rhel6-default-destroy
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

# Open SUSE 15
suse-test: suse-default-test
.PHONY: suse-test

suse-create: suse-default-create
.PHONY: suse-create

suse-prepare: suse-default-prepare
.PHONY: suse-prepare

suse-converge: suse-default-converge
.PHONY: suse-converge

suse-verify: suse-default-verify
.PHONY: suse-verify

suse-destroy: suse-default-destroy
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
