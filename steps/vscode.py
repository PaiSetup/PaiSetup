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

        extensions = []

        # Generic
        extensions.append("vscode-icons-team.vscode-icons")

        # C++
        self._install_extension_github("microsoft", "vscode-cpptools", "cpptools-linux.vsix", "ms-vscode.cpptools")
        extensions.append("matepek.vscode-catch2-test-adapter")
        extensions.append("twxs.cmake")
        extensions.append("ms-vscode.cmake-tools")
        extensions.append("hbenl.test-adapter-converter")
        extensions.append("hbenl.vscode-test-explorer")

        # Python
        log("Installing python formatters")
        command.run_command("pip install autopep8 black")  # TODO python -c "autopep8 black" is a faster check
        extensions.append("ms-python.python")

        self._install_extensions_with_commad(extensions)

    def _install_extensions_with_commad(self, extension_names):
        args = (f"--install-extension {x}" for x in extension_names)
        args = " ".join(args)
        log(f"Installing extensions: {', '.join(extension_names)}")
        command.run_command(f"code {args}")

    def _install_extension_github(self, repo_owner, repo_name, vsix_name, extension_name):
        """
        This function is for a handful of extension which are not downloadable by vscode OSS (or vscodium)
        command, because Microsoft says so. So we have to manually pull the .vsix from the web and install
        it. Parameters:
        - repo_owner, repo_name - address of Github repository to pull from
        - vsix_name - name of the actual .vsix file we'll need to download
        - extension name - name of the extension once it's installed (run code --list-extensions)
        """

        if self._is_extension_installed(extension_name):
            log(f"Installing extension {vsix_name} from GitHub (skipped)")
            return

        log(f"Installing extension {vsix_name} from GitHub")

        api_address = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        download_command = f"curl {api_address} | grep 'browser_download_url.*{vsix_name}' | awk '{{print $2}}' | xargs wget -O {self.download_dir}/{vsix_name}"
        log(f"XD: {download_command}")
        command.run_command(download_command, shell=True)
        command.run_command(f"code --install-extension {self.download_dir}/{vsix_name}")

    def _is_extension_installed(self, extension_name):
        try:
            command.run_command(f"code --list-extensions | grep '^{extension_name}$'", shell=True)
            return True
        except:
            return False


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
