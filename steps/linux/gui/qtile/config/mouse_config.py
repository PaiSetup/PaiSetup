from libqtile.config import Click, Drag
from libqtile.lazy import lazy

from utils.misc_actions import disable_all_window_floating
from utils.modkeys import *


class MouseConfig:
    def __init__(self):
        self.mouse = [
            Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
            Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
            Click([mod], "Button2", lazy.window.disable_floating()),
            Click([mod, shift], "Button2", lazy.function(disable_all_window_floating)),
        ]
