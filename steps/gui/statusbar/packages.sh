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
    command="$command echo '[1/4] Installing new packages' ; sudo pacman -Syu ;"
    command="$command echo '[2/4] Removing orphans'        ; pacman -Qtdq | sudo pacman -Rns - ;"
    command="$command echo '[3/4] Clearing pacman cache'   ; sudo pacman -Sc --noconfirm ;"
    command="$command echo '[4/4] Clearing yay cache'      ; yay -Sc --noconfirm ;"
    command="$command                                        pkill -RTMIN+13 dwmblocks ;"
    command="$command  printf \"\n\e[48;5;28m\" ; read -p \"All done. Press enter to close this window...\" foo"
    $TERMINAL sh -c "$command" >/dev/null 2>&1 &
fi

printf " %d" "$(checkupdates | wc -l)"
