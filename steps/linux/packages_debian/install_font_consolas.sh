#!/bin/sh

font_dir=/usr/share/fonts/truetype/consolas

get_name() {
    echo "consolas (from Github)"
}

install_package() {
    wget https://github.com/pensnarik/consolas-font/raw/refs/heads/master/consolas-fonts-tts.tar.bz2
    tar -xjf consolas-fonts-tts.tar.bz2

    sudo install -d -m755 $font_dir
    sudo install -D -m644 ./*.ttf $font_dir
}

is_installed() {
    test -f $font_dir/Consolas-Regular.ttf
    test -f $font_dir/Consolas-Bold.ttf
    test -f $font_dir/Consolas-Italic.ttf
    test -f $font_dir/Consolas-Bold-Italic.ttf
}

. $PAI_SETUP_ROOT/steps/linux/packages_debian/script_main.sh
