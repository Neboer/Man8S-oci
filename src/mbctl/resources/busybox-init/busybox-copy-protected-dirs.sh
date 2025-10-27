#!/bin/sh

copy_dir() {
    src=$1
    dest=$2

    if [ -d "$src" ]; then
        BUSYBOX_RUN echo "Found $src — copying its contents into $dest" >&2
        BUSYBOX_RUN mkdir -p "$dest" || { BUSYBOX_RUN echo "Failed to create $dest" >&2; return 1; }

        # Prefer cp -a with the src/. form to include hidden files
        if BUSYBOX_RUN cp -a "$src"/. "$dest"/ 2>/dev/null; then
            BUSYBOX_RUN echo "Copy to $dest completed" >&2
            return 0
        fi

        BUSYBOX_RUN echo "No suitable copy method available to copy $src to $dest" >&2
        return 1
    else
        BUSYBOX_RUN echo "$src does not exist; skipping" >&2
        return 0
    fi
}

copy_dir /run.man8sprotected /run
copy_dir /tmp.man8sprotected /tmp