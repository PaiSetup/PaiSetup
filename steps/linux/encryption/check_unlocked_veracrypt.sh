#!/bin/sh

header_printed=0
for mapped_drive in $(find /dev/mapper/ -mindepth 1 -not -path /dev/mapper/control); do
    if [ "$header_printed" = 0 ]; then
        header_printed=1
        echo "Veracrypt drives unlocked"
    fi
    echo "$mapped_drive"
done
exit $header_printed
