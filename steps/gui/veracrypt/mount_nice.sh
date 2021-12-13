#!/bin/sh

image_path="/run/media/$USER/External/Nice"
device_name="nice"
mount_point="/run/media/$USER/nice"
$LINUX_SETUP_ROOT/steps/gui/veracrypt/mount_veracrypt.sh "$image_path" "$device_name" "$mount_point"
