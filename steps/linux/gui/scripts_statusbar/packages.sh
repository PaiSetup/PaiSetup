#!/usr/bin/sh

[ -n "$1" ] && BUTTON="$1"
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
