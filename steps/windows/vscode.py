from steps.vscode.vscode_base import VscodeStepBase
from utils import command
from utils.log import log
from pathlib import Path


class VscodeStep(VscodeStepBase):
    def __init__(self, root_build_dir):
        super().__init__("Vscodium")
        self._root_build_dir = root_build_dir

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("vscodium")
        self._vscode_command = dependency_dispatcher.get_package_info("vscodium").install_dir / "bin\\codium"
        self._vscode_command = f'"{self._vscode_command}"'

    def perform(self):
        self._install_extensions()
        self._symlink_settings()

    def _get_vscode_config_dir(self):
        return Path(self._env.get("APPDATA")) / "VSCodium\\User"

    def _get_vscode_command(self):
        return self._vscode_command

    def _install_extension_github(self, repo_owner, repo_name, vsix_name, extension_name):
        # TODO implement this
        log(f"Skipping installing extension {vsix_name} from GitHub (not implemented)")
