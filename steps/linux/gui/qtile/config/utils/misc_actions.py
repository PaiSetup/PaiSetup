def disable_all_window_floating(qtile):
    for window in qtile.current_group.windows:
        window.disable_floating()
