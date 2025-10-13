#!/usr/bin/env python3
"""
man8s_add_initsystem.py

Python equivalent of man8s-add-initsystem.sh

Usage: python3 man8s_add_initsystem.py <MACHINE_PATH>

This will copy the host busybox into <MACHINE_PATH>/bin, ensure a
`sh` symlink to busybox exists, copy man8lib busybox init scripts to
<MACHINE_PATH>/sbin, and install the udhcpc default script to
<MACHINE_PATH>/usr/share/udhcpc/default.script.

Notes:
- This script attempts to match the behavior of the original bash
  script. It performs safe checks and will raise informative errors
  if files are missing or if permissions prevent writing to the target
  locations.
"""

from __future__ import annotations

import os
import shutil
import stat
import sys
from pathlib import Path

from mbctl.utils.man8config import config

HOST_BUSYBOX = Path(config["host_busybox_path"])
LIBRARY_DIR = Path(config["lib_root"])

def install(machine_path: Path) -> None:
    machine_path = machine_path.resolve()

    bin_dir = machine_path / "bin"
    sbin_dir = machine_path / "sbin"
    udhcpc_target_dir = machine_path / "usr" / "share" / "udhcpc"

    # 1. Ensure destination directories exist
    for d in (bin_dir, sbin_dir, udhcpc_target_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 2. Copy busybox
    if not HOST_BUSYBOX.exists():
        raise FileNotFoundError(f"Host busybox not found at {HOST_BUSYBOX}")

    dest_busybox = bin_dir / "busybox"
    shutil.copy2(HOST_BUSYBOX, dest_busybox)
    # keep executable bits
    dest_busybox.chmod(dest_busybox.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # 3. Ensure /bin/sh symlink to busybox
    sh_link = bin_dir / "sh"
    # If exists and not a symlink, do not overwrite; else create symlink
    if sh_link.exists():
        if sh_link.is_symlink():
            # update target if necessary
            current = os.readlink(sh_link)
            if Path(current).name != "busybox":
                sh_link.unlink()
                sh_link.symlink_to("busybox")
        else:
            # existing file (not symlink) - do nothing to avoid destructive change
            pass
    else:
        # create a relative symlink to busybox
        try:
            sh_link.symlink_to("busybox")
        except OSError:
            # On Windows or filesystems that don't support symlinks, copy as fallback
            shutil.copy2(dest_busybox, sh_link)

    # 4. Copy man8lib/busybox-init/* to <machine>/sbin
    busybox_init_dir = LIBRARY_DIR / "busybox-init"
    if busybox_init_dir.exists() and busybox_init_dir.is_dir():
        for item in busybox_init_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, sbin_dir / item.name)
                # ensure executable
                (sbin_dir / item.name).chmod((sbin_dir / item.name).stat().st_mode | stat.S_IXUSR)
    else:
        # If the directory doesn't exist, warn but continue
        print(f"Warning: {busybox_init_dir} not found; skipping busybox-init install", file=sys.stderr)

    # 5. Install udhcpc-default.script
    udhcpc_src = LIBRARY_DIR / "busybox-networking" / "udhcpc-default.script"
    if udhcpc_src.exists() and udhcpc_src.is_file():
        target = udhcpc_target_dir / "default.script"
        shutil.copy2(udhcpc_src, target)
        target.chmod(target.stat().st_mode | stat.S_IXUSR)
    else:
        print(f"Warning: {udhcpc_src} not found; skipping udhcpc script install", file=sys.stderr)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: man8s_add_initsystem.py <MACHINE_PATH>", file=sys.stderr)
        return 2

    machine_path = Path(argv[1])
    if not machine_path.exists():
        # Try to create the root directory if it doesn't exist
        try:
            machine_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"Cannot create machine path {machine_path}: {e}", file=sys.stderr)
            return 3

    try:
        install(machine_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
