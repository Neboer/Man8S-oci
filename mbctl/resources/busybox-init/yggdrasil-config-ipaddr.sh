#!/bin/sh
# Configure Yggdrasil IP address if MAN8S_YGGDRASIL_ADDRESS is set
if [ -n "$MAN8S_YGGDRASIL_ADDRESS" ]; then
    BUSYBOX_RUN ip addr add "$MAN8S_YGGDRASIL_ADDRESS" dev "$MAN8S_HOST_IFACE"
fi