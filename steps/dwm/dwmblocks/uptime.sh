#!/bin/sh

[ "$BUTTON" = "1" ] && notify-send "🔌 Computer uptime" "$(uptime --pretty)"

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh start 0
printf "%s" "$(uptime -p | sed "s/,.*//g")"
$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh end 0