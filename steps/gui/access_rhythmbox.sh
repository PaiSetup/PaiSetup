#!/bin/sh

action() {
    case "$1" in
    "0")
        rhythmbox-client --pause
        ;;
    "1")
        rhythmbox-client --play --shuffle
        ;;
    "2")
        rhythmbox-client --play
        rhythmbox-client --next
        ;;
    "3")
        rhythmbox-client --play
        rhythmbox-client --seek 1
        rhythmbox-client --previous
        ;;
    "4")
        pkill rhythmbox
        ;;
    *)
        exit 1
        ;;
    esac

    if [ -z "$2" ] || [ "$2" != 0 ]; then
        pkill -RTMIN+18 dwmblocks
    fi
}

action "$1" "$2" >/dev/null 2>&1 &
