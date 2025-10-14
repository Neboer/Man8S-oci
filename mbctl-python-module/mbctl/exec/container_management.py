import shutil
import os
from pathlib import Path

from mbctl.utils.man8log import logger
from mbctl.utils.man8config import config, ContainerTemplate, ContainerTemplateList


def check_and_delete(target: str) -> bool:
    """检查路径是否存在，如果存在则删除，返回是否删除成功"""

    if os.path.lexists(target):
        try:
            if os.path.isdir(target) and not os.path.islink(target):
                shutil.rmtree(target)
                logger.info(f"Existing directory '{target}' removed.")
            else:
                os.remove(target)
                logger.info(f"Existing file or symlink '{target}' removed.")
            return True
        except Exception as e:
            logger.error(f"Error removing '{target}': {e}")
            return False
    return True


def remove_container(name: str) -> None:
    """删除指定的容器"""
    container_lib_root = Path(config["man8machines_path"]) / name
    container_system_root = Path(config["system_machines_path"]) / name
    container_nspawn_file = Path(config["nspawn_file_path"]) / f"{name}.nspawn"

    targets = [
        ("库目录", container_lib_root),
        ("系统目录", container_system_root),
        ("nspawn 文件", container_nspawn_file),
    ]

    existing = [(desc, p) for desc, p in targets if os.path.lexists(str(p))]
    if not existing:
        logger.error(f"容器 '{name}' 不存在。")
        return

    deleted = []
    for desc, p in existing:
        if check_and_delete(str(p)):
            deleted.append(desc)

    if deleted:
        logger.info(f"容器 '{name}' 已删除: {', '.join(deleted)}。")


def remove_cache_dir() -> None:
    """删除临时缓存目录"""
    temp_dir = config["temp_dir"]
    if check_and_delete(temp_dir):
        logger.info(f"临时缓存目录 '{temp_dir}' 已删除或不存在。")
    else:
        logger.error(f"无法删除临时缓存目录 '{temp_dir}'。")