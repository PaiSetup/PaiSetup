import os

from libqtile import bar, widget
from libqtile.config import Screen


class ScreenConfig:
    def __init__(self, colors):
        wallpaper_path = os.environ["XDG_CONFIG_HOME"]
        wallpaper_path = f"{wallpaper_path}/PaiSetup/wallpaper"

        self.screens = [
            Screen(
                top=self._create_bar(colors),
                wallpaper=wallpaper_path,
                wallpaper_mode="stretch",
            ),
        ]

    def _create_bar(self, colors):
        bar_widgets = [
            widget.GroupBox(
                # General
                highlight_method="block",
                disable_drag=True,
                padding=7,
                visible_groups=None,
                # Font colors
                inactive=colors["theme"],  # no windows, not selected
                active=colors["theme"],  # has windows, not selected
                block_highlight_text_color=colors["gray_light"],  # selected
                # Background colors
                background=colors["gray_light"],  # not selected
                this_current_screen_border=colors["theme"],  # selected
                # Unknown settings
                this_screen_border="#FF0000",
                foreground="#00FF00",
                urgent_text="#FFFF00",
                highlight_color="#00FFFF",
            ),
            widget.WindowName(
                background=colors["gray_light"],
                foreground=colors["theme"],
            ),
            widget.Prompt(),
            widget.TextBox("This is theme color", background=colors["theme"], foreground=colors["theme"]),
            # widget.StatusNotifier(),
            widget.Systray(),  # NB Systray is incompatible with Wayland, consider using StatusNotifier instead
            widget.Clock(format="%Y-%m-%d %a %I:%M %p"),
            widget.CurrentLayoutIcon(),
        ]
        bar_size = 24
        return bar.Bar(
            bar_widgets,
            bar_size,
            background="#00000000",
            # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
        )
