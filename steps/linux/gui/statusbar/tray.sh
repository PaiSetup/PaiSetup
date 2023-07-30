#!/usr/bin/sh

[ -n "$1" ] && BUTTON="$1"

[ "$BUTTON" = "$BUTTON_INFO" ] && notify-send "System tray" "Click to show system tray"
if [ "$BUTTON" = "$BUTTON_ACTION" ]; then
    if [ -z "$(pgrep stalonetray)" ]; then
        xrdb -query | grep dwm.normbgcolor | cut -f2 | xargs stalonetray -bg >/dev/null 2>/dev/null &
    else
        pgrep stalonetray | xargs -l1  kill -9
    fi
fi

if [ -z "$(pgrep stalonetray)" ]; then
    printf ""
else
    printf ""
fi

exit 0
