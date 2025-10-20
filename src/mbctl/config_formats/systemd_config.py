from SystemdUnitParser import SystemdUnitParser

from mbctl.resources import get_file_content_as_str


# 代表一个nspawn config的抽象表示，它可以随时读写到文件中
class SystemdUnitINIConfig:

    def __init__(self, init_ini_file_content: str) -> None:
        self.systemd_ini_config = SystemdUnitParser()
        self.systemd_ini_config.read_string(init_ini_file_content)
    
    # 创造或添加一个键值对到nspawn配置中。
    def add_key_value(self, section: str, key: str, value: str):
        parser = self.systemd_ini_config
        if section not in parser.sections():
            parser.add_section(section)
        if key in parser[section]:
            current = parser[section][key]
            if isinstance(current, tuple):
                parser[section][key] = current + (value,) # type: ignore
            else:
                # 将已有的字符串值转换为tuple，再附加新值
                parser[section][key] = (current, value) # type: ignore
        else:
            parser[section][key] = value
    
    # 创造或设置一个键值对的值到nspawn配置中。
    def set_key_value(self, section: str, key: str, value: str):
        parser = self.systemd_ini_config
        if section not in parser.sections():
            parser.add_section(section)
        # 强行覆盖（无论原来是str还是tuple）
        parser[section][key] = value

    def write_to_file(self, file_path: str):
        parser = self.systemd_ini_config
        # 通用writer：不包含任何nspawn特定逻辑
        with open(file_path, "w", encoding="utf-8") as f:
            parser.write(f)
