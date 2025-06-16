#!/bin/sh

# Prepare our color palette
COLOR_THEME="$(xrdb -get color1)"
COLOR_GRAY_LIGHT="$(xrdb -get color2)"
COLOR_FONT="$(xrdb -get color4)"

# Prepare theme directory
src_theme_dir="$PAI_SETUP_ROOT/build/gtk_icon_theme"
dst_theme_dir="$HOME/.local/share/icons/PaiSetupIconTheme"
rm -rf "$dst_theme_dir"
mkdir -p "$dst_theme_dir"

# Helper functions
colorize_directory() (
    suffix="$1"
    sed_pattern="$2"
    echo "Colorizing $suffix"

    IFS="
    "
    mkdir -p "$dst_theme_dir/$suffix"
    for file in $(find "$src_theme_dir/$suffix" -type f -printf "%f\n"); do
        sed "$sed_pattern" "$src_theme_dir/$suffix/$file" > "$dst_theme_dir/$suffix/$file"
    done
    for file in $(find "$src_theme_dir/$suffix" -type l -printf "%f\n"); do
        cp --no-dereference "$src_theme_dir/$suffix/$file" "$dst_theme_dir/$suffix/$file"
    done
)
symlink_directory() {
    suffix="$1"
    echo "Symlinking $suffix"

    dst_dir="$(dirname "$dst_theme_dir/$suffix")"
    mkdir -p "$dst_dir"
    ln -s "$src_theme_dir/$suffix" "$dst_dir"
}
copy_directory() {
    suffix="$1"
    cp --no-dereference "$src_theme_dir/$suffix" "$dst_theme_dir/$suffix"
}
big_pattern="s/#7DC4E4/$COLOR_GRAY_LIGHT/g;s/#24273A/$COLOR_THEME/g;s/#F5A97F/$COLOR_FONT/g"
small_pattern="s/#F5A97F/$COLOR_THEME/g"

# Simply symlink some directories or colorize icons in them (more expensive)
mkdir -p "$dst_theme_dir/emblems"
ln -s              "$PAI_SETUP_ROOT/steps/linux/gtk_theme/emblems_64" "$dst_theme_dir/emblems/64"
ln -s              "$PAI_SETUP_ROOT/steps/linux/gtk_theme/emblems_512" "$dst_theme_dir/emblems/512"
symlink_directory  "emblems/48"
symlink_directory  "index.theme"
symlink_directory  "emotes"
symlink_directory  "intl"
symlink_directory  "mimetypes/64"
symlink_directory  "scalable-max-32"
symlink_directory  "status"
symlink_directory  "stock"
copy_directory     "categories"

colorize_directory "places/64" "$big_pattern"
colorize_directory "places/16" "$small_pattern"
colorize_directory "actions/16" "$small_pattern"
colorize_directory "devices/16" "$small_pattern"
colorize_directory "animations/24" "$small_pattern"
colorize_directory "mimetypes/16" "$small_pattern"
# colorize_directory "panel/24" "$big_pattern" # Removed this, it wouldn't be used
colorize_directory "apps/16" "$small_pattern"

# Flush caches
gtk-update-icon-cache
