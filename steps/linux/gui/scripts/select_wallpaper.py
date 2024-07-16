#!/bin/python

import argparse
import os
import random
from pathlib import Path

from utils.command import CommandError, Stdin, Stdout, run_command


class SelectWallpaperException(Exception):
    pass


def get_random_wallpaper_file(home, cache_dir):
    # Get a list of directories with wallpapers.
    cache_file = cache_dir / "directories"
    if cache_file.is_file():
        # The list of directories is cached
        with open(cache_file, "r") as f:
            wallpaper_dirs = f.readlines()
            wallpaper_dirs = [Path(x.strip()) for x in wallpaper_dirs]
    else:
        # The list of directories is not cached, we have to generate it. This could just be
        # hardcoded, but we'll search for directories named "wallpapers" to be more flexible.
        wallpaper_dirs = []
        for root, dirs, files in os.walk(home, topdown=False):
            for d in dirs:
                if d == "wallpapers":
                    wallpaper_dirs.append(Path(root) / d)

        # Cache list of directories we've just generated.
        with open(cache_file, "w") as f:
            lines = [f"{x}\n" for x in wallpaper_dirs]
            f.writelines(lines)

    # Get a list of potential wallpapers
    wallpapers = []
    for wallpaper_dir in wallpaper_dirs:
        wallpapers += [x for x in wallpaper_dir.iterdir() if x.suffix in [".png", ".jpg"]]

    # Randomize a wallpaper
    return random.choice(wallpapers)


def convert_to_png(wallpaper_file):
    # If file does not exist, return error.
    if not wallpaper_file.is_file():
        raise SelectWallpaperException(f"{wallpaper_file} does not exist.")

    # If file is already png, simply return the file path.
    if wallpaper_file.suffix == ".png":
        return wallpaper_file

    # Convert to png.
    out_dir = wallpaper_file.parent
    convert_command = f'mogrify -format png -path "{out_dir}" "{wallpaper_file}"'
    try:
        run_command(convert_command)
    except CommandError:
        raise SelectWallpaperException(f"Failed to convert {wallpaper_file} to png format.")

    # Return converted file's path.
    converted_file = wallpaper_file.with_suffix(".png")
    if not converted_file.is_file():
        raise SelectWallpaperException(f"Converted {wallpaper_file} to png, but {converted_file} does not exist.")
    return converted_file


def generate_main_color(wallpaper_file, cache_dir):
    cache_file = f"{wallpaper_file.name}.colorscheme"
    cache_file = cache_dir / cache_file

    if cache_file.is_file():
        # Color was already calculated and we have it cached
        with open(cache_file, "r") as f:
            main_color = f.readline().strip()
    else:
        # We have to calculate the color from image
        cache_dir.mkdir(parents=True, exist_ok=True)
        with open(wallpaper_file, "rb") as f:
            try:
                main_color = run_command("colors -n1", stdin=Stdin.file(f), stdout=Stdout.return_back())
                main_color = main_color.strip()
            except CommandError:
                raise (f"Failed to generate colors for {wallpaper_file}")

        # Save it to cache
        with open(cache_file, "w") as f:
            f.write(f"{main_color}\n")

    return main_color


def setup_xresources(xresources_main_path, xresources_theme_path, main_color):
    # Xresources theme is consumed by window managers and some apps.
    print(f"  Setting Xresources theme file: {xresources_theme_path}")
    with open(xresources_theme_path, "w") as f:
        line = f"#define COL_THEME1 {main_color}\n"
        f.write(line)

    # Load Xresources main file to the XServer. This file includes the theme file
    # we just produced.
    print(f"  Loading Xresources main file: {xresources_main_path}")
    try:
        xrdb_command = f"xrdb {xresources_main_path}"
        run_command(xrdb_command)
    except CommandError:
        raise SelectWallpaperException(f"Failed to run {xrdb_command}.")


def setup_cava_theme(cava_config_path, main_color):
    print(f"  Setting cava config: {cava_config_path}")
    with open(cava_config_path, "w") as f:
        lines = [
            "[color]\n",
            f"foreground = {main_color}\n",
        ]
        f.writelines(lines)


def setup_current_wallpaper_symlink(wallpaper_file, current_wallpaper_symlink_path):
    # Defaul wallpaper is a symlink to an actual png file. It is consumed by window managers
    # during start and set as current wallpaper.
    print(f"  Setting symlink {current_wallpaper_symlink_path} -> {wallpaper_file}")
    current_wallpaper_symlink_path.unlink(missing_ok=True)
    os.symlink(wallpaper_file, current_wallpaper_symlink_path)


def setup_gtk_theme(pai_setup_root):
    print(f"  Generating GTK widget and icon theme (in background)")
    gtk_theme_scripts_path = pai_setup_root / "steps/linux/gtk_theme"
    run_command(f"{gtk_theme_scripts_path}/generate_widget_theme.sh", background=True)
    run_command(f"{gtk_theme_scripts_path}/generate_icon_theme.sh", background=True)


def setup_wm(pai_setup_root, wm):
    match wm:
        case "dwm":
            # If DWM calls this script, we have to set the wallpaper (DWM cannot do this)
            # TODO create a patch for DWM to set the wallpaper. It will be cleaner.
            print("  Setting wallpaper for DWM")
            run_command("feh --bg-scale ~/.config/PaiSetup/wallpaper")
        case "awesome":
            # If AwesomeWM calls this script, it will restart shortly and load the new icons
            print("  Generating colored icons for AwesomeWM")
            command = str(pai_setup_root / "steps/linux/gui/awesome/colorize_icons.sh")
            run_command(command)
        case "qtile":
            pass


def restart_wm(pai_setup_root, restart_wm, wm):
    if restart_wm:
        print(f"  Resetting {wm}")
        command = str(pai_setup_root / "steps/linux/gui/scripts/restart_wm.sh")
        run_command(command)


if __name__ == "__main__":
    home = Path(os.environ["HOME"])
    wm = os.environ["WM"]
    pai_setup_root = Path(os.environ["PAI_SETUP_ROOT"])

    # fmt: off
    arg_parser = argparse.ArgumentParser(description="Set a wallpaper", allow_abbrev=False)
    arg_parser.add_argument("-f", "--wallpaper_file", type=Path,           help="Path to a wallpaper to set.")
    arg_parser.add_argument("-r", "--restart_wm",     action="store_true", help="Reset the window manager after setting up wallpaper and colorschemes.")
    path_args = arg_parser.add_argument_group("Path arguments", "These arguments have sane defaults and should generally be left unchanged.")
    path_args.add_argument("--cache_dir",                      type=Path, default=home/".cache/PaiSetupWallpapers",            help="Directory for wallpaper setting cache. The script caches colorschemes and wallpaper directories")
    path_args.add_argument("--xresources_theme_path",          type=Path, default=home/".config/XresourcesTheme",              help="Path to Xresources file storing wallpaper-specific theme.")
    path_args.add_argument("--xresources_main_path",           type=Path, default=home/".config/PaiSetup" / wm / "Xresources", help="Path to main Xresources file.")
    path_args.add_argument("--cava_theme_file",                type=Path, default=home/".config/cava/config",                  help="Path to cava theme file.")
    path_args.add_argument("--current_wallpaper_symlink_path", type=Path, default=home/".config/PaiSetup/wallpaper",           help="Path for a symlink to the wallpaper that can be used by window managers.")
    args = arg_parser.parse_args()
    # fmt: on

    if args.wallpaper_file is None:
        wallpaper_file = get_random_wallpaper_file(home, args.cache_dir)
    wallpaper_file = convert_to_png(wallpaper_file)
    main_color = generate_main_color(wallpaper_file, args.cache_dir)
    print(f"Setting a wallpaper {wallpaper_file}")
    print(f"  main_color={main_color}")

    setup_xresources(args.xresources_main_path, args.xresources_theme_path, main_color)
    setup_cava_theme(args.cava_theme_file, main_color)
    setup_current_wallpaper_symlink(wallpaper_file, args.current_wallpaper_symlink_path)
    setup_gtk_theme(pai_setup_root)
    setup_wm(pai_setup_root, wm)
    restart_wm(pai_setup_root, args.restart_wm, wm)
