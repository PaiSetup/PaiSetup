#!/bin/sh

# Constants
image_path="$1"
device_name="$2"
mount_point="$3"
mapped_device_path="/dev/mapper/$device_name"
notify_success=1  # 0 means notify

# Check current state
sudo cryptsetup status "$device_name" >/dev/null 2>&1
is_opened="$?"  # 0 means opened
mount | grep -q "/dev/mapper/$device_name"
is_mounted="$?"  # 0 means mounted

# Take actions
if [ "$is_mounted" = 0 ]; then
    # Device is fully mounted

    # First unmount device from the filesystem
    sudo umount "$mapped_device_path" || {
       notify-send "❌ Error" "Error unmounting $mapped_device_path from $mount_point."
       exit 1
    }

    # Cleanup remaining directory
    sudo rmdir "$mount_point" || {
        notify-send "⚠ Warning" "Could not cleanup $mount_point directory after unmounting $mapped_device_path."
    }

    # Lock the device, so it's not accessible
    sudo cryptsetup close "$device_name" || {
       notify-send "❌ Error" "Could not close $device_name. It's still unlocked (insecure)."
       exit 1
    }

    rm -rf ~/.cache/thumbnails/ ~/.thumbnails

    [ "$notify_success" = 0 ] && notify-send "✅ Drive encrypted" "Veracrypt device \"$device_name\" has been successfuly unounted and locked."
else
    if [ "$is_opened" = 0 ]; then
        # Device is not mounted, but it's opened (decrypted). We have to lock it.
        sudo cryptsetup close "$device_name" || {
            notify-send "❌ Error" "Could not close $device_name. It's still unlocked (insecure)."
            exit 1
        }

        [ "$notify_success" = 0 ] && notify-send "✅ Drive encrypted" "Veracrypt device \"$device_name\" has been successfuly locked."
    else
        # Device is fully locked

        # Prepare mountpoint directory
        sudo mkdir -p "$mount_point" || {
            notify-send "❌ Error" "Could create mountpoint in $mount_point"
            exit 1
        }

        # Unlock the deivce, so it's accessible
        $TERMINAL sudo cryptsetup --type tcrypt --veracrypt open "$image_path" "$device_name"
        if ! sudo cryptsetup status "$device_name" >/dev/null 2>&1; then
            notify-send "❌ Error" "Could open $device_name."
            exit 1
        fi

        # Mount the device in the filesystem
        sudo mount "$mapped_device_path" "$mount_point" || {
            notify-send "❌ Error" "Could mount \"$device_name\" device. Device is left unlocked and insecure!"
            exit 1
        }

        # Open mounted device
        $FILE_MANAGER "$mount_point" >/dev/null 2>&1 &

        [ "$notify_success" = 0 ] && notify-send "✅ Drive decrypted" "Veracrypt image $image_path has been successfuly decrypted and mapped to $mount_point."
    fi
fi
