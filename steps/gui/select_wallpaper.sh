#!/bin/sh

file_path="$1"
reset_wm="$2"
set_wallpaper_with_feh="$3"
[ -z "$reset_wm" ] && reset_wm=0
[ -z "$set_wallpaper_with_feh" ] && set_wallpaper_with_feh=0

# Generate theme colors based on the wallpaper
get_main_colors() (
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

main_colors="$(get_main_colors)"
if [ -n "$main_colors" ]; then
    # Save generated colors to a theme file
    theme_file=~/.config/XresourcesTheme
    echo "$main_colors" | awk '{ printf("#define COL_THEME%d %s\n", NR, $0)}' > "$theme_file"
    echo "Reloading colors" >&2

    # Set main color as default cava foreground
    main_color="$(echo "$main_colors" | head -1)"
    printf "[color]\nforeground = '$main_color'\n" > ~/.config/cava/config

    # Load theme colors
    xresources_file=~/.config/Xresources
    xrdb "$xresources_file"
else
    echo "Not reloading colors" >&2
fi

# Setup the wallpaper in predefined path
ln -sf "$file_path" ~/.config/LinuxSetup/wallpaper

# Execute post actions
if [ "$set_wallpaper_with_feh" != 0 ]; then
    feh --bg-scale ~/.config/LinuxSetup/wallpaper
fi
if [ "$reset_wm" != 0 ]; then
    $LINUX_SETUP_ROOT/steps/gui/reset_wm.sh
fi
