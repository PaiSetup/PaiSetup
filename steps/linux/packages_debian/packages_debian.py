from steps.step import Step
from utils.command import *
from utils.dependency_dispatcher import pull_dependency_handler, push_dependency_handler
from utils.os_helpers import TmpDir


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
    def __init__(self, name, is_pre_scripts=False):
        super().__init__(name)
        self.is_pre_scripts = is_pre_scripts

    def install(self):
        command = f"sudo apt-get install --yes {self._name}"
        run_command(command)

    @staticmethod
    def install_multiple(packages):
        package_names = [p._name for p in packages]
        package_names = " ".join(package_names)
        command = f"sudo apt-get install --yes {package_names}"
        run_command(command)


class DebianPackageScript(DebianPackage):
    def __init__(self, script_name):
        self._script_path = Path(__file__).parent / script_name

        name = run_command(f"{self._script_path} get_name", stdout=Stdout.return_back()).stdout
        super().__init__(name)

    def install(self):
        with TmpDir():
            run_command(f"{self._script_path} install_package")

    def is_installed(self, apt_context):
        try:
            run_command(f"{self._script_path} is_installed")
            return True
        except CommandError:
            return False


class PackagesDebianStep(Step):
    def __init__(self, enable_installation, separate_apt_commands=False):
        super().__init__("Packages")
        self._enable_installation = enable_installation
        self._separate_apt_commands = separate_apt_commands
        self._package_names = []

    def perform(self):
        if not self._enable_installation:
            return

        installed_package_names = PackagesDebianStep._get_installed_packages()

        packages = [PackagesDebianStep._translate_package(p) for p in self._package_names]
        packages = [i for x in packages for i in (x if isinstance(x, list) else [x])]  # Flatten nested lists
        packages = [p for p in packages if p is not None and not p.is_installed(installed_package_names)]

        if packages:
            with self._logger.indent("Installing packages:"):
                apt_packages_pre, script_packages, apt_packages_post = self._sort_packages(packages)
                self._install_apt_packages(apt_packages_pre)
                self._install_packages(script_packages)
                self._install_apt_packages(apt_packages_post)
        else:
            self._logger.log("No packages to install.")

        with self._logger.indent("Making sure all packages were installed:"):
            all_installed = True
            for package in packages:
                if not package.is_installed(installed_package_names):
                    self._logger.push_warning(f"package {package.name} was not installed correctly")
                    all_installed = False
            if all_installed:
                self._logger.log("OK")

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
                install_ppa = DebianPackageScript("install_code_ppa.sh")
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
            case "xorg-xwininfo" | "xorg-xev":
                return DebianPackageApt("x11-utils")
            case "libxft":
                return DebianPackageApt("libxft2")
            case "xorg-setxkbmap":
                return DebianPackageApt("x11-xkb-utils")
            case "pacman-contrib":
                pass  # For checkupdates on arch.
            case "libnotify":
                return DebianPackageApt("libnotify-bin")
            case "eza":
                dependencies = [
                    "gettext",
                    "libgtk-3-dev",
                    "libsass1",
                    "sassc",
                    "inkscape",
                ]
                install_oomox = DebianPackageScript("install_eza.sh")
                return [DebianPackageApt(d, True) for d in dependencies] + [install_oomox]
            case "themix-theme-oomox-git":
                return DebianPackageScript("install_oomox.sh")
            case "firefox":
                return DebianPackageApt("firefox-esr")
            case "ulauncher":
                pass  # TODO(debian) there's a PPA for this. Figure out how to do this safely.
            case "flamegraph":
                return DebianPackageScript("install_flamegraph.sh")
            case "alsa-firmware" | "pulseaudio-alsa" | "gvfs" | "gvfs-mtp" | "gvfs-gphoto2":
                pass  # Already installed
            case "bcompare":
                return DebianPackageScript("install_bcompare.sh")
            case "megasync-bin":
                return DebianPackageScript("install_megasync.sh")
            case "consolas-font":
                return DebianPackageScript("install_font_consolas.sh")
            case "ttf-font-awesome":
                return DebianPackageScript("install_font_awesome.sh")
            case "ttf-joypixels":
                return DebianPackageScript("install_font_joypixels.sh")
            case "gst-plugins-bad":
                return DebianPackageApt("gstreamer1.0-plugins-bad")
            case "gst-plugins-ugly":
                return DebianPackageApt("gstreamer1.0-plugins-ugly")
            case "libreoffice-still":
                return DebianPackageApt("libreoffice")
            case "losslesscut-bin":
                pass  # Ignored for now
            case "nomacs" | "qt5-imageformats":
                pass  # Ignored for now (no stable package, compiling is long and oudates easily)
            case "discord":
                pass  # Ignored for now
            case "mtpfs":
                return DebianPackageApt("go-mtpfs")

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

    def _sort_packages(self, packages):
        apt_packages_pre = []
        script_packages = []
        apt_packages_post = []

        for package in packages:
            if isinstance(package, DebianPackageScript):
                script_packages.append(package)
            elif isinstance(package, DebianPackageApt):
                if package.is_pre_scripts:
                    apt_packages_pre.append(package)
                else:
                    apt_packages_post.append(package)
            else:
                raise TypeError(f"Unknown package type: {type(pkg)}")

        return apt_packages_pre, script_packages, apt_packages_post

    def _install_apt_packages(self, packages):
        if not packages:
            return

        self._logger.log("Running apt-get update")
        run_command("sudo apt-get update")

        if self._separate_apt_commands:
            self._install_packages(packages)
        else:
            self._logger.log(" ".join((p.get_name() for p in packages)))
            DebianPackageApt.install_multiple(packages)

    def _install_packages(self, packages):
        for package in packages:
            self._logger.log(f"{package.get_name()}")
            package.install()

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
