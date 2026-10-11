#!/bin/bash

cleanup() {
    kill -9 "$cryptomator_pid" 2>/dev/null
    wait "$cryptomator_pid" 2>/dev/null
}
trap cleanup EXIT INT TERM

multimedia_dir="$HOME/multimedia"
encrypted_dirs=(climbing freestyle_football funny) # keep this in snc with sync_multimedia.sh
enc_vault_path="$HOME/multimedia/encrypted"
dec_vault_path="$HOME/.local/share/Cryptomator/mnt/encrypted_multimedia"
mounter=org.cryptomator.frontend.fuse.mount.LinuxFuseMountProvider

# Verify password is set
if ! secret-tool lookup PaiSetup multimedia_password >/dev/null; then
    echo "ERROR: multimedia password is not stored. Run" >&2
    echo "    secret-tool store PaiSetup multimedia_password --label PaiSetupMultimediaPassword"
    exit 1
fi

# Prepare symlinks
for dir in "${encrypted_dirs[@]}"; do
    ln -sT "$dec_vault_path/$dir" "$multimedia_dir/$dir"
done

# Execute
secret-tool lookup PaiSetup multimedia_password | cryptomator-cli unlock --mountPoint $dec_vault_path --mounter=$mounter --password:stdin $enc_vault_path &
cryptomator_pid=$!
wait "$cryptomator_pid"
