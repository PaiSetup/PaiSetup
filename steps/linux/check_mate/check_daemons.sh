#!/bin/sh

$PAI_SETUP_ROOT/steps/linux/check_mate/is_daemon_running.sh << EOM
    [a-zA-Z/]+python[23]? [a-zA-Z/]+ulauncher ulauncher
    flameshot flameshot
    picom picom
    [a-zA-Z/]+python[23]? [a-zA-Z/]+udiskie udiskie
EOM
