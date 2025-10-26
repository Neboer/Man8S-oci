# 将oci config转换成Man8S容器的差异化配置

Man8S 容器采用的配置方法整合进Man8S的init系统中。
Man8S 容器下载好镜像之后，会将oci的config.json提取出来，里面有各种配置，这些配置被解释成OCIConfig.
用户在创建Man8S的时候会指定比如nspawn template，比如容器的名字，比如容器镜像的URL，这些配置叫作Man8SContainerInfo

软件创建镜像时的主要工作是配置之间的转换，将OCICconfig和Man8SContainerInfo转换成NspawnConfig和ExtraEnvs。
 

## 挂载点

oci_config 中会提供一些“期望”的挂载点，同时软件的配置文件（夹）也会被挂载到容器中。
在这个转换的阶段，我们并不知道所有软件配置的挂载点，所以这里只挂载一些“有用”的挂载点。

容器需要挂载的数据，一般认为有配置文件和容器数据两种。如果一个容器中声明了volume，则mbctl在拉取容器之前会询问此volume的挂载目标。
询问挂载目标时，必须输入绝对路径，表示将此挂载点设置为哪个具体的路径，如果不存在会被创建。设置完路径后，容器对应volume下的所有内容都会被拷贝至新建的路径中。

用户会在程序开始时选择挂载volume的位置，也就是选择挂载点的目标，之后这些选择会成为man8s_config的一部分，传入config_generate中配置文件转换的过程。然后在配置文件具体的转换过程被应用，没有配置的volume会被弃用，不会被挂载。

用户选择volume挂载路径时，首先需要回答：这个挂载点是配置文件、数据路径、自定义目标还是跳过？

- 配置文件：会挂载到 `<config.man8machine_configs_path>/<ContainerName>/` 下的对应路径。
- 数据文件：会挂载到 `<config.man8machine_storage_path>/<ContainerName>/` 下的对应路径。
- 自定义目标：再弹出一个问题，要求用户输入自定义目标，会挂载到用户的目标路径。
- 跳过：不会挂载这个路径。
