from json import load, dump

normal_env_keys = ["PATH", "TERM", "HOME", "LANG"]


class OCIConfig:
    def __init__(self, config_json_path: str):
        with open(config_json_path, "r", encoding="utf-8") as f:
            self.config_data = load(f)

    def get_process_args(self) -> list[str]:
        return self.config_data.get("process", {}).get("args", [])

    def get_process_all_envs(self) -> dict[str, str]:
        env_strs = self.config_data.get("process", {}).get("env", [])
        return {env.split("=", 1)[0]: env.split("=", 1)[1] for env in env_strs}

    # 过滤掉一些常见的环境变量，只返回额外设置的环境变量，这些环境变量通常是软件配置的一部分。有很多docker容器直接使用这些环境变量来传递配置，甚至不需要配置文件。
    def get_process_extra_envs(self) -> dict:
        all_envs = self.get_process_all_envs()
        return {e:all_envs[e] for e in all_envs if e not in normal_env_keys}
    
    # 只返回常用环境变量的值。
    def get_process_normal_envs(self) -> dict:
        all_envs = self.get_process_all_envs()
        return {e:all_envs[e] for e in all_envs if e in normal_env_keys}

    def get_process_cwd(self) -> str:
        return self.config_data.get("process", {}).get("cwd", "/")

    def get_all_mounts(self) -> list[dict]:
        return self.config_data.get("mounts", [])

    # mounts会返回一个很大的列表，里面有类似dev/proc之类的，这些挂载通常是通用的，并且在nspawn配置中不需要重复指定
    # 在这里我们只取只有“"source": "none"”的那些挂载点，因为这些通常是特殊的挂载点，通常代表docker的volume挂载
    # 注意我们这个函数只返回字符串的单个需要挂载的路径，不是完整的mount对象
    def get_useful_mount_paths(self) -> list[str]:
        mounts = self.get_all_mounts()
        useful_mounts = []
        for mount in mounts:
            if mount.get("source") == "none":
                useful_mounts.append(mount["destination"])
        return useful_mounts

    def write_to_file(self, file_path: str):
        with open(file_path, "w", encoding="utf-8") as f:
            dump(self.config_data, f, indent=4, ensure_ascii=False)
