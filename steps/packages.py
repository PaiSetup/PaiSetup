from steps.step import Step
from utils import command
from utils.os_helpers import Pushd
from utils.log import log


class PackagesStep(Step):
    def __init__(self, root_build_dir):
        super().__init__("Packages")
        self.root_build_dir = root_build_dir
        self._packages = []
        self._assumed_packages = []

    def _perform_impl(self):
        if not command.get_missing_packages(["yay"]):
            log("yay is already installed")
        else:
            log("Downloading yay")
            build_dir = self.root_build_dir / "yay"
            command.setup_git_repo("https://aur.archlinux.org/yay-git.git", "", build_dir)
            log("Installing yay")
            with Pushd(build_dir):
                command.run_command("makepkg -si --noconfirm")

        log("Setting permissions for tmp yay directory")
        command.run_command("sudo mkdir /tmp/yay -p")
        command.run_command("sh -c 'sudo chown $USER /tmp/yay'")
        command.run_command("sh -c 'sudo chgrp $USER /tmp/yay'")

        log(f"Required packages: {self._packages}")
        missing_packages = command.get_missing_packages(self._packages)
        if not missing_packages:
            log("Already installed")
        else:
            assumed_packages_option = " ".join((f"--assume-installed {x}" for x in self._assumed_packages))
            packages_option = " ".join(missing_packages)
            install_command = f"sudo yay -Syu --noconfirm {packages_option} {assumed_packages_option}"
            log(f"Running command: {install_command}")
            command.run_command(install_command)

    @staticmethod
    def _add_packages_to_list(packages_list, *args):
        for arg in args:
            if arg is None:
                pass
            elif isinstance(arg, list):
                packages_list += arg
            else:
                packages_list.append(str(arg))

    def add_packages(self, *args):
        PackagesStep._add_packages_to_list(self._packages, *args)

    def add_assumed_packages(self, *args):
        PackagesStep._add_packages_to_list(self._assumed_packages, *args)

    def setup_required_packages(self, packages_step):
        packages_step.add_packages(
            [
                # Fonts
                "libxft-bgra",
                "ttf-joypixels",
                "ttf-font-awesome",
                "consolas-font",
                # General
                "nano",
                "code",  # TODO switch to codium
                "sudo",
                "openssh",
                "strace",
                "pacman-contrib",
                "libnotify",
                "wget",
                "curl",
                "graphui",  # graphviz
                "firefox",
                "man",
                "ntfs-3g",
                "xorg-xev",
                "shellcheck",
                "tmux",
                "dash-static-musl",
                "htop",
                "qbittorrent",
                "bc",
                "bmon",
                "unzip",
                "udisks2",
                "udiskie",
                "qpdfview",
                "pdfsam",
                "imagemagick",
                # Python
                "python",
                "python-pip",
                # C++
                "base-devel",
                "cmake",
                "doxygen",
                "gdb",
                "cgdb",
                # Cloud & encryption
                "cryptomator-bin",
                "megasync-bin",
                # Multimedia
                "vlc",
                "thunar",
                "tumbler", # needed for thumbnails in Thunar
                "mirage",
                "bcompare",
                "git",
                "alsa-utils",
                "pulseaudio",
                "pulseaudio-alsa",
                "gimp",
                # Nvidia
                "nvidia",
                "nvidia-settings",
                "lib32-nvidia-utils",
                # Gaming
                "steam",
            ]
        )
        packages_step.add_assumed_packages(
            [
                "libxft=2.3.3",  # Some packages have this as a dependency, but we actually need libxft-bgra
            ]
        )
