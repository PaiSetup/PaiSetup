import enum


class Installer(enum.Enum):
    # Inno Setup. It can be recognized by the '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-' parameters in packages
    Inno = enum.auto()

    # Microsoft installer. It can be recognized by the '/norestart /quiet ALLUSERS=1' parameters in packages. Beware though, there are
    # multiple flavors and MSI creation tools. They may accept different arguments. Unfortunately we always have to check if it works.
    Msi = enum.auto()

    # Advanced installer is an installer creation tool, which produces MSI packages. It uses different parameters than standard MSI package, though.
    MsiAdvancedInstaller = enum.auto()

    # Nullsoft Scriptable Install System. It can be recognized by the '/S' parameter in packages.
    Nsis = enum.auto()

    # Some packages are not available in upstream repos, so we embed some of our own
    EmbeddedPackage = enum.auto()

    # Windows store packages. They go to C:\Program Files\WindowsApps, no way to change it
    Appx = enum.auto()


class PackageInfo:
    def __init__(self, package_name, programs_dir, hw_tools_dir):
        self.choco_args = ""
        self.install_args = ""
        self.package_args = ""
        self.desktop_files_to_delete = []
        self.install_dir = None

        self._set_package(package_name, programs_dir, hw_tools_dir)

    def _append_choco_arg(self, arg):
        if self.choco_args:
            self.choco_args = f"{self.choco_args} {arg}"
        else:
            self.choco_args = arg

    def _append_install_arg(self, arg):
        if self.install_args:
            self.install_args = f"{self.install_args} {arg}"
        else:
            self.install_args = arg

    def _append_package_arg(self, arg):
        if self.package_args:
            self.package_args = f"{self.package_args} {arg}"
        else:
            self.package_args = arg

    def _set_package(self, package_name, programs_dir, hw_tools_dir):
        if package_name == "adobereader":
            self.install_dir = programs_dir / "AdobeReader"
            self._set_installer(Installer.Msi)
            self._append_package_arg(" /NoUpdates")
        elif package_name == "megasync":
            # Technically it's an NSIS installer, but it ignores /D switch. We cannot set installation dir.
            # See https://github.com/meganz/MEGAsync/issues/604
            self._append_choco_arg("--ignore-checksums")
            self._desktop_files_to_delete.append("MEGAsync.lnk")
        elif package_name == "msiafterburner":
            self.install_dir = hw_tools_dir / "MsiAfterburner"
            self._set_installer(Installer.Nsis)
            self._append_choco_arg("--ignore-checksums")
            self.desktop_files_to_delete.append("MSI Afterburner.lnk")
        elif package_name == "vscodium":
            self.install_dir = programs_dir / "Vscodium"
            self._set_installer(Installer.Inno)
            self._append_package_arg("/NoDesktopIcon /NoQuicklaunchIcon /NoAddContextMenuFiles /NoAddContextMenuFolders")
        else:
            raise ValueError(f"Unknown package: {package_name}")

    def _set_installer(self, installer):
        def assert_install_dir_present(value=True):
            present = self.install_dir is not None
            if present != value:
                m = "" if present else "not "
                raise ValueError(f"install_dir should{m} be present for {installer}")

        if installer == Installer.Inno:
            assert_install_dir_present()
            self._append_install_arg(f"/DIR={self.install_dir}")
        elif installer == Installer.Msi:
            assert_install_dir_present()
            self._append_install_arg(
                f"INSTALLDIR={self.install_dir} TARGETDIR={self.install_dir} INSTALLLOCATION={self.install_dir} INSTALL_ROOT={self.install_dir} APPLICATIONFOLDER={self.install_dir}"
            )
        elif installer == Installer.MsiAdvancedInstaller:
            assert_install_dir_present()
            self._append_install_arg(f"APPDIR={self.install_dir}")
        elif installer == Installer.Nsis:
            assert_install_dir_present()
            self._append_install_arg(f"/D={self.install_dir}")
        elif installer == Installer.EmbeddedPackage:
            raise NotImplementedError()  # TODO
        elif installer == Installer.Appx:
            assert_install_dir_present(False)
        else:
            raise ValueError(f"Unknown installer: {installer}")
