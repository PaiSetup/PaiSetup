#!/bin/sh

reboot_to_windows() {
    windows_title="$(sudo grep -i "menuentry 'windows" /boot/grub/grub.cfg | cut -d"'" -f2)"
    if [ $? != 0 ]; then
        echo "failed to query grub menuentry for Windows."
        return 1
    fi
    if [ -z "$windows_title" ]; then
        echo "no menuentry for Windows was found."
        return 1
    fi
    if [ "$(echo "$windows_title" | wc -l)" != 1 ]; then
        echo "too many menuentries for Windows were found."
        return 1
    fi

    sudo grub-reboot "$windows_title" || return 1
    if [ $? != 0 ]; then
        echo "failed execute grub-reboot."
        return 1
    fi

    sudo reboot || return 1
    if [ $? != 0 ]; then
        echo "failed execute reboot."
        return 1
    fi
}

error="$(reboot_to_windows)"
if [ $? != 0 ]; then
    notify-send "❌ Error" "Could not reboot to Windows: $error"
    return 1
fi
