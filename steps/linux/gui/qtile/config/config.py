from group_config import GroupConfig
from key_config import KeyConfig
from layout_config import LayoutConfig
from mouse_config import MouseConfig
from screen_config import ScreenConfig
from widget_defaults_config import WidgetDefaultsConfig

from utils.xrdb import Xrdb

xrdb = Xrdb()
colors = {
    "theme": xrdb.get_resource("color1"),
    "gray_light": xrdb.get_resource("color2"),
    "gray_dark": xrdb.get_resource("color3"),
    "font": xrdb.get_resource("color4"),
}

# Create configs
group_config = GroupConfig()
key_config = KeyConfig()
layout_config = LayoutConfig()
screen_config = ScreenConfig(colors)
widget_defaults_config = WidgetDefaultsConfig()
mouse_config = MouseConfig()

# Late-calls on configs
key_config.append_group_keys(group_config.groups)

# Export variables for qtile
keys = key_config.keys
groups = group_config.groups
layouts = layout_config.layouts
floating_layout = layout_config.floating_layout
screens = screen_config.screens
extension_defaults = widget_defaults_config.extension_defaults
widget_defaults = widget_defaults_config.widget_defaults
mouse = mouse_config.mouse

# Miscellaneous exports for qtile
dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
auto_minimize = True
wl_input_rules = None
wmname = "LG3D"
