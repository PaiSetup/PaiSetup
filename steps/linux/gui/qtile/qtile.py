from pathlib import Path

from steps.linux.gui.gui import GuiStep
from steps.step import dependency_listener
from utils.services.file_writer import FileType, LinePlacement


class QtileStep(GuiStep):
    def __init__(self):
        super().__init__("Qtile")
        self._current_step_dir = Path(__file__).parent

        self._qtile_config_script_path = self._current_step_dir / "config/config.py"
        self._app_keybindings_path = self._current_step_dir / "config/generated/app_keys.py"
        self._config_path = ".config/PaiSetup/qtile"
        self._xinitrc_path = f"{self._config_path}/xinitrc"

        self._keybindings = []

    @dependency_listener
    def add_keybindings(self, *keybindings):
        self._keybindings += keybindings

    def express_dependencies(self, dependency_dispatcher):
        super().express_dependencies(dependency_dispatcher)
        dependency_dispatcher.add_packages("qtile")
        dependency_dispatcher.add_xsession("Qtile", self._env.home() / self._xinitrc_path)

    def perform(self):
        self._setup_xinitrc_qtile()
        self._setup_app_keybindings_code()

        # Qtile places this file during installation, but we don't need it,
        # we generate our own session files.
        self._file_writer.remove_file("/usr/share/xsessions/qtile.desktop")

    def _setup_xinitrc_qtile(self):
        self._logger.log(f"Generating {self._xinitrc_path}")
        self._file_writer.write_section(
            self._xinitrc_path,
            "Call base script",
            [
                "export WM=qtile",
                ". ~/.config/PaiSetup/xinitrc_base",
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
            "Run Qtile",
            [f"exec qtile start -c {self._qtile_config_script_path}"],
            line_placement=LinePlacement.End,
        )

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

                line = f'    Key({modifiers}, "{key}", lazy.spawn({command})),'
                lines.append(line)

        lines.append("]")
        self._file_writer.write_lines(self._app_keybindings_path, lines, file_type=FileType.Python)
