from steps.step import Step
from pathlib import Path
from shutil import copyfile
import os
from steps.dotfiles import FileType, LinePlacement
from utils.log import log
import utils.external_project as ext
from utils import command
from steps.gui.gui import GuiStep


class DwmStep(GuiStep):
    def __init__(self, root_build_dir, fetch_git):
        super().__init__("Dwm")
        self.root_build_dir = root_build_dir
        self.fetch_git = fetch_git

    def _perform_impl(self):
        super()._perform_impl()

        current_step_dir = Path(__file__).parent

        dwm_dir = self.root_build_dir / "dwm"
        ext.download(
            "git://git.suckless.org/dwm",
            "6.2",
            dwm_dir,
            fetch=self.fetch_git,
            clean=True,
        )
        ext.make(dwm_dir, patches_dir=current_step_dir / "dwm")

        dwmblocks_dir = self.root_build_dir / "dwmblocks"
        ext.download(
            "https://github.com/torrinfail/dwmblocks",
            "96cbb453",
            dwmblocks_dir,
            fetch=self.fetch_git,
            clean=True,
        )
        ext.make(dwmblocks_dir, patches_dir=current_step_dir / "dwmblocks")

        dmenu_dir = self.root_build_dir / "dmenu"
        ext.download(
            "https://git.suckless.org/dmenu",
            "5.0",
            dmenu_dir,
            fetch=self.fetch_git,
            clean=True,
        )
        ext.make(dmenu_dir, patches_dir=current_step_dir / "dmenu")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("xorg-xsetroot")

        dependency_dispatcher.add_dotfile_section(
            ".xinitrc",
            "Load Xresources",
            [
                "xrdb ~/.config/Xresources &",
                'xrdb_pid="$!"',
            ],
        )

        super().express_dependencies(dependency_dispatcher)

        dependency_dispatcher.add_dotfile_section(
            ".xinitrc",
            "Run dwmblocks",
            ["dwmblocks &"],
        )

        dependency_dispatcher.add_dotfile_section(
            ".xinitrc",
            "Wait for commands which must complete before dwm starts",
            ['wait "$xrdb_pid"'],
        )

        dependency_dispatcher.add_dotfile_section(
            ".xinitrc",
            "Run DWM",
            ['dbus-launch --sh-syntax --exit-with-session "$LINUX_SETUP_ROOT/steps/dwm/launch_dwm.sh"'],
            line_placement=LinePlacement.End,
        )

        self._setup_xresources(dependency_dispatcher)
        self._setup_stalonetrayrc(dependency_dispatcher)

    def _setup_xresources(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_section(
            ".config/Xresources",
            "Theme colors",
            [
                '#include "Xresources.theme"',
                "#define COL_THEME2 #878787",
                "#define COL_THEME3 #555555",
            ],
            file_type=FileType.XResources,
        )
        dependency_dispatcher.add_dotfile_section(
            ".config/Xresources",
            "DWM/Dmenu constants",
            [
                "#define FOCUS #990000",
                "#define PADDING_PIXELS 10",
            ],
            file_type=FileType.XResources,
        )
        dependency_dispatcher.add_dotfile_section(
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
        dependency_dispatcher.add_dotfile_section(
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

    def _setup_stalonetrayrc(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_lines(
            ".config/stalonetrayrc",
            [
                "decorations none",
                "transparent false",
                "dockapp_mode none",
                "geometry 1x1-45+40",
                "max_geometry 10x1-45+40",
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
            file_type=FileType.ConfigFile,
        )
