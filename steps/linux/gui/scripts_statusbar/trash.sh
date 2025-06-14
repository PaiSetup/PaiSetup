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
    $TERMINAL_CMD sh -c "$PAI_SETUP_ROOT/steps/linux/gui/scripts/cleanup_trash.sh"
fi

if [ "$size" -ge "$threshold" ]; then
    printf ""
else
    printf ""
fi

$PAI_SETUP_ROOT/steps/linux/gui/scripts/refresh_statusbar.sh "Trash" "refresh:warnings"
