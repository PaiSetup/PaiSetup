#!/bin/sh

checkmate_name="$1"
awesome_name="$2"

if [ -n "$checkmate_name" ]; then
    check_mate_client refresh "$checkmate_name" -p 50198
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
