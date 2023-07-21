#!/bin/sh

[ -n "$1" ] && BUTTON="$1"

if [ "$BUTTON" = "$BUTTON_ACTION" ]; then
    $LINUX_SETUP_ROOT/steps/gui/shutdown.sh
fi

warnings="$(check_mate_client read -p 50198 -r 1)" # TODO do not hardcode port number, take it from CheckMateStep somehow
if [ "$?" != "0" ]; then
    warnings="check_mate_server is not running"
fi
if [ -n "$warnings" ]; then
    [ "$BUTTON" = "$BUTTON_INFO" ] && notify-send "⚠️ Warnings" "$warnings\n"
    printf "⚠️ "
else
    [ "$BUTTON" = "$BUTTON_INFO" ] && notify-send "✅ No warnings" ""
    printf ""
fi
