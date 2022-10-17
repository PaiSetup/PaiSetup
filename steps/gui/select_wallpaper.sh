#!/bin/sh

# Convert to a png file if necessary
get_png_file() (
    file_path="$1"

    # If file does not exist, return error
    if ! [ -f "$file_path" ]; then
        echo "ERROR: Invalid path $file_path" >&2
        return 1
    fi
    file_path="$(realpath "$file_path")"

    # If file is already png, simply return
    if echo "$file_path" | grep -qi "\.png$"; then
        echo "Wallpaper: $file_path (no conversion needed)" >&2
        echo "$file_path"
        return
    fi

    # Get output path for conversion. We don't want to pollute our official Wallpapers dir,
    # so we dump it into /tmp in that case.
    if echo "$file_path" | grep -qi "/Wallpapers/"; then
        out_dir=/tmp
    else
        out_dir="$(dirname "$file_path")"
    fi

    # Convert file to png
    if mogrify -format png -path "$out_dir" "$file_path"; then
        file_path="$out_dir/$(basename "$file_path" | sed -E "s/\.[A-z]+$/\.png/g")"
        echo "Wallpaper: $file_path (conversion to png was done)" >&2
        echo "$file_path"
    else
        echo "ERROR: Conversion to png needed but failed" >&2
        return 1
    fi
)

# Generate theme color based on the png image
get_main_color() (
    file_path="$1"
    cache_directory="$HOME/.cache/LinuxSetupWallpapers"
    scheme_file_path="$cache_directory/$(basename "$file_path").colorscheme"

    if [ -f "$scheme_file_path" ]; then
        # Color was already calculated and we have it cached
        main_color="$(cat "$scheme_file_path")"
        echo "Main color: $main_color (loaded from cache $scheme_file_path)" >&2
    else
        # We have to calculate the color from image
        mkdir -p "$cache_directory"
        main_color="$(colors -n1 < "$file_path")"
        if [ -z "$main_color" ]; then
            echo "ERROR: Colors generation for $file_path failed" >&2
            return 1
        fi
        echo "$main_color" > "$scheme_file_path"
        echo "Main color: $main_color (calculated with $(which colors))" >&2
    fi
    echo "$main_color"
)

# Perform all application-specific configuration based on the new wallpaper and theme color
setup_apps() (
    echo "App setup" >&2

    file_path="$1"
    main_color="$2"

    # XResources (consumed by window managers)
    echo "  XResources" >&2
    xresources_theme_file=~/.config/XresourcesTheme
    xresources_main_file=~/.config/Xresources
    echo "$main_color" | awk '{ printf("#define COL_THEME%d %s\n", NR, $0)}' > "$xresources_theme_file"
    xrdb "$xresources_main_file"

    # Cava
    echo "  Cava" >&2
    printf "[color]\nforeground = '$main_color'\n" > ~/.config/cava/config

    # Wallpaper path (consumed by AwesomeWM)
    echo "  ~/.config/LinuxSetup/wallpaper" >&2
    ln -sf "$file_path" ~/.config/LinuxSetup/wallpaper

    # Gtk
    echo "  GTK theme"
    ( $LINUX_SETUP_ROOT/steps/gtk_theme/generate_widget_theme.sh | sed "s/^/  /g" ) &
    ( $LINUX_SETUP_ROOT/steps/gtk_theme/generate_icon_theme.sh | sed "s/^/  /g" ) &
)

# Execute WM-specific operations
setup_wm() (
    echo "WM setup ($WM)" >&2

    case "$WM" in
        "dwm")
            # If DWM calls this script, we have to set the wallpaper (DWM cannot do this)
            feh --bg-scale ~/.config/LinuxSetup/wallpaper
            ;;
        "awesome")
            # If AwesomeWM calls this script, it will restart shortly and load the new icons
            $LINUX_SETUP_ROOT/steps/awesome/colorize_icons.sh 2>&1 | sed "s/^/  /g"
            ;;
    esac

    reset_wm="$1"
    if [ "$reset_wm" != 0 ]; then
        echo "  resetting WM" >&2
        $LINUX_SETUP_ROOT/steps/gui/reset_wm.sh
    fi
)

# Execute above functions
file_path="$1"
[ -n "$2" ] && reset_wm="$2" || reset_wm=1
file_path="$(get_png_file "$file_path")"    || exit 1
main_color="$(get_main_color "$file_path")" || exit 1
setup_apps "$file_path" "$main_color"       || exit 1
setup_wm "$reset_wm"                        || exit 1
