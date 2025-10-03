#!/usr/bin/env bash
# 将镜像umoci解包至指定目录，保留完整config.json和rootfs。
# 依赖: skopeo, umoci
set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "用法: $0 <镜像名:tag> <目标目录>"
    echo "示例: $0 gcr.io/distroless/nodejs22-debian12:nonroot /tmp/DTLTest1-bundle"
    exit 1
fi

IMAGE="$1"
TARGET="$2"

# 临时目录：bundle + unpack 目录
TMP_BUNDLE="$(mktemp -d /tmp/oci-bundle.XXXXXX)"
TMP_UNPACK="$TARGET"

cleanup() {
    rm -rf "$TMP_BUNDLE" "$TMP_UNPACK"
}
trap cleanup EXIT

echo "==> 拉取镜像 $IMAGE ..."
skopeo copy "docker://$IMAGE" "oci:$TMP_BUNDLE:latest"

echo "==> 解包镜像 ..."
sudo umoci unpack --image "$TMP_BUNDLE:latest" "$TMP_UNPACK"

echo "==> 完成"
