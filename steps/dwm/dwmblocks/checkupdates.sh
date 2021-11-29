#!/usr/bin/sh

[ "$BUTTON" = "1" ] && notify-send "Pending updates" "$(checkupdates | cut -d' ' -f1)"

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh start 1

printf "🔄 %d" "$(checkupdates | wc -l)"

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh end 1
