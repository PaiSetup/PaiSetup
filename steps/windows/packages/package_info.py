import enum
import tempfile
import re
from pathlib import Path
from utils.windows_registry import HKLM, set_registry_value_string

custom_packages_dir = Path(__file__).parent / "custom_packages"


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
    CustomPackage = enum.auto()

    # Windows store packages. They go to C:\Program Files\WindowsApps, no way to change it
    Appx = enum.auto()


class PackageInfo:
    def __init__(self, package_name, programs_dir, hw_tools_dir, games_dir):
        self.choco_args = ""
        self.install_args = ""
        self.package_args = ""
        self.desktop_files_to_delete = []
        self.install_dir = None
        self.is_custom_package = False

        self._set_package(package_name, programs_dir, hw_tools_dir, games_dir)

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

    def _set_package(self, package_name, programs_dir, hw_tools_dir, games_dir):
        if package_name == "7zip":
            self.install_dir = programs_dir / "7zip_"  # Installer ignores the last character in path
            self._set_installer(Installer.Nsis)
        elif package_name == "adobereader":
            self.install_dir = programs_dir / "AdobeReader"
            self._set_installer(Installer.Msi)
            self._append_package_arg(" /NoUpdates")
        elif package_name == "adoptopenjdk11":
            self.install_dir = programs_dir / "Java/aojdk11"
            self._append_package_arg(f"/ADDLOCAL=FeatureMain /INSTALLDIR={self.install_dir} /quiet")
        elif package_name == "audacity":
            self.install_dir = programs_dir / "Audacity"
            self._set_installer(Installer.Inno)
            self.desktop_files_to_delete.append("Audacity.lnk")
        elif package_name == "beyondcompare":
            self.install_dir = programs_dir / "BeyondCompare"
            self._set_installer(Installer.Inno)
            self.desktop_files_to_delete.append("Beyond Compare 4.lnk")
        elif package_name == "discord":
            # Selecting installation dir isn't allowed: https://twitter.com/discord/status/843624938674311168
            self.desktop_files_to_delete.append("Discord.lnk")
        elif package_name == "ccleaner":
            self.install_dir = programs_dir / "CCleaner"
            self._set_installer(Installer.Nsis)
            self.desktop_files_to_delete.append("CCleaner.lnk")
        elif package_name == "charon":
            self.install_dir = programs_dir / "Charon"
            self._set_installer(Installer.CustomPackage)
            self._append_package_arg(f"/folder={self.install_dir}")
        elif package_name == "cmake":
            self.install_dir = programs_dir / "CMake"
            self._set_installer(Installer.Msi)
            self._append_install_arg("ADD_CMAKE_TO_PATH=System")
        elif package_name == "cryptomator":
            self.install_dir = programs_dir / "Cryptomator"
            self._set_installer(Installer.Inno)
        elif package_name == "crystaldiskmark":
            self.install_dir = hw_tools_dir / "CrystalDiskMark"
            self._set_installer(Installer.Inno)
            self.desktop_files_to_delete.append("CrystalDiskMark 8.lnk")
        elif package_name == "crystaldiskinfo.install":
            self.install_dir = hw_tools_dir / "CrystalDiskInfo"
            self._set_installer(Installer.Inno)
            self.desktop_files_to_delete.append("CrystalDiskInfo.lnk")
        elif package_name == "doxygen.install":
            self.install_dir = programs_dir / "Doxygen"
            self._set_installer(Installer.Inno)
        elif package_name == "ea-app":
            # Technically it's an NSIS installer, but it ignores /D switch)
            # We can download games to a custom folder, but we have to manually change game library location.
            self.desktop_files_to_delete.append("EA.lnk")
        elif package_name == "firefox":
            self.install_dir = programs_dir / "Firefox"
            self._append_package_arg(
                f"/InstallDir:{self.install_dir} /NoTaskbarShortcut /NoDesktopShortcut /NoStartMenuShortcut /NoMaintenanceService /RemoveDistributionDir /NoAutoUpdate"
            )
        elif package_name == "formatfactory":
            self.install_dir = programs_dir / "FormatFactory"
            self._set_installer(Installer.Nsis)
            self.desktop_files_to_delete.append("Format Factory.lnk")
        elif package_name == "furmark":
            self.install_dir = hw_tools_dir / "Furmark"
            self._set_installer(Installer.Inno)
        elif package_name == "gimp":
            self.install_dir = programs_dir / "Gimp"
            self._set_installer(Installer.Inno)
        elif package_name == "git":
            self.install_dir = programs_dir / "Git"
            self._set_installer(Installer.Inno)

            # Git installer has some parameters, but not everything can be set. We can workaround this by passing an .inf file
            inf_file_path = tempfile.mktemp(suffix=".inf")
            with open(inf_file_path, "w") as file:
                lines = [
                    "[Setup]",
                    "EditorOption=Notepad++",  # There's no option to select it via package parameters
                    "UseCredentialManager=Disabled",  # Shouldn't be needed, there is the /NoCredentialManager option, but it doesn't work
                ]
            self._append_package_arg("/GitOnlyOnPath /NoGuiHereIntegration")
            self._append_install_arg(f"/LOADINF={inf_file_path}")
        elif package_name == "godot":
            # Binary file installed in <chocolatey_dir>/bin
            self.desktop_files_to_delete.append("Godot.lnk")
            pass
        elif package_name == "googlechrome":
            # Techincally it's an MSI installer, but command line args do not work. We cannot select installation dir.
            self.desktop_files_to_delete.append("Google Chrome.lnk")
        elif package_name == "graphviz":
            self.install_dir = programs_dir / "Graphviz"
            self._set_installer(Installer.Nsis)
        elif package_name == "hxd":
            self.install_dir = programs_dir / "Hxd"
            self._set_installer(Installer.Inno)
        elif package_name == "hwmonitor":
            self.install_dir = hw_tools_dir / "HwMonitor"
            self._set_installer(Installer.Inno)
            self.desktop_files_to_delete.append("CPUID HWMonitor.lnk")
        elif package_name == "imageglass":
            self.install_dir = programs_dir / "ImageGlass"
            self._set_installer(Installer.MsiAdvancedInstaller)
            self.desktop_files_to_delete.append("ImageGlass.lnk")
        elif package_name == "irfanview":
            self.install_dir = programs_dir / "IrfanView"
            self._append_package_arg(f"/folder={self.install_dir}")
        elif package_name == "jre8":
            self.install_dir = programs_dir / "Java/jre8"
            self._append_package_arg(f"/exclude:32 /64dir:{self.install_dir}")
        elif package_name == "killdisk-freeware":
            self.install_dir = hw_tools_dir / "KillDisk"
            self._set_installer(Installer.Inno)
            self._append_choco_arg("--ignore-checksums")
        elif package_name == "megasync":
            # Technically it's an NSIS installer, but it ignores /D switch. We cannot set installation dir.
            # See https://github.com/meganz/MEGAsync/issues/604
            self._append_choco_arg("--ignore-checksums")
            self.desktop_files_to_delete.append("MEGAsync.lnk")
        elif package_name == "microsoft-windows-terminal":
            self._set_installer(Installer.Appx)
        elif package_name == "minecraft-launcher":
            self.install_dir = games_dir / "Minecraft"
            self._set_installer(Installer.Msi)
            self.desktop_files_to_delete.append("Minecraft Launcher.lnk")
        elif package_name == "mp3tag":
            self.install_dir = programs_dir / "Mp3Tag"
            self._set_installer(Installer.Nsis)
            self._append_package_arg("/NoDesktopShortcut /NoContextMenu")
        elif package_name == "msiafterburner":
            self.install_dir = hw_tools_dir / "MsiAfterburner"
            self._set_installer(Installer.Nsis)
            self._append_choco_arg("--ignore-checksums")
            self.desktop_files_to_delete.append("MSI Afterburner.lnk")
        elif package_name == "notepadplusplus":
            self.install_dir = programs_dir / "Notepad++"
            self._set_installer(Installer.Nsis)
        elif package_name == "obsidian":
            # Technically it's an NSIS installer, but it doesn't allow setting installation dir
            # https://forum.obsidian.md/t/how-to-change-the-default-installation-path/3492
            self.desktop_files_to_delete.append("Obsidian.lnk")
        elif package_name == "pdfsam.install":
            self.install_dir = programs_dir / "PDFsam"
            self._set_installer(Installer.Msi)
        elif package_name == "pix":
            # Pix doesn't let us configure anything...
            pass
        elif package_name == "python3":  # TODO: test this (install dir)
            # Technically python3 has an MSI installer, but the package already passes installation dir so we have to use the package parameter
            self.install_dir = programs_dir / "Python3"
            self._append_package_arg(f"/InstallDir:{self.install_dir}")
        elif package_name == "pycharm-community":
            self.install_dir = programs_dir / "Pycharm"
            self._set_installer(Installer.Nsis)
        elif package_name == "qbittorrent":
            self.install_dir = programs_dir / "qBittorrent"
            self._set_installer(Installer.Nsis)
        elif package_name == "recuva":
            self.install_dir = hw_tools_dir / "Recuva"
            self._set_installer(Installer.Nsis)
        elif package_name == "stardock-fences":
            # Technically it's an MSI installer, but it doesn't allow us to set installation dir.
            # See https://forums.stardock.com/505813/page/1/#3811703
            self.desktop_files_to_delete.append("Customize Fences.lnk")
        elif package_name == "steam-client":
            self.install_dir = games_dir / "Steam"
            self._set_installer(Installer.Nsis)
            self.desktop_files_to_delete.append("Steam.lnk")
        elif package_name == "sysinternals":
            self.install_dir = programs_dir / "SysInternals"
            self._append_package_arg(f"/InstallDir={self.install_dir}")
        elif package_name == "vagrant":
            self.install_dir = programs_dir / "Vagrant"
            self._set_installer(Installer.Msi)
        elif package_name == "veracrypt":
            # Package is implemented as autohotkey script and does not offer a way to select install dir.
            # TODO: implement selecting installation dir and create a pull request
            self.desktop_files_to_delete.append("VeraCrypt.lnk")
        elif package_name == "virtualbox":
            self.install_dir = programs_dir / "VirtualBox"
            self._append_package_arg("/NoDesktopShortcut /NoPath")
            self._append_install_arg(f"--msiparams INSTALLDIR={self.install_dir}")
        elif re.match("visualstudio2019.*", package_name):
            self.install_dir = programs_dir / "VisualStudio/2019"
            shared_dir = programs_dir / "VisualStudio/Shared"
            self._append_package_arg(f"--passive --installPath {self.install_dir} --path shared={shared_dir}")
        elif package_name == "vivaldi":
            self.install_dir = programs_dir / "Vivaldi"
            self._append_install_arg(f"--vivaldi-install-dir={self.install_dir}")
        elif package_name == "vlc":
            self.install_dir = programs_dir / "Vlc"
            self._set_installer(Installer.Nsis)
            self.desktop_files_to_delete.append("VLC media player.lnk")

            # Vlc installer ignores the directory selection argument and goes straight to the registry
            set_registry_value_string(HKLM, r"SOFTWARE\VideoLAN\VLC", "InstallDir", self.install_dir)
        elif package_name == "vscodium":
            self.install_dir = programs_dir / "Vscodium"
            self._set_installer(Installer.Inno)
            self._append_package_arg("/NoDesktopIcon /NoQuicklaunchIcon /NoAddContextMenuFiles /NoAddContextMenuFolders")
        elif package_name == "windows-handies":
            self.install_dir = programs_dir / "WindowsHandies"
            self._set_installer(Installer.CustomPackage)
            self._append_package_arg(f"/folder={self.install_dir}")
        elif package_name == "xtreme-tuner":
            self.install_dir = hw_tools_dir / "XtremeTuner"
            self._append_package_arg(f"/installDir={self.install_dir}")
            self.desktop_files_to_delete.append("Xtreme Tuner.lnk")
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
        elif installer == Installer.CustomPackage:
            assert_install_dir_present()
            self._append_choco_arg(f"--source={custom_packages_dir}")
            self.is_custom_package = True
        elif installer == Installer.Appx:
            assert_install_dir_present(False)
        else:
            raise ValueError(f"Unknown installer: {installer}")
