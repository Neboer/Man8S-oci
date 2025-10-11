.PHONY: install uninstall install-man8libs install-man8utils install-python \
	uninstall-man8libs uninstall-man8utils ununinstall-python

MAN8LIBS = man8lib
MAN8UTILS_DIR = man8utils
INSTALL_BIN_DIR = /usr/bin/
INSTALL_LIB_DIR = /usr/lib/

install: install-man8libs install-man8utils install-python

uninstall: uninstall-man8libs uninstall-man8utils ununinstall-python

install-man8libs:
	cp --preserve=mode -r $(MAN8LIBS) $(INSTALL_LIB_DIR)

uninstall-man8libs:
	rm -rf $(INSTALL_LIB_DIR)$(MAN8LIBS)

install-man8utils:
	cp --preserve=mode $(MAN8UTILS_DIR)/* $(INSTALL_BIN_DIR)

uninstall-man8utils:
	for f in $(MAN8UTILS_DIR)/*; do rm -f $(INSTALL_BIN_DIR)$$(basename $$f); done

install-python:
	cd mbctl-python-module && pip install . --break-system-packages

uninstall-python:
	pip uninstall -y mbctl
