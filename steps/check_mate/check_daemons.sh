#!/bin/sh

get_daemons() {
    echo "[a-zA-Z/]+python[23]? [a-zA-Z/]+ulauncher ulauncher"
    echo "flameshot flameshot"
    echo "picom picom"
    echo "[a-zA-Z/]+python[23]? [a-zA-Z/]+udiskie udiskie"
}

. $SCRIPTS_PATH/core/linux/is_daemon_running.sh # TODO move it into PaiSetup
get_daemons | is_daemon_running
