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

    def perform(self):
        self._install_extensions()
        self._symlink_settings()

    def _get_vscode_config_dir(self):
        return Path("C:/Users/maciej/AppData/Roaming/VSCodium/User")

    def _get_vscode_command(self):
        return "D:/Programs/VsCodium/bin/codium"

    def _install_extension_github(self, repo_owner, repo_name, vsix_name, extension_name):
        # TODO implement this
        log(f"Skipping installing extension {vsix_name} from GitHub (not implemented)")
