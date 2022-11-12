#!/bin/bash

cycle_sinks() {
    cycle_forwards="$1"

    # Pulseaudio assigns IDs to sinks. They may be uncontiguous. Find which one of them is currently in use and get its index.
    # For example if we have sinks 13,19,100,200 and sink 100 is in use, then sink_index=2.
    sink_ids=($(pamixer --list-sinks | grep -vE "Built-in|Virtual" | grep -oE "^[0-9]+ ")) # This is an array
    max_sink_index=$((${#sink_ids[@]} - 1))
    current_sink_id="$(pamixer --get-default-sink | grep -Eo "^[0-9]+")"
    IFS="
    "
    sink_index=0
    for i in ${!sink_ids[*]}; do
        sink_id="${sink_ids[$i]}"
        if [ "$sink_id" = "$current_sink_id" ]; then
            sink_index="$i"
        fi
    done

    # Determine index of a sink to choose
    if [ "$cycle_forwards" = 1 ]; then
        if [ "$sink_index" = "$max_sink_index" ]; then
            next_sink_index=0
        else
            next_sink_index=$((sink_index + 1))
        fi
    else
        if [ "$sink_index" = 0 ]; then
            next_sink_index=$max_sink_index
        else
            next_sink_index=$((sink_index - 1))
        fi
    fi

    # Set the new default sink
    next_sink_id=${sink_ids[next_sink_index]}
    pactl set-default-sink "$next_sink_id"
}


[ -n "$1" ] && BUTTON="$1"
if [ "$BUTTON" = "$BUTTON_INFO" ]; then
    notify-send "🎛️ Current sink" "$(pamixer --get-default-sink | grep -v "Default sink:" | sed -E "s/\"[^\"]+\"[^$]//g" | tr -d '"')"
    notify-send "🎛️ Available sinks" "$(pamixer --list-sinks | grep -v "Sinks:" | sed -E "s/\"[^\"]+\"[^$]//g" | tr -d '"' | sed "s/^/  /g")"
fi
if [ "$BUTTON" = "$BUTTON_ACTION" ] || [ "$BUTTON" = "$BUTTON_SCROLL_UP" ]; then
    cycle_sinks 1
fi
if [ "$BUTTON" = "$BUTTON_SCROLL_DOWN" ]; then
    cycle_sinks 0
fi

# Print icon
icon=""
(pamixer --get-default-sink | grep -q  "USB") && icon=""
(pamixer --get-default-sink | grep -qE  "bluez") && icon=""
(pamixer --get-default-sink | grep -qE "HDMI|VGA") && icon="  "
printf "$icon"
