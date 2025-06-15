#!/bin/sh

get_name() {
    echo "eza (from Github)"
}

install_package() {
    wget https://github.com/eza-community/eza/releases/download/v0.21.4/eza_x86_64-unknown-linux-gnu.zip
    unzip eza_x86_64-unknown-linux-gnu.zip
    sudo cp eza /usr/local/bin/eza
    sudo chown root:root /usr/local/bin/eza
    sudo chmod 755 /usr/local/bin/eza
}

is_installed() {
    which eza
}

. $PAI_SETUP_ROOT/steps/linux/packages_debian/script_main.sh
