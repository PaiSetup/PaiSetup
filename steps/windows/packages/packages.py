from steps.step import Step, dependency_listener
from utils import command
from utils.os_helpers import Pushd
from utils.log import log
import utils.external_project as ext
from utils import command
from pathlib import Path
import re
from .package_info import PackageInfo, custom_packages_dir
from steps.windows.folders import KnownFolder


class PackagesStep(Step):
    def __init__(self, root_build_dir, skip_already_installed, is_main_machine):
        super().__init__("Packages")
        self._skip_already_installed = skip_already_installed
        self._is_main_machine = is_main_machine
        self._packages = []

    def express_dependencies(self, dependency_dispatcher):
        known_folders = dependency_dispatcher.get_known_folders()
        self._programs_dir = known_folders[KnownFolder.Programs]
        self._hw_tools_dir = known_folders[KnownFolder.HwTools]
        self._desktop_dir = known_folders[KnownFolder.Desktop]
        self._public_desktop_dir = known_folders[KnownFolder.PublicDesktop]
        self._games_dir = known_folders[KnownFolder.Games]

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
            "microsoft-windows-terminal",
            "python3",
        )
        if self._is_main_machine:
            dependency_dispatcher.add_packages(
                "discord",
                "obsidian",
                "veracrypt",
            )

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
        self._refresh_path()

    def install_package(self, package):
        # Gather required info for this package
        package_info = PackageInfo(package, self._programs_dir, self._hw_tools_dir, self._games_dir)

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
        log(install_command)
        try:
            command.run_command(install_command)
        except command.CommandError as e:
            self._warnings.push_with_report(
                f'Installation of "{package}" failed.',
                f"install_error_{package}",
                e.stdout,
                print=False,
            )
            log("FAILED", add_indent=True)
            return

        # Verify we really installed something
        if package_info.install_dir:
            if not package_info.install_dir.is_dir():
                raise ValueError(f"Package {package} was meant to be installed in {package_info.install_dir}, but the directory does not exist")
            try:
                next(package_info.install_dir.iterdir())
            except StopIteration:
                raise ValueError(f"Package {package} was meant to be installed in {package_info.install_dir}, but the directory is empty")

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
            command.run_command("choco pack")

    @dependency_listener
    def add_packages(self, *args):
        for arg in args:
            if arg is None:
                pass
            elif isinstance(arg, list):
                self._packages += arg
            else:
                self._packages.append(str(arg))

    @dependency_listener
    def list_packages(self, resolve_groups):
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
        installed_packages = command.run_command("choco list", return_stdout=True)
        installed_packages = installed_packages.splitlines()
        installed_packages = self._remove_chocolatey_warnings(installed_packages, True)
        installed_packages = [x.split()[0].lower() for x in installed_packages]

        required_packages = [x.lower() for x in required_packages]

        missing_packages = [x for x in required_packages if x not in installed_packages]
        return missing_packages

    def _refresh_path(self):
        log("Refreshing PATH variable")
        powershell_command = [
            "Import-Module $env:ChocolateyInstall\helpers\chocolateyProfile.psm1",
            "refreshenv | out-null",
            "echo $env:PATH",
        ]
        new_path = command.run_powershell_command(powershell_command, return_stdout=True).strip()
        self._env.set("PATH", new_path, force=True)
