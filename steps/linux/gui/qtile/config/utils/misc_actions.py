def set_random_wallpaper(qtile):
    pai_setup_root = "/home/maciej/linux_setup"
    script = f"{pai_setup_root}/steps/linux/gui/scripts/select_random_wallpaper.sh"
    qtile.spawn(script)  # TODO this should be called async
    qtile.restart()  # TODO  this does not wait for the script


def disable_all_window_floating(qtile):
    for window in qtile.current_group.windows:
        window.disable_floating()
