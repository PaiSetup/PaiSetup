from libqtile.config import Click, Drag
from libqtile.lazy import lazy

from utils.modkeys import *


@lazy.function
def disable_all_window_floating(qtile):
    for window in qtile.current_group.windows:
        window.disable_floating()


class MouseConfig:
    def __init__(self):
        self.mouse = [
            Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
            Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
            Click([mod], "Button2", lazy.window.disable_floating()),
            Click([mod, shift], "Button2", disable_all_window_floating()),
        ]
