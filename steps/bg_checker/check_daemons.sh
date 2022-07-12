get_daemons() {
    echo "sxhkd sxhkd"
    echo "[A-z/]+python[23]? [A-z/]+ulauncher ulauncher"
    echo "flameshot flameshot"
    echo "picom picom"
    echo "dwmblocks dwmblocks"
    echo "dunst dunst"
    echo "[A-z/]+python[23]? [A-z/]+udiskie udiskie"
}

. $SCRIPTS_PATH/core/linux/is_daemon_running.sh
get_daemons | is_daemon_running
