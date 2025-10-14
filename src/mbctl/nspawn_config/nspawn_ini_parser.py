# nspawn 文件是有重复键值的 ini 文件。它的重复键值只针对 Environment 字段，因此可以被特殊处理。

import configparser
import io


class NspawnConfigParser(configparser.ConfigParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.environment_key_count = 0  # 用于跟踪 Environment 键的数量
        self.optionxform = str  # pyright: ignore[reportAttributeAccessIssue]

    def read_nspawn_config_string(self, nspawn_config_content: str):
        """从给定字符串中读取配置。

        将原始字符串中的 Environment= 字段重命名为 Environment1=, Environment2= 等，
        以便 ConfigParser 能够处理多个同名键。
        """
        splited_string = nspawn_config_content.splitlines()
        self.environment_key_count = 0
        for i, line in enumerate(splited_string):
            if line.strip().startswith("Environment="):
                self.environment_key_count += 1
                splited_string[i] = (
                    f"Environment{self.environment_key_count}=" + line.split("=", 1)[1]
                )

        sfile = io.StringIO("\n".join(splited_string))
        self.read_file(sfile)

    def add_exec_environment(self, env_key, env_value):
        """向 Exec 段添加一个环境变量（以键/值形式）。"""
        env_string = f"{env_key}={env_value}"
        self.add_exec_environment_string(env_string)

    def add_exec_environment_string(self, env_string):
        """从字符串添加一个环境变量（格式 'KEY=VALUE'）。"""
        self["Exec"][f"Environment{self.environment_key_count}"] = env_string
        self.environment_key_count += 1

    def write_nspawn_config(self, fp, space_around_delimiters=True):
        """将配置写入类文件对象。

        在写入时，将 Environment1, Environment2 等键还原为重复的 Environment 字段：
        输出为 Environment = "KEY=VALUE" 的形式，匹配 nspawn 所期望的格式。
        """
        output = io.StringIO()
        self.write(output, space_around_delimiters)
        content = output.getvalue()

        # 将 Environment1, Environment2 等还原为 Environment
        splited_content = content.splitlines()
        for i, line in enumerate(splited_content):
            if line.strip().startswith("Environment"):
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if (
                    key.startswith("Environment")
                    and key[len("Environment") :].isdigit()
                ):
                    splited_content[i] = f'Environment = "{value}"'

        fp.write("\n".join(splited_content))
