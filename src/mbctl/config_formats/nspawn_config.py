from .systemd_config import SystemdUnitINIConfig


# nspawn 专用的配置包装器
class NspawnConfig(SystemdUnitINIConfig):
    # 单个键值对
    def add_environment_var(self, key: str, value: str):
        self.add_key_value("Exec", "Environment", f'"{key}={value}"')

    # 单个挂载: mount_point, mount_target
    ## 注意，实际写入bind的mount_point与mount_target是相反的。
    ## mount_point 指的是容器内的路径，mount_target 指的是宿主机的路径。
    ## 为什么这里要反过来？ 因为 systemd-nspawn 的 Bind 配置项的格式是 host_path:container_path 。
    ## 而我们在 Man8SContainerInfo 中定义的挂载点是 mount_point -> mount_target ，
    def add_bind_mount(self, mount_point: str, mount_target: str, opts: str | None = None):
        bind_entry = f"{mount_target}:{mount_point}" + (f":{opts}" if opts else "")
        self.add_key_value("Files", "Bind", bind_entry)

    def add_bind_mount_idmap(self, mount_point: str, mount_target: str):
        return self.add_bind_mount(mount_point, mount_target, "idmap")

    # 设置工作目录和启动命令
    def set_working_directory(self, path: str):
        self.set_key_value("Exec", "WorkingDirectory", path)

    def set_exec_command(self, command: str):
        # 在示例中使用 Parameters 作为启动命令键
        self.set_key_value("Exec", "Parameters", command)

    # 方便函数，获取所有bind_mount的src路径列表
    def get_all_bind_mount_srcs(self) -> list[str]:
        binds = self.systemd_ini_config["Files"].get("Bind", [])
        srcs = [bind.split(":", 1)[0] for bind in binds]
        return srcs
