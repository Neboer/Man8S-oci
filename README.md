# Man8S-OCI-tool

Man8S OCI工具，命令行工具为 mbctl 。

一种基于systemd-nspawn实现的、支持网络隔离和现代网络栈的容器运行时方案及配套技术规范，兼容OCI与Docker。

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

mbctl 支持 debug 输出，使用 `mbctl -v` 即可打开debug log，如 `mbctl -v machines pull docker.io/registry:latest Man8Registry`

- 拉取镜像到本地 nspawn 容器：

    ```bash
    mbctl machines pull docker.io/registry:latest Man8Registry
    ```

    如果容器定义了挂载点，mbctl会询问你是否将此挂载点挂载到某个目标。这个命令必须作用于本地完全没有安装过的容器，如果有配置文件等文件夹则会报错退出。

- 进入容器 shell：

    ```bash
    mbctl machines shell Man8Registry
    ```

    此命令目前支持进入容器完整namespace环境以及只进入容器网络环境。

    ```bash
    sudo mbctl machines shell Man8Registry --network-only -- /usr/bin/iperf3 -s
    ```

    用这个方法可以在容器的网络名字空间中执行主机的`iperf3 -s`命令，非常方便。

- 删除一个容器：

    ```bash
    mbctl machines remove Man8Registry
    ```

    删除容器时会检查容器是否在运行，然后彻底清除容器的所有内容（包括数据与配置文件夹）

- 下载一个容器为rootfs:

    ```bash
    mbctl oci download docker.io/registry:latest /var/lib/man8machine
    ```

    这个命令不会将man8s-init系统安装到容器中。

- 为路径下的rootfs容器安装man8s init系统

    ```bash
    mbctl oci man8init /var/lib/man8machine
    ```

    如果路径中已经有man8init系统，则会强制覆盖。注意此命令还是不会检测容器是否在运行。

- 计算容器名字的IPv6后缀：

    ```bash
    mbctl address getsuffix SomeFutureMachineName
    ```

- 在命令行中主动前台启动一个容器:

    ```bash
    systemd-nspawn -M Man8Registry -D /var/lib/man8machines/Man8Registry
    ```

    这个会利用现有的配置启动容器。
    如果在前面加上 `SYSTEMD_LOG_LEVEL=debug` 则会启动debug模式，会输出一些debug日志。

## 镜像配置

在拉取指定的容器之后，修改对应的nspawn文件和配置文件即可。

nspawn 配置，这里定义的环境变量都是一些无关紧要的环境变量，一般不会也不需要改变的，不会成为配置文件的一部分的。
所有的容器配置都应该放在 `/var/lib/man8machine_configs` 中，用这些配置就应该可以重建容器本身。
注意由于idmap，因此容器每次重启之后都会保留之前的旧数据。软件暂时还没有容器状态还原的功能，未来可以考虑借助btrfs的优势实现快照。
nspawn配置也放在 `/var/lib/man8machine_configs/container.nspawn` 中，留出一个符号链接指向 `/etc/systemd/nspawn/<container_name>.nspawn`

```ini
[Exec]
Boot=no
ProcessTwo=yes
Parameters=/man8s-init/00-init.sh.sh
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
MAN8S_CONTAINER_TEMPLATE=netns-init
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

### Man8S 网络配置

Man8S的内网地址分为两种：

- 动态DHCP/SLAAC分配IPv4/IPv6地址
- 由容器名哈希与主机前缀静态配置的ygg 300:: 地址

其中前者用于容器网络访问，后者用于容器互联。容器中的软件监听在ygg地址上，可以从内网地址访问该容器。

1. ygg (前缀 300:0:0:1::/64)：路由表编号199，优先匹配
    - 直连 300:0:0:1::/64 的流量直接通过 host0（链路/邻居发现）。
    - 仅 200::/7 范围的目标通过网关 300:0:0:1::1（实际为ipv6下的内网网关的本地地址） 发出，且源地址指定为 300:0:0:1::100（可以NAT也可以不NAT，不NAT节约性能）。
2. IPv6 ULA (前缀 fc00::/64)：路由表编号main，最后匹配
    - 直连 fc00::/64 的流量直接通过 host0 链路。
    - 其他（default）流量通过 ULA 网关 fc00::f:e:d:c 发出（和上述网关相同），且源地址指定为 fc00::a:b:c:d。（需要和v4一起NAT，否则无法正常访问IPv6互联网）

### Man8S init

容器启动前需要做一些准备工作，配置好自己的环境变量和网络地址，并确保所有的网络地址和环境变量正确配置，才能正式启动应用。

init过程总体分如下几步：

1. 加载helper函数
2. 加载环境变量配置
3. 将受保护的文件夹中的内容拷贝到/tmp等文件夹下
4. 网络1：DHCP客户端，设置自身的IPv4网络
5. 网络2：等待自身IPv6网络完成配置，并配置yggdrasil网络叠加路由表
6. 网络3：检查IPv4、IPv6、域名解析、ygg地址是否正确
7. 启动应用

## 开发计划

- 测试更多容器
- 当容器软件不监听IPv6时怎么办
- 将拉取的镜像缓存
- 将密码等不应该公开写进配置文件中的配置放进秘密存储中单独存放。
- 支持更多类型的容器，比如macvlan隔离的容器。
- 支持在仅IPv4公网的主机环境中部署（不强制检测IPv6）

## initsystem in docker

大多数docker容器都有自己的initsystem，比如 [tini](https://github.com/krallin/tini)、[dumb-init](https://github.com/Yelp/dumb-init)、[s6-overlay](https://github.com/just-containers/s6-overlay)、systemd、[pid1](https://github.com/fpco/pid1) 等等。这些init系统的行为各异，对 SIGKILL 与 SIGTERM 信号的响应方法也存在差异。目前 Man8S 统一使用PID2的方式管理这些容器，对其中的 init 系统并不公平，甚至 s6-overlay 的作者公开表示自己不会允许自己的软件运行在非PID1的环境中。我理解这些作者的想法，也清晰的知道Linux的容器化就是一个巨大的问题——Man8S不就是为了解决这个问题的吗对吧？所以我们会努力的支持所有的init系统，实现良好的Linux容器管理解决方案。

鉴于docker容器实际执行的init程序与信号管理相关的问题，为了更加的规范、标准化这个过程，我决定使用SIGTERM作为容器的终止信号。但如果进程本身不是合格的PID1，使用此方法可能导致僵尸进程出现，所以还是需要使用systemd提供的stub init的。这个过程应该由用户自行判断（而不应该让Man8S判断，Man8S总是推荐使用默认配置），具体的配法的区别如下：

1. 类Unix配置（假设容器使用合格的、非systemd系列的init）

    ```ini
    ProcessTwo=no
    KillSignal=SIGTERM
    ```

2. 接管配置（容器使用不合格的init）

    ```ini
    [Exec]
    ProcessTwo=yes
    KillSignal=SIGRTMIN+3
    ```

3. systemd配置（容器使用systemd作为init）

    ```ini
    ProcessTwo=no
    KillSignal=SIGRTMIN+3
    ```

可以看到这非常混乱。我建议Man8S应该主动识别容器的init类型并提供一个默认的配置方案，在安全的前提下尽可能使用类Unix配置。

但这并不是结束。实际上KillSignal设置成SIGTERM是不对的，Kill应该是SIGKILL，stop才是SIGTERM。通过KillSignal管理容器的生命周期是不足够的，还应该设置容器的StopSignal才对。这样才可以确保在关机时运行中的容器可以一个个正常关闭，而不是等到超时被kill，使用的kill signal还不正确，这太离谱了。

不过根据这个issue， <https://github.com/systemd/systemd/issues/21918> systemd-nspawn并不打算支持可配置的stop signal。因此，既然没有什么大问题，还是尽量用PID=2来部署服务比较好。man8s部署服务会尽量使用PID2，也就是“接管配置（容器使用不合格的init）”配置，因为无论容器中运行的init是否合格，它都不会响应machinectl的命令，而这完全是systemd要求行为。

对于 s6-overlay ，s6-overlay 强行要求自己一定要以PID=1运行，并且拒绝提供任何workaround，我们也完全没有办法解决这个问题。我个人的建议是如果可以则不要启动s6-supervisor的init，建议用PID=2直接启动容器需要启动的那个主进程，跳过其他的问题。

## 依赖关系

需要进一步研究……目前需要实现两个事，一个是确保容器“完全启动”的信息可以被处理，为了方便我们就暂时不实现这个功能。另外一个是确保容器可以定义自己的依赖和启动顺序。我觉得比较简单的方法是，可以在容器中设置“条件依赖”，容器启动时会等待条件依赖满足再启动容器。条件依赖都是简单的比如TCP端口检测、ping测试、HTTP请求之类的行为。

Man8S会对容器的init进程进行一个测试，以判断它是否是一个合格的init进程，如果该init不合格，则会启动PID=2来接管容器。如果init合格，Man8S会判断init的类型，测试它对不同信号的反应，正确的完成中止进程的操作。

## btrfs 集成

systemd-nspawn TemporaryFileSystem 与idmap可能存在兼容性问题，btrfs snapshot对btrfs有较好的支持，但可配置性上可能不及TemporaryFileSystem。

## 集群部署与严格模式

容器中可能不会只有一个entrypoint。经典的例子比如seaweedfs，它的docker的同镜像需要运行多个服务，这就是说对一个镜像可能要创建几个容器，这提出了一个“cluster”的概念。
目前 Man8S 中每个rootfs都是一个自由容器，容器的文件在反复重启中不会丢失。不过如果容器采用严格模式部署的话，就可以启动同软件的多个镜像而不重复占用空间了。
