#!/bin/sh

[ -n "$1" ] && BUTTON="$1"

if [ "$BUTTON" = "$BUTTON_ACTION" ]; then
    $LINUX_SETUP_ROOT/steps/gui/shutdown.sh
fi

warnings="$(BgCheckerClient ReadWarnings)"
if [ "$?" != "0" ]; then
    warnings="BgCheckerServer is not running"
fi
if [ -n "$warnings" ]; then
    [ "$BUTTON" = "$BUTTON_INFO" ] && notify-send "⚠️ Warnings" "$warnings\n"
    printf "⚠"
else
    [ "$BUTTON" = "$BUTTON_INFO" ] && notify-send "✅ No warnings" ""
    printf ""
fi
