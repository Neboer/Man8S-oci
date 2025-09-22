#!/bin/bash -e
[ -z "$1" ] && { echo "Usage: center <name> <exec-command>" >&2; return 1; }

name="$1"
exec_command="$2"

if [ -z "$exec_command" ]; then
    exec_command="/bin/sh -l"
fi

mainpid=$(systemctl show -p MainPID --value "systemd-nspawn@$1")
[ -z "$mainpid" ] && { echo "Container service not found" >&2; return 1; }

initpid=$(ps --ppid "$mainpid" -o pid= | awk 'NR==1{print $1}')
[ -z "$initpid" ] && { echo "Init PID not found" >&2; return 1; }

nsenter -t "$initpid" -a ${exec_command}