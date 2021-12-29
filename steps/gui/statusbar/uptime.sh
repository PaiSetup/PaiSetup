#!/bin/sh

[ "$BUTTON" = "$BUTTON_INFO" ] && notify-send "🔌 Computer uptime" "$(uptime --pretty)"

printf "%s" "$(uptime -p | sed "s/,.*//g")"
