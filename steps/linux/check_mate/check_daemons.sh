#!/bin/sh

# TODO generated this
$PAI_SETUP_ROOT/steps/linux/check_mate/is_daemon_running.sh << EOM
    [a-zA-Z/]+python[23]? [a-zA-Z/]+ulauncher ulauncher
    flameshot flameshot
    picom picom
    [a-zA-Z/]+python[23]? [a-zA-Z/_]+udiskie udiskie
    [a-zA-Z/]+python[23]? [a-zA-Z_/]+/rpi_led/client/rpi_led_client.py rpi_led_client
EOM
