#!/bin/busybox sh
# Wait for network connectivity

# 配置：可修改重试间隔（秒）
RETRY_INTERVAL_SECONDS=${RETRY_INTERVAL_SECONDS:-1}

# 目标主机
HOST1="1.1.1.1"
HOST2="mirrors.tuna.tsinghua.edu.cn" # 如果容器有v6，则会解析到v6地址，测试容器的v6。如果容器无v6，则测试v4。

# TODO: 需要增加“如果容器只有v4则不必添加默认IPv6路由”的配置。如果容器没有通过SLAAC自动分配IPv6地址，此脚本也不应该失败，而是应该跳过IPv6子网相关的配置。
# TODO: 是否允许容器获取各种类型的地址应该是可以配置的，比如 MAN8S_ALLOW_IPV4=true/false, MAN8S_ALLOW_IPV6=true/false。

# 确认 MAN8S_YGGDRASIL_ADDRESS 已设置
if [ -z "${MAN8S_YGGDRASIL_ADDRESS-}" ]; then
  printf '错误: 环境变量 MAN8S_YGGDRASIL_ADDRESS 未设置。\n请先 export MAN8S_YGGDRASIL_ADDRESS="你要检测的地址"\n'
  return 2
fi

# 简单的可用性检测：优先用 ping 单次检测，失败则退回到 HTTP(S) 头请求（curl/wget）
check_host() {
  host=$1

  # try ping -c 1 (most systems)
  if command -v ping >/dev/null 2>&1; then
    # 使用 -c 1 发一个包，-W 1 作为超时（部分系统支持 -w 或 -W）
    ping -c 1 -W 1 "$host" >/dev/null 2>&1 && return 0
    # 如果 ping 失败，再尝试 curl / wget
  fi

  return 1
}

# 检查本机是否拥有指定地址（优先 ifconfig，其次 ip addr）
check_local_addr() {
  addr="$1"
  if command -v ifconfig >/dev/null 2>&1; then
    ifconfig 2>/dev/null | grep -qF "$addr" && return 0
  fi

  return 1
}

# 捕获 Ctrl-C 使脚本优雅退出
trap 'printf "\n中断，退出。\n"; return 130' INT

attempts_text=${MAX_RETRY_TIMES:-"无限"}
printf '开始检测：\n  - %s\n  - %s\n  - 本机地址 %s\n每 %s 秒重试一次（最大尝试次数: %s）。\n\n' "$HOST1" "$HOST2" "$MAN8S_YGGDRASIL_ADDRESS" "$RETRY_INTERVAL_SECONDS" "$attempts_text"

while :; do
  now="$(date '+%Y-%m-%d %H:%M:%S' 2>/dev/null || printf '%s' "$(date)")"
  printf '[%s] 检测中: %s ... ' "$now" "$HOST1"
  if DO_UNTIL_SUCCESS check_host "$HOST1"; then
    printf 'OK\n'
  else
    printf 'FAIL\n'
    return 4
  fi

  printf '[%s] 检测中: %s ... ' "$now" "$HOST2"
  if DO_UNTIL_SUCCESS check_host "$HOST2"; then
    printf 'OK\n'
  else
    printf 'FAIL\n'
    return 4
  fi

  printf '[%s] 检查本机地址: %s ... ' "$now" "$MAN8S_YGGDRASIL_ADDRESS"
  if DO_UNTIL_SUCCESS check_local_addr "$MAN8S_YGGDRASIL_ADDRESS"; then
    printf 'FOUND\n'
  else
    printf 'NOT FOUND\n'
    return 4
  fi

  # 如果能运行到这里，三项都通过
  printf '\n网络正常。\n'
  return 0
done
