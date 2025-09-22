#!/bin/sh
# A minimal init script for BusyBox-based containers.
/sbin/busybox-autoconfig-networking.sh
exec /sbin/application.sh