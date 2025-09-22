#!/bin/sh
# Minimal network initialization for BusyBox-only container
# Supports DHCP(v4) + DHCPv6 (if udhcpc6 exists)

set -e

# 找出除了 lo 之外的第一个接口
IFACE="$(/usr/bin/ip -o link show | awk -F': ' '{print $2}' | grep -v '^lo$' | sed 's/@.*//' | head -n1)"

if [ -z "$IFACE" ]; then
    echo "No non-loopback interface found"
    exit 1
fi

echo "Bringing up interface $IFACE"

/usr/bin/ip link set dev "$IFACE" up

# IPv4 via DHCP
if command -v udhcpc >/dev/null 2>&1; then
    echo "Requesting IPv4 via DHCP..."
    /usr/bin/udhcpc -i "$IFACE" -q -n -t 3 -T 3
else
    echo "udhcpc not found: cannot configure IPv4 via DHCP"
fi

# IPv6 via DHCPv6
if command -v udhcpc6 >/dev/null 2>&1; then
    echo "Requesting IPv6 via DHCPv6..."
    /usr/bin/udhcpc6 -i "$IFACE" -n -q
else
    echo "udhcpc6 not found: skipping DHCPv6"
fi

# 打印配置结果
echo "Final addresses:"
/usr/bin/ip addr show dev "$IFACE"
/usr/bin/ip route show
