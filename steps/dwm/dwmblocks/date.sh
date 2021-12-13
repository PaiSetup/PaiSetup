#!/usr/bin/sh

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh start 1

printf " %s" "$(date '+%d %b %y  %R')"

[ "$BUTTON" = "1" ] && {
    if pgrep "yad --calendar" -f >/dev/null 2>&1; then
        pkill "yad --calendar" -f
    else
        yad --calendar --posx=-10 --posy=50 --no-buttons >/dev/null 2>&1 &
    fi
}

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh end 1
