#!/usr/bin/bash -e
# 将busybox从主机中拷贝到容器系统里，并在容器里安装Man8s-busybox-networkinit工具，使容器可以从网络启动，并执行启动命令。

HOST_BUSYBOX="/bin/busybox"
MACHINE_PATH="${1}"
LIBRARY_DIR="/usr/lib/man8lib"

mkdir -p ${MACHINE_PATH}/bin
if [ ! -e "${MACHINE_PATH}/bin/sh" ]; then
    ln -s busybox "${MACHINE_PATH}/bin/sh"
fi
cp -a ${HOST_BUSYBOX} ${MACHINE_PATH}/bin/busybox

# 安装Man8s-busybox-networkinit工具
cp -a ${LIBRARY_DIR}/busybox-init/* ${MACHINE_PATH}/sbin/
install -D ${LIBRARY_DIR}/busybox-networking/udhcpc-default.script ${MACHINE_PATH}/usr/share/udhcpc/default.script
