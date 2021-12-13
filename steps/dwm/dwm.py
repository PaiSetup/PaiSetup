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
        super()._perform_impl()

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
                "stalonetray",
                "yad",
            ]
        )

    def setup_required_dotfiles(self, dotfiles_step):
        dotfiles_step.add_dotfile_section(
            ".xinitrc",
            "Load Xresources",
            [
                "xrdb ~/.config/Xresources &",
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

        self._setup_stalonetrayrc(dotfiles_step)

    def _setup_xresources(self, dotfiles_step):
        super()._setup_xresources(dotfiles_step)

        dotfiles_step.add_dotfile_section(
            ".config/Xresources",
            "Constants",
            [
                "#define FOCUS #990000",
                "#define PADDING_PIXELS 10",
            ],
            file_type=FileType.XResources,
        )
        dotfiles_step.add_dotfile_section(
            ".config/Xresources",
            "Dwm",
            [
                "dwm.vertpad: PADDING_PIXELS",
                "dwm.sidepad: PADDING_PIXELS",
                "dwm.gappx: PADDING_PIXELS",
                "dwm.borderpx: 0",
                "dwm.normbgcolor: COL_THEME2",
                "dwm.normbordercolor: COL_THEME2",
                "dwm.normfgcolor: COL_THEME1",
                "dwm.selbgcolor: COL_THEME1",
                "dwm.selbordercolor: FOCUS",
                "dwm.selfgcolor: COL_THEME2",
                "dwm.appbarbgcolord: COL_THEME3",
                "dwm.statusbarcolor1: COL_THEME1",
                "dwm.statusbarcolor2: COL_THEME2",
            ],
            file_type=FileType.XResources,
        )
        dotfiles_step.add_dotfile_section(
            ".config/Xresources",
            "Dmenu",
            [
                "dmenu.font: monospace:size=15",
                "dmenu.dmx: PADDING_PIXELS",
                "dmenu.dmy: PADDING_PIXELS",
                "dmenu.normfgcolor: COL_THEME1",
                "dmenu.normbgcolor: COL_THEME2",
                "dmenu.selfgcolor: COL_THEME2",
                "dmenu.selbgcolor: COL_THEME1",
            ],
            file_type=FileType.XResources,
        )

    def _setup_stalonetrayrc(self, dotfiles_step):
        dotfiles_step.add_dotfile_lines(
            ".config/stalonetrayrc",
            [
                "decorations none",
                "transparent false",
                "dockapp_mode none",
                "geometry 1x1-60+40",
                "max_geometry 10x1-60+40",
                'background "#008866"',
                "grow_gravity NE",
                "icon_gravity NE",
                "icon_size 20",
                "slot_size 30",
                "sticky true",
                "window_strut none",
                "window_type dock",
                "window_layer bottom",
                "no_shrink false",
                "skip_taskbar true",
                "fuzzy_edges 3",
            ],
            file_type=FileType.Stalonetrayrc,
        )
