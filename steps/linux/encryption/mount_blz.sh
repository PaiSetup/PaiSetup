#!/bin/sh

image_path="/run/media/$USER/External/Blz"
device_name="blz"
mount_point="/home/maciej/notes/_blz"
$PAI_SETUP_ROOT/steps/linux/encryption/mount_veracrypt.sh "$image_path" "$device_name" "$mount_point"
