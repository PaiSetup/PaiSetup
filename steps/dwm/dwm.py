from steps.step import Step
from pathlib import Path
from shutil import copyfile
import os
from steps.dotfiles import FileType, LinePlacement
from utils.log import log
from utils import command
from steps.graphical_env.graphical_env import GraphicalEnvStep


class DwmStep(GraphicalEnvStep):
    def __init__(self, root_build_dir, setup_repo):
        super().__init__("Dwm")
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

    def setup_required_packages(self, packages_step):
        super().setup_required_packages(packages_step)
        packages_step.add_packages(
            [
                "xorg-xrandr",
                "xorg-xinit",
                "xorg-server",
                "xorg-xsetroot",
                "xorg-setxkbmap",
            ]
        )

    def setup_required_dotfiles(self, dotfiles_step):
        dotfiles_step.add_dotfile_section(
            ".xinitrc",
            "Load XResources",
            [
                "xrdb ~/.Xresources &",
                'xrdb_pid="$!"',
            ],
        )

        super().setup_required_dotfiles(dotfiles_step)

        dotfiles_step.add_dotfile_section(
            ".xinitrc",
            "Run dwmblocks",
            ["dwmblocks &"],
        )

        dotfiles_step.add_dotfile_section(
            ".xinitrc",
            "Wait for commands which must complete before dwm starts",
            ['wait "$xrdb_pid"'],
        )

        dotfiles_step.add_dotfile_section(
            ".xinitrc",
            "Run DWM",
            ['dbus-launch --sh-syntax --exit-with-session "$LINUX_SETUP_ROOT/steps/dwm/launch_dwm.sh"'],
        )

        self._setup_xresources(dotfiles_step)

    def _setup_xresources(self, dotfiles_step):
        dotfiles_step.add_dotfile_section(
            ".Xresources",
            "Constants",
            [
                "#define WEIRD #ff00ff",
                "#define DARK_BACKGROUND #222222",
                "#define LIGHT_BACKGROUND #555555",
                "#define FOCUS #990000",
                "#define THEME #000000",
                "#define FONT #008866",
            ],
            file_type=FileType.XResources,
        )
        dotfiles_step.add_dotfile_section(
            ".Xresources",
            "Dwm",
            [
                "dwm.vertpad: 10",
                "dwm.sidepad: 10",
                "dwm.gappx: 10",
                "dwm.borderpx: 3",
                "dwm.normbgcolor: DARK_BACKGROUND",
                "dwm.normbordercolor: DARK_BACKGROUND",
                "dwm.normfgcolor: FONT",
                "dwm.selbgcolor: FONT",
                "dwm.selbordercolor: FOCUS",
                "dwm.selfgcolor: DARK_BACKGROUND",
                "dwm.appbarbgcolord: LIGHT_BACKGROUND",
                "dwm.statusbarcolor1: FONT",
                "dwm.statusbarcolor2: DARK_BACKGROUND",
            ],
            file_type=FileType.XResources,
        )
        dotfiles_step.add_dotfile_section(
            ".Xresources",
            "Dmenu",
            [
                "dmenu.font: monospace:size=15",
                "dmenu.dmx: 10",
                "dmenu.dmy: 10",
                "dmenu.normfgcolor: FONT",
                "dmenu.normbgcolor: DARK_BACKGROUND",
                "dmenu.selfgcolor: DARK_BACKGROUND",
                "dmenu.selbgcolor: FONT",
            ],
            file_type=FileType.XResources,
        )
