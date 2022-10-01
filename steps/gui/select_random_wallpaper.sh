#!/bin/sh

get_wallpapers_directories() {
    cache_directory="$HOME/.cache/LinuxSetupWallpapers"
    cache_file="$cache_directory/directories"
    if [ -f "$cache_file" ]; then
        cat "$cache_file"
    else
        find ~ -iname "Wallpapers" -type d | tee "$cache_file"
    fi
}

get_wallpapers_directories                                    |
    xargs -I{} find "{}" \( -name "*.png" -o -name "*.jpg" \) |
    shuf -n 1                                                 |
    xargs -I{} $LINUX_SETUP_ROOT/steps/gui/select_wallpaper.sh "{}" "$@"
