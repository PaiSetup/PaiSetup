#!/usr/bin/sh

[ "$BUTTON" = "1" ] && {
    explicit="$(yay -Qe | wc -l) explcitly installed packages\n"
    implicit="$(yay -Qd | wc -l) implicitly installed packages\n"
    orphans="$(yay -Qtdq | wc -l) orphans\n"
    notify-send "📦 Installed packages" "$explicit$implicit$orphans"

    updates="$(checkupdates | cut -d' ' -f1)"
    if [ -z "$updates" ]; then
        updates="None"
    else
        updates_count="$(echo "$updates" | wc -l)"
        updates="$updates_count packages:\n$(echo "$updates" | sed "s/^/  /g")"
    fi
    notify-send "📦 Pending package updates" "$updates"
}

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh start 0

printf " %d" "$(checkupdates | wc -l)"

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh end 0
