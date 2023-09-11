#!/bin/bash

get_monitors() (
    # Blindly copy pasted from https://stackoverflow.com/questions/10500521/linux-retrieve-monitor-names
    while read -r output hex conn; do
        [[ -z "$conn" ]] && conn=${output%%-*}
        echo "$output $conn   $(xxd -r -p <<< "$hex")"
    done < <(xrandr --prop | awk '
        !/^[ \t]/ {
            if (output && hex) print output, hex, conn
            output=$1
            hex=""
        }
        /ConnectorType:/ {conn=$2}
        /[:.]/ && h {
            sub(/.*000000fc00/, "", hex)
            hex = substr(hex, 0, 26) "0a"
            sub(/0a.*/, "", hex)
            h=0
        }
        h {sub(/[ \t]+/, ""); hex = hex $0}
        /EDID.*:/ {h=1}
        END {if (output && hex) print output, hex, conn}
        ' | sort
    )
)

cycle_sinks() {
    cycle_forwards="$1"

    # My LG 27gn800 doesn't have a speaker, but is still reported as a sink, so we should skip it. The problem is pamixer
    # reports the GPU as the sink and not the monitor, so we cannot easily check it on a per-monitor basis. Hence, we
    # check if LG monitor is connected at all and then skip all HDMI sinks. This will cause problems with multimonitor setup,
    # but I have only one monitor, so I don't care.
    get_monitors | grep -qv "LG ULTRAGEAR"
    skip_hdmi=$?

    # Pulseaudio assigns IDs to sinks. They may be uncontiguous. Find which one of them is currently in use and get its index.
    # For example if we have sinks 13,19,100,200 and sink 100 is in use, then sink_index=2.
    sink_ids="$(pamixer --list-sinks | grep -vE "Built-in|Virtual")"
    if [ "$skip_hdmi" = 1 ]; then
        sink_ids="$(echo "$sink_ids" | grep -v hdmi-stereo)"
    fi
    sink_ids="$(echo "$sink_ids" | grep -oE "^[0-9]+ ")"
    # shellcheck disable=SC2206
    sink_ids=($sink_ids) # wrap in an array

    max_sink_index=$((${#sink_ids[@]} - 1))
    current_sink_id="$(pamixer --get-default-sink | grep -Eo "^[0-9]+")"
    IFS="
    "
    sink_index=-1
    for i in ${!sink_ids[*]}; do
        sink_id="${sink_ids[$i]}"
        if [ "$sink_id" = "$current_sink_id" ]; then
            sink_index="$i"
        fi
    done

    if [ $sink_index != -1 ]; then
        # We're currently on a valid sink. Determine index of a next sink to choose.
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
    else
        # We're currently on an invalid sink. Just select any.
        next_sink_index=0
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
(pamixer --get-default-sink | grep -q   "USB")      && icon=""
(pamixer --get-default-sink | grep -qE  "bluez")    && icon=""
(pamixer --get-default-sink | grep -qiE "wireless") && icon=""
(pamixer --get-default-sink | grep -qiE "headset")  && icon=""
(pamixer --get-default-sink | grep -qE "HDMI|VGA")  && icon="  "
printf "$icon"
