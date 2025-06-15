#!/bin/sh

get_name() {
    echo "megasync (from mega.nz)"
}

install_package() {
    # https://help.mega.io/installs-apps/desktop/linux

    # This is hardcoded to Debian 12... May break. I don't care enough to implement more robust script.
    wget https://mega.nz/linux/repo/Debian_12/amd64/megasync_5.12.0-1.1_amd64.deb
    sudo apt-get install ./megasync_5.12.0-1.1_amd64.deb --yes
}

is_installed() {
    which megasync
}

. $PAI_SETUP_ROOT/steps/linux/packages_debian/script_main.sh
