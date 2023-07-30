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
    "5")
        metadata="$(playerctl -p rhythmbox metadata)"
        if [ "$?" = 0 ]; then
            extract_data() {
                echo "$metadata" | awk "/$1/{ for (i=3; i < NF; i++) printf(\"%s \", \$i); printf(\"%s\n\", \$NF)}"
            }

            title="Rhythmbox $(playerctl -p rhythmbox status | tr '[:upper:]' '[:lower:]')"
            cover="$(extract_data mpris:artUrl)"
            text="$(extract_data xesam:artist) - $(extract_data xesam:title)"
            notify-send -i "$cover" "$title" "$text"
        else
            notify-send "Rhythmbox not playing" ""
        fi
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
