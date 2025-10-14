from pathlib import Path
import os

from mbctl.utils.man8config import config
from mbctl.utils.resources import copy_resdir_file_to_target_file


def shell_container(name: str, exec_command: str = "/bin/sh") -> None:
    """在指定的容器中打开一个 shell"""

    # 生成一个临时文件
    script_location = "/tmp/man8shell.sh"
    copy_resdir_file_to_target_file("mbctl.resources.utils", "man8shell.sh", script_location)
    os.execvp("/bin/bash", ["/bin/bash", script_location, name, exec_command])
