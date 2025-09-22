#!/bin/bash -e
# create a distroless rootfs.

IMAGE_NAME="${1}"
LIBRARY_DIR="/usr/lib/man8lib"

# gcr.io/distroless/static-debian12	latest, nonroot, debug, debug-nonroot	amd64, arm64, arm, s390x, ppc64le
# gcr.io/distroless/base-debian12	latest, nonroot, debug, debug-nonroot	amd64, arm64, arm, s390x, ppc64le
# gcr.io/distroless/base-nossl-debian12	latest, nonroot, debug, debug-nonroot	amd64, arm64, arm, s390x, ppc64le
# gcr.io/distroless/cc-debian12	latest, nonroot, debug, debug-nonroot	amd64, arm64, arm, s390x, ppc64le
# gcr.io/distroless/python3-debian12	latest, nonroot, debug, debug-nonroot	amd64, arm64
# gcr.io/distroless/java-base-debian12	latest, nonroot, debug, debug-nonroot	amd64, arm64, s390x, ppc64le
# gcr.io/distroless/java17-debian12	latest, nonroot, debug, debug-nonroot	amd64, arm64, s390x, ppc64le
# gcr.io/distroless/java21-debian12	latest, nonroot, debug, debug-nonroot	amd64, arm64, ppc64le
# gcr.io/distroless/nodejs20-debian12	latest, nonroot, debug, debug-nonroot	amd64, arm64, arm, s390x, ppc64le
# gcr.io/distroless/nodejs22-debian12	latest, nonroot, debug, debug-nonroot	amd64, arm64, arm, s390x, ppc64le
# gcr.io/distroless/nodejs24-debian12	latest, nonroot, debug, debug-nonroot	amd64, arm64, s390x, ppc64le

AVAILABLE_IMAGES=(
    "static-debian12"
    "base-debian12"
    "base-nossl-debian12"
    "cc-debian12"
    "python3-debian12"
    "java-base-debian12"
    "java17-debian12"
    "java21-debian12"
    "nodejs20-debian12"
    "nodejs22-debian12"
    "nodejs24-debian12"
)

# https://doc.nju.edu.cn/books/e1654/page/gcr 南京大学镜像
GCR_IO_MIRROR="gcr.nju.edu.cn"
# GCR_IO_MIRROR="gcr.io"

if [[ ! " ${AVAILABLE_IMAGES[*]} " =~ " ${IMAGE_NAME} " ]]; then
    echo "Error: Unsupported image name ${IMAGE_NAME}"
    echo "Supported images are: ${AVAILABLE_IMAGES[*]}"
    exit 1
fi

MACHINE_NAME="${2}"
if [ -z "${MACHINE_NAME}" ]; then
    echo "Usage: $0 IMAGE-NAME MACHINE-NAME" >&2
    exit 1
fi

TARGET_DIR="/var/lib/machines/${MACHINE_NAME}"

[ -z "${TARGET_DIR}" ] && { echo "Usage: $0 IMAGE-NAME TARGET-DIR" >&2; exit 1; }
[ -d "${TARGET_DIR}" ] && { echo "Directory ${TARGET_DIR} already exists" >&2; exit 1; }

man8pull-oci.sh "${GCR_IO_MIRROR}/distroless/${IMAGE_NAME}:debug" "${TARGET_DIR}"

# fix busybox links

ln -sf /busybox/busybox ${TARGET_DIR}/busybox/udhcpc6

cp -P ${TARGET_DIR}/busybox/* ${TARGET_DIR}/bin/
cp -P ${TARGET_DIR}/busybox/* ${TARGET_DIR}/usr/bin/

rm ${TARGET_DIR}/bin/busybox
rm ${TARGET_DIR}/usr/bin/busybox

# busybox init

cp ${LIBRARY_DIR}/busybox-init/* ${TARGET_DIR}/sbin/

# busybox autoconfig networking

install -D ${LIBRARY_DIR}/busybox-networking/udhcpc-default.script ${TARGET_DIR}/usr/share/udhcpc/default.script