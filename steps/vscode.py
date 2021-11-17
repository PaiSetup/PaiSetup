from steps.step import Step
from utils import command
from utils.log import log
from pathlib import Path


class VscodeStep(Step):
    def __init__(self, root_build_dir):
        super().__init__("Vscode")
        self.download_dir = Path(root_build_dir) / "vscode-extensions"

    def _perform_impl(self):
        self.download_dir.mkdir(exist_ok=True)

        log("Installing python formatters")
        command.run_command("pip install autopep8 black")

        self._install_extension_github("microsoft", "vscode-cpptools", "cpptools-linux.vsix")
        self._install_extension_with_commad("ms-python.python")
        self._install_extension_with_commad("vscode-icons-team.vscode-icons")

    def _install_extension_with_commad(self, extension_name):
        log(f"Installing extension {extension_name}")
        command.run_command(f"code --install-extension {extension_name}")

    def _install_extension_github(self, repo_owner, repo_name, vsix_name):
        log(f"Installing extension {vsix_name} from GitHub")

        api_address = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        download_command = f'curl {api_address} | grep "browser_download_url.*{vsix_name}" | cut -d\\\\\\" -f4 | xargs wget -P {self.download_dir}'
        command.run_command(download_command, run_in_sh=True)
        command.run_command(f"code --install-extension {self.download_dir}/{vsix_name}")


"""
VS code configuration to do:
1. General
    - workbench.tree.indent = 16
    - editor.mouseWheelZoom = true

2. Python
    - python.formatting.provider = black
    - python.formatting.blackArgs = { "--line-length", "119" }
    - keyboard shortcuts - format document CTRL + R + D

3. C++
"""
