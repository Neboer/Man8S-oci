#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "用法: $0 <镜像名:tag> <目标目录>"
    echo "示例: $0 gcr.io/distroless/nodejs22-debian12:nonroot /usr/lib/machines/DTLTest1"
    exit 1
fi

IMAGE="$1"
TARGET="$2"

# 临时目录：bundle + unpack 目录
TMP_BUNDLE="$(mktemp -d /tmp/oci-bundle.XXXXXX)"
TMP_UNPACK="$(mktemp -d /tmp/oci-unpack.XXXXXX)"

cleanup() {
    rm -rf "$TMP_BUNDLE" "$TMP_UNPACK"
}
trap cleanup EXIT

echo "==> 拉取镜像 $IMAGE ..."
skopeo copy "docker://$IMAGE" "oci:$TMP_BUNDLE:latest"

echo "==> 解包镜像 ..."
sudo umoci unpack --image "$TMP_BUNDLE:latest" "$TMP_UNPACK"

echo "==> 移动 rootfs 到 $TARGET ..."
sudo mkdir -p "$(dirname "$TARGET")"
sudo rm -rf "$TARGET"
sudo mv "$TMP_UNPACK/rootfs" "$TARGET"

echo "==> 完成"
