#!/bin/sh

mount_dir="$HOME/mounts"
rm -f "$mount_dir"/*
mkdir -p "$mount_dir"

IFS="
"
for line in $(mount | grep -E " on /(run/media|mount|mnt)"); do
    device_path="${line%% on *}"
    device_name="${device_path##*/}"
    mount_point="${line##* on }"
    mount_point="${mount_point%% type *}"
    link="$mount_dir/$device_name"

    echo "Linking $device_path mounted in $mount_point to $link" >&2
    ln -s "$mount_point" "$link"
done
