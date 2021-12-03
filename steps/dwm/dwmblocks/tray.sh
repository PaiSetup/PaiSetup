#!/usr/bin/sh

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh start 0

running_pid=""

[ "$BUTTON" = "1" ] && {
    if [ -z "$(pgrep stalonetray)" ]; then
       # #stalonetray & >/dev/null 2>/dev/null
        #disown
        stalonetray >/dev/null 2>/dev/null &
    else
        pgrep stalonetray | xargs -l1  kill -9
    fi
}

if [ -z "$(pgrep stalonetray)" ]; then
    printf ""
else
    printf ""
fi

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh end 0

exit 0
