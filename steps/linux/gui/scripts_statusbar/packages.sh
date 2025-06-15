#!/usr/bin/sh

[ -n "$1" ] && BUTTON="$1"

perform_arch() {
    if [ "$BUTTON" = "$BUTTON_INFO" ]; then
        explicit="$(yay -Qe | wc -l) explcitly installed packages\n"
        implicit="$(yay -Qd | wc -l) implicitly installed packages\n"
        orphans="$(yay -Qtdq | wc -l) orphans\n"
        notify-send "📦 Installed packages" "$explicit$implicit$orphans"

        updates="$(checkupdates | cut -d' ' -f1)"
        if [ -z "$updates" ]; then
            updates="None"
        else
            important_updates="$(echo "$updates" | grep -E "^(linux|firefox|nvidia)$" | sed "s/^/  /g")"
            if [ -n "$important_updates" ]; then
                notify-send "📦 Pending important updates" "$important_updates"
            fi
        fi
    fi

    if [ "$BUTTON" = "$BUTTON_ACTION" ]; then
        command="$PAI_SETUP_ROOT/steps/linux/gui/scripts/update_packages.sh 1"
        $TERMINAL_CMD sh -c "$command" >/dev/null 2>&1 &
    fi

    printf " %d" "$(checkupdates | wc -l)"
}

perform_debian() {
    packages_for_upgrade="$(apt-get --dry-run upgrade | grep '^Inst ')"
    packages_for_upgrade_count="$(echo "$packages_for_upgrade" | wc -l)"

    if [ "$BUTTON" = "$BUTTON_INFO" ]; then

        all="$(dpkg-query -W | wc -l) packages\n"
        manual="$(apt-mark showmanual | wc -l) manual packages\n"
        automatic="$(apt-mark showauto | wc -l) automatic packages\n" # same thing as grep -E "^Package:" /var/lib/apt/extended_states
        upgradeable="$packages_for_upgrade_count upgradeable packages\n"
        notify-send "📦 Installed packages" "$all$manual$automatic$upgradeable"

        updates="$(apt list --upgradable 2>/dev/null | grep -v 'Listing' | cut -d/ -f1)"
        if [ -z "$updates" ]; then
            updates="None"
        else
            important_updates="$(echo "$updates" | grep -E "^(linux-image|linux-headers|firefox|nvidia)" | sed "s/^/  /g")"
            if [ -n "$important_updates" ]; then
                notify-send "📦 Pending important updates" "$important_updates"
            fi
        fi
    fi

    if [ "$BUTTON" = "$BUTTON_ACTION" ]; then
        command="$PAI_SETUP_ROOT/steps/linux/gui/scripts/update_packages.sh 1"
        $TERMINAL_CMD sh -c "$command" >/dev/null 2>&1 &
    fi

    printf " $packages_for_upgrade_count"
}

case $($PAI_SETUP_ROOT/steps/linux/gui/scripts/get_distro.sh) in
    arch)
        perform_arch ;;
    debian)
        perform_debian ;;
    *)
        echo "ERROR: invalid distro"
        exit 1
esac
