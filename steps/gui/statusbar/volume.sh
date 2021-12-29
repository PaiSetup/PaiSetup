#!/bin/sh

[ "$BUTTON" = "$BUTTON_ACTION" ]      && $TERMINAL pulsemixer >/dev/null 2>/dev/null &
[ "$BUTTON" = "$BUTTON_SCROLL_UP" ]   && $LINUX_SETUP_ROOT/steps/gui/set_volume.sh 2 0
[ "$BUTTON" = "$BUTTON_SCROLL_DOWN" ] && $LINUX_SETUP_ROOT/steps/gui/set_volume.sh 1 0

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
