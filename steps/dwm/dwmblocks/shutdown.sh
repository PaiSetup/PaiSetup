#!/bin/sh

[ "$#" -ne 0 ] && [ -n "$BUTTON" ] && BUTTON="$1"

[ "$BUTTON" = "1" ] && {
    selection=$(printf "Cancel\nShutdown\nReboot" | dmenu -l 3)
    case $selection in
        Shutdown) shutdown now ;; 
        Reboot) reboot ;;
    esac
}
[ "$BUTTON" = "2" ] && eval "$TERMINAL $EDITOR $0"
