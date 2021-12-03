#!/bin/sh

[ "$BUTTON" = "3" ] && $LINUX_SETUP_ROOT/steps/graphical_env/shutdown.sh

get_daemon_warnings() {
    get_daemons() {
        # Format for below entries is as follows:
        #  - last word after a space is a human-readable name to be displayed in the notification
        #  - the rest (before the last space) is a regex for command called
        echo "sxhkd sxhkd"
        echo "synapse synapse"
        echo "flameshot flameshot"
        echo "picom picom"
        echo "dwmblocks dwmblocks"
        echo "dunst dunst"
        echo "[A-z/]+python[23]? [A-z/]+udiskie udiskie"
    }

    IFS='
'
    for daemon in $(get_daemons); do
        daemon_name="${daemon##* }"
        daemon_regex="${daemon% *}"
        # count=$(pgrep -f "$daemon" | wc -l)
        count=$(ps -x -o pid= -o cmd= | grep -Ec "^\s*[0-9]+ $daemon_regex")
        if [ "$count" = 0 ]; then echo "$daemon_name is not running"; fi
        if [ "$count" -gt 1 ]; then echo "$count instances of $daemon_name are running"; fi
    done

    return
}

get_internet_warnings() {
    interfaces=$(find -L /sys/class/net/ -name "operstate" -maxdepth 2 2>/dev/null | xargs -L1 cat | grep -c up)
    if [ "$interfaces" -eq "0" ]; then
        echo "No network interface are up"
    fi

    # address_to_ping="google.com"
    # ping $address_to_ping -c 1 >/dev/null 2>/dev/null
    # if [ "$?" != 0 ] ; then
    #     echo "Cannot ping $address_to_ping"
    # fi
}

warnings="$(get_daemon_warnings)$(get_internet_warnings)"

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh start 1
if [ -n "$warnings" ]; then
    [ "$BUTTON" = "1" ] && notify-send "⚠️ Warnings" "$warnings"
    printf "⚠"
else
    [ "$BUTTON" = "1" ] && notify-send "✅ No warnings" ""
    printf ""
fi
$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh barend 1
