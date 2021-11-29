#!/bin/sh

[ "$BUTTON" = "3" ] && $TERMINAL pulsemixer &

is_enabled=$(amixer get Master | grep -c "\[on\]")
volume=$(amixer get Master | grep -E "[0-9]+%" -o | sed 's/%//g' | head -1 | tr -d '\n')
if [ "$is_enabled" == 0 ]; then
    icon=""
else
    if [ "$volume" -ge "60" ]; then
        icon=""
    elif [ "$volume" -gt "0" ]; then
        icon=""
    else
        icon=""
    fi
fi

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh start 0
printf "$icon %3s%%" $volume
$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh end 0
