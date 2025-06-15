#!/bin/sh

get_name() {
    echo "joypixels (from cdn.joypixels.com)"
}

install_package() {
    mkdir -p ~/.local/share/fonts
    wget https://cdn.joypixels.com/arch-linux/font/8.0.0/joypixels-android.ttf -O ~/.local/share/fonts/joypixels.ttf
}

is_installed() {
    test -f ~/.local/share/fonts/joypixels.ttf
}

. $PAI_SETUP_ROOT/steps/linux/packages_debian/script_main.sh
