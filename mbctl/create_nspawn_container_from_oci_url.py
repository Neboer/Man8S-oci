# 从OCI镜像URL创建nspawn容器

from enum import Enum
import logging
import os
import shutil
import subprocess
import tempfile

from typing import Literal

from man8log import logger
from man8config import config, ContainerTemplate, ContainerTemplateList
from create_nspawn_file_by_oci_config import get_oci_config, create_nspawn_config_by_oci_config
from configure_nspawn_container_network import get_host_yggdrasil_address_and_subnet, calculate_nspawn_container_ipv6_address

def pull_oci_image(image: str, target: str):
    """
    下载 OCI 镜像并解包到指定目录，保留完整 config.json 和 rootfs。
    依赖: skopeo, umoci
    """
    tmp_bundle = tempfile.mkdtemp(prefix="oci-bundle.", dir=config["temp_dir"])
    tmp_unpack = target

    try:
        logger.info(f"拉取镜像 {image} ...")
        subprocess.run(
            ["skopeo", "copy", f"docker://{image}", f"oci:{tmp_bundle}:latest"],
            check=True
        )

        logger.info("解包镜像 ...")
        subprocess.run(
            ["umoci", "unpack", "--image", f"{tmp_bundle}:latest", tmp_unpack],
            check=True
        )

        logger.info("完成")
    except subprocess.CalledProcessError as e:
        logger.error(f"命令执行失败: {e}")
        raise
    finally:
        logger.info("清理临时目录 ...")
        shutil.rmtree(tmp_bundle, ignore_errors=True)

def create_nspawn_container_from_oci_bundle(oci_bundle_path: str, container_name: str, container_template: ContainerTemplate):
    """
    使用解包好的 OCI 镜像创建 nspawn 容器。
    """
    container_root_install_destination = os.path.join(config["man8machines_path"], container_name)
    if os.path.exists(container_root_install_destination):
        raise FileExistsError(f"容器 {container_name} 已存在")

    oci_config = get_oci_config(os.path.join(oci_bundle_path, "config.json"))
    nspawn_example_path = os.path.join(config["lib_root"], "nspawn-files", f"{container_template}.nspawn")
    
    if container_template == "network_isolated":
        ygg_address, ygg_subnet = get_host_yggdrasil_address_and_subnet()
        container_ipv6 = calculate_nspawn_container_ipv6_address(ygg_subnet, container_name)
        logger.info(f"为容器 {container_name} 分配 Yggdrasil 地址 {container_ipv6}/{ygg_subnet.split('/')[1]}")
    else:
        container_ipv6 = ""

    nspawn_config = create_nspawn_config_by_oci_config(oci_config, nspawn_example_path, container_ipv6)
    target_container_nspawn_file_path = os.path.join(config["nspawn_file_path"], f"{container_name}.nspawn")
    with open(target_container_nspawn_file_path, "w") as f:
        nspawn_config.write_nspawn_config(f)
 
    logger.info(f"nspawn 配置文件已写入 {target_container_nspawn_file_path}")

    shutil.move(os.path.join(oci_bundle_path, "rootfs"), container_root_install_destination)

    # 执行 man8s-add-initsystem ，将 busybox-network-init 系统安装在目标容器中。
    subprocess.run(["man8s-add-initsystem", container_root_install_destination])

    logger.info(f"容器 {container_name} 创建完成，根文件系统位于 {container_root_install_destination}")

    os.symlink(container_root_install_destination, os.path.join(config["system_machines_path"], container_name))

def main():
    import argparse

    parser = argparse.ArgumentParser(description="从OCI镜像URL创建nspawn容器")
    parser.add_argument("image", help="OCI镜像URL，例如 docker.io/library/ubuntu:latest")
    parser.add_argument("container_name", help="容器名称")
    parser.add_argument(
        "--template",
        type=str,
        choices=ContainerTemplateList,
        default="network_isolated",
        help="容器模板，默认为 network_isolated"
    )
    args = parser.parse_args()

    # 创建临时路径
    os.makedirs(config["temp_dir"], exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="oci-unpack.", dir=config["temp_dir"]) as tmpdir:
        pull_oci_image(args.image, tmpdir)
        create_nspawn_container_from_oci_bundle(tmpdir, args.container_name, args.template)

if __name__ == "__main__":
    main()