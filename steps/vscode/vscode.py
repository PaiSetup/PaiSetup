from steps.step import Step
from utils import command
from utils.log import log, LogIndent
from pathlib import Path


class VscodeStep(Step):
    def __init__(self, root_build_dir):
        super().__init__("Vscode")
        self._root_build_dir = root_build_dir

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("code")

    def perform(self):
        self._symlink_settings()
        self._install_extensions()
        self._create_terminal_vim_desktop_file()

    def _symlink_settings(self):
        log("Symlinking VScode settings")
        current_step_dir = Path(__file__).parent
        config_dir = Path(".config/Code - OSS/User/")
        self._file_writer.write_symlink(src=current_step_dir / "keybindings.json", link=config_dir / "keybindings.json")
        self._file_writer.write_symlink(src=current_step_dir / "settings.json", link=config_dir / "settings.json")

    def _install_extensions(self):
        download_dir = Path(self._root_build_dir) / "vscode-extensions"
        download_dir.mkdir(exist_ok=True)

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
        extensions.append("xaver.clang-format")
        extensions.append("shardulm94.trailing-spaces")

        # Python
        log("Installing python formatters")
        with LogIndent():
            self._install_python_package("autopep8")
            self._install_python_package("black")
        extensions.append("ms-python.python")

        self._install_extensions_with_commad(download_dir, extensions)

    def _install_extensions_with_commad(self, download_dir, extension_names):
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
        download_command = (
            f"curl {api_address} | grep 'browser_download_url.*{vsix_name}' | awk '{{print $2}}' | xargs wget -O {download_dir}/{vsix_name}"
        )
        command.run_command(download_command, shell=True)
        command.run_command(f"code --install-extension {download_dir}/{vsix_name}")

    def _is_extension_installed(self, extension_name):
        try:
            command.run_command(f"code --list-extensions | grep '^{extension_name}$'", shell=True)
            return True
        except:
            return False

    def _create_terminal_vim_desktop_file(self):
        self._file_writer.patch_dot_desktop_file(
            "code-oss.desktop",
            "code_new_window.desktop",
            {
                "Name": lambda section, name, value: f"{value} - New window" if section == "Desktop Entry" else value,
                "Exec": lambda section, name, value: f"{value} --new-window" if section == "Desktop Entry" else value,
            },
        )

    def _install_python_package(self, package_name, import_name=None):
        if import_name is None:
            import_name = package_name
        try:
            command.run_command(f'python -c "import {import_name}"')
        except command.CommandError:
            log(f"Installing {package_name} Python package")
            command.run_command(f"pip install {package_name}")
