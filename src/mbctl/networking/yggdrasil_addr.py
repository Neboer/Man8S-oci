import argparse
from .string_to_v6suffix import string_to_v6suffix


# return addr, subnet
def get_host_yggdrasil_address_and_subnet() -> tuple[str, str]:
    """
    获取宿主机的 Yggdrasil IPv6 地址。
    假设宿主机已经配置并运行了 Yggdrasil。
    """
    import subprocess
    result = subprocess.run(["yggdrasilctl", "getself"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("无法获取 Yggdrasil 地址，请确保 Yggdrasil 已正确安装和运行。")
    ygg_info = {line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip() for line in result.stdout.splitlines()}
    return ygg_info["IPv6 address"], ygg_info["IPv6 subnet"]

def string_to_host_ygg_subnet_v6addr(src_str: str) -> str:
    """
    计算宿主机的 Yggdrasil IPv6 地址。
    假设宿主机已经配置并运行了 Yggdrasil。
    """
    ygg_address, ygg_subnet = get_host_yggdrasil_address_and_subnet()
    return string_to_v6suffix(ygg_subnet, src_str)

def main():
    parser = argparse.ArgumentParser(description="Calculate nspawn container IPv6 address.")
    parser.add_argument("prefix", help="IPv6 前缀, e.g. '2001:db8:1:2::/64'")
    parser.add_argument("container_name", help="容器名称, e.g. 'mycontainer'")
    args = parser.parse_args()

    print(string_to_v6suffix(args.prefix, args.container_name))

if __name__ == "__main__":
    main()