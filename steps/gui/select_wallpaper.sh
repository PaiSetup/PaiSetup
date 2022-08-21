#!/bin/sh

do_notify="$2"
[ -z "$do_notify" ] && do_notify=0

# Generate theme colors based on the wallpaper
get_main_colors() (
    file_path="$1"
    cache_directory="$HOME/.cache/LinuxSetupWallpapers"
    scheme_file_path="$cache_directory/$(basename "$file_path").colorscheme"

    if [ -f "$scheme_file_path" ]; then
        echo "Found cached colors at $scheme_file_path" >&2
        cat "$scheme_file_path"
    else
        mkdir -p "$cache_directory"
        result="$(colors -n1 < "$file_path")"
        if [ -z "$result" ]; then
            echo "Colors generation for $file_path failed" >&2
            return 1
        fi

        echo "Caching colors at $scheme_file_path" >&2
        echo "$result"
        echo "$result" > "$scheme_file_path"
    fi
)

main_colors="$(get_main_colors "$1")"
if [ -n "$main_colors" ]; then
    # Save generated colors to a theme file
    theme_file=~/.config/XresourcesTheme
    echo "$main_colors" | awk '{ printf("#define COL_THEME%d %s\n", NR, $0)}' > "$theme_file"
    echo "Reloading colors" >&2

    # Load theme colors
    xresources_file=~/.config/Xresources
    xrdb "$xresources_file"
else
    echo "Not reloading colors" >&2
fi

ln -sf "$1" ~/.config/LinuxSetup/wallpaper
