#!/bin/sh

src_dir="$LINUX_SETUP_ROOT/steps/awesome/config/icons"
dst_dir="$LINUX_SETUP_ROOT/steps/awesome/config/icons_colorized"
mkdir -p "$dst_dir"
rm "$dst_dir"/* 2>/dev/null

echo "$src_dir"
echo "$dst_dir"

theme_color="$(xrdb -get color1)"
if [ -z "$theme_color" ]; then
    echo "WARNING: theme color is not set. Using white icons"
    find "$src_dir" -maxdepth 1 -type f -printf "%f\n" |
        xargs -I{} cp "$src_dir"/{} "$dst_dir"/{}
else
    echo "Colorizing icons to $theme_color"
    find "$src_dir" -maxdepth 1 -type f -printf "%f\n" |
        xargs -I{} convert "$src_dir"/{} -fill "$theme_color" -colorize 100 "$dst_dir"/{}
fi
