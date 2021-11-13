from steps.step import Step
from pathlib import Path
from shutil import copyfile
import os
from steps.dotfiles import FileType


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

        self._compile_remote_project(
            self.root_build_dir / "dmenu",
            "https://git.suckless.org/dmenu",
            "5.0",
            dwm_step_dir / "dmenu",
            self.setup_repo,
        )

    def setup_required_dotfiles(self, dotfiles_step):
        dwm_step_dir = Path(__file__).parent

        dotfiles_step.add_dotfile_lines(
            ".xinitrc",
            [
                "(sleep 0.1 ; xrandr --output Virtual-1 --mode 1920x1080) &",
                "(sleep 0.2 ; nitrogen --set-zoom-fill ~/Wallpapers/active) &",
                "picom -b --no-fading-openclose &",
                "dwmblocks &",
                "dunst -config ~/.dunstrc &",
                "",
                "while true; do",
                "    dwm >/dev/null 2>&1 || break",
                "done",
            ],
        )
        dotfiles_step.add_dotfile_symlink(
            src=dwm_step_dir / "dunstrc",
            link=".dunstrc",
            prepend_home_dir_src=False,
            prepend_home_dir_link=True,
        )

        dotfiles_step.add_dotfile_section(
            ".profile",
            "Load X Resources file",
            ["xrdb .Xresources"],
        )

        dotfiles_step.add_dotfile_lines(
            ".Xresources",
            [
                "dmenu.font: monospace:size=15",
                "dmenu.normfgcolor: #bbbbbb",
                "dmenu.normbgcolor: #222222",
                "dmenu.selfgcolor: #eeeeee",
                "dmenu.selbgcolor: #003b00",
            ],
            file_type=FileType.XResources,
        )

    def setup_required_packages(self, packages_step):
        packages_step.add_packages(
            [
                "xorg-xrandr",
                "xorg-xinit",
                "xorg-server",
                "xorg-xsetroot",
                "nitrogen",
                "picom",
                "dunst",
            ]
        )
