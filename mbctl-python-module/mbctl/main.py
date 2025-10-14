import argparse
import sys
from typing import Optional

from mbctl.utils.man8config import config, ContainerTemplate, ContainerTemplateList
from mbctl.exec.create_nspawn_container_from_oci_url import pull_oci_image_and_create_container
from mbctl.exec.shell_into_nspawn_container import shell_container
from mbctl.exec.container_management import remove_container, remove_cache_dir
from mbctl.exec.get_suffix_address_of_name import print_ipv6_suffix
from mbctl.utils.man8log import logger


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(prog="mbctl", description="mbctl 命令行工具")
	subparsers = parser.add_subparsers(dest="command_group", required=True)

	# machines 分组
	machines = subparsers.add_parser("machines", help="管理机器/容器")
	machines_sub = machines.add_subparsers(dest="machines_cmd", required=True)
	# pull 子命令
	pull = machines_sub.add_parser("pull", help="将镜像拉取到 nspawn 容器")
	pull.add_argument("source", help="镜像来源（例如 docker.io/registry）")
	pull.add_argument("name", help="目标本地容器名称")
	pull.add_argument("--template",type=str,choices=ContainerTemplateList,default="network_isolated",help="容器模板，默认为 network_isolated")
	# shell 子命令
	shell = machines_sub.add_parser("shell", help="进入容器 shell")
	shell.add_argument("name", help="容器名称")
	shell.add_argument("--command", help="替代 shell 的命令", default="/bin/sh")
	# remove 子命令
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

	return parser

def main(argv: Optional[list[str]] = None) -> int:
	if argv is None:
		argv = sys.argv[1:]
	parser = build_parser()
	args = parser.parse_args(argv)

	if args.command_group == "machines":
		if args.machines_cmd == "pull":
			pull_oci_image_and_create_container(args.source, args.name, args.template)
		elif args.machines_cmd == "shell":
			shell_container(args.name, args.command)
		elif args.machines_cmd == "remove":
			remove_container(args.name)
		else:
			parser.print_help()
			return 2
	elif args.command_group == "address":
		if args.address_cmd == "getsuffix":
			print_ipv6_suffix(args.name)
		else:
			parser.print_help()
			return 2
	elif args.command_group == "cache":
		if args.cache_cmd == "clear":
			remove_cache_dir()
		else:
			parser.print_help()
			return 2
	else:
		parser.print_help()
		return 2

	return 0

if __name__ == "__main__":
	sys.exit(main())