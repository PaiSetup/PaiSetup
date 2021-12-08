#!/bin/sh

# Generate theme colors based on the wallpaper
get_main_colors() (
    file_path="$1"
    cache_directory="/home/$USER/.cache/wallpaper_color_schemes"
    scheme_file_path="$cache_directory/$(basename "$file_path").colorscheme"

    if [ -f "$scheme_file_path" ]; then
        echo "Found cached colors at $scheme_file_path" >&2
        cat "$scheme_file_path"
    else
        mkdir -p "$cache_directory"
        colors -n1 < "$file_path" | tee "$scheme_file_path"
        echo "Caching colors at $scheme_file_path" >&2
    fi
)
theme_file=~/.config/Xresources.theme
get_main_colors "$1" | awk '{ printf("#define COL_THEME%d %s\n", NR, $0)}' > "$theme_file"

# Load theme colors
xresources_file=~/.config/Xresources
xrdb "$xresources_file"

# Restart window manager (TODO: dwm is hardcoded)
kill -TERM  $(pgrep ^dwm$)

# Set wallpaper
nitrogen --set-zoom-fill "$1"
