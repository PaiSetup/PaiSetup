#!/bin/sh

font_dir=/usr/share/fonts/truetype/joypixels

get_name() {
    echo "joypixels (from cdn.joypixels.com)"
}

install_package() {
    wget https://cdn.joypixels.com/arch-linux/font/8.0.0/joypixels-android.ttf -o joypixels.ttf

    sudo install -d -m755 $font_dir
    sudo install -D -m644 joypixels.ttf $font_dir
}

is_installed() {
    test -f $font_dir/joypixels.ttf
}

. $PAI_SETUP_ROOT/steps/linux/packages_debian/script_main.sh
