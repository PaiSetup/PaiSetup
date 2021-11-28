#!/usr/bin/sh

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh start 1

printf "🔄 %d" "$(checkupdates | wc -l)"

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh end 1
