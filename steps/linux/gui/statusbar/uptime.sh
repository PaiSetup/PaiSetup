#!/bin/sh

[ -n "$1" ] && BUTTON="$1"

[ "$BUTTON" = "$BUTTON_INFO" ] && notify-send "🔌 Computer uptime" "$(uptime --pretty)"

printf "%s" "$(uptime -p | sed "s/,.*//g")"
