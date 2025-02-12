from pathlib import Path

from steps.vscode.vscode_base import VscodeStepBase
from utils.command import *


class VscodeStep(VscodeStepBase):
    def __init__(self, root_build_dir):
        super().__init__(root_build_dir)
        self._root_build_dir = root_build_dir

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "code",
            "code-features",  # Fixes some issues with loading ms-python.python extension
            "autopep8",
            "python-black",
        )
        dependency_dispatcher.register_homedir_file(".vscode")

        # VsCode is an electron app, meaning it uses chromium engine. Chromium engine doesn't properly
        # follow XDG home. See bug: https://bugs.chromium.org/p/chromium/issues/detail?id=1038587
        dependency_dispatcher.register_homedir_file(".pki")

    def perform(self):
        self._install_extensions()
        self._symlink_settings()
        self._create_desktop_file()

    def _install_extensions(self):
        if len(self._env.get("DISPLAY")) > 0:
            super()._install_extensions()
        else:
            self._logger.log("Skipping extensions installation (no graphical display)")

    def _create_desktop_file(self):
        self._file_writer.patch_dot_desktop_file(
            "code-oss.desktop",
            "code_new_window.desktop",
            {
                "Name": lambda section, name, value: f"{value} - New window" if section == "Desktop Entry" else value,
                "Exec": lambda section, name, value: f"{value} --new-window" if section == "Desktop Entry" else value,
            },
        )

    def _get_vscode_config_dir(self):
        return Path(".config/Code/User/")

    def _get_vscode_command(self):
        return "code"
