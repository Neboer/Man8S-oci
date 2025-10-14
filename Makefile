.PHONY: build install uninstall install-man8libs install-python \
	uninstall-man8libs ununinstall-python

MAN8LIBS = man8lib
MAN8UTILS_DIR = man8utils
INSTALL_BIN_DIR = /usr/bin/
INSTALL_LIB_DIR = /usr/lib/

# 仅构建 Python Wheel（默认目标）
build:
	cd mbctl-python-module && python -m pip wheel . -w dist

# 安装：先构建，再安装 man8libs 和已构建的 wheel
install: build
	$(MAKE) install-man8libs
	$(MAKE) install-python

uninstall: uninstall-man8libs uninstall-python

install-man8libs:
	cp --preserve=mode -r $(MAN8LIBS) $(INSTALL_LIB_DIR)

uninstall-man8libs:
	rm -rf $(INSTALL_LIB_DIR)$(MAN8LIBS)

# 从已构建的 wheel 安装
install-python:
	cd mbctl-python-module && WHEEL=$$(ls -t dist/*.whl | head -n 1) && [ -n "$$WHEEL" ] && pip install "$$WHEEL" --break-system-packages

uninstall-python:
	pip uninstall -y mbctl
