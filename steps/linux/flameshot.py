import os

from steps.linux.spieven.spieven import SpievenDisplayType
from steps.step import Step
from utils.keybinding import KeyBinding


class FlameshotStep(Step):
    def __init__(self):
        super().__init__("Flameshot")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("flameshot")
        dependency_dispatcher.schedule_spieven_daemon("flameshot", "flameshot", display_type=SpievenDisplayType.Xorg)
        dependency_dispatcher.add_keybindings(KeyBinding("s").mod().shift().desc("Screenshot").execute("flameshot gui"))

    def perform(self):
        self._logger.log("Generating picom config")
        self._file_writer.write_lines(
            ".config/flameshot/flameshot.ini",
            [
                "[General]",
                "contrastOpacity=188",
                "drawColor=#ff1e00",
                "drawFontSize=7",
                "drawThickness=2",
                "fontFamily=C059",
                f"savePath={self._env.home() / "downloads"}",
                "useX11LegacyScreenshot=true",  # Workaround for https://github.com/flameshot-org/flameshot/issues/4639
            ],
        )
