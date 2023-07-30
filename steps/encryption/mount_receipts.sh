#!/bin/sh

image_path="/run/media/$USER/External/Receipts"
device_name="receipts"
mount_point="/run/media/$USER/receipts"
$PAI_SETUP_ROOT/steps/encryption/mount_veracrypt.sh "$image_path" "$device_name" "$mount_point"
