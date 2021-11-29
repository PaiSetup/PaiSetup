#!/bin/sh

[ "$BUTTON" = "1" ] && notify-send "🌐 Network activity" "  🔻 - download\n  🔺 - upload"
[ "$BUTTON" = "3" ] && $TERMINAL bmon

update() {
    sum=0
    for arg; do
        read -r i < "$arg"
        sum=$(( sum + i ))
    done
    cache=${XDG_CACHE_HOME:-$HOME/.cache}/${1##*/}
    [ -f "$cache" ] && read -r old < "$cache" || old=0
    printf %d\\n "$sum" > "$cache"
    printf %d\\n $(( sum - old ))
}

rx=$(update /sys/class/net/[ew]*/statistics/rx_bytes)
tx=$(update /sys/class/net/[ew]*/statistics/tx_bytes)

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh start 1
printf "🔻%4sB 🔺%4sB" "$(numfmt --to=iec "$rx")" "$(numfmt --to=iec "$tx")"
$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh end 1
