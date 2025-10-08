#!/bin/sh
# Configure Yggdrasil IP address if YGGDRASIL_IPADDR is set
if [ -n "$YGGDRASIL_IPADDR" ]; then
    BUSYBOX_RUN ip addr add "$YGGDRASIL_IPADDR" dev "$MAN8S_HOST_IFACE"
fi