#!/bin/sh

[ "$BUTTON" = "1" ] && notify-send "🔌 Computer uptime" "$(uptime --pretty)"

printf "%s" "$(uptime -p | sed "s/,.*//g")"
