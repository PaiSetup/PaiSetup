import utils.external_project as ext
from steps.step import Step
from utils.command import *
from utils.dependency_dispatcher import pull_dependency_handler, push_dependency_handler
from utils.os_helpers import Pushd


class PackagesStep(Step):
    def __init__(self, root_build_dir, print_installation, enable_installation):
        super().__init__("Packages")
        self._known_package_groups = ["vulkan-devel"]
        self.root_build_dir = root_build_dir
        self._enable_installation = enable_installation
        self.print_installation = print_installation
        self._packages = []
        self._assumed_packages = []

    def perform(self):
        self._install_yay()
        self._set_yay_permissions()
        self._install_packages()
        self._mark_packages_explicit()
        self._mark_packages_deps()

    def _install_yay(self):
        with self._logger.indent("Installing yay"):
            if not self._get_missing_packages(["yay"]):
                self._logger.log("Already installed. Skipping")
            else:
                self._logger.log("Downloading yay")
                build_dir = self.root_build_dir / "yay"
                ext.download(
                    "https://aur.archlinux.org/yay-git.git",
                    "master",
                    build_dir,
                    logger=self._logger,
                )
                self._logger.log("Installing yay")
                with Pushd(build_dir):
                    run_command("makepkg -si --noconfirm")

    def _set_yay_permissions(self):
        self._logger.log("Setting permissions for tmp yay directory")
        run_command("sudo mkdir /tmp/yay -p")
        run_command("sh -c 'sudo chown $USER /tmp/yay'")
        run_command("sh -c 'sudo chgrp $USER /tmp/yay'")

    def _install_packages(self):
        if not self._enable_installation:
            return

        with self._logger.indent(f"Installing packages: {self._packages}"):
            missing_packages = self._get_missing_packages(self._packages)
            if not missing_packages:
                self._logger.log("All packages are already installed.")
            else:
                packages_option = " ".join(missing_packages)
                assumed_packages_option = " ".join((f"--assume-installed {x}" for x in self._assumed_packages))
                install_command = f"yay -Syu --noconfirm {packages_option} {assumed_packages_option}"
                self._logger.log(f"Running command: {install_command}")
                stdout = Stdout.print_to_console() if self.print_installation else Stdout.ignore()
                run_command(install_command, stdout=stdout)

    def _mark_packages_explicit(self):
        # Mark all packages we install here as explictly installed. Sometimes a package can be already
        # installed as a dependency and then it won't show up in "yay -Qeq" invocation. This command
        # fixes this issue
        with self._logger.indent(f"Marking packages installed as explicit"):
            self._logger.silent_log("Finding packages to mark")
            packages_option = self._get_packages(True)
            packages_option = " ".join(packages_option)
            self._logger.log(packages_option)
            run_command(f"yay -D --asexplicit {packages_option}")

    def _mark_packages_deps(self):
        # In February 2022 base-devel stopped being a package group and started being a metapackage
        # (an empty package with only dependencies). This means all its packages should be switched
        # from "explicitly installed" to "installed as a dependency"
        self._logger.log("Marking packages installed as deps")
        packages_option = run_command(f"pactree base-devel --depth 1 -l", shell=False, stdout=Stdout.return_back()).stdout
        packages_option = packages_option.replace("\n", " ")
        packages_option = packages_option.replace("base-devel ", "")
        run_command(f"yay -D --asdeps {packages_option}")

    @staticmethod
    def _add_packages_to_list(packages_list, *args):
        for arg in args:
            if arg is None:
                pass
            elif isinstance(arg, list):
                packages_list += arg
            else:
                packages_list.append(str(arg))

    @push_dependency_handler
    def add_packages(self, *args):
        PackagesStep._add_packages_to_list(self._packages, *args)

    @push_dependency_handler
    def add_assumed_packages(self, *args):
        PackagesStep._add_packages_to_list(self._assumed_packages, *args)

    def _get_packages(self, resolve_groups):
        if resolve_groups:
            packages = [x for x in self._packages if x not in self._known_package_groups]
            groups = [x for x in self._packages if x in self._known_package_groups]
            if groups:
                packages_from_groups = run_command(f"yay -Qqg {' '.join(groups)}", stdout=Stdout.return_back()).stdout.strip().split("\n")
                packages += packages_from_groups
            return packages
        else:
            return self._packages

    def _get_missing_packages(self, required_packages):
        packages = [p for p in required_packages if p not in self._known_package_groups]
        package_groups = [p for p in required_packages if p in self._known_package_groups]

        # Try to get info on packages and package groups. Pacman will print a line to stderr for each
        # package that isn't installed.
        missing = []
        if packages:
            packages = " ".join(packages)
            try:
                run_command(f"pacman -Qi {packages}")
            except CommandError as e:
                missing += e.stderr.splitlines()
        if package_groups:
            package_groups = " ".join(package_groups)
            try:
                run_command(f"pacman -Qg {package_groups}")
            except CommandError as e:
                missing += e.stderr.splitlines()

        # Extract package name from the line
        missing = [re.search("'([^']+)'", x).group(1) for x in missing]
        return missing

    @pull_dependency_handler
    def query_installed_packages(self):
        return self._get_packages(True)

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            [
                # Installed during OS installation
                "base",
                "networkmanager",
                "grub",
                "efibootmgr",
                "linux-lts",
                "linux-firmware",
                "zsh",
                "bash",
                "update-grub",
                "grub-theme-vimix-very-dark-blue",
                "os-prober",
                # Linux kernels headers (needed for dkms modules)
                "linux-lts-headers",
                # General
                "consolas-font",
                "yay-git",
                "dash-static-musl",
                "unzip",
                "udisks2",
                "qpdfview",
                "pdfsam",
                "zip",
                "fzf",  # fuzzy search
                "file-roller",
                "imagemagick",  # file conversion
                "losslesscut-bin",  # cutting video
                "dos2unix",
                "nmap",
                "flamegraph",
                "xxd-standalone",
                # Unixporn
                "cava",
                # MTP (for Android phone mounting)
                "gvfs-mtp",
                "gvfs-gphoto2",
                "mtpfs",
                "jmtpfs",
                # Cloud
                "megasync-bin",
                # Multimedia
                "vlc",
                "mpv",
                "nomacs",
                "qt5-imageformats",  # For webp support in nomacs
                "libreoffice-still",
                "feh",
                "gimp",
                "rhythmbox",
                "playerctl",
                "gst-plugins-bad",  # Audio plugins
                "gst-plugins-ugly",  # Audio plugins
                "obs-studio",  # Recording
                # Communicators
                "discord",
            ]
        )
