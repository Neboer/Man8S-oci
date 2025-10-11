.PHONY: install uninstall install-man8libs install-man8utils install-systemd-netconf install-python \
	uninstall-man8libs uninstall-man8utils uninstall-systemd-netconf uninstall-python

MAN8LIBS = man8lib
MAN8UTILS_DIR = man8utils
INSTALL_BIN_DIR = /usr/bin/
INSTALL_LIB_DIR = /usr/lib/

install: install-man8libs install-man8utils install-systemd-netconf install-python

uninstall: uninstall-man8libs uninstall-man8utils uninstall-systemd-netconf uninstall-python

install-man8libs:
	cp --preserve=mode -r $(MAN8LIBS) $(INSTALL_LIB_DIR)

uninstall-man8libs:
	rm -rf $(INSTALL_LIB_DIR)$(MAN8LIBS)

install-man8utils:
	cp --preserve=mode $(MAN8UTILS_DIR)/* $(INSTALL_BIN_DIR)

uninstall-man8utils:
	for f in $(MAN8UTILS_DIR)/*; do rm -f $(INSTALL_BIN_DIR)$$(basename $$f); done

install-systemd-netconf:
	cp systemd-configs/80-srvgrp0.network /etc/systemd/network/80-srvgrp0.network
	cp systemd-configs/80-srvgrp0.netdev /etc/systemd/network/80-srvgrp0.netdev

uninstall-systemd-netconf:
	rm -f /etc/systemd/network/80-srvgrp0.network
	rm -f /etc/systemd/network/80-srvgrp0.netdev

install-python:
	cd mbctl-python-module && pip install . --break-system-packages

uninstall-python:
	pip uninstall -y mbctl
