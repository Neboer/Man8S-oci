#!/usr/bin/env python3
"""
man8s_add_initsystem.py

相当于 man8s-add-initsystem.sh 的 Python 版本

用法: python3 man8s_add_initsystem.py <MACHINE_PATH>

此脚本会将主机的 busybox 复制到 <MACHINE_PATH>/bin，确保存在指向 busybox 的 `sh` 链接，
将 man8lib 的 busybox init 脚本复制到 <MACHINE_PATH>/sbin，并将 udhcpc 的默认脚本安装到
<MACHINE_PATH>/usr/share/udhcpc/default.script。
"""

from __future__ import annotations

import os
import shutil
import stat
import sys
from pathlib import Path

from mbctl.utils.man8config import config
from mbctl.utils.man8log import logger
from mbctl.resources import copy_resdir_content_to_target_folder, get_file_content_as_str


HOST_BUSYBOX = Path(config["host_busybox_path"])

def install_init_system_to_machine(machine_path_str: str) -> None:
    machine_path = Path(machine_path_str).resolve()

    bin_dir = machine_path / "bin"
    sbin_dir = machine_path / "sbin"
    udhcpc_target_dir = machine_path / "usr" / "share" / "udhcpc"

    # 1. 确保目标目录存在
    for d in (bin_dir, sbin_dir, udhcpc_target_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 2. 复制 busybox
    if not HOST_BUSYBOX.exists():
        raise FileNotFoundError(f"主机上的 busybox 未找到：{HOST_BUSYBOX}")

    dest_busybox = bin_dir / "busybox"
    shutil.copy2(HOST_BUSYBOX, dest_busybox)
    # 保留可执行位
    dest_busybox.chmod(dest_busybox.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # 3. 确保 /bin/sh 指向 busybox 的符号链接
    sh_link = bin_dir / "sh"
    # 如果存在且不是符号链接，则不覆盖；否则创建符号链接
    if sh_link.exists():
        if sh_link.is_symlink():
            # 如有必要，更新目标
            current = os.readlink(sh_link)
            if Path(current).name != "busybox":
                sh_link.unlink()
                sh_link.symlink_to("busybox")
        else:
            # 已有文件（非符号链接）—为避免破坏性修改，保持原状
            pass
    else:
        sh_link.symlink_to("busybox")

    # 4. 复制 man8lib/busybox-init/* 到 <machine>/sbin
    copy_resdir_content_to_target_folder("mbctl.resources.busybox-init", sbin_dir)

    # 5. 安装 udhcpc-default.script
    copy_resdir_content_to_target_folder("mbctl.resources.busybox-networking", udhcpc_target_dir)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        logger.error("用法: man8s_add_initsystem.py <MACHINE_PATH>")
        return 2

    machine_path = argv[1]

    try:
        install_init_system_to_machine(machine_path)
    except Exception as e:
        logger.error(f"错误：{e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
