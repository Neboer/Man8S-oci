import argparse
import sys
from typing import Optional

from mbctl.utils.man8config import config, ContainerTemplate, ContainerTemplateList
from mbctl.exec.create_nspawn_container_from_oci_url import pull_oci_image_and_create_container
from mbctl.exec.shell_into_nspawn_container import shell_container
from mbctl.exec.container_management import remove_container
from mbctl.exec.get_suffix_address_of_name import print_ipv6_suffix


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(prog="mbctl", description="mbctl (stub) command-line")
	subparsers = parser.add_subparsers(dest="command_group", required=True)

	# machines group
	machines = subparsers.add_parser("machines", help="Manage machines/containers")
	machines_sub = machines.add_subparsers(dest="machines_cmd", required=True)
	# pull
	pull = machines_sub.add_parser("pull", help="Pull image into nspawn container")
	pull.add_argument("source", help="Image source (e.g. docker.io/registry)")
	pull.add_argument("name", help="Target local container name")
	pull.add_argument("--template",type=str,choices=ContainerTemplateList,default="network_isolated",help="容器模板，默认为 network_isolated")
	# shell
	shell = machines_sub.add_parser("shell", help="Open shell in a container")
	shell.add_argument("name", help="Container name")
	shell.add_argument("--command", help="Command to run instead of shell", default="/bin/sh")
	# remove
	remove = machines_sub.add_parser("remove", help="Remove a container")
	remove.add_argument("name", help="Container name to remove")

	# address group
	address = subparsers.add_parser("address", help="Address utilities")
	address_sub = address.add_subparsers(dest="address_cmd", required=True)
	
	getsuf = address_sub.add_parser("getsuffix", help="Get IPv6 suffix for a container name")
	getsuf.add_argument("name", help="Container name to compute suffix for")

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
	else:
		parser.print_help()
		return 2

	return 0

if __name__ == "__main__":
	sys.exit(main())