#!/bin/sh

trash_dir=$HOME/.local/share/Trash

while true; do
    printf "Cleanup $trash_dir (Y/N)? "
    read -r answer
    if [ "$answer" = y ] || [ "$answer" = Y ]; then
        printf "\nBefore:\n"
        du -sh "$trash_dir" | sed "s/^/    /g"

        printf "\nCleaning\n"
        sudo rm -rf "$trash_dir/files/"
        sudo rm -rf "$trash_dir/info/"

        printf "\nAfter:\n"
        du -sh "$trash_dir" | sed "s/^/    /g"

        break
    fi
    if [ "$answer" = n ] || [ "$answer" = N ]; then
        echo "Aborting..."
        break
    fi
done
read -r _
