#!/bin/sh

wm="$(wmctrl -m | grep Name: | cut -d' ' -f2)"

case "$wm" in
    "dwm") kill -TERM  $(pgrep ^dwm$) ;;
    "awesome") awesome-client "awesome.restart()" ;;
esac
