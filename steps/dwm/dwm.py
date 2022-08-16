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
        super().express_dependencies(dependency_dispatcher)

        dependency_dispatcher.add_packages(
            "xorg-xsetroot",
            "libxft-bgra",
            "ttf-joypixels",
            "ttf-font-awesome",
            "sxhkd",
            "dunst",
        )
        dependency_dispatcher.add_assumed_packages(
            [
                "libxft=2.3.3",  # Some packages have this as a dependency, but we actually need libxft-bgra
            ]
        )

        self._setup_xresources(dependency_dispatcher)
        self._setup_stalonetrayrc(dependency_dispatcher)
        self._setup_dunstrc(dependency_dispatcher)
        self._setup_sxhkdrc(dependency_dispatcher)
        self._setup_picom_config(dependency_dispatcher)

    def _setup_xinitrc(self, dependency_dispatcher):
        super()._setup_xinitrc(dependency_dispatcher)

        dependency_dispatcher.add_dotfile_section(
            ".config/LinuxSetup/xinitrc_dwm",
            "Call base script",
            [". ~/.config/LinuxSetup/xinitrc_base"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".config/LinuxSetup/xinitrc_dwm",
            "Load Xresources",
            ["xrdb ~/.config/Xresources"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".config/LinuxSetup/xinitrc_dwm",
            "Run dwmblocks",
            ["dwmblocks &"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".config/LinuxSetup/xinitrc_dwm",
            "Run picom",
            ["picom -b --no-fading-openclose --config ~/.config/LinuxSetup/picom_rounded.conf &"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".config/LinuxSetup/xinitrc_dwm",
            "Notification daemon",
            ["dunst &"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".config/LinuxSetup/xinitrc_dwm",
            "Keybindings daemon",
            ["sxhkd &"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".config/LinuxSetup/xinitrc_dwm",
            "Run DWM",
            ['dbus-launch --sh-syntax --exit-with-session "$LINUX_SETUP_ROOT/steps/dwm/launch_dwm.sh"'],
            line_placement=LinePlacement.End,
        )

        dependency_dispatcher.add_dotfile_symlink(src=".config/LinuxSetup/xinitrc_dwm", link=".xinitrc")

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

    def _setup_picom_config(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_lines(
            ".config/LinuxSetup/picom_rounded.conf",
            ["corner-radius = 8"],
        )

    def _setup_dunstrc(self, dependency_dispatcher):
        current_step_dir = Path(__file__).parent

        dependency_dispatcher.add_dotfile_symlink(
            src=current_step_dir / "dunstrc",
            link=".config/dunst/dunstrc",
            prepend_home_dir_src=False,
            prepend_home_dir_link=True,
        )

    def _setup_sxhkdrc(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_lines(
            ".config/sxhkd/sxhkdrc",
            [
                "super + shift + {Return, KP_Enter}",
                "    $TERMINAL",
                "",
                "super + shift + {BackSpace, l}",
                "    $LINUX_SETUP_ROOT/steps/gui/shutdown.sh",
                "",
                "{XF86AudioMute, XF86AudioLowerVolume, XF86AudioRaiseVolume}",
                "    $LINUX_SETUP_ROOT/steps/gui/set_volume.sh {0,1,2} 1",
                "",
                "super + {XF86AudioLowerVolume, XF86AudioRaiseVolume}",
                "    $LINUX_SETUP_ROOT/steps/gui/set_brightness.sh {0,1}",
                "",
                "super + control + {XF86AudioLowerVolume, XF86AudioRaiseVolume}",
                "    $LINUX_SETUP_ROOT/steps/gui/access_rhythmbox.sh {3,2} 1",
                "",
                "super + shift + s",
                "    flameshot gui",
                "",
                "Print",
                "    flameshot screen -c",
                "",
                "super + shift + w",
                "    $LINUX_SETUP_ROOT/steps/gui/set_random_wallpaper.sh 0",
                "",
                "super + shift + b",
                "    $BROWSER",
                "",
                "super + control shift + b",
                "    $BROWSER_PRIVATE",
                "",
                "super + shift + e",
                "    $FILE_MANAGER",
                "",
                "super + shift + t",
                "    obsidian e",
                "",
            ],
            file_type=FileType.ConfigFile,
        )
