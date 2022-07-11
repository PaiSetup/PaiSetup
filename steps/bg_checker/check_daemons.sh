get_daemons() {
    # Format for below entries is as follows:
    #  - last word after a space is a human-readable name to be displayed in the notification
    #  - the rest (before the last space) is a regex for command called
    echo "sxhkd sxhkd"
    echo "[A-z/]+python[23]? [A-z/]+ulauncher ulauncher"
    echo "flameshot flameshot"
    echo "picom picom"
    echo "dwmblocks dwmblocks"
    echo "dunst dunst"
    echo "Charon --config charon"
    echo "[A-z/]+python[23]? [A-z/]+udiskie udiskie"
}

IFS='
'
for daemon in $(get_daemons); do
    daemon_name="${daemon##* }"
    daemon_regex="${daemon% *}"
    # count=$(pgrep -f "$daemon" | wc -l)
    count=$(ps -x -o pid= -o cmd= | grep -Ec "^\s*[0-9]+ $daemon_regex")
    if [ "$count" = 0 ]; then echo "$daemon_name is not running"; fi
    if [ "$count" -gt 1 ]; then echo "$count instances of $daemon_name are running"; fi
done
