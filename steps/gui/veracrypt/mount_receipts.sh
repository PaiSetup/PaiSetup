#!/bin/sh

image_path="/run/media/$USER/External/Receipts"
device_name="receipts"
mount_point="/run/media/$USER/receipts"
$LINUX_SETUP_ROOT/steps/gui/veracrypt/mount_veracrypt.sh "$image_path" "$device_name" "$mount_point"
