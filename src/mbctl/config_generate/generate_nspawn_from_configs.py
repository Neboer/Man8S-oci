from mbctl.config_formats.nspawn_config import NspawnConfig
from mbctl.config_formats.man8s_config import Man8SContainerInfo
from mbctl.config_formats import OCIConfig
from mbctl.resources import get_file_content_as_str


# 从oci的json配置文件继续配置nspawn config。这个函数还是需要提供 man8s_config 的。
def generate_nspawn_config_from_configs(
    oci_config: OCIConfig, man8s_config: Man8SContainerInfo
) -> NspawnConfig:

    nspawn_example_config_content = get_file_content_as_str(
        "mbctl.resources.nspawn-files", f"{man8s_config.template}.nspawn"
    )

    nspawn_config = NspawnConfig(nspawn_example_config_content)

    # 设置init脚本和man8env.env挂载
    nspawn_config.set_exec_command("/sbin/busybox-init.sh")
    nspawn_config.add_bind_mount_idmap(
        "/man8env.env",
        man8s_config.get_container_man8env_config_path_str()
    )

    # 设置命令行参数
    process_args = oci_config.get_process_args()
    if process_args:
        nspawn_config.set_exec_command("/sbin/busybox-init.sh")

    # 设置环境变量。注意nspawn配置中只设置不属于软件配置的环境变量，属于容器配置的环境变量应该写入 config.man8machine_configs_path / man8env.env 中。
    normal_envs = oci_config.get_process_normal_envs()
    for env_key in normal_envs:
        nspawn_config.add_environment_var(env_key, normal_envs[env_key])

    # 设置工作目录
    process_cwd = oci_config.get_process_cwd()
    nspawn_config.set_working_directory(process_cwd)

    # 设置挂载点。具体参考README中关于“挂载点”的描述
    for mount_point, mount_target in man8s_config.user_defined_mount_points:
        nspawn_config.add_bind_mount_idmap(mount_point, mount_target)

    return nspawn_config
