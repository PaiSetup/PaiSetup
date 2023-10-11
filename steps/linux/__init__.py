from .audio import AudioStep
from .awesome.awesome import AwesomeStep
from .bash_scripts import BashScriptsStep
from .bluetooth.bluetooth import BluetoothStep
from .charon import CharonStep
from .check_mate.check_mate import CheckMateStep
from .dwm.dwm import DwmStep
from .encryption.encryption import EncryptionStep
from .file_associations import FileAssociationsStep
from .firefox import FirefoxStep
from .git import GitStep
from .gpu.gpu import GpuStep
from .gtk_theme.gtk_theme import GtkThemeStep
from .home_directory.home_directory import HomeDirectoryStep
from .java import JavaStep
from .lightdm.lightdm import LightDmStep
from .notes import NotesStep
from .packages import PackagesStep
from .picard import PicardStep
from .programming_common import ProgrammingCommonStep
from .programming_cpp import ProgrammingCppStep
from .programming_gamedev import ProgrammingGamedevStep
from .programming_python import ProgrammingPythonStep
from .programming_rust import ProgrammingRustStep
from .qbittorrent import QBitTorrentStep
from .raspberry_pi import RaspberryPiStep
from .screen_config_persistance import ScreenConfigPersistanceStep
from steps.ssh import SshStep
from .shell.shell import ShellStep
from .st.st import StStep
from .thunar import ThunarStep
from .virtualbox import VirtualBoxStep
from .vscode import VscodeStep
from .xsession import XsessionStep
from utils.setup_mode import SetupMode


def get_steps(args, root_dir, build_dir, secret_dir):
    if args.mode != SetupMode.main:
        raise ValueError("Arch Linux can only be setup as a main machine")

    steps = [
        PackagesStep(build_dir, True),
        ShellStep(root_dir),
        GtkThemeStep(regenerate_widget_theme=args.full, regenerate_icon_theme=args.full),
        FileAssociationsStep(),
        AudioStep(),
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
        DwmStep(build_dir, fetch_git=False, is_default_wm=False),
        AwesomeStep(build_dir, is_default_wm=True),
        StStep(build_dir, fetch_git=False),
        BashScriptsStep(fetch_git=args.full),
        VscodeStep(build_dir),
        ProgrammingCppStep(graphics=True, systemc=True),
        ProgrammingPythonStep(),
        ProgrammingRustStep(),
        ProgrammingCommonStep(),
        ProgrammingGamedevStep(),
        SshStep(secret_dir),
        CheckMateStep(build_dir),
        LightDmStep(),
        EncryptionStep(),
        CharonStep(build_dir, fetch_git=args.full),
        PicardStep(),
        NotesStep(fetch_git=args.full),
        VirtualBoxStep(),
        RaspberryPiStep(),
    ]

    return steps
