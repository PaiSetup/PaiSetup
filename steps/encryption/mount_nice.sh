#!/bin/sh

image_path="/run/media/$USER/External/Nice"
device_name="nice"
mount_point="/run/media/$USER/nice"
$PAI_SETUP_ROOT/steps/encryption/mount_veracrypt.sh "$image_path" "$device_name" "$mount_point"
