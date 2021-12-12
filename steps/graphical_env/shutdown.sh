#!/bin/sh

selection=$(printf "Cancel\nShutdown\nReboot\nExit GUI" | dmenu)
case $selection in
    Shutdown) shutdown now ;;
    Reboot) reboot ;;
    "Exit GUI") kill -9 -1 ;;
esac
