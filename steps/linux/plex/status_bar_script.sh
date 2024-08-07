#!/bin/sh

service=plexmediaserver.service
url=http://localhost:32400/
systemctl is-active --quiet $service
is_not_running=$? # 0 if running, otherwise not running
show_status=0

[ -n "$1" ] && BUTTON="$1"
if [ "$BUTTON" = "$BUTTON_INFO" ]; then
    show_status=1
fi
if [ "$BUTTON" = "$BUTTON_ACTION" ]; then

    if [ "$is_not_running" = 0 ]; then
        sudo systemctl stop $service && is_not_running=1
    else
        if sudo systemctl start $service; then
            is_not_running=0
            show_status=1
            (sleep 2; $BROWSER $url) & disown
        else
            notify-send "Failed to start service $service. Wait for a few seconds and try again."
            sudo systemctl stop $service
        fi
    fi
fi

if [ "$show_status" != 0 ]; then
    if [ "$is_not_running" = 0 ]; then
        notify-send "Plex is running" "Service $service is running. Access Plex at $url"
    else
        notify-send "Plex is not running" "Service $service is stopped"
    fi
fi

if [ "$is_not_running" = 0 ]; then
    printf "🟠"
else
    printf ""
fi
