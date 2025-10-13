import shutil
import os
from pathlib import Path

from mbctl.utils.man8config import config, ContainerTemplate, ContainerTemplateList


def check_and_delete(target_dir: str) -> bool:
    """检查路径是否存在，如果存在则删除，返回是否删除成功"""

    if os.path.exists(target_dir):
        try:
            shutil.rmtree(target_dir)
            print(f"Existing directory '{target_dir}' removed.")
            return True
        except Exception as e:
            print(f"Error removing directory '{target_dir}': {e}")
            return False
    return True


def remove_container(name: str) -> None:
    """删除指定的容器"""
    container_lib_root = Path(config["man8machines_path"]) / name
    container_system_root = Path(config["system_machines_path"]) / name
    container_nspawn_file = Path(config["nspawn_file_path"]) / f"{name}.nspawn"

    for target_path in [
        container_lib_root,
        container_system_root,
        container_nspawn_file,
    ]:
        target_path_str = str(target_path)
        check_and_delete(target_path_str)
