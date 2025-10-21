# 从OCI镜像URL创建nspawn容器

from enum import Enum
import os

from typing import Literal

from mbctl.utils.man8log import logger
from mbctl.utils.man8config import config, ContainerTemplate, ContainerTemplateList
from mbctl.config_formats import (
    OCIConfig,
    Man8SContainerInfo,
    NspawnConfig,
    EnvFileTools,
)
from mbctl.config_generate import (
    generate_nspawn_config_from_configs,
    generate_env_config_from_configs,
)
from mbctl.networking.yggdrasil_addr import string_to_host_ygg_subnet_v6addr
from mbctl.init_system.man8s_add_initsystem import install_init_system_to_machine
from mbctl.resources import get_file_content_as_str
from mbctl.get_bundle.get_oci import fetch_oci_to_rootfs  # 新增


# 主函数，完整流程。从OCI URL创建一个完整的容器。
def pull_oci_image_and_create_container(
    oci_image_url: str, container_name: str, container_template: ContainerTemplate
):
    # 第一步：创建man8s_config

    ## 首先，需要完成ygg_address的填写。
    ygg_address = string_to_host_ygg_subnet_v6addr(container_name)

    logger.info(f"为容器 {container_name} 分配 Yggdrasil 地址 {ygg_address}")

    man8s_container_info = Man8SContainerInfo(
        name=container_name,
        template=container_template,
        ygg_address=ygg_address,
        oci_image_url=oci_image_url,
    )

    if os.path.exists(man8s_container_info.container_dir):
        raise FileExistsError(f"容器 {man8s_container_info.container_dir} 已存在")

    # 拉取镜像并将 rootfs 放置到容器目标目录，返回 config.json 的临时路径
    oci_config_path = fetch_oci_to_rootfs(
        oci_image_url, man8s_container_info.container_dir_str
    )

    # 第二步：创建oci_config
    oci_config = OCIConfig(oci_config_path)

    # 第三步：可以生成 envs 配置文件与 nspawn 配置文件了
    ## 生成 nspawn 配置文件
    nspawn_config = generate_nspawn_config_from_configs(
        oci_config, man8s_container_info
    )
    ## 生成 envs 配置文件
    envs_config = generate_env_config_from_configs(oci_config, man8s_container_info)

    # 第四步：将配置文件中自动生成的容器数据挂载点实际创建出来。
    all_need_create_dirs = []

    ## 首先，创建容器的存储目录与配置目录
    all_need_create_dirs.append(man8s_container_info.get_container_config_path_str())
    all_need_create_dirs.append(man8s_container_info.get_container_storage_path_str())

    ## 其次，将 nspawn 配置文件中的存储挂载点目录创建出来
    for src_path in nspawn_config.get_all_bind_mount_srcs():
        if man8s_container_info.check_is_storage_path(src_path):
            all_need_create_dirs.append(src_path)

    ## 从all_bind_mount_srcs中找出所有man8s storage路径，并创建它们（此时，配置文件路径应该只有 man8env.env 这个文件，需要跳过它）
    for d in all_need_create_dirs:
        os.makedirs(d, exist_ok=True)
        logger.debug(f"已创建挂载点目录 {d}")

    # 第五步：写入 nspawn 和 envs 配置文件到对应位置，创建
    nspawn_config.write_to_file(
        man8s_container_info.get_container_nspawn_file_path_str()
    )
    logger.info(
        f"nspawn 配置文件已写入 {man8s_container_info.get_container_nspawn_file_path_str()}"
    )
    EnvFileTools.write_env_file(
        envs_config, man8s_container_info.get_container_man8env_config_path_str()
    )
    logger.info(
        f"环境变量配置文件已写入 {man8s_container_info.get_container_man8env_config_path_str()}"
    )

    # 第六步：执行 man8s-add-initsystem ，将 busybox-network-init 系统安装在目标容器中。
    install_init_system_to_machine(man8s_container_info.container_dir_str)

    logger.info(
        f"容器 {container_name} 创建完成，根文件系统位于 {man8s_container_info.container_dir_str}"
    )

    # 第七步：在 system_machines_path 下创建指向容器目录的符号链接，正式启用容器。
    os.symlink(
        man8s_container_info.container_dir_str,
        os.path.join(config["system_machines_path"], container_name),
    )
