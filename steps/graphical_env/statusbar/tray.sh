#!/usr/bin/sh

[ "$BUTTON" = "1" ] && {
    if [ -z "$(pgrep stalonetray)" ]; then
        xrdb -query | grep dwm.normbgcolor | cut -f2 | xargs stalonetray -bg >/dev/null 2>/dev/null &
    else
        pgrep stalonetray | xargs -l1  kill -9
    fi
}

if [ -z "$(pgrep stalonetray)" ]; then
    printf ""
else
    printf ""
fi

exit 0
