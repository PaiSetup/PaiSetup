checkmate_name="$1"
dwm_index="$2"
awesome_name="$3"

if [ -n "$checkmate_name" ]; then
    check_mate_client refresh "$checkmate_name" -p 50198
    echo "check_mate_client refresh "$checkmate_name" -p 50198"
fi

case "$WM" in
    "dwm")
        if [ -n "$dwm_index"; ]; then
            pkill "-RTMIN+$dwm_index" dwmblocks
        fi
        ;;
    "awesome")
        if [ -n "$awesome_name" ]; then
            awesome-client "awesome.emit_signal(\"$awesome_name\")"
        fi
        ;;
    "qtile")
        ;;
esac
