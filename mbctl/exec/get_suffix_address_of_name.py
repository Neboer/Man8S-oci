from mbctl.init_system.configure_nspawn_container_network import calculate_nspawn_container_ipv6_address

def print_ipv6_suffix(name: str) -> None:
    """
    打印指定容器名称的IPv6后缀。

    :param name: 容器名称
    """
    # 这里使用一个示例前缀，可以根据需要修改
    blank_prefix = "::/64"
    suffix_address = calculate_nspawn_container_ipv6_address(blank_prefix, name)
    print(f"容器名字: {name}")
    print(f"IPv6 后缀地址: {suffix_address}")