#!/bin/sh

find ~ -name "Wallpapers" -type d      |
    xargs -I{} find "{}" -name "*.png" |
    shuf -n 1                          |
    xargs "$LINUX_SETUP_ROOT/steps/gui/set_wallpaper.sh"
