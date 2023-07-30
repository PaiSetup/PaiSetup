#!/usr/bin/sh

selection="$(printf "Connect to trusted\nPower off\nUnpair device\n" | rofi -dmenu)"
if [ "$?" != 0 ]; then
    exit 0
fi

case "$selection" in
    "Power off")
        bluetoothctl power off
        ;;
    "Unpair device")
        devices="$(bluetoothctl devices Paired)"
        if [ -n "$(printf "$devices" | wc -l)" ]; then
            device_to_unpair="$(echo "$devices" | rofi -dmenu)"
            if [ $? = 0 ]; then
                mac_address="$(echo "$device_to_unpair" | sed "s/^Device //g" | sed "s/ .*//g")"
                bluetoothctl remove "$mac_address"
            fi
        else
            notify-send "No paired devices"
        fi
        ;;
    "Connect to trusted")
        $PAI_SETUP_ROOT/steps/linux/bluetooth/connect_to_trusted.sh
        ;;
    *)
        notify-send "Error" "Bluetooth panel got invalid response from rofi"
        ;;
esac
