#!/bin/sh

# First select the wallpaper and generate color schemes
$LINUX_SETUP_ROOT/steps/gui/select_random_wallpaper.sh


wallpaper=~/.config/LinuxSetup/wallpaper
echo "Setting wallpaper" >&2
feh --bg-scale "$wallpaper"
[ "$1" = 0 ] && notify-send -i "$wallpaper" "Wallpaper set!" "$wallpaper"

# Restart window manager
kill -TERM  $(pgrep ^dwm$)
