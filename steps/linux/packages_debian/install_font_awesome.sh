#!/bin/sh

font_dir=/usr/share/fonts/truetype/awesome

get_name() {
    echo "awesome (from Github)"
}

install_package() {
    wget https://github.com/FortAwesome/Font-Awesome/archive/6.7.2.tar.gz
    tar -xzf 6.7.2.tar.gz

    sudo install -d -m755 $font_dir
    sudo install -D -m644 Font-Awesome-6.7.2/webfonts/*.ttf $font_dir
}

is_installed() {
    test -f $font_dir/fa-brands-400.ttf
    test -f $font_dir/fa-regular-400.ttf
    test -f $font_dir/fa-solid-900.ttf
    test -f $font_dir/fa-v4compatibility.ttf
}

. $PAI_SETUP_ROOT/steps/linux/packages_debian/script_main.sh
