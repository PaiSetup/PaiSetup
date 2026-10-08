#!/bin/bash

# Prepare basic args
src_path="$HOME/multimedia"
dst_path="pc:multimedia"
debug_arg="--verbose"
#debug_arg="--dry-run"

# Prepare exclude string
encrypted_dirs=(climbing freestyle_football funny) # keep this in snc with mount_multimedia.sh
not_synced_dirs=(music_to_rate movies tv_series .debris)
not_synced_files=(.megaignore)
exclude=""
for dir in "${encrypted_dirs[@]}" "${not_synced_dirs[@]}"; do
    exclude+="${exclude:+,}${dir}/**"
done
for file in "${not_synced_files[@]}"; do
    exclude+=",${file}"
done
exclude="{${exclude}}"

# Execute
command="rclone sync $src_path $dst_path --immutable --delete-excluded --exclude=$exclude $debug_arg"
echo "$command"
eval "$command"
