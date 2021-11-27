#!/bin/sh

selection=$(printf "Cancel\nShutdown\nReboot" | dmenu)
case $selection in
    Shutdown) shutdown now ;;
    Reboot) reboot ;;
esac
