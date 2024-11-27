#!/bin/sh

# Early return if we're not focusing Thunar
focused_window_id=$(xdotool getwindowfocus)
focused_window_class=$(xdotool getwindowclassname $focused_window_id)
if [ "$focused_window_class" != "Thunar" ];  then
    exit 1
fi

# Save clipboard
clipboard="$(xclip -o)"

# Activate Thunar window and copy the current path
xdotool windowactivate --sync $focused_window_id || exit 1
sleep 0.05 # this micro-sleep is really needed
xdotool key --clearmodifiers ctrl+l ctrl+c || exit 1
cwd="$(xclip -o)" || exit 1

# Restore clipboard
# TODO why does this lag?
# echo "$clipboard" | xclip -selection clipboard

# Return current path to stdout
if [ -z "$cwd" ]; then
    exit 1
fi
echo "$cwd"
