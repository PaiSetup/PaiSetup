#!/bin/sh

case "$WM" in
    "dwm") kill -TERM  $(pgrep ^dwm$) ;;
    "awesome") awesome-client "awesome.restart()" 2>/dev/null || exit 0 ;;
    "qtile") qtile cmd-obj -o cmd -f restart ;;
esac
