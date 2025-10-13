from pathlib import Path
from mbctl.utils.man8config import config
import os


def shell_container(name: str, exec_command: str = "/bin/sh") -> None:
    """在指定的容器中打开一个 shell"""
    script_location = Path(config["lib_root"]) / "utils" / "man8shell.sh"

    os.execvp(str(script_location), [str(script_location), name, exec_command])