from libqtile import bar, widget
from libqtile.config import Screen


class ScreenConfig:
    def __init__(self):
        self.screens = [
            Screen(top=self._create_bar()),
        ]

    def _create_bar(self):
        bar_widgets = [
            widget.CurrentLayoutIcon(),
            widget.GroupBox(),
            widget.Prompt(),
            widget.WindowName(),
            widget.Chord(
                chords_colors={
                    "launch": ("#ffff00", "#ffffff"),
                },
                name_transform=lambda name: name.upper(),
            ),
            widget.TextBox("default config", name="default"),
            widget.TextBox("Press &lt;M-r&gt; to spawn", foreground="#d75f5f"),
            # NB Systray is incompatible with Wayland, consider using StatusNotifier instead
            # widget.StatusNotifier(),
            widget.Systray(),
            widget.Clock(format="%Y-%m-%d %a %I:%M %p"),
        ]
        bar_size = 24
        return bar.Bar(
            bar_widgets,
            bar_size,
            background="#ff0000",
            # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
        )
