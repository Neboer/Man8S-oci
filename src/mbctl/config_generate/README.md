# 将oci config转换成Man8S容器的差异化配置

Man8S 容器采用的配置方法整合进Man8S的init系统中。
Man8S 容器下载好镜像之后，会将oci的config.json提取出来，里面有各种配置，这些配置被解释成OCIConfig.
用户在创建Man8S的时候会指定比如nspawn template，比如容器的名字，比如容器镜像的URL，这些配置叫作Man8SContainerInfo

软件创建镜像时的主要工作是配置之间的转换，将OCICconfig和Man8SContainerInfo转换成NspawnConfig和ExtraEnvs。
 

## 挂载点

oci_config 中会提供一些“期望”的挂载点，同时软件的配置文件（夹）也会被挂载到容器中。
在这个转换的阶段，我们并不知道所有软件配置的挂载点，所以这里只挂载一些“有用”的挂载点。

### 对于数据挂载点：

我们会将oci_config 中的所有期望的挂载点都挂载到容器中，并且在 config.man8machine_storage_path 中创建对应的目录，并自动设置挂载点为这些目录。
这样，我们要求所有man8s容器重启之后数据丢失（标准行为），但是软件的数据文件（夹）会被保存在 config.man8machine_storage_path 中保留，统一管理。

### 对于配置文件挂载点：

由于docker中的软件配置一般不会声明在Volumes中，因此刚刚创建好的容器镜像是没有任何的配置文件挂载点的。
由于我们认为环境变量也属于配置文件的一部分，因此容器的 /man8env.env 文件会bindmount到 config.man8machine_configs_path / man8env.env 下。这个配置文件可能对于大多数容器来说已经足够了。

如果软件需要传入额外的配置文件，比如在/etc/下可能有一些配置，那就需要用户手动将软件专用的配置文件挂载到容器中，这里有一个很好的命令 `mbctl container <name> mount-add <path(incontainer)>`
这个命令会将用户指定的容器路径挂载到 config.man8machine_configs_path 下对应的路径，将容器对应路径的文件拷贝到该目录下，并添加记录到nspawn配置中。
