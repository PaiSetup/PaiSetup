#!/bin/sh

[ -n "$1" ] && BUTTON="$1"

if [ "$BUTTON" = "$BUTTON_ACTION" ]; then
    mixed_pid="$(pgrep pavucontrol)"
    if [ -z "$mixed_pid" ]; then
        pavucontrol >/dev/null 2>/dev/null &
    else
        kill -9 "$mixed_pid"
    fi
fi
if [ "$BUTTON" = "$BUTTON_SCROLL_UP" ]; then
    $LINUX_SETUP_ROOT/steps/gui/set_volume.sh 2 0
fi
if [ "$BUTTON" = "$BUTTON_SCROLL_DOWN" ]; then
    $LINUX_SETUP_ROOT/steps/gui/set_volume.sh 1 0
fi

if [ "$(pamixer --get-mute)" = "false" ]; then
    is_enabled=1
else
    is_enabled=0
fi
volume="$(pamixer --get-volume)"
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
