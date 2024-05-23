from pathlib import Path

from steps.step import dependency_listener
from utils.services.file_writer import LinePlacement

from ..gui.gui import GuiStep


class QtileStep(GuiStep):
    def __init__(self):
        super().__init__("Qtile")
        self._current_step_dir = Path(__file__).parent

        self._config_path = ".config/PaiSetup/qtile"
        self._xresources_path = f"{self._config_path}/Xresources"
        self._xinitrc_path = f"{self._config_path}/xinitrc"

        self._app_keybindings_path = f"{self._current_step_dir}/config/utils/app_keybindings.lua"
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
            ["exec qtile start"],
            line_placement=LinePlacement.End,
        )
