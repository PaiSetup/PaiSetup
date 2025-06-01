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
        command = f"sudo apt-get install --yes {self._name}"
        run_command(command)


class DebianPackageCommands(DebianPackage):
    def __init__(self, name, commands):
        super().__init__(name)
        self._commands = commands

    def install(self):
        # TODO do it in tmp dir
        for command in self._commands:
            run_command(command, shell=True)


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
                package = PackagesDebianStep._translate_package(package_name)
                if package is None:
                    continue

                self._logger.log(f"{package_name}")
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
                    "rm microsoft.gpg",  # TODO this shouldn't be needed when we do it in tmp dir and cleanup automatically.
                    "sudo apt-get update",  # TODO this is a bit inefficient... Split it somehow to pre-install and install?
                    "sudo apt-get install code",
                ]
                return DebianPackageCommands("code", commands)
            case "code-features":
                pass
            case "openssh":
                return DebianPackageApt("openssh-client")
            case "xorg-xrandr":
                return DebianPackageApt("x11-xserver-utils")
            case "xorg-xinit":
                return DebianPackageApt("xinit")
            case "xorg-server":
                return DebianPackageApt("xserver-xorg-core")
            case "xorg-server-xephyr":
                return DebianPackageApt("xserver-xephyr")
            case "xorg-xwininfo":
                return DebianPackageApt("x11-utils")
            case "picom-ibhagwan-git":
                # TODO, we could manually download the fork, but maybe it's time to ditch it... It's no longer maintained.
                return DebianPackageApt("picom")
            case "libxft":
                return DebianPackageApt("libxft2")
            case "xorg-setxkbmap":
                return DebianPackageApt("x11-xkb-utils")
            case "pacman-contrib":
                pass  # TODO Some Gui scripts use this to check for updates. Port to debian
            case "libnotify":
                return DebianPackageApt("libnotify-bin")

            case "python":
                return DebianPackageApt("python3")
            case "python-black":
                return DebianPackageApt("black")
            case "python-music-tag" | "python-pytz":
                pass  # TODO there's no debian repo for this... Replicate what it does? Use pipx?
            case "autopep8":
                return DebianPackageApt("python3-autopep8")
            case str() if package_name.startswith("python-"):
                package_name = package_name.replace("python-", "python3-")
                return DebianPackageApt(package_name)

            case _:
                return DebianPackageApt(package_name)

    @push_dependency_handler
    def add_packages(self, *args):
        for arg in args:
            if arg is None:
                pass
            elif isinstance(arg, list):
                self._packages += arg
            else:
                self._packages.append(str(arg))

    def _get_missing_packages(self, required_packages):
        # TODO compare required_packages with actually installed packages
        return required_packages

    @pull_dependency_handler
    def query_installed_packages(self):
        # TODO
        raise NotImplementedError()
