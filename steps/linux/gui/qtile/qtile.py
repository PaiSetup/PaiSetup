from pathlib import Path

from steps.linux.gui.gui_xorg import WindowManagerXorg
from steps.step import Step
from utils.dependency_dispatcher import push_dependency_handler
from utils.services.file_writer import FileType


class QtileStep(Step):
    def __init__(self):
        super().__init__("Qtile")
        self._current_step_dir = Path(__file__).parent

        self._qtile_config_script_path = self._current_step_dir / "config/config.py"
        self._app_keybindings_path = self._current_step_dir / "config/generated/app_keys.py"
        self._config_path = ""
        self._xinitrc_path = self._env.home() / f".config/PaiSetup/qtile/xinitrc"

        self._keybindings = []

    @push_dependency_handler
    def add_keybindings(self, *keybindings):
        self._keybindings += keybindings

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("qtile")
        dependency_dispatcher.register_xorg_wm(
            WindowManagerXorg(
                name="qtile",
                xsession_name="QtileX11",
                launch_command=f"qtile start -c {self._qtile_config_script_path}",
            )
        )

    def perform(self):
        self._setup_app_keybindings_code()

        # Qtile places this file during installation, but we don't need it,
        # we generate our own session files.
        self._file_writer.remove_file("/usr/share/xsessions/qtile.desktop")

    def _setup_app_keybindings_code(self):
        self._logger.log(f"Generating {self._app_keybindings_path}")
        lines = [
            "from libqtile.config import Key",
            "from libqtile.lazy import lazy",
            "",
            "from utils.modkeys import *",
            "",
            "app_keys = [",
        ]

        for keybinding in self._keybindings:
            for key in keybinding.keys:
                modifiers = []
                if keybinding.hold_mod:
                    modifiers.append("mod")
                if keybinding.hold_shift:
                    modifiers.append("shift")
                if keybinding.hold_ctrl:
                    modifiers.append("ctrl")
                modifiers = ", ".join(modifiers)
                modifiers = f"[{modifiers}]"

                command = keybinding.command
                if keybinding.command_shell:
                    command = f"'sh -c \"{command}\"'"
                else:
                    command = f'"{command}"'

                line = f'    Key({modifiers}, "{key}", lazy.spawn({command}), desc="{keybinding.description}"),'
                lines.append(line)

        lines.append("]")
        self._file_writer.write_lines(self._app_keybindings_path, lines, file_type=FileType.Python)
