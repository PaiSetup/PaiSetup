from steps.step import Step
from utils.command import *
from utils.dependency_dispatcher import pull_dependency_handler, push_dependency_handler


class DebianPackage:
    def __init__(self, name):
        self._name = name

    def install(self):
        raise NotImplementedError()

    def is_installed(self, apt_context):
        return self._name in apt_context

    def get_name(self):
        return self._name


class DebianPackageApt(DebianPackage):
    def __init__(self, name):
        super().__init__(name)

    def install(self):
        command = f"sudo apt-get install --yes {self._name}"
        run_command(command)


class DebianPackageCommands(DebianPackage):
    def __init__(self, name, commands, is_installed_command=None):
        super().__init__(name)
        self._commands = commands
        self._is_installed_command = is_installed_command

    def install(self):
        # TODO(debian) do it in tmp dir
        for command in self._commands:
            run_command(command, shell=True)

    def is_installed(self, apt_context):
        if self._is_installed_command is None:
            return super().is_installed(apt_context)

        try:
            run_command(self._is_installed_command, shell=True)
            return True
        except CommandError:
            return False


class PackagesDebianStep(Step):
    def __init__(self, enable_installation):
        super().__init__("Packages")
        self._enable_installation = enable_installation
        self._package_names = []

    def perform(self):
        self._install_packages()

    def _install_packages(self):
        if not self._enable_installation:
            return

        installed_package_names = PackagesDebianStep._get_installed_packages()

        packages = [PackagesDebianStep._translate_package(p) for p in self._package_names]
        packages = [i for x in packages for i in (x if isinstance(x, list) else [x])]  # Flatten nested lists
        packages = [p for p in packages if p is not None and not p.is_installed(installed_package_names)]
        # TODO(debian) simplify packages, i.e. group apt packages in a single command

        if not packages:
            self._logger.log("No packages to install.")
            return

        with self._logger.indent("Installing packages:"):
            for package in packages:
                self._logger.log(f"{package.get_name()}")  # TODO(debian) add more verbose logs
                package.install()

    @staticmethod
    def _translate_package(package_name):
        # PaiSetup was historically build around Arch Linux and all the steps express package dependencies in terms
        # of Arch Linux package names. Debian is a sort of second-class citizen, so here we translate Arch package
        # names in Debian package names. There are a couple of possible situations:
        #   1. There's an apt package with the same name. This is the default case in below match statement.
        #   2. There's an apt package with a different name. We hardcode the translation.
        #   3. There's no apt package and we don't want it, because it's Arch-specific. We just return None.
        #   4. There's no apt package and we want it. We return shell commands to execute.
        match package_name:
            case "code":
                install_ppa = DebianPackageCommands(
                    "code (PPA)",
                    [
                        "curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg",
                        "sudo install -o root -g root -m 644 microsoft.gpg /etc/apt/keyrings/microsoft-archive-keyring.gpg",
                        "sudo sh -c 'echo \"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/repos/code stable main\" > /etc/apt/sources.list.d/vscode.list'",
                        "rm microsoft.gpg",  # TODO(debian) this shouldn't be needed when we do it in tmp dir and cleanup automatically.
                        "sudo apt-get update",  # TODO(debian) this shouldn't be needed when we split execution into commands->apt update->apt install
                    ],
                    "test -f /etc/apt/sources.list.d/vscode.list",
                )
                install_code = DebianPackageApt("code")
                return [install_ppa, install_code]
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
                # TODO(debian) we could manually download the fork, but maybe it's time to ditch it... It's no longer maintained.
                return DebianPackageApt("picom")
            case "libxft":
                return DebianPackageApt("libxft2")
            case "xorg-setxkbmap":
                return DebianPackageApt("x11-xkb-utils")
            case "pacman-contrib":
                pass  # TODO(debian) Some Gui scripts use this to check for updates. Port to debian
            case "libnotify":
                return DebianPackageApt("libnotify-bin")
            case "eza":
                pass  # TODO(debian) no stable package. Build from source?
            case "themix-theme-oomox-git" | "themix-full-git":
                pass  # TODO(debian) install themix and oomox from github
            case "ttf-joypixels":
                return DebianPackageCommands(
                    "ttf-joypixels",
                    [
                        "wget https://cdn.joypixels.com/arch-linux/font/8.0.0/joypixels-android.ttf -O ~/.local/share/fonts/joypixels.ttf",
                    ],
                    "test -f ~/.local/share/fonts/joypixels.ttf",
                )
            case "ttf-font-awesome":
                return DebianPackageApt("fonts-font-awesome")
            case "firefox":
                return DebianPackageApt("firefox-esr")
            case "ulauncher":
                pass  # TODO(debian) there's a PPA for this. Figure out how to do this safely.

            case "python":
                return DebianPackageApt("python3")
            case "python-black":
                return DebianPackageApt("black")
            case "python-music-tag" | "python-pytz":
                pass  # TODO(debian) there's no debian repo for this... Replicate what it does? Use pipx?
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
                self._package_names += arg
            else:
                self._package_names.append(str(arg))

    @staticmethod
    def _get_installed_packages():
        packages = run_command("apt list --installed", stdout=Stdout.return_back()).stdout
        packages = packages.split("\n")
        packages = [line[: line.find("/")] for line in packages if line]
        return packages

    @pull_dependency_handler
    def query_installed_packages(self):
        # TODO(debian) not sure what to return here yet.
        raise NotImplementedError()
