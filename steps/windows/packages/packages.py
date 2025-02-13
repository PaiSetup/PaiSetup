import re
from pathlib import Path

import utils.external_project as ext
from steps.step import Step
from steps.windows.folders import KnownFolder
from utils.command import *
from utils.dependency_dispatcher import pull_dependency_handler, push_dependency_handler
from utils.os_helpers import Pushd

from .package_info import PackageInfo, custom_packages_dir


class PackagesStep(Step):
    def __init__(self, root_build_dir, skip_already_installed, is_main_machine):
        super().__init__("Packages")
        self._skip_already_installed = skip_already_installed
        self._is_main_machine = is_main_machine
        self._packages = []

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "7zip",
            "adobereader",
            "firefox",
            "imageglass",
            "notepadplusplus",
            # "recuva", # broken package
            "qbittorrent",
            "beyondcompare",
            "vlc",
            "dependencies",
            "microsoft-windows-terminal",
            "python3",
            "flamegraph",  # For performance analyzer
        )
        if self._is_main_machine:
            dependency_dispatcher.add_packages(
                "discord",
                "obsidian",
                "veracrypt",
            )

    def pull_dependencies(self, dependency_dispatcher):
        known_folders = dependency_dispatcher.get_known_folders()
        self._programs_dir = known_folders[KnownFolder.Programs]
        self._hw_tools_dir = known_folders[KnownFolder.HwTools]
        self._desktop_dir = known_folders[KnownFolder.Desktop]
        self._public_desktop_dir = known_folders[KnownFolder.PublicDesktop]
        self._games_dir = known_folders.get(KnownFolder.Games)

    def perform(self):
        self._logger.log(f"Required packages: {self._packages}")
        if self._skip_already_installed:
            packages_to_install = self._get_missing_packages(self._packages)
        else:
            packages_to_install = self._packages

        if not packages_to_install:
            self._logger.log("All packages already installed")
        else:
            for package in packages_to_install:
                self.install_package(package)
        self._refresh_path()

    def install_package(self, package):
        # Gather required info for this package
        package_info = self.get_package_info(package)

        # Install it with chocolatey
        install_command = f"choco install {package} --yes"
        if package_info.is_custom_package:
            self._pack_custom_package(package)
        if package_info.choco_args:
            install_command += f" {package_info.choco_args}"
        if package_info.install_args:
            install_command += f' --install-arguments="{package_info.install_args}"'
        if package_info.package_args:
            install_command += f' --packageparameters="{package_info.package_args}"'
        self._logger.log(install_command)
        try:
            run_command(install_command)
        except CommandError as e:
            self._logger.push_warning_with_report(
                f'Installation of "{package}" failed.',
                f"install_error_{package}",
                e.stdout,
                print=False,
            )
            self._logger.log("FAILED", add_indent=True)
            return

        # Verify whether the package was actually installed
        if package_info.install_dir:
            if package_info.install_dir.is_dir():
                try:
                    next(package_info.install_dir.iterdir())
                except StopIteration:
                    self._logger.push_warning(
                        f"Package {package} was meant to be installed in {package_info.install_dir}, but the directory is empty"
                    )
            else:
                self._logger.push_warning(
                    f"Package {package} was meant to be installed in {package_info.install_dir}, but the directory does not exist"
                )

        # Remove any automatically created desktop icons
        for file_name in package_info.desktop_files_to_delete:
            file = self._desktop_dir / file_name
            file.unlink(missing_ok=True)
            file = self._public_desktop_dir / file_name
            file.unlink(missing_ok=True)

    def _pack_custom_package(self, package_name):
        package_dir = custom_packages_dir / package_name

        # If there already is a nupkg file, early exit
        for file in package_dir.iterdir():
            if file.suffix == ".nupkg":
                return

        # Process the package
        with Pushd(package_dir):
            run_command("choco pack")

    @push_dependency_handler
    def add_packages(self, *args):
        for arg in args:
            if arg is None:
                pass
            elif isinstance(arg, list):
                self._packages += arg
            else:
                self._packages.append(str(arg))

    @push_dependency_handler
    def query_installed_packages(self):
        return self._packages

    @pull_dependency_handler
    def get_package_info(self, package):
        return PackageInfo(package, self._programs_dir, self._hw_tools_dir, self._games_dir)

    @pull_dependency_handler
    def get_generated_startup_entries(self):
        p = self._packages
        p = [self.get_package_info(x).startup_entries for x in p]
        p = sum(p, [])
        return p

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
        installed_packages = run_command("choco list", stdout=Stdout.return_back()).stdout
        installed_packages = installed_packages.splitlines()
        installed_packages = self._remove_chocolatey_warnings(installed_packages, True)
        installed_packages = [x.split()[0].lower() for x in installed_packages]

        required_packages = [x.lower() for x in required_packages]

        missing_packages = [x for x in required_packages if x not in installed_packages]
        return missing_packages

    def _refresh_path(self):
        self._logger.log("Refreshing PATH variable")
        powershell_command = [
            "Import-Module $env:ChocolateyInstall\helpers\chocolateyProfile.psm1",
            "refreshenv | out-null",
            "echo $env:PATH",
        ]
        new_path = run_powershell_command(powershell_command, stdout=Stdout.return_back()).stdout.strip()
        self._env.set("PATH", new_path, force=True)
