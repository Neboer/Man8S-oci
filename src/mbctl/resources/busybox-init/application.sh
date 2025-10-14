#!/bin/sh
# the real application program for the container
echo "Start Running application.sh"
exec /bin/sh -c "exec $MAN8S_APPLICATION_ARGS"