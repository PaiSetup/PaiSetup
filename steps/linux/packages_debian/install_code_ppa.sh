#!/bin/sh

get_name() {
    echo "code (setup PPA)"
}

install_package() {
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
    sudo install -o root -g root -m 644 microsoft.gpg /etc/apt/keyrings/microsoft-archive-keyring.gpg
    sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
}

is_installed() {
    test -f /etc/apt/sources.list.d/vscode.list
}

. $PAI_SETUP_ROOT/steps/linux/packages_debian/script_main.sh
