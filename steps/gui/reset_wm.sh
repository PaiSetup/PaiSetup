#!/bin/sh

case "$WM" in
    "dwm") kill -TERM  $(pgrep ^dwm$) ;;
    "awesome") awesome-client "awesome.restart()" ;;
esac
