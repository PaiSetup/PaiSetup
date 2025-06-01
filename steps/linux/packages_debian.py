from steps.step import Step
from utils.command import *
from utils.dependency_dispatcher import pull_dependency_handler, push_dependency_handler

class DebianPackage:
    def __init__(self, name):
        self._name = name

    def install(self):
        raise NotImplementedError()

class DebianPackageApt(DebianPackage):
    def __init__(self, name):
        super().__init__(name)

    def install(self):
        command = f"sudo apt-get install --yes {command}"
        run_command(command)

class DebianPackageCommands(DebianPackage):
    def __init__(self, name, commands):
        super().__init__(name)
        self._commands = commands

    def install(self):
        # TODO do it in tmp dir
        for command in self._commands:
            run_command(command)

class DebianPackageCustomFunction(DebianPackage):
    def __init__(self, name, command):
        super().__init__(name)
        self._function = _function

    def install(self):
        self._function()


class PackagesDebianStep(Step):
    def __init__(self, enable_installation):
        super().__init__("Packages")
        self._enable_installation = enable_installation
        self._packages = []

    def perform(self):
        self._install_packages()

    def _install_packages(self):
        if not self._enable_installation:
            return

        missing_packages = self._get_missing_packages(self._packages)
        if not missing_packages:
                self._logger.log("All packages are already installed.")
                return

        with self._logger.indent(f"Installing packages: {self._packages}"):
            for package_name in self._packages:
                self._logger.log(f"{package_name}")

                package = PackagesDebianStep._translate_package(package_name)
                package.install()

    @staticmethod
    def _translate_package(package_name):
        # TODO a comment
        match package_name:
            case "code":
                commands = [
                    "curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg",
                    "sudo install -o root -g root -m 644 microsoft.gpg /etc/apt/keyrings/microsoft-archive-keyring.gpg",
                    "sudo sh -c 'echo \"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/repos/code stable main\" > /etc/apt/sources.list.d/vscode.list'",
                ]
                return DebianPackageCommands(commands)
            case _:
                return DebianPackageApt(package)

    @push_dependency_handler
    def add_packages(self, *args):
        for arg in args:
            if arg is None:
                pass
            elif isinstance(arg, list):
                packages_list += arg
            else:
                packages_list.append(str(arg))
        PackagesStep._add_packages_to_list(self._packages, *args)

    def _get_missing_packages(self, required_packages):
        # TODO compare required_packages with actually installed packages
        return required_packages

    @pull_dependency_handler
    def query_installed_packages(self):
        # TODO
        raise NotImplementedError()
