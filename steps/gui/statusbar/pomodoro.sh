#!/bin/sh

[ -n "$1" ] && BUTTON="$1"

# Constants
idle_icon=""
pomodoro_icon="🍅"
break_icon="🆓"
pomodoro_time="$((25 * 60))"  # in seconds
break_time=$((5 * 60))        # in seconds
cache_file="$HOME/.cache/pomodoro/state"

# Helper function for interacting with current pomodoro state
# It sets the following bash variables:
#  - $state_changed  (0, if we updated current state, 1 if it was a read-only action.)
#  - $is_active      (0 means pomodoro mode or pause, 1 means idle mode.)
#  - $is_break       (0 means break, 1 means pomodoro mode. Only valid if $is_active=0.)
#  - $seconds_left   (how many seconds we have left in the current state (pomodoro or break). Only valid if $is_active=0.)
pomodoro_state() {
    case "$1" in
        0)
            # Start break time
            state_changed=0
            is_active=0
            is_break=0
            seconds_left="$break_time"
            timestamp="$(date -d "+$seconds_left seconds" +%s)"
            mkdir -p "$(dirname "$cache_file")"
            echo "$is_break $timestamp" > "$cache_file"
            ;;
        1)
            # Start pomodoro time
            state_changed=0
            is_active=0
            is_break=1
            seconds_left="$pomodoro_time"
            timestamp="$(date -d "+$seconds_left seconds" +%s)"
            mkdir -p "$(dirname "$cache_file")"
            echo "$is_break $timestamp" > "$cache_file"
            ;;
        2)
            # Deactivate pomodoro
            state_changed=0
            is_active=1
            rm "$cache_file"
            ;;
        3)
            # Query current state
            state_changed=1
            test -f "$cache_file"
            is_active="$?"
            if [ "$is_active" = 0 ]; then
                state="$(cat "$cache_file")"
                is_break="${state%% *}"
                timestamp="${state##* }"
                current_time="$(date +%s)"
                seconds_left="$((timestamp - current_time))"
            fi
    esac

    # Clear temporary variables
    unset timestamp
    unset current_time
}

# Query current state from file
pomodoro_state 3

# Active/deactivate
if [ "$BUTTON" = "$BUTTON_ACTION" ]; then
    if [ "$is_active" = 0 ]; then
        pomodoro_state 2
    else
        pomodoro_state 1
    fi
fi

# Begin/end pause if time elapsed
if [ "$is_active" = 0 ] && [ "$seconds_left" -le 0 ]; then
    if [ "$is_break" = 0 ]; then
        pomodoro_state 1
    else
        pomodoro_state 0
    fi
fi

# Show info
if [ "$BUTTON" = "$BUTTON_INFO" ] || [ "$state_changed" = 0 ]; then
    if [ "$is_active" = 0 ]; then
        if [ "$state_changed" = 0 ]; then
            paplay "$LINUX_SETUP_ROOT/steps/gui/statusbar/pomodoro_tone.ogg" >/dev/null 2>&1 &
        fi

        if [ "$is_break" = 0 ]; then
            title="$break_icon Pomodoro: break time"
        else
            title="$pomodoro_icon Pomodoro time"
        fi
        content=" $seconds_left seconds left"
    else
        title="$idle_icon Pomodoro not running"
        content="Click to activate"
    fi
    notify-send "$title" "$content"
fi

# Show icon on status bar
if [ "$is_active" = 0 ]; then
    if [ "$is_break" = 0 ]; then
        printf "$break_icon"
    else
        printf "$pomodoro_icon"
    fi
else
    printf "$idle_icon"
fi
