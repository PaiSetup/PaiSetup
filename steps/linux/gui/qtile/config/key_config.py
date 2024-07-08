from libqtile.config import Key
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal

from utils.modkeys import *


# A list of available commands that can be bound to keys can be found
# at https://docs.qtile.org/en/latest/manual/config/lazy.html
class KeyConfig:
    def __init__(self):
        self.keys = []
        self._append_layout_keys()
        self._append_general_keys()
        self._append_app_spawning_keys()
        self._append_wayland_vt_changing_keys()

    def append_group_keys(self, groups):
        for group in groups:
            i = group.name
            self.keys += [
                Key([mod], i, lazy.group[i].toscreen(), desc=f"Switch to group {i}"),
                Key([mod, shift], i, lazy.window.togroup(i), desc=f"Move focused window to group {i}"),
            ]

    def _append_layout_keys(self):
        self.keys += [
            # Switch between windows
            Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
            Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
            Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
            Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
            Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
            # Move windows between left/right columns or move up/down in current stack.
            # Moving out of range in Columns layout will create new column.
            Key([mod, shift], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
            Key([mod, shift], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
            Key([mod, shift], "j", lazy.layout.shuffle_down(), desc="Move window down"),
            Key([mod, shift], "k", lazy.layout.shuffle_up(), desc="Move window up"),
            # Grow windows. If current window is on the edge of screen and direction
            # will be to screen edge - window would shrink.
            Key([mod, ctrl], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
            Key([mod, ctrl], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
            Key([mod, ctrl], "j", lazy.layout.grow_down(), desc="Grow window down"),
            Key([mod, ctrl], "k", lazy.layout.grow_up(), desc="Grow window up"),
            Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
            # Toggle between split and unsplit sides of stack.
            # Split = all windows displayed
            # Unsplit = 1 window displayed, like Max layout, but still with
            # multiple stack panes
            Key([mod, shift], "Return", lazy.layout.toggle_split(), desc="Toggle between split and unsplit sides of stack"),
            # Toggle between different layouts as defined below
            Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
            Key([mod, shift], "c", lazy.window.kill(), desc="Kill focused window"),
            Key([mod], "f", lazy.window.toggle_fullscreen(), desc="Toggle fullscreen on the focused window"),
            Key([mod], "t", lazy.window.toggle_floating(), desc="Toggle floating on the focused window"),
        ]

    def _append_general_keys(self):
        self.keys += [
            Key([mod, ctrl], "r", lazy.reload_config(), desc="Reload the config"),
            Key([mod, ctrl], "w", lazy.restart(), desc="Shutdown Qtile"),
        ]

    def _append_app_spawning_keys(self):
        terminal = guess_terminal()
        self.keys += [
            Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
            Key([mod, shift], "Return", lazy.spawn(terminal), desc="Launch terminal"),
            Key([mod, shift], "KP_Enter", lazy.spawn(terminal), desc="Launch terminal"),
        ]

        from generated.app_keys import app_keys

        self.keys += app_keys

    def _append_wayland_vt_changing_keys(self):
        # This is taken from the default config. Not sure why, but it looks like it's needed for Wayland.
        for vt in range(1, 8):
            self.keys.append(
                Key(
                    ["control", "mod1"],
                    f"f{vt}",
                    lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
                    desc=f"Switch to VT{vt}",
                )
            )
