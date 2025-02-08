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
            self._logger.log(f"Installing extension {vsix_name} from GitHub (skipped)")
            return

        self._logger.log(f"Installing extension {vsix_name} from GitHub")

        self._extensions_download_dir.mkdir(exist_ok=True)

        api_address = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        download_command = f"curl {api_address} | grep 'browser_download_url.*{vsix_name}' | awk '{{print $2}}' | xargs wget -O {self._extensions_download_dir/vsix_name}"
        run_command(download_command, shell=True)
        run_command(f"{self._get_vscode_command()} --install-extension {self._extensions_download_dir/vsix_name}")
