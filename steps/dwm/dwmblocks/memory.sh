#!/bin/sh

[ "$BUTTON" = "1" ] && notify-send "🧠 Memory intensive processes" "$(ps axch -o cmd:15,%mem --sort=-%mem | head -10 | xargs -I{} printf "%s%%\n" "{}")"

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh barstart 1
free  | awk 'NR == 2 { printf(" %dMiB used", ($3/1024)) }'
$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh end 1
