interfaces=$(find -L /sys/class/net/ -name "operstate" -maxdepth 2 2>/dev/null | xargs -L1 cat | grep -c up)
if [ "$interfaces" -eq "0" ]; then
    echo "No network interface is up"
fi
