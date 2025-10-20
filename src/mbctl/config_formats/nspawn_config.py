from .systemd_config import SystemdUnitINIConfig


# nspawn 专用的配置包装器
class NspawnConfig(SystemdUnitINIConfig):
    # 单个键值对
    def add_environment_var(self, key: str, value: str):
        self.add_key_value("Exec", "Environment", f'"{key}={value}"')

    # 单个挂载: src, dst[, opts]
    def add_bind_mount(self, src: str, dst: str, opts: str | None = None):
        bind_entry = f"{src}:{dst}" + (f":{opts}" if opts else "")
        self.add_key_value("Files", "Bind", bind_entry)
    
    def add_bind_mount_idmap(self, src: str, dst: str):
        return self.add_bind_mount(src, dst, "idmap")

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
