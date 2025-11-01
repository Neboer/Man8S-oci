#!/bin/busybox sh
# A minimal init script for BusyBox-based containers.
source /sbin/busybox-execute.sh
source /sbin/busybox-copy-protected-dirs.sh
source /sbin/busybox-load-envs.sh
source /sbin/busybox-autoconfig-networking.sh
source /sbin/yggdrasil-config-ipaddr.sh
source /sbin/application.sh
