from steps.ssh import SshStep
from utils.setup_mode import SetupMode

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
from .thunar import ThunarStep
from .ulauncher import UlauncherStep
from .vagrant import VagrantStep
from .virtualbox import VirtualBoxStep
from .vscode import VscodeStep
from .xsession import XsessionStep


def get_steps(args, root_dir, build_dir, secret_dir):
    if args.mode != SetupMode.main:
        raise ValueError("Arch Linux can only be setup as a main machine")

    steps = [
        PackagesStep(build_dir, True),
        ShellStep(root_dir),
        GtkThemeStep(regenerate_widget_theme=args.full, regenerate_icon_theme=args.full),
        FileAssociationsStep(),
        AudioStep(),
        ClionStep(),
        ScreenConfigPersistanceStep(),
        GpuStep(),
        FirefoxStep(is_default_browser=True),
        ThunarStep(is_main_machine=args.mode == SetupMode.main),
        HomeDirectoryStep(root_dir, is_main_machine=args.mode == SetupMode.main),
        BluetoothStep(),
        JavaStep(),
        QBitTorrentStep(is_main_machine=args.mode == SetupMode.main),
        XsessionStep(),
        GitStep(),
        UlauncherStep(),
        DwmStep(build_dir, full=args.full, is_default_wm=False),
        AwesomeStep(build_dir, is_default_wm=True),
        StStep(build_dir, full=args.full),
        DushStep(fetch_git=args.full),
        NushStep(fetch_git=args.full),
        VscodeStep(build_dir),
        NeovimStep(),
        RpiLedStep(),
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

    return steps
