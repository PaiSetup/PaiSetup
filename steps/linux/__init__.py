from steps.ssh import SshStep
from utils.setup_mode import SetupMode

from .alacritty.alacritty import AlacrittyStep
from .audio import AudioStep
from .bluetooth.bluetooth import BluetoothStep
from .charon import CharonStep
from .clion.clion import ClionStep
from .dush import DushStep
from .encryption.encryption import EncryptionStep
from .file_associations import FileAssociationsStep
from .firefox import FirefoxStep
from .git import GitStep
from .gpu.gpu import GpuStep
from .gtk_theme.gtk_theme import GtkThemeStep
from .gui.awesome.awesome import AwesomeStep
from .gui.gui_xorg import GuiXorg
from .gui.qtile.qtile import QtileStep
from .home_directory.home_directory import HomeDirectoryStep
from .icon_font.icon_font import FontStep
from .lightdm.lightdm import LightDmStep
from .multimedia_software_step import MultimediaSoftwareStep
from .neovim.neovim import NeovimStep
from .notes import NotesStep
from .nush import NushStep
from .packages import PackagesStep
from .packages_debian.packages_debian import PackagesDebianStep
from .plex.plex import PlexStep
from .programming_common import ProgrammingCommonStep
from .programming_cpp import ProgrammingCppStep
from .programming_gamedev import ProgrammingGamedevStep
from .programming_go import ProgrammingGoStep
from .programming_java import ProgrammingJavaStep
from .programming_python import ProgrammingPythonStep
from .programming_rust import ProgrammingRustStep
from .qbittorrent import QBitTorrentStep
from .raspberry_pi import RaspberryPiStep
from .rpi_led.rpi_led import RpiLedStep
from .shell.shell import ShellStep
from .spieven.spieven import SpievenStep
from .systemd import SystemdStep
from .thunar import ThunarStep
from .udiskie_step import UdiskieStep
from .ulauncher import UlauncherStep
from .useless import UselessStep
from .vagrant import VagrantStep
from .virtualbox import VirtualBoxStep
from .vscode import VscodeStep


def get_steps(args, root_dir, build_dir, secret_dir, install_packages):
    match args.mode:
        case SetupMode.arch:
            steps = [
                PackagesStep(build_dir, True, install_packages),
                ShellStep(root_dir),
                GtkThemeStep(root_build_dir=build_dir, regenerate_widget_theme=args.full, regenerate_icon_theme=args.full),
                FileAssociationsStep(),
                AudioStep(),
                ClionStep(),
                UdiskieStep(),
                GpuStep(),
                FirefoxStep(is_default_browser=True),
                SystemdStep(),
                ThunarStep(),
                HomeDirectoryStep(root_dir, True),
                BluetoothStep(),
                ProgrammingJavaStep(include_android=True),
                QBitTorrentStep(),
                GitStep(),
                UlauncherStep(),
                GuiXorg(full=args.full, root_build_dir=build_dir),
                AwesomeStep(),
                AlacrittyStep(),
                MultimediaSoftwareStep(),
                DushStep(fetch_git=args.full),
                NushStep(fetch_git=args.full),
                VscodeStep(build_dir),
                NeovimStep(),
                RpiLedStep(),
                UselessStep(),
                FontStep(root_build_dir=build_dir, full=args.full),
                PlexStep(),
                ProgrammingCppStep(graphics=True, systemc=True),
                ProgrammingPythonStep(),
                ProgrammingRustStep(),
                ProgrammingCommonStep(),
                ProgrammingGamedevStep(),
                ProgrammingGoStep(),
                SshStep(secret_dir, full=args.full),
                SpievenStep(build_dir),
                LightDmStep(),
                EncryptionStep(),
                CharonStep(build_dir, full=args.full),
                QtileStep(),
                NotesStep(fetch_git=args.full),
                VirtualBoxStep(),
                VagrantStep(),
                RaspberryPiStep(),
            ]
        case SetupMode.debian_casual:
            steps = [
                PackagesDebianStep(install_packages),
                AwesomeStep(),
                ProgrammingCommonStep(),
                ProgrammingPythonStep(),
                GitStep(),
                UdiskieStep(),
                AudioStep(),
                ThunarStep(),
                SpievenStep(build_dir),
                ShellStep(root_dir),
                MultimediaSoftwareStep(),
                QBitTorrentStep(),
                GuiXorg(full=args.full, root_build_dir=build_dir),
                FontStep(root_build_dir=build_dir, full=args.full),
                AlacrittyStep(),
                GtkThemeStep(root_build_dir=build_dir, regenerate_widget_theme=args.full, regenerate_icon_theme=args.full),
                FirefoxStep(is_default_browser=True),
                FileAssociationsStep(),
                HomeDirectoryStep(root_dir, has_multimedia_dir=False),
                UlauncherStep(),
                DushStep(fetch_git=args.full),
                NushStep(fetch_git=args.full),
                SshStep(secret_dir, full=args.full),
                VscodeStep(build_dir),
            ]
        case SetupMode.debian_work:
            pass
        case _:
            raise ValueError("Selected SetupMode is unsupported for Linux")

    return steps
