#!/bin/sh
# load /man8env.env environment variables into the current shell
# code from https://gist.github.com/mihow/9c7f559807069a03e302605691f85572?permalink_comment_id=4494251#gistcomment-4494251
ENV_VARS="$(cat /man8env.env | awk '!/^\s*#/' | awk '!/^\s*$/')"

eval "$(
  BUSYBOX_RUN printf '%s\n' "$ENV_VARS" | while IFS='' read -r line; do
    key=$(BUSYBOX_RUN printf '%s\n' "$line"| BUSYBOX_RUN sed 's/"/\\"/g' | BUSYBOX_RUN cut -d '=' -f 1)
    value=$(BUSYBOX_RUN printf '%s\n' "$line" | BUSYBOX_RUN cut -d '=' -f 2- | BUSYBOX_RUN sed 's/"/\\\"/g')
    BUSYBOX_RUN printf '%s\n' "export $key=\"$value\""
  done
)"
