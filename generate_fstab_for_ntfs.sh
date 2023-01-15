#!/usr/bin/sh

partition="$1"

# Get metadata about partition
line="$(blkid | grep "^$partition: ")"
if [ $? != 0 ]; then
   echo "ERROR: invalid partition specified: \"$partition\". Valid partitions:"
   blkid | sed "s/^/    /g"
   exit 1
fi

# Verify type
type="$(echo "$line" | grep -oE "TYPE=\"[^\"]+\"")"
if [ $? != 0 ]; then
   echo "ERROR: could not get type of $partition."
   echo "    $line"
   exit 1
fi
if [ "$type" != "TYPE=\"ntfs\"" ]; then
   echo "ERROR: invalid type of $partition. Expected ntfs."
   echo "    $line"
   exit 1
fi

# Get UUID
uuid="$(echo "$line" | grep -oE " UUID=\"[^\"]+" | sed "s/.*\"//g")"
if [ $? != 0 ]; then
   echo "ERROR: could not get UUID of $partition."
   echo "    $line"
   exit 1
fi

# Get label
label="$(echo "$line" | grep -oE " LABEL=\"[^\"]+" | sed "s/.*\"//g")"
if [ $? != 0 ]; then
   echo "ERROR: could not get label of $partition."
   echo "    $line"
   exit 1
fi

# Generate /etc/fstab entry
mount_point="/mnt/$label"
options="ro,noauto"
echo "# $partition"
echo "UUID=$uuid       $mount_point      ntfs  $options 0 0"
