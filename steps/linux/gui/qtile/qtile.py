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
        self._xresources_path = f"{self._config_path}/Xresources"

        self._keybindings = []

    @dependency_listener
    def add_keybindings(self, *keybindings):
        self._keybindings += keybindings

    def push_dependencies(self, dependency_dispatcher):
        super().push_dependencies(dependency_dispatcher)
        dependency_dispatcher.add_packages("qtile")
        dependency_dispatcher.add_xsession("Qtile", self._env.home() / self._xinitrc_path)

    def perform(self):
        self._setup_xinitrc_qtile()
        self._setup_app_keybindings_code()
        self._setup_xresources()

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
            "Run picom",
            ["picom -b --no-fading-openclose  &"],
        )
        self._file_writer.write_section(
            self._xinitrc_path,
            "Run Qtile",
            [f"exec qtile start -c {self._qtile_config_script_path}"],
            line_placement=LinePlacement.End,
        )

    def _setup_xresources(self):
        self._logger.log(f"Generating {self._xresources_path}")
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
            "Colors readable by Qtile",
            [
                "color1: COL_THEME1",
                "color2: COL_THEME2",
                "color3: COL_THEME3",
                "color4: #ffffff",
            ],
            file_type=FileType.XResources,
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

                line = f'    Key({modifiers}, "{key}", lazy.spawn({command}), desc="{keybinding.description}"),'
                lines.append(line)

        lines.append("]")
        self._file_writer.write_lines(self._app_keybindings_path, lines, file_type=FileType.Python)
