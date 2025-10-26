import os
import shutil

def copy_all_contents(src_dir: str, dst_dir: str):
    """
    递归复制 src_dir 下的所有文件和文件夹到 dst_dir 中。
    等价于 shell 命令: cp -r src_dir/* dst_dir/

    参数:
        src_dir (str): 源目录路径
        dst_dir (str): 目标目录路径
    """
    if not os.path.isdir(src_dir):
        raise ValueError(f"源路径不是有效的文件夹: {src_dir}")

    os.makedirs(dst_dir, exist_ok=True)

    for entry in os.listdir(src_dir):
        src_path = os.path.join(src_dir, entry)
        dst_path = os.path.join(dst_dir, entry)

        if os.path.isdir(src_path):
            # 递归复制目录
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            # 复制单个文件
            shutil.copy2(src_path, dst_path)