from pathlib import Path

from steps.vscode.vscode_base import VscodeStepBase
from utils.command import *


class VscodeStep(VscodeStepBase):
    def __init__(self, use_vscodium):
        super().__init__()
        if use_vscodium:
            self._package_name = "vscodium"
            self._binary_name = "codium"
            self._config_dir_name = "VSCodium"
            self._extensions_dir_name = ".vscode-oss"
        else:
            self._package_name = "vscode"
            self._binary_name = "code"
            self._config_dir_name = "Code"
            self._extensions_dir_name = ".vscode"

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(self._package_name)

    def pull_dependencies(self, dependency_dispatcher):
        self._vscode_command = dependency_dispatcher.get_package_info(self._package_name).install_dir / "bin" / self._binary_name
        self._vscode_command = f'"{self._vscode_command}"'

    def perform(self):
        self._install_extensions()
        self._symlink_settings()

    def _get_vscode_config_dir(self):
        return Path(self._env.get("APPDATA")) / self._config_dir_name / "User"

    def _get_vscode_extensions_dir(self):
        return self._paths.home() / self._extensions_dir_name / "extensions"

    def _get_vscode_command(self):
        return self._vscode_command
