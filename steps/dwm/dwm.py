from steps.step import Step
from pathlib import Path


class DwmStep(Step):
    def __init__(self, root_build_dir, setup_repo):
        super().__init__("dwm")
        self.root_build_dir = root_build_dir
        self.setup_repo = setup_repo

    def _perform_impl(self):
        (Path(self.root_build_dir) / "dwm" / "config.h").unlink(True)
        (Path(self.root_build_dir) / "dwm" / "blocks.h").unlink(True)

        self._compile_remote_project(
            self.root_build_dir / "dwm",
            "git://git.suckless.org/dwm",
            "6.2",
            Path(__file__).parent / "dwm",
            self.setup_repo,
        )

        self._compile_remote_project(
            self.root_build_dir / "dwmblocks",
            "https://github.com/torrinfail/dwmblocks",
            "",
            Path(__file__).parent / "dwmblocks",
            self.setup_repo,
        )

    def get_required_packages(self):
        return [
            "xorg-xrandr",
            "xorg-xinit",
            "xorg-server",
            "xorg-xsetroot",
        ]
