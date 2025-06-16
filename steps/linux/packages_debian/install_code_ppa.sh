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
    # We create .list file, but after installing code, the .list file is removed and .sources file is created.
    # If we then try to install again, we will have both .list and .sources, and apt doesn't like this. Hence,
    # we check if either one of them is present. For the most part it should be .sources.
    test -f /etc/apt/sources.list.d/vscode.list || test -f /etc/apt/sources.list.d/vscode.sources
}

. $PAI_SETUP_ROOT/steps/linux/packages_debian/script_main.sh
