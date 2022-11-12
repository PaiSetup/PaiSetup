#!/bin/sh

[ -n "$1" ] && BUTTON="$1"
if [ "$BUTTON" = "$BUTTON_INFO" ]; then
    notify-send "🎛️ Current sink" "$(pamixer --get-default-sink | grep -oE "\"[^\"]+\"$" | tr -d \")"
    notify-send "🎛️ Available sinks" "$(pamixer --list-sinks | grep -oE "\"[^\"]+\"$" | tr -d \" | sed "s/^/ - /g")"
fi
if [ "$BUTTON" = "$BUTTON_ACTION" ]; then
    current_sink="$(pamixer --get-default-sink | grep -oE "^[0-9]+")"
    next=$( (pamixer --list-sinks; pamixer --list-sinks) | # List sinks two times, so the list wraps around after last sink
        grep -vE "Sinks|Built-in|Virtual"                | # Remove unneeded lines
        grep -m1 -A1 -E "^$current_sink"                 | # Find first occurrence of our current sink and also print one line below
        tail -1                                          | # Take only line below, which is our next sink
        cut -d' ' -f1)                                     # Extract index of the sink
    if [ -z "$next" ]; then
        next="0"
    fi
    pactl set-default-sink "$next"
fi

# Print icon
icon=""
(pamixer --get-default-sink | grep -q  "USB") && icon=""
(pamixer --get-default-sink | grep -qE "HDMI|VGA") && icon=""
printf "$icon"
