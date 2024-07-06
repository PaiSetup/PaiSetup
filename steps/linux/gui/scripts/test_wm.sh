#!/bin/sh

xinitrc_path=~/.config/PaiSetup/$1/xinitrc
if ! [ -e $xinitrc_path ]; then
    if [ -n "$1" ]; then
        echo "$xinitrc_path does not exist!" >&2
    fi
    echo "Specify correct WM name"       >&2
    echo "Valid values are:"             >&2
    find ~/.config/PaiSetup/ -name xinitrc | grep -o "/[^/]*/xinitrc" | cut -d "/" -f 2 | sed "s/^/  /g"
    exit 1
fi

test_display=:16

Xephyr -br -ac -noreset -screen 800x600 $test_display &
pid_xephyr=$!

DISPLAY=$test_display $xinitrc_path &
pid_wm=$!

echo "Press enter to stop testing WM"
read
kill -9 $pid_xephyr
kill -9 $pid_wm
