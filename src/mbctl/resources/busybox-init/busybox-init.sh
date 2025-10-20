#!/bin/sh
# A minimal init script for BusyBox-based containers.
source /man8env.env
source /sbin/busybox-execute.sh
source /sbin/busybox-autoconfig-networking.sh
source /sbin/yggdrasil-config-ipaddr.sh
source /sbin/application.sh
