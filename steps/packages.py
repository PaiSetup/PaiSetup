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
        if command.is_package_installed("yay-git"):
            log("yay is already installed")
        else:
            log("Installing git")
            command.run_command("sudo pacman -Syu git --noconfirm")

            log("Downloading yay")
            build_dir = self.root_build_dir / "yay-git"
            command.setup_git_repo("https://aur.archlinux.org/yay-git.git", "", build_dir)
            log("Installing yay")
            with Pushd(build_dir):
                command.run_command("makepkg -si --noconfirm")

        packages = " ".join(self._packages)
        log(f"Installing packages: {packages}")
        command.run_command(f"sudo yay -Syu --noconfirm {packages}")

    def add_packages(self, *args):
        for arg in args:
            if arg is None:
                pass
            elif isinstance(arg, list):
                self._packages += arg
            else:
                self._packages.append(str(arg))

    def get_required_packages(self):
        return [
            # General
            "nano",
            "code",  # TODO switch to codium
            "sudo",
            "openssh",
            "strace",
            "wget",
            "curl",
            # Fonts
            # "libxft-bgra",
            "ttf-joypixels",
            # C++
            "base-devel",
            "cmake",
        ]
