from steps.step import Step
from pathlib import Path
from shutil import copyfile
import os


class DwmStep(Step):
    def __init__(self, root_build_dir, setup_repo):
        super().__init__("dwm")
        self.root_build_dir = root_build_dir
        self.setup_repo = setup_repo

    def _perform_impl(self):
        dwm_step_dir = Path(__file__).parent

        (Path(self.root_build_dir) / "dwm" / "config.h").unlink(True)
        (Path(self.root_build_dir) / "dwmblocks" / "blocks.h").unlink(True)

        self._compile_remote_project(
            self.root_build_dir / "dwm",
            "git://git.suckless.org/dwm",
            "6.2",
            dwm_step_dir / "dwm",
            self.setup_repo,
        )

        self._compile_remote_project(
            self.root_build_dir / "dwmblocks",
            "https://github.com/torrinfail/dwmblocks",
            "96cbb453",
            dwm_step_dir / "dwmblocks",
            self.setup_repo,
        )

        copyfile(dwm_step_dir / "xinitrc", f"{os.environ['HOME']}/.xinitrc")
        copyfile(dwm_step_dir / "dunstrc", f"{os.environ['HOME']}/.dunstrc")

    def setup_required_packages(self, packages_step):
        packages_step.add_packages(
            [
                "xorg-xrandr",
                "xorg-xinit",
                "xorg-server",
                "xorg-xsetroot",
                "nitrogen",
                "picom",
                "dmenu",
                "dunst",
            ]
        )
