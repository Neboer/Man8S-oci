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
    如果容器定义了挂载点，mbctl会询问你是否将此挂载点挂载到某个目标。

- 进入容器 shell：
    ```bash
    mbctl machines shell Man8Registry
    ```

- 删除一个容器：
    ```bash
    mbctl machines remove Man8Registry
    ```
    注意：不做运行时检查，不要删除运行中的容器

- 下载一个容器为rootfs:
    ```bash
    mbctl oci download docker.io/registry:latest
    ```

- 计算容器名字的IPv6后缀：
    ```bash
    mbctl address getsuffix SomeFutureMachineName
    ```

- 在命令行中主动前台启动一个容器:
    ```
    systemd-nspawn -M Man8Registry -D /var/lib/man8machines/Man8Registry
    ```
    这个会利用现有的配置启动容器。
    如果在前面加上 `SYSTEMD_LOG_LEVEL=debug` 则会启动debug模式，会输出一些debug日志。


## 镜像配置

在拉取指定的容器之后，修改对应的nspawn文件和配置文件即可。

nspawn 配置，这里定义的环境变量都是一些无关紧要的环境变量，一般不会也不需要改变的，不会成为配置文件的一部分的。
所有的容器配置都应该放在 /var/lib/man8machine_configs 中，用这些配置就应该可以重建容器本身。
注意由于idmap，因此容器每次重启之后都会保留之前的旧数据。软件暂时还没有容器状态还原的功能，未来可以考虑借助btrfs的优势实现快照。
```ini
[Exec]
Boot=no
ProcessTwo=yes
Parameters=/sbin/busybox-init.sh
ResolvConf=copy-stub
Timezone=copy
LinkJournal=no
PrivateUsers=pick
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="TERM=xterm"
Environment="HOME=/root"
WorkingDirectory=/app

[Network]
VirtualEthernet=yes
Bridge=srvgrp0

[Files]
PrivateUsersOwnership=map
Bind=/var/lib/man8machine_configs/TestBWContainer3/man8env.env:/man8env.env:idmap
Bind=/var/lib/man8machine_configs/TestBWContainer3/etc/bitwarden:/etc/bitwarden:idmap
```

man8env.env 这是配置文件的一部分，用来定义容器环境变量。Docker容器的运行大都依赖环境变量传入，因此man8s中环境变量文件也是配置文件的一部分。
```bash
MAN8S_CONTAINER_NAME=TestBWContainer3
MAN8S_CONTAINER_TEMPLATE=network_isolated
MAN8S_YGGDRASIL_ADDRESS=300:2e98:a4b0:1789:1d44:bc13:a177:c4d
MAN8S_OCI_IMAGE_URL=ghcr.io/bitwarden/self-host:latest
MAN8S_APPLICATION_ARGS=/entrypoint.sh
APP_UID=1654
ASPNETCORE_HTTP_PORTS=8080
DOTNET_RUNNING_IN_CONTAINER=true
DOTNET_VERSION=8.0.13
ASPNET_VERSION=8.0.13
ASPNETCORE_ENVIRONMENT=Production
BW_ENABLE_ADMIN=true
BW_ENABLE_API=true
BW_ENABLE_EVENTS=false
BW_ENABLE_ICONS=true
BW_ENABLE_IDENTITY=true
BW_ENABLE_NOTIFICATIONS=true
BW_ENABLE_SCIM=false
BW_ENABLE_SSO=false
BW_DB_FILE=/etc/bitwarden/vault.db
DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=false
globalSettings__selfHosted=true
globalSettings__unifiedDeployment=true
globalSettings__pushRelayBaseUri=https://push.bitwarden.com
globalSettings__baseServiceUri__internalAdmin=http://localhost:5000
globalSettings__baseServiceUri__internalApi=http://localhost:5001
globalSettings__baseServiceUri__internalEvents=http://localhost:5003
globalSettings__baseServiceUri__internalIcons=http://localhost:5004
globalSettings__baseServiceUri__internalIdentity=http://localhost:5005
globalSettings__baseServiceUri__internalNotifications=http://localhost:5006
globalSettings__baseServiceUri__internalSso=http://localhost:5007
globalSettings__baseServiceUri__internalScim=http://localhost:5002
globalSettings__baseServiceUri__internalVault=http://localhost:8080
globalSettings__identityServer__certificatePassword=default_cert_password
globalSettings__dataProtection__directory=/etc/bitwarden/data-protection
globalSettings__attachment__baseDirectory=/etc/bitwarden/attachments
globalSettings__send__baseDirectory=/etc/bitwarden/attachments/send
globalSettings__licenseDirectory=/etc/bitwarden/licenses
globalSettings__logDirectoryByProject=false
globalSettings__logRollBySizeLimit=1073741824
```

MAN8S_APPLICATION_ARGS 是实际需要执行的命令（实际是一个需要传递给sh解析的字符串），注意整个env文件使用特殊的方式加载，并不是简单的source，因此用=可以很好的分隔字符串，不需要担心空格、双引号等escaping的问题。MAN8S_YGGDRASIL_ADDRESS 是容器自动计算出的固定yggdrasil内网ipv6地址。前缀与网桥相同。

如果指定了新的配置文件或数据文件路径，需要在nspawn文件中的Files.Bind配置中指出。

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
1. /sbin/busybox-init.sh
2. /sbin/busybox-execute.sh
3. /sbin/busybox-copy-protected-dirs.sh
4. /sbin/busybox-load-envs.sh
5. /sbin/busybox-autoconfig-networking.sh
6. /sbin/yggdrasil-config-ipaddr.sh
7. /sbin/application.sh

## 开发计划

- 测试更多容器
- 当容器软件不监听IPv6时怎么办
- 将拉取的镜像缓存
- 将密码等不应该公开写进配置文件中的配置放进秘密存储中单独存放。
- 支持更多类型的容器，比如macvlan隔离的容器。
