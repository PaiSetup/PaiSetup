#!/bin/sh

wm="$(wmctrl -m | head -1)"
wm="${wm##Name: }"
case "$wm" in
    dwm)     kill -TERM  $(pgrep ^dwm$) ;;
    awesome) echo 'awesome.restart()' | awesome-client ;;
esac
