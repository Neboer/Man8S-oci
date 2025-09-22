.PHONY: install uninstall

MAN8LIBS = man8lib
MAN8UTILS_DIR = man8utils
INSTALL_BIN_DIR = /usr/bin/
INSTALL_LIB_DIR = /usr/lib/

install:
	# 拷贝 man8lib 文件夹到 /usr/lib/
	cp -r $(MAN8LIBS) $(INSTALL_LIB_DIR)
	# 拷贝 man8utils 目录下所有文件到 /usr/bin/
	cp $(MAN8UTILS_DIR)/* $(INSTALL_BIN_DIR)

uninstall:
	# 删除 /usr/lib/man8lib 文件夹
	rm -rf $(INSTALL_LIB_DIR)$(MAN8LIBS)
	# 删除 /usr/bin/ 下 man8utils 目录中的所有文件
	for f in $(MAN8UTILS_DIR)/*; do rm -f $(INSTALL_BIN_DIR)$$(basename $$f); done
