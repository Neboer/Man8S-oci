# 配置文件
from typing import Literal, TypedDict


class Man8Config(TypedDict):
    man8machines_path: str
    system_machines_path: str
    proxy_server: str
    nspawn_file_path: str
    temp_dir: str
    host_busybox_path: str


config = Man8Config(
    man8machines_path="/var/lib/man8machines",
    system_machines_path="/var/lib/machines",
    proxy_server="",
    nspawn_file_path="/etc/systemd/nspawn",
    temp_dir="/var/tmp/man8s",
    host_busybox_path="/bin/busybox",
)

ContainerTemplate = Literal["network_isolated"]
ContainerTemplateList = ["network_isolated"]
