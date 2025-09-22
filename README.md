# Man8S-distroless

一种新的Man8S容器，与docker兼容（实验性）

## 安装方法

克隆仓库， `sudo make install`

## 使用方法

执行  `sudo -E man8s-create-distroless.sh nodejs24-debian12 DTLTest1`
执行后， /var/lib/machines/DTLTest1 下会生成完整的容器镜像
支持的镜像有：
- static-debian12
- base-debian12
- base-nossl-debian12
- cc-debian12
- python3-debian12
- java-base-debian12
- java17-debian12
- java21-debian12
- nodejs20-debian12
- nodejs22-debian12
- nodejs24-debian12

我们会将这些镜像变为rootfs存储进指定文件夹。

## 镜像配置

在拉取指定的容器之后……

配置nspawn，并做出对应的修改，注意目前仅支持网络隔离。
```bash
sudo cp /usr/lib/man8lib/nspawn-files/example.nspawn /etc/systemd/nspawn/<container_name>.nspawn
```

将你的应用环境放进 `/var/lib/machines/<container_name>/` 下

然后编写 `/var/lib/machines/<container_name>/sbin/application.sh` ，在里面写上容器启动后要执行的命令。

一切准备就绪， machinectl start <container_name>。

## 容器调试

`sudo man8shell.sh <container_name>` 可以进入正在运行的容器中的shell，可以在里面调查容器。

## 从docker站拉取rootfs

`man8pull-oci.sh gcr.io/distroless/nodejs22-debian12:nonroot test-dtl-fs`

用类似的方法可以拉取所有的docker镜像为rootfs。但当然大多数docker镜像并不能直接被nspawn启动，需要额外的修改。本项目提供的man8s-create-distroless就是其中之一。