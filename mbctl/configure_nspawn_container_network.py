import ipaddress
import hashlib
import argparse

def calculate_nspawn_container_ipv6_address(prefix: str, container_name: str) -> str:
    """
    计算nspawn容器的IPv6地址。

    :param prefix: IPv6前缀，例如 "2001:db8:1:2::/64"
    :param container_name: 容器名称，例如 "mycontainer"
    :return: IPv6地址字符串，例如 "2001:db8:1:2:abcd:1234:a123:b124"
    """
    # 解析前缀
    network = ipaddress.IPv6Network(prefix, strict=False)
    prefix_len = network.prefixlen
    
    # 把前缀转为整数
    prefix_int = int(network.network_address)
    
    # 计算哈希
    digest = hashlib.sha256(container_name.encode("utf-8")).digest()
    hash_int = int.from_bytes(digest, "big")
    
    # IPv6 是 128 位，剩余位数
    remaining_bits = 128 - prefix_len
    
    # 从哈希中取对应长度的比特
    suffix = hash_int & ((1 << remaining_bits) - 1)
    
    # 拼接完整IPv6整数
    ipv6_int = (prefix_int & (~((1 << remaining_bits) - 1))) | suffix
    
    # 转换回 IPv6 地址
    ipv6_addr = ipaddress.IPv6Address(ipv6_int)
    return str(ipv6_addr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate nspawn container IPv6 address.")
    parser.add_argument("prefix", help="IPv6 prefix, e.g. '2001:db8:1:2::/64'")
    parser.add_argument("container_name", help="Container name, e.g. 'mycontainer'")
    args = parser.parse_args()

    print(calculate_nspawn_container_ipv6_address(args.prefix, args.container_name))