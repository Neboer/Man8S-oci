#!/bin/bash -e

network_only=0

if [ "$1" == "--network" ]; then
    network_only=1
    shift
fi

[ -z "$1" ] && { echo "Usage: man8shell [--network] <name> <exec-command>" >&2; exit 1; }

name="$1"
exec_command="${@:2}"

if [ -z "$exec_command" ]; then
    exec_command="/bin/sh -l"
fi

mainpid=$(systemctl show -p MainPID --value "systemd-nspawn@$name")
[ -z "$mainpid" ] && { echo "Container service not found" >&2; exit 1; }

initpid=$(ps --ppid "$mainpid" -o pid= | awk 'NR==1{print $1}')
[ -z "$initpid" ] && { echo "Init PID not found" >&2; exit 1; }

if [ "$network_only" -eq 1 ]; then
    nsenter -t "$initpid" -n ${exec_command}
else
    nsenter -t "$initpid" -a ${exec_command}
fi