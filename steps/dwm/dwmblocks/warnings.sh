#!/bin/sh

[ "$BUTTON" = "3" ] && $LINUX_SETUP_ROOT/steps/graphical_env/shutdown.sh

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

get_internet_warnings() {
    interfaces=$(find -L /sys/class/net/ -name "operstate" -maxdepth 2 2>/dev/null | xargs -L1 cat | grep -c up)
    if [ "$interfaces" -eq "0" ]; then
        echo "No network interface are up"
    fi

    address_to_ping="google.com"
    ping $address_to_ping -c 1 >/dev/null 2>/dev/null
    if [ "$?" != 0 ] ; then
        echo "Cannot ping $address_to_ping"
    fi
}

printf " "
warnings="$(get_daemon_warnings)$(get_internet_warnings)"

if [ -n "$warnings" ]; then
    [ "$BUTTON" = "1" ] && notify-send "⚠️ Warnings" "$warnings"
    printf "⚠"
else
    [ "$BUTTON" = "1" ] && notify-send "✅ No warnings" ""
    printf "🖥"
fi
printf " "