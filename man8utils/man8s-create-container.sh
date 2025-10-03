#!/bin/bash -e

IMAGE="$1"
NAME="$2"

[ -z "$IMAGE" ] && { echo "Usage: $0 IMAGE-NAME MACHINE-NAME" >&2; exit 1; }
[ -z "$NAME" ] && { echo "Usage: $0 IMAGE-NAME MACHINE-NAME" >&2; exit 1; }

IMAGE_TEMP_DIR="/var/lib/man8s/temp/$NAME"
[ -d "$IMAGE_TEMP_DIR" ] && { echo "Directory $IMAGE_TEMP_DIR already exists" >&2; exit 1; }
man8pull-oci.sh "$IMAGE" "$IMAGE_TEMP_DIR"
