#!/bin/sh

[ -n "$1" ] && BUTTON="$1"

show_popup=0
if [ "$BUTTON" = "$BUTTON_INFO" ]; then
    show_popup=1
fi
if [ "$BUTTON" = "$BUTTON_ACTION" ]; then
    check_mate_client refresh_all -p 50198 -r 1
    sleep 0.1 # TODO this is a hack, so refresh is done before read. An ideal solution would be to add blocking refresh to CheckMate
    show_popup=1
fi

warnings="$(check_mate_client read -p 50198 -r 1)" # TODO do not hardcode port number, take it from CheckMateStep somehow
if [ "$?" != "0" ]; then
    warnings="check_mate_server is not running"
fi

if [ -n "$warnings" ]; then
    [ "$show_popup" = 1 ] && notify-send "⚠️ Warnings" "$warnings\n"
    printf "⚠️ "
else
    [ "$show_popup" = 1 ] && notify-send "✅ No warnings" ""
    printf ""
fi
