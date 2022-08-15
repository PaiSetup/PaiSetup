#!/usr/bin/sh

[ -n "$1" ] && BUTTON="$1"

printf " %s" "$(date '+%d %b %y  %R')"

if [ "$BUTTON" = "$BUTTON_ACTION" ]; then
    if pgrep "yad --calendar" -f >/dev/null 2>&1; then
        pkill "yad --calendar" -f
    else
        yad --calendar --show-weeks --posx=-10 --posy=50 --no-buttons >/dev/null 2>&1 &
    fi
fi
