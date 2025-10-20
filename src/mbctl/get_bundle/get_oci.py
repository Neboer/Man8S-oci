import os
import shutil
import subprocess
import tempfile

from mbctl.utils.man8log import logger
from mbctl.utils.man8config import config


def fetch_oci_to_rootfs(image: str, rootfs_target: str) -> str:
    """
    拉取 OCI 镜像并将 rootfs 安装到 rootfs_target，同时返回一个可读取的 oci config.json 的临时文件路径。
    依赖: skopeo, umoci
    """
    os.makedirs(config["temp_dir"], exist_ok=True)
    parent_dir = os.path.dirname(rootfs_target)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    if os.path.exists(rootfs_target):
        raise FileExistsError(f"目标 rootfs 目录已存在: {rootfs_target}")

    tmp_bundle = tempfile.mkdtemp(prefix="oci-bundle.", dir=config["temp_dir"])
    tmp_unpack = tempfile.mkdtemp(prefix="oci-unpack.", dir=config["temp_dir"])

    oci_config_temp_path = None

    try:
        logger.info(f"拉取镜像 {image} ...")
        subprocess.run(
            ["skopeo", "copy", f"docker://{image}", f"oci:{tmp_bundle}:latest"],
            check=True,
        )

        logger.info("解包镜像 ...")
        subprocess.run(
            ["umoci", "unpack", "--image", f"{tmp_bundle}:latest", tmp_unpack],
            check=True,
        )

        # 将 rootfs 移动到目标目录
        unpacked_rootfs = os.path.join(tmp_unpack, "rootfs")
        if not os.path.isdir(unpacked_rootfs):
            raise FileNotFoundError(f"未找到解包后的 rootfs: {unpacked_rootfs}")
        shutil.move(unpacked_rootfs, rootfs_target)

        # 将 config.json 复制到 temp_dir 下的临时文件，返回该路径
        src_config = os.path.join(tmp_unpack, "config.json")
        if not os.path.isfile(src_config):
            raise FileNotFoundError(f"未找到解包后的 config.json: {src_config}")

        with tempfile.NamedTemporaryFile(
            prefix="oci-config.", suffix=".json", dir=config["temp_dir"], delete=False
        ) as cfg_tmp:
            shutil.copyfile(src_config, cfg_tmp.name)
            oci_config_temp_path = cfg_tmp.name

        logger.info("OCI 镜像获取完成")
        return oci_config_temp_path

    except subprocess.CalledProcessError as e:
        logger.error(f"命令执行失败: {e}")
        raise
    finally:
        # 清理临时目录
        shutil.rmtree(tmp_bundle, ignore_errors=True)
        shutil.rmtree(tmp_unpack, ignore_errors=True)
