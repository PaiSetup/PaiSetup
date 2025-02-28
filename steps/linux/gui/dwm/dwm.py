import os
from pathlib import Path
from shutil import copyfile

import utils.external_project as ext
from steps.linux.check_mate.check_mate import CheckMateStep
from steps.linux.gui.gui import GuiStep
from steps.step import Step
from utils.command import *
from utils.dependency_dispatcher import push_dependency_handler
from utils.keybinding import KeyBinding
from utils.services.file_writer import FileType, LinePlacement


class DwmStep(GuiStep):
    def __init__(self, root_build_dir, full, is_default_wm):
        super().__init__("Dwm")
        self.root_build_dir = root_build_dir
        self._full = full
        self._current_step_dir = Path(__file__).parent

        self._config_path = ".config/PaiSetup/dwm"
        self._xresources_path = f"{self._config_path}/Xresources"
        self._xinitrc_path = f"{self._config_path}/xinitrc"

        self._picom_config_path = f"{self._config_path}/picom.conf"
        self._dunst_config_path = f"{self._config_path}/dunstrc"
        self._sxhkd_config_path = f"{self._config_path}/sxhkdrc"

        self._periodic_check_launch_script = f"{self._config_path}/run_check_mate.sh"
        self._periodic_check_profile = CheckMateStep.Profile(self._periodic_check_launch_script, self._xinitrc_path, is_default_profile=is_default_wm)

        # fmt: off
        self._keybindings = [
            KeyBinding("BackSpace").mod().shift().executeShell("$PAI_SETUP_ROOT/steps/linux/gui/dwm/shutdown_dmenu.sh"),
        ]
        # fmt: on

    def perform(self):
        super().perform()
        self._compile_projects()
        self._setup_xinitrc_dwm()
        self._setup_xresources()
        self._setup_stalonetrayrc()
        self._setup_dunstrc()
        self._setup_picom_config()
        self._setup_sxhkdrc()

    @push_dependency_handler
    def add_keybindings(self, *keybindings):
        self._keybindings += list(keybindings)

    def push_dependencies(self, dependency_dispatcher):
        super().push_dependencies(dependency_dispatcher)
        dependency_dispatcher.add_packages(
            "xorg-xsetroot",
            "sxhkd",
            "dunst",
            "stalonetray",
        )

        dependency_dispatcher.add_xsession("DWM", self._env.home() / self._xinitrc_path)

        dependency_dispatcher.register_periodic_daemon_check("dunst", "dunst", profile=self._periodic_check_profile)
        dependency_dispatcher.register_periodic_daemon_check("sxhkd", "sxhkd", profile=self._periodic_check_profile)
        dependency_dispatcher.register_periodic_daemon_check("dwmblocks", "dwmblocks", profile=self._periodic_check_profile)

    def _compile_projects(self):
        if ext.should_build(self._full, ["dwm"]):
            dwm_dir = self.root_build_dir / "dwm"
            ext.download(
                "https://git.suckless.org/dwm",
                "6.2",
                dwm_dir,
                logger=self._logger,
                fetch=self._full,
                clean=True,
            )
            ext.make(dwm_dir, patches_dir=self._current_step_dir / "dwm", logger=self._logger)

        if ext.should_build(self._full, ["dwmblocks"]):
            dwmblocks_dir = self.root_build_dir / "dwmblocks"
            ext.download(
                "https://github.com/torrinfail/dwmblocks",
                "96cbb453",
                dwmblocks_dir,
                logger=self._logger,
                fetch=self._full,
                clean=True,
            )
            ext.make(dwmblocks_dir, patches_dir=self._current_step_dir / "dwmblocks", logger=self._logger)

        if ext.should_build(self._full, ["dmenu"]):
            dmenu_dir = self.root_build_dir / "dmenu"
            ext.download(
                "https://git.suckless.org/dmenu",
                "5.0",
                dmenu_dir,
                logger=self._logger,
                fetch=self._full,
                clean=True,
            )
            ext.make(dmenu_dir, patches_dir=self._current_step_dir / "dmenu", logger=self._logger)

    def _setup_xinitrc_dwm(self):
        self._file_writer.write_section(
            self._xinitrc_path,
            "Call base script",
            [
                "export WM=dwm",
                ". ~/.config/PaiSetup/xinitrc_base",
            ],
        )
        self._file_writer.write_section(
            self._xinitrc_path,
            "Run dwmblocks",
            ["dwmblocks &"],
        )
        self._file_writer.write_section(
            self._xinitrc_path,
            "Run picom",
            [f"picom -b --no-fading-openclose --config ~/{self._picom_config_path} &"],
        )
        self._file_writer.write_section(
            self._xinitrc_path,
            "Notification daemon",
            [f"dunst -conf ~/{self._dunst_config_path} &"],
        )
        self._file_writer.write_section(
            self._xinitrc_path,
            "Keybindings daemon",
            [f"sxhkd -c ~/{self._sxhkd_config_path} &"],
        )
        self._file_writer.write_section(
            self._xinitrc_path,
            "Run DWM",
            ['dbus-launch --sh-syntax --exit-with-session "$PAI_SETUP_ROOT/steps/linux/gui/dwm/launch_dwm.sh"'],
            line_placement=LinePlacement.End,
        )

    def _setup_xresources(self):
        self._file_writer.write_section(
            self._xresources_path,
            "Apps styles",
            [f'#include "{self._env.home() / ".config/XresourcesApp"}"'],
            file_type=FileType.XResources,
        )
        self._file_writer.write_section(
            self._xresources_path,
            "Theme colors",
            [
                f'#include "{self._env.home() / ".config/XresourcesTheme"}"',
                "#define COL_THEME2 #878787",
                "#define COL_THEME3 #555555",
            ],
            file_type=FileType.XResources,
        )
        self._file_writer.write_section(
            self._xresources_path,
            "DWM/Dmenu constants",
            [
                "#define FOCUS #990000",
                "#define PADDING_PIXELS 10",
            ],
            file_type=FileType.XResources,
        )
        self._file_writer.write_section(
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
        self._file_writer.write_section(
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

    def _setup_stalonetrayrc(self):
        self._file_writer.write_lines(
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

    def _setup_picom_config(self):
        self._file_writer.write_lines(
            self._picom_config_path,
            ["corner-radius = 8"],
        )

    def _setup_dunstrc(self):
        self._file_writer.write_symlink(
            src=self._current_step_dir / "dunstrc",
            link=self._dunst_config_path,
        )

    def _setup_sxhkdrc(self):
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
