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
