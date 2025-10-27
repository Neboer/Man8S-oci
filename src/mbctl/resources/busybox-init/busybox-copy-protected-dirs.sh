#!/bin/sh

copy_dir() {
    src=$1
    dest=$2

    if [ -d "$src" ]; then
        BUSYBOX_RUN echo "Found $src — copying its contents into $dest" >&2
        BUSYBOX_RUN cp -a "$src"/. "$dest"/
        BUSYBOX_RUN echo "Copy to $dest completed" >&2
    else
        BUSYBOX_RUN echo "$src does not exist; skipping" >&2
        return 0
    fi
}

copy_dir /run.man8sprotected /run
copy_dir /tmp.man8sprotected /tmp