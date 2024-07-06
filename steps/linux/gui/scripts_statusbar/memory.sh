#!/bin/sh

[ -n "$1" ] && BUTTON="$1"
[ "$BUTTON" = "$BUTTON_INFO" ] && notify-send "🧠 Memory intensive processes" "$(ps axch -o cmd:15,%mem --sort=-%mem | head -10 | xargs -I{} printf "%s%%\n" "{}")"

free  | awk 'NR == 2 { printf(" %dMiB used", ($3/1024)) }'
