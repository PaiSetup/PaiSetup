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

[ "$BUTTON" = "3" ] && {
    command="$command echo '[1/4] Installing new packages' ; sudo pacman -Syu ;"
    command="$command echo '[2/4] Removing orphans'        ; pacman -Qtdq | sudo pacman -Rns - ;"
    command="$command echo '[3/4] Clearing pacman cache'   ; sudo pacman -Sc --noconfirm ;"
    command="$command echo '[4/4] Clearing yay cache'      ; yay -Sc --noconfirm ;"
    command="$command  printf \"\n\e[48;5;28m\" ; read -p \"All done. Press enter to close this window...\" foo"
    $TERMINAL sh -c "$command" >/dev/null 2>&1 &
}

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh start 0

printf " %d" "$(checkupdates | wc -l)"

$LINUX_SETUP_ROOT/steps/dwm/dwmblocks/bg_helper.sh end 0
