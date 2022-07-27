#!/bin/sh

trash_dir=$HOME/.local/share/Trash

size="$(du -s "$trash_dir" | awk '{ print $1; }')"
size=$((size * 1024))
threshold=$((5*1024*1024*1024))

if [ "$size" -ge "$threshold" ]; then
    echo "$trash_dir contains $(numfmt --to=iec-i --suffix=B "$size")"
fi
