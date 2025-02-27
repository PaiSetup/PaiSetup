#!/bin/sh

# Inputs
image_path="$1"                           # Path to encrypted partition file
mapping_name="$2"                         # Selected name passed to cryptsetup
mount_path="$3"                           # Path to decrypted partition
mapping_path="/dev/mapper/$mapping_name"  # Path of mapped partition inside devfs

# Constants
notify_success=0 # 0 means notify

# Current state
sudo cryptsetup status "$mapping_name" >/dev/null 2>&1
is_mapped="$?"  # 0 means opened
mount | grep -q "/dev/mapper/$mapping_name"
is_mounted="$?"  # 0 means mounted

# -------------------------------------------------------------------------- Functions realizing encryption/decryption

perform_map() {
    $TERMINAL_CMD sudo cryptsetup --type tcrypt --veracrypt open "$image_path" "$mapping_name"
    if ! sudo cryptsetup status "$mapping_name" >/dev/null 2>&1; then
        notify-send "❌ Error" "Could not map $mapping_name."
        return 1
    fi
}

perform_unmap() {
    sudo cryptsetup close "$mapping_name" || {
       notify-send "❌ Error" "Could not unmap $mapping_name. It's still unlocked (insecure)."
       return 1
    }
}

perform_mount() {
    sudo mkdir -p "$mount_path" || {
        notify-send "❌ Error" "Could not create mountpoint in $mount_path"
        return 1
    }
    sudo chown maciej "$mount_path" && sudo chgrp maciej "$mount_path" && sudo chmod 700 "$mount_path" || {
        notify-send "⚠ Warning" "Could not setup correct permissions for the mount point: $mount_path."
    }
    uid=$(id -u $(whoami))
    gid=$(id -g $(whoami))
    fmask=177 # File permissions. User: read-write, Group: none, Other: none
    dmask=077 # Directory permissions. User: read-write-execute, Group: none, Other: none
    sudo mount "$mapping_path" "$mount_path" -o uid=$uid,gid=$gid,fmask=$fmask,dmask=$dmask || {
        notify-send "❌ Error" "Could not mount \"$mapping_name\" device. Device is left unlocked and insecure!"
        return 1
    }
    $FILE_MANAGER "$mount_path" >/dev/null 2>&1 &
}

perform_umount() {
    sudo umount "$mapping_path" || {
       notify-send "❌ Error" "Error unmounting $mapping_path from $mount_path."
       return 1
    }
    sudo rmdir "$mount_path" || {
        notify-send "⚠ Warning" "Could not cleanup $mount_path directory after unmounting $mapping_path."
    }
    rm -rf ~/.cache/thumbnails/ ~/.thumbnails
}

# -------------------------------------------------------------------------- Main procedure
if [ "$is_mounted" = 0 ]; then
    # Partition is mapped and mounted (fully unlocked).
    perform_umount || exit 1
    perform_unmap  || exit 1
    [ "$notify_success" = 0 ] && notify-send "✅ Drive encrypted" "Veracrypt device \"$mapping_name\" is unmounted and unmapped."
else
    if [ "$is_mapped" = 0 ]; then
        # Partition is mapped, but not mounted.
        perform_unmap || exit 1
        [ "$notify_success" = 0 ] && notify-send "✅ Drive encrypted" "Veracrypt device \"$mapping_name\" is unmounted and unmapped."
    else
        # Partition is not mapped and not mounted (fully locked).
        perform_map   || exit 1
        perform_mount || {
            perform_unmap
            exit 1
        }
        [ "$notify_success" = 0 ] && notify-send "✅ Drive decrypted" "Veracrypt image \"$mapping_name\" is mapped and mounted to $mount_path."
    fi
fi

# Refresh status icons
$PAI_SETUP_ROOT/steps/linux/gui/scripts/refresh_statusbar.sh "Veracrypt" "15" "refresh:warnings"
