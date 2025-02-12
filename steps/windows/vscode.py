from pathlib import Path

from steps.vscode.vscode_base import VscodeStepBase
from utils.command import *


class VscodeStep(VscodeStepBase):
    def __init__(self, root_build_dir):
        super().__init__(root_build_dir)
        self._root_build_dir = root_build_dir

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("vscodium")

    def pull_dependencies(self, dependency_dispatcher):
        self._vscode_command = dependency_dispatcher.get_package_info("vscodium").install_dir / "bin\\codium"
        self._vscode_command = f'"{self._vscode_command}"'

    def perform(self):
        self._install_extensions()
        self._symlink_settings()

    def _get_vscode_config_dir(self):
        return Path(self._env.get("APPDATA")) / "VSCodium\\User"

    def _get_vscode_command(self):
        return self._vscode_command
