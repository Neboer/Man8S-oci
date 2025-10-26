# 从OCI镜像URL创建nspawn容器

from enum import Enum
import os

from pathlib import Path
from typing import Literal

from mbctl.utils.man8log import logger
from mbctl.utils.man8config import config, ContainerTemplate, ContainerTemplateList
from mbctl.utils.file_operate import copy_all_contents
from mbctl.config_formats import (
    OCIConfig,
    Man8SContainerInfo,
    NspawnConfig,
    EnvFileTools,
    OCIShallowConfig,
)
from mbctl.config_generate import (
    generate_nspawn_config_from_configs,
    generate_env_config_from_configs,
)
from mbctl.networking.yggdrasil_addr import string_to_host_ygg_subnet_v6addr
from mbctl.init_system.man8s_add_initsystem import install_init_system_to_machine
from mbctl.resources import get_file_content_as_str
from mbctl.get_bundle.get_oci import fetch_oci_to_rootfs  # 新增
from mbctl.get_bundle.get_oci_shallow_config import get_container_shallow_config
from mbctl.user_interaction.must_input import must_input_list, must_input_absolute_path


# 交互式询问用户挂载的目标路径，将用户选好的路径添加到 man8s_container_info 中。
# - 配置文件：会挂载到 `<config.man8machine_configs_path>/<ContainerName>/` 下的对应路径。
# - 数据文件：会挂载到 `<config.man8machine_storage_path>/<ContainerName>/` 下的对应路径。
# - 自定义目标：再弹出一个问题，要求用户输入自定义目标，会挂载到用户的目标路径。
# - 跳过：不会挂载这个路径。
# 注意，所有的这些挂载，都是指路径挂载。Man8S不支持文件挂载，如果要求文件挂载请回答跳过，然后自己编辑nspawn文件创建挂载关系。
def ask_user_input_mount_target(
    man8s_container_info: Man8SContainerInfo,
    mount_point: str,
) -> str | None:
    print(f"容器镜像声明了挂载点 {mount_point} 。")
    print(f"请输入数字选择此挂载点的类型：")
    print("\n1)配置文件 2)数据路径 3)自定义目标 4)跳过：")
    target_type = must_input_list({"1", "2", "3", "4"})
    if target_type == "1":
        # 配置文件
        print(f"选择将挂载点 {mount_point} 作为配置文件挂载。")
        mount_target = man8s_container_info.get_container_config_path_str(mount_point)
    elif target_type == "2":
        print(f"选择将挂载点 {mount_point} 作为数据路径挂载。")
        mount_target = man8s_container_info.get_container_storage_path_str(mount_point)
    elif target_type == "3":
        print(f"请输入自定义挂载目标的绝对路径")
        custom_target = must_input_absolute_path(must_exist=False, must_non_exst=True)
        mount_target = custom_target
    elif target_type == "4":
        print(f"选择跳过挂载点 {mount_point} 。")
        mount_target = None
    else:
        raise ValueError("未知的挂载点类型选择。")  # how do you reach here?

    return mount_target


# 主函数，完整流程。从OCI URL创建一个完整的容器。
def pull_oci_image_and_create_container(
    oci_image_url: str,
    container_name: str,
    container_template: ContainerTemplate,
    provided_mount_configs: dict = {},
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

    # 第二步：获取容器的shallow config，确认容器基本信息，并且获取容器的推荐挂载点，询问用户将这些挂载点挂载到哪里。
    container_shallow_config: OCIShallowConfig = get_container_shallow_config(
        oci_image_url
    )
    ## 获得所有volume，并打印提示信息，让用户选择这些挂载点的目标。挂载点目标选择的详细文档请参考 config_generate/README.md
    mount_points: list[str] = container_shallow_config["config"]["Volumes"]
    for mount_point in mount_points:
        if mount_point in provided_mount_configs:
            mount_target = provided_mount_configs[mount_point]
        else:
            mount_target = ask_user_input_mount_target(
                man8s_container_info, mount_point
            )
        if mount_target is not None:
            man8s_container_info.add_user_defined_mount_point(mount_point, mount_target)

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

    ## 首先，创建容器的存储目录与配置目录的基本目录
    os.makedirs(man8s_container_info.get_container_config_path_str())
    os.makedirs(man8s_container_info.get_container_storage_path_str())

    ## 其次，将man8s配置中，用户之前写明的作为目标的target挂载点目录创建出来
    ## 然后将实际容器路径中，mount_point下所有的内容（可能是一些示例配置或基本数据）全部拷贝到target_path下。
    for mount_point, target_path in man8s_container_info.user_defined_mount_points:
        os.makedirs(target_path)
        # 将容器内挂载目标的内容全部复制到目标路径下
        mount_point_real_path = man8s_container_info.get_container_path_str(mount_point)
        if os.path.exists(mount_point_real_path) and os.path.isdir(
            mount_point_real_path
        ):
            copy_all_contents(
                man8s_container_info.get_container_path_str(mount_point),
                target_path,
            )
            logger.info(f"已拷贝挂载点中的所有内容 {mount_point} -> {target_path} 。")

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
