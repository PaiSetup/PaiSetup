#!/bin/sh

case "$1" in
  "0")
    pamixer --toggle-mute
    ;;
  "1")
    pamixer --decrease 2 --unmute
    ;;
  "2")
    pamixer --increase 2 --unmute
    ;;
    *)
    exit 1
    ;;
esac

if [ -z "$2" ] || [ "$2" != 0 ]; then
    pkill -RTMIN+12 dwmblocks
    awesome-client 'awesome.emit_signal("refresh:volume")'
fi
