import argparse
import sys
from typing import Optional
import logging

from mbctl import __version__
from mbctl.utils.man8config import config, ContainerTemplate, ContainerTemplateList
from mbctl.exec.create_nspawn_container_from_oci_url import (
    pull_oci_image_and_create_container,
)
from mbctl.exec.shell_into_nspawn_container import shell_container
from mbctl.exec.remove_container import remove_container, clear_cache_dir
from mbctl.exec.get_suffix_address_of_name import print_ipv6_suffix
from mbctl.utils.man8log import logger
from mbctl.get_bundle.get_oci import fetch_oci_to_rootfs
from mbctl.init_system.man8s_add_initsystem import install_init_system_to_machine
from mbctl.config_formats.man8s_config import Man8SContainerInfo
from mbctl.exec.recreate_man8s_container_rootfs import (
    recreate_man8s_container_rootfs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mbctl", description="mbctl 命令行工具")
    # Add global verbose flag to enable debug logging
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable verbose debug logging"
    )
    subparsers = parser.add_subparsers(dest="command_group", required=True)

    # machines 分组
    machines = subparsers.add_parser("machines", help="管理机器/容器")
    machines_sub = machines.add_subparsers(dest="machines_cmd", required=True)
    ## pull 子命令
    pull = machines_sub.add_parser("pull", help="将镜像拉取到 nspawn 容器")
    pull.add_argument("source", help="镜像来源（例如 docker.io/registry）")
    pull.add_argument("name", help="目标本地容器名称")
    pull.add_argument(
        "--template",
        type=str,
        choices=ContainerTemplateList,
        default="netns-noinit",
        help="容器模板，默认为 netns-noinit",
    )
    ## renew 子命令
    renew = machines_sub.add_parser("renew", help="重新创建容器的 rootfs（升级容器）")
    renew.add_argument("name", help="容器名称")
    ## shell 子命令
    shell = machines_sub.add_parser("shell", help="进入容器 shell")
    shell.add_argument("name", help="容器名称")
    shell.add_argument("all_command", nargs=argparse.REMAINDER)
    ## remove 子命令
    remove = machines_sub.add_parser("remove", help="删除容器")
    remove.add_argument("name", help="要删除的容器名称")

    # address 分组
    address = subparsers.add_parser("address", help="地址工具")
    address_sub = address.add_subparsers(dest="address_cmd", required=True)

    getsuf = address_sub.add_parser("getsuffix", help="获取容器名称的 IPv6 后缀")
    getsuf.add_argument("name", help="要计算后缀的容器名称")

    # cache 分组
    cache = subparsers.add_parser("cache", help="缓存工具")
    cache_sub = cache.add_subparsers(dest="cache_cmd", required=True)
    # 清理缓存目录
    cleancache = cache_sub.add_parser("clear", help="清理临时缓存目录")
    # 添加顶层 version 子命令用于显示版本
    version = subparsers.add_parser("version", help="显示 mbctl 版本")

    # oci 分组
    oci = subparsers.add_parser("oci", help="OCI 工具")
    oci_sub = oci.add_subparsers(dest="oci_cmd", required=True)
    ## fetch 子命令
    download = oci_sub.add_parser("download", help="将 OCI 镜像拉取到根文件系统")
    download.add_argument("source", help="镜像来源（例如 docker.io/registry）")
    download.add_argument(
        "local_path", help="目标本地容器路径（例如 ~/test_container）"
    )
    ## man8init 子命令
    man8init = oci_sub.add_parser(
        "man8init", help="向指定路径安装 Man8S init 系统（覆盖安装）"
    )
    man8init.add_argument("machine_path", help="目标机器路径（例如 ~/test_container）")

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    # Enable debug logging when verbose flag is provided
    if getattr(args, "verbose", False):
        # set root logger and module logger to DEBUG
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    elif args.command_group == "machines":
        if args.machines_cmd == "pull":
            pull_oci_image_and_create_container(args.source, args.name, args.template)
        elif args.machines_cmd == "shell":
            # 如果没有传入命令，则传入空列表，正好触发默认 shell 行为
            shell_container(args.name, args.all_command)
        elif args.machines_cmd == "remove":
            remove_container(args.name)
        elif args.machines_cmd == "renew":
            man8s_container_info = Man8SContainerInfo.from_env_file_of_container(args.name)
            recreate_man8s_container_rootfs(man8s_container_info)

    elif args.command_group == "address":
        if args.address_cmd == "getsuffix":
            print_ipv6_suffix(args.name)

    elif args.command_group == "cache":
        if args.cache_cmd == "clear":
            clear_cache_dir()

    elif args.command_group == "version":
        print(f"mbctl 版本：{__version__}")

    elif args.command_group == "oci":
        if args.oci_cmd == "download":
            fetch_oci_to_rootfs(args.source, args.local_path)
        elif args.oci_cmd == "man8init":
            install_init_system_to_machine(args.machine_path)

    else:
        parser.print_help()
        return 2
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
