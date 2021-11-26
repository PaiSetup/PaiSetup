#!/bin/sh

get_daemon_warnings() {
    get_daemons() {
        echo "sxhkd"
        echo "synapse"
        echo "flameshot"
        echo "picom"
        echo "dwmblocks"
        echo "dunst -config"
    }

    IFS='
'
    for daemon in $(get_daemons); do
        # count=$(pgrep -f "$daemon" | wc -l)
        count=$(ps -x -o pid= -o cmd= | grep -Ec "^\s*[0-9]+ $daemon")
        if [ "$count" = 0 ]; then echo "$daemon is not running"; fi
        if [ "$count" -gt 1 ]; then echo "$count instances of $daemon are running"; fi
    done

    return
}

warnings=$(get_daemon_warnings)

[ "$BUTTON" = "2" ] && eval "$TERMINAL $EDITOR $0"

if [ -n "$warnings" ]; then
    [ "$BUTTON" = "1" ] && notify-send "⚠️ Warnings" "$warnings"
    printf "⚠"
else
    [ "$BUTTON" = "1" ] && notify-send "✅ No warnings" ""
    printf "🖥"
fi
