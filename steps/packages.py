from steps.step import Step
from utils import command
from utils.os_helpers import Pushd
from utils.log import log
import utils.external_project as ext


class PackagesStep(Step):
    def __init__(self, root_build_dir, print_installation):
        super().__init__("Packages")
        self._known_package_groups = ["base-devel", "vulkan-devel"]
        self.root_build_dir = root_build_dir
        self.print_installation = print_installation
        self._packages = []
        self._assumed_packages = []

    def register_as_dependency_listener(self, dependency_dispatcher):
        dependency_dispatcher.register_listener(self.add_packages)
        dependency_dispatcher.register_listener(self.add_assumed_packages)
        dependency_dispatcher.register_listener(self.list_packages)

    def perform(self):
        self._install_yay()
        self._set_yay_permissions()
        self._install_packages()
        self._mark_packages_explicit()

    def _install_yay(self):
        if not command.get_missing_packages(["yay"], self._known_package_groups):
            log("yay is already installed")
        else:
            log("Downloading yay")
            build_dir = self.root_build_dir / "yay"
            ext.download(
                "https://aur.archlinux.org/yay-git.git",
                "master",
                build_dir,
            )
            log("Installing yay")
            with Pushd(build_dir):
                command.run_command("makepkg -si --noconfirm")

    def _set_yay_permissions(self):
        log("Setting permissions for tmp yay directory")
        command.run_command("sudo mkdir /tmp/yay -p")
        command.run_command("sh -c 'sudo chown $USER /tmp/yay'")
        command.run_command("sh -c 'sudo chgrp $USER /tmp/yay'")

    def _install_packages(self):
        log(f"Required packages: {self._packages}")
        missing_packages = command.get_missing_packages(self._packages, self._known_package_groups)
        if not missing_packages:
            log("Already installed")
        else:
            packages_option = " ".join(missing_packages)
            assumed_packages_option = " ".join((f"--assume-installed {x}" for x in self._assumed_packages))
            install_command = f"yay -Syu --noconfirm {packages_option} {assumed_packages_option}"
            log(f"Running command: {install_command}")
            command.run_command(install_command, print_stdout=self.print_installation)

    def _mark_packages_explicit(self):
        packages_option = self._get_packages(True)
        packages_option = " ".join(packages_option)
        log(f"Making packages installed as explicit: {packages_option}.")
        command.run_command(f"yay -D --asexplicit {packages_option}")

    @staticmethod
    def _add_packages_to_list(packages_list, *args):
        for arg in args:
            if arg is None:
                pass
            elif isinstance(arg, list):
                packages_list += arg
            else:
                packages_list.append(str(arg))

    def add_packages(self, *args, **kwargs):
        PackagesStep._add_packages_to_list(self._packages, *args)

    def add_assumed_packages(self, *args, **kwargs):
        PackagesStep._add_packages_to_list(self._assumed_packages, *args)

    def _get_packages(self, resolve_groups):
        if resolve_groups:
            packages = [x for x in self._packages if x not in self._known_package_groups]
            groups = [x for x in self._packages if x in self._known_package_groups]
            if groups:
                packages_from_groups = command.run_command(f"yay -Qqg {' '.join(groups)}", return_stdout=True).strip().split("\n")
                packages += packages_from_groups
            return packages
        else:
            return self._packages

    def list_packages(self, resolve_groups, **kwargs):
        packages = self._get_packages(resolve_groups)
        packages = "\n".join(packages)
        print(packages)

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            [
                # Installed during OS installation
                "base",
                "networkmanager",
                "grub",
                "efibootmgr",
                "linux",
                "linux-lts",
                "linux-firmware",
                "zsh",
                "bash",
                # Linux kernels headers (needed for dkms modules)
                "linux-headers",
                "linux-lts-headers",
                # General
                "consolas-font",
                "openssh",
                "update-grub",
                "yay-git",
                "dash-static-musl",
                "qbittorrent",
                "unzip",
                "udisks2",
                "udiskie",
                "qpdfview",
                "pdfsam",
                "zip",
                "fzf",  # fuzzy search
                "file-roller",
                "imagemagick",  # file conversion
                "losslesscut-bin",  # cutting video
                "dos2unix",
                # Unixporn
                "neofetch",
                "cava",
                "cmatrix",
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
                "libreoffice-still",
                "feh",
                "gimp",
                "rhythmbox",
                "playerctl",
                "gst-plugins-bad",  # Audio plugins
                "gst-plugins-ugly",  # Audio plugins
                # Communicators
                "discord",
            ]
        )
