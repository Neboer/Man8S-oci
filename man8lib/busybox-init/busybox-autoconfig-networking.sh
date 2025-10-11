#!/bin/sh
# Minimal network initialization for BusyBox-only container
# Supports DHCP(v4) + DHCPv6 (if udhcpc6 exists)

set -e

# 找出除了 lo 之外的第一个接口
MAN8S_HOST_IFACE="$(BUSYBOX_RUN ip -o link show | BUSYBOX_RUN awk -F': ' '{print $2}' | BUSYBOX_RUN grep -v '^lo$' | BUSYBOX_RUN sed 's/@.*//' | BUSYBOX_RUN head -n1)"

export MAN8S_HOST_IFACE

if [ -z "$MAN8S_HOST_IFACE" ]; then
    echo "No non-loopback interface found"
    exit 1
fi

echo "Bringing up interface $MAN8S_HOST_IFACE"

BUSYBOX_RUN ip link set dev "$MAN8S_HOST_IFACE" up
BUSYBOX_RUN udhcpc -i "$MAN8S_HOST_IFACE" -q -n -t 3 -T 3

# 打印配置结果
echo "Final addresses:"
BUSYBOX_RUN ip addr show dev "$MAN8S_HOST_IFACE"
BUSYBOX_RUN ip route show
