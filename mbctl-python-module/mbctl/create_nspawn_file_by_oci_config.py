#!/bin/bash -e
# 从解包好的oci容器（带config.json配置）创建一个machinectl下的nspawn容器。
# rootfs的存储路径是 /var/lib/man8machines/<container_name>
from json import load
from typing import TypedDict, List, Dict, Any
import argparse

from .man8config import config
from .nspawn_ini_parser import NspawnConfigParser

class nspawnconfig(TypedDict):
    process: Dict[str, Any]  # 包含 user, args, env, cwd 等


def get_oci_config(oci_config_file: str) -> nspawnconfig:
    """从oci的config.json中获取启动命令及相关配置"""
    with open(oci_config_file, "r", encoding="utf-8") as f:
        oci_config = load(f)
    return oci_config  # 返回整个配置，包含 process 字段

def create_nspawn_config_by_oci_config(oci_config: nspawnconfig, nspawn_example_file_path: str, nspawn_yggdrasil_dir: str) -> NspawnConfigParser:
    nspawn_config = NspawnConfigParser()
    with open(nspawn_example_file_path, "r", encoding="utf-8") as f:
        nspawn_config.read_nspawn_config_string(f.read(), nspawn_example_file_path)

    nspawn_config["Exec"]["Parameters"] = "/sbin/busybox-init.sh" # 使用自定义的init脚本
    nspawn_config["Exec"]["WorkingDirectory"] = oci_config["process"].get("cwd", "/")
    for env_string in oci_config["process"].get("env", []):
        nspawn_config.add_exec_environment_string(env_string)
    nspawn_config.add_exec_environment("MAN8S_APPLICATION_ARGS", " ".join(oci_config["process"].get("args", [])))
    nspawn_config.add_exec_environment("MAN8S_YGGDRASIL_ADDRESS", nspawn_yggdrasil_dir)
    return nspawn_config

def main():
    parser = argparse.ArgumentParser(
        description="根据OCI config.json和nspawn参考配置生成nspawn配置文件"
    )
    parser.add_argument(
        "--oci-config",
        required=True,
        help="OCI config.json 文件路径"
    )
    parser.add_argument(
        "--nspawn-example",
        required=True,
        help="nspawn参考配置文件路径"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="输出nspawn配置文件路径"
    )
    args = parser.parse_args()

    oci_config = get_oci_config(args.oci_config)
    nspawn_config = create_nspawn_config_by_oci_config(oci_config, args.nspawn_example, "")

    with open(args.output, "w", encoding="utf-8") as f:
        nspawn_config.write_nspawn_config(f)

if __name__ == "__main__":
    main()
