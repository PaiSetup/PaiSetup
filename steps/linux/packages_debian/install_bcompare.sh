#!/bin/sh

get_name() {
    echo "bcompare (from scootersoftware.com)"
}

install_package() {
    # https://www.scootersoftware.com/kb/linux_install
    wget https://www.scootersoftware.com/files/bcompare-5.1.0.31016_amd64.deb
    sudo apt-get install --yes ./bcompare-5.1.0.31016_amd64.deb
}

is_installed() {
    which bcompare
}

. $PAI_SETUP_ROOT/steps/linux/packages_debian/script_main.sh
