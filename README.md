# Man8S-distroless

一种新的Man8S容器，与docker兼容（实验性）

## 安装方法

Man8S环境有所变化，在安装此软件之前，需要做一切必要的准备。

在archlinux中安装如下软件：
```bash
pacman -S python yggdrasil skopeo umoci busybox python-pip
```

1. 基础环境: systemd-networkd，nspawn，python，python-pip，注意pip需要换源。
2. 安装软件：skopeo、umoci
3. yggdrasil安装
4. 将50-mbsrv0.network/netdev安装到systemd-networkd配置中并完成此配置
5. 安装必需依赖：busybox 二进制可执行文件（静态链接）到 /usr/bin/busybox

其中，本软件的makefile已经将4完成了，并且自动将mbctl工具安装进系统中。
如果你准备重新安装mbctl这个Python模块而不是复用已缓存的wheel，可以先卸载再无缓存安装。
```bash
pip uninstall mbctl --break-system-packages
rm -rf build
pip install . --no-cache-dir --force-reinstall --break-system-packages
```

克隆仓库， `sudo make install`

## 使用方法

执行  `sudo -E man8s-create-distroless.sh nodejs24-debian12 DTLTest1`


## 镜像配置

在拉取指定的容器之后……



## 容器调试

`sudo man8shell.sh <container_name>` 可以进入正在运行的容器中的shell，可以在里面调查容器。

## 从docker站拉取rootfs

`man8pull-oci.sh gcr.io/distroless/nodejs22-debian12:nonroot test-dtl-fs`

用类似的方法可以拉取所有的docker镜像为rootfs。但当然大多数docker镜像并不能直接被nspawn启动，需要额外的修改。本项目提供的man8s-create-distroless就是其中之一。如果遇到网络问题可以直接开代理HTTP_PROXY。

## init系统

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