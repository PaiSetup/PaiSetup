#!/bin/sh

set -e

git clone https://github.com/themix-project/oomox-gtk-theme.git
cd oomox-gtk-theme

_oomox_dir=/opt/oomox
_plugin_name=theme_oomox
sudo make -f Makefile_oomox_plugin DESTDIR="${pkgdir}" APPDIR="${_oomox_dir}" PREFIX="/usr" install
sudo python3 -O -m compileall "${pkgdir}${_oomox_dir}/plugins/${_plugin_name}" -d "${_oomox_dir}/plugins/${_plugin_name}"
