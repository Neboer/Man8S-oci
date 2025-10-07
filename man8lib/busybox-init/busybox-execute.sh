#!/bin/sh
# A helper script to execute BusyBox commands
BUSYBOX_LOCATION=${BUSYBOX_LOCATION:-/bin/busybox}
if [ ! -x "$BUSYBOX_LOCATION" ]; then
    echo "Error: BusyBox not found at $BUSYBOX_LOCATION"
    exit 1
fi
# execute busybox with all parameters
function BUSYBOX_RUN() {
    exec "$BUSYBOX_LOCATION" "$@"
}
