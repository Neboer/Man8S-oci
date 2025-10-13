#!/bin/bash -e

# Usage: man8shell <name> <exec-command>
# exec-command is optional; default: /bin/sh -l

[ -z "$1" ] && { echo "Usage: man8shell <name> <exec-command>" >&2; exit 1; }

name="$1"
exec_command="${@:2}"

if [ -z "$exec_command" ]; then
    exec_command="/bin/sh -l"
fi

mainpid=$(systemctl show -p MainPID --value "systemd-nspawn@$name")
[ -z "$mainpid" ] && { echo "Container service not found" >&2; exit 1; }

initpid=$(ps --ppid "$mainpid" -o pid= | awk 'NR==1{print $1}')
[ -z "$initpid" ] && { echo "Init PID not found" >&2; exit 1; }

# Enter all namespaces by default
nsenter -t "$initpid" -a ${exec_command}