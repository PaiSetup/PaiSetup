from steps.ssh import SshStep
from utils.setup_mode import SetupMode

from .alacritty.alacritty import AlacrittyStep
from .audio import AudioStep
from .bluetooth.bluetooth import BluetoothStep
from .charon import CharonStep
from .check_mate.check_mate import CheckMateStep
from .clion.clion import ClionStep
from .dush import DushStep
from .encryption.encryption import EncryptionStep
from .file_associations import FileAssociationsStep
from .firefox import FirefoxStep
from .git import GitStep
from .gpu.gpu import GpuStep
from .gtk_theme.gtk_theme import GtkThemeStep
from .gui.awesome.awesome import AwesomeStep
from .gui.dwm.dwm import DwmStep
from .gui.qtile.qtile import QtileStep
from .home_directory.home_directory import HomeDirectoryStep
from .icon_font.icon_font import IconFontStep
from .java import JavaStep
from .lightdm.lightdm import LightDmStep
from .neovim.neovim import NeovimStep
from .notes import NotesStep
from .nush import NushStep
from .packages import PackagesStep
from .picard import PicardStep
from .plex.plex import PlexStep
from .programming_common import ProgrammingCommonStep
from .programming_cpp import ProgrammingCppStep
from .programming_gamedev import ProgrammingGamedevStep
from .programming_python import ProgrammingPythonStep
from .programming_rust import ProgrammingRustStep
from .qbittorrent import QBitTorrentStep
from .raspberry_pi import RaspberryPiStep
from .rpi_led.rpi_led import RpiLedStep
from .screen_config_persistance import ScreenConfigPersistanceStep
from .shell.shell import ShellStep
from .st.st import StStep
from .systemd import SystemdStep
from .thunar import ThunarStep
from .ulauncher import UlauncherStep
from .useless import UselessStep
from .vagrant import VagrantStep
from .virtualbox import VirtualBoxStep
from .vscode import VscodeStep
from .xsession import XsessionStep


def get_steps(args, root_dir, build_dir, secret_dir, install_packages):
    has_multimedia_dir = args.mode == SetupMode.main

    match args.mode:
        case SetupMode.main: # Arch Linux
            steps = [
                PackagesStep(build_dir, True, install_packages),
                ShellStep(root_dir),
                GtkThemeStep(regenerate_widget_theme=args.full, regenerate_icon_theme=args.full),
                FileAssociationsStep(),
                AudioStep(),
                ClionStep(),
                ScreenConfigPersistanceStep(),
                GpuStep(),
                FirefoxStep(is_default_browser=True),
                SystemdStep(),
                ThunarStep(is_main_machine=has_multimedia_dir),
                HomeDirectoryStep(root_dir, is_main_machine=has_multimedia_dir),
                BluetoothStep(),
                JavaStep(),
                QBitTorrentStep(is_main_machine=has_multimedia_dir),
                XsessionStep(),
                GitStep(),
                UlauncherStep(),
                DwmStep(build_dir, full=args.full, is_default_wm=False),
                AwesomeStep(build_dir, is_default_wm=True),
                AlacrittyStep(),
                DushStep(fetch_git=args.full),
                NushStep(fetch_git=args.full),
                VscodeStep(build_dir),
                NeovimStep(),
                RpiLedStep(),
                UselessStep(),
                IconFontStep(full=args.full),
                PlexStep(),
                ProgrammingCppStep(graphics=True, systemc=True),
                ProgrammingPythonStep(),
                ProgrammingRustStep(),
                ProgrammingCommonStep(),
                ProgrammingGamedevStep(),
                SshStep(secret_dir, full=args.full),
                CheckMateStep(build_dir),
                LightDmStep(),
                EncryptionStep(),
                CharonStep(build_dir, full=args.full),
                PicardStep(),
                QtileStep(),
                NotesStep(fetch_git=args.full),
                VirtualBoxStep(),
                VagrantStep(),
                RaspberryPiStep(),
            ]
        case SetupMode.debian_casual:
            pass
        case SetupMode.debian_work:
            pass
        case _:
            raise ValueError("Selected SetupMode is unsupported for Linux")

    return steps
