# 将man8s拉下来的镜像做一些后处理，便于nspawn使用
import os
import shutil


# 由于 nspawn 强制要求将容器的 /run 和 /tmp 目录挂载为 tmpfs，所以我们要保护容器中已有的这些目录，man8s-init 系统会在容器启动的时候将这些被保护的目录里的内容拷贝到 tmpfs 中去。
def oci_convert_protect_dirs(rootfs_path: str) -> list[str]:
    protected_dirs = ["/run", "/tmp"]
    successful_copied_dirs = []
    for dir in protected_dirs:
        dir_path = os.path.join(rootfs_path, dir.lstrip("/"))
        if os.path.exists(dir_path):
            protected_path = dir_path + ".man8sprotected"
            shutil.move(dir_path, protected_path)
            os.makedirs(dir_path, exist_ok=True)
            successful_copied_dirs.append(dir)
    return successful_copied_dirs
