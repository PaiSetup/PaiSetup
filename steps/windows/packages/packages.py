from steps.step import Step
from utils import command
from utils.os_helpers import Pushd
from utils.log import log
import utils.external_project as ext
from utils import command
from pathlib import Path
import re
from .package_info import PackageInfo


class PackagesStep(Step):
    def __init__(self, root_build_dir, skip_already_installed):
        super().__init__("Packages")
        self._skip_already_installed = skip_already_installed
        self._packages = []
        # TODO there should be a step defining paths like this and we should query it for programs_dir. Hardcoding for now.
        self._programs_dir = Path("D:/Programs")
        self._hw_tools_dir = Path("D:/HwTools")
        self._desktop_dir = Path("D:/Desktop")
        self._games_dir = Path("D:/Games")

    def register_as_dependency_listener(self, dependency_dispatcher):
        dependency_dispatcher.register_listener(self.add_packages)
        dependency_dispatcher.register_listener(self.list_packages)

    def perform(self):
        log(f"Required packages: {self._packages}")
        if self._skip_already_installed:
            packages_to_install = self._get_missing_packages(self._packages)
        else:
            packages_to_install = self._packages

        if not packages_to_install:
            log("All packages already installed")
            return

        for package in packages_to_install:
            self.install_package(package)

    def install_package(self, package):
        # Gather required info for this package
        package_info = PackageInfo(package, self._programs_dir, self._hw_tools_dir, self._games_dir)

        # Install it with chocolatey
        install_command = f"choco install {package} --yes"
        if package_info.choco_args:
            install_command += f" {package_info.choco_args}"
        if package_info.install_args:
            install_command += f' --install-arguments="{package_info.install_args}"'
        if package_info.package_args:
            install_command += f' --packageparameters="{package_info.package_args}"'
        log(install_command)
        command.run_command(install_command)

        # Verify we really installed something
        if package_info.install_dir:
            if not package_info.install_dir.is_dir():
                raise ValueError(f"Package {package} was meant to be installed in {package_info.install_dir}, but the directory does not exist")
            try:
                next(package_info.install_dir.iterdir())
            except StopIteration:
                raise ValueError(f"Package {package} was meant to be installed in {package_info.install_dir}, but the directory is empty")

        # Remove any automatically created desktop icons
        for file in package_info.desktop_files_to_delete:
            file = self._desktop_dir / file
            file.unlink(missing_ok=True)

    def add_packages(self, *args, **kwargs):
        for arg in args:
            if arg is None:
                pass
            elif isinstance(arg, list):
                self._packages += arg
            else:
                self._packages.append(str(arg))

    def list_packages(self, resolve_groups, **kwargs):
        packages = "\n".join(self._packages)
        print(packages)

    def _remove_chocolatey_warnings(self, lines, remove_empty_lines=False):
        warnings_line_prefixes = [
            "Chocolatey v",
            "Validation Warnings",
            " - A pending system reboot request",
            "   being ignored due to",
            "   It is recommended that you reboot",
        ]
        warnings_regexes = [
            "[0-9]+ validations performed.",
        ]

        def should_remove(line):
            if remove_empty_lines and len(line) == 0:
                return True
            for prefix in warnings_line_prefixes:
                if line.startswith(prefix):
                    return True
            for regex in warnings_regexes:
                if re.match(regex, line):
                    return True
            return False

        return [line for line in lines if not should_remove(line)]

    def _get_missing_packages(self, required_packages):
        installed_packages = command.run_command("choco list --local-only", return_stdout=True)
        installed_packages = installed_packages.splitlines()
        installed_packages = self._remove_chocolatey_warnings(installed_packages, True)
        installed_packages = {x.split()[0] for x in installed_packages}

        required_packages = set(required_packages)

        missing_packages = required_packages.difference(installed_packages)
        missing_packages = list(missing_packages)
        return missing_packages
