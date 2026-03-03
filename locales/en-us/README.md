# Man8S-OCI-tool

Man8S OCI tool, the command-line tool is mbctl.

A container runtime solution and supporting technical specifications based on systemd-nspawn implementation, supporting network isolation and a modern network stack, compatible with OCI and Docker.

## Installation Method

The Man8S environment has undergone some changes. Before installing this software, all necessary preparations must be made.

Install the following software in archlinux:

```bash
pacman -S python yggdrasil skopeo umoci busybox python-pip
```

This software is not just a single standalone executable; it needs to work in conjunction with other modules. The dependencies and configuration methods for this software are as follows:

1. Basic Environment: systemd-networkd, nspawn, python, python-pip. Note that pip needs to change its source.
2. Install software: skopeo, umoci
3. Install and configure yggdrasil.
4. Install the .network/netdev files from the systemd-configs folder into the systemd-networkd configuration.
5. Then edit the .network file, assign one of the container's 300-prefixed /64 subnets to the bridge (e.g., srvgrp0), for example, `Address=300:2e98:a4b0:1789::1/64`, and restart the network with networkctl.
6. Install the necessary dependency: the busybox binary executable (statically linked) to /usr/bin/busybox.

Among these, this software will automatically install the mbctl tool into the system. The steps above need to be configured manually.

## Usage

The main usage of this tool is mbctl.

mbctl supports debug output. Use `mbctl -v` to enable debug log, e.g., `mbctl -v machines pull docker.io/registry:latest Man8Registry`

- Pull an image to a local nspawn container:

    ```bash
    mbctl machines pull docker.io/registry:latest Man8Registry
    ```

    If the container defines mount points, mbctl will ask you whether to mount this mount point to a specific target. This command must be used on a local container that has not been installed at all; if configuration files or other folders exist, it will error and exit.

- Enter the container shell:

    ```bash
    mbctl machines shell Man8Registry
    ```

    This command currently supports entering the container's full namespace environment and only entering the container's network environment.

    ```bash
    sudo mbctl machines shell Man8Registry --network-only -- /usr/bin/iperf3 -s
    ```

    Using this method, you can execute the host's `iperf3 -s` command within the container's network namespace, which is very convenient.

- Remove a container:

    ```bash
    mbctl machines remove Man8Registry
    ```

    When deleting a container, it checks if the container is running and then completely clears all contents of the container (including data and configuration folders).

- Download a container as rootfs:

    ```bash
    mbctl oci download docker.io/registry:latest /var/lib/man8machine
    ```

    This command will not install the man8s-init system into the container.

- Install the man8s init system for a rootfs container at the specified path:

    ```bash
    mbctl oci man8init /var/lib/man8machine
    ```

    If the man8init system already exists in the path, it will be forcibly overwritten. Note that this command still does not check if the container is running.

- Calculate the IPv6 suffix for a container name:

    ```bash
    mbctl address getsuffix SomeFutureMachineName
    ```

- Manually start a container in the foreground from the command line:

    ```bash
    systemd-nspawn -M Man8Registry -D /var/lib/man8machines/Man8Registry
    ```

    This will start the container using the existing configuration.
    Prepending `SYSTEMD_LOG_LEVEL=debug` will start debug mode, outputting some debug logs.

## Image Configuration

After pulling the specified container, modify the corresponding nspawn file and configuration file.

nspawn configuration. The environment variables defined here are mostly trivial and generally do not and need not change; they will not become part of the configuration file.
All container configurations should be placed in `/var/lib/man8machine_configs`. These configurations should be sufficient to rebuild the container itself.
Note that due to idmap, the container will retain old data from previous runs each time it restarts. The software currently lacks a container state restoration function; leveraging btrfs advantages for snapshots could be considered in the future.
The nspawn configuration is also placed in `/var/lib/man8machine_configs/container.nspawn`, with a symbolic link pointing to `/etc/systemd/nspawn/<container_name>.nspawn`

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

man8env.env This is part of the configuration file, used to define container environment variables. Docker container operation mostly relies on environment variables, so the environment variable file is also part of the configuration in man8s.

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

MAN8S_APPLICATION_ARGS is the actual command that needs to be executed (actually a string that needs to be parsed by sh). Note that the entire env file is loaded in a special way, not simply sourced, so using = can separate strings well without worrying about escaping spaces, double quotes, etc. MAN8S_YGGDRASIL_ADDRESS is the fixed yggdrasil internal IPv6 address automatically calculated for the container. The prefix is the same as the bridge.

If new configuration file or data file paths are specified, they need to be indicated in the Files.Bind configuration within the nspawn file.

## Working Principle

mbctl uses docker and busybox as dependencies.

### Man8S Network Configuration

Man8S internal addresses are divided into two types:

- Dynamically assigned IPv4/IPv6 addresses via DHCP/SLAAC.
- Statically configured ygg 300:: addresses based on the container name hash and the host prefix.

The former is used for container network access, and the latter is used for container interconnection. Software within the container listens on the ygg address and can be accessed from the internal network address.

1. ygg (prefix 300:0:0:1::/64): Routing table number 199, priority match.
    - Traffic directly to 300:0:0:1::/64 goes directly via host0 (link/neighbor discovery).
    - Only traffic destined for the 200::/7 range is sent via the gateway 300:0:0:1::1 (which is actually the local address of the internal IPv6 gateway), with the source address specified as 300:0:0:1::100 (NAT can be applied or not; not applying NAT saves performance).
2. IPv6 ULA (prefix fc00::/64): Routing table number main, last match.
    - Traffic directly to fc00::/64 goes directly via the host0 link.
    - Other (default) traffic is sent via the ULA gateway fc00::f:e:d:c (same as the gateway above), with the source address specified as fc00::a:b:c:d. (Needs to be NATed together with v4, otherwise normal IPv6 internet access is not possible).

### Man8S init

Before the container starts, some preparatory work is needed to configure its own environment variables and network addresses, ensuring all network addresses and environment variables are correctly configured before officially starting the application.

The init process is broadly divided into the following steps:

## Development Plan

- Test more containers.
- What to do when the container software does not listen on IPv6.
- Cache pulled images.
- Store configurations like passwords that should not be publicly written into configuration files into a secret store separately.
- Support more types of containers, such as macvlan isolated containers.
