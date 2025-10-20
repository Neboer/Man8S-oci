from mbctl.config_formats.nspawn_config import NspawnConfig
from mbctl.config_formats.man8s_config import Man8SContainerInfo
from mbctl.config_formats import OCIConfig
from mbctl.utils.shell import args_list_to_command

# 从 oci 与 man8s 配置生成软件的基本配置的环境变量。对很多软件而言，这些环境变量足以表达软件的配置需求，类似docker的环境变量配置方式。
# 生成的文件的名字叫 man8env.env，放在 man8machine_configs_path / <container_name> / man8env.env 中。
def generate_env_config_from_configs(
    oci_config: OCIConfig, man8s_config: Man8SContainerInfo
) -> dict[str, str]:
    # 将man8s_config作为基本信息配置进去。
    env_config: dict[str, str] = {}
    env_config["MAN8S_CONTAINER_NAME"] = man8s_config.name
    env_config["MAN8S_CONTAINER_TEMPLATE"] = man8s_config.template
    env_config["MAN8S_YGGDRASIL_ADDRESS"] = man8s_config.ygg_address
    env_config["MAN8S_OCI_IMAGE_URL"] = man8s_config.oci_image_url
    
    # 从oci_config中获取实际的运行的命令与环境变量
    process_commandline = args_list_to_command(oci_config.get_process_args())
    env_config["MAN8S_APPLICATION_ARGS"] = process_commandline
    # 从oci_config中获取额外的环境变量，这些环境变量是应用程序需要的配置环境变量
    config_envs = oci_config.get_process_extra_envs()
    for env_key in config_envs:
        env_config[env_key] = config_envs[env_key]
    
    return env_config