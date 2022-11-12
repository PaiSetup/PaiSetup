#!/usr/bin/sh

bluetoothctl devices Trusted | sed "s/^Device //g" | sed "s/ .*//g" | while read -r trusted_mac_address ; do
    bluetoothctl connect "$trusted_mac_address"
done
