from pathlib import Path

from steps.linux.gui.gui_xorg import WindowManagerXorg
from steps.step import Step
from utils.dependency_dispatcher import push_dependency_handler
from utils.services.file_writer import FileType


class AwesomeStep(Step):
    def __init__(self):
        super().__init__("Awesome")
        self._current_step_dir = Path(__file__).parent

        self._config_path = ".config/PaiSetup/awesome"
        self._xinitrc_path = f"{self._config_path}/xinitrc"

        self._keybindings = []

    @push_dependency_handler
    def add_keybindings(self, *keybindings):
        self._keybindings += keybindings

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "awesome",
            "jq",  # needed for parsing json when getting currency exchange
        )
        dependency_dispatcher.register_xorg_wm(
            WindowManagerXorg(
                name="awesome",
                xsession_name="AwesomeWM",
                launch_command="awesome",
            )
        )

    def perform(self):
        self._setup_awesome_config()

        self._setup_app_keybindings_code()

        # Awesome places this file during installation, but we don't need it,
        # we generate our own session files.
        self._file_writer.remove_file("/usr/share/xsessions/awesome.desktop")

    def _setup_awesome_config(self):
        self._logger.log("Symlinking rc.lua into ~/.config")
        self._file_writer.write_symlink(
            src=self._current_step_dir / "config",
            link=".config/awesome",
        )

    def _setup_app_keybindings_code(self):
        app_keybindings_path = f"{self._current_step_dir}/config/utils/app_keybindings.lua"

        self._logger.log(f"Generating {app_keybindings_path}")
        lines = [
            'local awful = require("awful")',
            'local gears = require("gears")',
            'local utils = require("utils.utils")',
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

                    if keybinding.command == "$TERMINAL":
                        spawn_function = "utils.spawn_terminal_from_thunar"
                    else:
                        precommand = ""
                        if "useless shit" in keybinding.description:
                            precommand = "utils.switch_to_empty_tag() utils.switch_to_fairv() "
                        spawn_function = "awful.spawn.with_shell" if keybinding.command_shell else "awful.spawn"
                        spawn_function = f'function() {precommand}{spawn_function}("{keybinding.command}") end'

                    modifiers = f"{{{', '.join(modifiers)}}}"
                    lines.append(
                        f'        awful.key({modifiers}, "{key}", {spawn_function}, {{description = "{keybinding.description}", group = "Generated"}}),'
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
        self._file_writer.write_lines(app_keybindings_path, lines, file_type=FileType.Lua)
