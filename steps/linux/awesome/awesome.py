from steps.step import Step, dependency_listener
from pathlib import Path
from shutil import copyfile
import os
from utils.file_writer import FileType, LinePlacement
from utils.log import log
import utils.external_project as ext
from utils import command
from ..gui.gui import GuiStep


class AwesomeStep(GuiStep):
    def __init__(self, root_build_dir, fetch_git, is_default_wm):
        super().__init__("Awesome")
        self.root_build_dir = root_build_dir
        self.fetch_git = fetch_git
        self._current_step_dir = Path(__file__).parent

        self._config_path = ".config/PaiSetup/awesome"
        self._xresources_path = f"{self._config_path}/Xresources"
        self._xinitrc_path = f"{self._config_path}/xinitrc"

        self._app_keybindings_path = f"{self._current_step_dir}/config/utils/app_keybindings.lua"
        self._keybindings = []

    @dependency_listener
    def add_keybindings(self, *keybindings, **kwargs):
        self._keybindings += keybindings

    def express_dependencies(self, dependency_dispatcher):
        super().express_dependencies(dependency_dispatcher)
        dependency_dispatcher.add_packages(
            "awesome",
            "lua", # not strictly needed, but useful for prototyping
            "jq", # needed for parsing json when getting currency exchange
        )
        dependency_dispatcher.add_xsession("AwesomeWM", self._env.home() / self._xinitrc_path)

    def perform(self):
        self._setup_awesome_config()
        self._setup_xinitrc_awesome()
        self._setup_xresources()
        self._setup_app_keybindings_code()

        # Awesome places this file during installation, but we don't need it,
        # we generate our own session files.
        self._file_writer.remove_file("/usr/share/xsessions/awesome.desktop")

    def _setup_awesome_config(self):
        log("Symlinking rc.lua into ~/.config")
        self._file_writer.write_symlink(
            src=self._current_step_dir / "config",
            link=".config/awesome",
        )

    def _setup_xinitrc_awesome(self):
        log(f"Generating {self._xinitrc_path}")
        self._file_writer.write_section(
            self._xinitrc_path,
            "Call base script",
            [
                "export WM=awesome",
                ". ~/.config/PaiSetup/xinitrc_base",
            ],
        )
        self._file_writer.write_section(
            self._xinitrc_path,
            "Load Xresources",
            [
                "rm ~/.config/Xresources 2>/dev/null",
                f"ln -sf ~/{self._xresources_path} ~/.config/Xresources",
                f"xrdb ~/.config/Xresources",
            ],
        )
        self._file_writer.write_section(
            self._xinitrc_path,
            "Define mouse button values for statusbar scripts",
            [
                "export BUTTON_ACTION=1",
                "export BUTTON_TERMINATE=2",
                "export BUTTON_INFO=3",
                "export BUTTON_SCROLL_UP=4",
                "export BUTTON_SCROLL_DOWN=5",
            ],
        )
        self._file_writer.write_section(
            self._xinitrc_path,
            "Run picom",
            ["picom -b --no-fading-openclose  &"],
        )
        self._file_writer.write_section(
            self._xinitrc_path,
            "Run AwesomeWM",
            ["exec awesome"],
            line_placement=LinePlacement.End,
        )

    def _setup_xresources(self):
        log(f"Generating {self._xresources_path}")
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
            "Colors readable by AwesomeWM",
            [
                "color1: COL_THEME1",
                "color2: COL_THEME2",
                "color3: COL_THEME3",
                "color4: #ffffff",
            ],
            file_type=FileType.XResources,
        )

    def _setup_app_keybindings_code(self):
        log(f"Generating {self._app_keybindings_path}")
        lines = [
            'local awful = require("awful")',
            'local gears = require("gears")',
            "local function get_keybindings(modkey)",
        ]

        if len(self._keybindings) > 0:
            lines.append("    return gears.table.join(")
            for keybinding in self._keybindings:
                for key in keybinding.keys:
                    modifiers = []
                    if keybinding.hold_mod:
                        modifiers.append("modkey")
                    if keybinding.hold_shift:
                        modifiers.append('"Shift"')
                    if keybinding.hold_ctrl:
                        modifiers.append('"Control"')

                    spawn_function = "awful.spawn.with_shell" if keybinding.command_shell else "awful.spawn"

                    modifiers = f"{{{', '.join(modifiers)}}}"
                    lines.append(
                        f'        awful.key({modifiers}, "{key}", function () {spawn_function}("{keybinding.command}") end, {{description = "", group = "App launching"}}),'
                    )
            lines[-1] = lines[-1][:-1]  # Remove trailing comma from last line
        else:
            lines.append("    return {}")

        lines += [
            ")",
            "end",
            "return {",
            "    get_keybindings = get_keybindings,",
            "}",
        ]
        self._file_writer.write_lines(self._app_keybindings_path, lines, file_type=FileType.Lua)
