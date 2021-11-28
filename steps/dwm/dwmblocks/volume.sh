#!/bin/sh

[ "$BUTTON" = "1" ] && $TERMINAL pulsemixer &

volume=$(amixer get Master | grep -E "[0-9]+%" -o | sed 's/%//g' | head -1 | tr -d '\n')
is_enabled=$(amixer get Master | grep -c "\[on\]")
[ "$volume" = 0 ] || [ "$is_enabled" = 0 ] && icon="🔈" || icon="🔊"

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh start 0
printf "$icon %3s%%" $volume
$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh end 0
