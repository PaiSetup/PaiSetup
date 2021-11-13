[ "$BUTTON" = "1" ] && {
    selection=`printf "Cancel\nShutdown\nReboot" | dmenu -l 3`
    case $selection in
        Cancel) ;;
        Shutdown) shutdown now ;; 
        Reboot) reboot ;;
    esac
}
[ "$BUTTON" = "2" ] && eval "$TERMINAL $EDITOR $0"
