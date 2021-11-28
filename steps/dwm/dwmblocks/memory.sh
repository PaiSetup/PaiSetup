#!/bin/sh

[ "$BUTTON" = "1" ] && notify-send "🧠 Memory hogs" "$(ps axch -o cmd:15,%mem --sort=-%mem | head)"

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh barstart 1
printf " "
free | awk 'NR == 2 {printf("%.2f%% of "), $3/$2*100}'
free -h | awk 'NR == 2 {printf ($2)}'
$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh end 1
