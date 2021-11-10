from steps.step import Step
from pathlib import Path


class DwmStep(Step):
    def __init__(self):
        super().__init__("dwm")

    def _perform_impl(self, root_build_dir):
        self._compile_remote_project(
            root_build_dir / "dwm",
            "git://git.suckless.org/dwm",
            "6.2",
            Path(__file__).parent / "dwm",
            True,
        )

        self._compile_remote_project(
            root_build_dir / "dwmblocks",
            "https://github.com/torrinfail/dwmblocks",
            "",
            Path(__file__).parent / "dwmblocks",
            True,
        )

    def get_required_packages(self):
        return [
            "xorg-xrandr",
            "xorg-xinit",
            "xorg-server",
            "xorg-xsetroot",
        ]
