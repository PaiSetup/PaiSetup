from steps.step import Step
from pathlib import Path
from shutil import copyfile
import os
from steps.dotfiles import FileType, LinePlacement
from utils.keybinding import KeyBinding
from utils.log import log
import utils.external_project as ext
from utils import command
from steps.gui.gui import GuiStep


class DwmStep(GuiStep):
    def __init__(self, root_build_dir, fetch_git):
        super().__init__("Dwm")
        self.root_build_dir = root_build_dir
        self.fetch_git = fetch_git

        self._dwm_config_path = ".config/LinuxSetup/dwm"
        self._xresources_path = f"{self._dwm_config_path}/Xresources"
        self._xinitrc_path = f"{self._dwm_config_path}/xinitrc"
        self._picom_config_path = f"{self._dwm_config_path}/picom.conf"
        self._dunst_config_path = f"{self._dwm_config_path}/dunstrc"
        self._sxhkd_config_path = f"{self._dwm_config_path}/sxhkdrc"

        self._keybindings = [
            KeyBinding("w").mod().shift().executeShell("$LINUX_SETUP_ROOT/steps/dwm/set_random_wallpaper.sh 0"),
        ]

    def register_as_dependency_listener(self, dependency_dispatcher):
        dependency_dispatcher.register_listener(self.add_keybindings)

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

        self._setup_sxhkdrc()

    def express_dependencies(self, dependency_dispatcher):
        super().express_dependencies(dependency_dispatcher)

        dependency_dispatcher.add_packages(
            "xorg-xsetroot",
            "ttf-joypixels",
            "ttf-font-awesome",
            "sxhkd",
            "dunst",
            "stalonetray",
        )

        self._setup_xinitrc_dwm(dependency_dispatcher)
        self._setup_xresources(dependency_dispatcher)
        self._setup_stalonetrayrc(dependency_dispatcher)
        self._setup_dunstrc(dependency_dispatcher)
        self._setup_picom_config(dependency_dispatcher)

    def _setup_xinitrc_dwm(self, dependency_dispatcher):
        # TODO make xinitrc files executable!!!

        dependency_dispatcher.add_dotfile_section(
            self._xinitrc_path,
            "Call base script",
            [". ~/.config/LinuxSetup/xinitrc_base"],
        )
        dependency_dispatcher.add_dotfile_section(
            self._xinitrc_path,
            "Load Xresources",
            [
                "rm ~/.config/Xresources 2>/dev/null",
                f"ln -sf ~/{self._xresources_path} ~/.config/Xresources",
                f"xrdb ~/.config/Xresources",
            ],
        )
        dependency_dispatcher.add_dotfile_section(
            self._xinitrc_path,
            "Run dwmblocks",
            ["dwmblocks &"],
        )
        dependency_dispatcher.add_dotfile_section(
            self._xinitrc_path,
            "Run picom",
            [f"picom -b --no-fading-openclose --config ~/{self._picom_config_path} &"],
        )
        dependency_dispatcher.add_dotfile_section(
            self._xinitrc_path,
            "Notification daemon",
            [f"dunst -conf ~/{self._dunst_config_path} &"],
        )
        dependency_dispatcher.add_dotfile_section(
            self._xinitrc_path,
            "Keybindings daemon",
            [f"sxhkd -c ~/{self._sxhkd_config_path} &"],
        )
        dependency_dispatcher.add_dotfile_section(
            self._xinitrc_path,
            "Run DWM",
            ['dbus-launch --sh-syntax --exit-with-session "$LINUX_SETUP_ROOT/steps/dwm/launch_dwm.sh"'],
            line_placement=LinePlacement.End,
        )

        dependency_dispatcher.add_dotfile_symlink(src=self._xinitrc_path, link=".xinitrc")

    def _setup_xresources(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_section(
            self._xresources_path,
            "Apps styles",
            [f'#include "{os.environ["HOME"]}/.config/XresourcesApp"'],
            file_type=FileType.XResources,
        )
        dependency_dispatcher.add_dotfile_section(
            self._xresources_path,
            "Theme colors",
            [
                f'#include "{os.environ["HOME"]}/.config/XresourcesTheme"',
                "#define COL_THEME2 #878787",
                "#define COL_THEME3 #555555",
            ],
            file_type=FileType.XResources,
        )
        dependency_dispatcher.add_dotfile_section(
            self._xresources_path,
            "DWM/Dmenu constants",
            [
                "#define FOCUS #990000",
                "#define PADDING_PIXELS 10",
            ],
            file_type=FileType.XResources,
        )
        dependency_dispatcher.add_dotfile_section(
            self._xresources_path,
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
            self._xresources_path,
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
            self._picom_config_path,
            ["corner-radius = 8"],
        )

    def _setup_dunstrc(self, dependency_dispatcher):
        current_step_dir = Path(__file__).parent

        dependency_dispatcher.add_dotfile_symlink(
            src=current_step_dir / "dunstrc",
            link=self._dunst_config_path,
            prepend_home_dir_src=False,
            prepend_home_dir_link=True,
        )

    def _setup_sxhkdrc(self):
        # TODO convert this to normal keybindings
        hardcoded_lines = [
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
        ]
        self._file_writer.write_lines(self._sxhkd_config_path, hardcoded_lines, file_type=FileType.ConfigFile)

        for keybinding in self._keybindings:
            tokens = []
            if keybinding.hold_mod:
                tokens.append("super")
            if keybinding.hold_shift:
                tokens.append("shift")
            if keybinding.hold_ctrl:
                tokens.append("ctrl")
            tokens.append(f"{{{', '.join(keybinding.keys)}}}")

            lines = [
                " + ".join(tokens),
                f"    {keybinding.command}",
                "",
            ]
            self._file_writer.write_lines(self._sxhkd_config_path, lines, file_type=FileType.ConfigFile)

    def add_keybindings(self, *keybindings, **kwargs):
        self._keybindings += list(keybindings)
