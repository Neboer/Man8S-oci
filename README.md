# Man8S-OCI-tool

Man8S OCI工具，命令行工具为 mbctl 。

一种基于systemd-nspawn实现的、支持网络隔离和现代网络栈的容器运行时方案，兼容OCI与Docker。

## 安装方法

Man8S环境有所变化，在安装此软件之前，需要做一切必要的准备。

在archlinux中安装如下软件：
```bash
pacman -S python yggdrasil skopeo umoci busybox python-pip
```

本软件不只有一个独立的可执行程序，它需要配合其他模块一起工作。本软件的依赖及配置方法如下：

1. 基础环境: systemd-networkd，nspawn，python，python-pip，注意pip需要换源。
2. 安装软件：skopeo、umoci
3. yggdrasil安装并配置
4. 将systemd-configs文件夹中的.network/netdev文件安装到systemd-networkd配置中
5. 然后编辑.network文件，将容器的300开头的、带/64的子网其中一个地址分配给网桥（如srvgrp0），比如 `Address=300:2e98:a4b0:1789::1/64`，networkctl重启网络。
6. 安装必需依赖：busybox 二进制可执行文件（静态链接）到 /usr/bin/busybox

其中，本软件会自动将mbctl工具安装进系统中，以上步骤需要自己配置。

## 使用方法

本工具的主要用法就是mbctl。

- 拉取镜像到本地 nspawn 容器：
    ```bash
    mbctl machines pull docker.io/registry:latest Man8Registry
    ```

- 进入容器 shell：
    ```bash
    mbctl machines shell Man8Registry
    ```

- 删除一个容器：
    ```bash
    mbctl machines remove Man8Registry
    ```
    注意：不要删除运行中的容器。

- 计算容器名字的IPv6后缀：
    ```bash
    mbctl address getsuffix SomeFutureMachineName
    ```

## 镜像配置

在拉取指定的容器之后，修改对应的nspawn文件即可。

```ini
[Exec]
Boot = no
ProcessTwo = yes
Parameters = /sbin/busybox-init.sh
ResolvConf = copy-stub
Timezone = copy
LinkJournal = no
PrivateUsers = pick
WorkingDirectory = /
Environment = "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment = "TERM=xterm"
Environment = "HOME=/root"
Environment = "MAN8S_APPLICATION_ARGS=/bin/sh"
Environment = "MAN8S_YGGDRASIL_ADDRESS=300:xxx:xxx:xxx:fb2:bb91:2f33:ad7e"

[Network]
VirtualEthernet = yes
Bridge = srvgrp0

[Files]
PrivateUsersOwnership = map
```

nspawn 配置中的 MAN8S_APPLICATION_ARGS 是实际需要执行的命令，MAN8S_YGGDRASIL_ADDRESS 是容器自动计算出的固定yggdrasil内网ipv6地址。前缀与网桥相同。

## 工作原理

mbctl 使用 docker、busybox 作为依赖。

### Man8S 固定ygg内网IPv6地址

Man8S的内网地址分为两种：
- 动态DHCP/SLAAC分配IPv4/IPv6地址
- 由容器名哈希与主机前缀静态配置的ygg 300:: 地址

其中前者用于容器网络访问，后者用于容器互联。容器中的软件监听在ygg地址上，可以从内网地址访问该容器。

### Man8S busybox init

安装init系统的方法：

man8lize-container.sh 

init过程总体分如下几步：

必须设置的环境变量：
- MAN8S_APPLICATION_ARGS ：实际容器中需要执行的启动命令
- MAN8S_YGGDRASIL_ADDRESS ：容器yggdrasil的地址，注意迁移容器之后迁移配置时需要将此配置也一并。

init步骤如下：
1. /sbin/busybox-init.sh
2. /sbin/busybox-autoconfig-networking.sh
3. /sbin/yggdrasil-config-ipaddr.sh
4. /sbin/application.sh

## 开发计划

- 创建容器
- 删除容器