#!/bin/sh

get_name() {
    echo "oomox (from Github)"
}

install_package() {
    # This is mostly stolen from https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=themix-theme-oomox-git
    git clone https://github.com/themix-project/oomox-gtk-theme.git
    cd oomox-gtk-theme || exit 1

    pkgdir=""
    _oomox_dir=/opt/oomox
    _plugin_name=theme_oomox
    sudo make -f Makefile_oomox_plugin DESTDIR="${pkgdir}" APPDIR="${_oomox_dir}" PREFIX="/usr" install
    sudo python3 -O -m compileall "${pkgdir}${_oomox_dir}/plugins/${_plugin_name}" -d "${_oomox_dir}/plugins/${_plugin_name}"
}

is_installed() {
    which oomox-cli
}

. $PAI_SETUP_ROOT/steps/linux/packages_debian/script_main.sh
