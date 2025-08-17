#!/bin/sh

spieven_name="$1"
awesome_name="$2"

if [ -n "$spieven_name" ]; then
    printf ""
    spieven refresh --names "$spieven_name" >/dev/null
fi

case "$WM" in
    "awesome")
        if [ -n "$awesome_name" ]; then
            awesome-client "awesome.emit_signal(\"$awesome_name\")"
        fi
        ;;
    "qtile")
        ;;
esac
