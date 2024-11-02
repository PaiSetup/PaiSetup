#!/bin/sh

trash_dir=$HOME/.local/share/Trash

while true; do
    printf "Cleanup $trash_dir (Y/N)? "
    read answer
    echo "WTF: $answer"
    if [ "$answer" = y -o "$answer" = Y ]; then
        printf "\nBefore:\n"
        du -sh "$trash_dir" | sed "s/^/    /g"

        printf "\nCleaning\n"
        sudo rm -rf "$trash_dir/files/"
        sudo rm -rf "$trash_dir/info/"

        printf "\nAfter:\n"
        du -sh "$trash_dir" | sed "s/^/    /g"

        break
    fi
    if [ "$answer" = n -o "$answer" = N ]; then
        echo "Aborting..."
        break
    fi
done
read _
