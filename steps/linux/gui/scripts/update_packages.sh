#!/usr/bin/sh

is_interactive="$1"
[ -z "$is_interactive" ] && is_interactive=1

perform_arch() {
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
}

perform_debian() {
    confirmation_arg="--yes"
    if [ "$is_interactive" != 0 ]; then
        confirmation_arg=""
    fi

    echo '[1/4] Updating package lists and upgrading packages'
    sudo apt update && sudo apt upgrade $confirmation_arg

    echo '[2/4] Removing orphans'
    sudo apt autoremove $confirmation_arg

    echo '[3/4] Clearing local package cache'
    sudo apt clean

    echo '[4/4] Removing obsolete packages'
    sudo apt autoclean
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

$PAI_SETUP_ROOT/steps/linux/gui/scripts/refresh_statusbar.sh "" "refresh:packages"

if [ "$is_interactive" != 0 ]; then
    printf "\n\e[48;5;28mAll done. Press enter to close this window...\e[0m "
    read -r _
fi
