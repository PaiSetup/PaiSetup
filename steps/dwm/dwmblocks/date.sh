#!/usr/bin/sh

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh start 0

printf "📅 %s" "$(date '+%d %b %y  %R')"

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh end 0
