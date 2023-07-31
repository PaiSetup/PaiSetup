from steps.step import Step
from utils import command
from utils.log import log
from pathlib import Path


class VscodeStepBase(Step):
    def __init__(self, root_build_dir):
        super().__init__("Vscode")
        self._root_build_dir = root_build_dir
        self._extensions_download_dir = Path(self._root_build_dir) / "vscode-extensions"

        current_step_dir = Path(__file__).parent
        self._keybindings_path = current_step_dir / "keybindings.json"
        self._settings_path = current_step_dir / "settings.json"

    def _symlink_settings(self):
        log("Symlinking VScode settings")

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
        extensions_github.append(("microsoft", "vscode-cpptools", "cpptools-linux.vsix", "ms-vscode.cpptools"))
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
        python_packages.append("autopep8")
        python_packages.append("black")
        extensions_command.append("ms-python.python")

        # Install everything
        self._install_extensions_with_commad(extensions_command)
        for x in extensions_github:
            self._install_extension_github(*x)
        for x in python_packages:
            self._install_python_package(x)

    def _is_extension_installed(self, extension_name):
        try:
            command.run_command(f"{self._get_vscode_command()} --list-extensions | grep '^{extension_name}$'", shell=True)
            return True
        except:
            return False

    def _install_extensions_with_commad(self, extension_names):
        args = (f"--install-extension {x}" for x in extension_names)
        args = " ".join(args)
        log(f"Installing extensions: {', '.join(extension_names)}")
        command.run_command(f"{self._get_vscode_command()} {args}")

    def _install_python_package(self, package_name, import_name=None):
        if import_name is None:
            import_name = package_name
        try:
            command.run_command(f'python -c "import {import_name}"')
        except command.CommandError:
            log(f"Installing {package_name} Python package")
            command.run_command(f"pip install {package_name}")

    def _get_vscode_config_dir(self):
        raise NotImplementedError()

    def _get_vscode_command(self):
        raise NotImplementedError()

    def _install_extension_from_github(self, repo_owner, repo_name, vsix_name, extension_name):
        raise NotImplementedError()
