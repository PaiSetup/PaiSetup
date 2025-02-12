import re
from pathlib import Path

from steps.step import Step
from utils.command import *
from utils.os_function import OperatingSystem


class VscodeStepBase(Step):
    def __init__(self, root_build_dir):
        super().__init__("Vscode")
        self._root_build_dir = root_build_dir
        self._extensions_download_dir = Path(self._root_build_dir) / "vscode-extensions"

        current_step_dir = Path(__file__).parent
        self._keybindings_path = current_step_dir / "keybindings.json"
        self._settings_path = current_step_dir / "settings.json"

    def _symlink_settings(self):
        self._logger.log("Symlinking VScode settings")

        config_dir = self._get_vscode_config_dir()
        system_keybindings_path = config_dir / "keybindings.json"
        system_settings_path = config_dir / "settings.json"

        self._file_writer.write_symlink(src=self._keybindings_path, link=system_keybindings_path)
        self._file_writer.write_symlink(src=self._settings_path, link=system_settings_path)

    def _install_extensions(self):
        extensions_command = []
        extensions_github = []
        python_packages = []

        # Generic
        extensions_command.append("vscode-icons-team.vscode-icons")

        # C++
        cpp_tools_vsix_name = "cpptools-linux-x64.vsix" if OperatingSystem.current().is_linux() else "cpptools-windows-x64.vsix"
        extensions_github.append(("microsoft", "vscode-cpptools", cpp_tools_vsix_name, "ms-vscode.cpptools"))
        extensions_command.append("matepek.vscode-catch2-test-adapter")
        extensions_command.append("twxs.cmake")
        extensions_command.append("ms-vscode.cmake-tools")
        extensions_command.append("hbenl.test-adapter-converter")
        extensions_command.append("hbenl.vscode-test-explorer")
        extensions_command.append("xaver.clang-format")
        extensions_command.append("shardulm94.trailing-spaces")

        # Rust
        extensions_command.append("rust-lang.rust-analyzer")
        extensions_command.append("vadimcn.vscode-lldb")

        # Python
        if not OperatingSystem.current().is_linux():  # On Arch there is a separate pacman package for this...
            python_packages.append("autopep8")
            python_packages.append("black")
        extensions_command.append("ms-python.python")
        extensions_command.append("ms-python.isort")
        extensions_command.append("ms-python.black-formatter")

        # Install everything
        self._install_extensions_with_commad(extensions_command)
        for x in extensions_github:
            self._install_extension_github(*x)
        for x in python_packages:
            self._install_python_package(x)

    def _is_extension_installed(self, extension_name):
        extensions = run_command(f"{self._get_vscode_command()} --list-extensions", shell=True, stdout=Stdout.return_back()).stdout
        extensions = extensions.split("\n")
        return extension_name in extensions

    def _install_extensions_with_commad(self, extension_names):
        args = (f"--install-extension {x}" for x in extension_names)
        args = " ".join(args)
        self._logger.log(f"Installing extensions: {', '.join(extension_names)}")
        run_command(f"{self._get_vscode_command()} {args}", shell=True)

    def _install_python_package(self, package_name, import_name=None):
        if import_name is None:
            import_name = package_name
        try:
            run_command(f'python -c "import {import_name}"')
        except CommandError:
            self._logger.log(f"Installing {package_name} Python package")
            run_command(f"pip install {package_name}")

    def _get_vscode_config_dir(self):
        raise NotImplementedError()

    def _get_vscode_command(self):
        raise NotImplementedError()

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

        # Download metadata for latest release
        api_address = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        api_download_command = f"curl {api_address}"
        api_data = run_command(api_download_command, stdout=Stdout.return_back()).stdout
        api_data = api_data.split("\n")

        # Search for download url for our vsix
        pattern = rf'"browser_download_url":.*(https.*{vsix_name})'
        download_url = None
        for line in api_data:
            match = re.search(pattern, line)
            if match:
                download_url = match.group(1)
                break
        if download_url is None:
            raise ValueError(f"Could not find {vsix_name}")

        # Download the vsix
        self._extensions_download_dir.mkdir(exist_ok=True)
        download_command = f"wget -O {self._extensions_download_dir/vsix_name} {download_url}"
        if OperatingSystem.current().is_windows():
            # This is insane.
            # https://stackoverflow.com/questions/28682642/powershell-why-is-using-invoke-webrequest-much-slower-than-a-browser-download
            download_command = ["$ProgressPreference = 'SilentlyContinue'", download_command]
            run_powershell_command(download_command)
        else:
            run_command(download_command)

        # Install the vsix
        install_command = f"{self._get_vscode_command()} --install-extension {self._extensions_download_dir/vsix_name}"
        run_command(install_command, shell=True)
