#!/bin/sh

# This scripts create new pulseaudio modules in order to redirect all sound sources to a single virtual sound source.
# Useful commands for debugging:
#    watch -n0.1 "pamixer --list-sources ; echo; pamixer --list-sinks; echo;  pactl list short modules"
#    pactl unload-module module-loopback ; pactl unload-module module-null-sink


cache_dir="$HOME/.cache/LinuxSetupFfmpegRecording"
modules_file="$cache_dir/pulseaudio_modules"
ffmpeg_log_file="$cache_dir/ffmpeg_log"
ffmpeg_pid_file="$cache_dir/ffmpeg_pid"
virtual_sink_name="VirtualRecordingSink"
virtual_source_name="$virtual_sink_name.monitor"
output_file=~/Downloads/recording.mp4

failure() {
    notify-send "Error occurred" "$1"
    exit 1
}

is_ffmpeg_running() {
    ffmpeg_pid="$(cat "$ffmpeg_pid_file")"
    [ -d "/proc/$ffmpeg_pid" ] && [ "$(cat /proc/$ffmpeg_pid/comm)" = "ffmpeg" ]
    echo "$?"
}

wait_for_ffmpeg() (
    success=1
    for sleep_time in 1 1 1 1 1 2 2 2 2 2; do
        sleep "$sleep_time"
        if [ "$(is_ffmpeg_running)" != "0" ]; then
            success=0
            break
        fi
    done

    if [ "$success" = 0 ]; then
        notify-send " Screen capture saved" "$output_file"
    else
        failure "Failed to close ffmpeg"
    fi
)

get_audio_sources() {
    if [ "$(printf "No\nYes" | dmenu -p "Record PC audio?")" = "Yes" ]; then
        pamixer --list-sources | grep output | grep -vE "Sinks|Virtual|Null Output"
    fi
    if [ "$(printf "No\nYes" | dmenu -p "Record microphone audio?")" = "Yes" ]; then
        pamixer --list-sources | grep input
    fi
}

start_recording() (
    echo "Creating cached data in $cache_dir" >&2
    mkdir -p "$cache_dir"

    module_id="$(pactl load-module module-null-sink sink_name="$virtual_sink_name")" || failure "Creating virtual sink"
    echo "Creating $virtual_sink_name for all audio sources (module id - $module_id)" >&2
    echo "$module_id $virtual_sink_name" > "$modules_file"

    echo "Linking all hardware audio sources to the $virtual_sink_name" >&2
    get_audio_sources | grep -vE "Sinks|Virtual|Null Output" | while read -r line; do
        source_num="$(echo "$line" | cut -d' ' -f1)"
        source_name="$(echo "$line" | cut -d' ' -f3- | tr -d '"')"
        module_id="$(pactl load-module module-loopback sink="$virtual_sink_name" source="$source_num")" || failure "Creating loopback sink"
        echo "  $source_num $source_name (module id - $module_id)" >&2
        echo "$module_id $source_name" >> "$modules_file"
    done

    echo "Launching ffmpeg" >&2
    ffmpeg -y   -f x11grab -framerate 60 -i :0.0   -f pulse -i "$virtual_source_name" "$output_file" > "$ffmpeg_log_file" 2>&1 &
    ffmpeg_pid="$!"
    echo "ffmpeg pid: $ffmpeg_pid" >&2
    echo "$ffmpeg_pid" > "$ffmpeg_pid_file"
    [ "$(is_ffmpeg_running)" = "0" ] || failure "Failed to started ffmpeg (see logs: $ffmpeg_log_file)"
)

end_recording() (
    if [ -f "$ffmpeg_pid_file" ]; then
        echo "Stopping ffmpeg" >&2
        ffmpeg_pid="$(cat "$cache_dir/ffmpeg_pid")"
        kill "$ffmpeg_pid"
        wait_for_ffmpeg >/dev/null 2>&1 &
    fi

    if [ -f "$modules_file" ]; then
        echo "Removing pulseaudio modules" >&2
        cat "$modules_file" | cut -d' ' -f1 | xargs -L1 pactl unload-module 2>/dev/null
    fi

    if [ -d "$cache_dir" ]; then
        echo "Removing cache directory" >&2
        rm -rf "$cache_dir"
    fi

    echo "Recording done" >&2
)

# Start or stop recording
print_info=1
[ "$BUTTON" = "$BUTTON_ACTION" ] && {
    if [ -d "$cache_dir" ]; then
        end_recording
    else
        start_recording
        print_info=0
    fi
    echo >&2
}

# Get current state
if [ -d "$cache_dir" ]; then
    icon="🔴"
    modules="$(cat "$modules_file" | cut -d' ' -f1 | xargs echo)"
    ffmpeg_pid="$(cat "$ffmpeg_pid_file")"
    if [ "$(is_ffmpeg_running)" = 0 ]; then
        ffmpeg_status="OK"
    else
        icon=""
        ffmpeg_status="NOT RUNNING"
    fi
    notification_title="$icon Capture in progress"
    notification_text="pulseaudio modules: $modules\nffmpeg: $ffmpeg_pid ($ffmpeg_status)"
else
    icon=""
    notification_text="Click to activate"
    notification_title="$icon Capture not running"
fi

# Show info
if [ "$BUTTON" = "$BUTTON_INFO" ] || [ "$print_info" = "0" ]; then
    notify-send "$notification_title" "$notification_text"
fi

# Print bar icon
printf "$icon"
