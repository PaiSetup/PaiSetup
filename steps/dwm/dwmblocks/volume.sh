#!/bin/sh

[ "$BUTTON" = "1" ] && {
    notify-send "🎛️ Current sink" "$(pamixer --get-default-sink | grep -oE "\"[^\"]+\"$" | tr -d \")"
    notify-send "🎛️ Available sinks" "$(pamixer --list-sinks | grep -oE "\"[^\"]+\"$" | tr -d \" | sed "s/^/ - /g")"
}
[ "$BUTTON" = "2" ] && {
    current_sink="$(pamixer --get-default-sink | grep -oE "^[0-9]+")"
    next=$( (pamixer --list-sinks; pamixer --list-sinks) | # List sinks two times, so the list wraps around after last sink
        grep -vE "Sinks|Built-in"                       | # Remove unneeded lines
        grep -m1 -A1 -E "^$current_sink"                | # Find first occurrence of our current sink and also print one line below
        tail -1                                         | # Take only line below, which is our next sink
        cut -d' ' -f1)                                    # Extract index of the sink
    [ -z "$next" ] && next="0"
    pacmd set-default-sink "$next"
}
[ "$BUTTON" = "3" ] && {
    $TERMINAL pulsemixer >/dev/null 2>/dev/null &
}

is_enabled=$(amixer get Master | grep -c "\[on\]")
volume=$(amixer get Master | grep -E "[0-9]+%" -o | sed 's/%//g' | head -1 | tr -d '\n')
if [ "$is_enabled" = 0 ]; then
    icon=""
else
    if [ "$volume" -ge "60" ]; then
        icon=""
    elif [ "$volume" -gt "0" ]; then
        icon=""
    else
        icon=""
    fi
fi

device_icon=""
(pamixer --get-default-sink | grep -q  "USB") && device_icon=""
(pamixer --get-default-sink | grep -qE "HDMI|VGA") && device_icon=""

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh start 1
printf "$device_icon $icon %3s%%" $volume
$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh end 1
