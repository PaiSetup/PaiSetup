import json
import os
from pathlib import Path

from steps.step import Step
from utils.services.file_writer import FileType


class UlauncherStep(Step):
    def __init__(self):
        super().__init__("Ulauncher")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("ulauncher")

    def perform(self):
        self._logger.log("Configuring ulauncher")
        self._setup_ulauncher_config()

        self._logger.log("Enabling ulauncher on startup")
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "App launcher",
            ["ulauncher --hide-window &"],
        )

    def _setup_ulauncher_config(self):
        config = {
            "blacklisted-desktop-dirs": "/usr/share/locale:/usr/share/app-install:/usr/share/kservices5:/usr/share/fk5:/usr/share/kservicetypes5:/usr/share/applications/screensavers:/usr/share/kde4:/usr/share/mimelnk",
            "clear-previous-query": True,
            "disable-desktop-filters": False,
            "grab-mouse-pointer": True,
            "hotkey-show-app": "<Super>grave",
            "render-on-screen": "mouse-pointer-monitor",
            "show-indicator-icon": True,
            "show-recent-apps": "3",
            "terminal-command": "",
            "theme-name": "dark",
        }
        config = json.dumps(config, indent=4)

        self._file_writer.write_lines(".config/ulauncher/settings.json", [config], file_type=FileType.Json)
