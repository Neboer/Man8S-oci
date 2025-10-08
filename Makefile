.PHONY: install uninstall

MAN8LIBS = man8lib
MAN8UTILS_DIR = man8utils
INSTALL_BIN_DIR = /usr/bin/
INSTALL_LIB_DIR = /usr/lib/

install:
	cp -r $(MAN8LIBS) $(INSTALL_LIB_DIR)
	cp $(MAN8UTILS_DIR)/* $(INSTALL_BIN_DIR)
	cp systemd-configs/50-mbsrv0.network /etc/systemd/network/50-mbsrv0.network
	cp systemd-configs/50-mbsrv0.netdev /etc/systemd/network/50-mbsrv0.netdev
	cd mbctl && pip install .

uninstall:
	rm -rf $(INSTALL_LIB_DIR)$(MAN8LIBS)
	for f in $(MAN8UTILS_DIR)/*; do rm -f $(INSTALL_BIN_DIR)$$(basename $$f); done
	pip uninstall -y mbctl
