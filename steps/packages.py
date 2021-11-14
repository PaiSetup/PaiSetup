from steps.step import Step
from utils import command
from utils.os_helpers import Pushd
from utils.log import log


class PackagesStep(Step):
    def __init__(self, root_build_dir):
        super().__init__("packages")
        self.root_build_dir = root_build_dir
        self._packages = []

    def _perform_impl(self):
        if not command.get_missing_packages(["yay-git"]):
            log("yay is already installed")
        else:
            log("Downloading yay")
            build_dir = self.root_build_dir / "yay-git"
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
            log(f"Missing packages: {missing_packages}")
            log("Installing")
            command.run_command(f"sudo yay -Syu --noconfirm {' '.join(missing_packages)}")

    def add_packages(self, *args):
        for arg in args:
            if arg is None:
                pass
            elif isinstance(arg, list):
                self._packages += arg
            else:
                self._packages.append(str(arg))

    def setup_required_packages(self, packages_step):
        packages_step.add_packages(
            [
                # General
                "nano",
                "code",  # TODO switch to codium
                "sudo",
                "openssh",
                "strace",
                "wget",
                "curl",
                "graphui",  # graphviz
                "chromium",
                # Fonts
                "libxft-bgra",
                "ttf-joypixels",
                "ttf-font-awesome",
                # Python
                "python",
                "python-pip",
                # C++
                "base-devel",
                "cmake",
                "doxygen",
                # Multimedia
                "vlc",
                "bcompare",
                "git",
                "alsa-utils",
            ]
        )
