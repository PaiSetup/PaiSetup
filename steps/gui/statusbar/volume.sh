#!/bin/sh

[ -n "$1" ] && BUTTON="$1"

if [ "$BUTTON" = "$BUTTON_ACTION" ]; then
    $TERMINAL pulsemixer >/dev/null 2>/dev/null &
fi
if [ "$BUTTON" = "$BUTTON_SCROLL_UP" ]; then
    $LINUX_SETUP_ROOT/steps/gui/set_volume.sh 2 0
fi
if [ "$BUTTON" = "$BUTTON_SCROLL_DOWN" ]; then
    $LINUX_SETUP_ROOT/steps/gui/set_volume.sh 1 0
fi

is_enabled=$(amixer get Master | grep -c "\[on\]")
volume=$(amixer get Master | grep -E "[0-9]+%" -o | sed 's/%//g' | head -1 | tr -d '\n')
if [ "$is_enabled" = 0 ]; then
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

printf "$icon %3s%%" $volume
