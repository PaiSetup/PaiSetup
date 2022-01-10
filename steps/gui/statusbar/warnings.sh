#!/bin/sh

if [ "$BUTTON" = "$BUTTON_ACTION" ]; then
    $LINUX_SETUP_ROOT/steps/gui/shutdown.sh
fi

. ~/.profile

get_daemon_warnings() {
    get_daemons() {
        # Format for below entries is as follows:
        #  - last word after a space is a human-readable name to be displayed in the notification
        #  - the rest (before the last space) is a regex for command called
        echo "sxhkd sxhkd"
        echo "[A-z/]+python[23]? [A-z/]+ulauncher ulauncher"
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

get_unlocked_veracrypt_warnings() {
    for mapped_drive in $(find /dev/mapper/ -mindepth 1 -not -path /dev/mapper/control); do
        echo "Veracrypt \"$(basename "$mapped_drive")\" drive is unlocked"
    done
}

get_internet_warnings() {
    interfaces=$(find -L /sys/class/net/ -name "operstate" -maxdepth 2 2>/dev/null | xargs -L1 cat | grep -c up)
    if [ "$interfaces" -eq "0" ]; then
        echo "No network interface is up"
    fi

    # address_to_ping="google.com"
    # ping $address_to_ping -c 1 >/dev/null 2>/dev/null
    # if [ "$?" != 0 ] ; then
    #     echo "Cannot ping $address_to_ping"
    # fi
}

get_updated_kernel_warnings() {
    if [ -z "$(find /lib/modules -maxdepth 1 -type d -name "$(uname -a | cut -d' ' -f3)")" ]; then
        echo "Possible kernel update detected. Some kernel modules may not work."
    fi
}

get_unmatching_packages_warnings() {
    packages="$(get_unmatching_packages | grep -E "<|>")"
    if [ -n "$packages" ]; then
        echo "$(echo "$packages" | wc -l) packages do not match with LinuxSetup"
    fi
}

warnings="$(get_daemon_warnings)$(get_internet_warnings)$(get_unlocked_veracrypt_warnings)$(get_updated_kernel_warnings)$(get_unmatching_packages_warnings)"

if [ -n "$warnings" ]; then
    [ "$BUTTON" = "$BUTTON_INFO" ] && notify-send "⚠️ Warnings" "$warnings"
    printf "⚠"
else
    [ "$BUTTON" = "$BUTTON_INFO" ] && notify-send "✅ No warnings" ""
    printf ""
fi
