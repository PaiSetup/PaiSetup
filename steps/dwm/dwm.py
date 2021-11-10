from steps.step import SucklessSoftwareStep
from pathlib import Path


class DwmStep(SucklessSoftwareStep):
    def __init__(self):
        super().__init__(
            "dwm",
            "git://git.suckless.org/dwm",
            "6.2",
            Path(__file__).parent,
        )

    def get_required_packages(self):
        return ["xorg-xrandr", "xorg-xinit", "xorg-server", "xorg-xsetroot"]
