#!/usr/bin/sh

[ -n "$1" ] && BUTTON="$1"

trash_dir=$HOME/.local/share/Trash

size="$(du -s "$trash_dir" | awk '{ print $1; }')"
size=$((size * 1024))
threshold=$((5*1024*1024*1024))

[ "$BUTTON" = "$BUTTON_INFO" ] && notify-send "Trash directory" "$trash_dir contains $(numfmt --to=iec-i --suffix=B "$size")"
if [ "$BUTTON" = "$BUTTON_ACTION" ]; then
    $FILE_MANAGER $trash_dir
fi
if [ "$BUTTON" = "$BUTTON_TERMINATE" ]; then
    code=$(cat << EOM
while true; do
    printf "Cleanup $trash_dir (Y/N)? "
    read answer
    if [ "\$answer" = y -o "\$answer" = Y ]; then
        printf "\nBefore:\n"
        du -sh "$trash_dir" | sed "s/^/    /g"

        printf "\nCleaning\n"
        sudo rm -rf "$trash_dir/files/"
        sudo rm -rf "$trash_dir/info/"

        printf "\nAfter:\n"
        du -sh "$trash_dir" | sed "s/^/    /g"

        break
    fi
    if [ "\$answer" = n -o "\$answer" = N ]; then
        echo "Aborting..."
        break
    fi
done
read _
EOM
)
    $TERMINAL sh -c "$code"
fi

if [ "$size" -ge "$threshold" ]; then
    printf ""
else
    printf ""
fi
