#!/usr/bin/sh

is_interactive="$1"
[ -z "$is_interactive" ] && is_interactive=1

confirmation_arg="--noconfirm"
if [ "$is_interactive" != 0 ]; then
    confirmation_arg=""
fi

echo '[1/4] Installing new packages'
sudo pacman -Syu $confirmation_arg

echo '[2/4] Removing orphans'
pacman -Qtdq | xargs sudo pacman -Rns $confirmation_arg

echo '[3/4] Clearing pacman cache'
sudo pacman -Sc --noconfirm

echo '[4/4] Clearing yay cache'
yay -Sc --noconfirm

$PAI_SETUP_ROOT/steps/linux/gui/scripts/refresh_statusbar.sh "" "13" "refresh:packages"

if [ "$is_interactive" != 0 ]; then
    printf "\n\e[48;5;28mAll done. Press enter to close this window...\e[0m "
    read -r _
fi
